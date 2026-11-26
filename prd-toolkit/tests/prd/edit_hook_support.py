"""Shared helper of the edit-hook characterization tests (testing.md: Harness, Fixtures, Setup steps (edit-hook)).

Everything here comes from docs/prd/prd-toolkit/testing.md: `<tmp>` is `<tmp_path>/repo` and `<outside>` is
`<tmp_path>/outside`, both resolved; the environment the edit-hook paragraph gives (set through monkeypatch before
the first step); the steps H0 to HB, with the status-next steps N0, NL1 and NLV borrowed from
`status_next_support`; the warm-up of the prd launcher for a case whose preconditions name
lint-cli/plugins_superpowers; and the way a case's command and stdin are written and run.

A setup step that cannot be done (a git command that exits other than 0, a line a step changes that is not
there, a warm-up that exits other than 0) raises SetupError inside the `edit_case` fixture, so the test ends as
an error, not a failure.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from status_next_support import N0, NL1, NLV

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
TEXTS = FIXTURES / "edit-hook" / "texts.yaml"
PLUGINS_SUPERPOWERS = FIXTURES / "lint-cli" / "plugins_superpowers.json"
LAUNCHER = REPO / "prd-toolkit" / "scripts" / "prd"
ORDERS_REL = Path("docs") / "prd" / "orders"

# testing.md, Subprocess environment and the edit-hook paragraph: the variables a run never inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_TOOLKIT_EDIT_HOOK",
)
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung command ends the test
WARMUP_TIMEOUT = 600  # seconds; a harness choice: the warm-up may download the uv scripts' packages


class SetupError(Exception):
    """A Setup step could not be done: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: bytes
    stderr: bytes


def subprocess_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(extra or {})
    return env


@dataclass
class EditCase:
    tmp_path: Path
    tmp: Path
    outside: Path
    sid: str
    sid2: str
    texts: dict

    @property
    def orders(self) -> Path:
        return self.tmp / ORDERS_REL

    def _fill(self, text: str) -> str:
        for key, value in (("<tmp>", self.tmp), ("<outside>", self.outside),
                           ("<sid2>", self.sid2), ("<sid>", self.sid)):
            text = text.replace(key, str(value))
        return text

    def _fill_stdin(self, value):
        if isinstance(value, str):
            return self._fill(value)
        if isinstance(value, dict):
            return {key: self._fill_stdin(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._fill_stdin(item) for item in value]
        return value

    def words(self, command: str) -> list[str]:
        words = shlex.split(self._fill(command.replace("<repo>", str(REPO))))
        if words and words[0] == "python":
            words[0] = sys.executable
        return words

    def run(self, command: str, stdin=None, env: dict[str, str] | None = None, cwd: Path | None = None) -> Result:
        """Run a case's command with no shell; a mapping stdin is written as its json.dumps, a string as itself."""
        if stdin is None:
            data = b""
        elif isinstance(stdin, str):
            data = stdin.encode("utf-8")
        else:
            data = json.dumps(self._fill_stdin(stdin)).encode("utf-8")
        proc = subprocess.run(self.words(command), cwd=cwd or self.tmp, env=subprocess_env(env), input=data,
                              capture_output=True, timeout=RUN_TIMEOUT)
        return Result(proc.returncode, proc.stdout, proc.stderr)


# -- assertion keys (testing.md, Harness, Assertions) --

def assert_text(actual: bytes, expected: str) -> None:
    """`stdout` and `stderr`: the whole output byte for byte, against the expected text encoded as UTF-8."""
    assert actual == expected.encode("utf-8"), f"expected {expected!r}, got {actual!r}"


def stdout_json(stdout: bytes) -> dict:
    """The whole stdout must be one line ending in a newline; that line parsed as one JSON object."""
    text = stdout.decode("utf-8")
    assert text.endswith("\n") and len(text.splitlines()) == 1, f"stdout is not one line: {stdout!r}"
    doc = json.loads(text)
    assert isinstance(doc, dict), f"stdout is not a JSON object: {stdout!r}"
    return doc


def json_at(doc, path: str):
    """The value at a `.`-joined path of object keys and list indexes (`""` is the document itself)."""
    value = doc
    if path == "":
        return value
    for part in path.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def stdout_json_at(stdout: bytes, expected: dict) -> None:
    doc = stdout_json(stdout)
    for path, value in expected.items():
        assert json_at(doc, path) == value, f"at {path!r}: expected {value!r}, got {json_at(doc, path)!r}"


def stdout_json_keys_at(stdout: bytes, expected: dict) -> None:
    doc = stdout_json(stdout)
    for path, keys in expected.items():
        assert list(json_at(doc, path).keys()) == keys, f"keys at {path!r}: {list(json_at(doc, path).keys())}"


def stderr_single_line_starts(stderr: bytes, prefix: str) -> None:
    lines = stderr.decode("utf-8").splitlines()
    assert len(lines) == 1 and lines[0].startswith(prefix), f"stderr is not one line starting {prefix!r}: {stderr!r}"


def additional_context(stdout: bytes) -> str:
    return json_at(stdout_json(stdout), "hookSpecificOutput.additionalContext")


def each_run(results: list[Result], exit_code: int = 0, stderr: str = "", stdout: str | None = None) -> None:
    for number, result in enumerate(results, 1):
        assert result.exit == exit_code, f"run_{number} exited {result.exit}: {result.stderr!r}"
        assert result.stderr == stderr.encode("utf-8"), f"run_{number} stderr: {result.stderr!r}"
        if stdout is not None:
            assert result.stdout == stdout.encode("utf-8"), f"run_{number} stdout: {result.stdout!r}"


# -- setup steps (testing.md, Setup steps (edit-hook)) --

def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _git(tmp: Path, *args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


def _commit(tmp: Path, message: str) -> None:
    _git(tmp, "add", "-A")
    _git(tmp, "-c", "user.name=Sample", "-c", "user.email=sample@example.com", "-c", "commit.gpgsign=false",
         "commit", "-q", "-m", message)


def _heading_level(line: str) -> int:
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def _adoption_line(case: EditCase) -> None:
    """In prd.md, the line `Not applicable: new project.` under `## 8. Adoption map` becomes `See adoption.md.`."""
    prd_md = case.orders / "prd.md"
    lines = prd_md.read_text(encoding="utf-8").split("\n")
    heading = "## 8. Adoption map"
    found = [i for i, line in enumerate(lines) if line == heading]
    if len(found) != 1:
        raise SetupError(f"expected one heading {heading!r} in prd.md, found {len(found)}")
    start, end = found[0] + 1, len(lines)
    for j in range(start, len(lines)):
        if 0 < _heading_level(lines[j]) <= 2:
            end = j
            break
    hits = [i for i in range(start, end) if lines[i] == "Not applicable: new project."]
    if len(hits) != 1:
        raise SetupError(f"expected one line 'Not applicable: new project.' under {heading!r}, found {len(hits)}")
    lines[hits[0]] = "See adoption.md."
    prd_md.write_bytes("\n".join(lines).encode("utf-8"))


def H0(case: EditCase) -> None:
    N0(case.tmp)
    _commit(case.tmp, "base")


def HC(case: EditCase) -> None:
    _commit(case.tmp, "step")


def HA(case: EditCase) -> None:
    _adoption_line(case)
    _write(case.orders / "adoption.md", case.texts["adoption"].encode("utf-8"))
    HC(case)


def HL(case: EditCase) -> None:
    NLV(case.tmp)
    HC(case)


def HW(case: EditCase) -> None:
    path = case.orders / "features" / "import.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith("Status:")]
    if not hits:
        raise SetupError("features/import.md holds no line that starts with 'Status:'")
    lines[hits[0]] = "Status: approved"
    path.write_bytes("\n".join(lines).encode("utf-8"))


def HX(case: EditCase) -> None:
    _write(case.orders / "adoption.md", case.texts["adoption"].encode("utf-8") + b"\xff" + b"\n")
    _adoption_line(case)
    HC(case)


def H2(case: EditCase) -> None:
    source = case.orders
    target = case.tmp / "docs" / "prd" / "orders2"
    for path in sorted(source.rglob("*")):
        if path.is_file():
            dest = target / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)


def HB(case: EditCase) -> None:
    _write(case.tmp / ".prd-toolkit" / "prd", case.texts["stub_broken"].encode("utf-8"))


def HG(case: EditCase) -> None:
    _write(case.tmp / ".prd-toolkit" / "prd", case.texts["stub_logging"].encode("utf-8"))


STEPS = {
    "H0": H0, "HC": HC, "HA": HA, "HL": HL, "HW": HW, "HX": HX, "H2": H2, "HB": HB, "HG": HG,
    "NL1": lambda case: NL1(case.tmp), "NLV": lambda case: NLV(case.tmp),
}


def _warm_up(case: EditCase) -> None:
    """`sh <repo>/prd-toolkit/scripts/prd lint --list-rules` once in <tmp>, so the launcher's uv environment exists."""
    proc = subprocess.run(["sh", str(LAUNCHER), "lint", "--list-rules"], cwd=case.tmp, env=subprocess_env(),
                          capture_output=True, timeout=WARMUP_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"the launcher warm-up exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


@pytest.fixture
def edit_case(request, tmp_path, monkeypatch) -> EditCase:
    """The case's state: environment, folders, its `setup:` steps in order, and the warm-up when it needs one."""
    steps, plugins = request.param
    base = tmp_path.resolve()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_TOOLKIT_EDIT_HOOK"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    temp = base / "temp"
    temp.mkdir()
    monkeypatch.setenv("TMPDIR", str(temp))
    if plugins:
        monkeypatch.setenv("PRD_PLUGINS_FILE", str(PLUGINS_SUPERPOWERS))
    tmp, outside = base / "repo", base / "outside"
    tmp.mkdir()
    outside.mkdir()
    case = EditCase(tmp_path=base, tmp=tmp.resolve(), outside=outside.resolve(), sid=uuid.uuid4().hex,
                    sid2=uuid.uuid4().hex, texts=yaml.safe_load(TEXTS.read_text(encoding="utf-8")))
    for step in steps:
        STEPS[step](case)
    if plugins:
        _warm_up(case)
    return case


def given(*steps: str, plugins: bool = False):
    """Mark a test with its case's `setup:` list and whether its preconditions name lint-cli/plugins_superpowers."""
    return pytest.mark.parametrize("edit_case", [(steps, plugins)], indirect=True, ids=["+".join(steps) or "none"])
