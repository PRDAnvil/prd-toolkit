"""Shared helper of the context-notes characterization tests (docs/prd/prd-toolkit/test-cases/context-notes.yaml).

Everything here comes from docs/prd/prd-toolkit/testing.md (Harness, Fixtures, Setup steps, Borrowed steps and
helpers) and the conventions at the top of test-cases/context-notes.yaml:

- the context-notes Setup steps CN1, CN2 and CNB, defined here;
- the borrowed status-next step N0, imported from status_next_support.py with the call the table Borrowed steps
  and helpers gives (`status_next_support.N0(tmp: Path) -> None`);
- the Subprocess environment of a context-notes run, which drops PRD_PLUGINS_FILE and the git variables as well;
- the assertion keys the cases use (pack_part_titles, pack_part_lines, stdout_json's comparison of values).

A setup step that cannot be applied raises SetupError inside the `scratch` fixture, so the test ends as an
error, not a failure.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

# Borrowed step (testing.md, Borrowed steps and helpers): status_next_support.N0(tmp).
from status_next_support import N0

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
CONTEXT = REPO / "prd-toolkit" / "scripts" / "prd_context.py"
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_REL = Path("docs") / "prd" / "orders"

# testing.md: the Subprocess environment's dropped variables, the git variables the status-next steps drop, and
# PRD_PLUGINS_FILE, which every run of a context-notes case and every command of its steps removes as well.
DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
    "PRD_PLUGINS_FILE",
)
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


def subprocess_env() -> dict[str, str]:
    """The test process's environment when the command starts, minus DROPPED_ENV."""
    env = dict(os.environ)
    for name in DROPPED_ENV:
        env.pop(name, None)
    return env


def run_context(cwd: Path, *args: str) -> Result:
    """Run `python CONTEXT <args>` in `cwd` with the test's own interpreter; output decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(CONTEXT), *args],
        cwd=cwd, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def orders(tmp: Path) -> Path:
    """The PRD folder the setup steps write, `<tmp>/docs/prd/orders`."""
    return tmp / ORDERS_REL


# -- fixtures (testing.md, Fixtures) --

def texts(key: str) -> str:
    """`texts.<key>`: the text at `key` of fixture context-notes/texts, read with yaml.safe_load."""
    data = yaml.safe_load((FIXTURES / "context-notes" / "texts.yaml").read_text(encoding="utf-8"))
    return data[key]


# -- assertion keys (testing.md, Harness, Assertions) --

def pack_part_titles(stdout: str) -> list[str]:
    """The stdout lines (str.splitlines()) that start with `## `, in order."""
    return [line for line in stdout.splitlines() if line.startswith("## ")]


def pack_part_lines(stdout: str, title: str) -> list[str]:
    """The lines from the line `## <title>`, which stdout must hold exactly once, up to, not including, the
    next line that starts with `## `, or to the end of stdout."""
    lines = stdout.splitlines()
    heading = f"## {title}"
    count = lines.count(heading)
    assert count == 1, f"stdout holds the line {heading!r} {count} times, not once:\n{stdout}"
    start = lines.index(heading)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return lines[start:end]


def parts_of(stdout: str) -> list[tuple[str, list[str]]]:
    """Every part of a text pack, in order: (title, its lines from `## <title>` up to, not including, the next
    stdout line that starts with `## `, or to the end of stdout)."""
    out: list[tuple[str, list[str]]] = []
    for line in stdout.splitlines():
        if line.startswith("## "):
            out.append((line[3:], [line]))
        elif out:
            out[-1][1].append(line)
    return out


def one_json_line(stdout: str) -> dict:
    """The whole stdout must be one line ending in a newline; that line parsed as one JSON object."""
    assert stdout.endswith("\n") and "\n" not in stdout[:-1], f"stdout is not one line ending in a newline:\n{stdout!r}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{stdout}"
    return doc


def json_equal(a, b) -> bool:
    """stdout_json's comparison of a value: a bool apart from a number, a number apart from a string and null
    apart from everything else; object key order is not compared here."""
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) or isinstance(b, (int, float)):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and a == b
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys()
                and all(json_equal(a[k], b[k]) for k in a))
    if isinstance(a, list) or isinstance(b, list):
        return (isinstance(a, list) and isinstance(b, list) and len(a) == len(b)
                and all(json_equal(x, y) for x, y in zip(a, b)))
    return type(a) is type(b) and a == b


# -- the context-notes Setup steps (testing.md, Setup steps) --

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _replace(path: Path, text: str) -> None:
    """Write `text` to `path`, in place of its text; the file must be there (N0 wrote it)."""
    if not path.is_file():
        raise SetupError(f"{path} is missing")
    _write(path, text)


def CN1(tmp: Path) -> None:
    _replace(orders(tmp) / "features/import.md", texts("features_import_notes"))


def CN2(tmp: Path) -> None:
    _replace(orders(tmp) / "features/import.md", texts("features_import_quiet"))


def CNB(tmp: Path) -> None:
    b = tmp / "b"
    N0(b)
    _replace(orders(b) / "features/import.md", texts("features_import_blank"))


STEPS = {"N0": N0, "CN1": CN1, "CN2": CN2, "CNB": CNB}


@pytest.fixture
def scratch(request, tmp_path) -> Path:
    """<tmp>: the scratch repository, built by the case's setup steps in the order it lists them."""
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def given_steps(*steps: str):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=["+".join(steps)])
