"""lint-contracts FR-184 and FR-185: cited error codes against the catalogue, both ways.

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml
and features/lint-contracts.md.
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

P = "docs/prd/orders"


def _append_unused_code(p, meaning: str) -> None:
    p.append("contracts/errors.yaml", "UNUSED_CODE:")
    p.append("contracts/errors.yaml", f"  meaning: {meaning}")
    p.append("contracts/errors.yaml", "  when: Never.")
    p.append("contracts/errors.yaml", "  status: 500")
    p.append("contracts/errors.yaml", "  message: Unused")
    p.append("contracts/errors.yaml", "  log_level: error")
    p.append("contracts/errors.yaml", "  retryable: false")
    p.append("contracts/errors.yaml", "  metric: unused_total")


def test_t184_1_errors_line_code_not_catalogued(tmp_path, monkeypatch):
    """@prd T-184.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace("features/api.md", 17, "Errors: ORDER_NOT_FOUND, ORDER_LOCKED (contracts/errors.yaml)")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_exact_lines(
        r.stdout,
        [f"{P}/features/api.md:17: error-codes: error code ORDER_LOCKED is not in contracts/errors.yaml"],
    )
    assert r.stderr == ""


def test_t184_2_openapi_x_error_codes_not_catalogued(tmp_path, monkeypatch):
    """@prd T-184.2"""
    p = S0(tmp_path, monkeypatch)
    p.replace("contracts/openapi.yaml", 23, "      x-error-codes: ORDER_GONE")
    p.replace("contracts/openapi.yaml", 44, "      x-error-codes: [FORBIDDEN, NOPE]")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{P}/contracts/openapi.yaml:23: error-codes: error code ORDER_GONE is not in contracts/errors.yaml",
            f"{P}/contracts/openapi.yaml:44: error-codes: error code NOPE is not in contracts/errors.yaml",
        ],
    )
    assert r.stderr == ""


def test_t184_3_dependency_failures_not_catalogued(tmp_path, monkeypatch):
    """@prd T-184.3"""
    p = S0(tmp_path, monkeypatch)
    p.replace("contracts/dependencies/geocoder.yaml", 14, "  5xx: [GEOCODER_TIMEOUT, GEOCODER_DOWN]")
    p.replace("contracts/dependencies/geocoder.yaml", 15, "  outage: GEOCODER_GONE")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{P}/contracts/dependencies/geocoder.yaml:14: error-codes: error code GEOCODER_DOWN is not in contracts/errors.yaml",
            f"{P}/contracts/dependencies/geocoder.yaml:15: error-codes: error code GEOCODER_GONE is not in contracts/errors.yaml",
        ],
    )
    assert r.stderr == ""


def test_t184_4_test_case_expect_errors_not_checked(tmp_path, monkeypatch):
    """@prd T-184.4"""
    p = S0(tmp_path, monkeypatch)
    p.replace("test-cases/api.yaml", 66, "    errors: [FORBIDDEN, GHOST]")
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "error-codes: error code GHOST")
    assert r.stderr == ""


def test_t184_5_catalogue_not_a_mapping_no_finding(tmp_path, monkeypatch):
    """@prd T-184.5"""
    p = S0(tmp_path, monkeypatch)
    p.write("contracts/errors.yaml", "- IMPORT_DUPLICATE")
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "error-codes:")
    assert r.stderr == ""


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_t184_6_dependency_subfolder_cites_nothing(tmp_path, monkeypatch):
    """@prd T-184.6 known-failing E-062"""
    p = S0(tmp_path, monkeypatch)
    p.write("contracts/dependencies/old/legacy.yaml", "failures: {timeout: NOT_CATALOGUED}")
    r = run_lint(tmp_path)
    symptom = (
        f"{P}/contracts/dependencies/old/legacy.yaml:1: error-codes: "
        "error code NOT_CATALOGUED is not in contracts/errors.yaml"
    )
    if r.returncode == 1 and symptom in r.stdout.splitlines():
        raise KnownFailure("E-062: a subfolder dependency file's failure is checked")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout == ""
    assert r.stderr == ""


def test_t185_1_catalogued_code_cited_nowhere(tmp_path, monkeypatch):
    """@prd T-185.1"""
    p = S0(tmp_path, monkeypatch)
    _append_unused_code(p, "Nothing cites this.")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(
        r.stdout, f"{P}/contracts/errors.yaml:41: error-codes: error code UNUSED_CODE is catalogued but cited nowhere"
    )
    assert r.stderr == ""


def test_t185_2_code_named_only_in_test_case_counts(tmp_path, monkeypatch):
    """@prd T-185.2"""
    p = S0(tmp_path, monkeypatch)
    p.replace("features/api.md", 30, "Errors: -")
    p.replace("contracts/openapi.yaml", 44, "      x-error-codes: []")
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "error code FORBIDDEN is catalogued but cited nowhere")
    assert r.stderr == ""


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_t185_3_code_cited_only_in_subfolder_is_cited_nowhere(tmp_path, monkeypatch):
    """@prd T-185.3 known-failing E-062"""
    p = S0(tmp_path, monkeypatch)
    _append_unused_code(p, "Only a legacy file cites this.")
    p.write("contracts/dependencies/old/legacy.yaml", "failures: {timeout: UNUSED_CODE}")
    r = run_lint(tmp_path)
    if r.returncode == 0 and r.stdout == "":
        raise KnownFailure("E-062: exit 0 and empty stdout")
    assert r.returncode == 1, r.stdout + r.stderr
    assert_exact_lines(
        r.stdout,
        [f"{P}/contracts/errors.yaml:41: error-codes: error code UNUSED_CODE is catalogued but cited nowhere"],
    )
    assert r.stderr == ""
