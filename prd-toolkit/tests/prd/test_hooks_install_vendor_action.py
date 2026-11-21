"""hooks-install: `prd_hooks.py vendor` refreshes .prd-toolkit/ and writes nothing else (FR-107).

Every value comes from docs/prd/prd-toolkit/test-cases/hooks-install.yaml and the ACs it names.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from hooks_install_support import (
    N0E, ORDERS_REL, V, VENDOR, built, files_outside_pycache, given, hi_tmp, insert_after, run,
    write_empty_no_git,
)

__all__ = ["built", "hi_tmp"]  # pytest fixtures, imported for use

VENDOR_CMD = f"python HOOKS vendor {ORDERS_REL}"


class KnownFailure(Exception):
    """The known failure of a case's `symptom:` was seen (raised for a strict xfail with raises=KnownFailure)."""


def _setup_107_1(tmp: Path) -> None:
    """N0E in <tmp>/a; N0E in <tmp>/b."""
    N0E(tmp / "a")
    N0E(tmp / "b")


@given(_setup_107_1)
def test_vendor_writes_the_copy_as_install_does(built):
    """@prd T-107.1"""
    tmp = built
    a, b = tmp / "a", tmp / "b"

    r1 = run(tmp, a, f"python HOOKS install {ORDERS_REL}")
    assert r1.exit == 0, r1

    r2 = run(tmp, b, VENDOR_CMD)
    assert r2.exit == 0, r2
    assert r2.stderr == ""
    assert r2.stdout == f"vendored the toolkit into .prd-toolkit/ (version {V()})\n"

    # the hooks-install paragraph: a folder comparison leaves out __pycache__ folders and .pyc files
    assert files_outside_pycache(b / ".prd-toolkit") == files_outside_pycache(a / ".prd-toolkit")
    for rel in (".git/hooks/commit-msg", ".git/hooks/pre-commit", ".gitignore", "CLAUDE.md",
                f"{ORDERS_REL}/README.md", "docs/prd/README.md", ".github", ".gitlab"):
        assert not (b / rel).exists(), rel


def _setup_107_2(tmp: Path) -> None:
    """N0E; VENDOR."""
    N0E(tmp)
    VENDOR(tmp)


@given(_setup_107_2)
def test_vendor_refuses_from_the_vendored_copy(built):
    """@prd T-107.2"""
    tmp = built
    before = files_outside_pycache(tmp / ".prd-toolkit")
    r = run(tmp, tmp, f"python VHOOKS vendor {ORDERS_REL}")
    assert r.exit == 2, r
    assert r.stdout == ""
    assert r.stderr == "prd_hooks: vendor runs from the plugin, not from .prd-toolkit/\n"
    assert files_outside_pycache(tmp / ".prd-toolkit") == before


def _setup_nosuch_pack(tmp: Path) -> None:
    """N0E; the line `- Pack: nosuch 1.0.0 (prd-toolkit)` directly after `- Language: Python 3.12` in prd.md."""
    N0E(tmp)
    insert_after(tmp / ORDERS_REL / "prd.md", "- Language: Python 3.12", "- Pack: nosuch 1.0.0 (prd-toolkit)")


@given(_setup_nosuch_pack)
def test_vendor_refuses_an_unresolved_pack(built):
    """@prd T-107.3"""
    tmp = built
    r = run(tmp, tmp, VENDOR_CMD)
    assert r.exit == 2, r
    assert r.stdout == ""
    assert not (tmp / ".prd-toolkit").exists()


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-042")
@given(_setup_nosuch_pack)
def test_vendor_refusal_names_vendor(built):
    """@prd T-107.4 known-failing E-042"""
    tmp = built
    r = run(tmp, tmp, VENDOR_CMD)
    symptom = "prd_hooks: install refused: pack nosuch 1.0.0 (prd-toolkit) not found; looked in: "
    if r.exit == 2 and symptom in r.stderr and "vendor refused" not in r.stderr:
        raise KnownFailure(f"E-042: {r.stderr.strip()}")
    assert r.exit == 2, r
    assert r.stdout == ""
    assert "prd_hooks: vendor refused: pack nosuch 1.0.0 (prd-toolkit) not found; looked in: " in r.stderr, r.stderr
    assert not (tmp / ".prd-toolkit").exists()


def _setup_no_git(tmp: Path) -> None:
    """status-next/empty written to <tmp> with no git init; <tmp> must lie outside every git checkout."""
    write_empty_no_git(tmp)


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-043")
@given(_setup_no_git)
def test_vendor_refuses_outside_a_git_checkout(built):
    """@prd T-107.5 known-failing E-043"""
    tmp = built
    r = run(tmp, tmp, VENDOR_CMD)
    if r.exit == 0 and (tmp / ORDERS_REL / ".prd-toolkit").is_dir():
        raise KnownFailure("E-043: exit 0 and docs/prd/orders/.prd-toolkit exists")
    assert r.exit == 2, r
    assert r.stdout == ""
    assert r.stderr == f"prd_hooks: {os.path.realpath(tmp)}/{ORDERS_REL} is not inside a git checkout\n"
    assert not (tmp / ".prd-toolkit").exists()
    assert not (tmp / ORDERS_REL / ".prd-toolkit").exists()
