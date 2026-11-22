"""lint-registries characterization tests: runbook-env names, production-gate, runbook-tests and
drift-rows (test-cases/lint-registries.yaml, T-140 to T-143)."""
from __future__ import annotations

import pytest

from lint_registries_support import (  # noqa: F401  (case is a fixture)
    S0, assert_exit, assert_stderr, assert_stdout, assert_stdout_contains_line,
    assert_stdout_exact_lines, assert_stdout_not_contains, case, delete_file, insert_after, replace,
    steps, text,
)


class KnownFailure(Exception):
    """The symptom a known-failing case's `symptom:` names was seen."""


@steps(S0, replace("operations.md", 14, "1. Deploy to staging (actor: agent) (env: qa)"))
def test_step_env_not_in_operations(case):
    """@prd T-140.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/operations.md:14: runbook-env: step 1: environment 'qa' is not in operations.md Environments"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 14, "1. Deploy to staging (actor: agent) (env: Staging)"))
def test_step_env_case_hint(case):
    """@prd T-140.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/operations.md:14: runbook-env: step 1: environment 'Staging' is not in operations.md Environments (did you mean 'staging'?)"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 34, "| prod | 1.0.0 | 3f2c1a9 | 2026-11-02 | 20261102T103000Z-production |"))
def test_deployed_row_env_unknown(case):
    """@prd T-140.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:34: runbook-env: Deployed row: environment 'prod' is not in operations.md Environments")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 40, "| Production | version | `curl -fsS https://orders.example.com/version` |"))
def test_drift_row_env_case_hint(case):
    """@prd T-140.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:40: runbook-env: Drift row: environment 'Production' is not in operations.md Environments (did you mean 'production'?)")
    assert_stderr(r, "")


@steps(S0,
       insert_after("operations.md", 10, "| qa | https://qa.example.com | no |"),
       replace("operations.md", 14, "1. Deploy to staging (actor: agent) (env: qa)"))
def test_step_env_not_in_testing(case):
    """@prd T-140.5"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [
        "docs/prd/orders/operations.md:11: runbook-env: environment 'qa' is in operations.md but not in testing.md Environments",
        "docs/prd/orders/operations.md:15: runbook-env: step 1: environment 'qa' is not in testing.md Environments",
    ])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 20, "3. Approve production (actor: agent) (env: production)"))
def test_production_step_without_human(case):
    """@prd T-141.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:20: production-gate: step 3 deploys production with no human step at or just before it")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 20, "3. Approve production (actor: human) (env: staging)"))
def test_human_step_on_staging_gates_production(case):
    """@prd T-141.2"""
    r = case.lint()
    assert_stdout_not_contains(r, "production-gate")
    assert_stderr(r, "")


@steps(S0)
def test_first_production_step_is_human(case):
    """@prd T-141.3"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 19, "   Run: tests system, nope"))
def test_tests_level_not_in_levels(case):
    """@prd T-142.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/operations.md:19: runbook-tests: step 2: level 'nope' is not in testing.md Levels"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 19, "   Run: tests system, unit"))
def test_tests_level_gate_build(case):
    """@prd T-142.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/operations.md:19: runbook-tests: step 2: level 'unit' has Gate build; a tests step runs deploy-gate levels"])
    assert_stderr(r, "")


@steps(S0, replace("testing.md", 11, "| e2e | `pytest tests/e2e` | staging | |"))
def test_tests_level_gate_blank(case):
    """@prd T-142.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:19: runbook-tests: step 2: level 'e2e' has Gate none; a tests step runs deploy-gate levels")
    assert_stderr(r, "")


@steps(S0, replace("testing.md", 11, "| e2e | | staging | deploy |"))
def test_tests_level_no_harness_command(case):
    """@prd T-142.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:19: runbook-tests: step 2: level 'e2e' has no Harness command")
    assert_stderr(r, "")


@steps(S0, lambda c: c.replace("testing.md", 11, text("e2e_marker_row")))
def test_tests_level_marker_harness_command(case):
    """@prd T-142.5"""
    r = case.lint()
    assert_stdout_not_contains(r, "runbook-tests")
    assert_stderr(r, "")


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps(S0, replace("operations.md", 40, "| production | schema | `true` |"))
def test_drift_check_schema(case):
    """@prd T-143.1 known-failing E-053"""
    r = case.lint()
    symptom = "docs/prd/orders/operations.md:40: drift-rows: check 'schema': schema drift arrives in prd-toolkit 0.6"
    if symptom in r.lines:
        raise KnownFailure(symptom)
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:40: drift-rows: check 'schema' is not version or config")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 40, "| production | size | `true` |"))
def test_drift_check_unknown(case):
    """@prd T-143.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:40: drift-rows: check 'size' is not version or config")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 40, "| production | Version | `curl -fsS https://orders.example.com/version` |"))
def test_drift_check_case_sensitive(case):
    """@prd T-143.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:40: drift-rows: check 'Version' is not version or config")
    assert_stderr(r, "")


@steps(S0, delete_file("contracts/config.yaml"))
def test_drift_config_needs_contract(case):
    """@prd T-143.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/operations.md:41: drift-rows: a config drift row needs contracts/config.yaml")
    assert_stderr(r, "")
