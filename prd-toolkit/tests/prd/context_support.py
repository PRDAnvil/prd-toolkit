"""Shared helper of the context characterization tests (testing.md: Harness, Setup steps, the context paragraph).

Everything here comes from docs/prd/prd-toolkit/testing.md and the header of test-cases/context.yaml: the steps
CX0 to CXL with COMMIT and IMPORTER, the environment of a run, the way a run's command text becomes its argument
list, and the assertion keys of Harness, Assertions (pack_part_titles, pack_part_lines, stdout_json_at, ...).

N0 and N0X are borrowed from status_next_support (Borrowed steps and helpers). Every other helper is defined here.
A step that cannot be applied (a git command that exits other than 0, a line it is to change that is not there)
raises SetupError inside the `scratch` fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml

from status_next_support import N0 as _borrowed_N0, N0X as _borrowed_N0X

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
CTX = REPO / "prd-toolkit" / "scripts" / "prd_context.py"
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_REL = Path("docs") / "prd" / "orders"
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test

# testing.md: Subprocess environment, the status-next steps' terms, and the context paragraph (PRD_PLUGINS_FILE).
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_PLUGINS_FILE",
)

IMPORTER = [
    "def import_file(path):",
    "    header = read_header(path)",
    "    if header is None:",
    "        raise SystemExit(2)",
    "",
    "    return header",
]


class SetupError(Exception):
    """A step could not be applied: the test ends as an error, not a failure."""


class KnownFailure(Exception):
    """The expected failure of a known-failing case: raised only when the test sees the case's `symptom:`."""


@dataclass
class Scratch:
    tmp: Path
    values: dict = field(default_factory=dict)

    @property
    def sha(self) -> str:
        return self.values["sha"]

    @property
    def real(self) -> str:
        """`<real tmp>`: os.path.realpath(<tmp>)."""
        return os.path.realpath(self.tmp)

    @property
    def orders(self) -> Path:
        return self.tmp / ORDERS_REL


@dataclass
class Result:
    exit: int
    out_b: bytes
    err_b: bytes

    @property
    def out(self) -> str:
        return self.out_b.decode("utf-8")

    @property
    def err(self) -> str:
        return self.err_b.decode("utf-8")


# -- environment and runs --

def env(extra: dict[str, str] | None = None) -> dict[str, str]:
    e = dict(os.environ)
    for name in _DROPPED_ENV:
        e.pop(name, None)
    e.update(extra or {})
    return e


def _words(s: Scratch, command) -> list[str]:
    if isinstance(command, list):
        words = [w.replace("CTX", str(CTX)).replace("<tmp>", str(s.tmp)) for w in command]
    else:
        words = shlex.split(command.replace("CTX", str(CTX)).replace("<tmp>", str(s.tmp)))
    if words and words[0] == "python":
        words[0] = sys.executable
    return words


def run(s: Scratch, spec) -> Result:
    """Run one entry of a case's `runs:`: a command text, an argument list, or a mapping {command, cwd, env}."""
    cwd, extra = s.tmp, {}
    if isinstance(spec, dict):
        if "cwd" in spec:
            cwd = Path(spec["cwd"].replace("<tmp>", str(s.tmp)))
        for key, value in spec.get("env", {}).items():
            extra[key] = value.replace("<tmp>", str(s.tmp)).replace("<the runner's PATH>", os.environ.get("PATH", ""))
        spec = spec["command"]
    proc = subprocess.run(_words(s, spec), cwd=cwd, env=env(extra), capture_output=True, timeout=RUN_TIMEOUT)
    return Result(proc.returncode, proc.stdout, proc.stderr)


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, env=env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout.decode("utf-8")


# -- assertion keys (testing.md, Harness, Assertions) --

def titles(out: str) -> list[str]:
    """pack_part_titles: the stdout lines that start with `## `, in order."""
    return [line for line in out.splitlines() if line.startswith("## ")]


def part(out: str, title: str) -> list[str]:
    """pack_part_lines: from the line `## <title>` (exactly once) up to the next `## ` line or the end of stdout."""
    lines = out.splitlines()
    hits = [i for i, line in enumerate(lines) if line == f"## {title}"]
    assert len(hits) == 1, f"stdout holds the line '## {title}' {len(hits)} times:\n{out}"
    start = hits[0]
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return lines[start:end]


def one_json(out: str) -> dict:
    """The whole stdout is one line ending in a newline, parsed as one JSON object."""
    assert out.endswith("\n") and len(out.splitlines()) == 1, f"stdout is not one line:\n{out}"
    doc = json.loads(out)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{out}"
    return doc


def json_at(doc, path: str):
    if path == "":
        return doc
    value = doc
    for piece in path.split("."):
        value = value[int(piece)] if isinstance(value, list) else value[piece]
    return value


def assert_json_at(out: str, expected: dict) -> None:
    doc = one_json(out)
    for path, value in expected.items():
        assert json_at(doc, path) == value, f"{path}: {json_at(doc, path)!r} != {value!r}"


def assert_relative_order(out: str, wanted: list[str]) -> None:
    """stdout_lines_in_this_relative_order: each line, whole, after the one before it."""
    lines, pos = out.splitlines(), 0
    for line in wanted:
        try:
            pos = lines.index(line, pos) + 1
        except ValueError:
            raise AssertionError(f"line {line!r} not found after line {pos}:\n{out}") from None


def assert_last_line_starts(err: str, text: str) -> None:
    lines = err.splitlines()
    assert lines and lines[-1].startswith(text), f"last stderr line does not start {text!r}:\n{err}"


def assert_first_line_starts(text_out: str, text: str) -> None:
    lines = text_out.splitlines()
    assert lines and lines[0].startswith(text), f"first line does not start {text!r}:\n{text_out}"


def headings(lines: list[str]) -> list[str]:
    return [line for line in lines if line.startswith("### ")]


def load_texts() -> dict:
    """Fixture context/texts."""
    return yaml.safe_load((FIXTURES / "context" / "texts.yaml").read_text(encoding="utf-8"))


# -- file edits (every line a step writes ends in a newline) --

def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("".join(line + "\n" for line in lines)).encode("utf-8"))


def _read(path: Path) -> list[str]:
    if not path.is_file():
        raise SetupError(f"{path}: no such file")
    return path.read_text(encoding="utf-8").split("\n")


def _save(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def _unique(lines: list[str], line: str, path: Path) -> int:
    hits = [i for i, x in enumerate(lines) if x == line]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected the line {line!r} once, found it {len(hits)} times")
    return hits[0]


def insert_after(path: Path, anchor: str, new: list[str]) -> None:
    lines = _read(path)
    i = _unique(lines, anchor, path)
    lines[i + 1:i + 1] = new
    _save(path, lines)


def insert_at(path: Path, number: int, new: list[str]) -> None:
    """Insert `new` so that its first line becomes line `number` (1-based)."""
    lines = _read(path)
    if number - 1 > len(lines) - 1:
        raise SetupError(f"{path}: no line {number}")
    lines[number - 1:number - 1] = new
    _save(path, lines)


def replace_line(path: Path, old: str, new: list[str], first: bool = False) -> None:
    lines = _read(path)
    if first:
        if old not in lines:
            raise SetupError(f"{path}: no line {old!r}")
        i = lines.index(old)
    else:
        i = _unique(lines, old, path)
    lines[i:i + 1] = new
    _save(path, lines)


def set_line(path: Path, number: int, text: str) -> None:
    lines = _read(path)
    if number < 1 or number > len(lines) - 1:
        raise SetupError(f"{path}: no line {number}")
    lines[number - 1] = text
    _save(path, lines)


def replace_under(path: Path, heading: str, old: str, new: list[str]) -> None:
    """Replace the first line `old` in the section under the level-2 `heading`."""
    lines = _read(path)
    h = _unique(lines, heading, path)
    end = next((j for j in range(h + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    hits = [i for i in range(h + 1, end) if lines[i] == old]
    if not hits:
        raise SetupError(f"{path}: no line {old!r} under {heading!r}")
    lines[hits[0]:hits[0] + 1] = new
    _save(path, lines)


def append_lines(path: Path, new: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        raise SetupError(f"{path}: its last line has no newline")
    path.write_bytes((text + "".join(line + "\n" for line in new)).encode("utf-8"))


def delete_range(path: Path, start_line: str, stop_line: str) -> None:
    """Delete the lines from `start_line` up to, not including, `stop_line`."""
    lines = _read(path)
    a, b = _unique(lines, start_line, path), _unique(lines, stop_line, path)
    if b <= a:
        raise SetupError(f"{path}: {stop_line!r} does not follow {start_line!r}")
    del lines[a:b]
    _save(path, lines)


# -- steps (test-cases/context.yaml header) --

def N0(s: Scratch, root: Path | None = None) -> None:
    _borrowed_N0(root or s.tmp)


def N0X(s: Scratch) -> None:
    _borrowed_N0X(s.tmp)


def COMMIT(s: Scratch, root: Path | None = None, message: str = "base") -> None:
    root = root or s.tmp
    git(root, "add", "-A")
    git(root, "-c", "user.name=Sample", "-c", "user.email=sample@example.com", "-c", "commit.gpgsign=false",
        "commit", "-q", "-m", message)
    s.values["sha"] = git(root, "rev-parse", "--short=7", "HEAD").strip()


def _orders(s: Scratch, root: Path | None) -> Path:
    return (root or s.tmp) / ORDERS_REL


def CX0(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)


def _adoption_pointer(prd: Path) -> None:
    replace_line(prd / "prd.md", "Not applicable: new project.", ["See adoption.md."])


def CXA(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    prd = _orders(s, root)
    _adoption_pointer(prd)
    write_lines(prd / "adoption.md", [
        "# Adoption map", "", "| Area | State | Boundary |", "|---|---|---|",
        "| import | adopted | `src/importer.py`, `tests/test_orders.py` |", "| reports | not started | |",
    ])
    write_lines(prd / "features/billing.md", ["# Billing"])


def CXE(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    prd = _orders(s, root)
    _adoption_pointer(prd)
    write_lines(prd / "adoption.md", ["# Adoption map", "", "| Area | State | Boundary |", "|---|---|---|"])


TESTS_001 = "Tests: T-001.1 [integration]  (test-cases/import.yaml)"
ERRORS_ROW = "| errors | `contracts/errors.yaml` | built-in |"


def CXN(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    append_lines(_orders(s, root) / "nfr.md", [
        "", "### NFR-008 Import speed", "Status: approved", "Acceptance (EARS):",
        "- AC-008.1 The importer shall store a 10,000-row file in under 60 seconds.", "Errors: -",
        "Tests: T-008.1 [integration]  (test-cases/nfr.yaml)",
    ])


def CXR(s: Scratch, root: Path | None = None) -> None:
    CXN(s, root)
    prd = _orders(s, root)
    append_lines(prd / "features/reports.md", [
        "", "### UJ-01 Read a month's orders", "Flow: 1. A user asks for a month → 2. the report prints its orders",
    ])
    insert_after(prd / "features/import.md", TESTS_001, ["Traces: UJ-01, UJ-02"])


def CXC(s: Scratch, root: Path | None = None) -> None:
    CXN(s, root)
    prd = _orders(s, root)
    insert_after(prd / "prd.md", ERRORS_ROW, ["| cli | `contracts/cli.yaml` | `true` |"])
    lines = _read(prd / "prd.md")
    h = _unique(lines, "| ID | Assumption | Status |", prd / "prd.md")
    if lines[h + 1] != "|---|---|---|":
        raise SetupError("prd.md: no `|---|---|---|` line under `| ID | Assumption | Status |`")
    lines[h + 2:h + 2] = ["| A-01 | Import files are UTF-8 | open |"]
    _save(prd / "prd.md", lines)
    write_lines(prd / "contracts/cli.yaml", ["importer:", "  invocation: python import.py", "  exit: 2"])
    replace_line(prd / "features/import.md", "Errors: IMPORT_NO_HEADER (contracts/errors.yaml)",
                 ["Errors: IMPORT_NO_HEADER, IMPORT_EMPTY, IMPORT_BAD_DATE (contracts/errors.yaml)"])
    insert_after(prd / "features/import.md", TESTS_001,
                 ["Traces: NFR-008; cli:importer.", load_texts()["cxc_edge_line"]])


def CXK(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    prd = _orders(s, root)
    insert_at(prd / "features/reports.md", 3, ["Target: pack document 1.0.0 (prd-toolkit)", ""])
    insert_after(prd / "prd.md", ERRORS_ROW, ["| outline | `contracts/outline.yaml` | pack |"])
    write_lines(prd / "contracts/outline.yaml", ["guide:", "  title: Install guide"])
    replace_line(prd / "test-cases/reports.yaml", "  target: code:reports.monthly", ["  target: doc:guide"], first=True)


def CXS(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    base = root or s.tmp
    write_lines(base / "src/importer.py", IMPORTER)
    COMMIT(s, root)
    insert_after(_orders(s, root) / "features/import.md", "Status: approved",
                 [f"Source: src/importer.py:3 @{s.sha}"])


def CXM(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    base = root or s.tmp
    write_lines(base / "src/importer.py", IMPORTER)
    write_lines(base / "src/calc.py", ["total = 0"])
    COMMIT(s, root)
    insert_at(base / "src/importer.py", 1, ["import os"])
    insert_after(_orders(s, root) / "features/import.md", "Status: approved",
                 [f"Source: src/importer.py:3 @{s.sha}", f"  src/calc.py:1 @{s.sha}"])


def CXT(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    base = root or s.tmp
    write_lines(base / "src/importer.py", IMPORTER)
    write_lines(base / "src/twice.py", ["a = 1", "b = 2"])
    COMMIT(s, root)
    set_line(base / "src/importer.py", 3, "    if not header:")
    write_lines(base / "src/twice.py", ["b = 2", "a = 1", "b = 2"])
    write_lines(base / "src/new.py", ["x = 1"])
    sha = s.sha
    insert_after(_orders(s, root) / "features/import.md", "Status: approved", [
        f"Source: src/importer.py:3 @{sha}", f"  src/importer.py:9 @{sha}", f"  src/gone.py:1 @{sha}",
        f"  src/new.py:1 @{sha}", "  src/importer.py:2 @0000000", f"  src/twice.py:2 @{sha}",
    ])


def CXB(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    base = root or s.tmp
    for name in ("a", "b", "c"):
        write_lines(base / f"src/{name}.py", ["x = 1", "", "y = 2"])
    COMMIT(s, root)
    first = s.sha
    set_line(base / "src/c.py", 3, "y = 3")
    COMMIT(s, root, message="second")
    s.values["sha"] = first  # <sha> is the first commit's hash
    set_line(base / "src/b.py", 3, "y = 4")
    insert_after(_orders(s, root) / "features/import.md", "Status: approved", [
        f"Source: src/a.py:2 @{first}", f"  src/b.py:2 @{first}", f"  src/c.py:2 @{first}",
    ])


def CXP(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    base = root or s.tmp
    write_lines(base / "src/importer.py", IMPORTER)
    COMMIT(s, root)
    set_line(base / "src/importer.py", 3, "    if not header:")
    imp = _orders(s, root) / "features/import.md"
    if _read(imp)[2] != "### FR-001 Refuse a file with no header":
        raise SetupError("features/import.md: line 3 is not `### FR-001 Refuse a file with no header`")
    insert_at(imp, 3, ["### UJ-01 Import a file", f"Source: src/importer.py:3 @{s.sha}", ""])
    insert_after(imp, TESTS_001, ["Traces: UJ-01"])


def CXO(s: Scratch, root: Path | None = None) -> None:
    CXP(s, root)
    insert_after(_orders(s, root) / "features/import.md", "Status: approved",
                 [f"Source: src/importer.py:3 @{s.sha}", f"  src/importer.py:3 @{s.sha}"])


def CXL(s: Scratch, root: Path | None = None) -> None:
    N0(s, root)
    prd = _orders(s, root)
    write_lines(prd / "links.md", [
        "# Links", "", "## Upstreams", "", "| Upstream | Location | Version | Commit | Needs |",
        "|---|---|---|---|---|", "| greet | `../greet` | | | |",
    ])
    insert_after(prd / "features/import.md", TESTS_001, ["Traces: op:greet/hello"])


def in_dir(step, name: str):
    """`<step> in <tmp>/<name>`."""
    def at(s: Scratch) -> None:
        step(s, s.tmp / name)
    at.__name__ = f"{step.__name__}@{name}"
    return at


def mkdir(name: str):
    """`create the empty folder <tmp>/<name>`."""
    def make(s: Scratch) -> None:
        (s.tmp / name).mkdir(parents=True)
    make.__name__ = f"mkdir-{name}"
    return make


# -- the fixture --

@pytest.fixture
def scratch(request, tmp_path, monkeypatch) -> Scratch:
    """<tmp>: GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM set in the test's process, then the case's steps in order."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    s = Scratch(tmp_path)
    for step in getattr(request, "param", ()):
        step(s)
    return s


def given(*steps):
    """Mark a test with its case's `setup:` steps (callables taking the Scratch); `scratch` runs them."""
    name = "+".join(getattr(step, "__name__", "step") for step in steps) or "none"
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=[name])


SIZE_RE = re.compile(r"pack ([0-9,]+) bytes \(~([0-9]+\.[0-9])k tokens, bytes / 4\); prd\.md ([0-9,]+)")
SIZE_RE_AREA = re.compile(
    r"pack ([0-9,]+) bytes \(~([0-9]+\.[0-9])k tokens, bytes / 4\); prd\.md ([0-9,]+); features/import\.md ([0-9,]+)")
