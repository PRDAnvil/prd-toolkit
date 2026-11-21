"""error-replay, FR-077: replay an entry resolved with a red run (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, json_at  # noqa: F401

RED_RUN = "fixed in <fix>, red run tests/test_total.py [integration]"


@given("R0", "RTD", "RF", "RE", resolution="fixed in <fix>, red run tests/a$b;c.py [integration]")
def test_test_id_reaches_the_command_as_plain_text(case):
    """@prd T-077.1"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="E-001: tests/a$b;c.py fails on <fix>^ and passes on <fix>\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RF", "RT", "RE", resolution=RED_RUN)
def test_test_committed_after_the_fix_fails_both(case):
    """@prd T-077.2"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: tests/test_total.py fails on <fix>: tests/test_total.py\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RE", resolution=RED_RUN)
def test_red_run_holds(case):
    """@prd T-077.3"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="E-001: tests/test_total.py fails on <fix>^ and passes on <fix>\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RTP", "RF", "RE", resolution=RED_RUN)
def test_red_run_passes_on_the_bug(case):
    """@prd T-077.4"""
    res = case.run(REPLAY)
    case.expect(res, exit=1,
                stdout="E-001: tests/test_total.py passes on <fix>^; <fix> did not turn it green\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RS", "RE", resolution=RED_RUN)
def test_red_run_fails_on_the_fix(case):
    """@prd T-077.5"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: tests/test_total.py fails on <fix>: tests/test_total.py\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RIW", "RE", resolution=RED_RUN)
def test_one_test_program_finds_a_git_checkout_in_each_clone(case):
    """@prd T-077.6"""
    res = case.run(REPLAY + " --json")
    case.expect(res, exit=1, stderr="")
    doc = case.expect_json_at(res, {
        "outcome": "findings",
        "findings": ["E-001: tests/test_total.py passes on <fix>^; <fix> did not turn it green"],
        "runs.0.commit": "FULL(fix^)",
        "runs.0.when": "before",
        "runs.0.exit": 0,
        "runs.1.commit": "FULL(fix)",
        "runs.1.when": "after",
        "runs.1.exit": 0,
    })
    runs = json_at(doc, "runs")
    assert isinstance(runs, list) and len(runs) == 2, doc
    assert_left_as_it_was(res)
