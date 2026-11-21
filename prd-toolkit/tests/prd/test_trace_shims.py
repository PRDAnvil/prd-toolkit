"""The hook shims (FR-096): test-cases/trace.yaml T-096.1 to T-096.7.

A shim is <repo>/prd-toolkit/templates/hooks/<h> with `{{hook}}` and `{{prd}}` filled (step SH:h,p); each case runs
it with `sh` (or `/bin/sh`), or through `git commit`, with no shell of the test's own.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from trace_support import (  # noqa: F401
    RUN_TIMEOUT, TEMPLATES, SetupError, filled_template, git_out, given_steps, run_command, scratch,
    subprocess_env, write_lines,
)

LINE_2 = "# prd-toolkit hook: written by prd_hooks.py install; removed by prd_hooks.py uninstall"
SKIPPED = "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped\n"


def _step(name, fn):
    fn.__name__ = name
    return fn


def _outside_git(tmp: Path) -> None:
    """Run git rev-parse --show-toplevel in <tmp>; end the test as an error when it exits 0; then write the shim."""
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=tmp, env=subprocess_env(),
                          capture_output=True, timeout=RUN_TIMEOUT)
    if proc.returncode == 0:
        raise SetupError(f"{tmp} lies inside a git checkout: {proc.stdout.decode('utf-8', 'replace').strip()}")
    shim = tmp / "x" / "commit-msg"
    shim.parent.mkdir(parents=True, exist_ok=True)
    shim.write_bytes(filled_template("commit-msg", "docs/prd/orders").encode("utf-8"))
    write_lines(tmp / "x" / "msg.txt", ["add"])


@given_steps(_step("outside_git", _outside_git))
def test_a_shim_outside_every_work_tree_exits_1(scratch):
    """@prd T-096.1"""
    r = run_command(scratch / "x", "sh commit-msg msg.txt")
    assert (r.exit, r.stdout) == (1, ""), r


def _empty_hook_script(tmp: Path) -> None:
    path = tmp / ".prd-toolkit" / "prd_git_hook.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


@given_steps("N0E", _step("empty_prd_git_hook", _empty_hook_script), "SH:pre-commit,docs/prd/orders")
def test_a_copy_without_the_launcher_is_skipped(scratch):
    """@prd T-096.2"""
    r = run_command(scratch, "sh .git/hooks/pre-commit")
    assert (r.exit, r.stdout, r.stderr) == (
        0, "", "prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped\n"), r


@given_steps("N0E", "SH:pre-commit,docs/prd/orders")
def test_no_vendored_copy_is_skipped(scratch):
    """@prd T-096.3"""
    r = run_command(scratch, "sh .git/hooks/pre-commit")
    assert (r.exit, r.stdout, r.stderr) == (0, "", SKIPPED), r


@given_steps("N0E", "TV", "SH:pre-commit,docs/prd/missing")
def test_no_prd_folder_is_skipped(scratch):
    """@prd T-096.4"""
    r = run_command(scratch, "sh .git/hooks/pre-commit")
    assert (r.exit, r.stdout, r.stderr) == (0, "", SKIPPED), r


def _git_only_bin(tmp: Path) -> None:
    found = shutil.which("git")
    if found is None:
        raise SetupError("no git on the runner's PATH")
    (tmp / "bin").mkdir()
    os.symlink(os.path.realpath(found), tmp / "bin" / "git")


@given_steps("N0E", "TV", "SH:pre-commit,docs/prd/orders", _step("git_only_bin", _git_only_bin))
def test_no_uv_on_path_blocks(scratch):
    """@prd T-096.5"""
    r = run_command(scratch, "/bin/sh .git/hooks/pre-commit", env={"PATH": str(scratch / "bin")})
    assert (r.exit, r.stdout, r.stderr) == (1, "", "prd-toolkit: uv is not on PATH; install uv to run this hook\n"), r


def _hooks_path(tmp: Path) -> None:
    git_out(tmp, "config", "core.hooksPath", ".git/hooks")


@given_steps("N0E", "TV", "TB", _step("hooks_path", _hooks_path), "SH:commit-msg,docs/prd/orders", "TX")
def test_the_commit_msg_shim_runs_the_launcher_and_passes_its_exit(scratch):
    """@prd T-096.6"""
    r1 = run_command(scratch, 'git commit -q -m "add app"')
    assert r1.exit == 1, r1
    assert ("prd-toolkit: no `Refs:` trailer (`Refs: FR-001`, or `Refs: none (no behaviour change)`)"
            in r1.stderr.splitlines()), r1.stderr
    assert git_out(scratch, "rev-list", "--count", "HEAD") == "1"
    r2 = run_command(scratch, 'git commit -q -m "add app" -m "Refs: FR-001"')
    assert r2.exit == 0, r2
    assert git_out(scratch, "rev-list", "--count", "HEAD") == "2"


def test_each_template_holds_the_toolkit_header_on_line_2():
    """@prd T-096.7"""
    for h in ("commit-msg", "pre-commit"):
        lines = (TEMPLATES / h).read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 2 and lines[1] == LINE_2, (h, lines[:2])
