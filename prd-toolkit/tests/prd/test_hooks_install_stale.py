"""hooks-install: install names a stale CI file (FR-105) and install from the vendored copy (FR-106).

Every value comes from docs/prd/prd-toolkit/test-cases/hooks-install.yaml and the ACs it names.
"""
from __future__ import annotations

from pathlib import Path

from hooks_install_support import (
    N0E, ORDERS_REL, VENDOR, built, files_outside_pycache, given, hi_tmp, run, step_run, write,
)

__all__ = ["built", "hi_tmp"]  # pytest fixtures, imported for use

INSTALL = f"python HOOKS install {ORDERS_REL}"
GL_FILE = Path(".gitlab") / "prd-toolkit.yml"
GH_FILE = Path(".github") / "workflows" / "prd-toolkit.yml"


def _setup_105_1(tmp: Path) -> None:
    """N0E in <tmp>/a; N0E in <tmp>/b; the two old CI files in a; ci --github and ci --gitlab in b."""
    N0E(tmp / "a")
    N0E(tmp / "b")
    write(tmp / "a" / GL_FILE, "# old\n")
    write(tmp / "a" / GH_FILE, "# old\n")
    step_run(tmp, tmp / "b", f"python HOOKS ci --github {ORDERS_REL}")
    step_run(tmp, tmp / "b", f"python HOOKS ci --gitlab {ORDERS_REL}")


@given(_setup_105_1)
def test_install_names_stale_ci_files(built):
    """@prd T-105.1"""
    tmp = built
    a, b = tmp / "a", tmp / "b"

    r1 = run(tmp, a, INSTALL)
    assert r1.exit == 0, r1
    assert r1.stdout.splitlines()[-2:] == [
        "stale: .gitlab/prd-toolkit.yml: re-run prd_hooks.py ci --gitlab --force",
        "stale: .github/workflows/prd-toolkit.yml: re-run prd_hooks.py ci --github --force",
    ], r1.stdout
    assert (a / GL_FILE).read_bytes() == b"# old\n"
    assert (a / GH_FILE).read_bytes() == b"# old\n"

    b_before = ((b / GL_FILE).read_bytes(), (b / GH_FILE).read_bytes())
    r2 = run(tmp, b, INSTALL)
    assert r2.exit == 0, r2
    assert "stale: " not in r2.stdout, r2.stdout
    assert ((b / GL_FILE).read_bytes(), (b / GH_FILE).read_bytes()) == b_before


def _setup_106_1(tmp: Path) -> None:
    """N0E; VENDOR; an old GitHub CI file."""
    N0E(tmp)
    VENDOR(tmp)
    write(tmp / GH_FILE, "# old\n")


@given(_setup_106_1)
def test_install_from_vendored_copy_writes_hooks_only(built):
    """@prd T-106.1"""
    tmp = built
    vendored = tmp / ".prd-toolkit"
    before = files_outside_pycache(vendored)

    r = run(tmp, tmp, f"python VHOOKS install {ORDERS_REL}")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert r.stdout.splitlines() == [
        "installed .git/hooks/commit-msg",
        "installed .git/hooks/pre-commit",
        "stale: .github/workflows/prd-toolkit.yml: re-run prd_hooks.py ci --github --force",
    ], r.stdout

    template = (vendored / "hooks" / "commit-msg").read_bytes().decode("utf-8")
    expected = template.replace("{{hook}}", "commit-msg").replace("{{prd}}", ORDERS_REL)
    assert (tmp / ".git" / "hooks" / "commit-msg").read_bytes().decode("utf-8") == expected
    assert files_outside_pycache(vendored) == before
    for rel in (".gitignore", "CLAUDE.md", f"{ORDERS_REL}/README.md"):
        assert not (tmp / rel).exists(), rel
