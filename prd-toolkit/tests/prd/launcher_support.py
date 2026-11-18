"""Helpers for the launcher cases (test-cases/launcher.yaml).

Written from testing.md (Harness; the launcher paragraph of Setup steps) and the conventions at the top of
test-cases/launcher.yaml. Every helper a launcher case needs is defined here; nothing is imported from another
area's support file.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
LAUNCHER = REPO / "prd-toolkit" / "scripts" / "prd"
# SCRIPTS is written exactly as LAUNCHER's folder is written in the command.
SCRIPTS = str(LAUNCHER.parent)
FIXTURES = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures"
PLUGIN_JSON = REPO / "prd-toolkit" / ".claude-plugin" / "plugin.json"

# Harness, Subprocess environment: removed from the runner's environment.
_HARNESS_DROP = ("PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE")
# Setup steps, launcher paragraph: removed as well for every run of a launcher case.
_LAUNCHER_DROP = ("UV_PYTHON", "VIRTUAL_ENV", "CONDA_PREFIX", "UV_STUB_LOG", "UV_STUB_FIND", "UV_STUB_FIND_EXIT")


@dataclass
class Run:
    exit: int
    stdout: bytes
    stderr: bytes


def texts() -> dict:
    """Fixture launcher/texts, read with yaml.safe_load."""
    return yaml.safe_load((FIXTURES / "launcher" / "texts.yaml").read_text(encoding="utf-8"))


def base_env() -> dict[str, str]:
    """The Subprocess environment of a launcher run, before the case's own env is added."""
    env = dict(os.environ)
    for name in _HARNESS_DROP + _LAUNCHER_DROP:
        env.pop(name, None)
    return env


def subprocess_path() -> str:
    """<PATH>: the value of PATH in the Subprocess environment."""
    return base_env().get("PATH", "")


def run_launcher(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> Run:
    """Run LAUNCHER as a program, with cwd as the working directory and the case's env added."""
    full = base_env()
    full.update(env or {})
    p = subprocess.run([str(LAUNCHER), *args], cwd=str(cwd), env=full, capture_output=True)
    return Run(p.returncode, p.stdout, p.stderr)


def plugin_version() -> str:
    """<version>: the key `version` of prd-toolkit/.claude-plugin/plugin.json, read as JSON."""
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]


def log_lines(path: Path) -> list[str]:
    """A uv log's text split by str.splitlines()."""
    return path.read_text(encoding="utf-8").splitlines()


def LS0(tmp: Path) -> Path:
    """Step LS0: write texts.stub_uv to <tmp>/bin/uv and set its mode to 0o755."""
    stub = tmp / "bin" / "uv"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_bytes(texts()["stub_uv"].encode("utf-8"))
    os.chmod(stub, 0o755)
    return stub


@contextlib.contextmanager
def LV(tmp: Path) -> Iterator[None]:
    """Step LV, as a context manager: whatever the test's outcome, <tmp>/locked gets its mode 0o700 back."""
    locked = tmp / "locked"
    locked.mkdir(parents=True)
    venv_bin = tmp / "work" / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (tmp / "work" / ".venv" / "pyvenv.cfg").write_bytes(texts()["pyvenv_cfg"].encode("utf-8"))
    os.symlink(str(locked / "python"), str(venv_bin / "python"))
    try:
        os.chmod(locked, 0o000)
        try:
            os.listdir(locked)
        except PermissionError:
            pass
        else:
            pytest.skip("os.listdir of <tmp>/locked succeeded at mode 0o000 (step LV)")
        yield
    finally:
        os.chmod(locked, 0o700)
