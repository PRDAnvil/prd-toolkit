"""hooks-install: `prd_hooks.py uninstall` removes only the toolkit's own hooks (FR-112).

Every value comes from docs/prd/prd-toolkit/test-cases/hooks-install.yaml and the ACs it names.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from hooks_install_support import (
    N0E, ORDERS_REL, built, files_outside_pycache, given, hi_tmp, run, step_run, write_exec,
)

__all__ = ["built", "hi_tmp"]  # pytest fixtures, imported for use

UNINSTALL = f"python HOOKS uninstall {ORDERS_REL}"


class KnownFailure(Exception):
    """The known failure of a case's `symptom:` was seen (raised for a strict xfail with raises=KnownFailure)."""


def _setup_112_1(tmp: Path) -> None:
    """N0E; install; a pre-commit hook of the user's own (mode 0o755: a hook file)."""
    N0E(tmp)
    step_run(tmp, tmp, f"python HOOKS install {ORDERS_REL}")
    write_exec(tmp / ".git" / "hooks" / "pre-commit", "#!/bin/sh\necho mine\n")


@given(_setup_112_1)
def test_uninstall_removes_only_the_toolkit_hook(built):
    """@prd T-112.1"""
    tmp = built
    hooks = tmp / ".git" / "hooks"
    before = files_outside_pycache(tmp / ".prd-toolkit")

    r1 = run(tmp, tmp, UNINSTALL)
    assert r1.exit == 0, r1
    assert r1.stderr == ""
    assert r1.stdout.splitlines() == ["removed .git/hooks/commit-msg"], r1.stdout
    assert not (hooks / "commit-msg").exists()
    assert (hooks / "pre-commit").read_bytes() == b"#!/bin/sh\necho mine\n"
    assert files_outside_pycache(tmp / ".prd-toolkit") == before

    r2 = run(tmp, tmp, UNINSTALL)
    assert r2.exit == 0, r2
    assert r2.stdout == ""


def _setup_112_2(tmp: Path) -> None:
    """N0E; install; git config core.hooksPath .git/hooks."""
    N0E(tmp)
    step_run(tmp, tmp, f"python HOOKS install {ORDERS_REL}")
    step_run(tmp, tmp, "git config core.hooksPath .git/hooks")


@given(_setup_112_2)
def test_uninstall_where_hooks_path_is_set(built):
    """@prd T-112.2"""
    tmp = built
    hooks = tmp / ".git" / "hooks"
    r = run(tmp, tmp, UNINSTALL)
    if (r.stdout.splitlines() == ["core.hooksPath is set to .git/hooks; removed nothing"]
            and (hooks / "commit-msg").exists() and (hooks / "pre-commit").exists()):
        raise KnownFailure("E-044: core.hooksPath is set to .git/hooks; removed nothing")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert r.stdout.splitlines() == ["removed .git/hooks/commit-msg", "removed .git/hooks/pre-commit"], r.stdout
    assert not (hooks / "commit-msg").exists()
    assert not (hooks / "pre-commit").exists()
