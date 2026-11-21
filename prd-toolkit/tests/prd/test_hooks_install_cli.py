"""hooks-install: a malformed hooks command line (features/hooks-install.md FR-097; test-cases/hooks-install.yaml)."""
import os

from hooks_install_support import N0E, built, given, hi_tmp, run  # noqa: F401


def _n0e(tmp):
    N0E(tmp)


@given(_n0e)
def test_ci_needs_exactly_one_forge(built):
    """@prd T-097.1"""
    tmp = built
    for command in ("python HOOKS ci --gitlab --github docs/prd/orders", "python HOOKS ci docs/prd/orders"):
        r = run(tmp, tmp, command)
        assert r.exit == 2, (command, r)
        assert r.stdout == "", (command, r)
        assert r.stderr == "prd_hooks: ci needs exactly one of --gitlab or --github\n", (command, r)
    assert not (tmp / ".github").exists()
    assert not (tmp / ".gitlab").exists()


@given(_n0e)
def test_forge_and_force_flags_belong_to_ci(built):
    """@prd T-097.2"""
    tmp = built
    for command in ("python HOOKS install --force docs/prd/orders", "python HOOKS check --github docs/prd/orders"):
        r = run(tmp, tmp, command)
        assert r.exit == 2, (command, r)
        assert r.stdout == "", (command, r)
        assert r.stderr == "prd_hooks: --gitlab, --github and --force belong to ci\n", (command, r)
    assert not (tmp / ".prd-toolkit").exists()
    assert not (tmp / ".git/hooks/commit-msg").exists()


@given(_n0e)
def test_ci_flag_belongs_to_check(built):
    """@prd T-097.3"""
    tmp = built
    r = run(tmp, tmp, "python HOOKS install --ci docs/prd/orders")
    assert r.exit == 2, r
    assert r.stdout == "", r
    assert r.stderr == "prd_hooks: --ci belongs to check\n", r
    assert not (tmp / ".prd-toolkit").exists()


@given(_n0e)
def test_unknown_action_missing_folder_and_help(built):
    """@prd T-097.4"""
    tmp = built
    env = {"COLUMNS": "80", "PYTHON_COLORS": "0"}
    for command in ("python HOOKS frobnicate docs/prd/orders", "python HOOKS install"):
        r = run(tmp, tmp, command, env=env)
        assert r.exit == 2, (command, r)
        lines = r.stderr.splitlines()
        assert lines and lines[0].startswith("usage: prd_hooks.py "), (command, r)
        assert "prd_hooks.py: error: " in r.stderr, (command, r)
    r = run(tmp, tmp, "python HOOKS --help", env=env)
    assert r.exit == 0, r
    assert r.stderr == "", r
    lines = r.stdout.splitlines()
    assert lines and lines[0].startswith("usage: prd_hooks.py [-h] [--gitlab] [--github] [--force] [--ci]"), r
    assert not (tmp / ".prd-toolkit").exists()


@given(_n0e)
def test_folder_with_no_prd_md(built):
    """@prd T-097.5"""
    tmp = built
    r = run(tmp, tmp, "python HOOKS install nope")
    assert r.exit == 2, r
    assert r.stdout == "", r
    assert r.stderr == f"prd_hooks: {os.path.realpath(tmp)}/nope: no prd.md\n", r
    assert not (tmp / ".prd-toolkit").exists()
    assert not (tmp / ".git/hooks/commit-msg").exists()
