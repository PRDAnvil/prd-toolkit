"""Helpers for the pack-authoring black-box tests (docs/prd/prd-toolkit/test-cases/pack-authoring.yaml).

Everything here follows docs/prd/prd-toolkit/testing.md (Harness; Setup steps, the pack-authoring
paragraph and table; Borrowed steps and helpers) and the conventions at the top of
test-cases/pack-authoring.yaml. The one borrowed helper is lint_cli_support.load_vendored (fixture
repo/vendored, step KVC); every other helper is defined here.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from lint_cli_support import load_vendored

# <repo> is the repository root: prd-toolkit/tests/prd/<this file>.
REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "prd-toolkit" / "scripts"
PACK = SCRIPTS / "prd_pack.py"
CHANGE = SCRIPTS / "prd_change.py"
LINT = SCRIPTS / "prd_lint.py"
CONTEXT = SCRIPTS / "prd_context.py"
DISPATCH = SCRIPTS / "prd_dispatch.py"
HOOKS = SCRIPTS / "prd_hooks.py"
# Load paths are relative to contracts/fixtures/ (testing.md, Fixtures).
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
SITES = FIXTURES / "pack-authoring" / "sites.yaml"
TEXTS = FIXTURES / "pack-authoring" / "texts.yaml"

# Subprocess environment (Harness) minus the git variables the pack-authoring Setup steps name.
DROPPED = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
)


def vpack(tmp: Path) -> Path:
    """VPACK: <tmp>/.prd-toolkit/prd_pack.py, the vendored copy step KVC loads."""
    return tmp / ".prd-toolkit" / "prd_pack.py"


def environment() -> dict:
    """The runner's environment as it is now (PRD_PLUGINS_FILE included once K0 set it), minus DROPPED."""
    env = dict(os.environ)
    for name in DROPPED:
        env.pop(name, None)
    return env


def today() -> str:
    """The date a command writes as today (testing.md, Assertions)."""
    return datetime.date.today().isoformat()


@dataclass
class Run:
    code: int
    stdout: str
    stderr: str
    dates: tuple  # today's date just before and just after the command ran

    @property
    def lines(self) -> list:
        return self.stdout.splitlines()


def run(script: Path, *args: str, cwd: Path) -> Run:
    """Run `python <script> <args>` with the test's interpreter, in `cwd`, with environment()."""
    before = today()
    proc = subprocess.run(
        [sys.executable, str(script), *args], cwd=cwd, env=environment(), capture_output=True
    )
    after = today()
    return Run(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"), (before, after))


def git(repo: Path, *args: str) -> str:
    """A git command in `repo`, with the steps' environment; fails the test when git exits other than 0."""
    proc = subprocess.run(["git", *args], cwd=repo, env=environment(), capture_output=True, check=True)
    return proc.stdout.decode("utf-8")


def commit(repo: Path, message: str) -> None:
    """Commit as the pack-authoring Setup steps say: no hook and no signing setting take part."""
    git(repo, "add", "-A")
    git(repo, "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
        "-c", "user.name=Sample", "-c", "user.email=sample@example.com",
        "commit", "-q", "-m", message)


def status(repo: Path) -> str:
    """`git status --porcelain` in `repo`."""
    return git(repo, "status", "--porcelain")


def diff(repo: Path, *paths: str) -> str:
    """`git diff -U0 --no-color --no-ext-diff -- <paths>` in `repo`."""
    return git(repo, "diff", "-U0", "--no-color", "--no-ext-diff", "--", *paths)


# -- files --

def write(path: Path, text: str) -> None:
    """Write `text` byte for byte as UTF-8, creating parent folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def sites() -> dict:
    """Fixture pack-authoring/sites: path from tmp_path -> full text."""
    return yaml.safe_load(SITES.read_text(encoding="utf-8"))


def texts() -> dict:
    """Fixture pack-authoring/texts."""
    return yaml.safe_load(TEXTS.read_text(encoding="utf-8"))


def north(tmp: Path) -> Path:
    return tmp / "north" / "docs" / "prd" / "north"


def south(tmp: Path) -> Path:
    return tmp / "south" / "docs" / "prd" / "south"


def the_pack(tmp: Path) -> Path:
    return tmp / "plug" / "prd-packs" / "leaflet"


def _lines(path: Path) -> list:
    return read(path).splitlines(keepends=True)


def _save(path: Path, lines: list) -> None:
    write(path, "".join(lines))


def _one(lines: list, test, what: str, path: Path) -> int:
    hits = [i for i, line in enumerate(lines) if test(line.rstrip("\n"))]
    assert len(hits) == 1, f"setup: {path}: {len(hits)} lines {what}, expected exactly one"
    return hits[0]


def insert_after_line(path: Path, whole: str, new: str) -> None:
    lines = _lines(path)
    i = _one(lines, lambda s: s == whole, f"equal to {whole!r}", path)
    lines.insert(i + 1, new + "\n")
    _save(path, lines)


def insert_after_number(path: Path, number: int, whole: str, new: str) -> None:
    lines = _lines(path)
    assert lines[number - 1].rstrip("\n") == whole, f"setup: {path}:{number} is {lines[number - 1]!r}"
    lines.insert(number, new + "\n")
    _save(path, lines)


def replace_in_line(path: Path, starts: str, old: str, new: str) -> None:
    lines = _lines(path)
    i = _one(lines, lambda s: s.startswith(starts), f"starting {starts!r}", path)
    assert old in lines[i], f"setup: {path}: {old!r} not in {lines[i]!r}"
    lines[i] = lines[i].replace(old, new, 1)
    _save(path, lines)


def replace_line(path: Path, starts: str, new: str) -> None:
    lines = _lines(path)
    i = _one(lines, lambda s: s.startswith(starts), f"starting {starts!r}", path)
    lines[i] = new + "\n"
    _save(path, lines)


def delete_line(path: Path, starts: str) -> None:
    lines = _lines(path)
    i = _one(lines, lambda s: s.startswith(starts), f"starting {starts!r}", path)
    del lines[i]
    _save(path, lines)


# -- Setup steps (testing.md, the pack-authoring table) --

def K0(tmp: Path, monkeypatch) -> None:
    for key, text in sites().items():
        write(tmp / key, text)
    for repo in (tmp / "north", tmp / "south"):
        git(repo, "init", "-q")
        commit(repo, "base")
    plugins = tmp / "plugins.json"
    write(plugins, '{"plugins": {"leaflet-kit@example": [{"installPath": "' + str(tmp) + '/plug"}]}}\n')
    monkeypatch.setenv("PRD_PLUGINS_FILE", str(plugins))


def KC(tmp: Path) -> None:
    commit(tmp / "north", "edit")


def KS(tmp: Path) -> None:
    insert_after_line(south(tmp) / "prd.md", "| a change to a page | code-review | recommended |",
                      "| a new page | security-review | recommended |")


def KV(tmp: Path) -> None:
    replace_in_line(south(tmp) / "prd.md", "| pages |", "chr(58)", "chr(61)")


def KG(tmp: Path) -> None:
    replace_in_line(south(tmp) / "prd.md", "| routes |", "`contracts/routes.yaml`", "`contracts/routes/*.yaml`")


def KL(tmp: Path) -> None:
    replace_in_line(south(tmp) / "prd.md", "| `site/**/*.html` |",
                    "`python3 tools/check_html.py`", "python3 tools/check_html.py")


def KN(tmp: Path) -> None:
    delete_line(south(tmp) / "prd.md", "| pages |")
    delete_line(south(tmp) / "prd.md", "| routes |")


def KZ(tmp: Path) -> None:
    KN(tmp)
    delete_line(south(tmp) / "prd.md", "| feeds |")


def KP1(tmp: Path) -> None:
    (the_pack(tmp) / "samples" / "routes" / "bad.yaml").unlink()


def KP2(tmp: Path) -> None:
    write(the_pack(tmp) / "samples" / "pages" / "bad.yaml", "home:\n  title: Home\n")


def KP3(tmp: Path) -> None:
    path = the_pack(tmp) / "pack.yaml"
    text = read(path)
    old = '"python3 -m pytest tests/unit"'
    assert text.count(old) == 1, f"setup: {path}: {text.count(old)} of {old!r}"
    write(path, text.replace(old, '"no-such-runner tests/unit"'))


def KP8(tmp: Path) -> None:
    """Step KP8: the pages validator first reads `prd.md` by a relative path (the bytes spell `prd.md`)."""
    path = the_pack(tmp) / "pack.yaml"
    text = read(path)
    old = "import sys; sys.exit(any(not open(f)"
    assert text.count(old) == 1, f"setup: {path}: {text.count(old)} of {old!r}"
    write(path, text.replace(old, "import sys, os; os.stat(bytes((112, 114, 100, 46, 109, 100))); "
                                  "sys.exit(any(not open(f)"))


def KP4(tmp: Path) -> None:
    path = the_pack(tmp) / "pack.yaml"
    write(path, read(path) + "colour: green\n")


def KP5(tmp: Path) -> None:
    write(north(tmp) / "contracts" / "routes.yaml", "old-home: /\n")


def KP6(tmp: Path) -> None:
    (south(tmp) / "contracts" / "pages.yaml").unlink()


FIXTURES_LINE = "- Not applicable: `contracts/fixtures/` — no fixture data"


def KR1(tmp: Path) -> None:
    insert_after_number(north(tmp) / "prd.md", 21, FIXTURES_LINE, "- Pack: document 1.0.0 (prd-toolkit)")


def KB(tmp: Path) -> None:
    path = north(tmp) / "prd.md"
    lines = _lines(path)
    assert lines[10].rstrip("\n") == "## 1. Metadata & stack", f"setup: {path}:11 is {lines[10]!r}"
    assert all(line.startswith("- ") for line in lines[12:21]), f"setup: {path}: lines 13 to 21 are not bullets"
    del lines[12:21]
    _save(path, lines)
    KC(tmp)


def KA(tmp: Path) -> None:
    insert_after_number(north(tmp) / "prd.md", 39, "The site is a folder of static files.",
                        "[ASSUMPTION A-99: a guess]")
    KC(tmp)


def KT1(tmp: Path) -> None:
    replace_line(north(tmp) / "prd.md", "| routes |", "| routes | `contracts/routes.yaml` | built-in |")


def KT2(tmp: Path) -> None:
    replace_in_line(north(tmp) / "prd.md", "| routes |", "`contracts/routes.yaml`", "`contracts/routes*.yaml`")


def KD(tmp: Path) -> None:
    path = north(tmp) / "errors.md"
    write(path, read(path) + "A note.\n")


def KH(tmp: Path) -> None:
    write(north(tmp) / "prd.md", texts()["north_lifted"])
    KC(tmp)


def KP7(tmp: Path) -> None:
    shutil.copytree(tmp / "plug", tmp / "plug2")
    write(tmp / "plugins.json",
          '{"plugins": {"leaflet-kit@example": [{"installPath": "' + str(tmp) + '/plug"}], '
          '"leaflet-copy@example": [{"installPath": "' + str(tmp) + '/plug2"}]}}\n')


def KE(tmp: Path) -> None:
    """Step KE: the pack declares no contract type (`contract-types: []`, its two rows deleted)."""
    path = the_pack(tmp) / "pack.yaml"
    lines = _lines(path)
    i = _one(lines, lambda s: s == "contract-types:", "equal to 'contract-types:'", path)
    assert lines[i + 1].startswith("  - {type: pages,"), f"setup: {path}: {lines[i + 1]!r}"
    assert lines[i + 2].startswith("  - {type: routes,"), f"setup: {path}: {lines[i + 2]!r}"
    lines[i:i + 3] = ["contract-types: []\n"]
    _save(path, lines)


def KX(tmp: Path) -> None:
    """Step KX: the pack holds one vocabulary word, `visitor`."""
    path = the_pack(tmp) / "pack.yaml"
    lines = _lines(path)
    i = _one(lines, lambda s: s == "vocabulary: []", "equal to 'vocabulary: []'", path)
    lines[i] = "vocabulary: [visitor]\n"
    _save(path, lines)


def KI(tmp: Path) -> None:
    """Step KI: the identity, and no signing, of a commit a run of the case makes in <tmp>/north."""
    repo = tmp / "north"
    git(repo, "config", "user.name", "Sample")
    git(repo, "config", "user.email", "sample@example.com")
    git(repo, "config", "commit.gpgsign", "false")


def KW(tmp: Path) -> None:
    """Step KW: write north's review verdict from `prd_change.py digest`, then switch the hooks off in <tmp>/north."""
    repo = tmp / "north"
    r = run(CHANGE, "digest", "docs/prd/north", cwd=repo)
    assert r.code == 0 and len(r.lines) == 1, f"setup KW: digest exited {r.code}: {r.stdout!r} {r.stderr!r}"
    digest = r.lines[0]
    write(north(tmp) / ".prd-review.json",
          '{"digest": "' + digest + '", "touches": [], "dry_run": {"record": "no dry run (pack lifted)"}, '
          '"ready": true}\n')
    git(repo, "config", "core.hooksPath", "/dev/null")


@pytest.fixture(name="kvc")
def kvc_fixture(tmp_path) -> Path:
    """Step KVC: fixture repo/vendored loaded into <tmp>/.prd-toolkit with its check.

    It runs in pytest's setup phase, so a mismatch ends the test as an error, not a failure
    (testing.md, Fixtures). Returns <tmp>/.prd-toolkit.
    """
    return load_vendored(tmp_path)


# -- Assertions (testing.md, Harness, Assertions) --

def part_titles(stdout: str) -> list:
    """pack_part_titles: the stdout lines that start with `## `, in order."""
    return [line for line in stdout.splitlines() if line.startswith("## ")]


def part_lines(stdout: str, title: str) -> list:
    """pack_part_lines: from `## <title>` (exactly once) up to, not including, the next `## ` line or the end."""
    lines = stdout.splitlines()
    head = "## " + title
    assert lines.count(head) == 1, f"stdout holds {lines.count(head)} lines {head!r}, expected one:\n{stdout}"
    start = lines.index(head)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return lines[start:end]


def one_json(stdout: str) -> dict:
    """The whole stdout as one line ending in a newline, parsed as one JSON object."""
    assert stdout.endswith("\n") and stdout.count("\n") == 1, f"stdout is not one line: {stdout!r}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object: {stdout!r}"
    return doc


def at(doc, path: str):
    """The value at a path of object keys and list indexes joined by `.` (`""` is the document)."""
    cur = doc
    if path == "":
        return cur
    for seg in path.split("."):
        cur = cur[int(seg)] if isinstance(cur, list) else cur[seg]
    return cur


def assert_json_at(stdout: str, mapping: dict) -> None:
    doc = one_json(stdout)
    for path, value in mapping.items():
        assert at(doc, path) == value, f"{path}: {at(doc, path)!r} != {value!r}"


def assert_json_keys_at(stdout: str, mapping: dict) -> None:
    doc = one_json(stdout)
    for path, keys in mapping.items():
        assert list(at(doc, path).keys()) == keys, f"keys at {path!r}: {list(at(doc, path).keys())} != {keys}"


def untoday(actual: list, expected: list, dates) -> list:
    """`actual`, with each line that equals its expected line's `<today>` written as one of `dates` put back as
    the expected line, so `untoday(actual, expected, dates) == expected` accepts either date."""
    out = []
    for i, line in enumerate(actual):
        want = expected[i] if i < len(expected) else None
        if want is not None and "<today>" in want and line in {want.replace("<today>", d) for d in dates}:
            out.append(want)
        else:
            out.append(line)
    return out


def hunk_lines(diff_text: str) -> tuple:
    """The removed and the added lines of a diff's hunks, without their leading `-` or `+`, and the files it
    changes (from its `diff --git a/<path> b/<path>` lines); the `---` and `+++` file headers are not hunk lines."""
    removed, added, files = [], [], []
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            files.append(line)
            in_hunk = False
        elif line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line.startswith("-"):
            removed.append(line[1:])
        elif in_hunk and line.startswith("+"):
            added.append(line[1:])
    return removed, added, files
