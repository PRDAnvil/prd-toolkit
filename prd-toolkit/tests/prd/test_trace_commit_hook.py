"""The commit-msg hook (FR-093): test-cases/trace.yaml T-093.1 to T-093.14.

Each case runs `python HOOK commit-msg docs/prd/orders msg.txt` in <tmp> after the steps its `setup:` lists
(testing.md, Setup steps: N0E and the trace steps), and compares exit, stdout and stderr byte for byte.
"""
from __future__ import annotations

from pathlib import Path

from trace_support import TM, git, git_out, given_steps, orders, run_hook, scratch, write_lines  # noqa: F401

ACCEPTED = "prd-toolkit: accepted forms: Refs: FR-001, E-002 | Refs: none (no behaviour change)\n"
NO_REFS = "prd-toolkit: no `Refs:` trailer (`Refs: FR-001`, or `Refs: none (no behaviour change)`)\n"
NOT_CONFIRMED = ("prd-toolkit: E-001 is not confirmed; a commit that changes code may cite it only after "
                 "prd_error.py confirm\n")
BAD_CHANGE_SET = "prd-toolkit: `Change-set: orders/CS-1` must be orders/CS-nnn\n"


def _step(name, fn):
    fn.__name__ = name
    return fn


def tm(*lines: str):
    """TM:t with t the lines given, each ending in a newline."""
    return _step("TM", lambda tmp: TM(tmp, list(lines)))


def commit_msg(tmp: Path):
    return run_hook(tmp, "commit-msg", "docs/prd/orders", "msg.txt")


def assert_result(r, exit_code: int, stderr: str) -> None:
    assert (r.exit, r.stdout, r.stderr) == (exit_code, "", stderr), r


@given_steps("N0E", "TB", "TX", tm("add app", "", "Change-set: orders/CS-1", "Refs: JIRA-1"))
def test_refs_problems_come_before_change_set_problems(scratch):
    """@prd T-093.1"""
    assert_result(commit_msg(scratch), 1,
                  "prd-toolkit: `JIRA-1` is not a PRD ID; give other keys their own trailer\n"
                  + BAD_CHANGE_SET + ACCEPTED)


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: FR-001"))
def test_a_good_message_inside_the_boundary_passes(scratch):
    """@prd T-093.2"""
    assert_result(commit_msg(scratch), 0, "")


@given_steps("N0E", "TB", "TX", tm("add app", "", "# Refs: FR-001"))
def test_a_comment_line_is_not_read(scratch):
    """@prd T-093.3"""
    assert_result(commit_msg(scratch), 1, NO_REFS + ACCEPTED)


def _merge_head(tmp: Path) -> None:
    """Write <tmp>/.git/MERGE_HEAD with the output of git rev-parse HEAD."""
    (tmp / ".git" / "MERGE_HEAD").write_bytes((git_out(tmp, "rev-parse", "HEAD") + "\n").encode("utf-8"))


@given_steps("N0E", "TB", "TX", _step("MERGE_HEAD", _merge_head), "TM:add app")
def test_a_merge_in_progress_is_allowed(scratch):
    """@prd T-093.4"""
    assert_result(commit_msg(scratch), 0, "")


@given_steps("N0E", "TE", "TB", "TX", tm("add app", "", "Refs: E-001"))
def test_an_unconfirmed_entry_is_refused_inside_the_boundary(scratch):
    """@prd T-093.5"""
    assert_result(commit_msg(scratch), 1, NOT_CONFIRMED + ACCEPTED)


@given_steps("N0E", "TEC", "TB", "TX", tm("add app", "", "Refs: E-001"))
def test_a_confirmed_entry_is_accepted(scratch):
    """@prd T-093.6"""
    assert_result(commit_msg(scratch), 0, "")


def _commit_app(tmp: Path) -> None:
    git(tmp, "commit", "-q", "-m", "app", "-m", "Refs: none (no behaviour change)")


@given_steps("N0E", "TB", "TX", _step("commit_app", _commit_app),
             _step("git_rm", lambda tmp: git(tmp, "rm", "-q", "src/app.py")), "TM:remove app")
def test_a_staged_deletion_counts(scratch):
    """@prd T-093.7"""
    assert_result(commit_msg(scratch), 1, NO_REFS + ACCEPTED)


@given_steps("N0E", "TB", "TX", _step("commit_app", _commit_app),
             _step("git_mv", lambda tmp: git(tmp, "mv", "src/app.py", "docs/prd/orders/app.md")), "TM:move app")
def test_both_paths_of_a_staged_rename_count(scratch):
    """@prd T-093.8"""
    assert_result(commit_msg(scratch), 1, NO_REFS + ACCEPTED)


def _add_lib(tmp: Path) -> None:
    write_lines(tmp / "lib" / "x.py", ["x = 1"])
    git(tmp, "add", "lib/x.py")


@given_steps("N0E", "TA:adopted", "TB", _step("add_lib", _add_lib), "TM:add lib")
def test_a_path_outside_the_adopted_globs_needs_no_refs(scratch):
    """@prd T-093.9"""
    assert_result(commit_msg(scratch), 0, "")


@given_steps("N0E", "TA:adopted", "TB", "TX", "TM:add app")
def test_a_path_inside_the_adopted_globs_needs_refs(scratch):
    """@prd T-093.10"""
    assert_result(commit_msg(scratch), 1, NO_REFS + ACCEPTED)


def _notes_and_vendored(tmp: Path) -> None:
    """Write <tmp>/docs/prd/orders/notes.md (`notes`) and <tmp>/.prd-toolkit/x.txt (`x`); git add -A."""
    write_lines(tmp / "docs" / "prd" / "orders" / "notes.md", ["notes"])
    write_lines(tmp / ".prd-toolkit" / "x.txt", ["x"])
    git(tmp, "add", "-A")


@given_steps("N0E", "TB", _step("notes_and_vendored", _notes_and_vendored), "TM:notes")
def test_no_path_inside_the_boundary_and_nothing_named_passes(scratch):
    """@prd T-093.11"""
    assert_result(commit_msg(scratch), 0, "")


def _vendored_only(tmp: Path) -> None:
    write_lines(tmp / ".prd-toolkit" / "x.txt", ["x"])
    git(tmp, "add", "-A")


@given_steps("N0E", "TE", "TB", _step("vendored_only", _vendored_only), tm("add x", "", "Refs: E-001"))
def test_an_unconfirmed_entry_is_refused_outside_the_boundary_and_the_prd_folder(scratch):
    """@prd T-093.12"""
    assert_result(commit_msg(scratch), 1, NOT_CONFIRMED + ACCEPTED)


def _notes_only(tmp: Path) -> None:
    write_lines(tmp / "docs" / "prd" / "orders" / "notes.md", ["notes"])
    git(tmp, "add", "-A")


@given_steps("N0E", "TE", "TB", _step("notes_only", _notes_only), tm("notes", "", "Refs: E-001"))
def test_a_prd_folder_only_commit_may_cite_an_unconfirmed_entry(scratch):
    """@prd T-093.13"""
    assert_result(commit_msg(scratch), 0, "")


@given_steps("N0E", "TB", _step("notes_only", _notes_only), tm("notes", "", "Change-set: orders/CS-1"))
def test_a_change_set_problem_is_refused_outside_the_boundary(scratch):
    """@prd T-093.14"""
    assert_result(commit_msg(scratch), 1, BAD_CHANGE_SET + ACCEPTED)
