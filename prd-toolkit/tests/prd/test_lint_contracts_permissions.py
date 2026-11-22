"""lint-contracts: permissions.yaml roles, operations and row rules (FR-176, FR-177).

Cases from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml.
"""
from __future__ import annotations

import pytest

from lint_contracts_support import (
    KnownFailure,
    S0,
    assert_contains_line,
    assert_exact_lines,
    assert_lines_in_relative_order,
    assert_not_contains,
    run_lint,
)

F = "contracts/permissions.yaml"
P = "docs/prd/orders/contracts/permissions.yaml"


def test_roles_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-176.1"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 1, "people:")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:1: contracts-valid: roles must be a mapping of role to {{identity}}")
    assert r.stderr == ""


def test_role_missing_identity(tmp_path, monkeypatch):
    """@prd T-176.2"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 3, "  rep: {secret: ORDERS_TEST_REP_TOKEN}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:3: contracts-valid: role rep: missing identity")
    assert r.stderr == ""


def test_operations_absent(tmp_path, monkeypatch):
    """@prd T-176.3"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 4, "actions:")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{P}:1: contracts-valid: operations must be a mapping of operation to {{allow, deny}}"
    )
    assert r.stderr == ""


def test_operation_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-176.4"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 5, "  getOrder: open")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{P}:5: contracts-valid: operation getOrder: must be a mapping with allow and deny lists"
    )
    assert r.stderr == ""


def test_allow_not_a_list(tmp_path, monkeypatch):
    """@prd T-176.5"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 6, "  deleteOrder: {allow: admin, deny: [rep]}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:6: contracts-valid: operation deleteOrder: allow must be a list")
    assert_not_contains(r.stdout, ["operation deleteOrder: role", "operation deleteOrder: unknown role"])
    assert r.stderr == ""


def test_role_in_neither_or_both_lists(tmp_path, monkeypatch):
    """@prd T-176.6"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 5, "  getOrder: {allow: [admin], deny: []}")
    o.replace(F, 6, "  deleteOrder: {allow: [admin, rep], deny: [rep]}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{P}:5: contracts-valid: operation getOrder: role rep must appear in exactly one of allow and deny (found 0)",
            f"{P}:6: contracts-valid: operation deleteOrder: role rep must appear in exactly one of allow and deny (found 2)",
        ],
    )
    assert r.stderr == ""


def test_unknown_role(tmp_path, monkeypatch):
    """@prd T-176.7"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 6, "  deleteOrder: {allow: [admin], deny: [rep, auditor]}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:6: contracts-valid: operation deleteOrder: unknown role auditor")
    assert r.stderr == ""


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_role_missing_secret(tmp_path, monkeypatch):
    """@prd T-176.8 known-failing E-061"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 2, "  admin: {identity: test-admin}")
    o.replace(F, 3, "  rep: {identity: test-rep, secret: ''}")
    r = run_lint(tmp_path)
    # symptom: "the exit code is 0 and stdout is empty"
    if r.returncode == 0 and r.stdout == "":
        raise KnownFailure("E-061: exit 0 and empty stdout")
    assert r.returncode == 1
    assert_exact_lines(
        r.stdout,
        [
            f"{P}:2: contracts-valid: role admin: missing secret",
            f"{P}:3: contracts-valid: role rep: missing secret",
        ],
    )
    assert r.stderr == ""


def test_row_rules_absent(tmp_path, monkeypatch):
    """@prd T-177.1"""
    o = S0(tmp_path, monkeypatch)
    for n in range(7, 12):
        o.delete(F, n)
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "row_rules")
    assert r.stderr == ""


def test_row_rules_not_a_list(tmp_path, monkeypatch):
    """@prd T-177.2"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 7, "row_rules: {}")
    for n in range(8, 12):
        o.delete(F, n)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:7: contracts-valid: row_rules must be a list")
    assert_not_contains(r.stdout, "row_rules item")
    assert r.stderr == ""


def test_row_rule_missing_key(tmp_path, monkeypatch):
    """@prd T-177.3"""
    o = S0(tmp_path, monkeypatch)
    o.delete(F, 11)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:8: contracts-valid: row_rules item 1: missing attribute")
    assert r.stderr == ""


def test_row_rule_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-177.4"""
    o = S0(tmp_path, monkeypatch)
    o.append(F, "  - 3")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:7: contracts-valid: row_rules item 2 must be a mapping")
    assert r.stderr == ""
