"""Shared helper of the status characterization tests (testing.md: Harness, Setup steps, the status paragraph).

Everything here comes from docs/prd/prd-toolkit/testing.md and the header of test-cases/status.yaml: the steps
SB0 to SS9, the names STATUS, BLOCK, VBLOCK, RTMP, CLAUDE_BASE, README_BASE, PARENT_V, PARENT_P and H, the way a
run's text becomes its argument list, and the assertion keys the status cases use.

The status-next steps (N0, N0X, NA1, NE1, NE2, NB2, NLV, NR1 to NR4, NT1) and load_vendored are borrowed from
their own support files, with the calls the table Borrowed steps and helpers gives. A step that cannot be applied
raises SetupError inside the `repo` fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

import status_next_support as sn
from lint_cli_support import load_vendored

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
STATUS = SCRIPTS_DIR / "prd_status.py"
BLOCK = SCRIPTS_DIR / "prd_block.py"
MANIFEST = REPO / "prd-toolkit" / ".claude-plugin" / "plugin.json"
CASES_FILE = REPO / "docs" / "prd" / "prd-toolkit" / "test-cases" / "status.yaml"
ORDERS_REL = Path("docs") / "prd" / "orders"

# testing.md, Subprocess environment and Setup steps: the variables a run never inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
)
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test

SUMMARY = "The orders service imports order files and prints monthly reports."


class SetupError(Exception):
    """A step could not be applied: the test ends as an error, not a failure."""


class KnownFailure(Exception):
    """The symptom a known-failing case names was seen: the strict xfail marker accepts only this."""


# -- the texts the header names (CLAUDE_BASE, README_BASE, PARENT_V are the texts T-235.1, T-241.1, T-242.1 give) --

def _case_text(tid: str) -> str:
    cases = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
    return cases[tid]["expect"]["effects"][0]["text"]


CLAUDE_BASE = _case_text("T-235.1")
README_BASE = _case_text("T-241.1")
PARENT_V = _case_text("T-242.1")


@pytest.fixture
def H() -> str:
    """The manifest's homepage, stripped; the case's precondition, so a manifest that differs is an error."""
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SetupError(f"{MANIFEST}: cannot be read: {exc}")
    homepage = manifest.get("homepage")
    if manifest.get("name") != "prd-toolkit" or not isinstance(homepage, str) or not homepage.strip():
        raise SetupError(f"{MANIFEST}: not named prd-toolkit with a non-empty homepage")
    return homepage.strip()


def parent_p(h: str) -> str:
    return PARENT_V.replace("https://example.com/toolkit", h)


# -- runs --

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


def subprocess_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(extra or {})
    return env


def orders(tmp: Path) -> Path:
    return tmp / ORDERS_REL


def rtmp(tmp: Path) -> str:
    return str(tmp.resolve())


_NAMES = re.compile(r"\bVBLOCK\b|\bBLOCK\b|\bSTATUS\b|<tmp>")


def argv(tmp: Path, text: str) -> list[str]:
    values = {"STATUS": str(STATUS), "BLOCK": str(BLOCK),
              "VBLOCK": str(tmp / ".prd-toolkit" / "prd_block.py"), "<tmp>": str(tmp)}
    words = shlex.split(_NAMES.sub(lambda m: values[m.group(0)], text))
    if words and words[0] == "python":
        words[0] = sys.executable
    return words


def run(tmp: Path, text: str, cwd: Path, env: dict[str, str] | None = None) -> Result:
    """Run a case's command text in `cwd`; stdout and stderr captured as bytes."""
    proc = subprocess.run(argv(tmp, text), cwd=cwd, env=subprocess_env(env), capture_output=True,
                          timeout=RUN_TIMEOUT)
    return Result(proc.returncode, proc.stdout, proc.stderr)


def status(tmp: Path, text: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> Result:
    """A cli:prd_status run: ORDERS is the working directory unless the case says otherwise."""
    return run(tmp, text, orders(tmp) if cwd is None else cwd, env)


def block(tmp: Path, text: str, cwd: Path | None = None) -> Result:
    """A cli:prd_block run: <tmp> is the working directory unless the case says otherwise."""
    return run(tmp, text, tmp if cwd is None else cwd)


def write_files(files: dict[Path, str]) -> None:
    """A case's input.files, written after every setup step, byte for byte as UTF-8."""
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))


# -- assertion keys --

def part_titles(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if line.startswith("## ")]


def part_lines(stdout: str, title: str) -> list[str]:
    lines = stdout.splitlines()
    head = "## " + title
    assert lines.count(head) == 1, f"stdout holds the line {head!r} {lines.count(head)} times:\n{stdout}"
    i = lines.index(head)
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
    return lines[i:j]


def one_json_line(stdout: str) -> dict:
    assert stdout.endswith("\n") and len(stdout.splitlines()) == 1, f"stdout is not one line:\n{stdout}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{stdout}"
    return doc


def status_items(stdout: str) -> list[dict]:
    """The entries of `items` whose part is not Next, in order."""
    return [item for item in one_json_line(stdout)["items"] if item.get("part") != "Next"]


def assert_lines_in_order(actual: list[str], wanted: list[str]) -> None:
    pos = 0
    for line in wanted:
        try:
            pos = actual.index(line, pos) + 1
        except ValueError:
            raise AssertionError(f"line {line!r} not found after position {pos} in:\n" + "\n".join(actual))


def file_lines(path: Path) -> list[str]:
    return path.read_bytes().decode("utf-8").splitlines()


def absent(path: Path) -> bool:
    return not os.path.lexists(path)


def snapshot(*paths: Path) -> dict[Path, bytes | None]:
    return {p: (p.read_bytes() if p.exists() else None) for p in paths}


def as_json(value):
    return json.loads(json.dumps(value, default=str))


# -- the in-process call (testing.md, In-process calls and the status paragraph) --

@pytest.fixture
def facts(monkeypatch):
    """F = prdlint.overview.facts(prdlint.model.load(ORDERS)), with prd-toolkit/scripts on sys.path."""
    for name in _DROPPED_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.syspath_prepend(str(SCRIPTS_DIR))

    def get(tmp: Path):
        model = importlib.import_module("prdlint.model")
        overview = importlib.import_module("prdlint.overview")
        return overview.facts(model.load(orders(tmp)))

    return get


# -- the file's own steps (header of test-cases/status.yaml) --

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _write_lines(path: Path, lines: list[str]) -> None:
    _write(path, "".join(line + "\n" for line in lines))


def _split(path: Path) -> list[str]:
    if not path.is_file():
        raise SetupError(f"{path}: no such file")
    return path.read_bytes().decode("utf-8").split("\n")


def _join(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def _index(lines: list[str], old: str, path: Path, start: int = 0, end: int | None = None) -> int:
    end = len(lines) if end is None else end
    hits = [i for i in range(start, end) if lines[i] == old]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {old!r}, found {len(hits)}")
    return hits[0]


def _replace(path: Path, old: str, new: list[str]) -> None:
    lines = _split(path)
    i = _index(lines, old, path)
    lines[i:i + 1] = new
    _join(path, lines)


def _insert_after(path: Path, anchor: str, new: list[str]) -> None:
    lines = _split(path)
    i = _index(lines, anchor, path)
    lines[i + 1:i + 1] = new
    _join(path, lines)


def _insert_after_line_1(path: Path, line_1: str, new: list[str]) -> None:
    lines = _split(path)
    if lines[0] != line_1:
        raise SetupError(f"{path}: line 1 is {lines[0]!r}, not {line_1!r}")
    lines[1:1] = new
    _join(path, lines)


def _append(path: Path, new: list[str]) -> None:
    text = path.read_bytes().decode("utf-8") if path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    _write(path, text + "".join(line + "\n" for line in new))


def SB0(tmp: Path) -> None:
    r = run(tmp, "python BLOCK docs/prd/orders", tmp)
    if r.exit != 0:
        raise SetupError(f"SB0: prd_block.py exited {r.exit}: {r.stderr}")


def SVER(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", "version: 1.0.0", ["version: 1.1.0"])


def SH0(tmp: Path) -> None:
    path = orders(tmp) / "prd.md"
    lines = _split(path)
    if lines[0] != "---" or "---" not in lines[1:]:
        raise SetupError(f"{path}: no frontmatter")
    del lines[_index(lines, "status: Approved", path, 1, lines.index("---", 1))]
    _join(path, lines)


def SU8(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", "Not applicable: new project.",
             ["| Area | State | Boundary |", "|---|---|---|", "| import | adopted | `src/**` |"])


def S8(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", "Not applicable: new project.", ["See adoption.md."])


def _skills(tmp: Path, code_object: str) -> None:
    _replace(orders(tmp) / "prd.md", "Not applicable: the fixture requires no skill.",
             ["| Object or activity | Skill | Decision |", "|---|---|---|",
              f"| {code_object} | `superpowers:test-driven-development` | required |",
              "| a review | code-review | recommended |"])


def SR6(tmp: Path) -> None:
    _skills(tmp, "a code change")


def SR8(tmp: Path) -> None:
    _skills(tmp, "a change to {{adopted_areas}}")


def SP1(tmp: Path) -> None:
    _insert_after(orders(tmp) / "prd.md", "- Language: Python 3.12", ["- Pack: document 1.0.0 (prd-toolkit)"])


def SS1(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY,
             ["<!-- a note -->", "The orders service imports order files. It prints" + " " * 3, "monthly reports."])


def SS2(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY, [])


def SS3(tmp: Path) -> None:
    _insert_after(orders(tmp) / "prd.md", "- Import a 10,000-row file in under 60 seconds.",
                  ["", "Principles: Keep it small.", "", "- **Plain.** One command, one answer.", "",
                   "Getting started:", "", "1. Install the service.", "2. Import a file."])


def SS4(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY, [SUMMARY + " <!-- prd-toolkit:end -->"])


def SS5(tmp: Path) -> None:
    _insert_after(orders(tmp) / "prd.md", SUMMARY, ["<!-- prd-toolkit:start -->"])


def SS6(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY, ["Does it import files? Yes, v1.2 does."])


def SS7(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY, ["See {{areas}} for the areas."])


def SS8(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY, ["Prints {{homepage}} as text."])


def SS9(tmp: Path) -> None:
    _replace(orders(tmp) / "prd.md", SUMMARY, ["Intro <!-- note --> text"])


def SN1(tmp: Path) -> None:
    _insert_after_line_1(orders(tmp) / "nfr.md", "# Non-functional requirements",
                         ["", "### NFR-008 Import speed", "Status: verified"])


def SZ(tmp: Path) -> None:
    for rel in ("features/import.md", "features/reports.md"):
        path = orders(tmp) / rel
        if not path.is_file():
            raise SetupError(f"{path}: no such file")
        path.unlink()


def SA1(tmp: Path) -> None:
    _insert_after_line_1(orders(tmp) / "features/reports.md", "# Reports", ["Target: output language pt-BR"])


def SA2(tmp: Path) -> None:
    path = orders(tmp) / "adoption.md"
    _replace(path, "| import | adopted | `src/import/**` |",
             ["| import | adopted | `src/import/**`, `tests/test_import.py` |"])
    _replace(path, "| audit | not started | `src/audit/**` |", ["| audit | not started |  |"])


def SA3(tmp: Path) -> None:
    path = orders(tmp) / "adoption.md"
    lines = _split(path)
    rows = lines[4:9]
    if len(rows) != 5 or not all(r.startswith("| ") for r in rows):
        raise SetupError(f"{path}: lines 5 to 9 are not five table rows: {rows}")
    del lines[4:9]
    _join(path, lines)


def SM1(tmp: Path) -> None:
    _replace(orders(tmp) / "features/import.md", "Tests: T-001.1 [integration]  (test-cases/import.yaml)",
             ["Tests: T-001.1 [system]  (test-cases/import.yaml)"])


def SU1(tmp: Path) -> None:
    _append(orders(tmp) / "features/import.md",
            ["", "### UJ-01 An operator imports a file", "Status: verified", "Flow: 1. run the importer"])


def SR7(tmp: Path) -> None:
    path = orders(tmp) / "features/reports.md"
    lines = _split(path)
    head = _index(lines, "### FR-007 Refuse an unknown month", path)
    end = next((k for k in range(head + 1, len(lines)) if lines[k].startswith("### ")), len(lines))
    i = _index(lines, "Status: live (since 1.0.0)", path, head + 1, end)
    lines[i] = "Status: removed"
    _join(path, lines)


def SAB(tmp: Path) -> None:
    _replace(orders(tmp) / "features/import.md", "Status: live (since 1.0.0)", ["Status: as-built"])


def SE1(tmp: Path) -> None:
    _write_lines(orders(tmp) / "errors.md", [
        "# Error ledger", "", "### E-001 The importer stops at row 1000",
        "Detected: 2026-11-03, a run on the October file", "Classification: code bug", "Touches: FR-003",
        "Resolution: not a defect: the file was cut short", "Recurrence of: -"])


def _links(tmp: Path, upstream_row: str, consumer_rows: list[str]) -> None:
    _write_lines(orders(tmp) / "links.md", [
        "# Links", "", "## Upstreams", "", "| Upstream | Location | Version | Commit | Needs |", "|---|---|---|---|---|",
        upstream_row, "", "## Consumers", "", "| Consumer | Location |", "|---|---|", *consumer_rows])


def SK1(tmp: Path) -> None:
    _links(tmp, "| greet | `https://example.com/greet.git#docs/prd/greet` | 1.1.0 | 4f1c9a2 |  |",
           ["| dashboards | `git@example.com:org/bi.git#docs/prd/dashboards` |"])


def _no_billing_beside(tmp: Path) -> None:
    if os.path.lexists(tmp / ".." / "billing"):
        raise SetupError(f"{tmp / '..' / 'billing'} exists")


def SK2(tmp: Path) -> None:
    _no_billing_beside(tmp)
    _links(tmp, "| billing | `../billing` | 1.0.0 | abc1234 | verified |", [])


def SK3(tmp: Path) -> None:
    _no_billing_beside(tmp)
    _links(tmp, "| orders | `../billing` | 1.0.0 | abc1234 |  |", [])


_CS_HEAD = ["| Order | PRD | Location | Branch | Version | IDs | Waits for | Target | State |",
            "|---|---|---|---|---|---|---|---|---|"]


def SC1(tmp: Path) -> None:
    _write_lines(orders(tmp) / "changes/CS-001.md", [
        "# CS-001 Add a flag", "", "Started: 2026-11-02 in orders", "Status: running", "", *_CS_HEAD,
        "| 1 | billing | `../billing` | cs-001-add-a-flag | 1.0.0 → 1.1.0 | — | — | verified | approved |",
        "| 2 | orders | `.` | cs-001-add-a-flag | 1.0.0 | — | billing verified | verified | proposed |",
        "", "## Log", "", "- 2026-11-02 started"])
    _write_lines(orders(tmp) / "changes/CS-002.md", [
        "# CS-002 Old", "", "Started: 2026-10-01 in orders", "Status: done", "", *_CS_HEAD,
        "| 1 | orders | `.` | cs-002-old | 1.0.0 | — | — | verified | verified |",
        "", "## Log", "", "- 2026-10-01 done"])


def SD0(tmp: Path) -> None:
    _append(orders(tmp) / "operations.md",
            ["", "## Deployed", "", "| Environment | PRD version | Commit | Date | Run |", "|---|---|---|---|---|"])


def _deployed_row(tmp: Path, row: str) -> None:
    path = orders(tmp) / "operations.md"
    if "## Deployed" not in _split(path):
        raise SetupError("a Deployed row step runs after SD0")
    _append(path, [row])


def SD1(tmp: Path) -> None:
    _deployed_row(tmp, "| production | 1.0.0 | 3f2c1a9 | 2026-11-02 | 20261102T103000Z-production |")


def SD2(tmp: Path) -> None:
    _deployed_row(tmp, "| staging | 1.0.0 | 3f2c1a9 | 2026-11-12 | 20261112T000000Z-all |")


def SD3(tmp: Path) -> None:
    _deployed_row(tmp, "| qa | 1.0.0 | abc1234 | 2026-11-03 | 20261103T000000Z-qa |")


def _deploys(tmp: Path) -> Path:
    return tmp / ".git" / "prd-toolkit" / "deploys"


def SG1(tmp: Path) -> None:
    _write_lines(_deploys(tmp) / "20261112T100000Z-all.jsonl", [
        '{"kind": "header", "run": "20261112T100000Z-all", "prd": "docs/prd/orders", "version": "1.0.0"}',
        '{"kind": "step", "step": 1, "env": "staging", "actor": "agent", "result": "pass"}'])


def SG2(tmp: Path) -> None:
    _write_lines(_deploys(tmp) / "20261113T090000Z-all.jsonl", [
        '{"kind": "header", "run": "20261113T090000Z-all", "prd": "docs/prd/other", "version": "1.0.0"}',
        '{"kind": "step", "step": 1, "env": "staging", "actor": "agent", "result": "fail"}'])


def SG3(tmp: Path) -> None:
    _write_lines(tmp / ".gitignore", ["CLAUDE.md"])


def SV0(tmp: Path) -> None:
    load_vendored(tmp)
    _write_lines(tmp / ".prd-toolkit" / "HOMEPAGE", ["https://example.com/toolkit"])


def SV1(tmp: Path) -> None:
    home = tmp / ".prd-toolkit" / "HOMEPAGE"
    if not home.is_file():
        raise SetupError("SV1 runs after SV0")
    home.write_bytes(b"\n")
    _write_lines(tmp / ".claude-plugin" / "plugin.json",
                 ['{"name": "prd-toolkit", "homepage": "https://example.com/host"}'])


def SV2(tmp: Path) -> None:
    home = tmp / ".prd-toolkit" / "HOMEPAGE"
    if not home.is_file():
        raise SetupError("SV2 runs after SV0")
    home.unlink()


def SB2(tmp: Path) -> None:
    billing = tmp / "docs" / "prd" / "billing"
    shutil.copytree(orders(tmp), billing, symlinks=True)
    _replace(billing / "prd.md", "version: 1.0.0", ["version: 0.2.0"])
    _replace(billing / "prd.md", SUMMARY, ["Billing sends invoices | credits. It runs nightly."])


def SB3(tmp: Path) -> None:
    path = tmp / "docs" / "prd" / "broken" / "prd.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes([0xFF, 0xFE, 0x80, 0x0A]))


def SB4(tmp: Path) -> None:
    shutil.copytree(orders(tmp), tmp / "docs" / "prd" / "my notes", symlinks=True)


def SB5(tmp: Path) -> None:
    _write_lines(tmp / "docs" / "prd" / "notes" / "a.md", ["x"])
    hidden = tmp / "docs" / "prd" / ".hidden" / "prd.md"
    hidden.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(orders(tmp) / "prd.md", hidden)


def SQ(tmp: Path) -> None:
    target = tmp / "docs" / "requirements" / "orders"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(orders(tmp)), str(target))


def SY(tmp: Path) -> None:
    _write_lines(tmp / "real.md", ["# Agents"])
    os.symlink("real.md", tmp / "CLAUDE.md")


def SMODE(tmp: Path) -> None:
    path = orders(tmp) / "README.md"
    _write_lines(path, ["# Mine"])
    os.chmod(path, 0o640)


def SF1(tmp: Path) -> None:
    _write_lines(tmp / "CLAUDE.md", ["# Docs", "", "```", "<!-- prd-toolkit:start -->", "example",
                                     "<!-- prd-toolkit:end -->", "```"])


def SF2(tmp: Path) -> None:
    _write_lines(tmp / "CLAUDE.md", ["# D", "", "```", "unclosed example"])


def SX1(tmp: Path) -> None:
    _write_lines(orders(tmp) / "README.md",
                 ["<!-- prd-toolkit:start -->", "<!-- prd-toolkit:start -->", "<!-- prd-toolkit:end -->"])


def SX2(tmp: Path) -> None:
    _write_lines(tmp / "CLAUDE.md", ["# Mine", "<!-- prd-toolkit:start -->", "half"])


def SX3(tmp: Path) -> None:
    _write_lines(tmp / "CLAUDE.md", ["<!-- prd-toolkit:end -->", "<!-- prd-toolkit:start -->"])


STEPS = {
    # borrowed: status-next steps (testing.md, Borrowed steps and helpers)
    "N0": sn.N0, "N0X": sn.N0X, "NA1": sn.NA1, "NE1": sn.NE1, "NE2": sn.NE2, "NB2": sn.NB2, "NLV": sn.NLV,
    "NR1": sn.NR1, "NR2": sn.NR2, "NR3": sn.NR3, "NR4": sn.NR4, "NT1": sn.NT1,
    # this file's own
    "SB0": SB0, "SVER": SVER, "SH0": SH0, "SU8": SU8, "S8": S8, "SR6": SR6, "SR8": SR8, "SP1": SP1,
    "SS1": SS1, "SS2": SS2, "SS3": SS3, "SS4": SS4, "SS5": SS5, "SS6": SS6, "SS7": SS7, "SS8": SS8, "SS9": SS9,
    "SN1": SN1, "SZ": SZ, "SA1": SA1, "SA2": SA2, "SA3": SA3, "SM1": SM1, "SU1": SU1, "SR7": SR7, "SAB": SAB,
    "SE1": SE1, "SK1": SK1, "SK2": SK2, "SK3": SK3, "SC1": SC1, "SD0": SD0, "SD1": SD1, "SD2": SD2, "SD3": SD3,
    "SG1": SG1, "SG2": SG2, "SG3": SG3, "SV0": SV0, "SV1": SV1, "SV2": SV2, "SB2": SB2, "SB3": SB3, "SB4": SB4,
    "SB5": SB5, "SQ": SQ, "SY": SY, "SMODE": SMODE, "SF1": SF1, "SF2": SF2, "SX1": SX1, "SX2": SX2, "SX3": SX3,
}


@pytest.fixture
def repo(request, tmp_path) -> Path:
    """<tmp>: the scratch repository, built by the case's setup steps in the order it lists them."""
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def steps(*names: str):
    """Mark a test with its case's `setup:` list; the `repo` fixture runs the steps."""
    return pytest.mark.parametrize("repo", [names], indirect=True, ids=["+".join(names)])
