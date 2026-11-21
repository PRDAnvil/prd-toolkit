"""Shared helper of the hooks-install characterization tests.

Everything here comes from docs/prd/prd-toolkit/testing.md (Harness; Setup steps, the hooks-install paragraph;
Borrowed steps and helpers) and from the header of docs/prd/prd-toolkit/test-cases/hooks-install.yaml: the
environment of the steps and the runs, the way a case's command text becomes an argument list, and the names the
header defines (HOOKS, VHOOKS, DISPATCH, VENDOR, V, SHIM, LINE).

A setup step that cannot be applied raises SetupError inside the `built` fixture, so the test ends as an error,
not a failure.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from lint_cli_support import load_vendored  # borrowed: VENDOR (testing.md, Borrowed steps and helpers)
from status_next_support import N0E  # borrowed: step N0E (testing.md, Borrowed steps and helpers)

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
PLUGIN = REPO / "prd-toolkit"
SCRIPTS = PLUGIN / "scripts"
HOOKS = SCRIPTS / "prd_hooks.py"
DISPATCH = SCRIPTS / "prd_dispatch.py"
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
ORDERS_REL = "docs/prd/orders"
RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung command ends the test

# testing.md, Subprocess environment and the hooks-install paragraph: the variables a run never inherits.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
    "PRD_PLUGINS_FILE", "STUB_LOG", "STUB_EXIT",
)

__all__ = [
    "REPO", "PLUGIN", "SCRIPTS", "HOOKS", "DISPATCH", "ORDERS_REL", "SetupError", "Result",
    "V", "SHIM", "LINE", "VENDOR", "N0E", "run", "step_run", "git", "write", "insert_after",
    "write_empty_no_git", "check_outside_git", "tree", "files_outside_pycache", "in_relative_order",
    "hi_tmp", "built", "given", "DEPLOY_OPS", "DEPLOY", "GH", "GL", "replace_line", "yaml_at", "file_lines",
    "write_exec", "FIXTURES",
]


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str


# -- names the case file's header defines --

def V() -> str:
    """The `version` of <repo>/prd-toolkit/.claude-plugin/plugin.json."""
    return json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def SHIM(hook: str, prd: str) -> str:
    """The text of templates/hooks/<hook>, read as UTF-8 with LF line ends, with every {{hook}} replaced by <hook>
    and every {{prd}} by <prd>."""
    text = (PLUGIN / "templates" / "hooks" / hook).read_bytes().decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("{{hook}}", hook).replace("{{prd}}", prd)


# AC-102.1: the hook line, exactly, with <hook> and <prd> to fill.
_LINE = (
    'prd_top="$(git rev-parse --show-toplevel)" || exit 1; '
    'if [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ ! -f "$prd_top/.prd-toolkit/prd" ]; '
    'then echo "prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped" >&2; '
    'elif [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ -f "$prd_top/.prd-toolkit/prd" ] '
    '&& [ -d "$prd_top/<prd>" ]; '
    'then command -v uv >/dev/null 2>&1 || '
    '{ echo "prd-toolkit: uv is not on PATH; install uv to run this hook" >&2; exit 1; }; '
    'sh "$prd_top/.prd-toolkit/prd" git-hook <hook> "$prd_top/<prd>" "$@" || exit $?; '
    'else echo "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped" >&2; fi'
)


def LINE(hook: str, prd: str = ORDERS_REL) -> str:
    """The hook line of FR-102 for <hook> and <prd> (docs/prd/orders unless given)."""
    return _LINE.replace("<hook>", hook).replace("<prd>", prd)


def VENDOR(repo: Path) -> Path:
    """Copy fixture repo/vendored to <repo>/.prd-toolkit, as its Load column says (lint_cli_support.load_vendored)."""
    try:
        return load_vendored(repo)
    except Exception as exc:  # the fixture's own check failed: the state was never built
        raise SetupError(f"VENDOR into {repo}: {exc}") from exc


# The header's DEPLOY_OPS: each wrapped comment line continues the string; the "Do:" and "Check:" lines are
# indented three spaces, as the header's note says.
DEPLOY_OPS = (
    "# Operations\n\n## Environments\n\n| Environment | URL | Production |\n|---|---|---|\n"
    "| staging | https://staging.example.com | no |\n| production | https://example.com | yes |\n\n"
    "## Runbook\n\n1. System tests on staging (actor: agent) (env: staging)\n   Run: tests system\n"
    "2. Approve production (actor: human) (env: production)\n   Do: reply \"deploy production\"\n"
    "   Check: the reply says \"deploy production\"\n\n## Drift\n\n"
    "| Environment | Check | Introspection command |\n|---|---|---|\n"
    "| production | version | `./app --prd-version` |\n\n## Secrets\n\n- DEPLOY_TOKEN: the deploy key\n"
)


def DEPLOY(repo: Path) -> None:
    """After N0E: write docs/prd/orders/operations.md as DEPLOY_OPS, and insert the system Levels row in testing.md."""
    orders = repo / ORDERS_REL
    write(orders / "operations.md", DEPLOY_OPS)
    insert_after(orders / "testing.md", "| integration | `pytest tests/integration` | local | build |",
                 "| system | `pytest tests/system` | local | deploy |")


def GH(job: str, cmds: list[str]) -> list[str]:
    """The GitHub job lines of the header's GH(id, cmds)."""
    return [f"  {job}:", "    runs-on: ubuntu-latest", "    steps:", "      - uses: actions/checkout@v4",
            "        with:", "          fetch-depth: 0", "      - uses: astral-sh/setup-uv@v5",
            *[f"      - run: {json.dumps(c)}" for c in cmds], ""]


def GL(job: str, cmds: list[str]) -> list[str]:
    """The GitLab job lines of the header's GL(id, cmds)."""
    return [f"{job}:", "  image: python:3.12", "  rules:",
            "    - if: '$CI_PIPELINE_SOURCE == \"merge_request_event\"'", "  before_script:",
            '    - "pip install uv"', "  script:", *[f"    - {json.dumps(c)}" for c in cmds], ""]


def replace_line(path: Path, old: str, new: list[str]) -> None:
    """Replace the one line equal to `old` with the lines `new`, or end the test as an error."""
    lines = path.read_bytes().decode("utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line == old]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {old!r}, found {len(hits)}")
    lines[hits[0]:hits[0] + 1] = new
    path.write_bytes("\n".join(lines).encode("utf-8"))


def yaml_at(doc, path: str):
    """The value at a read_as_yaml path: object keys and list indexes joined by `.`."""
    for part in path.split("."):
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


def file_lines(path: Path) -> list[str]:
    """str.splitlines() of the file's text, read as UTF-8."""
    return path.read_bytes().decode("utf-8").splitlines()


# -- the environment and the runs --

def _env(tmp: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for name in _DROPPED_ENV:
        env.pop(name, None)
    env["GIT_CONFIG_GLOBAL"] = str(tmp / "gitconfig-empty")
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    for key, value in (extra or {}).items():
        env[key] = _subst(value, tmp)
    return env


_NAMES = re.compile(r"\b(VHOOKS|HOOKS|DISPATCH)\b")


def _subst(text: str, tmp: Path) -> str:
    values = {"HOOKS": str(HOOKS), "VHOOKS": str(tmp / ".prd-toolkit" / "prd_hooks.py"), "DISPATCH": str(DISPATCH)}
    text = _NAMES.sub(lambda m: values[m.group(1)], text)
    return text.replace("<repo>", str(REPO)).replace("<tmp>", str(tmp))


def run(tmp: Path, cwd: Path, command: str | list[str], env: dict[str, str] | None = None) -> Result:
    """Run one case command: names replaced, split with shlex.split (a list is taken as its words), a first word
    `python` the interpreter running the tests, no shell. `env` is the case's own env, for this run only."""
    if isinstance(command, str):
        args = shlex.split(_subst(command, tmp))
    else:
        args = [_subst(word, tmp) for word in command]
    if args[0] == "python":
        args[0] = sys.executable
    proc = subprocess.run(args, cwd=cwd, env=_env(tmp, env), capture_output=True, timeout=RUN_TIMEOUT)
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


def step_run(tmp: Path, cwd: Path, command: str | list[str]) -> Result:
    """A step's command: it must exit 0, or the test ends as an error."""
    result = run(tmp, cwd, command)
    if result.exit != 0:
        raise SetupError(f"step command {command!r} in {cwd} exited {result.exit}:\n{result.stdout}{result.stderr}")
    return result


def git(tmp: Path, cwd: Path, *args: str) -> Result:
    """A test's own git command, in the hooks-install environment."""
    proc = subprocess.run(["git", *args], cwd=cwd, env=_env(tmp), capture_output=True, timeout=RUN_TIMEOUT)
    return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))


# -- step helpers --

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def write_exec(path: Path, text: str) -> None:
    """Write a file for git or sh to run (a hook file, hook.sh, a stub launcher), with mode 0o755."""
    write(path, text)
    os.chmod(path, 0o755)


def insert_after(path: Path, anchor: str, new: str) -> None:
    """Insert the line `new` directly after the one line equal to `anchor`."""
    lines = path.read_bytes().decode("utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line == anchor]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {anchor!r}, found {len(hits)}")
    lines.insert(hits[0] + 1, new)
    path.write_bytes("\n".join(lines).encode("utf-8"))


def check_outside_git(tmp: Path, folder: Path) -> None:
    """`git rev-parse --show-toplevel` must exit other than 0 in `folder`, or the test ends as an error."""
    result = git(tmp, folder, "rev-parse", "--show-toplevel")
    if result.exit == 0:
        raise SetupError(f"{folder} lies inside a git checkout: {result.stdout.strip()}")


def write_empty_no_git(tmp: Path) -> None:
    """Write each entry of fixture status-next/empty to <tmp>/<key>, run no git init, and check <tmp> is outside git."""
    data = yaml.safe_load((FIXTURES / "status-next" / "empty.yaml").read_text(encoding="utf-8"))
    for key, text in data.items():
        write(tmp / key, text)
    check_outside_git(tmp, tmp)


# -- effects --

def tree(root: Path) -> dict[str, bytes]:
    """Every file under `root`, by its relative path, with its bytes."""
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def files_outside_pycache(root: Path) -> dict[str, bytes]:
    """The files under `root` outside __pycache__ folders and not ending .pyc, by relative path, with their bytes."""
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_file() and "__pycache__" not in rel.parts and not p.name.endswith(".pyc"):
            out[rel.as_posix()] = p.read_bytes()
    return out


def in_relative_order(lines: list[str], expected: list[str]) -> bool:
    """Each expected line found, whole, after the one before it, other lines allowed between."""
    i = 0
    for line in lines:
        if i < len(expected) and line == expected[i]:
            i += 1
    return i == len(expected)


# -- fixtures --

@pytest.fixture
def hi_tmp(tmp_path, monkeypatch) -> Path:
    """<tmp>, with the empty file <tmp>/gitconfig-empty written before the first step, and GIT_CONFIG_GLOBAL and
    GIT_CONFIG_NOSYSTEM set in the test's own process (monkeypatch), so the borrowed step N0E's git init inherits
    them (testing.md, the hooks-install paragraph)."""
    (tmp_path / "gitconfig-empty").write_bytes(b"")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig-empty"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    return tmp_path


@pytest.fixture
def built(request, hi_tmp) -> Path:
    """<tmp> after the case's setup, run in pytest's setup phase so a SetupError ends the test as an error."""
    request.param(hi_tmp)
    return hi_tmp


def given(setup: Callable[[Path], None]):
    """Mark a test with its case's setup, a function of <tmp>; the `built` fixture runs it."""
    return pytest.mark.parametrize("built", [setup], indirect=True, ids=[setup.__name__])
