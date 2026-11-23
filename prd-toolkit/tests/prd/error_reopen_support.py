"""Shared helper of the error-reopen characterization tests (testing.md: Harness, Setup steps, error-reopen).

Everything here comes from docs/prd/prd-toolkit/testing.md and the header of
docs/prd/prd-toolkit/test-cases/error-reopen.yaml: the scratch repository <tmp> that steps N0, NE1 and NE2
(borrowed from status_next_support, testing.md Borrowed steps and helpers) and the file's own steps O0 to OS
build; the environment of every run, step command and git command; the way a run's text becomes its argument
list (ERROR, GATES, LINT and HELP replaced, shlex.split, a first word `python` the test's interpreter, no shell,
cwd <tmp>); `<today>` (Harness, Assertions: the date taken just before and just after a command, either
accepted); HEAD8; and the assertion keys the cases use.

A setup step that cannot be applied (a command that exits other than 0, a line or text it changes that is not
there) raises SetupError, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from status_next_support import N0, NE1, NE2  # testing.md, Borrowed steps and helpers

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
NAMES = {
    "ERROR": str(SCRIPTS_DIR / "prd_error.py"),
    "GATES": str(SCRIPTS_DIR / "prd_gates.py"),
    "LINT": str(SCRIPTS_DIR / "prd_lint.py"),
    "HELP": str(SCRIPTS_DIR / "prd_help.py"),
}
FILES_FIXTURE = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures" / "status-next" / "files.yaml"
ORDERS_REL = Path("docs") / "prd" / "orders"

# testing.md, Harness (Subprocess environment), and the case file's header: the variables no run inherits,
# and the two it gets.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_PLUGINS_FILE",
)
_ADDED_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung command ends the test

# Step OM's text (test-cases/error-reopen.yaml header), one line each.
OM_LINES = [
    "# Error ledger",
    "",
    "### E-001 The importer stops at row 1000",
    "Detected: 2026-11-03, a run on the October file",
    "Classification: code bug",
    "Touches: FR-003",
    "Resolution: -",
    "Recurrence of: -",
    "",
    "### E-002 A monthly report printed no total",
    "Detected: 2026-11-05, a reader of the October report",
    "Classification: unclassified",
    "Touches: FR-006",
    "Resolution: -",
    "Recurrence of: -",
    "",
    "### E-003 An import printed no count",
    "Detected: 2026-11-06, a run on the November file",
    "Classification: code bug",
    'Confirmed: 2026-11-07, "Yes."',
    "Touches: FR-004",
    "Resolution: not a defect: the file was empty",
    "Recurrence of: -",
]
OM_TEXT = "".join(line + "\n" for line in OM_LINES)


class SetupError(Exception):
    """A setup step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout_bytes: bytes
    stderr_bytes: bytes

    @property
    def stdout(self) -> str:
        return self.stdout_bytes.decode("utf-8")

    @property
    def stderr(self) -> str:
        return self.stderr_bytes.decode("utf-8")

    def describe(self) -> str:
        return f"\nexit {self.exit}\n--- stdout ---\n{self.stdout}--- stderr ---\n{self.stderr}"


def subprocess_env() -> dict[str, str]:
    """The environment of every run, step command and git command of an error-reopen case."""
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(_ADDED_ENV)
    return env


def argv(text: str) -> list[str]:
    """A run's text as its argument list: the names replaced, shlex.split, `python` the test's interpreter."""
    for name, value in NAMES.items():
        text = text.replace(name, value)
    words = shlex.split(text)
    if words and words[0] == "python":
        words[0] = sys.executable
    return words


def files(key: str) -> str:
    """files.<key>: the text at that key of fixture status-next/files."""
    data = yaml.safe_load(FILES_FIXTURE.read_text(encoding="utf-8"))
    if key not in data:
        raise SetupError(f"fixture status-next/files has no key {key!r}")
    return data[key]


@dataclass
class Case:
    """The scratch repository <tmp> of one case, and the dates its commands ran on."""

    tmp: Path
    dates: set[str] = field(default_factory=set)

    @property
    def orders(self) -> Path:
        return self.tmp / ORDERS_REL

    @property
    def errors_md(self) -> Path:
        return self.orders / "errors.md"

    def run(self, text: str) -> Result:
        """Run one command text with no shell, from <tmp>; the date before and after it is kept for <today>."""
        self.dates.add(datetime.date.today().isoformat())
        proc = subprocess.run(argv(text), cwd=self.tmp, env=subprocess_env(),
                              capture_output=True, timeout=RUN_TIMEOUT)
        self.dates.add(datetime.date.today().isoformat())
        return Result(proc.returncode, proc.stdout, proc.stderr)

    def git(self, *args: str) -> Result:
        proc = subprocess.run(["git", *args], cwd=self.tmp, env=subprocess_env(),
                              capture_output=True, timeout=RUN_TIMEOUT)
        return Result(proc.returncode, proc.stdout, proc.stderr)

    # -- step helpers --

    def step_git(self, *args: str) -> None:
        r = self.git(*args)
        if r.exit != 0:
            raise SetupError(f"step: git {' '.join(args)} exited {r.exit}:{r.describe()}")

    def step_run(self, text: str) -> None:
        r = self.run(text)
        if r.exit != 0:
            raise SetupError(f"step: {text!r} exited {r.exit}:{r.describe()}")

    def commit(self, *messages: str) -> None:
        """`git add -A`, then `git commit -q` with each message as its own -m."""
        self.step_git("add", "-A")
        args = ["commit", "-q"]
        for message in messages:
            args += ["-m", message]
        self.step_git(*args)

    def errors_text(self) -> str:
        if not self.errors_md.is_file():
            raise SetupError(f"step: {self.errors_md} does not exist")
        return self.errors_md.read_bytes().decode("utf-8")

    def write_errors(self, text: str) -> None:
        self.errors_md.parent.mkdir(parents=True, exist_ok=True)
        self.errors_md.write_bytes(text.encode("utf-8"))

    # -- what the tests read --

    def errors_bytes(self) -> bytes:
        return self.errors_md.read_bytes()

    def errors_lines(self) -> list[str]:
        return self.errors_md.read_bytes().decode("utf-8").splitlines()

    def head8(self) -> str:
        r = self.git("rev-parse", "HEAD")
        if r.exit != 0:
            raise SetupError(f"git rev-parse HEAD exited {r.exit}:{r.describe()}")
        return r.stdout.strip()[:8]


# -- the case file's own steps (test-cases/error-reopen.yaml header) --

def O0(c: Case) -> None:
    N0(c.tmp)
    c.step_git("config", "user.name", "Sample")
    c.step_git("config", "user.email", "sample@example.com")
    c.step_git("config", "commit.gpgsign", "false")
    c.step_git("config", "core.hooksPath", "/dev/null")


def OC(c: Case) -> None:
    NE1(c.tmp)


def OP(c: Case) -> None:
    NE2(c.tmp)


def OM(c: Case) -> None:
    c.write_errors(OM_TEXT)


def OK(c: Case) -> None:
    c.commit("base")
    c.step_git("tag", "start")


def OX(c: Case) -> None:
    c.step_run("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes now'")
    c.commit("docs(prd): reopen E-001", "Refs: E-001")


def OY(c: Case) -> None:
    c.step_run("python ERROR confirm docs/prd/orders E-001 --reply 'Yes, a code bug after all.'")
    c.commit("docs(prd): confirm E-001")


def OZ(c: Case) -> None:
    c.step_run("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes again'")
    c.commit("docs(prd): reopen E-001 again")


def OE(c: Case) -> None:
    text = c.errors_text()
    old, new = '"the run passes now"', '"the run passed"'
    if old not in text:
        raise SetupError(f"step OE: errors.md does not hold the text {old}")
    c.write_errors(text.replace(old, new))
    c.commit("edit the reopen")


def _one_index(lines: list[str], line: str, step: str) -> int:
    hits = [i for i, x in enumerate(lines) if x == line]
    if len(hits) != 1:
        raise SetupError(f"step {step}: expected one line {line!r} in errors.md, found {len(hits)}")
    return hits[0]


def OH(c: Case) -> None:
    lines = c.errors_text().splitlines()
    i = _one_index(lines, "Classification: unclassified", "OH")
    lines.insert(i + 1, 'Reopened: 2026-11-06, "no reason"; was Confirmed: 2026-11-05, "yes"')
    c.write_errors("".join(x + "\n" for x in lines))
    c.commit("add a reopen")


def OW(c: Case) -> None:
    lines = c.errors_text().splitlines()
    del lines[_one_index(lines, 'Confirmed: 2026-11-04, "Yes, it is a code bug."', "OW")]
    c.write_errors("".join(x + "\n" for x in lines))
    c.commit("drop the confirmation")


def OS(c: Case) -> None:
    path = c.tmp / "src" / "importer.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x = 1\n")
    c.commit("Fix the importer", "Refs: FR-003, E-001")


STEPS = {
    "O0": O0, "OC": OC, "OP": OP, "OM": OM, "OK": OK, "OX": OX, "OY": OY, "OZ": OZ,
    "OE": OE, "OH": OH, "OW": OW, "OS": OS,
}


def build(tmp: Path, monkeypatch, *steps: str) -> Case:
    """Set GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM in the test process, then run the case's steps in order."""
    for name, value in _ADDED_ENV.items():
        monkeypatch.setenv(name, value)
    c = Case(tmp)
    for step in steps:
        STEPS[step](c)
    return c


# -- expected values with <today> (testing.md, Harness, Assertions) --

def today_pattern(template: str, dates: set[str]) -> re.Pattern:
    """The template as a pattern in which each `<today>` is any of the dates the commands ran on."""
    if not dates:
        dates = {datetime.date.today().isoformat()}
    alt = "(?:" + "|".join(re.escape(d) for d in sorted(dates)) + ")"
    return re.compile(alt.join(re.escape(part) for part in template.split("<today>")), re.DOTALL)


def matches(actual: str, template: str, dates: set[str]) -> bool:
    return today_pattern(template, dates).fullmatch(actual) is not None


def assert_line(c: Case, n: int, template: str) -> None:
    """Line n (from 1) of errors.md is the template, <today> being a date a command ran on."""
    lines = c.errors_lines()
    assert len(lines) >= n, f"errors.md has {len(lines)} lines, no line {n}:\n" + "\n".join(lines)
    assert matches(lines[n - 1], template, c.dates), (
        f"line {n} of errors.md is {lines[n - 1]!r}, expected {template!r} (<today> in {sorted(c.dates)})")


def assert_lines(actual: list[str], templates: list[str], dates: set[str], what: str) -> None:
    ok = len(actual) == len(templates) and all(matches(a, t, dates) for a, t in zip(actual, templates))
    assert ok, f"{what}:\n" + "\n".join(actual) + "\nexpected:\n" + "\n".join(templates)


def entry_lines(lines: list[str], eid: str) -> list[str]:
    """An entry's lines: from its heading to its last line that is not empty before the next heading."""
    starts = [i for i, x in enumerate(lines) if x.startswith(f"### {eid} ")]
    assert len(starts) == 1, f"errors.md holds {len(starts)} headings of {eid}:\n" + "\n".join(lines)
    out = [lines[starts[0]]]
    for x in lines[starts[0] + 1:]:
        if x.startswith("#"):
            break
        out.append(x)
    while out and out[-1].strip() == "":
        out.pop()
    return out


def assert_run(r: Result, exit: int, stdout: str | None = None, stderr: str | None = None) -> None:
    """exit, and stdout and stderr compared byte for byte when given."""
    assert r.exit == exit, f"exit {r.exit}, expected {exit}" + r.describe()
    if stdout is not None:
        assert r.stdout_bytes == stdout.encode("utf-8"), f"stdout is not {stdout!r}" + r.describe()
    if stderr is not None:
        assert r.stderr_bytes == stderr.encode("utf-8"), f"stderr is not {stderr!r}" + r.describe()


def one_json_line(r: Result) -> dict:
    """stdout_json_at's requirement: the whole stdout is one line ending in a newline, one JSON object."""
    out = r.stdout
    assert out.endswith("\n") and len(out.splitlines()) == 1, "stdout is not one line" + r.describe()
    doc = json.loads(out)
    assert isinstance(doc, dict), "stdout is not a JSON object" + r.describe()
    return doc


def json_at(doc, path: str):
    """The value at a `.`-joined path of object keys and list indexes."""
    value = doc
    for part in path.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value
