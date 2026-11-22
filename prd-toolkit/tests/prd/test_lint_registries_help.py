"""lint-registries characterization tests: the help text of each rule of the area
(test-cases/lint-registries.yaml, T-148)."""
from __future__ import annotations

from lint_registries_support import Result, assert_exit, assert_stderr, case  # noqa: F401


def first_line(r: Result) -> str:
    assert r.lines, r.describe()
    return r.lines[0]


def second_line(r: Result) -> str:
    assert len(r.lines) >= 2, r.describe()
    return r.lines[1]


def test_rule_titles(case):
    """@prd T-148.1"""
    for rule in ("registries", "runbook-steps", "runbook-env", "production-gate", "drift-rows",
                 "error-entries"):
        r = case.help("--rule", rule)
        assert_exit(r, 0)
        assert first_line(r) == f"{rule} (error)", r.describe()
        assert_stderr(r, "")


def _second(case, rule: str, expected: str) -> None:
    r = case.help("--rule", rule)
    assert_exit(r, 0)
    assert second_line(r) == expected, r.describe()
    assert_stderr(r, "")


def test_registries_description(case):
    """@prd T-148.2"""
    _second(case, "registries", "Checks the section 5 and 6 registries: each Decision is one of its table's values, no row is proposed while the PRD is Approved, an enforced standard has a backticked linter command on PATH, and a required skill is installed. Fix the Decision or the command, install the skill, or mark a skill built into Claude Code recommended.")


def test_runbook_steps_description(case):
    """@prd T-148.3"""
    _second(case, "runbook-steps", "Checks the operations.md runbook: steps numbered from 1 with no gap, each with (actor: agent|human) (env: <environment>), an agent step's Run:, Check: and Rollback: in their forms, a human step's Do: and Check:, and no label twice. Rewrite the step to the form the message gives.")


def test_runbook_env_description(case):
    """@prd T-148.4"""
    _second(case, "runbook-env", "Checks that operations.md Environments has a Production column with yes or no on every row and at least one yes, and a valid branch name or blank in each Branch cell, that every environment there is also in testing.md Environments, and that each runbook step and Deployed or Drift row names an environment of both tables. Add the environment to both tables or correct the name the message gives, add the Production column or set a row's Production to yes or no, and write a valid branch name or leave the Branch blank.")


def test_production_gate_description(case):
    """@prd T-148.5"""
    _second(case, "production-gate", "Checks that the first runbook step on each production environment is a human step or directly follows one. Add a human approval step just before it.")


def test_drift_rows_description(case):
    """@prd T-148.6"""
    _second(case, "drift-rows", "Checks that each Drift row's Check is version or config, and that a config row has contracts/config.yaml. Use one of the two checks, or add the config contract.")


def test_error_entries_description(case):
    """@prd T-148.7"""
    _second(case, "error-entries", "Checks errors.md entries: they run from E-001 upward with no gap, newest last; each has a known Classification, Evidence of at most 20 lines, and a Confirmed: in its form only on a classified entry; and an entry with Confirmed: also has Detected in its form and a Recurrence of that names an entry. Fix the line the message names, put an out-of-order entry back in sequence, and restore a deleted entry from git.")
