"""error-replay, FR-075: the One test column of the Levels table (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, given  # noqa: F401

RED_RUN = "fixed in <fix>, red run tests/test_total.py [integration]"


@given("R0", "RT", "RF", "RL", "RQ", "RE", resolution=RED_RUN)
def test_header_in_any_case_and_quoted_cell(case):
    """@prd T-075.1"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="E-001: tests/test_total.py fails on <fix>^ and passes on <fix>\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RC", "RE", resolution=RED_RUN)
def test_no_column_no_one_test_command(case):
    """@prd T-075.2"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: integration has no One test command\n", stderr="")
    assert_left_as_it_was(res)


MALFORMED = [
    "docs/prd/orders/testing.md:7: runbook-tests: level 'unit': One test '`cd tests`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:8: runbook-tests: level 'integration': One test 'python3 tools/one.py' is not one simple command in backticks",
    "docs/prd/orders/testing.md:9: runbook-tests: level 'judged': One test '`TEST_ENV=ci python3 tools/one.py`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:10: runbook-tests: level 'slow': One test '`python3 tools/one.py ~/x`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:11: runbook-tests: level 'system': One test '`python3 tools/one.py; true`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:12: runbook-tests: level 'quote': One test '`python3 'tools/one.py`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:13: runbook-tests: level 'spans': One test '`python3` `tools/one.py`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:14: runbook-tests: level 'pipe': One test '`python3 tools/one.py | cat`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:15: runbook-tests: level 'dollar': One test '`python3 tools/one.py $X`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:16: runbook-tests: level 'brace': One test '`python3 tools/one.py {a}`' is not one simple command in backticks",
    "docs/prd/orders/testing.md:17: runbook-tests: level 'and': One test '`python3 tools/one.py && true`' is not one simple command in backticks",
]


@given("R0", "RB")
def test_lint_reports_each_malformed_cell(case):
    """@prd T-075.3"""
    res = case.run("python LINT docs/prd/orders")
    case.expect(res, exit=1, stderr="")
    lines = res.stdout.splitlines()
    at = 0
    for want in MALFORMED:  # stdout_lines_in_this_relative_order
        assert want in lines[at:], f"not found after line {at}: {want}\n{res.stdout}"
        at = lines.index(want, at) + 1
    others = [line for line in lines if ": runbook-tests: " in line and line not in MALFORMED]
    assert others == [], f"runbook-tests lines beyond the eleven: {others}"


@given("R0", "R0 in <tmp>/b", "RC in <tmp>/b")
def test_lint_same_with_and_without_the_column(case):
    """@prd T-075.4"""
    run_1 = case.run("python LINT docs/prd/orders", cwd=case.repo)
    run_2 = case.run("python LINT docs/prd/orders", cwd=case.tmp / "b")
    assert run_1.exit == run_2.exit, f"{run_1.detail()}\n===\n{run_2.detail()}"
    assert run_1.stdout == run_2.stdout, f"{run_1.detail()}\n===\n{run_2.detail()}"
    assert run_1.stderr == run_2.stderr, f"{run_1.detail()}\n===\n{run_2.detail()}"


DESCRIPTION = (
    "Checks that each level a runbook tests step names is in testing.md Levels with Gate deploy and a Harness "
    "command, that each Timeout cell is a whole number of seconds of at least 1, and that each One test cell is "
    "one simple command in backticks. Add or fix the level's row, or name a deploy-gate level."
)


@given()
def test_help_describes_the_column(case):
    """@prd T-075.5"""
    res = case.run("python HELP --rule runbook-tests", cwd=case.tmp)
    case.expect(res, exit=0, stderr="")
    lines = res.stdout.splitlines()
    assert lines[:1] == ["runbook-tests (error)"], res.detail()
    assert len(lines) >= 2 and lines[1] == DESCRIPTION, res.detail()
