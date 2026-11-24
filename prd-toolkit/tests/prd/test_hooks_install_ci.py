"""hooks-install: `prd_hooks.py ci` writes the include file and refuses to overwrite a different one (FR-113).

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/hooks-install.yaml (T-113.1 to T-113.5)
and features/hooks-install.md (AC-113.1 to AC-113.5); the environment and the steps from testing.md (Setup steps,
the hooks-install paragraph).
"""
from __future__ import annotations

import os
from pathlib import Path

from hooks_install_support import (  # noqa: F401  (hi_tmp, built: fixtures)
    N0E, ORDERS_REL, SetupError, VENDOR, built, given, hi_tmp, in_relative_order, run, step_run, write,
    write_empty_no_git,
)

GH_FILE = ".github/workflows/prd-toolkit.yml"
GL_FILE = ".gitlab/prd-toolkit.yml"
GH_WROTE = "wrote .github/workflows/prd-toolkit.yml\n"
GL_WROTE = "wrote .gitlab/prd-toolkit.yml\ninclude: '.gitlab/prd-toolkit.yml'\n"


# -- setups (the cases' `setup:` lists) --

def setup_n0e(tmp: Path) -> None:
    """setup: [N0E]"""
    N0E(tmp)


def setup_113_2(tmp: Path) -> None:
    """N0E in <tmp>/a; N0E in <tmp>/b; run python HOOKS ci --github docs/prd/orders in <tmp>/b;
    write <tmp>/a/.github/workflows/prd-toolkit.yml as "# old\\n"."""
    N0E(tmp / "a")
    N0E(tmp / "b")
    step_run(tmp, tmp / "b", "python HOOKS ci --github docs/prd/orders")
    write(tmp / "a" / GH_FILE, "# old\n")


def setup_113_4(tmp: Path) -> None:
    """N0E; VENDOR; delete <tmp>/.prd-toolkit/prd."""
    N0E(tmp)
    VENDOR(tmp)
    launcher = tmp / ".prd-toolkit" / "prd"
    if not launcher.is_file():
        raise SetupError(f"{launcher}: no file to delete")
    launcher.unlink()


def setup_no_git(tmp: Path) -> None:
    """Write each entry of status-next/empty to <tmp>/<key>, run no git init, and check <tmp> is outside git."""
    write_empty_no_git(tmp)


# -- tests --

@given(setup_n0e)
def test_ci_writes_both_files(built):
    """@prd T-113.1"""
    tmp = built
    r1 = run(tmp, tmp, "python HOOKS ci --github docs/prd/orders")
    r2 = run(tmp, tmp, "python HOOKS ci --gitlab docs/prd/orders")

    assert r1.exit == 0, r1.stdout + r1.stderr
    assert r1.stderr == ""
    assert r1.stdout == GH_WROTE
    assert r2.exit == 0, r2.stdout + r2.stderr
    assert r2.stderr == ""
    assert r2.stdout == GL_WROTE

    for rel in (GH_FILE, GL_FILE):
        path = tmp / rel
        assert path.is_file(), f"{rel} does not exist"
        assert b"\r" not in path.read_bytes(), f"{rel} holds a \\r byte"


@given(setup_113_2)
def test_ci_refuses_a_different_file_without_force(built):
    """@prd T-113.2"""
    tmp = built
    a = tmp / "a"

    r1 = run(tmp, a, "python HOOKS ci --github docs/prd/orders")
    assert r1.exit == 1, r1.stdout + r1.stderr
    lines = r1.stdout.splitlines()
    assert lines, "stdout is empty"
    assert lines[0] == "--- .github/workflows/prd-toolkit.yml (existing)", r1.stdout
    assert in_relative_order(lines, [
        "+++ .github/workflows/prd-toolkit.yml (generated)",
        "-# old",
        ".github/workflows/prd-toolkit.yml exists and differs; rerun with --force to overwrite it",
    ]), r1.stdout
    assert (a / GH_FILE).read_bytes() == b"# old\n", "the file changed on run_1"

    r2 = run(tmp, a, "python HOOKS ci --github --force docs/prd/orders")
    assert r2.exit == 0, r2.stdout + r2.stderr
    assert r2.stdout == GH_WROTE
    assert (a / GH_FILE).read_bytes() == (tmp / "b" / GH_FILE).read_bytes()


@given(setup_n0e)
def test_ci_rewrites_the_generated_text(built):
    """@prd T-113.3"""
    tmp = built
    r1 = run(tmp, tmp, "python HOOKS ci --gitlab docs/prd/orders")
    assert r1.exit == 0, r1.stdout + r1.stderr
    assert r1.stdout == GL_WROTE
    after_run_1 = (tmp / GL_FILE).read_bytes()

    r2 = run(tmp, tmp, "python HOOKS ci --gitlab docs/prd/orders")
    assert r2.exit == 0, r2.stdout + r2.stderr
    assert r2.stdout == GL_WROTE
    assert (tmp / GL_FILE).read_bytes() == after_run_1


@given(setup_113_4)
def test_ci_refuses_a_vendored_copy_without_launcher(built):
    """@prd T-113.4"""
    tmp = built
    r = run(tmp, tmp, "python HOOKS ci --github docs/prd/orders")
    assert r.exit == 2, r.stdout + r.stderr
    assert r.stdout == ""
    assert r.stderr == (
        "prd_hooks: .prd-toolkit/ predates 0.8.8 (no .prd-toolkit/prd); "
        "run prd_hooks.py install docs/prd/orders first\n"
    )
    assert not (tmp / ".github").exists()


@given(setup_no_git)
def test_ci_refuses_outside_a_git_checkout(built):
    """@prd T-113.5"""
    tmp = built
    r = run(tmp, tmp, "python HOOKS ci --github docs/prd/orders")
    folder = os.path.realpath(tmp) + "/docs/prd/orders"
    assert r.exit == 2, r.stdout + r.stderr
    assert r.stdout == ""
    assert r.stderr == f"prd_hooks: {folder} is not inside a git checkout\n"
    assert not (tmp / ".github").exists()
    assert not (tmp / ORDERS_REL / ".github").exists()
