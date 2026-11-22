"""Shared helper of the build-check characterization tests (testing.md: Harness, Setup steps).

Everything here comes from docs/prd/prd-toolkit/testing.md (the build-check paragraph of Setup steps, which puts
these cases on the tester-paths paragraph's terms, and the table Borrowed steps and helpers) and from the header of
docs/prd/prd-toolkit/test-cases/build-check.yaml, which defines CHECK, R, <h>, HEAD12 and the steps BD1 to BT9.

The borrowed steps N0 and N0X come from status_next_support and TP0 from tester_paths_support (Borrowed steps and
helpers); every other helper is defined here. A step whose command exits other than 0, or that does not find the
line it is to change, raises SetupError inside the `scratch` fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from status_next_support import N0, N0X  # testing.md, Borrowed steps and helpers
from tester_paths_support import TP0  # testing.md, Borrowed steps and helpers

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
CHECK = REPO / "prd-toolkit" / "scripts" / "prd_build_check.py"
PRD_DIR = "docs/prd/orders"

# A citation of another PRD's T-id is built from parts (testing.md, Layout), never written whole.
AT_PRD = "@" + "prd"

# testing.md, Harness (Subprocess environment) and the tester-paths paragraph of Setup steps, whose terms the
# build-check paragraph takes.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_PLUGINS_FILE",
)
ADDED_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung script ends the test
SLOW_RUN_TIMEOUT = 450  # seconds; T-197.1's run takes about 120 s and its stand-in git sleeps 300 s


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


class KnownFailure(Exception):
    """Raised by a known-failing case's test when it sees its case's `symptom:`, and only then."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


def bc_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env.update(ADDED_ENV)
    if extra:
        env.update(extra)
    return env


def argv(tmp: Path, command: str) -> list[str]:
    """A case's command text as its argument list (testing.md, the build-check paragraph of Setup steps)."""
    text = command.replace("CHECK", str(CHECK)).replace("<tmp>", str(tmp))
    words = shlex.split(text)
    if words and words[0] == "python":
        words[0] = sys.executable
    return words


def run(tmp: Path, command: str, env: dict[str, str] | None = None, timeout: int = RUN_TIMEOUT) -> Result:
    """Run one entry of a case's `runs:` with <tmp> as the working directory, with no shell."""
    proc = subprocess.run(argv(tmp, command), cwd=tmp, env=bc_env(env), capture_output=True, timeout=timeout)
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def git_out(tmp: Path, *args: str) -> str:
    """A test's own git command, in <tmp>, with the case's environment; it must exit 0."""
    proc = subprocess.run(["git", *args], cwd=tmp, env=bc_env(), capture_output=True, timeout=RUN_TIMEOUT)
    assert proc.returncode == 0, f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr!r}"
    return proc.stdout.decode("utf-8")


def R(tmp: Path) -> str:
    """R: the resolved absolute path of <tmp>/docs/prd/orders, written with `/`."""
    return os.path.realpath(tmp / PRD_DIR).replace(os.sep, "/")


def h_of(tmp: Path, path: str) -> str:
    """What `git log -1 --format=%h -- <path>` prints in <tmp>, less its newline (<h>, <h8>)."""
    out = git_out(tmp, "log", "-1", "--format=%h", "--", path)
    return out[:-1] if out.endswith("\n") else out


def head12(tmp: Path) -> str:
    return git_out(tmp, "rev-parse", "HEAD")[:12]


def porcelain(tmp: Path) -> str:
    return git_out(tmp, "status", "--porcelain")


def write_files(tmp: Path, files: dict[str, str]) -> None:
    """A case's `input.files`: each text written byte for byte as UTF-8, its folder created, none committed."""
    for key, text in files.items():
        path = Path(key.replace("<tmp>", str(tmp)))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))


# -- assertion keys (testing.md, Harness, Assertions, and the build-check paragraph of Setup steps) --

def lines_of(text: str) -> list[str]:
    return text.splitlines()


def assert_first_line_starts(text: str, start: str, what: str) -> None:
    lines = text.splitlines()
    assert lines and lines[0].startswith(start), f"{what} first line does not start with {start!r}:\n{text}"


def assert_last_line(text: str, line: str, what: str) -> None:
    lines = text.splitlines()
    assert lines and lines[-1] == line, f"{what} last line is not {line!r}:\n{text}"


def assert_single_line_starts(text: str, start: str, what: str) -> None:
    lines = text.splitlines()
    assert len(lines) == 1 and lines[0].startswith(start), f"{what} is not one line starting {start!r}:\n{text}"


# -- setup steps (the header of test-cases/build-check.yaml) --

def _git(tmp: Path, *args: str, env: dict[str, str] | None = None) -> None:
    proc = subprocess.run(["git", *args], cwd=tmp, env=bc_env(env), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode} in {tmp}: "
                         f"{proc.stderr.decode('utf-8', 'replace')}")


def _commit(tmp: Path, message: str, env: dict[str, str] | None = None) -> None:
    """`commit <m>`: git add -A, then git commit -q -m <m>."""
    _git(tmp, "add", "-A", env=env)
    _git(tmp, "commit", "-q", "-m", message, env=env)


def _write(path: Path, lines: list[str]) -> None:
    """Write a file holding the given lines and nothing else, each ending in a newline, as UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("".join(line + "\n" for line in lines).encode("utf-8"))


def _append(path: Path, line: str) -> None:
    if not path.is_file():
        raise SetupError(f"{path}: no such file to append to")
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_bytes((text + line + "\n").encode("utf-8"))


def _replace_line(path: Path, old: str, new: list[str], start: int = 0, end: int | None = None) -> None:
    """The one line equal to `old` (between lines `start` and `end`) becomes the lines `new`."""
    if not path.is_file():
        raise SetupError(f"{path}: no such file")
    lines = path.read_text(encoding="utf-8").split("\n")
    stop = len(lines) if end is None else end
    hits = [i for i in range(start, stop) if lines[i] == old]
    if len(hits) != 1:
        raise SetupError(f"expected one line {old!r} in {path}, found {len(hits)}")
    lines[hits[0]:hits[0] + 1] = new
    path.write_bytes("\n".join(lines).encode("utf-8"))


def _vendor(tmp: Path, plugin: str) -> None:
    """Run `python <plugin>/scripts/prd_hooks.py vendor docs/prd/orders` in <tmp>; it must exit 0."""
    proc = subprocess.run(
        [sys.executable, f"{plugin}/scripts/prd_hooks.py", "vendor", PRD_DIR],
        cwd=tmp, env=bc_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    if proc.returncode != 0:
        raise SetupError(f"vendor with {plugin} exited {proc.returncode}: "
                         f"{proc.stderr.decode('utf-8', 'replace')}{proc.stdout.decode('utf-8', 'replace')}")


def _copy_plugin(tmp: Path, name: str) -> None:
    """Copy <repo>/prd-toolkit to <tmp>/<name> as plain files (a symlink is followed), leaving out its two
    top-level folders tests/ and evals/ and every .venv, .uv-test-cache and __pycache__ folder."""
    src = os.fspath(REPO / "prd-toolkit")
    everywhere = {".venv", ".uv-test-cache", "__pycache__"}

    def ignore(folder: str, names: list[str]) -> set[str]:
        out = {n for n in names if n in everywhere and os.path.isdir(os.path.join(folder, n))}
        if os.path.normpath(folder) == os.path.normpath(src):
            out |= {n for n in names if n in ("tests", "evals") and os.path.isdir(os.path.join(folder, n))}
        return out

    try:
        shutil.copytree(src, tmp / name, symlinks=False, ignore=ignore)
    except (OSError, shutil.Error) as exc:
        raise SetupError(f"copying {src} to {tmp / name} failed: {exc}") from exc


def BD1(tmp: Path) -> None:
    _write(tmp / PRD_DIR / "notes.txt", ["a note"])
    _append(tmp / "src/app.py", "y = 2")
    _commit(tmp, "edit the PRD folder")


def BD2(tmp: Path) -> None:
    _append(tmp / "src/app.py", "y = 2")
    _commit(tmp, "edit the code")


def BD3(tmp: Path) -> None:
    BD1(tmp)
    _git(tmp, "tag", "-f", "base")
    _git(tmp, "mv", f"{PRD_DIR}/notes.txt", "notes.txt")
    _commit(tmp, "move the note out")


def BM1(tmp: Path) -> None:
    prd_md = tmp / PRD_DIR / "prd.md"
    if not prd_md.is_file():
        raise SetupError(f"{prd_md}: no such file")
    lines = prd_md.read_text(encoding="utf-8").split("\n")
    heads = [i for i, line in enumerate(lines) if line == "## 8. Adoption map"]
    if len(heads) != 1:
        raise SetupError(f"expected one heading '## 8. Adoption map' in {prd_md}, found {len(heads)}")
    start = heads[0] + 1
    end = next((j for j in range(start, len(lines)) if lines[j].startswith("## ") or lines[j].startswith("# ")),
               len(lines))
    _replace_line(prd_md, "Not applicable: new project.",
                  ["| Area | State | Boundary |", "|---|---|---|", "| import | adopted | `src/**` |"], start, end)


def BV1(tmp: Path) -> None:
    _write(tmp / ".prd-toolkit/extra.txt", ["x"])
    _write(tmp / PRD_DIR / "notes.txt", ["a note"])
    _commit(tmp, "edit the copy")


def BP0(tmp: Path) -> None:
    _copy_plugin(tmp, "prd-toolkit")
    _vendor(tmp, "prd-toolkit")
    _commit(tmp, "the plugin")
    _git(tmp, "tag", "-f", "base")


def BP1(tmp: Path) -> None:
    _append(tmp / ".prd-toolkit/prd_lint.py", "# a hand edit")
    _write(tmp / ".prd-toolkit/extra.txt", ["x"])
    version = tmp / ".prd-toolkit/VERSION"
    if not version.is_file():
        raise SetupError(f"{version}: no such file")
    os.chmod(version, 0o755)
    requirements = tmp / ".prd-toolkit/requirements.txt"
    if not requirements.is_file():
        raise SetupError(f"{requirements}: no such file")
    requirements.unlink()
    _commit(tmp, "edit the copy by hand")


def BP2(tmp: Path) -> None:
    _append(tmp / "prd-toolkit/scripts/prd_lint.py", "# a comment")
    _vendor(tmp, "prd-toolkit")
    _commit(tmp, "refresh the copy")


def BP3(tmp: Path) -> None:
    _append(tmp / "prd-toolkit/scripts/prd_lint.py", "# a comment")
    _write(tmp / ".prd-toolkit/extra.txt", ["x"])
    _commit(tmp, "a change without its refresh")


def BP4(tmp: Path) -> None:
    for rel in (".claude-plugin/plugin.json", "scripts/prd_hooks.py"):
        src, dst = tmp / "prd-toolkit" / rel, tmp / "other" / rel
        if not src.is_file():
            raise SetupError(f"{src}: no such file")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    _write(tmp / ".prd-toolkit/extra.txt", ["x"])
    _commit(tmp, "a second plugin")


def BF1(tmp: Path) -> None:
    _write(tmp / "tool/.claude-plugin/plugin.json", ['{"name": "prd-toolkit"}'])
    _write(tmp / "tool/scripts/prd_hooks.py",
           ["import sys", 'print("vendor broke", file=sys.stderr)', "sys.exit(1)"])
    _write(tmp / ".prd-toolkit/a.txt", ["x"])
    _commit(tmp, "a broken plugin")


def BS1(tmp: Path) -> None:
    _write(tmp / "src/app.py", ["x = 1", "y = 2", "z = 3"])
    _commit(tmp, "sources")


def BS2(tmp: Path) -> None:
    _write(tmp / "src/app.py", ["a = 1", "b = 2", "c = 3", "d = 4"])
    _commit(tmp, "four lines")
    _git(tmp, "tag", "-f", "base")
    _write(tmp / "src/app.py", ["a = 1", "b = 2", "d = 4"])
    _commit(tmp, "delete line 3")


def BS3(tmp: Path) -> None:
    _write(tmp / "src/x*.py", ["a = 1"])
    _write(tmp / "src/xy.py", ["b = 1", "b = 2", "b = 3"])
    _commit(tmp, "glob names")


UMLAUT = "plügin"  # u with diaeresis, U+00FC


def BU0(tmp: Path) -> None:
    _copy_plugin(tmp, UMLAUT)
    _vendor(tmp, UMLAUT)
    _commit(tmp, "the plugin")
    _git(tmp, "tag", "-f", "base")


def BU2(tmp: Path) -> None:
    _append(tmp / UMLAUT / "scripts/prd_lint.py", "# a comment")
    _vendor(tmp, UMLAUT)
    _commit(tmp, "refresh the copy")


_IMPORT_YAML = f"{PRD_DIR}/test-cases/import.yaml"


def BT1(tmp: Path) -> None:
    _replace_line(tmp / _IMPORT_YAML, '  input: {content: "K-1,2026-10-01"}', ['  input: {content: "K-1,2026-10-02"}'])


def BT2(tmp: Path) -> None:
    BT1(tmp)
    _commit(tmp, "change a case")


def BT3(tmp: Path) -> None:
    BT2(tmp)
    _append(tmp / "tests/test_orders.py", "# rewritten")
    _commit(tmp, "rewrite the test")


def BT4(tmp: Path) -> None:
    BT1(tmp)
    _append(tmp / "tests/test_orders.py", "# being written")


def BT5(tmp: Path) -> None:
    BT1(tmp)
    _write(tmp / "tests/test_new.py", ["# " + AT_PRD + " T-001.1"])


def BT6(tmp: Path) -> None:
    _write(tmp / "tests/test_more.py", ["# " + AT_PRD + " T-001.1"])
    day1 = "2026-01-01T12:00:00+0000"
    _commit(tmp, "another test", env={"GIT_AUTHOR_DATE": day1, "GIT_COMMITTER_DATE": day1})
    _append(tmp / "tests/test_orders.py", "# later")
    day2 = "2026-01-02T12:00:00+0000"
    _commit(tmp, "a later test", env={"GIT_AUTHOR_DATE": day2, "GIT_COMMITTER_DATE": day2})
    BT1(tmp)


def BT7(tmp: Path) -> None:
    _write(tmp / "tests/test_extra.py", ["# " + AT_PRD + " T-008.1"])
    _commit(tmp, "a test before its case")
    reports = tmp / PRD_DIR / "test-cases/reports.yaml"
    _append(reports, "T-008.1:")
    _append(reports, "  ac: AC-007.1")


def BT8(tmp: Path) -> None:
    _replace_line(tmp / _IMPORT_YAML, "T-001.1:", ["T-001.9:"])


def BT9(tmp: Path) -> None:
    BT1(tmp)
    _replace_line(tmp / _IMPORT_YAML, '  input: {rows: ["K-2"]}', ['  input: {rows: ["K-9"]}'])


# -- the one-off setup entries a case writes out in its `setup:` list (named here; a harness choice) --

def VENV(tmp: Path) -> None:
    """T-187.1: create a virtual environment with `python3 -m venv <tmp>/venv` (no packages installed)."""
    proc = subprocess.run(["python3", "-m", "venv", str(tmp / "venv")], cwd=tmp, env=bc_env(),
                          capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"python3 -m venv exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


def EMPTY(tmp: Path) -> None:
    """T-188.1: create the empty folder <tmp>/empty."""
    (tmp / "empty").mkdir()


def SLOWGIT(tmp: Path) -> None:
    """T-197.1: write <tmp>/bin/git, a git whose command with the word diff among its arguments sleeps."""
    real = shutil.which("git")
    if not real:
        raise SetupError("no git on PATH")
    _write(tmp / "bin/git", [
        "#!/bin/sh",
        'for a in "$@"; do [ "$a" = diff ] && exec sleep 300; done',
        f'exec {real} "$@"',
    ])
    os.chmod(tmp / "bin/git", 0o755)


def BADMD(tmp: Path) -> None:
    """T-198.1: write the three bytes ff fe 00 (hexadecimal) to <tmp>/bad.md."""
    (tmp / "bad.md").write_bytes(bytes([0xFF, 0xFE, 0x00]))


STEPS = {
    "N0": N0, "N0X": N0X, "TP0": TP0,
    "BD1": BD1, "BD2": BD2, "BD3": BD3, "BM1": BM1, "BV1": BV1,
    "BP0": BP0, "BP1": BP1, "BP2": BP2, "BP3": BP3, "BP4": BP4, "BF1": BF1,
    "BS1": BS1, "BS2": BS2, "BS3": BS3, "BU0": BU0, "BU2": BU2,
    "BT1": BT1, "BT2": BT2, "BT3": BT3, "BT4": BT4, "BT5": BT5, "BT6": BT6, "BT7": BT7, "BT8": BT8, "BT9": BT9,
    "VENV": VENV, "EMPTY": EMPTY, "SLOWGIT": SLOWGIT, "BADMD": BADMD,
}


@pytest.fixture
def scratch(request, tmp_path, monkeypatch) -> Path:
    """<tmp>: the scratch repository, built by the case's setup steps in the order it lists them.

    GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM are set in the test's own process before the first step, so the
    borrowed steps' `git init` inherits them (testing.md, the tester-paths and build-check paragraphs).
    """
    for name, value in ADDED_ENV.items():
        monkeypatch.setenv(name, value)
    for step in request.param:
        STEPS[step](tmp_path)
    return tmp_path


def given_steps(*steps: str):
    """Mark a test with its case's `setup:` list; the `scratch` fixture runs the steps."""
    return pytest.mark.parametrize("scratch", [steps], indirect=True, ids=["+".join(steps) or "none"])
