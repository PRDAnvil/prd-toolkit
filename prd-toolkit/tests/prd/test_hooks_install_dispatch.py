"""hooks-install: the dispatcher `prd_dispatch.py` runs a script by its command name, and prints help and its
version (FR-119, FR-120).

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/hooks-install.yaml (T-119.1 to T-120.3)
and the names its header defines (DISPATCH, V).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from hooks_install_support import SCRIPTS, V, hi_tmp, run, write  # noqa: F401  (hi_tmp: fixture)

# AC-119.1 / AC-119.2: the twenty commands, in name order.
COMMANDS = ["block", "build-check", "change", "confirm", "context", "deploy", "drift", "error", "gates", "git-hook",
            "help", "hooks", "judge", "links", "lint", "pack", "practices", "publish", "status", "trace"]


def copy_script(name: str, folder: Path) -> None:
    """Copy <repo>/prd-toolkit/scripts/<name> into `folder`, creating it."""
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SCRIPTS / name, folder / name)


def triple(r) -> tuple:
    return (r.exit, r.stdout, r.stderr)


# -- FR-119 --

def test_dispatcher_runs_the_script(hi_tmp):
    """@prd T-119.1"""
    tmp = hi_tmp
    r1 = run(tmp, tmp, "python DISPATCH trace --interface")
    r2 = run(tmp, tmp, "python <repo>/prd-toolkit/scripts/prd_trace.py --interface")
    r3 = run(tmp, tmp, "python DISPATCH lint <tmp>/nope")
    r4 = run(tmp, tmp, "python <repo>/prd-toolkit/scripts/prd_lint.py <tmp>/nope")

    assert r1.exit == 0, r1.stderr
    assert r1.stdout == "1\n"
    # relations
    assert triple(r1) == triple(r2)
    assert triple(r3) == triple(r4)
    assert r3.exit == 2


def test_dispatcher_unknown_command(hi_tmp):
    """@prd T-119.2"""
    tmp = hi_tmp
    r = run(tmp, tmp, "python DISPATCH nope")
    assert r.exit == 2, r.stderr
    assert r.stdout == ""
    assert r.stderr == (
        "prd: unknown command 'nope'\n"
        "commands: block, build-check, change, confirm, context, deploy, drift, error, gates, git-hook, help, hooks, "
        "judge, links, lint, pack, practices, publish, status, trace\n"
    )


def test_dispatcher_script_absent(hi_tmp):
    """@prd T-119.3"""
    tmp = hi_tmp
    copy_script("prd_dispatch.py", tmp / "d")
    folder = os.path.realpath(tmp / "d")

    r1 = run(tmp, tmp, "python <tmp>/d/prd_dispatch.py lint")
    assert triple(r1) == (2, "", f"prd: prd_lint.py is not in {folder}; run prd_hooks.py install\n")

    r2 = run(tmp, tmp, "python <tmp>/d/prd_dispatch.py publish")
    assert triple(r2) == (2, "", f"prd: prd_publish.py is not in {folder}; run prd_hooks.py install\n")


def test_dispatcher_publish_from_a_vendored_copy(hi_tmp):
    """@prd T-119.4"""
    tmp = hi_tmp
    copy_script("prd_dispatch.py", tmp / "d")
    write(tmp / "d" / "VERSION", "0.0.0-test\n")
    folder = os.path.realpath(tmp / "d")

    r1 = run(tmp, tmp, "python <tmp>/d/prd_dispatch.py publish docs/prd/x")
    assert triple(r1) == (2, "", "prd: publish runs from the plugin, not from a vendored copy\n")

    r2 = run(tmp, tmp, "python <tmp>/d/prd_dispatch.py lint")
    assert r2.exit == 2, r2.stderr
    assert r2.stderr == f"prd: prd_lint.py is not in {folder}; run prd_hooks.py install\n"


# -- FR-120 --

HOOKS_LINE = (
    "hooks        Vendor the toolkit into a repo and manage its git hooks: install | check | uninstall | vendor "
    "<prd-folder> (vendor refreshes .prd-toolkit/ alone, from the plugin); ci --gitlab|--github [--force] "
    "<prd-folder> writes the merge-gate CI include file. Exit 0 clean, 1 findings, 2 usage, dependency or internal "
    "error."
)


def first_non_space_after_name(line: str) -> int:
    """The index of the first non-space character after the line's first word, its command name."""
    name = line.split()[0]
    assert line.startswith(name), line
    i = len(name)
    while i < len(line) and line[i] == " ":
        i += 1
    return i


def test_dispatcher_help(hi_tmp):
    """@prd T-120.1"""
    tmp = hi_tmp
    runs = [run(tmp, tmp, "python DISPATCH"), run(tmp, tmp, "python DISPATCH -h"),
            run(tmp, tmp, "python DISPATCH --help")]
    for r in runs:
        assert r.exit == 0, r.stderr
        assert r.stderr == ""
        lines = r.stdout.splitlines()
        assert lines[:1] == ["usage: prd <command> [arguments]"], r.stdout
        assert HOOKS_LINE in lines, r.stdout
        # relations
        assert len(lines) == 21, r.stdout
        assert [line.split()[0] if line.split() else "" for line in lines[1:21]] == COMMANDS, r.stdout
        for line in lines[1:21]:
            assert first_non_space_after_name(line) == 13, line
    assert runs[0].stdout == runs[1].stdout == runs[2].stdout


def test_dispatcher_help_lists_only_present_scripts(hi_tmp):
    """@prd T-120.2"""
    tmp = hi_tmp
    for name in ("prd_dispatch.py", "prd_lint.py", "prd_status.py"):
        copy_script(name, tmp / "d")
    write(tmp / "d" / "VERSION", "0.0.0-test\n")
    copy_script("prd_dispatch.py", tmp / "e")

    r1 = run(tmp, tmp, "python <tmp>/d/prd_dispatch.py --help")
    assert r1.exit == 0, r1.stderr
    assert r1.stdout == (
        "usage: prd <command> [arguments]\n"
        "lint    Lint a PRD folder. Exit 0 clean, 1 violations, 2 usage, dependency or internal error.\n"
        "status  Print where every requirement of a PRD stands. Exit 0 printed, 2 usage or tool error.\n"
    )

    r2 = run(tmp, tmp, "python <tmp>/e/prd_dispatch.py --help")
    assert r2.exit == 0, r2.stderr
    assert r2.stdout == "usage: prd <command> [arguments]\n"


def test_dispatcher_version(hi_tmp):
    """@prd T-120.3"""
    tmp = hi_tmp
    copy_script("prd_dispatch.py", tmp / "d")
    write(tmp / "d" / "VERSION", "  0.0.0-test \n")

    r1 = run(tmp, tmp, "python DISPATCH --version")
    assert r1.exit == 0, r1.stderr
    assert r1.stdout == V() + "\n"

    r2 = run(tmp, tmp, "python <tmp>/d/prd_dispatch.py --version")
    assert r2.exit == 0, r2.stderr
    assert r2.stdout == "0.0.0-test\n"
