"""hooks-install: `prd_hooks.py check` (FR-108 to FR-111).

Every value comes from docs/prd/prd-toolkit/test-cases/hooks-install.yaml and the ACs it names.
"""
from __future__ import annotations

import os
import shutil
from collections import Counter
from pathlib import Path

import pytest

from hooks_install_support import (
    N0E, ORDERS_REL, SHIM, V, VENDOR, built, files_outside_pycache, given, hi_tmp, run, step_run, write,
    write_empty_no_git, write_exec,
)

__all__ = ["built", "hi_tmp"]  # pytest fixtures, imported for use

CHECK = f"python HOOKS check {ORDERS_REL}"
CHECK_CI = f"python HOOKS check --ci {ORDERS_REL}"


class KnownFailure(Exception):
    """The known failure of a case's `symptom:` was seen (raised for a strict xfail with raises=KnownFailure)."""


def append_line(path: Path, line: str) -> None:
    """Append `line` and a newline; a last line with no newline is ended first (the hooks-install paragraph)."""
    text = path.read_bytes().decode("utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_bytes((text + line + "\n").encode("utf-8"))


def installed(tmp: Path) -> None:
    """N0E, then run python HOOKS install docs/prd/orders in <tmp> (a step: it must exit 0)."""
    N0E(tmp)
    step_run(tmp, tmp, f"python HOOKS install {ORDERS_REL}")


# -- FR-108 --

def _setup_n0e(tmp: Path) -> None:
    N0E(tmp)


@given(_setup_n0e)
def test_check_without_vendored_copy(built):
    """@prd T-108.1"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stderr == ""
    assert r.stdout == ".prd-toolkit/ is missing; run prd_hooks.py install\n"


def _setup_108_2(tmp: Path) -> None:
    installed(tmp)
    v = tmp / ".prd-toolkit"
    write(v / "VERSION", "0.0.1\n")
    append_line(v / "prd_lint.py", "# changed")
    (v / "prd_trace.py").unlink()
    write(v / "prdlint" / "stale.py", "x = 1\n")


@given(_setup_108_2)
def test_check_reports_version_changed_missing_and_extra_files(built):
    """@prd T-108.2"""
    tmp = built
    before = files_outside_pycache(tmp / ".prd-toolkit")
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stderr == ""
    assert r.stdout.splitlines() == [
        f".prd-toolkit/VERSION 0.0.1 differs from the plugin version {V()}",
        ".prd-toolkit/prd_lint.py differs from the plugin copy",
        ".prd-toolkit/prd_trace.py is missing",
        ".prd-toolkit/prdlint/stale.py is not in the plugin",
    ], r.stdout
    assert files_outside_pycache(tmp / ".prd-toolkit") == before


@given(installed)
def test_check_clean_after_install(built):
    """@prd T-108.3"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 0, r
    assert r.stdout == ""
    assert r.stderr == ""


def _setup_108_4(tmp: Path) -> None:
    installed(tmp)
    (tmp / ".prd-toolkit" / "VERSION").unlink()


@given(_setup_108_4)
def test_check_with_no_version_file(built):
    """@prd T-108.4"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stdout.splitlines() == [f".prd-toolkit/VERSION (none) differs from the plugin version {V()}"], r.stdout


def _setup_108_5(tmp: Path) -> None:
    N0E(tmp)
    VENDOR(tmp)


@given(_setup_108_5)
def test_check_refuses_from_the_vendored_copy(built):
    """@prd T-108.5"""
    tmp = built
    r = run(tmp, tmp, f"python VHOOKS check {ORDERS_REL}")
    assert r.exit == 2, r
    assert r.stdout == ""
    assert r.stderr == "prd_hooks: run check from the plugin, not the vendored copy\n"


def _setup_108_6(tmp: Path) -> None:
    installed(tmp)
    write(tmp / ".prd-toolkit" / "prd_retired.py", "x = 1\n")
    write(tmp / ".prd-toolkit" / "templates" / "old.md", "old\n")


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-045")
@given(_setup_108_6)
def test_check_reports_files_the_plugin_no_longer_ships(built):
    """@prd T-108.6 known-failing E-045"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    if r.exit == 0 and r.stdout == "":
        raise KnownFailure("E-045: exit 0 and stdout empty")
    assert r.exit == 1, r
    assert r.stderr == ""
    assert Counter(r.stdout.splitlines()) == Counter([
        ".prd-toolkit/prd_retired.py is not in the plugin",
        ".prd-toolkit/templates/old.md is not in the plugin",
    ]), r.stdout


# -- FR-109 --

def _setup_109_1(tmp: Path) -> None:
    installed(tmp)
    append_line(tmp / ".git" / "hooks" / "pre-commit", "echo extra")


@given(_setup_109_1)
def test_check_reports_an_edited_toolkit_hook(built):
    """@prd T-109.1"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stdout.splitlines() == ["stale: .git/hooks/pre-commit; run prd_hooks.py install"], r.stdout


def _setup_109_2(tmp: Path) -> None:
    installed(tmp)
    write_exec(tmp / ".git" / "hooks" / "pre-commit",
               "#!/bin/sh\nuv run --script .prd-toolkit/prd_git_hook.py pre-commit docs/prd/orders\n")


@given(_setup_109_2)
def test_check_reports_a_user_hook_with_the_old_line(built):
    """@prd T-109.2"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stdout.splitlines() == [
        "stale: .git/hooks/pre-commit; replace its uv run --script … prd_git_hook.py line with the line "
        "prd_hooks.py install prints"
    ], r.stdout


def _setup_109_3(tmp: Path) -> None:
    installed(tmp)
    write_exec(tmp / ".git" / "hooks" / "commit-msg", SHIM("commit-msg", "docs/prd/other"))
    (tmp / ".git" / "hooks" / "pre-commit").unlink()


@given(_setup_109_3)
def test_check_quiet_on_other_prd_absent_and_own_hooks(built):
    """@prd T-109.3"""
    tmp = built
    r1 = run(tmp, tmp, CHECK)
    write_exec(tmp / ".git" / "hooks" / "pre-commit", "#!/bin/sh\necho mine\n")
    r2 = run(tmp, tmp, CHECK)
    for i, r in enumerate((r1, r2), start=1):
        assert r.exit == 0, (i, r)
        assert r.stdout == "", (i, r.stdout)
        assert r.stderr == "", (i, r.stderr)


# -- FR-110 --

def _setup_110_1(tmp: Path) -> None:
    installed(tmp)
    shutil.rmtree(tmp / ".prd-toolkit" / "packs" / "service")


@given(_setup_110_1)
def test_check_reports_a_missing_pack(built):
    """@prd T-110.1"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stdout.splitlines() == [
        "packs/service: missing; source prd-toolkit 1.0.0; run prd_hooks.py install"
    ], r.stdout


def _setup_110_2(tmp: Path) -> None:
    installed(tmp)
    append_line(tmp / ".prd-toolkit" / "packs" / "service" / "pack.yaml", "# edited")


@given(_setup_110_2)
def test_check_reports_a_differing_pack(built):
    """@prd T-110.2"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stdout.splitlines() == [
        "packs/service: differs from prd-toolkit 1.0.0; run prd_hooks.py install"
    ], r.stdout


@given(installed)
def test_check_reports_an_unrecorded_or_other_pack_source(built):
    """@prd T-110.3"""
    tmp = built
    sources = tmp / ".prd-toolkit" / "pack-sources.json"
    unrecorded = ("packs/service: vendored from an unrecorded source, the PRD names prd-toolkit; "
                  "run prd_hooks.py install")
    other = "packs/service: vendored from kit@example, the PRD names prd-toolkit; run prd_hooks.py install"
    for i, (text, line) in enumerate(
            (("{}\n", unrecorded), ('{"service": "kit@example"}\n', other), ("not json\n", unrecorded)), start=1):
        write(sources, text)
        r = run(tmp, tmp, CHECK)
        assert r.exit == 1, (i, r)
        assert r.stdout.splitlines() == [line], (i, r.stdout)


# -- FR-111 --

def _setup_111_1(tmp: Path) -> None:
    installed(tmp)
    write(tmp / "CLAUDE.md", "# Notes\n")


@given(_setup_111_1)
def test_check_reports_a_stale_claude_block(built):
    """@prd T-111.1"""
    tmp = built
    for command in (CHECK, CHECK_CI):
        r = run(tmp, tmp, command)
        assert r.exit == 1, (command, r)
        assert r.stderr == "", (command, r.stderr)
        assert r.stdout.splitlines() == [f"stale: CLAUDE.md; run prd_block.py {ORDERS_REL}"], (command, r.stdout)
    assert (tmp / "CLAUDE.md").read_bytes() == b"# Notes\n"


def _setup_111_2(tmp: Path) -> None:
    installed(tmp)
    write(tmp / "CLAUDE.md", "<!-- prd-toolkit:start -->\n<!-- prd-toolkit:start -->\n<!-- prd-toolkit:end -->\n")


@given(_setup_111_2)
def test_check_reports_a_broken_marker_as_stale(built):
    """@prd T-111.2"""
    tmp = built
    for command in (CHECK_CI, CHECK):
        r = run(tmp, tmp, command)
        assert r.exit == 1, (command, r)
        assert r.stderr == "", (command, r.stderr)
        assert r.stdout.splitlines() == [
            f"stale: CLAUDE.md: more than one prd-toolkit block; run prd_block.py {ORDERS_REL}"
        ], (command, r.stdout)


def _setup_111_3(tmp: Path) -> None:
    installed(tmp)
    append_line(tmp / ".gitignore", "CLAUDE.md")
    write(tmp / "CLAUDE.md", "# Notes\n")


@given(_setup_111_3)
def test_check_ci_skips_an_ignored_claude_md(built):
    """@prd T-111.3"""
    tmp = built
    r = run(tmp, tmp, CHECK_CI)
    assert r.exit == 0, r
    assert r.stdout == ""
    assert r.stderr == ""


def _setup_111_4(tmp: Path) -> None:
    installed(tmp)
    v = tmp / ".prd-toolkit"
    append_line(v / "prd_lint.py", "# changed")
    write(v / "VERSION", "0.0.1\n")
    append_line(tmp / ".git" / "hooks" / "pre-commit", "echo extra")
    append_line(v / "packs" / "service" / "pack.yaml", "# edited")


@given(_setup_111_4)
def test_check_ci_ignores_copy_hooks_and_packs(built):
    """@prd T-111.4"""
    tmp = built
    r = run(tmp, tmp, CHECK_CI)
    assert r.exit == 0, r
    assert r.stdout == ""
    assert r.stderr == ""


def _setup_111_5(tmp: Path) -> None:
    N0E(tmp)
    VENDOR(tmp)
    step_run(tmp, tmp, f"python HOOKS ci --github {ORDERS_REL}")


@given(_setup_111_5)
def test_check_ci_runs_from_the_vendored_copy(built):
    """@prd T-111.5"""
    tmp = built
    r = run(tmp, tmp, f"python VHOOKS check --ci {ORDERS_REL}")
    assert r.exit == 1, r
    assert r.stderr == ""
    assert f"stale: CLAUDE.md; run prd_block.py {ORDERS_REL}" in r.stdout.splitlines(), r.stdout
    assert "stale: .github" not in r.stdout, r.stdout


def _setup_no_git(tmp: Path) -> None:
    write_empty_no_git(tmp)


@given(_setup_no_git)
def test_check_ci_refuses_outside_a_git_checkout(built):
    """@prd T-111.6"""
    tmp = built
    r = run(tmp, tmp, CHECK_CI)
    assert r.exit == 2, r
    assert r.stdout == ""
    assert r.stderr == f"prd_hooks: {os.path.realpath(tmp)}/{ORDERS_REL} is not inside a git checkout\n"


def _setup_111_7(tmp: Path) -> None:
    installed(tmp)
    write(tmp / ".github" / "workflows" / "prd-toolkit.yml", "# old\n")


@given(_setup_111_7)
def test_check_reports_a_stale_ci_file(built):
    """@prd T-111.7"""
    tmp = built
    r = run(tmp, tmp, CHECK)
    assert r.exit == 1, r
    assert r.stdout.splitlines() == [
        "stale: .github/workflows/prd-toolkit.yml: re-run prd_hooks.py ci --github --force"
    ], r.stdout
