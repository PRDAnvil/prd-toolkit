"""lint-registries: FR-139, the Environments tables of the runbook-env rule (test-cases/lint-registries.yaml)."""
from lint_registries_support import (  # noqa: F401  (case is a pytest fixture)
    S0, assert_exit, assert_stderr, assert_stdout_contains_line, assert_stdout_exact_lines,
    assert_stdout_not_contains, case, delete_file, insert_after, replace, steps,
)

OPS = "docs/prd/orders/operations.md"


@steps(S0, insert_after("operations.md", 10, "| qa | https://qa.example.com | no |"))
def test_environment_missing_from_testing(case):
    """@prd T-139.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:11: runbook-env: environment 'qa' is in operations.md but not in testing.md Environments"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 9, "| staging | https://orders-staging.example.com | maybe |"))
def test_production_cell_not_yes_or_no(case):
    """@prd T-139.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:9: runbook-env: environment 'staging': Production 'maybe' is not yes or no"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 5, "| Environment | URL | Live |"))
def test_no_production_column(case):
    """@prd T-139.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, f"{OPS}:7: runbook-env: operations.md Environments has no Production column")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 10, "| production | https://orders.example.com | no |"))
def test_no_production_yes(case):
    """@prd T-139.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, f"{OPS}:7: runbook-env: operations.md Environments: no environment has Production yes")
    assert_stderr(r, "")


@steps(S0, delete_file("operations.md"))
def test_no_operations_file_env(case):
    """@prd T-139.5"""
    r = case.lint()
    assert_stdout_not_contains(r, "runbook-env")
    assert_stderr(r, "")
