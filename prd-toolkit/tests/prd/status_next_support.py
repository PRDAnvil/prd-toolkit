"""Shared helper of the status-next characterization tests (testing.md: Harness, Fixtures, Setup steps).

Everything here comes from docs/prd/prd-toolkit/testing.md: the scratch repository the Setup steps build in a
test's tmp_path, the Subprocess environment, the way a CLI script runs (`python <repo>/prd-toolkit/scripts/<script>`
with the test's own interpreter), and the assertion keys `next_part_lines`, `next_items_json`, `stdout_json`,
`stdout_json_at` and `stdout_json_keys_at`.

A setup step that cannot be applied (N0X finding a git checkout, a line a step edits that is not there) raises
SetupError inside the `scratch` fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
SCRIPTS = {
    "STATUS": SCRIPTS_DIR / "prd_status.py",
    "LINT": SCRIPTS_DIR / "prd_lint.py",
    "TRACE": SCRIPTS_DIR / "prd_trace.py",
    "GATES": SCRIPTS_DIR / "prd_gates.py",
}
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures" / "status-next"
ORDERS_REL = Path("docs") / "prd" / "orders"

# A citation of another PRD's T-id is built from parts (testing.md, Layout), never written whole.
AT_PRD = "@" + "prd"

# testing.md, Subprocess environment and Setup steps: the variables a run never inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
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
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    return env


def run(cwd: Path, script: str, *args: str) -> Result:
    """Run `python <SCRIPT> <args>` (STATUS, LINT, TRACE or GATES) in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS[script]), *args],
        cwd=cwd, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def orders(tmp: Path) -> Path:
    """ORDERS, the PRD folder the setup steps write."""
    return tmp / ORDERS_REL


# -- assertion keys (testing.md, Harness, Assertions) --

def next_part_lines(stdout: str) -> list[str]:
    """The stdout lines from the first up to, and not including, the first line that is `## Header`."""
    lines = stdout.splitlines()
    assert "## Header" in lines, f"stdout holds no line `## Header`:\n{stdout}"
    return lines[: lines.index("## Header")]


def one_json_line(stdout: str) -> dict:
    """The whole stdout must be one line ending in a newline; that line parsed as one JSON object."""
    assert stdout.endswith("\n") and len(stdout.splitlines()) == 1, f"stdout is not one line:\n{stdout}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{stdout}"
    return doc


def next_items_json(stdout: str) -> list[dict]:
    """The entries of `items` whose `part` is `Next`, checked to come before every other entry."""
    items = one_json_line(stdout)["items"]
    positions = [i for i, item in enumerate(items) if item.get("part") == "Next"]
    assert positions == list(range(len(positions))), f"a Next entry comes after another entry: {positions}"
    return [items[i] for i in positions]


def json_at(doc, path: str):
    """The value at a `.`-joined path of object keys and list indexes (`""` is the document itself)."""
    value = doc
    if path == "":
        return value
    for part in path.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def keys_at(doc, path: str) -> list[str]:
    return list(json_at(doc, path).keys())


def json_lines(text: str) -> list[dict]:
    """A case's list of JSON mappings, written one per line."""
    return [json.loads(line) for line in text.strip().splitlines() if line.strip()]


# -- fixtures and setup steps (testing.md, Fixtures and Setup steps) --

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / f"{name}.yaml").read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _files(key: str) -> str:
    return _load("files")[key]


def _git(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)


def _write_fixture(tmp: Path, name: str) -> None:
    for key, text in _load(name).items():
        _write(tmp / key, text)


def _git_init(tmp: Path) -> None:
    proc = _git(tmp, "init", "-q")
    if proc.returncode != 0:
        raise SetupError(f"git init -q exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").split("\n")


def _write_lines(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def _level(line: str) -> int:
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def _section(lines: list[str], heading: str) -> tuple[int, int]:
    """The line range under `heading`, up to the next heading of its level or higher."""
    found = [i for i, line in enumerate(lines) if line == heading]
    if len(found) != 1:
        raise SetupError(f"expected one heading {heading!r}, found {len(found)}")
    start, level = found[0] + 1, _level(heading)
    for j in range(start, len(lines)):
        if 0 < _level(lines[j]) <= level:
            return start, j
    return start, len(lines)


def _one_line(lines: list[str], start: int, end: int, old: str) -> int:
    hits = [i for i in range(start, end) if lines[i] == old]
    if len(hits) != 1:
        raise SetupError(f"expected one line {old!r}, found {len(hits)}")
    return hits[0]


def _replace_under(path: Path, heading: str, old: str, new: list[str]) -> None:
    lines = _read_lines(path)
    i = _one_line(lines, *_section(lines, heading), old)
    lines[i:i + 1] = new
    _write_lines(path, lines)


def _replace_frontmatter(path: Path, old: str, new: str) -> None:
    lines = _read_lines(path)
    if lines[0] != "---" or "---" not in lines[1:]:
        raise SetupError(f"{path}: no frontmatter")
    i = _one_line(lines, 1, lines.index("---", 1), old)
    lines[i] = new
    _write_lines(path, lines)


def _append_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_bytes((text + line + "\n").encode("utf-8"))


def _delete_line(path: Path, line: str) -> None:
    lines = _read_lines(path)
    del lines[_one_line(lines, 0, len(lines), line)]
    _write_lines(path, lines)


def _set_index_status(prd_md: Path, value: str, ids: list[str] | None) -> None:
    """Set the Status cell of the rows under `## 11. Requirement index` (every row when `ids` is None)."""
    lines = _read_lines(prd_md)
    start, end = _section(lines, "## 11. Requirement index")
    table = [i for i in range(start, end) if lines[i].startswith("|")]
    if len(table) < 2:
        raise SetupError("no Requirement index table")
    header = [c.strip() for c in lines[table[0]].split("|")]
    col = header.index("Status")
    seen = []
    for i in table[2:]:
        cells = lines[i].split("|")
        row_id = cells[1].strip()
        if ids is None or row_id in ids:
            cells[col] = f" {value} "
            lines[i] = "|".join(cells)
            seen.append(row_id)
    if ids is not None and sorted(seen) != sorted(ids):
        raise SetupError(f"Requirement index rows {ids} not found once each: {seen}")
    _write_lines(prd_md, lines)


def _deploys(tmp: Path) -> Path:
    return tmp / ".git" / "prd-toolkit" / "deploys"


def N0(tmp: Path) -> None:
    _write_fixture(tmp, "base")
    _git_init(tmp)


def N0E(tmp: Path) -> None:
    _write_fixture(tmp, "empty")
    _git_init(tmp)


def N0X(tmp: Path) -> None:
    _write_fixture(tmp, "base")
    proc = _git(tmp, "rev-parse", "--show-toplevel")
    if proc.returncode == 0:
        raise SetupError(f"{tmp} lies inside a git checkout: {proc.stdout.decode('utf-8', 'replace').strip()}")


def NL1(tmp: Path) -> None:
    _append_line(orders(tmp) / "contracts/errors.yaml", "IMPORT_NO_HEADER: {}")


def NL2(tmp: Path) -> None:
    NL1(tmp)
    _append_line(orders(tmp) / "test-cases/import.yaml", "T-001.1: {}")


def NT1(tmp: Path) -> None:
    _delete_line(tmp / "tests/test_orders.py", "# " + AT_PRD + " T-002.1")


def NT2(tmp: Path) -> None:
    _delete_line(tmp / "tests/test_orders.py", "# " + AT_PRD + " T-003.1")


def NE1(tmp: Path) -> None:
    _write(orders(tmp) / "errors.md", _files("errors_confirmed"))


def NE2(tmp: Path) -> None:
    _write(orders(tmp) / "errors.md", _files("errors_proposed"))


def NE3(tmp: Path) -> None:
    _write(orders(tmp) / "errors.md", _files("errors_question"))


def NQ1(tmp: Path) -> None:
    prd_md = orders(tmp) / "prd.md"
    lines = _read_lines(prd_md)
    i = _one_line(lines, *_section(lines, "## 12. Assumptions index"), "|---|---|---|")
    lines.insert(i + 1, "| A-01 | Reports count only shipped orders | awaiting Sample Owner |")
    _write_lines(prd_md, lines)


def NQ2(tmp: Path) -> None:
    prd_md = orders(tmp) / "prd.md"
    _replace_frontmatter(prd_md, "status: Approved", "status: In review")
    _replace_under(prd_md, "## 13. Open questions", "None.", ["- Who signs off the monthly report?"])


def NQ3(tmp: Path) -> None:
    prd_md = orders(tmp) / "prd.md"
    _replace_frontmatter(prd_md, "status: Approved", "status: In review")
    _replace_under(prd_md, "## 13. Open questions", "None.",
                   ["- Who signs off the monthly report", "  before it is sent?", "Which month is the first one?"])


def ND1(tmp: Path) -> None:
    _replace_frontmatter(orders(tmp) / "prd.md", "version: 1.0.0", "version: 0.3.0")


def NA1(tmp: Path) -> None:
    folder = orders(tmp)
    _replace_under(folder / "prd.md", "## 8. Adoption map", "Not applicable: new project.", ["See adoption.md."])
    _write(folder / "adoption.md", _files("adoption"))
    _write(folder / "features/billing.md", _files("features_billing"))
    _write(folder / "features/export.md", _files("features_export"))
    _write(tmp / ".prd-confirm-billing.json", _files("answers_billing"))


def NR1(tmp: Path) -> None:
    _write(_deploys(tmp) / "20261110T090000Z-all.jsonl", _files("log_failed"))


def NR2(tmp: Path) -> None:
    _write(_deploys(tmp) / "20261110T100000Z-all.jsonl", _files("log_unfinished"))


def NR3(tmp: Path) -> None:
    _write(_deploys(tmp) / "20261111T090000Z-all.jsonl", _files("log_human"))


def NR4(tmp: Path) -> None:
    _write(_deploys(tmp) / "20261112T090000Z-all.jsonl", _files("log_unreadable"))


def NR5(tmp: Path) -> None:
    log = _deploys(tmp) / "20261111T090000Z-all.jsonl"
    if not log.is_file():
        raise SetupError("NR5 runs after NR3: the run log 20261111T090000Z-all is missing")
    _append_line(log, '{"kind": "confirm", "step": 2, "reply": "deploy production"}')


def NV2(tmp: Path) -> None:
    folder = orders(tmp)
    _replace_under(folder / "features/import.md", "### FR-002 Skip a duplicate order",
                   "Status: built", ["Status: verified"])
    _set_index_status(folder / "prd.md", "verified", ["FR-002"])


def NB2(tmp: Path) -> None:
    folder = orders(tmp)
    _replace_under(folder / "features/import.md", "### FR-001 Refuse a file with no header",
                   "Status: approved", ["Status: built"])
    _set_index_status(folder / "prd.md", "built", ["FR-001"])


def NB3(tmp: Path) -> None:
    folder = orders(tmp)
    for heading in ("### FR-006 Total the monthly report", "### FR-007 Refuse an unknown month"):
        _replace_under(folder / "features/reports.md", heading, "Status: live (since 1.0.0)", ["Status: approved"])
    _set_index_status(folder / "prd.md", "approved", ["FR-006", "FR-007"])


def NLV(tmp: Path) -> None:
    folder = orders(tmp)
    for rel in ("features/import.md", "features/reports.md"):
        path = folder / rel
        _write_lines(path, ["Status: live (since 1.0.0)" if line.startswith("Status:") else line
                            for line in _read_lines(path)])
    _set_index_status(folder / "prd.md", "live", None)


STEPS = {
    "N0": N0, "N0E": N0E, "N0X": N0X, "NL1": NL1, "NL2": NL2, "NT1": NT1, "NT2": NT2,
    "NE1": NE1, "NE2": NE2, "NE3": NE3, "NQ1": NQ1, "NQ2": NQ2, "NQ3": NQ3, "ND1": ND1, "NA1": NA1,
    "NR1": NR1, "NR2": NR2, "NR3": NR3, "NR4": NR4, "NR5": NR5, "NV2": NV2, "NB2": NB2, "NB3": NB3, "NLV": NLV,
}


@pytest.fixture
def scratch(request, tmp_path) -> Path:
    """<tmp>: the scratch repository, built by the case's setup steps in the order it lists them."""
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def given_steps(*steps: str):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=["+".join(steps)])
