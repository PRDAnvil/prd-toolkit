#!/usr/bin/env python3
"""Claude Code plugin hook in two tiers: an edit reminder (PostToolUse) and a lint report (Stop).

`post` reminds the agent, once per session and area, that an edit landed in an adopted area with no
block approved at HEAD, and notes each PRD folder an edit lands in. `stop` runs lint on each noted
folder and reports the error findings the session has not been told of. Neither tier blocks: every
run with `post` or `stop` exits 0. Standard library only, so `python3 -S` runs it the same.
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

USAGE = "usage: prd_edit_hook.py post|stop"
FAIL_PREFIX = "prd-toolkit edit hook: "
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
OFF_VAR = "PRD_TOOLKIT_EDIT_HOOK"
VENDOR_DIR = ".prd-toolkit"
LINT_TIMEOUT = 50
MAX_FINDINGS = 20
TAIL = ("a behaviour change there starts with /prd-toolkit:prd-change before any code, "
        "and a change of no behaviour cites Refs: none (no behaviour change).")

_SESSION_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE = re.compile(r"(`+)(.+?)\1")
_HEADING = re.compile(r"^#{1,3}\s")
_BLOCK = re.compile(r"^### (?:UJ|FR|NFR)-\d+\s")
_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_BACKTICKED = re.compile(r"`([^`]+)`")


class Quiet(Exception):
    """Nothing to say: print nothing and exit 0."""


# ---- git, read at HEAD ----

def _git(root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", root, *args], capture_output=True, stdin=subprocess.DEVNULL)


def _toplevel(path: str) -> str | None:
    """The working tree root holding `path`, resolved; None when it lies in none."""
    d = os.path.dirname(path)
    while d and not os.path.isdir(d):
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    r = _git(d, "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        return None
    top = r.stdout.decode("utf-8").rstrip("\n")
    return os.path.realpath(top) if top else None


def _relative(path: str, top: str) -> str | None:
    """`path` from the repository root, `/`-separated; None when it lies outside it."""
    real = os.path.join(os.path.realpath(os.path.dirname(path)), os.path.basename(path))
    rel = os.path.relpath(real, top)
    if rel == "." or rel == ".." or rel.startswith(".." + os.sep) or os.path.isabs(rel):
        return None
    return rel.replace(os.sep, "/")


def _has_head(top: str) -> bool:
    return _git(top, "rev-parse", "--verify", "-q", "HEAD^{commit}").returncode == 0


def _ls_head(top: str, *paths: str) -> list[str]:
    """Names of the entries at HEAD for the given tree paths (`dir/` lists the folder)."""
    r = _git(top, "ls-tree", "-z", "--name-only", "HEAD", "--", *paths)
    if r.returncode != 0:
        raise RuntimeError(f"git ls-tree failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return [n for n in r.stdout.decode("utf-8").split("\0") if n]


def _show_head(top: str, path: str) -> str:
    r = _git(top, "cat-file", "blob", f"HEAD:{path}")
    if r.returncode != 0:
        raise RuntimeError(f"git cat-file failed on HEAD:{path}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8")


def _head_prd_folders(top: str) -> list[str]:
    """The slugs of the PRD folders `docs/prd/<slug>/` whose prd.md HEAD holds, sorted."""
    entries = _ls_head(top, "docs/prd/")
    slugs = sorted(e.rsplit("/", 1)[-1] for e in entries if e.startswith("docs/prd/"))
    if not slugs:
        return []
    have = set(_ls_head(top, *(f"docs/prd/{s}/prd.md" for s in slugs)))
    return [s for s in slugs if f"docs/prd/{s}/prd.md" in have]


# ---- markdown, as prdlint reads it ----

def _cells(line: str) -> list[str]:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    cells, cur, in_code, i = [], [], False, 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if c == "`":
            in_code = not in_code
        if c == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _adoption_rows(text: str) -> list[tuple[str, str, list[str]]]:
    """(area, state, Boundary globs) for each row of the first table in adoption.md."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.lstrip().startswith("|") and i + 1 < len(lines) and _SEP.match(lines[i + 1]):
            rows = []
            for row in lines[i + 2:]:
                if not row.lstrip().startswith("|"):
                    break
                c = _cells(row) + [""] * 3
                rows.append((c[0].strip("`"), c[1].strip("`"), _BACKTICKED.findall(c[2])))
            return rows
    return []


def _any_approved(text: str) -> bool:
    """True when a requirement block of the file has the `Status:` value `approved`, with nothing after it."""
    in_fence, in_block, seen_status = False, False, False
    for line in text.split("\n"):
        if _FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence:
            st = _INLINE.sub(lambda m: " " * len(m.group(0)), line)
            if _HEADING.match(st):
                in_block, seen_status = bool(_BLOCK.match(st)), False
                continue
        if in_block and not seen_status and line.startswith("Status:"):
            seen_status = True
            if line[len("Status:"):].strip() == "approved":
                return True
    return False


def _glob_re(glob: str) -> re.Pattern:
    """A Boundary glob as the commit rule matches it, against the whole path from the repository root."""
    out, i = "", 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif glob.startswith("**", i):
            out, i = out + ".*", i + 2
        elif glob[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif glob[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(glob[i]), i + 1
    return re.compile(out + r"\Z", re.S)


# ---- the session's record ----

def _session(data: dict) -> str | None:
    sid = data.get("session_id")
    return sid if isinstance(sid, str) and _SESSION_ID.fullmatch(sid) else None


def _record_path(sid: str) -> Path:
    return Path(tempfile.gettempdir()) / f"prd-toolkit-edit-hook-{sid}.json"


def _load(sid: str) -> dict:
    p = _record_path(sid)
    try:
        raw = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        raw = ""
    rec = json.loads(raw) if raw.strip() else {}
    if not isinstance(rec, dict):
        rec = {}
    rec.setdefault("reminded", [])
    rec.setdefault("noted", {})
    rec.setdefault("reported", {})
    rec.setdefault("could_not_run", [])
    return rec


def _save(sid: str, rec: dict) -> None:
    p = _record_path(sid)
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", dir=str(p.parent))
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(rec, f)
    os.replace(tmp, p)


# ---- output ----

def _emit(event: str, context: str) -> None:
    line = json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}) + "\n"
    sys.stdout.buffer.write(line.encode("utf-8"))
    sys.stdout.buffer.flush()


def _read_input() -> dict:
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise Quiet
    if not isinstance(data, dict):
        raise Quiet
    return data


# ---- post: the edit tier ----

def _edited_path(data: dict) -> str:
    tool = data.get("tool_name")
    if tool not in EDIT_TOOLS:
        raise Quiet
    tin = data.get("tool_input")
    if not isinstance(tin, dict):
        raise Quiet
    path = tin.get("notebook_path" if tool == "NotebookEdit" else "file_path")
    if not isinstance(path, str) or not path or not os.path.isabs(path):
        raise Quiet
    return path


def _reminder(top: str, rel: str, slug: str) -> tuple[str, str] | None:
    """(session key, reminder line) for the PRD folder `slug` at HEAD, or None when it says nothing about `rel`."""
    folder = f"docs/prd/{slug}"
    names = {n.rsplit("/", 1)[-1] for n in _ls_head(top, folder + "/")}
    if "adoption.md" in names:
        rows = _adoption_rows(_show_head(top, f"{folder}/adoption.md"))
        features = {n.rsplit("/", 1)[-1] for n in _ls_head(top, folder + "/features/")} if "features" in names else set()
        for area, state, globs in rows:
            if state != "adopted" or not any(_glob_re(g).match(rel) for g in globs):
                continue
            name = f"{area}.md"
            if name in features and _any_approved(_show_head(top, f"{folder}/features/{name}")):
                continue
            return (f"{top}\0{folder}\0{area}",
                    f"prd-toolkit: {rel} is in area {area} of {folder}, and no block of that area is approved at HEAD; {TAIL}")
        return None
    files = []
    if "features" in names:
        files += [f"{folder}/features/{n.rsplit('/', 1)[-1]}" for n in _ls_head(top, folder + "/features/") if n.endswith(".md")]
    if "nfr.md" in names:
        files.append(f"{folder}/nfr.md")
    if any(_any_approved(_show_head(top, f)) for f in files):
        return None
    return (f"{top}\0{folder}",
            f"prd-toolkit: {rel} is in the Boundary of {folder}, and no block of that PRD is approved at HEAD; {TAIL}")


def post() -> None:
    if os.environ.get(OFF_VAR) == "off":
        raise Quiet
    data = _read_input()
    path = _edited_path(data)
    top = _toplevel(path)
    if top is None:
        raise Quiet
    rel = _relative(path, top)
    if rel is None:
        raise Quiet
    sid = _session(data)
    parts = rel.split("/")
    if len(parts) > 3 and parts[:2] == ["docs", "prd"] and os.path.isfile(os.path.join(top, "docs", "prd", parts[2], "prd.md")):
        if sid:  # AC-279.1: note the PRD folder for the Stop tier
            rec = _load(sid)
            folder = f"docs/prd/{parts[2]}"
            rec["noted"][os.path.join(top, "docs", "prd", parts[2])] = [top, folder]
            _save(sid, rec)
        raise Quiet
    agent = data.get("agent_type")
    if isinstance(agent, str) and (agent == "prd-tester" or agent.endswith(":prd-tester")):
        raise Quiet
    if rel == VENDOR_DIR or rel.startswith(VENDOR_DIR + "/"):
        raise Quiet
    if not _has_head(top):
        raise Quiet
    slugs = _head_prd_folders(top)
    if any(rel.startswith(f"docs/prd/{s}/") for s in slugs):
        raise Quiet
    rec = _load(sid) if sid else None
    lines = []
    for slug in slugs:
        hit = _reminder(top, rel, slug)
        if hit is None:
            continue
        key, line = hit
        if rec is not None:
            if key in rec["reminded"]:
                continue
            rec["reminded"].append(key)
        lines.append(line)
    if not lines:
        raise Quiet
    if rec is not None:
        _save(sid, rec)
    _emit("PostToolUse", "\n".join(lines))


# ---- stop: the lint tier ----

def _launcher(top: str) -> str:
    vendored = os.path.join(top, VENDOR_DIR, "prd")
    if os.path.isfile(vendored):
        return f"{VENDOR_DIR}/prd"
    return str(Path(__file__).resolve().parent / "prd")


def _lint(top: str, folder: str) -> tuple[int | None, str, str]:
    """(exit code or None on time-out, stdout, stderr) of `sh <launcher> lint <folder>` from the repository root."""
    p = subprocess.Popen(["sh", _launcher(top), "lint", folder], cwd=top, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = p.communicate(timeout=LINT_TIMEOUT)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            p.kill()
        p.communicate()
        return None, "", ""
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def _folder_report(rec: dict, key: str, top: str, folder: str) -> str | None:
    code, out, err = _lint(top, folder)
    if code == 0:
        return None
    if code == 1:
        told = rec["reported"].setdefault(key, [])
        new = [ln for ln in out.splitlines() if ln.strip() and ": warn: " not in ln and ln not in told]
        if not new:
            return None
        shown, more = new[:MAX_FINDINGS], len(new) - MAX_FINDINGS
        told.extend(shown)
        lines = [f"prd-toolkit: prd lint fails on {folder} after this session's edits:", *shown]
        if more > 0:
            lines.append(f"and {more} more")
        lines.append("Finish the PRD edit through /prd-toolkit:prd-change, which runs lint itself.")
        return "\n".join(lines)
    if key in rec["could_not_run"]:
        return None
    rec["could_not_run"].append(key)
    if code is None:
        reason = "timed out after 50 s"
    else:
        first = next((ln for ln in err.splitlines() if ln.strip()), None)
        reason = first if first is not None else f"exit {code}"
    return f"prd-toolkit: prd lint could not run on {folder}: {reason}"


def stop() -> None:
    if os.environ.get(OFF_VAR) == "off":
        raise Quiet
    data = _read_input()
    sid = _session(data)
    if sid is None:
        raise Quiet
    rec = _load(sid)
    noted, rec["noted"] = rec["noted"], {}
    try:
        reports = []
        for key in sorted(noted):
            top, folder = noted[key]
            report = _folder_report(rec, key, top, folder)
            if report:
                reports.append(report)
    finally:
        _save(sid, rec)  # AC-279.6: no folder stays noted after a Stop run
    if not reports:
        raise Quiet
    _emit("Stop", "\n\n".join(reports))


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in ("post", "stop"):
        sys.stderr.write(USAGE + "\n")
        return 2
    try:
        (post if argv[1] == "post" else stop)()
    except Quiet:
        pass
    except Exception as e:  # any other failure: one stderr line, nothing on stdout, exit 0
        msg = " ".join(str(e).split())
        sys.stderr.buffer.write(f"{FAIL_PREFIX}{type(e).__name__}: {msg}\n".encode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
