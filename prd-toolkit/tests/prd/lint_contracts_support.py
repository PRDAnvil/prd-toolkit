"""Shared helpers of the lint-contracts characterization tests (testing.md, Layout).

Everything here follows docs/prd/prd-toolkit/testing.md (Harness) and the header of
docs/prd/prd-toolkit/test-cases/lint-contracts.yaml, which extends the conventions of
test-cases/lint-registries.yaml. Nothing is imported from another area's support file.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

import yaml

# tests/prd/<this file> -> prd-toolkit/tests/prd -> the repository root
REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
LINT_SCRIPT = REPO / "prd-toolkit" / "scripts" / "prd_lint.py"
PRD_REL = "docs/prd/orders"

# Subprocess environment (testing.md, Harness) minus the variables the lint-registries
# header and the lint-contracts header take out as well.
_REMOVED = (
    "PYTHONIOENCODING",
    "PYTHONPATH",
    "PYTHONHOME",
    "PRD_LINT_CI",
    "PRD_HELP_FILE",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
    "PRD_VALIDATOR_TIMEOUT",
)


class KnownFailure(Exception):
    """Raised by a known-failing test when it sees exactly the case's symptom."""


class StepError(Exception):
    """A setup step did not find the file or the line it names: the state was never built."""


class Orders:
    """The orders PRD folder <P> = <tmp>/docs/prd/orders after step S0, with the setup edits.

    "line N of F" in a step is line N of F as S0 wrote it, before any other step of the case,
    so each file's lines carry the number S0 gave them (None for a line a step added).
    """

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.root = tmp / "docs" / "prd" / "orders"
        self._files: dict[str, list[tuple[int | None, str]]] = {}

    # -- state --------------------------------------------------------------
    def _lines(self, rel: str) -> list[tuple[int | None, str]]:
        if rel not in self._files:
            path = self.root / rel
            if not path.is_file():
                raise StepError(f"no file {rel}")
            text = path.read_bytes().decode("utf-8")
            self._files[rel] = [(i + 1, line) for i, line in enumerate(text.splitlines())]
        return self._files[rel]

    def _flush(self, rel: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "".join(line + "\n" for _, line in self._files[rel])
        path.write_bytes(text.encode("utf-8"))

    def _pos(self, rel: str, n: int) -> int:
        for i, (orig, _) in enumerate(self._lines(rel)):
            if orig == n:
                return i
        raise StepError(f"no line {n} in {rel}")

    # -- steps --------------------------------------------------------------
    def replace(self, rel: str, n: int, text: str) -> None:
        lines = self._lines(rel)
        i = self._pos(rel, n)
        lines[i] = (n, text)
        self._flush(rel)

    def delete(self, rel: str, n: int) -> None:
        lines = self._lines(rel)
        del lines[self._pos(rel, n)]
        self._flush(rel)

    def insert_after(self, rel: str, n: int, text: str) -> None:
        lines = self._lines(rel)
        lines.insert(self._pos(rel, n) + 1, (None, text))
        self._flush(rel)

    def append(self, rel: str, text: str) -> None:
        self._lines(rel).append((None, text))
        self._flush(rel)

    def write(self, rel: str, *lines: str) -> None:
        self._files[rel] = [(None, line) for line in lines]
        self._flush(rel)

    def delete_file(self, rel: str) -> None:
        """"delete the file F": a missing F is a StepError."""
        path = self.root / rel
        if not path.is_file():
            raise StepError(f"no file {rel}")
        path.unlink()
        self._files.pop(rel, None)

    def make_executable(self, rel: str) -> None:
        """"make F executable": add the execute permission for F's owner (chmod u+x)."""
        path = self.root / rel
        if not path.is_file():
            raise StepError(f"no file {rel}")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)


def S0(tmp: Path, monkeypatch) -> Orders:
    """Step S0: write fixture lint-cli/orders to <P> and set PRD_PLUGINS_FILE."""
    data = yaml.safe_load((FIXTURES / "lint-cli" / "orders.yaml").read_text(encoding="utf-8"))
    root = tmp / "docs" / "prd" / "orders"
    for key, text in data.items():
        path = root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    monkeypatch.setenv(
        "PRD_PLUGINS_FILE", str((FIXTURES / "lint-cli" / "plugins_superpowers.json").resolve())
    )
    return Orders(tmp)


def lint_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in _REMOVED:
        env.pop(name, None)
    return env


def run_lint(tmp: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """LINT: python <repo>/prd-toolkit/scripts/prd_lint.py docs/prd/orders, cwd <tmp>.

    `env` is a run's own env ({env: ..., command: LINT}), added for that run only.
    stdout and stderr are captured as bytes (testing.md, Assertions) and decoded as strict UTF-8 with no
    newline translation, so every \\r stays and output that is not UTF-8 raises, never passes.
    """
    r = run_lint_bytes(tmp, env)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout.decode("utf-8"), r.stderr.decode("utf-8"))


def run_lint_bytes(tmp: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """LINT as run_lint runs it, with stdout and stderr captured as bytes, never in text mode
    (testing.md, Assertions). A test decodes stdout as UTF-8 for its line assertions and
    compares stderr with the expected text encoded as UTF-8.
    """
    run_env = lint_env()
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(LINT_SCRIPT), PRD_REL],
        cwd=tmp,
        env=run_env,
        capture_output=True,
    )


# -- assertions (testing.md, Assertions) ------------------------------------
def _as_list(value) -> list[str]:
    return [value] if isinstance(value, str) else list(value)


def assert_contains_line(out: str, line: str) -> None:
    assert line in out.splitlines(), f"no line {line!r} in:\n{out}"


def assert_contains(out: str, value) -> None:
    for s in _as_list(value):
        assert s in out, f"{s!r} not in:\n{out}"


def assert_not_contains(out: str, value) -> None:
    for s in _as_list(value):
        assert s not in out, f"{s!r} found in:\n{out}"


def assert_lines_in_relative_order(out: str, expected: list[str]) -> None:
    lines = out.splitlines()
    at = 0
    for want in expected:
        try:
            at = lines.index(want, at) + 1
        except ValueError:
            raise AssertionError(f"line {want!r} not found in order in:\n{out}") from None


def assert_exact_lines(out: str, expected: list[str]) -> None:
    assert out.splitlines() == expected, f"stdout lines differ:\n{out}"
