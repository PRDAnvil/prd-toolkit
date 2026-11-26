"""prd_dispatch.py: one `prd <command>` entry that runs the script of that name."""
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import prd_dispatch
from prdlint import hooks
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
    have = {p.name for p in SCRIPTS.glob("prd_*.py")} - {"prd_dispatch.py", "prd_tester_guard.py", "prd_edit_hook.py"}
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


def _name(dep):
    return re.split(r"[<>=!~;\[ ]", dep, maxsplit=1)[0].lower()


def test_requirements_is_the_headers_union():
    """requirements.txt: what the vendored scripts need; requirements-publish.txt: prd_publish.py's header, never vendored."""
    vendored = [f for f in prd_dispatch.COMMANDS.values() if f in hooks.VENDORED]
    union = sorted({dep for f in vendored for dep in header_deps(SCRIPTS / f)})
    assert (SCRIPTS / "requirements.txt").read_text().splitlines() == union
    publish = sorted(header_deps(SCRIPTS / "prd_publish.py"))
    assert (SCRIPTS / "requirements-publish.txt").read_text().splitlines() == publish
    others = {_name(d) for f in prd_dispatch.COMMANDS.values() if f != "prd_publish.py" for d in header_deps(SCRIPTS / f)}
    publish_only = {_name(d) for d in publish} - others
    assert publish_only and not publish_only & {_name(d) for d in union}, publish_only
    for name in ("requirements.txt", "requirements-publish.txt"):
        data = (SCRIPTS / name).read_bytes()
        assert data.endswith(b"\n") and not data.endswith(b"\n\n") and b"\r" not in data, name
    assert "requirements-publish.txt" not in hooks.VENDORED


def vendored_copy(dest, *scripts):
    """A vendored-copy layout: the dispatcher with a VERSION beside it, and only the scripts named."""
    shutil.copy(SCRIPTS / "prd_dispatch.py", dest / "prd_dispatch.py")
    (dest / "VERSION").write_text("0.0.0-test\n")
    for name in scripts:
        shutil.copy(SCRIPTS / name, dest / name)
    return dest / "prd_dispatch.py"


def test_plugin_only_is_what_install_never_vendors():
    assert prd_dispatch.PLUGIN_ONLY == ("publish",)
    assert set(prd_dispatch.PLUGIN_ONLY) == {c for c, f in prd_dispatch.COMMANDS.items() if f not in hooks.VENDORED}


def test_dispatch_plugin_only_command_in_a_vendored_copy(tmp_path):
    here = tmp_path.resolve()
    r = _run(vendored_copy(tmp_path), "publish", "docs/prd/x")
    assert (r.returncode, r.stdout, r.stderr) == (2, "", "prd: publish runs from the plugin, not from a vendored copy\n")
    r = _run(tmp_path / "prd_dispatch.py", "lint")  # a vendored script that is missing: install does bring it
    assert (r.returncode, r.stderr) == (2, f"prd: prd_lint.py is not in {here}; run prd_hooks.py install\n")


def test_dispatch_publish_missing_outside_a_vendored_copy(tmp_path):
    r = run_copy(tmp_path, "publish")  # no VERSION: not a vendored copy, the existing message
    assert (r.returncode, r.stderr) == (2, f"prd: prd_publish.py is not in {tmp_path.resolve()}; run prd_hooks.py install\n")


def test_dispatch_help_lists_only_the_scripts_present(tmp_path):
    r = _run(vendored_copy(tmp_path, "prd_lint.py", "prd_status.py"), "--help")
    lines = r.stdout.splitlines()
    assert r.returncode == 0 and lines[0] == "usage: prd <command> [arguments]"
    assert [ln.split()[0] for ln in lines[1:]] == ["lint", "status"]
    empty = tmp_path / "empty"
    empty.mkdir()
    r = run_copy(empty, "--help")  # no script beside the dispatcher at all
    assert (r.returncode, r.stdout) == (0, "usage: prd <command> [arguments]\n")


def test_dispatch_header_is_requirements_txt():
    """Run by its own header, the vendored dispatcher must not pull the publish-only packages."""
    assert sorted(header_deps(SCRIPTS / "prd_dispatch.py")) == (SCRIPTS / "requirements.txt").read_text().splitlines()
