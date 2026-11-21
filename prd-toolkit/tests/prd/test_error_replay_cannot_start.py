"""error-replay, AC-078.14 and AC-080.9: a One test program that cannot start (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, files, given, json_at  # noqa: F401

FIX = "T-006.1 [integration], PRD 1.0.0, fixed in <fix>"
RED_RUN = "fixed in <fix>, red run tests/test_total.py [integration]"


@given("R0", "RT", "RF", "RA", "RE", resolution=FIX)
def test_replay_prints_cannot_start_for_each_run(case):
    """@prd T-078.23"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stderr="")
    case.expect_lines(res.stdout, [
        "E-001: tools/absent cannot start on <fix>^",
        "E-001: tools/absent cannot start on <fix>",
    ])
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RA", "RE", resolution=RED_RUN)
def test_replay_json_records_cannot_start_as_exit_null(case):
    """@prd T-078.24"""
    res = case.run(REPLAY + " --json")
    case.expect(res, exit=1, stderr="")
    doc = case.expect_json_at(res, {
        "outcome": "findings",
        "subject": "tests/test_total.py",
        "findings": ["E-001: tools/absent cannot start on <fix>^", "E-001: tools/absent cannot start on <fix>"],
        "runs.0.commit": "FULL(fix^)",
        "runs.0.when": "before",
        "runs.0.argument": "tests/test_total.py",
        "runs.0.exit": None,
        "runs.0.timed_out": False,
        "runs.1.commit": "FULL(fix)",
        "runs.1.when": "after",
        "runs.1.argument": "tests/test_total.py",
        "runs.1.exit": None,
        "runs.1.timed_out": False,
    })
    runs = json_at(doc, "runs")
    assert isinstance(runs, list) and len(runs) == 2, doc
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RA", "RO")
def test_resolve_red_run_refuses_a_program_that_cannot_start(case):
    """@prd T-080.16"""
    res = case.run("python ERROR resolve docs/prd/orders E-001 --commit <fix> "
                   "--red-run tests/test_total.py --level integration")
    case.expect(res, exit=1, stdout="")
    case.expect_lines(res.stderr, [
        "refused: E-001: tools/absent cannot start on <fix>^",
        "refused: E-001: tools/absent cannot start on <fix>",
    ])
    assert case.errors_md() == files("ledger_open").encode("utf-8"), case.errors_md().decode("utf-8")
    assert_left_as_it_was(res)
