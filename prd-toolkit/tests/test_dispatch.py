"""prd_dispatch.py: one `prd <command>` entry that runs the script of that name."""
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

import prd_dispatch
from conftest import edit

PLUGIN_ROOT = Path(__file__).parent.parent
SCRIPTS = PLUGIN_ROOT / "scripts"
PLUGIN_VERSION = json.loads((PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text())["version"]


def _run(path, *args):
    return subprocess.run([sys.executable, str(path), *args], capture_output=True, text=True)


def run(*args):
    return _run(SCRIPTS / "prd_dispatch.py", *args)


def run_script(name, *args):
    return _run(SCRIPTS / name, *args)


def run_copy(tmp_path, *args):
    shutil.copy(SCRIPTS / "prd_dispatch.py", tmp_path / "prd_dispatch.py")
    return _run(tmp_path / "prd_dispatch.py", *args)


def header_deps(path):
    for line in Path(path).read_text().splitlines():
        if line.startswith("# dependencies = "):
            return ast.literal_eval(line.removeprefix("# dependencies = "))
    return []


def test_dispatch_table_covers_every_script():
    have = {p.name for p in SCRIPTS.glob("prd_*.py")} - {"prd_dispatch.py", "prd_tester_guard.py"}
    assert set(prd_dispatch.COMMANDS.values()) == have
    assert all(cmd == f[4:-3].replace("_", "-") for cmd, f in prd_dispatch.COMMANDS.items())


def test_dispatch_output_is_the_scripts():
    a, b = run("lint", "--help"), run_script("prd_lint.py", "--help")
    assert (a.returncode, a.stdout, a.stderr) == (b.returncode, b.stdout, b.stderr)


def test_dispatch_exit_codes(prd):
    assert run("lint", str(prd)).returncode == 0
    edit(prd, "prd.md", "status: Approved", "status: Nonsense")
    assert run("lint", str(prd)).returncode == 1
    assert run("lint", str(prd / "missing")).returncode == 2


def test_dispatch_help():
    for args in ((), ("-h",), ("--help",)):
        r = run(*args)
        lines = r.stdout.splitlines()
        assert r.returncode == 0 and lines[0] == "usage: prd <command> [arguments]"
        assert [ln.split()[0] for ln in lines[1:]] == sorted(prd_dispatch.COMMANDS)


def test_dispatch_version():
    assert run("--version").stdout.strip() == PLUGIN_VERSION


def test_dispatch_unknown_command():
    r = run("nope")
    assert r.returncode == 2 and r.stderr.splitlines()[0] == "prd: unknown command 'nope'"


def test_dispatch_missing_script(tmp_path):
    r = run_copy(tmp_path, "lint")
    assert r.returncode == 2
    assert r.stderr.strip() == f"prd: prd_lint.py is not in {tmp_path}; run prd_hooks.py install"


def test_requirements_is_the_headers_union():
    union = sorted({dep for f in prd_dispatch.COMMANDS.values() for dep in header_deps(SCRIPTS / f)})
    assert (SCRIPTS / "requirements.txt").read_text().splitlines() == union
