"""Shared helper for the lint-ids black-box tests (testing.md, Harness: Layout).

Everything here follows docs/prd/prd-toolkit/testing.md (Harness, Fixtures) and the conventions at the
head of docs/prd/prd-toolkit/test-cases/lint-ids.yaml: step S0, the line edits, texts.<key>, and the
subprocess run of prd_lint.py with the test's own interpreter.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]  # prd-toolkit/tests/prd/<file> -> the repository root
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_FIXTURE = FIXTURES / "lint-cli" / "orders.yaml"
PLUGINS_SUPERPOWERS = FIXTURES / "lint-cli" / "plugins_superpowers.json"
TEXTS_FIXTURE = FIXTURES / "lint-ids" / "texts.yaml"
LINT = REPO / "prd-toolkit" / "scripts" / "prd_lint.py"
PRD_REL = "docs/prd/orders"

# Harness, Subprocess environment: the runner's environment minus these.
DROPPED_ENV = ("PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE")


class SetupStepError(Exception):
    """A setup step did not find the file or the line it names: the case's state was never built."""


class KnownFailure(Exception):
    """The expected-failure exception: raised only when a known-failing case's `symptom:` is seen."""


def load_texts() -> dict:
    """Fixture lint-ids/texts, read with yaml.safe_load (Fixtures table)."""
    return yaml.safe_load(TEXTS_FIXTURE.read_text(encoding="utf-8"))


def S0(tmp: Path, monkeypatch) -> "Folder":
    """Step S0: write fixture lint-cli/orders under <tmp>/docs/prd/orders and set PRD_PLUGINS_FILE."""
    data = yaml.safe_load(ORDERS_FIXTURE.read_text(encoding="utf-8"))
    prd = tmp / PRD_REL
    for key, text in data.items():
        path = prd / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    monkeypatch.setenv("PRD_PLUGINS_FILE", str(PLUGINS_SUPERPOWERS.resolve()))
    return Folder(prd)


class Folder:
    """The PRD folder <P>; each method is one of the case file's setup-step forms, applied in order."""

    def __init__(self, root: Path):
        self.root = root

    def _read(self, rel: str) -> list[str]:
        path = self.root / rel
        if not path.is_file():
            raise SetupStepError(f"{rel} does not exist")
        return path.read_text(encoding="utf-8").splitlines(keepends=True)

    def _write(self, rel: str, lines: list[str]) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("".join(lines))

    def _check(self, rel: str, lines: list[str], n: int) -> None:
        if not 1 <= n <= len(lines):
            raise SetupStepError(f"{rel} has no line {n} ({len(lines)} lines)")

    def replace(self, rel: str, n: int, text: str) -> None:
        """replace line N of F with X"""
        lines = self._read(rel)
        self._check(rel, lines, n)
        lines[n - 1] = text + "\n"
        self._write(rel, lines)

    def insert_before(self, rel: str, n: int, text: str) -> None:
        """insert X before line N of F: X becomes line N"""
        lines = self._read(rel)
        self._check(rel, lines, n)
        lines.insert(n - 1, text + "\n")
        self._write(rel, lines)

    def insert_after(self, rel: str, n: int, text: str) -> None:
        """insert X after line N of F: X becomes line N+1"""
        lines = self._read(rel)
        self._check(rel, lines, n)
        if not lines[n - 1].endswith("\n"):
            lines[n - 1] += "\n"
        lines.insert(n, text + "\n")
        self._write(rel, lines)

    def delete(self, rel: str, n: int) -> None:
        """delete line N of F: the lines after it move up"""
        lines = self._read(rel)
        self._check(rel, lines, n)
        del lines[n - 1]
        self._write(rel, lines)

    def append(self, rel: str, new_lines: list[str]) -> None:
        """append X to F: each line, with a newline, after F's final newline"""
        lines = self._read(rel)
        if lines and not lines[-1].endswith("\n"):
            raise SetupStepError(f"{rel} has no final newline")
        lines.extend(line + "\n" for line in new_lines)
        self._write(rel, lines)

    def write(self, rel: str, line: str) -> None:
        """write F with the one line X: F holds X and a newline"""
        self._write(rel, [line + "\n"])


def run_lint(tmp: Path) -> subprocess.CompletedProcess:
    """`python <repo>/prd-toolkit/scripts/prd_lint.py docs/prd/orders` with <tmp> as the working directory.

    stdout and stderr are captured as bytes (testing.md, Assertions) and decoded as strict UTF-8 with no
    newline translation, so every \\r stays and output that is not UTF-8 raises, never passes.
    """
    env = {k: v for k, v in os.environ.items() if k not in DROPPED_ENV}
    r = subprocess.run([sys.executable, str(LINT), PRD_REL], cwd=tmp, env=env, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout.decode("utf-8"), r.stderr.decode("utf-8"))


def _show(r: subprocess.CompletedProcess) -> str:
    return f"exit {r.returncode}\n--- stdout ---\n{r.stdout}--- stderr ---\n{r.stderr}"


def assert_exit(r, code: int) -> None:
    assert r.returncode == code, f"expected exit {code}\n{_show(r)}"


def assert_stderr_empty(r) -> None:
    assert r.stderr == "", f"expected empty stderr\n{_show(r)}"


def assert_contains_line(r, line: str) -> None:
    """stdout_contains_line: one whole line of str.splitlines()."""
    assert line in r.stdout.splitlines(), f"missing stdout line {line!r}\n{_show(r)}"


def assert_contains(r, texts) -> None:
    """stdout_contains: a substring, or each string of a list."""
    for text in [texts] if isinstance(texts, str) else texts:
        assert text in r.stdout, f"stdout does not hold {text!r}\n{_show(r)}"


def assert_not_contains(r, texts) -> None:
    """stdout_not_contains: a substring, or each string of a list, that stdout must not hold anywhere."""
    for text in [texts] if isinstance(texts, str) else texts:
        assert text not in r.stdout, f"stdout holds {text!r}\n{_show(r)}"


def assert_count_of_line(r, line: str, count: int) -> None:
    """stdout_count_of_line: the number of stdout lines equal to `line`."""
    got = r.stdout.splitlines().count(line)
    assert got == count, f"line {line!r} appears {got} times, expected {count}\n{_show(r)}"


def known_failure_if(seen: bool, entry: str, symptom: str, r) -> None:
    """Raise KnownFailure only when the case's symptom is seen."""
    if seen:
        raise KnownFailure(f"{entry}: {symptom}\n{_show(r)}")
