"""Shared helpers of the lint-registries characterization tests (testing.md, Layout).

Everything here follows testing.md (Harness, Fixtures) and the conventions at the head of
docs/prd/prd-toolkit/test-cases/lint-registries.yaml. Nothing is imported from another area's
support file.

A test lists its setup steps with the ``steps(...)`` decorator; the ``case`` fixture applies them
while pytest sets the test up, so a step that does not find its file or line, a step command that
exits other than 0, or a note's precondition that does not hold ends the test as an error, not a
failure.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_FIXTURE = FIXTURES / "lint-cli" / "orders.yaml"
PLUGINS_SUPERPOWERS = FIXTURES / "lint-cli" / "plugins_superpowers.json"
TEXTS_FIXTURE = FIXTURES / "lint-registries" / "texts.yaml"
PRD_LINT = REPO / "prd-toolkit" / "scripts" / "prd_lint.py"
PRD_HELP = REPO / "prd-toolkit" / "scripts" / "prd_help.py"

# Harness, Subprocess environment, and the case file's header (git variables).
_REMOVED = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
)


class StepError(Exception):
    """A setup step could not build the state its case needs."""


def text(key: str):
    """texts.<key> of fixture lint-registries/texts, read with yaml.safe_load."""
    data = yaml.safe_load(TEXTS_FIXTURE.read_text(encoding="utf-8"))
    if key not in data:
        raise StepError(f"fixture lint-registries/texts has no key {key!r}")
    return data[key]


def subprocess_env(extra: dict | None = None) -> dict:
    env = dict(os.environ)
    for name in _REMOVED:
        env.pop(name, None)
    if extra:
        env.update(extra)
    return env


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

    @property
    def lines(self) -> list[str]:
        return self.stdout.splitlines()

    def describe(self) -> str:
        return f"exit {self.exit}\n--- stdout ---\n{self.stdout}--- stderr ---\n{self.stderr}"


class Case:
    """The state of one test: its tmp_path, the PRD folder <P> and the edits made so far."""

    def __init__(self, tmp: Path, monkeypatch: pytest.MonkeyPatch):
        self.tmp = tmp
        self.P = tmp / "docs" / "prd" / "orders"
        self.monkeypatch = monkeypatch
        # file -> list of [original line number or None, text without its newline]
        self._lines: dict[str, list[list]] = {}

    def sub(self, value: str) -> str:
        return value.replace("<tmp>", str(self.tmp))

    # "line N of F" is line N of F as S0 wrote it, before any other step of the case.
    def _entries(self, rel: str) -> list[list]:
        if rel not in self._lines:
            path = self.P / rel
            if not path.is_file():
                raise StepError(f"step: no file {rel} in the PRD folder")
            text_ = path.read_bytes().decode("utf-8")
            self._lines[rel] = [[i + 1, line] for i, line in enumerate(text_.splitlines())]
        return self._lines[rel]

    def _index(self, rel: str, n: int) -> int:
        for i, (orig, _) in enumerate(self._entries(rel)):
            if orig == n:
                return i
        raise StepError(f"step: line {n} of {rel} not found")

    def _flush(self, rel: str) -> None:
        body = "".join(line + "\n" for _, line in self._lines[rel])
        (self.P / rel).write_bytes(body.encode("utf-8"))

    def replace(self, rel: str, n: int, line: str) -> None:
        i = self._index(rel, n)
        self._lines[rel][i][1] = line
        self._flush(rel)

    def insert_after(self, rel: str, n: int, lines: list[str]) -> None:
        i = self._index(rel, n)
        self._lines[rel][i + 1:i + 1] = [[None, line] for line in lines]
        self._flush(rel)

    def delete_line(self, rel: str, n: int) -> None:
        i = self._index(rel, n)
        del self._lines[rel][i]
        self._flush(rel)

    def append(self, rel: str, lines: list[str]) -> None:
        """"append X to F": each line of X, each with a newline, after F's final newline."""
        path = self.P / rel
        if not path.is_file():
            raise StepError(f"step: no file {rel} to append to")
        if not path.read_bytes().endswith(b"\n"):
            raise StepError(f"step: {rel} has no final newline to append after")
        self._entries(rel).extend([None, line] for line in lines)
        self._flush(rel)

    # A run's before: step: "line N of F" is line N of F as it stands at that moment.
    def _index_now(self, rel: str, n: int, was: str | None) -> int:
        entries = self._entries(rel)
        if not 1 <= n <= len(entries):
            raise StepError(f"step: {rel} has no line {n} now")
        if was is not None and entries[n - 1][1] != was:
            raise StepError(f"step: line {n} of {rel} is {entries[n - 1][1]!r}, not {was!r}")
        return n - 1

    def replace_now(self, rel: str, n: int, line: str, was: str | None = None) -> None:
        self._lines[rel][self._index_now(rel, n, was)][1] = line
        self._flush(rel)

    def delete_now(self, rel: str, n: int, was: str | None = None) -> None:
        del self._lines[rel][self._index_now(rel, n, was)]
        self._flush(rel)

    def delete_file(self, rel: str) -> None:
        path = self.P / rel
        if not path.is_file():
            raise StepError(f"step: no file {rel} to delete")
        path.unlink()
        self._lines.pop(rel, None)

    def write_lines(self, path: str, lines: list[str]) -> None:
        target = Path(self.sub(path))
        if not target.is_absolute():
            target = self.P / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes("".join(self.sub(line) + "\n" for line in lines).encode("utf-8"))

    def git(self, *args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
        r = subprocess.run(["git", *args], cwd=cwd or self.tmp, env=subprocess_env(),
                           capture_output=True)
        if check and r.returncode != 0:
            raise StepError(f"step: git {' '.join(args)} exited {r.returncode}: {r.stderr!r}")
        return r

    def _run(self, script: Path, args: list[str], env: dict | None) -> Result:
        extra = {k: self.sub(v) for k, v in (env or {}).items()}
        r = subprocess.run([sys.executable, str(script), *args], cwd=self.tmp,
                           env=subprocess_env(extra), capture_output=True)
        return Result(r.returncode, r.stdout, r.stderr)

    def lint(self, *args: str, env: dict | None = None) -> Result:
        """LINT = python <repo>/prd-toolkit/scripts/prd_lint.py docs/prd/orders, cwd <tmp>."""
        return self._run(PRD_LINT, ["docs/prd/orders", *args], env)

    def help(self, *args: str, env: dict | None = None) -> Result:
        """HELP = python <repo>/prd-toolkit/scripts/prd_help.py, cwd <tmp>."""
        return self._run(PRD_HELP, list(args), env)


# ---- steps: each returns a callable applied to the Case during setup ----

def S0(c: Case) -> None:
    """Write fixture lint-cli/orders to <P> and set PRD_PLUGINS_FILE to lint-cli/plugins_superpowers."""
    data = yaml.safe_load(ORDERS_FIXTURE.read_text(encoding="utf-8"))
    for key, body in data.items():
        path = c.P / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body.encode("utf-8"))
    c.monkeypatch.setenv("PRD_PLUGINS_FILE", str(PLUGINS_SUPERPOWERS.resolve()))


def replace(rel: str, n: int, line: str):
    return lambda c: c.replace(rel, n, line)


def insert_after(rel: str, n: int, *lines: str):
    return lambda c: c.insert_after(rel, n, list(lines))


def delete_line(rel: str, n: int):
    return lambda c: c.delete_line(rel, n)


def delete_file(rel: str):
    return lambda c: c.delete_file(rel)


def append(rel: str, *lines: str):
    return lambda c: c.append(rel, list(lines))


def write_lines(path: str, *lines: str):
    return lambda c: c.write_lines(path, list(lines))


def git_init(c: Case) -> None:
    c.git("init", "-q")


# ---- preconditions a case's note states, checked before the run ----

def require_not_on_path(word: str):
    def check(c: Case) -> None:
        if shutil.which(word, path=subprocess_env().get("PATH")) is not None:
            raise StepError(f"precondition: {word} is on PATH")
    return check


def require_on_path(word: str):
    def check(c: Case) -> None:
        if shutil.which(word, path=subprocess_env().get("PATH")) is None:
            raise StepError(f"precondition: {word} is not on PATH")
    return check


def require_outside_git(c: Case) -> None:
    r = c.git("rev-parse", "--show-toplevel", check=False)
    if r.returncode == 0:
        raise StepError(f"precondition: {c.tmp} is inside a git checkout")


def require_absent(path: str):
    def check(c: Case) -> None:
        if Path(c.sub(path)).exists():
            raise StepError(f"precondition: {c.sub(path)} exists")
    return check


def require_toplevel_is_tmp(c: Case) -> None:
    r = c.git("rev-parse", "--show-toplevel", cwd=c.P)
    top = Path(r.stdout.decode("utf-8").strip()).resolve()
    if top != c.tmp.resolve():
        raise StepError(f"precondition: git toplevel of the PRD folder is {top}, not {c.tmp}")


def require_no_skill_under(path: str):
    def check(c: Case) -> None:
        root = Path(c.sub(path))
        if root.exists() and any(root.rglob("SKILL.md")):
            raise StepError(f"precondition: {root} holds a skill")
    return check


# ---- wiring ----

def steps(*fns):
    """Record a test's setup steps; the ``case`` fixture applies them in order."""
    def deco(func):
        func._lint_registries_steps = fns
        return func
    return deco


@pytest.fixture
def case(request, tmp_path, monkeypatch) -> Case:
    c = Case(tmp_path, monkeypatch)
    for fn in getattr(request.function, "_lint_registries_steps", ()):
        fn(c)
    return c


# ---- assertions (testing.md, Assertions) ----

def assert_exit(r: Result, code: int) -> None:
    assert r.exit == code, r.describe()


def assert_stdout_exact_lines(r: Result, lines: list[str]) -> None:
    assert r.lines == lines, r.describe()


def assert_stdout(r: Result, expected: str) -> None:
    assert r.stdout_bytes == expected.encode("utf-8"), r.describe()


def assert_stderr(r: Result, expected: str) -> None:
    assert r.stderr_bytes == expected.encode("utf-8"), r.describe()


def assert_stdout_contains_line(r: Result, line: str) -> None:
    assert line in r.lines, r.describe()


def assert_stdout_not_contains(r: Result, texts) -> None:
    for t in ([texts] if isinstance(texts, str) else texts):
        assert t not in r.stdout, f"stdout holds {t!r}\n{r.describe()}"
