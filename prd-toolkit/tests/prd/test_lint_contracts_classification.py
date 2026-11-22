"""lint-contracts: the tables and masking of data-classification.yaml (FR-179).

Cases from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml.
"""
from __future__ import annotations

import pytest

from lint_contracts_support import (
    KnownFailure,
    S0,
    assert_contains_line,
    assert_exact_lines,
    assert_not_contains,
    run_lint,
)

F = "contracts/data-classification.yaml"
P = "docs/prd/orders/contracts/data-classification.yaml"


def test_tables_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-179.1"""
    o = S0(tmp_path, monkeypatch)
    o.write(F, "tables: [x]")
    o.append(F, "masking: {logs: a, errors: b, fixtures: c}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:1: contracts-valid: tables must be a mapping")
    assert_not_contains(r.stdout, "contracts-valid: masking")
    assert r.stderr == ""


def test_table_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-179.2"""
    o = S0(tmp_path, monkeypatch)
    o.insert_after(F, 9, "  refunds: 3")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:10: contracts-valid: table refunds: must be a mapping")
    assert r.stderr == ""


def test_table_missing_retention(tmp_path, monkeypatch):
    """@prd T-179.3"""
    o = S0(tmp_path, monkeypatch)
    o.delete(F, 3)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:2: contracts-valid: table customers: missing retention")
    assert r.stderr == ""


def test_columns_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-179.4"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 9, "    columns: [id, order_key]")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{P}:9: contracts-valid: table orders: columns must be a mapping of column to class"
    )
    assert r.stderr == ""


def test_unknown_class(tmp_path, monkeypatch):
    """@prd T-179.5"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 5, "    columns: {id: internal, email: secret, name: pii}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        f"{P}:5: contracts-valid: customers.email: class 'secret' must be public, internal, confidential or pii",
    )
    assert r.stderr == ""


def test_masking_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-179.6"""
    o = S0(tmp_path, monkeypatch)
    o.write(F, "tables: {}")
    o.append(F, "masking: 4")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{P}:2: contracts-valid: masking must be a mapping with logs, errors and fixtures"
    )
    assert r.stderr == ""


def test_masking_missing_errors(tmp_path, monkeypatch):
    """@prd T-179.7"""
    o = S0(tmp_path, monkeypatch)
    o.delete(F, 12)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:11: contracts-valid: masking: missing errors")
    assert r.stderr == ""


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_list_or_mapping_class(tmp_path, monkeypatch):
    """@prd T-179.8 known-failing E-058"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 5, "    columns: {id: internal, email: [pii], name: {kind: pii}}")
    r = run_lint(tmp_path)
    # symptom: exit 2, stdout empty, and the first stderr line starts with exactly
    # `prd_lint: internal error in rule contracts-valid: TypeError:`
    err_lines = r.stderr.splitlines()
    if (
        r.returncode == 2
        and r.stdout == ""
        and err_lines
        and err_lines[0].startswith("prd_lint: internal error in rule contracts-valid: TypeError:")
    ):
        raise KnownFailure("E-058: internal error TypeError in contracts-valid")
    assert r.returncode == 1
    assert_exact_lines(
        r.stdout,
        [
            f"{P}:5: contracts-valid: customers.email: class ['pii'] must be public, internal, confidential or pii",
            f"{P}:5: contracts-valid: customers.name: class {{'kind': 'pii'}} must be public, internal, confidential or pii",
        ],
    )
    assert r.stderr == ""
