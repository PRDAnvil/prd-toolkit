"""Shared helpers of the lint-testcases characterization tests.

Written from docs/prd/prd-toolkit/testing.md (Harness, Layout, Fixtures) and the conventions at the head of
test-cases/lint-testcases.yaml (which extend those of lint-registries.yaml, lint-ids.yaml, lint-structure.yaml
and lint-cli.yaml). Nothing here is imported from another area's support file.

A case is a dict:
    {"setup": [step, ...], "runs": [{"before": step or None}, ...]}
A step is a tuple:
    ("replace", F, N, X)        replace line N of F with X (a string or a list of lines)
    ("insert_after", F, N, X)   insert X after line N of F
    ("delete", F, N)            delete line N of F
    ("delete_range", F, N, M)   delete lines N to M of F
    ("append", F, X)            append X to F
    ("write", F, X)             write F with the lines X: create F and its folders, each line of X and a newline
F is relative to <P> = <tmp>/docs/prd/orders, unless it starts with "<tmp>/", when it is relative to <tmp>. In setup,
"line N" is line N as S0 wrote it; in a before: step it is line N of F as the file stands at that moment.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
LINT_SCRIPT = REPO / "prd-toolkit" / "scripts" / "prd_lint.py"

# Harness, Subprocess environment; the case file's conventions add the git variables.
_REMOVED_ENV = (
    "PYTHONIOENCODING",
    "PYTHONPATH",
    "PYTHONHOME",
    "PRD_LINT_CI",
    "PRD_HELP_FILE",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
)


class SetupError(Exception):
    """A step did not find its file or its line: the state the case needs was never built."""


class KnownFailure(Exception):
    """The symptom a known-failing case names was seen."""


@dataclass
class Run:
    exit: int
    stdout: str
    stderr: str


def texts() -> dict:
    """Fixture lint-testcases/texts, read with yaml.safe_load."""
    return yaml.safe_load((FIXTURES / "lint-testcases" / "texts.yaml").read_text(encoding="utf-8"))


def prd_dir(tmp: Path) -> Path:
    return tmp / "docs" / "prd" / "orders"


def S0(tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Write each entry of fixture lint-cli/orders to <P>/<key>; set PRD_PLUGINS_FILE to plugins_superpowers."""
    orders = yaml.safe_load((FIXTURES / "lint-cli" / "orders.yaml").read_text(encoding="utf-8"))
    p = prd_dir(tmp)
    for key, text in orders.items():
        target = p / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    monkeypatch.setenv("PRD_PLUGINS_FILE", str((FIXTURES / "lint-cli" / "plugins_superpowers.json").resolve()))


def _as_lines(x) -> list[str]:
    return [x] if isinstance(x, str) else list(x)


def _read(path: Path) -> tuple[list[str], bool]:
    if not path.is_file():
        raise SetupError(f"no file {path}")
    text = path.read_text(encoding="utf-8")
    return text.splitlines(), text.endswith("\n")


def _write(path: Path, lines: list[str], ends_nl: bool) -> None:
    text = "\n".join(lines)
    if lines and ends_nl:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def _check_line(lines: list, n: int, f: str) -> None:
    if not 1 <= n <= len(lines):
        raise SetupError(f"{f} has no line {n}")


class _Slot:
    def __init__(self, line: str):
        self.own: list[str] = [line]
        self.after: list[str] = []


_TMP_PREFIX = "<tmp>/"


def _path(tmp: Path, f: str) -> Path:
    """F relative to <P>, or to <tmp> when it starts with "<tmp>/"."""
    if f.startswith(_TMP_PREFIX):
        return tmp / f[len(_TMP_PREFIX) :]
    return prd_dir(tmp) / f


def write_lines(tmp: Path, f: str, x) -> None:
    """Write F with the lines X: create F and its folders, holding each line of X and a newline."""
    target = _path(tmp, f)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(line + "\n" for line in _as_lines(x)), encoding="utf-8")


def delete_file(tmp: Path, f: str) -> None:
    """Delete the file F; a file that is not there ends the test as an error."""
    target = _path(tmp, f)
    if not target.is_file():
        raise SetupError(f"no file {target}")
    target.unlink()


def apply_setup(tmp: Path, steps: list) -> None:
    """Apply setup steps, each "line N" counted as S0 wrote the file."""
    p = prd_dir(tmp)
    state: dict[str, tuple[list[_Slot], list[str], bool]] = {}

    def get(f: str):
        if f not in state:
            lines, ends_nl = _read(p / f)
            state[f] = ([_Slot(line) for line in lines], [], ends_nl)
        return state[f]

    for step in steps:
        kind, f = step[0], step[1]
        if kind == "delete_file":
            if f in state:
                raise SetupError(f"delete of {f} after an edit of it in the same setup")
            delete_file(tmp, f)
            continue
        if kind == "write":
            if f in state:
                raise SetupError(f"write of {f} after an edit of it in the same setup")
            write_lines(tmp, f, step[2])
            continue
        slots, tail, _ = get(f)
        if kind == "replace":
            _check_line(slots, step[2], f)
            slots[step[2] - 1].own = _as_lines(step[3])
        elif kind == "insert_after":
            _check_line(slots, step[2], f)
            slots[step[2] - 1].after.extend(_as_lines(step[3]))
        elif kind == "delete":
            _check_line(slots, step[2], f)
            slots[step[2] - 1].own = []
        elif kind == "delete_range":
            _check_line(slots, step[2], f)
            _check_line(slots, step[3], f)
            for i in range(step[2], step[3] + 1):
                slots[i - 1].own = []
        elif kind == "append":
            tail.extend(_as_lines(step[2]))
        else:
            raise SetupError(f"unknown step {kind}")

    for f, (slots, tail, ends_nl) in state.items():
        lines: list[str] = []
        for s in slots:
            lines.extend(s.own)
            lines.extend(s.after)
        lines.extend(tail)
        _write(p / f, lines, ends_nl or bool(tail))


def apply_before(tmp: Path, step) -> None:
    """Apply a before: step, each "line N" counted as the file stands now."""
    p = prd_dir(tmp)
    kind, f = step[0], step[1]
    if kind == "delete_file":
        delete_file(tmp, f)
        return
    if kind == "write":
        write_lines(tmp, f, step[2])
        return
    lines, ends_nl = _read(p / f)
    if kind == "replace":
        _check_line(lines, step[2], f)
        lines[step[2] - 1 : step[2]] = _as_lines(step[3])
    elif kind == "insert_after":
        _check_line(lines, step[2], f)
        lines[step[2] : step[2]] = _as_lines(step[3])
    elif kind == "delete":
        _check_line(lines, step[2], f)
        del lines[step[2] - 1]
    elif kind == "delete_range":
        _check_line(lines, step[2], f)
        _check_line(lines, step[3], f)
        del lines[step[2] - 1 : step[3]]
    elif kind == "append":
        lines.extend(_as_lines(step[2]))
        ends_nl = True
    else:
        raise SetupError(f"unknown step {kind}")
    _write(p / f, lines, ends_nl)


def subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in _REMOVED_ENV:
        env.pop(name, None)
    return env


def LINT(tmp: Path) -> Run:
    """python <repo>/prd-toolkit/scripts/prd_lint.py docs/prd/orders, with <tmp> as its working directory."""
    r = subprocess.run(
        [sys.executable, str(LINT_SCRIPT), "docs/prd/orders"],
        cwd=tmp,
        env=subprocess_env(),
        capture_output=True,
        text=True,
    )
    return Run(r.returncode, r.stdout, r.stderr)


HELP_SCRIPT = REPO / "prd-toolkit" / "scripts" / "prd_help.py"


def HELP(tmp: Path, *args: str) -> Run:
    """python <repo>/prd-toolkit/scripts/prd_help.py <args>, with <tmp> as its working directory."""
    r = subprocess.run(
        [sys.executable, str(HELP_SCRIPT), *args],
        cwd=tmp,
        env=subprocess_env(),
        capture_output=True,
        text=True,
    )
    return Run(r.returncode, r.stdout, r.stderr)


@pytest.fixture
def lint_case(request, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[Run]:
    """Run a case's setup, before: steps and LINT runs; the test body only asserts."""
    case = request.param
    S0(tmp_path, monkeypatch)
    apply_setup(tmp_path, case.get("setup", []))
    results: list[Run] = []
    for run in case.get("runs", [{}]):
        if run.get("before") is not None:
            apply_before(tmp_path, run["before"])
        results.append(LINT(tmp_path))
    return results


# Assertions (testing.md, Harness, Assertions).


def contains_line(text: str, line: str) -> bool:
    return line in text.splitlines()


def not_contains(text: str, subs) -> list[str]:
    """The substrings of subs (a string or a list) that text holds."""
    return [s for s in _as_lines(subs) if s in text]


def in_relative_order(text: str, wanted: list[str]) -> bool:
    lines = text.splitlines()
    i = 0
    for w in wanted:
        while i < len(lines) and lines[i] != w:
            i += 1
        if i == len(lines):
            return False
        i += 1
    return True


def count_of_line(text: str, line: str) -> int:
    return sum(1 for x in text.splitlines() if x == line)


def check(run: Run, expect: dict) -> None:
    """Assert one run against an expect.output mapping; keys the case does not give are not asserted."""
    if "exit" in expect:
        assert run.exit == expect["exit"], f"exit {run.exit}, expected {expect['exit']}\nstdout:\n{run.stdout}\nstderr:\n{run.stderr}"
    if "stderr" in expect:
        assert run.stderr == expect["stderr"], f"stderr:\n{run.stderr}"
    if "stdout" in expect:
        assert run.stdout == expect["stdout"], f"stdout:\n{run.stdout}"
    if "stdout_exact_lines" in expect:
        assert run.stdout.splitlines() == list(expect["stdout_exact_lines"]), f"stdout lines:\n{run.stdout}"
    if "stdout_contains_line" in expect:
        assert contains_line(run.stdout, expect["stdout_contains_line"]), (
            f"no line {expect['stdout_contains_line']!r}\nstdout:\n{run.stdout}"
        )
    if "stdout_not_contains" in expect:
        found = not_contains(run.stdout, expect["stdout_not_contains"])
        assert not found, f"stdout holds {found!r}\nstdout:\n{run.stdout}"
    if "stdout_lines_in_this_relative_order" in expect:
        assert in_relative_order(run.stdout, expect["stdout_lines_in_this_relative_order"]), (
            f"lines not found in order {expect['stdout_lines_in_this_relative_order']!r}\nstdout:\n{run.stdout}"
        )
    if "stdout_count_of_line" in expect:
        c = expect["stdout_count_of_line"]
        n = count_of_line(run.stdout, c["line"])
        assert n == c["count"], f"{n} lines equal {c['line']!r}, expected {c['count']}\nstdout:\n{run.stdout}"
