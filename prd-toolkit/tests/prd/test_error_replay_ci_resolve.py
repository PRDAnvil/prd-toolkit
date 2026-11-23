"""Characterization tests of `prd_error.py resolve --ci-run` (test-cases/error-replay.yaml, AC-081.6 to AC-081.8).

Every input and expected value comes from the case it cites; the steps and names from testing.md (Setup steps,
the error-replay paragraph and its table) through error_replay_support.py.
"""
from __future__ import annotations

from error_replay_support import (  # noqa: F401  (case is the fixture)
    assert_worktrees_same_and_scratch_empty,
    case,
    files,
    given,
    ledger_with,
)

ENV_MISUSE = ("prd_error: --ci-run takes --version, and no --t, --commit, --run, --red-run, --level or "
              "--not-a-defect\n")
URL_BAD = "prd_error: --ci-run must start with http:// or https:// and hold no white space; got '{}'\n"


@given("R0", "RV")
def test_resolve_ci_run_environment(case):
    """@prd T-081.15"""
    res = case.run("python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42 "
                   "--version 1.0.0")
    case.expect(res, exit=0, stdout="E-001 resolved environment\n", stderr="")
    case.expect_errors_md(ledger_with(
        "ledger_env", "Resolution: -, PRD 1.0.0, CI run https://ci.example.com/orders/runs/42"))
    assert_worktrees_same_and_scratch_empty(res)


@given("R0", "RSD")
def test_resolve_ci_run_standard_http_query(case):
    """@prd T-081.16"""
    res = case.run("python ERROR resolve docs/prd/orders E-001 --ci-run http://ci.example.com/runs/7?attempt=2 "
                   "--version 1.0.0")
    case.expect(res, exit=0, stdout="E-001 resolved standard\n", stderr="")
    case.expect_errors_md(ledger_with(
        "ledger_standard", "Resolution: -, PRD 1.0.0, CI run http://ci.example.com/runs/7?attempt=2"))


@given("R0", "RV")
def test_resolve_ci_run_misused_flags(case):
    """@prd T-081.17"""
    runs = [
        "python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42 --version 1.0.0 "
        "--t T-006.1",
        "python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42 --version 1.0.0 "
        "--run 20261110T090000Z-all",
        "python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42",
    ]
    want = files("ledger_env").encode("utf-8")
    for command in runs:
        res = case.run(command)
        case.expect(res, exit=2, stdout="", stderr=ENV_MISUSE)
        assert case.errors_md() == want, f"errors.md changed after: {command}"


@given("R0", "RV")
def test_resolve_ci_run_bad_url(case):
    """@prd T-081.18"""
    want = files("ledger_env").encode("utf-8")
    runs = [
        ("python ERROR resolve docs/prd/orders E-001 --ci-run ftp://ci.example.com/runs/42 --version 1.0.0",
         URL_BAD.format("ftp://ci.example.com/runs/42")),
        ("python ERROR resolve docs/prd/orders E-001 --ci-run 'https://ci.example.com/runs/4 2' --version 1.0.0",
         URL_BAD.format("https://ci.example.com/runs/4 2")),
    ]
    for command, stderr in runs:
        res = case.run(command)
        case.expect(res, exit=2, stdout="", stderr=stderr)
        assert case.errors_md() == want, f"errors.md changed after: {command}"


@given("R0", "RV")
def test_resolve_ci_run_bad_version(case):
    """@prd T-081.19"""
    res = case.run("python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42 "
                   "--version 1.0")
    case.expect(res, exit=2, stdout="", stderr="prd_error: version must be X.Y.Z; got '1.0'\n")
    assert case.errors_md() == files("ledger_env").encode("utf-8")


@given("R0", "RO")
def test_resolve_ci_run_code_bug_and_no_entry(case):
    """@prd T-081.20"""
    want = files("ledger_open").encode("utf-8")
    runs = [
        ("python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42 --version 1.0.0",
         "refused: E-001 is classed code bug; a CI run resolves an environment or standard entry only\n"),
        ("python ERROR resolve docs/prd/orders E-009 --ci-run https://ci.example.com/orders/runs/42 --version 1.0.0",
         "refused: E-009 is not an entry\n"),
    ]
    for command, stderr in runs:
        res = case.run(command)
        case.expect(res, exit=1, stdout="", stderr=stderr)
        assert case.errors_md() == want, f"errors.md changed after: {command}"


@given("R0", "RP")
def test_resolve_ci_run_not_confirmed(case):
    """@prd T-081.21"""
    res = case.run("python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/42 "
                   "--version 1.0.0")
    case.expect(res, exit=1, stdout="", stderr="refused: E-001 is not confirmed\n")
    assert case.errors_md() == files("ledger_proposed").encode("utf-8")


@given("R0", "REC", resolution="-, PRD 1.0.0, CI run https://ci.example.com/orders/runs/42")
def test_resolve_ci_run_already_resolved(case):
    """@prd T-081.22"""
    before = case.errors_md()
    res = case.run("python ERROR resolve docs/prd/orders E-001 --ci-run https://ci.example.com/orders/runs/43 "
                   "--version 1.0.0")
    case.expect(res, exit=1, stdout="", stderr="refused: E-001 is already resolved\n")
    assert case.errors_md() == before
