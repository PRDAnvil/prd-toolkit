"""Shared helper of the card-context characterization tests (docs/prd/prd-toolkit/test-cases/card-context.yaml).

Everything here comes from docs/prd/prd-toolkit/testing.md (Harness, Fixtures, Setup steps, Borrowed steps and
helpers) and the conventions at the top of test-cases/card-context.yaml:

- the card-context Setup steps (C1, CE, CK, CS, CB, CA1, CA2, CL1, CT2, CT3, CT5), defined here;
- the borrowed status-next steps (N0, NE1, NE2, NR3, NR4, NA1), imported from status_next_support.py with the
  calls the table Borrowed steps and helpers gives;
- the Subprocess environment of a card-context run, which drops PRD_PLUGINS_FILE and the git variables as well;
- the assertion keys the cases use (stdout_json_at, stdout_json_keys_at, stdout_lines_in_this_relative_order, ...).

A setup step that cannot be applied (a line it edits that is not there, a command it runs that fails) raises
SetupError inside the `scratch` fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

# Borrowed steps (testing.md, Borrowed steps and helpers): status_next_support.N0(tmp), NE1, NE2, NR3, NR4, NA1.
from status_next_support import N0, NA1, NE1, NE2, NR3, NR4

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
SCRIPTS = {
    "GATES": SCRIPTS_DIR / "prd_gates.py",
    "ERROR": SCRIPTS_DIR / "prd_error.py",
    "LINT": SCRIPTS_DIR / "prd_lint.py",
    "STATUS": SCRIPTS_DIR / "prd_status.py",
    "HELP": SCRIPTS_DIR / "prd_help.py",
}
CHANGE = SCRIPTS_DIR / "prd_change.py"  # step CA1's `prd_change.py digest .`
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_REL = Path("docs") / "prd" / "orders"

# testing.md: the Subprocess environment's dropped variables, the git variables the Setup steps drop, and
# PRD_PLUGINS_FILE, which every run of a card-context case and every command of its steps removes as well.
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


def clear_env(monkeypatch) -> None:
    """The same environment rules for an in-process call (testing.md, In-process calls), set through monkeypatch."""
    for name in DROPPED_ENV:
        monkeypatch.delenv(name, raising=False)


def run(cwd: Path, script: str, *args: str) -> Result:
    """Run `python <SCRIPT> <args>` (GATES, ERROR, LINT, STATUS or HELP) in `cwd`; output decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS[script]), *args],
        cwd=cwd, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def orders(tmp: Path) -> Path:
    """ORDERS, the PRD folder the setup steps write."""
    return tmp / ORDERS_REL


def today() -> datetime.date:
    """`<today>` (testing.md, Assertions): the local date, as datetime.date.today() gives it."""
    return datetime.date.today()


# -- fixtures (testing.md, Fixtures) --

def fixture_text(name: str, key: str) -> str:
    """The text at `key` of fixture `name` (`card-context/files` or `status-next/files`), read with yaml.safe_load."""
    data = yaml.safe_load((FIXTURES / f"{name}.yaml").read_text(encoding="utf-8"))
    return data[key]


def files(key: str) -> str:
    """`files.<key>` of fixture card-context/files."""
    return fixture_text("card-context/files", key)


def status_next_files(key: str) -> str:
    """`files.<key>` of fixture status-next/files, where a case says so."""
    return fixture_text("status-next/files", key)


# -- assertion keys (testing.md, Harness, Assertions) --

def one_json_line(stdout: str) -> dict:
    """The whole stdout must be one line ending in a newline; that line parsed as one JSON object."""
    assert stdout.endswith("\n") and "\n" not in stdout[:-1], f"stdout is not one line ending in a newline:\n{stdout!r}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{stdout}"
    return doc


def json_at(doc, path: str):
    """The value at a `.`-joined path of object keys and list indexes (`""` is the document itself)."""
    node = doc
    if path == "":
        return node
    for part in path.split("."):
        if isinstance(node, list):
            index = int(part)
            assert 0 <= index < len(node), f"{path!r}: index {index} is past the list's {len(node)} entries"
            node = node[index]
        else:
            assert isinstance(node, dict), f"{path!r}: {part!r} reached a {type(node).__name__}"
            assert part in node, f"{path!r}: no key {part!r} in {sorted(node)}"
            node = node[part]
    return node


def json_equal(a, b) -> bool:
    """Equality of two JSON values that keeps a bool apart from a number, a number apart from a string and
    null apart from everything else; object key order is not compared here (stdout_json_keys_at does that)."""
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


def assert_json_at(stdout: str, expected: dict) -> None:
    """stdout_json_at: the value at each path equals the mapping's; nothing else is compared."""
    doc = one_json_line(stdout)
    for path, want in expected.items():
        got = json_at(doc, path)
        assert json_equal(got, want), f"at {path!r}: {got!r} != {want!r}"


def assert_json_keys_at(stdout: str, expected: dict) -> None:
    """stdout_json_keys_at: the exact list of the keys of the object at each path, in order."""
    doc = one_json_line(stdout)
    for path, want in expected.items():
        node = json_at(doc, path)
        assert isinstance(node, dict), f"{path!r} is not an object: {node!r}"
        assert list(node.keys()) == want, f"keys at {path!r}: {list(node.keys())} != {want}"


def assert_lines_in_relative_order(stdout: str, expected: list[str]) -> None:
    """stdout_lines_in_this_relative_order: each line, whole, after the one before it, others allowed between."""
    lines = stdout.splitlines()
    pos = 0
    for want in expected:
        try:
            pos = lines.index(want, pos) + 1
        except ValueError:
            raise AssertionError(f"line {want!r} not found (in order) in stdout:\n{stdout}") from None


def assert_not_contains(stdout: str, absent) -> None:
    """stdout_not_contains: a substring, or each string of a list, that stdout must not hold anywhere."""
    for text in [absent] if isinstance(absent, str) else absent:
        assert text not in stdout, f"stdout holds {text!r}:\n{stdout}"


# -- the card-context Setup steps (testing.md, Setup steps) --

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise SetupError(f"{path} is missing")
    return path.read_text(encoding="utf-8").split("\n")


def _write_lines(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def _append_text(path: Path, text: str) -> None:
    if not path.is_file():
        raise SetupError(f"{path} is missing")
    old = path.read_text(encoding="utf-8")
    if old and not old.endswith("\n"):
        old += "\n"
    path.write_bytes((old + text).encode("utf-8"))


def _set_target_line(path: Path, new: str) -> None:
    """Line 3 of a features file becomes `new`; line 3 must be its `Target:` line (written by C1)."""
    lines = _read_lines(path)
    if len(lines) < 3 or not lines[2].startswith("Target:"):
        raise SetupError(f"{path}: line 3 is not a `Target:` line")
    lines[2] = new
    _write_lines(path, lines)


def _git(tmp: Path, *args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


def C1(tmp: Path) -> None:
    folder = orders(tmp)
    _write(folder / "features/import.md", files("features_import"))
    _write(folder / "features/reports.md", files("features_reports"))


def CE(tmp: Path) -> None:
    _write(orders(tmp) / "errors.md", files("errors_cards"))


def CK(tmp: Path) -> None:
    path = orders(tmp) / "test-cases/import.yaml"
    lines = _read_lines(path)
    if len(lines) < 2 or lines[1] != "  ac: AC-001.1":
        raise SetupError(f"{path}: line 2 is not `  ac: AC-001.1`")
    lines.insert(2, "  known-failing: E-003")
    _write_lines(path, lines)


def CS(tmp: Path) -> None:
    _append_text(orders(tmp) / "test-cases/reports.yaml", files("case_acceptance"))


def CB(tmp: Path) -> None:
    path = orders(tmp) / "features/billing.md"
    if not path.is_file():
        raise SetupError("CB runs after NA1: features/billing.md is missing")
    _write(path, files("features_billing"))


def _verdict(tmp: Path, touches: list[str]) -> None:
    """CA1's body: the branch `cards`, a pending changelog row, then the verdict, written last."""
    folder = orders(tmp)
    _git(tmp, "symbolic-ref", "HEAD", "refs/heads/cards")
    _append_text(folder / "prd.md", "| 1.1.0 | 2026-11-12 | a report change; pending | FR-001 |\n")
    proc = subprocess.run([sys.executable, str(CHANGE), "digest", "."], cwd=folder, env=subprocess_env(),
                          capture_output=True, timeout=RUN_TIMEOUT)
    out = proc.stdout.decode("utf-8", "replace")
    if proc.returncode != 0 or len(out.splitlines()) != 1:
        raise SetupError(f"prd_change.py digest . exited {proc.returncode} with stdout {out!r}: "
                         f"{proc.stderr.decode('utf-8', 'replace')}")
    digest = out.splitlines()[0]
    touches_json = "[" + ", ".join(f'"{t}"' for t in touches) + "]"
    _write(folder / ".prd-review.json",
           '{"digest": "' + digest + '", "touches": ' + touches_json
           + ', "dry_run": {"record": "dry run T-001.1"}, "ready": true}\n')


def CA1(tmp: Path) -> None:
    _verdict(tmp, ["FR-001"])


def CA2(tmp: Path) -> None:
    _verdict(tmp, ["T-001.1", "AC-005.1", "README"])


def CL1(tmp: Path) -> None:
    _write(orders(tmp) / "errors.md", files("errors_lint"))


def CT2(tmp: Path) -> None:
    folder = orders(tmp)
    _set_target_line(folder / "features/import.md", "Target: url ftp://example.com/orders")
    _set_target_line(folder / "features/reports.md", "Target: output language en, url https://example.com/a b")


def CT3(tmp: Path) -> None:
    _set_target_line(orders(tmp) / "features/import.md",
                     "Target: pack service 1.0.0 (prd-toolkit), output language en, "
                     "url https://example.com/orders/import?a=1,b=2")


def CT5(tmp: Path) -> None:
    _set_target_line(orders(tmp) / "features/reports.md",
                     "Target: output language en, pack service 1.0.0 (prd-toolkit)")


STEPS = {
    "N0": N0, "NE1": NE1, "NE2": NE2, "NR3": NR3, "NR4": NR4, "NA1": NA1,
    "C1": C1, "CE": CE, "CK": CK, "CS": CS, "CB": CB, "CA1": CA1, "CA2": CA2, "CL1": CL1,
    "CT2": CT2, "CT3": CT3, "CT5": CT5,
}

FULL_STATE = ("N0", "C1", "CE", "CK", "CS", "NR3", "NA1", "CB", "CA1")


@pytest.fixture
def scratch(request, tmp_path) -> Path:
    """<tmp>: the scratch repository, built by the case's setup steps in the order it lists them."""
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def given_steps(*steps: str):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=["+".join(steps)])
