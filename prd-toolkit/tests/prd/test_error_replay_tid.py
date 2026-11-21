"""error-replay, FR-076: replay an entry resolved with a T-id (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, given  # noqa: F401

FIX = "T-006.1 [integration], PRD 1.0.0, fixed in <fix>"
HOLDS = "E-001: T-006.1 fails on <fix>^ and passes on <fix>\n"


@given("R0", "RT", "RF", "RL", "RE", resolution=FIX)
def test_only_cited_files_run(case):
    """@prd T-076.1"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout=HOLDS, stderr="")
    assert_left_as_it_was(res)


@given("R0", "RF", "RT", "RL", "RE", resolution=FIX)
def test_test_committed_after_its_fix(case):
    """@prd T-076.2"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout=HOLDS, stderr="")
    assert_left_as_it_was(res)


@given("R0", "RTS", "RF", "RE", resolution=FIX)
def test_path_with_a_space_is_one_argument(case):
    """@prd T-076.3"""
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=0, stdout=HOLDS, stderr="")
    assert_left_as_it_was(run_1)
    run_2 = case.run(REPLAY + " --json")
    case.expect(run_2, exit=0, stderr="")
    case.expect_json_at(run_2, {
        "outcome": "holds",
        "runs.0.argument": "tests/test total.py",
        "runs.1.argument": "tests/test total.py",
    })
    assert_left_as_it_was(run_2)


@given("R0", "RT", "RM", "RE", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <merge>")
def test_merge_fix_uses_first_parent(case):
    """@prd T-076.4"""
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=0, stdout="E-001: T-006.1 fails on <merge>^ and passes on <merge>\n", stderr="")
    assert_left_as_it_was(run_1)
    run_2 = case.run(REPLAY + " --json")
    case.expect(run_2, exit=0, stderr="")
    case.expect_json_at(run_2, {
        "runs.0.commit": "FULL(merge^)",
        "runs.0.when": "before",
        "runs.1.commit": "FULL(merge)",
        "runs.1.when": "after",
    })
    assert_left_as_it_was(run_2)


@given("R0", "RTP", "RF", "RE", resolution=FIX)
def test_passes_on_the_bug(case):
    """@prd T-076.5"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: T-006.1 passes on <fix>^; <fix> did not turn it green\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RS", "RE", resolution=FIX)
def test_fails_on_the_fix(case):
    """@prd T-076.6"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: T-006.1 fails on <fix>: tests/test_total.py\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RE", "RN", resolution=FIX)
def test_harness_that_needs_the_checkout(case):
    """@prd T-076.7"""
    # run_1: the One test command RN names passes in the repository's own checkout, which holds .ready.
    run_1 = case.run("python3 tools/needs.py tests/test_total.py")
    case.expect(run_1, exit=0)
    # run_2: in a fresh clone .ready is absent, so the command exits 3 on both trees and the proof does not hold.
    run_2 = case.run(REPLAY)
    case.expect(run_2, exit=1, stdout="E-001: T-006.1 fails on <fix>: tests/test_total.py\n", stderr="")
    assert_left_as_it_was(run_2)


@given("R0", "RT", "RF", "RE", resolution="T-007.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_cited_by_no_test(case):
    """@prd T-076.8"""
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=1, stdout="E-001: T-007.1 is cited by no test in HEAD7\n", stderr="")
    assert_left_as_it_was(run_1)
    run_2 = case.run(REPLAY + " --json")
    case.expect(run_2, exit=1, stderr="")
    case.expect_json(run_2, {
        "interface": 1,
        "kind": "error-replay",
        "entry": "E-001",
        "outcome": "findings",
        "subject": "T-007.1",
        "reason": None,
        "findings": ["E-001: T-007.1 is cited by no test in HEAD7"],
        "runs": [],
    })
    assert_left_as_it_was(run_2)


@given("R0", "RT", "RF", "RL", "REU", "RW", resolution=FIX)
def test_uncommitted_resolution_takes_head_tests(case):
    """@prd T-076.9"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout=HOLDS, stderr="")
    assert_left_as_it_was(res)
