"""Shared helper of the tester-paths characterization tests (testing.md: Harness, Setup steps).

Everything here comes from docs/prd/prd-toolkit/testing.md: the tester-paths Setup steps TP0 to TP5, which borrow
step N0 from status_next_support (Borrowed steps and helpers), the tester-paths environment (the Subprocess
environment minus GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_COMMON_DIR and PRD_PLUGINS_FILE, plus
GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1), and the way a CLI script runs (`python
<repo>/prd-toolkit/scripts/<script>` with the test's own interpreter).

A relative path in a step is relative to <tmp>, the root of the scratch repository. A step whose git command exits
other than 0, or that does not find the line or the text it is to change, raises SetupError inside the `scratch`
fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from status_next_support import N0  # testing.md, Borrowed steps and helpers

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
CHECK = REPO / "prd-toolkit" / "scripts" / "prd_build_check.py"
PRD_DIR = "docs/prd/orders"

# A citation of another PRD's T-id is built from parts (testing.md, Layout), never written whole.
AT_PRD = "@" + "prd"

# testing.md, Harness (Subprocess environment) and the tester-paths paragraph of Setup steps.
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


def tp_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(_ADDED_ENV)
    return env


def run_check(cwd: Path, *args: str) -> Result:
    """Run `python CHECK <args>` in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(CHECK), *args],
        cwd=cwd, env=tp_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


# -- setup steps (testing.md, Setup steps: tester-paths) --

def _git(tmp: Path, *args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=tmp, env=tp_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode} in {tmp}: "
                         f"{proc.stderr.decode('utf-8', 'replace')}")


def _commit(tmp: Path, message: str) -> None:
    """Step wording `commit <message>`: git add -A, then git commit -q -m <message>."""
    _git(tmp, "add", "-A")
    _git(tmp, "commit", "-q", "-m", message)


def _write(path: Path, lines: list[str]) -> None:
    """Write a file holding the given lines and nothing else, each ending in a newline, as UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("".join(line + "\n" for line in lines).encode("utf-8"))


def _append(path: Path, line: str) -> None:
    if not path.is_file():
        raise SetupError(f"{path}: no such file to append to")
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_bytes((text + line + "\n").encode("utf-8"))


def _layout_line(testing_md: Path) -> tuple[list[str], int]:
    """The lines of testing.md and the index of the one line that starts with `- **Layout.**`."""
    if not testing_md.is_file():
        raise SetupError(f"{testing_md}: no such file")
    lines = testing_md.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith("- **Layout.**")]
    if len(hits) != 1:
        raise SetupError(f"expected one line starting with '- **Layout.**' in {testing_md}, found {len(hits)}")
    return lines, hits[0]


def TP0(tmp: Path) -> None:
    N0(tmp)
    _git(tmp, "config", "user.name", "Sample")
    _git(tmp, "config", "user.email", "sample@example.com")
    _git(tmp, "config", "commit.gpgsign", "false")
    _git(tmp, "config", "core.hooksPath", "/dev/null")
    _write(tmp / "scaffolds/make_repo.py", ["# builds a demo repository", "# " + AT_PRD + " T-002.1"])
    _write(tmp / "tests-old/test_old.py", ["# " + AT_PRD + " T-003.1"])
    _write(tmp / "checks/test_a.py", ["# " + AT_PRD + " T-004.1"])
    _write(tmp / "src/app.py", ["x = 1"])
    _commit(tmp, "base")
    _git(tmp, "tag", "base")


def TP1(tmp: Path) -> None:
    for rel in ("scaffolds/make_repo.py", "tests-old/test_old.py", "checks/test_a.py", "src/app.py"):
        _append(tmp / rel, "y = 2")
    _commit(tmp, "edit outside the tests")


def TP2(tmp: Path) -> None:
    _append(tmp / "tests/test_orders.py", "y = 2")
    _commit(tmp, "edit a test")


def TP3(tmp: Path) -> None:
    _git(tmp, "mv", "tests/test_orders.py", "scaffolds/test_orders.py")
    _git(tmp, "mv", "tests-old/test_old.py", "tests/test_old.py")
    _commit(tmp, "move two files")


def TP4(tmp: Path) -> None:
    testing_md = tmp / PRD_DIR / "testing.md"
    lines, i = _layout_line(testing_md)
    old, new = "Test roots: `tests/`", "Test roots: `checks/`"
    if old not in lines[i]:
        raise SetupError(f"the Layout line of {testing_md} does not hold {old!r}")
    lines[i] = lines[i].replace(old, new)
    testing_md.write_bytes("\n".join(lines).encode("utf-8"))
    _commit(tmp, "another test root")
    _git(tmp, "tag", "-f", "base")


def TP5(tmp: Path) -> None:
    testing_md = tmp / PRD_DIR / "testing.md"
    lines, i = _layout_line(testing_md)
    tail = " Test roots: `tests/`"  # its last 21 characters: a space and Test roots: `tests/`
    if len(tail) != 21 or not lines[i].endswith(tail):
        raise SetupError(f"the Layout line of {testing_md} does not end with {tail!r}")
    lines[i] = lines[i][: -len(tail)]
    end = "`" + AT_PRD + " T-001.1`."
    if not lines[i].endswith(end):
        raise SetupError(f"the Layout line of {testing_md} does not end with {end!r} after TP5")
    testing_md.write_bytes("\n".join(lines).encode("utf-8"))
    _commit(tmp, "no test roots text")
    _git(tmp, "tag", "-f", "base")


STEPS = {"TP0": TP0, "TP1": TP1, "TP2": TP2, "TP3": TP3, "TP4": TP4, "TP5": TP5}


@pytest.fixture
def scratch(request, tmp_path, monkeypatch) -> Path:
    """<tmp>: the scratch repository, built by the case's setup steps in the order it lists them.

    GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM are set in the test's own process before the first step, so the
    borrowed step N0's `git init` inherits them (testing.md, the tester-paths paragraph).
    """
    for name, value in _ADDED_ENV.items():
        monkeypatch.setenv(name, value)
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def given_steps(*steps: str):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=["+".join(steps)])
