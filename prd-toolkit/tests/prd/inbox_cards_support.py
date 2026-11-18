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


STEPS = {"IC0": IC0, "IC2": IC2, "ICN": ICN, "ICT": ICT, "ICD": ICD}


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
