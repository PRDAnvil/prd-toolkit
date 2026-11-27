"""Shared helper of the change characterization tests (testing.md: Harness, Setup steps, the change paragraph).

Everything here comes from docs/prd/prd-toolkit/testing.md and the header of test-cases/change.yaml: the
scratch repository the steps build in a test's tmp_path, the Subprocess environment of a change case, the way a
command text becomes an argument list, the header's setup steps (G0 to GZ, R) and DRY, and the assertion keys the
change cases use.

A step that fails while the case's `setup:` is built (inside the `case` fixture) ends the test as an error; a step
that fails in a run's `setup_before`, inside the test body, raises StepError, whose message names the step and the
line or text it did not find.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from status_next_support import N0, N0X, SetupError

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
SCRIPTS = {
    "CHANGE": SCRIPTS_DIR / "prd_change.py",
    "BLOCK": SCRIPTS_DIR / "prd_block.py",
    "HOOKS": SCRIPTS_DIR / "prd_hooks.py",
}
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
PLUGINS_NONE = FIXTURES / "lint-cli" / "plugins_none.json"
TEXTS = yaml.safe_load((FIXTURES / "change" / "texts.yaml").read_text(encoding="utf-8"))
DRY = "dry run T-008.1, 0 open questions, 0 dismissed by quote"
ORDERS_REL = "docs/prd/orders"

# testing.md, Subprocess environment and the change paragraph: the variables a run never inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
)
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test


class StepError(Exception):
    """A step could not be applied: the case's state was never built."""


class KnownFailure(Exception):
    """The known failure a case's `symptom:` describes was seen."""


@dataclass
class Result:
    exit: int
    out: bytes
    err: bytes

    @property
    def stdout(self) -> str:
        return self.out.decode("utf-8")

    @property
    def stderr(self) -> str:
        return self.err.decode("utf-8")

    @property
    def lines(self) -> list[str]:
        return self.stdout.splitlines()

    @property
    def err_lines(self) -> list[str]:
        return self.stderr.splitlines()

    def __str__(self) -> str:
        return f"exit {self.exit}\nstdout: {self.stdout!r}\nstderr: {self.stderr!r}"


def subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    return env


_NAME = re.compile(r"\bCHANGE\b|\bBLOCK\b|\bHOOKS\b|\bDRY\b|<tmp>|texts\.(\w+)")


def _value(match: re.Match, tmp: Path) -> str:
    word = match.group(0)
    if word in SCRIPTS:
        return str(SCRIPTS[word])
    if word == "DRY":
        return DRY
    if word == "<tmp>":
        return str(tmp)
    return TEXTS[match.group(1)]


def substitute(text: str, tmp: Path, quote: bool) -> str:
    """Replace CHANGE, BLOCK, HOOKS, DRY, <tmp> and texts.<key>, each value one word (shlex.quote) when `quote`."""
    return _NAME.sub(lambda m: shlex.quote(_value(m, tmp)) if quote else _value(m, tmp), text)


class Case:
    """<tmp>, the scratch repository, and the runs and steps of one change case."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.orders = tmp / ORDERS_REL
        self.dates: set[str] = set()
        # The bytes a step committed, by path from <tmp> (GY, GZ): "byte-identical to the file GY committed".
        self.committed: dict[str, dict[str, bytes]] = {}
        self._note_date()

    def _note_date(self) -> None:
        self.dates.add(datetime.date.today().isoformat())

    def path(self, rel: str) -> Path:
        """A step's path: inside <tmp>/docs/prd/orders unless it starts with <tmp>."""
        if rel.startswith("<tmp>/"):
            return self.tmp / rel[len("<tmp>/"):]
        return self.orders / rel

    def _exec(self, words: list[str], cwd: Path | None) -> Result:
        if words and words[0] == "python":
            words = [sys.executable, *words[1:]]
        self._note_date()
        proc = subprocess.run(words, cwd=cwd or self.tmp, env=subprocess_env(), capture_output=True,
                              timeout=RUN_TIMEOUT)
        self._note_date()
        return Result(proc.returncode, proc.stdout, proc.stderr)

    def run(self, command: str, cwd: Path | None = None) -> Result:
        """A case's `command:` or a `runs:` entry: names replaced, split with shlex.split, run with no shell."""
        return self._exec(shlex.split(substitute(command, self.tmp, quote=True)), cwd)

    def argv(self, items: list[str], cwd: Path | None = None) -> Result:
        """An `argv:` list: each item with the names replaced and not split again."""
        return self._exec([substitute(item, self.tmp, quote=False) for item in items], cwd)

    def git(self, *args: str) -> Result:
        return self._exec(["git", *args], None)

    def steps(self, *steps) -> None:
        """A run's `setup_before`: each step in order, inside the test body."""
        for step in steps:
            try:
                step(self)
            except SetupError as exc:
                raise StepError(f"{label(step)}: {exc}") from exc

    def today(self, text: str) -> list[str]:
        """`text` with <today> as each date taken just before or just after a run of the case."""
        return [text.replace("<today>", day) for day in sorted(self.dates)]


# -- snapshots ("unchanged", "no file changes") --

def snapshot(root: Path, skip_git: bool = True) -> dict[str, bytes]:
    """Every file under `root`, by relative path, leaving out `root/.git/`."""
    files: dict[str, bytes] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        if skip_git and here == root and ".git" in dirnames:
            dirnames.remove(".git")
        for name in filenames:
            path = here / name
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def diff(before: dict[str, bytes], after: dict[str, bytes]) -> list[str]:
    return sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))


# -- assertion keys (testing.md, Harness, Assertions) --

def stdout_is(r: Result, text: str) -> None:
    assert r.out == text.encode("utf-8"), str(r)


def stderr_is(r: Result, text: str) -> None:
    assert r.err == text.encode("utf-8"), str(r)


def exit_is(r: Result, code: int) -> None:
    assert r.exit == code, str(r)


def stderr_first_line_starts(r: Result, text: str) -> None:
    assert r.err_lines and r.err_lines[0].startswith(text), str(r)


def stderr_single_line_starts(r: Result, text: str) -> None:
    assert len(r.err_lines) == 1 and r.err_lines[0].startswith(text), str(r)


def stdout_contains_line(r: Result, line: str) -> None:
    assert line in r.lines, f"no stdout line {line!r}\n{r}"


def stdout_contains(r: Result, texts) -> None:
    for text in [texts] if isinstance(texts, str) else texts:
        assert text in r.stdout, f"stdout lacks {text!r}\n{r}"


def stdout_not_contains(r: Result, texts) -> None:
    for text in [texts] if isinstance(texts, str) else texts:
        assert text not in r.stdout, f"stdout holds {text!r}\n{r}"


def in_relative_order(lines: list[str], wanted: list[str]) -> bool:
    """Each wanted line, whole, after the one before it, other lines allowed between."""
    at = 0
    for line in wanted:
        try:
            at = lines.index(line, at) + 1
        except ValueError:
            return False
    return True


def stdout_lines_in_this_relative_order(r: Result, wanted: list[str]) -> None:
    assert in_relative_order(r.lines, wanted), f"lines {wanted!r} not in this order\n{r}"


def one_json_line(r: Result) -> dict:
    """The whole stdout is one line ending in a newline, parsed as one JSON object."""
    assert r.stdout.endswith("\n") and len(r.lines) == 1, f"stdout is not one line\n{r}"
    doc = json.loads(r.stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object\n{r}"
    return doc


def stdout_json(r: Result, mapping: dict) -> None:
    assert one_json_line(r) == mapping, str(r)


# -- steps --

def label(step) -> str:
    return getattr(step, "label", getattr(step, "__name__", repr(step)))


def named(name: str):
    def wrap(fn):
        fn.label = name
        return fn
    return wrap


def _read(path: Path) -> list[str]:
    if not path.is_file():
        raise StepError(f"{path} does not exist")
    return path.read_bytes().decode("utf-8").split("\n")


def _write_lines(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _section(lines: list[str], heading: str, name: str) -> tuple[int, int]:
    """The 0-based line range under a `## ` heading, up to the next `## ` heading."""
    found = [i for i, line in enumerate(lines) if line == heading]
    if len(found) != 1:
        raise StepError(f"{name}: expected one line {heading!r}, found {len(found)}")
    start = found[0] + 1
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            return start, j
    return start, len(lines)


def line_becomes(rel: str, n: int, old: str, new: str, name: str | None = None):
    """Line `n` of `rel`, which must be `old`, becomes `new`."""
    step_name = name or f"{rel} line {n} becomes {new!r}"

    @named(step_name)
    def step(c: Case) -> None:
        path = c.path(rel)
        lines = _read(path)
        if len(lines) < n or lines[n - 1] != old:
            got = lines[n - 1] if len(lines) >= n else None
            raise StepError(f"{step_name}: line {n} of {rel} is {got!r}, not {old!r}")
        lines[n - 1] = new
        _write_lines(path, lines)
    return step


def text_in_line(rel: str, n: int, old: str, new: str, name: str | None = None):
    """In line `n` of `rel`, the text `old` (found once) becomes `new`."""
    step_name = name or f"{rel} line {n}: {old!r} becomes {new!r}"

    @named(step_name)
    def step(c: Case) -> None:
        path = c.path(rel)
        lines = _read(path)
        if len(lines) < n or lines[n - 1].count(old) != 1:
            got = lines[n - 1] if len(lines) >= n else None
            raise StepError(f"{step_name}: line {n} of {rel} ({got!r}) does not hold {old!r} once")
        lines[n - 1] = lines[n - 1].replace(old, new)
        _write_lines(path, lines)
    return step


def text_in_section(rel: str, heading: str, old: str, new: str, name: str):
    """Under `heading`, the one line holding `old` has it replaced by `new`."""
    @named(name)
    def step(c: Case) -> None:
        path = c.path(rel)
        lines = _read(path)
        start, end = _section(lines, heading, name)
        hits = [i for i in range(start, end) if old in lines[i]]
        if len(hits) != 1:
            raise StepError(f"{name}: {len(hits)} lines under {heading!r} hold {old!r}")
        lines[hits[0]] = lines[hits[0]].replace(old, new)
        _write_lines(path, lines)
    return step


def line_in_section(rel: str, heading: str, old: str, new: str, name: str):
    """Under `heading`, the one line that is `old` becomes `new`."""
    @named(name)
    def step(c: Case) -> None:
        path = c.path(rel)
        lines = _read(path)
        start, end = _section(lines, heading, name)
        hits = [i for i in range(start, end) if lines[i] == old]
        if len(hits) != 1:
            raise StepError(f"{name}: {len(hits)} lines under {heading!r} are {old!r}")
        lines[hits[0]] = new
        _write_lines(path, lines)
    return step


def text_in_yaml_entry(rel: str, key: str, old: str, new: str, name: str):
    """In the top-level entry `key:` of a YAML file, the one line holding `old` has it replaced by `new`."""
    @named(name)
    def step(c: Case) -> None:
        path = c.path(rel)
        lines = _read(path)
        if lines.count(f"{key}:") != 1:
            raise StepError(f"{name}: {rel} has no one line {key + ':'!r}")
        start = lines.index(f"{key}:") + 1
        end = next((j for j in range(start, len(lines)) if lines[j] and not lines[j][0].isspace()), len(lines))
        hits = [i for i in range(start, end) if old in lines[i]]
        if len(hits) != 1:
            raise StepError(f"{name}: {len(hits)} lines of {key} hold {old!r}")
        lines[hits[0]] = lines[hits[0]].replace(old, new)
        _write_lines(path, lines)
    return step


def insert_after(rel: str, n: int, new: str, expect: str | None = None, name: str | None = None):
    """Insert the line `new` after line `n` of `rel` (which must be `expect` when given)."""
    step_name = name or f"{rel}: insert after line {n} the line {new!r}"

    @named(step_name)
    def step(c: Case) -> None:
        path = c.path(rel)
        lines = _read(path)
        if len(lines) < n or (expect is not None and lines[n - 1] != expect):
            got = lines[n - 1] if len(lines) >= n else None
            raise StepError(f"{step_name}: line {n} of {rel} is {got!r}, not {expect!r}")
        lines.insert(n, new)
        _write_lines(path, lines)
    return step


def append(rel: str, *new: str, name: str | None = None):
    """Append each line to `rel`, each ending in a newline (a last line with no newline is ended first)."""
    step_name = name or f"append to {rel} the lines {list(new)!r}"

    @named(step_name)
    def step(c: Case) -> None:
        path = c.path(rel)
        if not path.is_file():
            raise StepError(f"{step_name}: {path} does not exist")
        text = path.read_bytes().decode("utf-8")
        if text and not text.endswith("\n"):
            text += "\n"
        path.write_bytes((text + "".join(line + "\n" for line in new)).encode("utf-8"))
    return step


def write(rel: str, *new: str, name: str | None = None):
    """Write `rel` with these lines, each ending in a newline, creating its folder."""
    step_name = name or f"write {rel} with the lines {list(new)!r}"

    @named(step_name)
    def step(c: Case) -> None:
        write_text(c.path(rel), "".join(line + "\n" for line in new))
    return step


def delete(rel: str, name: str | None = None):
    step_name = name or f"delete {rel}"

    @named(step_name)
    def step(c: Case) -> None:
        path = c.path(rel)
        if not path.is_file():
            raise StepError(f"{step_name}: {path} does not exist")
        path.unlink()
    return step


def command(text: str, name: str | None = None):
    """A step that runs a command (git or python) in <tmp>; it must exit 0."""
    step_name = name or f"run `{text}`"

    @named(step_name)
    def step(c: Case) -> None:
        r = c.run(text)
        if r.exit != 0:
            raise StepError(f"{step_name} exited {r.exit}: {r.stderr.strip()}")
    return step


def _git_settings(c: Case, hooks_off: bool) -> None:
    settings = [("user.name", "Sample"), ("user.email", "sample@example.com"), ("commit.gpgsign", "false")]
    if hooks_off:
        settings.append(("core.hooksPath", "/dev/null"))
    for key, value in settings:
        _git_ok(c, "G0", "config", key, value)
    _git_ok(c, "G0", "add", "-A")
    _git_ok(c, "G0", "commit", "-q", "-m", "base")


def _git_ok(c: Case, name: str, *args: str) -> None:
    r = c.git(*args)
    if r.exit != 0:
        raise StepError(f"{name}: git {' '.join(args)} exited {r.exit}: {r.stderr.strip()}")


# -- the header's steps (test-cases/change.yaml) --

@named("G0")
def G0(c: Case) -> None:
    N0(c.tmp)
    _git_settings(c, hooks_off=True)


@named("G0N")
def G0N(c: Case) -> None:
    N0(c.tmp)
    _git_settings(c, hooks_off=False)


@named("GC")
def GC(c: Case) -> None:
    _git_ok(c, "GC", "add", "-A")
    _git_ok(c, "GC", "commit", "-q", "-m", "edit")


GQ = line_becomes("prd.md", 4, "status: Approved", "status: In review", name="GQ")

_GA_FEATURES = append(
    "features/import.md", "", "### FR-008 Refuse an empty file", "Status: approved", "Acceptance (EARS):",
    "- AC-008.1 If the import file is empty, the importer shall exit 2.", "Errors: -",
    "Tests: T-008.1 [integration]  (test-cases/import.yaml)", name="GA (features/import.md)")
_GA_CASES = append(
    "test-cases/import.yaml", "",
    "T-008.1:",
    "  ac: AC-008.1",
    "  level: integration",
    "  target: code:importer.import_file",
    "  environment: local",
    "  identity: none",
    "  preconditions: []",
    '  input: {content: ""}',
    "  expect:",
    "    output: {exit: 2}",
    "    effects: []",
    "    errors: []",
    "    leaks: none",
    name="GA (test-cases/import.yaml)")


@named("GA")
def GA(c: Case) -> None:
    _GA_FEATURES(c)
    _GA_CASES(c)


@named("GR")
def GR(c: Case) -> None:
    r = c.run("python CHANGE record docs/prd/orders --base HEAD --bump minor --change 'Refuse an empty file'")
    if r.exit != 0:
        raise StepError(f"GR: record exited {r.exit}: {r.stderr.strip()}")


@named("GV")
def GV(c: Case) -> None:
    r = c.run("python CHANGE digest docs/prd/orders")
    if r.exit != 0 or len(r.lines) != 1:
        raise StepError(f"GV: digest did not print one line\n{r}")
    write_text(c.path(".prd-review.json"), '{"digest": "%s", "ready": true, "blockers": []}\n' % r.lines[0])


GS = line_becomes("features/import.md", 11, "Status: built", "Status: verified", name="GS")
GW = text_in_line("features/import.md", 6, "has no header line, the importer", "has no header line the importer",
                  name="GW")
GX = text_in_line("features/import.md", 6, "exit 2 with", "exit 3 with", name="GX")
UNDO_GX = text_in_line("features/import.md", 6, "exit 3 with", "exit 2 with", name="undo GX")
GD = line_becomes("features/reports.md", 18, "Status: live (since 1.0.0)", "Status: removed", name="GD")
GG = text_in_section("prd.md", "## 3. Glossary", "stored once per order key", "stored once for each order key",
                     name="GG")
_GI_SOURCE = insert_after("features/import.md", 4, "Source: src/importer.py:10 @abc1234", name="GI")


@named("GI")
def GI(c: Case) -> None:
    _GI_SOURCE(c)
    GQ(c)


GE = write("errors.md", "# Error ledger", "", "### E-001 The importer accepts an empty file",
           "Detected: 2026-11-20, a user report", "Classification: code bug", "Touches: FR-001",
           "Diagnosis: the header check skips an empty file", "Resolution: open", "Recurrence of: -", name="GE")
GT = append(
    "test-cases/import.yaml", "",
    "T-001.2:",
    "  ac: AC-001.1",
    "  level: integration",
    "  target: code:importer.import_file",
    "  environment: local",
    "  identity: none",
    "  preconditions: []",
    '  input: {content: ""}',
    "  expect:",
    "    output: {exit: 2}",
    "    effects: []",
    "    errors: [IMPORT_NO_HEADER]",
    "    leaks: none",
    name="GT")
GK = line_becomes("contracts/errors.yaml", 5, "  message: The import file has no header line.",
                  "  message: The import file has no header line (FR-001).", name="GK")
UNDO_GK = line_becomes("contracts/errors.yaml", 5, "  message: The import file has no header line (FR-001).",
                       "  message: The import file has no header line.", name="undo GK")
GL = append("prd.md", "| 1.1.0 | 2026-11-12 | a removal; no dry run (removal only) | FR-012, T-001.4, UJ-03 |",
            name="GL")
GM = insert_after("features/import.md", 6,
                  "- AC-001.2 (removed in 1.1.0) If the file is empty, the importer shall exit 2.", name="GM")
GP = insert_after("prd.md", 13, "- Pack: service 0.9.0 (prd-toolkit)", expect="- Language: Python 3.12", name="GP")

_G09_VERSION = line_becomes("prd.md", 3, "version: 1.0.0", "version: 0.9.0", name="G09 (version)")


@named("G09")
def G09(c: Case) -> None:
    _G09_VERSION(c)
    path = c.path("prd.md")
    lines = _read(path)
    start, end = _section(lines, "## 14. Changelog", "G09")
    rows = [i for i in range(start, end) if lines[i].startswith("| 1.0.0 |")]
    if len(rows) != 1:
        raise StepError(f"G09: §14 holds {len(rows)} rows whose first cell is 1.0.0")
    lines[rows[0]] = "| 0.9.0 |" + lines[rows[0]][len("| 1.0.0 |"):]
    _write_lines(path, lines)
    GC(c)


@named("GH")
def GH(c: Case) -> None:
    write_text(c.path("<tmp>/CLAUDE.md"), "# Notes\n")
    GC(c)


@named("GN")
def GN(c: Case) -> None:
    path = c.path("prd.md")
    lines = _read(path)
    start, end = _section(lines, "## 14. Changelog", "GN")
    table = [i for i in range(start, end) if lines[i].startswith("|")]
    if len(table) != 3:
        raise StepError(f"GN: §14 holds {len(table)} table lines, not 3")
    for i in reversed(table):
        del lines[i]
    _write_lines(path, lines)


GITHUB_CI = ".github/workflows/prd-toolkit.yml"  # a path from <tmp>, as the change cases name it


def _keep_committed(c: Case, name: str, rel: str) -> None:
    """Record the bytes of `rel` (a path from <tmp>) at HEAD, the commit step `name` just made."""
    r = c.git("show", f"HEAD:{rel}")
    if r.exit != 0:
        raise StepError(f"{name}: git show HEAD:{rel} exited {r.exit}: {r.stderr.strip()}")
    c.committed.setdefault(name, {})[rel] = r.out


@named("GY")
def GY(c: Case) -> None:
    r = c.run("python HOOKS ci --github docs/prd/orders")
    if r.exit != 0:
        raise StepError(f"GY: ci --github exited {r.exit}: {r.stderr.strip()}")
    GC(c)
    _keep_committed(c, "GY", GITHUB_CI)


_GZ_APPEND = append(f"<tmp>/{GITHUB_CI}", "# old", name="GZ")


@named("GZ")
def GZ(c: Case) -> None:
    _GZ_APPEND(c)
    GC(c)
    _keep_committed(c, "GZ", GITHUB_CI)


@named("R")
def R(c: Case) -> None:
    for step in (G0, GQ, GA, GR, GV):
        step(c)


@named("N0X")
def N0X_here(c: Case) -> None:
    N0X(c.tmp)


# -- the `case` fixture --

@pytest.fixture
def case(request, tmp_path, monkeypatch) -> Case:
    """<tmp> with the change environment set in the test's own process, then the case's `setup:` steps in order."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("PRD_PLUGINS_FILE", str(PLUGINS_NONE))
    c = Case(tmp_path)
    for step in getattr(request, "param", ()):
        step(c)  # a failure here ends the test as an error, not a failure
    return c


def given(*steps):
    """Mark a test with its case's `setup:` list; the `case` fixture runs the steps."""
    return pytest.mark.parametrize("case", [steps], indirect=True,
                                   ids=["+".join(label(s).split(" ")[0] for s in steps)])
