"""Shared helper of the standards-run characterization tests (docs/prd/prd-toolkit/test-cases/standards-run.yaml).

Everything here comes from docs/prd/prd-toolkit/testing.md (Harness, Fixtures, Setup steps, Borrowed steps and
helpers) and the conventions at the top of test-cases/standards-run.yaml:

- the standards-run Setup steps (SR0, SG1 to SG5, SO, SM1 to SM5, SC1), defined here, a relative path in them
  taken from <tmp>;
- the borrowed step N0E, imported from status_next_support.py, and the fixture repo/vendored, loaded with
  lint_cli_support.load_vendored, the calls the table Borrowed steps and helpers gives;
- the Subprocess environment of a standards-run run, which drops PRD_PLUGINS_FILE and the git variables as well;
- the scripts the cases run (HOOK, HOOKS) and the `sh -c JOB` run of T-068.5;
- the fixture standards-run/texts, and reading a value of a YAML document at a `.`-joined path.

A setup step that cannot be applied (a line it edits that is not there, a git command that fails, the vendored
fixture's check) raises inside the `scratch` fixture, so the test ends as an error, not a failure.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

# Borrowed (testing.md, Borrowed steps and helpers): status_next_support.N0E(tmp: Path) -> None and
# lint_cli_support.load_vendored(tmp: Path) -> Path, which raises VendoredFixtureMismatch on a failed check.
from lint_cli_support import load_vendored
from status_next_support import N0E

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
SCRIPTS = {
    "HOOK": SCRIPTS_DIR / "prd_git_hook.py",  # the script the installed pre-commit hook runs
    "HOOKS": SCRIPTS_DIR / "prd_hooks.py",
}
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_REL = Path("docs") / "prd" / "orders"
GITHUB_YML = Path(".github") / "workflows" / "prd-toolkit.yml"
GITLAB_YML = Path(".gitlab") / "prd-toolkit.yml"

# testing.md: the Subprocess environment's dropped variables, the git variables the Setup steps drop, and
# PRD_PLUGINS_FILE, which every run of a standards-run case and every command of its steps removes as well.
DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
    "PRD_PLUGINS_FILE",
)
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung command ends the test


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


def subprocess_env() -> dict[str, str]:
    """The test process's environment when the command starts, minus DROPPED_ENV."""
    env = dict(os.environ)
    for name in DROPPED_ENV:
        env.pop(name, None)
    return env


def _result(proc: subprocess.CompletedProcess) -> Result:
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def run(cwd: Path, script: str, *args: str) -> Result:
    """Run `python <SCRIPT> <args>` (HOOK or HOOKS) in `cwd`; stdout and stderr decoded as UTF-8."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS[script]), *args],
        cwd=cwd, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT,
    )
    return _result(proc)


def run_sh(cwd: Path, command: str, env: dict[str, str] | None = None) -> Result:
    """Run `sh -c <command>` in `cwd`, the command passed to sh as one argument (T-068.5's `sh -c JOB`);
    `env` is a run's own `env` (a run written as a mapping), added for that run only."""
    run_env = subprocess_env()
    if env:
        run_env.update(env)
    proc = subprocess.run(
        ["sh", "-c", command], cwd=cwd, env=run_env, capture_output=True, timeout=RUN_TIMEOUT,
    )
    return _result(proc)


def orders(tmp: Path) -> Path:
    """The PRD folder the setup steps write, <tmp>/docs/prd/orders."""
    return tmp / ORDERS_REL


# -- fixtures (testing.md, Fixtures) --

def texts(key: str):
    """`texts.<key>`: the text at that key of fixture standards-run/texts, read with yaml.safe_load."""
    data = yaml.safe_load((FIXTURES / "standards-run" / "texts.yaml").read_text(encoding="utf-8"))
    return data[key]


def lint_log_lines(tmp: Path) -> list[str]:
    """The text of <tmp>/lint.log split by str.splitlines() (testing.md, the standards-run steps' paragraph)."""
    return (tmp / "lint.log").read_text(encoding="utf-8").splitlines()


def yaml_at(path: Path, dotted: str):
    """The value at a `.`-joined path of mapping keys and list indexes of the file read with yaml.safe_load."""
    node = yaml.safe_load(path.read_text(encoding="utf-8"))
    for part in dotted.split("."):
        if isinstance(node, list):
            index = int(part)
            assert 0 <= index < len(node), f"{dotted!r}: index {index} is past the list's {len(node)} entries"
            node = node[index]
        else:
            assert isinstance(node, dict), f"{dotted!r}: {part!r} reached a {type(node).__name__}"
            assert part in node, f"{dotted!r}: no key {part!r} in {sorted(map(str, node))}"
            node = node[part]
    return node


# -- the standards-run Setup steps (testing.md, Setup steps) --

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _git(tmp: Path, *args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")


def _level(line: str) -> int:
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def _replace_under(path: Path, heading: str, old: str, new: list[str]) -> None:
    """The one line `old` under `heading` (up to the next heading of its level or higher) becomes `new`."""
    lines = path.read_text(encoding="utf-8").split("\n")
    found = [i for i, line in enumerate(lines) if line == heading]
    if len(found) != 1:
        raise SetupError(f"{path}: expected one heading {heading!r}, found {len(found)}")
    start, level = found[0] + 1, _level(heading)
    end = next((j for j in range(start, len(lines)) if 0 < _level(lines[j]) <= level), len(lines))
    hits = [i for i in range(start, end) if lines[i] == old]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {old!r} under {heading!r}, found {len(hits)}")
    lines[hits[0]:hits[0] + 1] = new
    path.write_bytes("\n".join(lines).encode("utf-8"))


def SR0(tmp: Path) -> None:
    N0E(tmp)
    _replace_under(orders(tmp) / "prd.md", "## 5. Standards registry",
                   "Not applicable: the fixture runs no linter.", list(texts("rows")))
    load_vendored(tmp)
    _write(tmp / "src/ok.py", "x = 1\n")
    _write(tmp / "src/bad.py", "x = 2\n")
    _write(tmp / "src/.prd-toolkit/x.py", "x = 3\n")
    _write(tmp / ".prd-toolkit-notes.py", "x = 4\n")


def SG1(tmp: Path) -> None:
    _git(tmp, "add", ".prd-toolkit", "src/ok.py")


def SG2(tmp: Path) -> None:
    _git(tmp, "add", ".prd-toolkit", "src/.prd-toolkit/x.py", ".prd-toolkit-notes.py")


def SG3(tmp: Path) -> None:
    _git(tmp, "add", ".prd-toolkit")


def SG4(tmp: Path) -> None:
    _git(tmp, "add", ".prd-toolkit", "src/bad.py", "src/ok.py")


def SG5(tmp: Path) -> None:
    (tmp / "src/bad.py").unlink()
    (tmp / ".prd-toolkit-notes.py").unlink()
    _git(tmp, "add", "-A")


def SO(tmp: Path) -> None:
    """Delete the text ` ':(exclude).prd-toolkit'` where it appears in the generated GitHub workflow, so that
    the job's command is texts.old_job_line; raises SetupError when the text is not there or the command at
    `jobs.standards-1.steps.2.run` is not texts.old_job_line afterwards."""
    path = tmp / GITHUB_YML
    if not path.is_file():
        raise SetupError(f"SO: {path} is missing")
    text = path.read_text(encoding="utf-8")
    needle = " ':(exclude).prd-toolkit'"
    if needle not in text:
        raise SetupError(f"SO: {path} does not hold {needle!r}")
    path.write_bytes(text.replace(needle, "").encode("utf-8"))
    got = yaml_at(path, "jobs.standards-1.steps.2.run")
    if got != texts("old_job_line"):
        raise SetupError(f"SO: the job's command is {got!r}, not texts.old_job_line")


def _git_out(tmp: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=tmp, env=subprocess_env(), capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode != 0:
        raise SetupError(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout.decode("utf-8")


def _the_enforced_row(tmp: Path, row: str) -> tuple[Path, list[str], int]:
    """The prd.md path, its lines and the index of the one line equal to `row`; SetupError unless exactly one."""
    path = orders(tmp) / "prd.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line == row]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {row!r}, found {len(hits)}")
    return path, lines, hits[0]


def _row_becomes(tmp: Path, key: str) -> None:
    """In docs/prd/orders/prd.md, the enforced row (the third line of texts.rows) becomes texts.<key>."""
    path, lines, i = _the_enforced_row(tmp, texts("rows")[2])
    lines[i] = texts(key)
    path.write_bytes("\n".join(lines).encode("utf-8"))


def SM1(tmp: Path) -> None:
    _row_becomes(tmp, "none_row")


def SM2(tmp: Path) -> None:
    _row_becomes(tmp, "changed_row")


def SM3(tmp: Path) -> None:
    _row_becomes(tmp, "bogus_row")


def SM4(tmp: Path) -> None:
    _row_becomes(tmp, "failing_none_row")


def SM5(tmp: Path) -> None:
    """After SM1 (which the case names before it): in the enforced row, now texts.none_row, the text
    `` `**/*.py` `` becomes `` `**/*.rs` ``."""
    path, lines, i = _the_enforced_row(tmp, texts("none_row"))
    old, new = "`**/*.py`", "`**/*.rs`"
    if lines[i].count(old) != 1:
        raise SetupError(f"{path}: expected the text {old!r} once in the enforced row, found {lines[i].count(old)}")
    lines[i] = lines[i].replace(old, new)
    path.write_bytes("\n".join(lines).encode("utf-8"))


# <base> of step SC1, by the scratch repository's root (tmp_path); read with base_of(tmp).
_BASES: dict[Path, str] = {}

_COMMIT = ("-c", "user.name=Sample", "-c", "user.email=sample@example.com", "-c", "commit.gpgsign=false",
           "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m")


def SC1(tmp: Path) -> None:
    _git(tmp, "add", "-A")
    _git(tmp, *_COMMIT, "base")
    out = _git_out(tmp, "rev-parse", "HEAD").splitlines()
    if len(out) != 1:
        raise SetupError(f"SC1: git rev-parse HEAD printed {len(out)} lines, not one")
    _BASES[tmp] = out[0]
    ok = tmp / "src/ok.py"
    if not ok.is_file():
        raise SetupError(f"SC1: {ok} is missing")
    ok.write_bytes(ok.read_bytes() + b"y = 1\n")
    _write(tmp / "src/new.py", "x = 5\n")
    _write(tmp / ".prd-toolkit/extra.py", "x = 6\n")
    bad = tmp / "src/bad.py"
    if not bad.is_file():
        raise SetupError(f"SC1: {bad} is missing")
    bad.unlink()
    _git(tmp, "add", "-A")
    _git(tmp, *_COMMIT, "head")


def base_of(tmp: Path) -> str:
    """<base>: the commit step SC1 took, the one stdout line of `git rev-parse HEAD` after its first commit."""
    return _BASES[tmp]


STEPS = {
    "SR0": SR0, "SG1": SG1, "SG2": SG2, "SG3": SG3, "SG4": SG4, "SG5": SG5,
    "SM1": SM1, "SM2": SM2, "SM3": SM3, "SM4": SM4, "SM5": SM5, "SC1": SC1,
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
