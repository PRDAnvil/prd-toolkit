"""The practices area's shared test helper (testing.md: Harness, Fixtures, Setup steps; test-cases/practices.yaml).

Every value here comes from docs/prd/prd-toolkit: the scripts' paths (the conventions at the top of
test-cases/practices.yaml), the Subprocess environment, the fixtures practices/repo, practices/texts and
repo/vendored, the practices Setup steps (P0 ... PK3) and the Assertions keys.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# tests/prd/practices_support.py -> tests/prd -> tests -> prd-toolkit -> the repository root
REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "prd-toolkit" / "scripts"
PRACTICES = SCRIPTS / "prd_practices.py"
LINT = SCRIPTS / "prd_lint.py"
CHANGE = SCRIPTS / "prd_change.py"
CONTEXT = SCRIPTS / "prd_context.py"
DISPATCH = SCRIPTS / "prd_dispatch.py"
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_REL = "docs/prd/orders"

# Harness, Subprocess environment, and the practices Setup steps' own removals.
_DROPPED = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
)


class SetupError(RuntimeError):
    """A setup step could not be applied as testing.md writes it (the fixture is not what the step expects)."""


def environment(extra: dict | None = None) -> dict:
    """The runner's environment as it is now, minus the variables testing.md removes, plus the case's own env."""
    env = {k: v for k, v in os.environ.items() if k not in _DROPPED}
    if extra:
        env.update(extra)
    return env


@dataclass
class Run:
    args: list
    returncode: int
    stdout_bytes: bytes
    stderr_bytes: bytes

    @property
    def stdout(self) -> str:
        return self.stdout_bytes.decode("utf-8")

    @property
    def stderr(self) -> str:
        return self.stderr_bytes.decode("utf-8")

    def __repr__(self) -> str:
        return (f"Run({self.args!r}, exit={self.returncode}, stdout={self.stdout_bytes!r}, "
                f"stderr={self.stderr_bytes!r})")


def run(cwd: Path, *args, env: dict | None = None) -> Run:
    """Run `python <args...>` with the test's own interpreter, `cwd` the working directory."""
    cmd = [sys.executable, *(str(a) for a in args)]
    p = subprocess.run(cmd, cwd=str(cwd), env=environment(env), capture_output=True, timeout=600)
    return Run(cmd, p.returncode, p.stdout, p.stderr)


# -- fixtures --------------------------------------------------------------------------------------------------

def fixture(name: str):
    """A YAML fixture under contracts/fixtures/, read with yaml.safe_load."""
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def orders(tmp: Path) -> Path:
    return Path(tmp) / ORDERS_REL


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def write_lines(path: Path, lines: list[str]) -> None:
    """Write each line followed by a newline, the last one included."""
    write_text(path, "".join(line + "\n" for line in lines))


def git_init(cwd: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=str(cwd), env=environment(), check=True,
                   capture_output=True)


def _write_repo(root: Path) -> None:
    for key, text in fixture("practices/repo.yaml").items():
        write_text(root / key, text)


def load_vendored(tmp: Path) -> None:
    """Fixture repo/vendored: copy <repo>/.prd-toolkit to <tmp>/.prd-toolkit as plain files, no __pycache__, and check it.

    A check that fails raises SetupError; call this from a pytest fixture so it ends the test as an error.
    """
    dest = Path(tmp) / ".prd-toolkit"
    shutil.copytree(REPO / ".prd-toolkit", dest, symlinks=False,
                    ignore=shutil.ignore_patterns("__pycache__"))
    packs = dest / "packs"
    names = sorted(p.name for p in packs.iterdir() if not p.name.startswith("."))
    if names != ["service"] or not (packs / "service").is_dir():
        raise SetupError(f"repo/vendored: packs/ holds {names!r}, not the one folder 'service'")
    sources = json.loads((dest / "pack-sources.json").read_text(encoding="utf-8"))
    if sources != {"service": "prd-toolkit"}:
        raise SetupError(f"repo/vendored: pack-sources.json is {sources!r}")


# -- line and cell edits ---------------------------------------------------------------------------------------

def _lines(path: Path) -> list[str]:
    return path.read_bytes().decode("utf-8").split("\n")


def _store(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def replace_line_at(path: Path, lineno: int, before: str, after: str) -> None:
    lines = _lines(path)
    if lines[lineno - 1] != before:
        raise SetupError(f"{path.name}:{lineno} is {lines[lineno - 1]!r}, not {before!r}")
    lines[lineno - 1] = after
    _store(path, lines)


def replace_line_under(path: Path, heading: str, before: str, after: str) -> None:
    """Replace the first line equal to `before` after the line `heading`."""
    lines = _lines(path)
    start = lines.index(heading)
    for i in range(start + 1, len(lines)):
        if lines[i] == before:
            lines[i] = after
            _store(path, lines)
            return
    raise SetupError(f"{path.name}: no line {before!r} under {heading!r}")


def replace_frontmatter_line(path: Path, before: str, after: str) -> None:
    lines = _lines(path)
    if lines[0] != "---":
        raise SetupError(f"{path.name}: no frontmatter")
    end = lines.index("---", 1)
    for i in range(1, end):
        if lines[i] == before:
            lines[i] = after
            _store(path, lines)
            return
    raise SetupError(f"{path.name}: no frontmatter line {before!r}")


def edit_cell(path: Path, lineno: int, column: int, before: str, after: str) -> None:
    """Change the text of cell `column` (1 is the first cell after the leading `|`) of line `lineno`.

    The cell's surrounding spaces and every `|` stay as they are; only its text changes.
    """
    lines = _lines(path)
    cells = lines[lineno - 1].split("|")
    cell = cells[column]
    if cell.strip() != before:
        raise SetupError(f"{path.name}:{lineno} cell {column} is {cell!r}, not {before!r}")
    lead = cell[: len(cell) - len(cell.lstrip())]
    trail = cell[len(cell.rstrip()):]
    cells[column] = lead + after + trail
    lines[lineno - 1] = "|".join(cells)
    _store(path, lines)


# Cell positions: a source row is ID, Title, Location, Covers, Read, Decision; a practice row is ID, Source,
# Object (glob), Applies to, Practice; a section 5 row is Object (glob), Linter command, Rules live in, ...
S_ID, S_READ, S_DECISION = 1, 5, 6
P_ID, P_SOURCE, P_GLOB, P_APPLIES = 1, 2, 3, 4
STD_RULES = 3


# -- the practices Setup steps ---------------------------------------------------------------------------------

def P0(tmp: Path) -> None:
    _write_repo(Path(tmp))
    git_init(Path(tmp))


def P0B(tmp: Path) -> None:
    b = Path(tmp) / "b"
    _write_repo(b)
    (b / ORDERS_REL / "practices.md").unlink()
    git_init(b)


def PN(tmp: Path) -> None:
    (orders(tmp) / "practices.md").unlink()


def PM(tmp: Path) -> None:
    dest = orders(tmp) / "notes" / "practices.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    (orders(tmp) / "practices.md").rename(dest)


def PA1(tmp: Path) -> None:
    (orders(tmp) / "adoption.md").unlink()
    replace_line_under(orders(tmp) / "prd.md", "## 8. Adoption map", "See adoption.md.",
                       "Not applicable: new project.")


def PR1(tmp: Path) -> None:
    replace_frontmatter_line(orders(tmp) / "prd.md", "status: Approved", "status: In review")


def PI1(tmp: Path) -> None:
    path = orders(tmp) / "prd.md"
    text = path.read_bytes().decode("utf-8")
    if not text.endswith("\n"):
        raise SetupError("prd.md does not end in a newline")
    line = "| 1.1.0 | 2026-11-05 | two rows removed; no dry run (removal only) | S-05, P-07, CS-009 |"
    path.write_bytes((text + line + "\n").encode("utf-8"))


def _pmd(tmp: Path) -> Path:
    return orders(tmp) / "practices.md"


def PB1(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 8, S_ID, "S-02", "S-2")
    edit_cell(_pmd(tmp), 16, P_ID, "P-03", "P-3")


def PB2(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 8, S_ID, "S-02", "S-01")
    edit_cell(_pmd(tmp), 16, P_ID, "P-03", "P-02")


def PB3(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 8, S_DECISION, "declined", "maybe")


def PB4(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 8, S_DECISION, "declined", "proposed")


def PB5(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 15, P_SOURCE, "S-01", "S-09")


def PB6(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 15, P_APPLIES, "code", "docs")


def PB7(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 14, P_GLOB, "`src/**/*.py`", "")
    edit_cell(_pmd(tmp), 15, P_GLOB, "`tests/*.py`", "-")


def PB8(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 7, S_READ, "2026-11-01", "November 2026")
    edit_cell(_pmd(tmp), 8, S_READ, "2026-11-02", "2026-02-30")


def PB9(tmp: Path) -> None:
    edit_cell(orders(tmp) / "prd.md", 45, STD_RULES, "`pyproject.toml`, S-01",
              "`pyproject.toml`, S-01, S-02, S-07, CS-08")


def PB10(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 14, P_GLOB, "`src/**/*.py`", "`lib/**/*.rb`")


def PB11(tmp: Path) -> None:
    edit_cell(_pmd(tmp), 16, P_SOURCE, "S-01", "S-02")


def PF1(tmp: Path) -> None:
    write_text(_pmd(tmp), fixture("practices/texts.yaml")["format"])


def PF2(tmp: Path) -> None:
    replace_line_at(_pmd(tmp), 10, "## Practices", "## Checklist")


def PU1(tmp: Path) -> None:
    _pmd(tmp).write_bytes(bytes.fromhex("fffe00"))


_TOOLKIT = 'toolkit: ">=0.8.0,<0.9"'
_PY_SOURCE = '  - {title: Python style guide, location: "https://example.com/python-style", covers: Python}'


def PK0(tmp: Path, monkeypatch) -> None:
    """Write <tmp>/plugins.json and set PRD_PLUGINS_FILE to it for every run of the case."""
    path = Path(tmp) / "plugins.json"
    write_lines(path, ['{"plugins": {"demo@example": [{"installPath": "' + str(tmp) + '/plug"}]}}'])
    monkeypatch.setenv("PRD_PLUGINS_FILE", str(path))


def PK1(tmp: Path) -> None:
    write_lines(Path(tmp) / "plug/prd-packs/demo/pack.yaml", [
        "pack: demo", "version: 1.0.0", _TOOLKIT, "description: A pack for the practices cases.",
        "sources:", _PY_SOURCE,
    ])


def PK2(tmp: Path) -> None:
    write_lines(Path(tmp) / "plug/prd-packs/demo2/pack.yaml", [
        "pack: demo2", "version: 1.0.0", _TOOLKIT, "description: An item without covers.",
        "sources:", _PY_SOURCE, "  - {title: Notes, location: docs/notes.md}",
    ])
    write_lines(Path(tmp) / "plug/prd-packs/demo3/pack.yaml", [
        "pack: demo3", "version: 1.0.0", _TOOLKIT, "description: Sources that are not a list.",
        "sources: none",
    ])


def PK3(tmp: Path) -> None:
    write_lines(Path(tmp) / "plug/prd-packs/demo4/pack.yaml", [
        "pack: demo4", "version: 1.0.0", _TOOLKIT, "description: A pack without sources.",
    ])
    write_lines(Path(tmp) / "plug/prd-packs/demo5/pack.yaml", [
        "pack: demo5", "version: 1.0.0", _TOOLKIT, "description: A misspelt key.", "source: []",
    ])


def setup(tmp: Path, *steps) -> None:
    """Run the named steps in order."""
    for step in steps:
        step(Path(tmp))


# -- assertions (testing.md, Harness, Assertions) ----------------------------------------------------------------

def same(actual, expected) -> bool:
    """Deep equality in which a JSON value's type counts (1 is not true, "1" is not 1)."""
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and set(actual) == set(expected)
                and all(same(actual[k], expected[k]) for k in expected))
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(same(a, e) for a, e in zip(actual, expected)))
    return type(actual) is type(expected) and actual == expected


def one_json_line(r: Run):
    """The whole stdout is one line ending in a newline; return it parsed as one JSON object."""
    out = r.stdout
    assert out.endswith("\n") and "\n" not in out[:-1], f"stdout is not one line ending in a newline: {r!r}"
    doc = json.loads(out)
    assert isinstance(doc, dict), f"stdout is not a JSON object: {r!r}"
    return doc


def json_at(doc, path: str):
    cur = doc
    if path == "":
        return cur
    for key in path.split("."):
        cur = cur[int(key)] if isinstance(cur, list) else cur[key]
    return cur


def pack_titles(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if line.startswith("## ")]


def pack_part(stdout: str, title: str) -> list[str]:
    lines = stdout.splitlines()
    head = "## " + title
    assert lines.count(head) == 1, f"stdout holds {lines.count(head)} lines {head!r}, not one"
    i = lines.index(head)
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
    return lines[i:j]


def pack_parts(stdout: str) -> list[tuple[str, list[str]]]:
    """Every part of a pack, in order: (title, its lines from `## <title>` up to the next `## ` line or the end)."""
    lines = stdout.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    out = []
    for n, i in enumerate(starts):
        j = starts[n + 1] if n + 1 < len(starts) else len(lines)
        out.append((lines[i][3:], lines[i:j]))
    return out


def check(r: Run, **expect) -> None:
    """Assert each of the case's expect.output keys on one run."""
    for key, want in expect.items():
        if key == "exit":
            assert r.returncode == want, f"exit {r.returncode}, expected {want}: {r!r}"
        elif key == "stdout":
            assert r.stdout_bytes == want.encode("utf-8"), f"stdout != {want!r}: {r!r}"
        elif key == "stderr":
            assert r.stderr_bytes == want.encode("utf-8"), f"stderr != {want!r}: {r!r}"
        elif key == "stdout_exact_lines":
            assert r.stdout.splitlines() == want, f"stdout lines != {want!r}: {r!r}"
        elif key == "stdout_contains_line":
            assert want in r.stdout.splitlines(), f"no stdout line {want!r}: {r!r}"
        elif key in ("stdout_contains", "stdout_not_contains", "stderr_not_contains"):
            text = r.stderr if key.startswith("stderr") else r.stdout
            for s in ([want] if isinstance(want, str) else want):
                if key.endswith("not_contains"):
                    assert s not in text, f"{key}: {s!r} found: {r!r}"
                else:
                    assert s in text, f"{key}: {s!r} not found: {r!r}"
        elif key == "stdout_json":
            doc = one_json_line(r)
            assert same(doc, want), f"stdout JSON {doc!r} != {want!r}"
        elif key == "stdout_json_at":
            doc = one_json_line(r)
            for path, value in want.items():
                got = json_at(doc, path)
                assert same(got, value), f"stdout JSON at {path!r} is {got!r}, not {value!r}"
        elif key == "stdout_json_keys_at":
            doc = one_json_line(r)
            for path, keys in want.items():
                got = list(json_at(doc, path).keys())
                assert got == keys, f"keys at {path!r} are {got!r}, not {keys!r}"
        elif key == "stderr_single_line_starts":
            lines = r.stderr.splitlines()
            assert len(lines) == 1 and lines[0].startswith(want), f"stderr is not one line starting {want!r}: {r!r}"
        elif key == "stderr_first_line_starts":
            lines = r.stderr.splitlines()
            assert lines and lines[0].startswith(want), f"stderr's first line does not start {want!r}: {r!r}"
        elif key == "stderr_last_line":
            lines = r.stderr.splitlines()
            assert lines and lines[-1] == want, f"stderr's last line is not {want!r}: {r!r}"
        elif key == "pack_part_titles":
            got = pack_titles(r.stdout)
            assert got == want, f"part titles {got!r} != {want!r}"
        elif key == "pack_part_lines":
            for title, lines in want.items():
                got = pack_part(r.stdout, title)
                assert got == lines, f"part {title!r} is {got!r}, not {lines!r}"
        else:
            raise KeyError(f"unknown assertion key {key!r}")
