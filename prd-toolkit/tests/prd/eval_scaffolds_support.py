"""Helpers for the eval-scaffolds cases (test-cases/eval-scaffolds.yaml).

Everything here comes from the case file's conventions and testing.md Harness:
- the Subprocess environment (the runner's, minus PYTHONIOENCODING, PYTHONPATH, PYTHONHOME, PRD_LINT_CI and
  PRD_HELP_FILE), minus GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE and GIT_COMMON_DIR, plus GIT_CONFIG_GLOBAL=/dev/null
  and GIT_CONFIG_NOSYSTEM=1, for every command of a case and every git command of its effects;
- DEPLOY_REPO run with the test's own interpreter as `python -B DEPLOY_REPO <dst> <state>`;
- "git in <dst>" is `git -C <dst> <arguments>`, which must exit 0, its stdout split by str.splitlines() with the
  empty lines at its start and at its end dropped.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # prd-toolkit/tests/prd/<file> -> the repository root
DEPLOY_REPO = REPO / "prd-toolkit/evals/scaffolds/deploy_repo.py"
REVIEW_EDITS_NOTHING_SCAFFOLD = REPO / "prd-toolkit/evals/review-edits-nothing/scaffold.sh"

_HARNESS_DROPPED = ("PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE")
_GIT_DROPPED = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR")
_GIT_ADDED = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def case_env() -> dict[str, str]:
    """The environment of every command of an eval-scaffolds case and of every git command of its effects."""
    env = dict(os.environ)
    for name in _HARNESS_DROPPED + _GIT_DROPPED:
        env.pop(name, None)
    env.update(_GIT_ADDED)
    return env


def run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run one command of a case, text mode, stdout and stderr captured, with no time limit."""
    return subprocess.run([str(a) for a in argv], cwd=cwd, env=case_env(),
                          capture_output=True, text=True)


def deploy_repo(dst: Path, state: str, cwd: Path) -> subprocess.CompletedProcess:
    """`python -B DEPLOY_REPO <dst> <state>` with the test's own interpreter and `cwd` as the working directory."""
    return run([sys.executable, "-B", DEPLOY_REPO, dst, state], cwd)


def describe(proc: subprocess.CompletedProcess) -> str:
    """A failure message: the exit code, stdout and stderr of a run."""
    return f"exit {proc.returncode}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"


def git_stdout(dst: Path, *args: str) -> str:
    """`git -C <dst> <args>`, which must exit 0; returns its whole stdout."""
    proc = subprocess.run(["git", "-C", str(dst), *args], env=case_env(), capture_output=True, text=True)
    assert proc.returncode == 0, f"git -C {dst} {' '.join(args)}: {describe(proc)}"
    return proc.stdout


def git_lines(dst: Path, *args: str) -> list[str]:
    """`git -C <dst> <args>` (exit 0 required), stdout split by str.splitlines(), leading and trailing empty lines dropped."""
    lines = git_stdout(dst, *args).splitlines()
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return lines
