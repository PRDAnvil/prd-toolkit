"""Characterization test of `prd_error.py replay` on a CI run (test-cases/error-replay.yaml, AC-078.3).

Every input and expected value comes from the case it cites; the steps and names from testing.md (Setup steps,
the error-replay paragraph and its table) through error_replay_support.py.
"""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, given  # noqa: F401  (case is the fixture)


@given("R0", "RT", "RF", "REC", resolution="-, PRD 1.0.0, CI run https://ci.example.com/orders/runs/42")
def test_replay_skips_ci_run(case):
    """@prd T-078.25"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: resolved by an environment run\n", stderr="")
    assert_left_as_it_was(res)
