"""Shared helper of the inbox-cards characterization tests (testing.md: Harness, Setup steps, inbox-cards).

Everything here comes from docs/prd/prd-toolkit/testing.md and test-cases/inbox-cards.yaml: the scratch
repository <tmp>/main with its worktrees <tmp>/wt and <tmp>/wt2 (steps IC0, IC2, ICN, ICT, ICD), the
environment every run, step command and in-process call of an inbox-cards case uses, LISTING(P) and GROUPS(L),
and the way a CLI script runs (`python <repo>/prd-toolkit/scripts/<script>` with the test's own interpreter).

Steps N0 and NE2 are borrowed from status_next_support (testing.md, Borrowed steps and helpers); every other
helper is defined here. A setup step that cannot be applied raises SetupError, so the test ends as an error,
not a failure.
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from status_next_support import N0, NE2  # testing.md, Borrowed steps and helpers

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
GATES = SCRIPTS_DIR / "prd_gates.py"
ORDERS_REL = Path("docs") / "prd" / "orders"

# testing.md, Harness (Subprocess environment) and the inbox-cards paragraph: the variables no run inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_PLUGINS_FILE",
)
_ADDED_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung command ends the test


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


def subprocess_env() -> dict[str, str]:
    """The environment of every run, step command and git command of an inbox-cards case."""
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(_ADDED_ENV)
    return env


def git(cwd: Path, *args: str) -> Result:
    """Run `git <args>` in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(["git", *args], cwd=cwd, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def run_gates(cwd: Path, *args: str) -> Result:
    """Run `python GATES <args>` in `cwd` with the case's environment."""
    proc = subprocess.run(
        [sys.executable, str(GATES), *args],
        cwd=cwd, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def resolved(path: Path) -> str:
    """MAIN, WT, WT2: str(pathlib.Path(<path>).resolve())."""
    return str(Path(path).resolve())


def orders(worktree: Path) -> Path:
    """The PRD folder docs/prd/orders of a worktree."""
    return worktree / ORDERS_REL


# -- environment and setup steps (testing.md, Setup steps, inbox-cards) --

def _case_env(monkeypatch) -> None:
    """The case's environment in the test process, so in-process calls and the inbox's git commands inherit it."""
    for name in _DROPPED_ENV:
        monkeypatch.delenv(name, raising=False)
    for name, value in _ADDED_ENV.items():
        monkeypatch.setenv(name, value)


def _step_git(cwd: Path, *args: str) -> None:
    r = git(cwd, *args)
    if r.exit != 0:
        raise SetupError(f"git {' '.join(args)} in {cwd} exited {r.exit}: {r.stderr}")


def _replace_line(path: Path, old: str, new: str) -> None:
    if not path.is_file():
        raise SetupError(f"{path} does not exist")
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line == old]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {old!r}, found {len(hits)}")
    lines[hits[0]] = new
    path.write_bytes("\n".join(lines).encode("utf-8"))


def IC0(tmp: Path, monkeypatch) -> None:
    main = tmp / "main"
    N0(main)
    NE2(main)
    _case_env(monkeypatch)
    _step_git(main, "symbolic-ref", "HEAD", "refs/heads/main")
    _step_git(main, "config", "user.name", "Sample")
    _step_git(main, "config", "user.email", "sample@example.com")
    _step_git(main, "config", "commit.gpgsign", "false")
    _step_git(main, "config", "core.hooksPath", "/dev/null")
    _step_git(main, "add", "-A")
    _step_git(main, "commit", "-q", "-m", "base")
    _step_git(main, "worktree", "add", "-q", str(tmp / "wt"), "-b", "other")


def IC2(tmp: Path, monkeypatch) -> None:
    _step_git(tmp / "main", "worktree", "add", "-q", str(tmp / "wt2"), "-b", "third")


def ICN(tmp: Path, monkeypatch) -> None:
    path = tmp / "main" / ORDERS_REL / "errors.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("# Error ledger\n".encode("utf-8"))


def ICT(tmp: Path, monkeypatch) -> None:
    _replace_line(tmp / "wt" / ORDERS_REL / "errors.md",
                  "### E-001 The importer stops at row 1000", "### E-001 The importer stops at row 2000")


def ICD(tmp: Path, monkeypatch) -> None:
    _replace_line(tmp / "wt2" / ORDERS_REL / "errors.md",
                  "Detected: 2026-11-03, a run on the October file", "Detected: 2026-11-04, a run on the October file")


def ICE(tmp: Path, monkeypatch) -> None:
    """Insert after main's line `Touches: FR-003` the line `Explanation: …`; nothing is committed."""
    path = tmp / "main" / ORDERS_REL / "errors.md"
    if not path.is_file():
        raise SetupError(f"{path} does not exist")
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line == "Touches: FR-003"]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line 'Touches: FR-003', found {len(hits)}")
    lines.insert(hits[0] + 1, "Explanation: An import of a file of 1,200 rows stored 1,000 of them.")
    path.write_bytes("\n".join(lines).encode("utf-8"))


STEPS = {"IC0": IC0, "IC2": IC2, "ICN": ICN, "ICT": ICT, "ICD": ICD, "ICE": ICE}


def build(tmp: Path, monkeypatch, *steps: str) -> None:
    """Run the case's `setup:` steps in order, after setting GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM in the
    test process, and leave the case's environment set and prd-toolkit/scripts on sys.path."""
    for name, value in _ADDED_ENV.items():
        monkeypatch.setenv(name, value)
    for step in steps:
        STEPS[step](tmp, monkeypatch)
    _case_env(monkeypatch)
    monkeypatch.syspath_prepend(str(SCRIPTS_DIR))


# -- LISTING and GROUPS (test-cases/inbox-cards.yaml, conventions) --

def gates_module():
    """prdlint.gates, imported with prd-toolkit/scripts on sys.path (build puts it there)."""
    return importlib.import_module("prdlint.gates")


def make_inbox(prd_dir: Path):
    """server, token = prdlint.gates.make_inbox(prd_dir)."""
    return gates_module().make_inbox(prd_dir)


def listing(prd_dir: Path) -> dict:
    """LISTING(P): the inbox listing of the PRD folder P; server_close runs even when the listing raises."""
    server, _token = make_inbox(prd_dir)
    try:
        return server.state.listing()
    finally:
        server.server_close()


def groups(doc: dict) -> list[dict]:
    """GROUPS(L): one mapping per entry of L["worktrees"], in order: {path, branch, ids}."""
    return [
        {"path": g["path"], "branch": g["branch"], "ids": [card["id"] for card in g["gates"]]}
        for g in doc["worktrees"]
    ]


# -- the T-254 cases' log and "as before" (test-cases/inbox-cards.yaml, conventions) --

def log_path(tmp: Path) -> Path:
    """LOG: <tmp>/main/.git/prd-gates-log.jsonl, the answer log of the repository's git common folder."""
    return tmp / "main" / ".git" / "prd-gates-log.jsonl"


def log_lines(tmp: Path) -> list[str]:
    """LOG's lines (str.splitlines()); none when it does not exist."""
    path = log_path(tmp)
    return path.read_bytes().decode("utf-8").splitlines() if path.is_file() else []


def log_last(tmp: Path) -> dict:
    """LOG's LAST line: its last line parsed as JSON."""
    lines = log_lines(tmp)
    assert lines, f"{log_path(tmp)} holds no line"
    return json.loads(lines[-1])


def head(worktree: Path) -> str:
    """The commit `git rev-parse HEAD` prints in the worktree, less its newline."""
    r = git(worktree, "rev-parse", "HEAD")
    if r.exit != 0:
        raise SetupError(f"git rev-parse HEAD in {worktree} exited {r.exit}: {r.stderr}")
    return r.stdout.strip()


@dataclass
class Before:
    """What a T-254 case keeps before its call or first run: errors.md, HEAD and LOG's line count."""
    errors: bytes
    head: str
    log_count: int


def before(tmp: Path) -> Before:
    main = tmp / "main"
    return Before((orders(main) / "errors.md").read_bytes(), head(main), len(log_lines(tmp)))


def assert_nothing_written(tmp: Path, was: Before) -> None:
    """errors.md byte-identical to before, HEAD as before, and `git status --porcelain` prints nothing."""
    main = tmp / "main"
    assert (orders(main) / "errors.md").read_bytes() == was.errors, "main's errors.md changed"
    assert head(main) == was.head, "HEAD in <tmp>/main moved"
    status = git(main, "status", "--porcelain")
    assert status.exit == 0 and status.stdout == "", f"git status --porcelain in <tmp>/main: {status.stdout!r}"
