"""Characterization tests of `prd_error.py check` on a CI run (test-cases/error-replay.yaml, AC-081.9).

Every input and expected value comes from the case it cites; the steps and names from testing.md (Setup steps,
the error-replay paragraph and its table) through error_replay_support.py.
"""
from __future__ import annotations

from error_replay_support import CHECK, assert_left_as_it_was, case, given  # noqa: F401  (case is the fixture)


@given("R0", "RK", "REC", resolution="-, PRD 1.0.0, CI run https://ci.example.com/orders/runs/42")
def test_check_ci_run_environment_passes(case):
    """@prd T-081.23"""
    res = case.run(CHECK)
    case.expect(res, exit=0, stdout="", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RK", "RE", resolution="-, PRD 2.0.0, CI run https://ci.example.com/orders/runs/42")
def test_check_ci_run_code_bug_above_version(case):
    """@prd T-081.24"""
    res = case.run(CHECK)
    case.expect(res, exit=1,
                stdout="errors.md: E-001: a CI run resolves an environment or standard entry only\n"
                       "errors.md: E-001: PRD 2.0.0 is above the PRD version 1.0.0\n",
                stderr="")
    assert_left_as_it_was(res)


@given("R0", "RK", "REC", resolution="-, PRD 0.9.0, CI run https://ci.example.com/orders/runs/42")
def test_check_ci_run_no_changelog_row(case):
    """@prd T-081.25"""
    res = case.run(CHECK)
    case.expect(res, exit=1, stdout="errors.md: E-001: PRD 0.9.0 has no changelog row\n", stderr="")
    assert_left_as_it_was(res)
