"""Shared helper of the trace characterization tests (testing.md: Harness, Setup steps, the trace steps).

Everything here comes from docs/prd/prd-toolkit/testing.md and test-cases/trace.yaml: the scratch repository the
steps build in a test's tmp_path (step N0E borrowed from status_next_support, as Borrowed steps and helpers says),
the trace steps (TB, TU, TC9, TS:x, TL:x, TD, TA:x, TE, TEC, TK:x, TX, TM:t, TR:r, TV, SH:h,p, T256; TV borrows
load_vendored from lint_cli_support), the Subprocess environment minus GIT_DIR,
GIT_WORK_TREE, GIT_INDEX_FILE and GIT_COMMON_DIR, the way a CLI script runs (`python <repo>/prd-toolkit/scripts/
<script>` with the test's own interpreter), and the assertion keys the trace cases use.

A step that cannot be applied (a git command that exits other than 0, a line a step edits that does not hold the
text the step names) raises SetupError inside the `scratch` fixture, so the test ends as an error, not a failure.

Every `@prd` citation text a step writes is built from parts (testing.md, Layout), since this file lies under this
PRD's test root.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

import lint_cli_support
import status_next_support

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
TRACE = REPO / "prd-toolkit" / "scripts" / "prd_trace.py"
HOOK = REPO / "prd-toolkit" / "scripts" / "prd_git_hook.py"
EMPTY_FIXTURE = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures" / "status-next" / "empty.yaml"
ORDERS_REL = Path("docs") / "prd" / "orders"

AT_PRD = "@" + "prd"

# testing.md, Subprocess environment, and the trace paragraph of Setup steps: the variables a run never inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
)
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test


class SetupError(Exception):
    """A step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


def cite(tid: str, rest: str = "") -> str:
    """The comment line `# @prd <tid><rest>`, built from parts."""
    return "# " + AT_PRD + " " + tid + rest


def subprocess_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(extra or {})
    return env


def run_trace(cwd: Path, *args: str, env: dict[str, str] | None = None) -> Result:
    """Run `python TRACE <args>` in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(TRACE), *args],
        cwd=cwd, env=subprocess_env(env), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def orders(tmp: Path) -> Path:
    return tmp / ORDERS_REL


# -- file edits: lines numbered from 1; every line a step writes ends in a newline --

def _read(path: Path) -> list[str]:
    """The file's lines, without their newlines (a final newline gives no extra entry)."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("".join(line + "\n" for line in lines)).encode("utf-8"))


def _check_line(lines: list[str], path: Path, n: int) -> None:
    if not 1 <= n <= len(lines):
        raise SetupError(f"{path}: has no line {n} ({len(lines)} lines)")


def replace_line(path: Path, n: int, new: list[str] | str, old: str | None = None) -> None:
    """Line `n` becomes the line(s) `new`; when `old` is given, line `n` must be exactly `old`."""
    lines = _read(path)
    _check_line(lines, path, n)
    if old is not None and lines[n - 1] != old:
        raise SetupError(f"{path}:{n} is {lines[n - 1]!r}, not {old!r}")
    lines[n - 1:n] = [new] if isinstance(new, str) else list(new)
    write_lines(path, lines)


def replace_in_line(path: Path, n: int, old: str, new: str) -> None:
    """In line `n`, the text `old`, which it must hold once, becomes `new`."""
    lines = _read(path)
    _check_line(lines, path, n)
    if lines[n - 1].count(old) != 1:
        raise SetupError(f"{path}:{n} holds {old!r} {lines[n - 1].count(old)} times, not once")
    lines[n - 1] = lines[n - 1].replace(old, new)
    write_lines(path, lines)


def insert_after(path: Path, n: int, new: list[str]) -> None:
    lines = _read(path)
    _check_line(lines, path, n)
    lines[n:n] = new
    write_lines(path, lines)


def delete_line(path: Path, n: int, old: str) -> None:
    lines = _read(path)
    _check_line(lines, path, n)
    if lines[n - 1] != old:
        raise SetupError(f"{path}:{n} is {lines[n - 1]!r}, not {old!r}")
    del lines[n - 1]
    write_lines(path, lines)


def append_line(path: Path, line: str) -> int:
    """Append `line`; return its line number."""
    lines = _read(path)
    lines.append(line)
    write_lines(path, lines)
    return len(lines)


def git(tmp: Path, *args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


# -- the steps (testing.md, Setup steps: N0E and the trace steps) --

def N0E(tmp: Path) -> None:
    status_next_support.N0E(tmp)


def N0E_NO_GIT(tmp: Path) -> None:
    """T-083.4: fixture status-next/empty written with no git init; <tmp> must lie outside every git checkout."""
    for key, text in yaml.safe_load(EMPTY_FIXTURE.read_text(encoding="utf-8")).items():
        path = tmp / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=tmp, env=subprocess_env(),
                          capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode == 0:
        raise SetupError(f"{tmp} lies inside a git checkout: {proc.stdout.decode('utf-8', 'replace').strip()}")


def TB(tmp: Path) -> None:
    git(tmp, "config", "user.name", "Sample")
    git(tmp, "config", "user.email", "sample@example.com")
    git(tmp, "config", "commit.gpgsign", "false")
    git(tmp, "config", "core.hooksPath", "/dev/null")
    git(tmp, "add", "-A")
    git(tmp, "commit", "-q", "-m", "base", "-m", "Refs: none (no behaviour change)")


def TU(tmp: Path) -> None:
    delete_line(tmp / "tests/test_orders.py", 2, cite("T-001.1"))


def TC9(tmp: Path) -> None:
    replace_line(tmp / "tests/test_orders.py", 2, cite("T-009.1"))


def TS(tmp: Path, x: str) -> None:
    replace_line(orders(tmp) / "features/import.md", 4, f"Status: {x}")


def TL(tmp: Path, x: str) -> None:
    replace_line(orders(tmp) / "features/import.md", 8, f"Tests: T-001.1 [{x}]  (test-cases/import.yaml)")


def TD(tmp: Path) -> None:
    insert_after(orders(tmp) / "testing.md", 8, ["| system | `pytest tests/system` | local | deploy |"])


def TA(tmp: Path, x: str) -> None:
    replace_line(orders(tmp) / "prd.md", 57, "See adoption.md.")
    write_lines(orders(tmp) / "adoption.md",
                ["# Adoption map", "", "| Area | State | Boundary |", "|---|---|---|", f"| import | {x} | `src/**` |"])


TE_LINES = [
    "# Error ledger", "",
    "### E-001 A blank file passes", "Detected: 2026-11-01, a test run", "Classification: code bug",
    "Touches: FR-001", "Diagnosis: the check reads only the first line", "Resolution: open", "Recurrence of: -", "",
    "### E-002 An old crash", "Detected: 2026-10-01, a test run", "Classification: code bug", "Touches: FR-001",
    "Diagnosis: fixed", "Resolution: T-001.1 [integration], PRD 1.0.0, fixed in abc1234", "Recurrence of: -",
]


def TE(tmp: Path) -> None:
    write_lines(orders(tmp) / "errors.md", TE_LINES)


def TEC(tmp: Path) -> None:
    TE(tmp)
    insert_after(orders(tmp) / "errors.md", 5, ['Confirmed: 2026-11-02, "yes, a code bug"'])


def TK(tmp: Path, x: str) -> None:
    insert_after(orders(tmp) / "test-cases/import.yaml", 2, [f"  known-failing: {x}"])


def TX(tmp: Path) -> None:
    write_lines(tmp / "src/app.py", ["x = 1"])
    git(tmp, "add", "src/app.py")


def TM(tmp: Path, t: str | list[str]) -> None:
    """Write <tmp>/msg.txt with the text t: one line, or each line of a list, each ending in a newline."""
    write_lines(tmp / "msg.txt", [t] if isinstance(t, str) else list(t))


def T256(tmp: Path) -> None:
    N0E(tmp)
    shutil.rmtree(tmp / ".git")
    git(tmp, "init", "-q", "--object-format=sha256")


def git_out(tmp: Path, *args: str) -> str:
    """A git command's stdout, less its newline; exits other than 0 raise SetupError."""
    proc = subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout.decode("utf-8").rstrip("\n")


def run_hook(cwd: Path, *args: str, env: dict[str, str] | None = None) -> Result:
    """Run `python HOOK <args>` in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(HOOK), *args],
        cwd=cwd, env=subprocess_env(env), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def run_command(cwd: Path, command: str | list[str], env: dict[str, str] | None = None) -> Result:
    """Run a case's command (`sh …`, `git commit …`) with no shell: a string is split as shell words
    (shlex.split); stdout and stderr decoded as UTF-8."""
    argv = shlex.split(command) if isinstance(command, str) else list(command)
    proc = subprocess.run(argv, cwd=cwd, env=subprocess_env(env), capture_output=True, timeout=RUN_TIMEOUT)
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


# -- TR, TV and SH (testing.md, Setup steps: the trace steps) --

TR_HEADER = "| Object (glob) | Linter command | Rules live in | Applies to | Decision |"
TR_SEPARATOR = "|---|---|---|---|---|"


def standards_row(linter_cell: str, decision: str = "enforced") -> str:
    """One section 5 row as the FR-094 cases describe it: glob `**/*.py`, Rules live in `-`, Applies to `code`.

    `linter_cell` is the Linter command cell's whole text, backticks included when the case puts them there.
    """
    return f"| `**/*.py` | {linter_cell} | - | code | {decision} |"


def TR(tmp: Path, rows: list[str]) -> None:
    """In prd.md line 43, `Not applicable: the fixture runs no linter.`, becomes the header, separator and rows."""
    replace_line(orders(tmp) / "prd.md", 43, [TR_HEADER, TR_SEPARATOR, *rows],
                 old="Not applicable: the fixture runs no linter.")


def TV(tmp: Path) -> None:
    """Fixture repo/vendored into <tmp>/.prd-toolkit, borrowed from lint_cli_support (Borrowed steps and helpers)."""
    lint_cli_support.load_vendored(tmp)


TEMPLATES = REPO / "prd-toolkit" / "templates" / "hooks"


def filled_template(h: str, p: str) -> str:
    """The template <repo>/prd-toolkit/templates/hooks/<h>, `{{hook}}` replaced by h and `{{prd}}` by p."""
    text = (TEMPLATES / h).read_text(encoding="utf-8")
    return text.replace("{{hook}}", h).replace("{{prd}}", p)


def SH(tmp: Path, value: str) -> None:
    """`SH:h,p`: write the filled template to <tmp>/.git/hooks/<h>, mode 0o755."""
    h, p = value.split(",", 1)
    path = tmp / ".git" / "hooks" / h
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(filled_template(h, p).encode("utf-8"))
    os.chmod(path, 0o755)


_PLAIN = {"N0E": N0E, "TB": TB, "TU": TU, "TC9": TC9, "TD": TD, "TE": TE, "TEC": TEC, "TX": TX, "T256": T256,
          "TV": TV}
_WITH_VALUE = {"TS": TS, "TL": TL, "TA": TA, "TK": TK, "TM": TM, "SH": SH}


def apply(tmp: Path, step: str | Callable[[Path], None]) -> None:
    """A step by its name (`TS:x` takes the text after its colon as x), or a case's own step as a callable."""
    if callable(step):
        step(tmp)
    elif ":" in step:
        name, value = step.split(":", 1)
        _WITH_VALUE[name](tmp, value)
    else:
        _PLAIN[step](tmp)


@pytest.fixture
def scratch(request, tmp_path) -> Path:
    """<tmp>: the test's tmp_path as its resolved absolute path, built by the case's steps in the order it lists them."""
    tmp = tmp_path.resolve()
    for step in request.param:
        apply(tmp, step)
    return tmp


def given_steps(*steps: str | Callable[[Path], None]):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    ids = "+".join(s if isinstance(s, str) else s.__name__ for s in steps) or "none"
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=[ids])


# -- assertion keys (testing.md, Harness, Assertions) --

def one_json_line(stdout: str) -> dict:
    """The whole stdout must be one line ending in a newline; that line parsed as one JSON object."""
    assert stdout.endswith("\n") and len(stdout.splitlines()) == 1, f"stdout is not one line:\n{stdout}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{stdout}"
    return doc


def assert_exact_lines(stdout: str, lines: list[str]) -> None:
    assert stdout.splitlines() == lines, f"stdout:\n{stdout}"


def assert_single_line_starts(text: str, prefix: str) -> None:
    lines = text.splitlines()
    assert len(lines) == 1 and lines[0].startswith(prefix), f"not one line starting {prefix!r}:\n{text}"
