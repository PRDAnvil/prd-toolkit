"""error-replay, FR-081: check a red run, and the older forms as before (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import (  # noqa: F401
    CHECK, assert_left_as_it_was, assert_worktrees_same_and_scratch_empty, case, given, ledger_with,
)

RED_RUN = "fixed in <fix>, red run tests/test_total.py [integration]"
RESOLVE = "python ERROR resolve docs/prd/orders E-001"


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution=RED_RUN)
def test_red_run_in_range_passes(case):
    """@prd T-081.1"""
    res = case.run(CHECK)
    case.expect(res, exit=0, stdout="", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution="fixed in 0000000, red run tests/test_total.py [integration]")
def test_red_run_commit_not_an_ancestor(case):
    """@prd T-081.2"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: commit 0000000 is not an ancestor of HEAD\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RFA", "RL", "RK", "RE", resolution=RED_RUN)
def test_red_run_commit_changes_a_covered_path(case):
    """@prd T-081.3"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: commit <fix> changes src/importer.py, which area import covers\n",
                stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution="fixed in <fix>, red run tests/test_total.py [nosuch]")
def test_red_run_level_not_in_levels(case):
    """@prd T-081.4"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: nosuch is not a level of testing.md\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RX", "RK", "RE", resolution=RED_RUN)
def test_red_run_without_adoption_map(case):
    """@prd T-081.5"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: the PRD has no adoption map, so every path is covered\n",
                stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RK", "RE", resolution="fixed it in the end")
def test_none_of_the_four_forms(case):
    """@prd T-081.6"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: resolution is not one of the four forms\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_fix_with_a_tid_passes(case):
    """@prd T-081.7"""
    res = case.run(CHECK)
    case.expect(res, exit=0, stdout="", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution="T-099.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_tid_with_no_test_case(case):
    """@prd T-081.8"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: T-099.1 has no test case\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution="-, PRD 1.0.0, run 20261110T090000Z-all")
def test_environment_run_with_no_log(case):
    """@prd T-081.9"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stderr="")
    prefix = "errors.md: E-001: run 20261110T090000Z-all has no log in "
    assert prefix in res.stdout, res.detail()
    lines = res.stdout.splitlines()
    assert len(lines) == 1 and lines[0].startswith(prefix), res.detail()
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RK", "RE", resolution="not a defect: the total was read from the wrong report")
def test_not_a_defect_passes(case):
    """@prd T-081.10"""
    res = case.run(CHECK)
    case.expect(res, exit=0, stdout="", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RTP", "RF", "RO")
def test_resolve_with_a_tid_runs_nothing(case):
    """@prd T-081.11"""
    res = case.run(f"{RESOLVE} --t T-006.1 --version 1.0.0 --commit <fix>")
    case.expect(res, exit=0, stdout="E-001 resolved code bug\n", stderr="")
    case.expect_errors_md(ledger_with("ledger_open", "Resolution: T-006.1 [integration], PRD 1.0.0, fixed in <fix>"))


@given("R0", "RT", "RF", "RO")
def test_resolve_not_a_defect(case):
    """@prd T-081.12"""
    res = case.run(f"{RESOLVE} --not-a-defect 'the report was read wrong'")
    case.expect(res, exit=0, stdout="E-001 resolved code bug\n", stderr="")
    case.expect_errors_md(ledger_with("ledger_open", "Resolution: not a defect: the report was read wrong"))
    assert_worktrees_same_and_scratch_empty(res)


@given("R0", "RT", "RF", "RO")
def test_resolve_environment_run(case):
    """@prd T-081.13"""
    res = case.run(f"{RESOLVE} --t T-006.1 --version 1.0.0 --run 20261110T090000Z-all")
    case.expect(res, exit=0, stdout="E-001 resolved code bug\n", stderr="")
    case.expect_errors_md(ledger_with("ledger_open", "Resolution: T-006.1, PRD 1.0.0, run 20261110T090000Z-all"))
    assert_worktrees_same_and_scratch_empty(res)
