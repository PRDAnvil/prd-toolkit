"""Shared helper of the hook-shims characterization tests (testing.md: Harness, Fixtures, Setup steps).

Everything here comes from docs/prd/prd-toolkit/testing.md: the hook-shims Setup steps HS0, HS1 and HS2, which
borrow step N0E from status_next_support (Borrowed steps and helpers), the hook-shims environment (the Subprocess
environment minus GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_COMMON_DIR and PRD_PLUGINS_FILE, plus
GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1), the way a CLI script runs (`python
<repo>/prd-toolkit/scripts/<script>` with the test's own interpreter), the fixture hook-shims/texts and the
assertion key `stdout_lines_in_this_relative_order`.

A setup step that cannot be applied raises SetupError inside the `scratch` fixture, so the test ends as an error,
not a failure.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from status_next_support import N0E  # testing.md, Borrowed steps and helpers

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
HOOKS = REPO / "prd-toolkit" / "scripts" / "prd_hooks.py"
TEXTS_FILE = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures" / "hook-shims" / "texts.yaml"
PRD_DIR = "docs/prd/orders"

# testing.md, Harness (Subprocess environment) and the hook-shims paragraph of Setup steps.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_PLUGINS_FILE",
)
_ADDED_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


def hook_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(_ADDED_ENV)
    return env


def run_hooks(cwd: Path, *args: str) -> Result:
    """Run `python HOOKS <args>` in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(HOOKS), *args],
        cwd=cwd, env=hook_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def texts() -> dict[str, str]:
    """Fixture hook-shims/texts, read with yaml.safe_load."""
    return yaml.safe_load(TEXTS_FILE.read_text(encoding="utf-8"))


def executable_by_owner(path: Path) -> bool:
    """The bit 0o100 is set in os.stat(path).st_mode."""
    return bool(os.stat(path).st_mode & 0o100)


# -- assertion keys (testing.md, Harness, Assertions) --

def assert_lines_in_relative_order(stdout: str, expected: list[str]) -> None:
    """Each listed line, whole, after the one before it, with other lines allowed between."""
    lines = stdout.splitlines()
    pos = 0
    for want in expected:
        try:
            pos = lines.index(want, pos) + 1
        except ValueError:
            raise AssertionError(f"line {want!r} not found (in this relative order) in stdout:\n{stdout}") from None


# -- setup steps (testing.md, Setup steps: hook-shims) --

def _git(repo: Path, *args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=repo, env=hook_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode} in {repo}: "
                         f"{proc.stderr.decode('utf-8', 'replace')}")


def _write_hook(path: Path, key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(texts()[key].encode("utf-8"))
    os.chmod(path, 0o755)


def HS0(tmp: Path) -> None:
    a, b = tmp / "a", tmp / "b"
    N0E(a)
    _git(a, "config", "core.hooksPath", ".git/hooks")
    N0E(b)
    for repo in (a, b):
        _write_hook(repo / ".git/hooks/commit-msg", "old_commit_msg")
        _write_hook(repo / ".git/hooks/pre-commit", "old_pre_commit")


def HS1(tmp: Path) -> None:
    N0E(tmp)
    _git(tmp, "config", "core.hooksPath", "hooks")
    _write_hook(tmp / "hooks/commit-msg", "edited_commit_msg")
    _write_hook(tmp / "hooks/pre-commit", "old_pre_commit")


def HS2(tmp: Path) -> None:
    N0E(tmp)
    _git(tmp, "config", "core.hooksPath", "hooks")
    _write_hook(tmp / "hooks/pre-commit", "own_pre_commit")


STEPS = {"HS0": HS0, "HS1": HS1, "HS2": HS2}


@pytest.fixture
def scratch(request, tmp_path, monkeypatch) -> Path:
    """<tmp>: the test's tmp_path, built by the case's setup steps in the order it lists them.

    GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM are set in the test's own process before the first step, so the
    borrowed step N0E's `git init` inherits them (testing.md, the hook-shims paragraph).
    """
    for name, value in _ADDED_ENV.items():
        monkeypatch.setenv(name, value)
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def given_steps(*steps: str):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=["+".join(steps)])
