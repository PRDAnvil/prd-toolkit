"""The technical view of a PRD: what it says about how the system is built, beside what the repository holds
(FR-265, FR-266). The view is an output, never a part of the PRD: nothing here writes a file or checks the PRD."""
import re
import subprocess
from pathlib import Path

from . import model
from .markdown import tables

SECTIONS = ("Stack", "Architecture", "Components", "Requirements to code", "Standards", "Skills", "Contracts",
            "Uncovered code")
_PRD_SECTION = {"Stack": 1, "Architecture": 4, "Standards": 5, "Skills": 6}  # copied line for line (AC-265.2)
_FEATURES = re.compile(r"features/[^/]+\.md")
_ASSUMPTION = re.compile(r"\s*\[ASSUMPTION [^\]]*\]")  # on one line: the first `]` after it ends it (AC-265.2)
_CI_FILES = (".github/workflows/prd-toolkit.yml", ".gitlab/prd-toolkit.yml")  # the generated CI files (AC-266.4)
_DEFAULT_TEST_ROOTS = ["tests/"]


def _git(top: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=top, capture_output=True)


def head(top: Path) -> str | None:
    """HEAD's full name, as `git rev-parse HEAD` prints it; None when the repository has no commit."""
    r = _git(top, "rev-parse", "--verify", "--quiet", "HEAD")
    out = r.stdout.decode().strip()
    return out if r.returncode == 0 and out else None


def files_at_head(top: Path) -> list[str]:
    """The paths `git ls-tree -r --name-only HEAD` prints, relative to the repository's root."""
    r = _git(top, "ls-tree", "-r", "-z", "--name-only", "--full-tree", "HEAD")
    return [p for p in r.stdout.decode("utf-8", errors="surrogateescape").split("\0") if p]


def _line_counts(top: Path, paths: list[str]) -> dict[str, int]:
    """Each path's number of lines in its text at HEAD."""
    counts: dict[str, int] = {}
    for path in paths:
        r = _git(top, "cat-file", "blob", f"HEAD:{path}")
        data = r.stdout if r.returncode == 0 else b""
        counts[path] = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    return counts


def matches(path: str, glob: str) -> bool:
    """A path matches a Boundary glob (trd area notes)."""
    if "*" not in glob:
        return path == glob
    if glob.endswith("/**"):
        return path.startswith(glob[:-2])
    if "**" in glob:
        return False
    parts, globs = path.split("/"), glob.split("/")
    if len(parts) != len(globs):
        return False
    return all(re.fullmatch(".*".join(re.escape(s) for s in g.split("*")), p, re.S) for p, g in zip(parts, globs))


def _cells(line: str) -> list[str]:
    """A table line's cells as the row holds them, the white space around each removed: split on the pipes outside
    backticks that no backslash escapes, the escape kept."""
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    cells, cur, in_code, i = [], [], False, 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("\\|")
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


def _raw_rows(text: str, first_table_of: list[tuple[int, str]]) -> tuple[list[str], list[list[str]]]:
    """The header cells and each row's cells of the first table in a body, as the rows hold them."""
    ts = tables(first_table_of)
    if not ts:
        return [], []
    lines = text.split("\n")
    return _cells(lines[ts[0].line - 1]), [_cells(lines[r.line - 1]) for r in ts[0].rows]


def section_body(prd: model.Prd, number: int) -> list[str]:
    """A `prd.md` section's body: its lines after its `## ` heading, up to the next line that starts with `## ` or
    the end of the file, the empty lines at its start and at its end removed."""
    start = next((s.line for s in prd.sections if s.number == number), None)
    if start is None:
        return []
    body = []
    for line in prd.docs["prd.md"].split("\n")[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    return body


def _copied_body(prd: model.Prd, number: int) -> list[str]:
    """A `prd.md` section's body, each assumption marker removed with the white space directly before it
    (AC-265.2)."""
    return [_ASSUMPTION.sub("", line) for line in section_body(prd, number)]


def _status_word(b: model.ReqBlock) -> str:
    value = next((t for _, t in model._field_lines(b.lines, "Status")[:1]), "")
    return value.split()[0] if value.split() else ""


def _source_refs(b: model.ReqBlock) -> list[str] | None:
    """The block's Source refs: its `Source:` value and each continuation line split at every comma, each part with
    the white space around it removed, the empty parts left out (AC-266.3); None when it has no `Source:` line."""
    lines = model._field_lines(b.lines, "Source")
    if not lines:
        return None
    return [p.strip() for _, t in lines for p in t.split(",") if p.strip()]


def _requirements(prd: model.Prd, rel: str) -> str:
    listed = [f"{b.id} {_status_word(b)}" for b in prd.blocks if b.file == rel]
    return ", ".join(listed) if listed else "-"


def _features(prd: model.Prd) -> list[str]:
    return sorted((r for r in prd.docs if _FEATURES.fullmatch(r)), key=lambda r: r.split("/", 1)[1])


def _components(prd: model.Prd, files: list[str], sha7: str) -> tuple[str, list[str]]:
    body = ["| Area | State | Boundary | Files | Requirements |", "|---|---|---|---|---|"]
    if prd.adoption is None:  # AC-266.2
        for rel in _features(prd):
            body.append(f"| {rel.split('/', 1)[1][:-3]} | - | - | - | {_requirements(prd, rel)} |")
        return f"From: the features files and the files at {sha7}.", body
    text = prd.docs[model.ADOPTION_FILE]
    _, rows = _raw_rows(text, list(enumerate(text.split("\n"), 1)))
    for row, raw in zip(prd.adoption, rows):  # AC-266.1
        c = raw + [""] * 3
        count = sum(1 for f in files if any(matches(f, g) for g in row.boundary))
        body.append(f"| {c[0]} | {c[1]} | {c[2]} | {count} | {_requirements(prd, f'features/{row.area}.md')} |")
    return f"From: {model.ADOPTION_FILE} and the files at {sha7}.", body


def _at_head(source: str, files: set[str], counts: dict[str, int]) -> str:
    path, colon, rest = source.partition(":")
    number = re.match(r"\d+", rest)
    if not colon or not number or path not in files:
        return "no"
    return "yes" if counts[path] >= int(number.group(0)) else "no"


def _refs_at_head(refs: list[str], files: set[str], counts: dict[str, int]) -> str:
    """`yes` when every one of the Source refs holds at HEAD, else `no` (AC-266.3)."""
    return "yes" if all(_at_head(r, files, counts) == "yes" for r in refs) else "no"


def _requirements_to_code(prd: model.Prd, top: Path, files: list[str], sha7: str) -> tuple[str, list[str]]:
    order = _features(prd) + (["nfr.md"] if "nfr.md" in prd.docs else [])
    sourced = [(b, s) for rel in order for b in prd.blocks if b.file == rel and (s := _source_refs(b)) is not None]
    at = set(files)
    counts = _line_counts(top, sorted({p for _, refs in sourced for r in refs if (p := r.partition(":")[0]) in at}))
    body = ["| ID | Status | Source | At HEAD |", "|---|---|---|---|"]
    body += [f"| {b.id} | {_status_word(b)} | {', '.join(refs)} | {_refs_at_head(refs, at, counts)} |"
             for b, refs in sourced]
    if not sourced:
        body = ["No requirement block has a Source: line."]
    return f"From: the Source: lines of the requirement blocks, checked at {sha7}.", body


def _contracts(prd: model.Prd) -> tuple[str, list[str]]:
    body7 = section_body(prd, 7)
    header, rows = _raw_rows("\n".join(body7), list(enumerate(body7, 1)))
    names = [h.strip() for h in header]
    ti = names.index("Type") if "Type" in names else 0
    fi = names.index("Files (glob)") if "Files (glob)" in names else 1
    body = ["These stay in the PRD: the black-box tester writes its tests from them.", "", "| Type | Files (glob) |",
            "|---|---|"]
    for raw in rows:
        c = raw + [""] * (max(ti, fi) + 1)
        body.append(f"| {c[ti]} | {c[fi]} |")
    return "From: prd.md section 7.", body


def _uncovered(prd: model.Prd, files: list[str], folder: str, sha7: str) -> tuple[str, list[str]]:
    if prd.adoption is None:
        return "From: prd.md section 8.", ["No adoption map: every path outside the PRD folder and .prd-toolkit/ is covered."]
    globs = [g for row in prd.adoption for g in row.boundary]
    roots = [r if r.endswith("/") else f"{r}/" for r in (prd.testing.harness.test_roots or _DEFAULT_TEST_ROOTS)]
    # a path lies under a root when it starts with it, a `/` added to a root that does not end in one (AC-266.4)
    left = sorted(f for f in files if not f.startswith(f"{folder}/") and not f.startswith(".prd-toolkit/")
                  and not any(f.startswith(r) for r in roots) and f not in _CI_FILES
                  and not any(matches(f, g) for g in globs))
    body = [f"- `{f}`" for f in left] or ["Every file is in an area's Boundary."]
    return f"From: the files at {sha7} that no Boundary glob of {model.ADOPTION_FILE} matches.", body


def view(prd: model.Prd, top: Path, sha: str) -> str:
    """The technical view's text (AC-265.1): the header, then the eight sections, ending with one newline."""
    sha7 = sha[:7]
    try:
        folder = prd.root.relative_to(top).as_posix()
    except ValueError:
        folder = prd.root.as_posix()
    files = files_at_head(top)
    parts: dict[str, tuple[str, list[str]]] = {
        name: (f"From: prd.md section {n}.", _copied_body(prd, n)) for name, n in _PRD_SECTION.items()}
    parts["Components"] = _components(prd, files, sha7)
    parts["Requirements to code"] = _requirements_to_code(prd, top, files, sha7)
    parts["Contracts"] = _contracts(prd)
    parts["Uncovered code"] = _uncovered(prd, files, folder, sha7)
    out = [f"# Technical view: {prd.frontmatter.get('prd', '')} {prd.frontmatter.get('version', '')}", "",
           f"Generated by prd trd from `{folder}` at {sha7}. Do not edit it: run prd trd again. The PRD is the "
           "authority, and the black-box tester never reads this file."]
    for name in SECTIONS:
        from_line, body = parts[name]
        out += ["", f"## {name}", "", from_line, "", *body]
    return "\n".join(out) + "\n"
