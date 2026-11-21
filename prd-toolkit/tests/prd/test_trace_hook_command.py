"""The git hook command's refusals and its work tree (FR-095): test-cases/trace.yaml T-095.1 to T-095.5."""
from __future__ import annotations

from pathlib import Path

from trace_support import (  # noqa: F401
    TR, git, given_steps, orders, replace_line, run_hook, scratch, standards_row, write_lines,
)

CWD_ROW = standards_row("`python3 -c \"import os; open('cwd.log','w').write(os.getcwd())\"`")


def _step(name, fn):
    fn.__name__ = name
    return fn


def test_no_hook_name_prints_the_usage(tmp_path):
    """@prd T-095.1"""
    r = run_hook(tmp_path.resolve())
    assert (r.exit, r.stdout) == (2, ""), r
    assert r.stderr.splitlines()[0].startswith("usage: prd_git_hook.py"), r.stderr


def test_a_folder_with_no_prd_md(tmp_path):
    """@prd T-095.2"""
    tmp = tmp_path.resolve()
    (tmp / "nothing").mkdir()
    r = run_hook(tmp, "pre-commit", "nothing")
    assert (r.exit, r.stdout, r.stderr) == (2, "", f"prd-toolkit: {tmp}/nothing: no prd.md\n"), r


def _map_in_prd_md(tmp: Path) -> None:
    """In prd.md line 57, `Not applicable: new project.`, becomes the three table lines; no adoption.md is written."""
    replace_line(orders(tmp) / "prd.md", 57,
                 ["| Area | State | Boundary |", "|---|---|---|", "| import | adopted | `src/**` |"],
                 old="Not applicable: new project.")


@given_steps("N0E", _step("map_in_prd_md", _map_in_prd_md), "TM:add app")
def test_a_section_8_table_with_no_adoption_md(scratch):
    """@prd T-095.3"""
    r = run_hook(scratch, "commit-msg", "docs/prd/orders", "msg.txt")
    assert r.exit == 2, r
    assert r.stdout == "", r
    assert r.stderr == (
        f"prd-toolkit: {scratch}/docs/prd/orders/prd.md: section 8: the adoption map moved to adoption.md in "
        "prd-toolkit 0.3; move the table there and leave \"See adoption.md.\"\n"
    ), r


def _tr_cwd(tmp: Path) -> None:
    TR(tmp, [CWD_ROW])


def _worktree(tmp: Path) -> None:
    git(tmp, "worktree", "add", "-q", str(tmp / "wt"), "-b", "wt")
    write_lines(tmp / "wt" / "src" / "app.py", ["x = 1"])
    git(tmp, "-C", str(tmp / "wt"), "add", "src/app.py")


@given_steps("N0E", _step("TR", _tr_cwd), "TB", _step("worktree", _worktree))
def test_an_absolute_git_dir_in_a_linked_worktree(scratch):
    """@prd T-095.4"""
    wt = scratch / "wt"
    r = run_hook(wt, "pre-commit", "docs/prd/orders", env={"GIT_DIR": str(scratch / ".git" / "worktrees" / "wt")})
    assert (r.exit, r.stdout, r.stderr) == (0, "", ""), r
    assert (wt / "cwd.log").read_text(encoding="utf-8") == str(wt)
    assert not (wt / "docs" / "prd" / "orders" / "cwd.log").exists()


@given_steps("N0E", _step("TR", _tr_cwd), "TB", "TX")
def test_a_relative_git_dir_in_the_main_checkout(scratch):
    """@prd T-095.5"""
    r = run_hook(scratch, "pre-commit", "docs/prd/orders", env={"GIT_DIR": ".git"})
    assert (r.exit, r.stdout, r.stderr) == (0, "", ""), r
    assert (scratch / "cwd.log").read_text(encoding="utf-8") == str(scratch)
    assert not (scratch / "docs" / "prd" / "orders" / "cwd.log").exists()
