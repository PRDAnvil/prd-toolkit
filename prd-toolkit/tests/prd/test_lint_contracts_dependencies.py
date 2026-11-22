"""lint-contracts: the shape of each dependency file (FR-180).

Cases from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml.
"""
from __future__ import annotations

from lint_contracts_support import S0, assert_contains_line, run_lint

F = "contracts/dependencies/geocoder.yaml"
P = "docs/prd/orders/contracts/dependencies/geocoder.yaml"


def test_missing_mock(tmp_path, monkeypatch):
    """@prd T-180.1"""
    o = S0(tmp_path, monkeypatch)
    o.delete(F, 10)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:1: contracts-valid: missing mock")
    assert r.stderr == ""


def test_auth_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-180.2"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 8, "  token: GEOCODER_API_KEY")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:7: contracts-valid: auth must be a mapping with secret")
    assert r.stderr == ""


def test_failures_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-180.3"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 11, "failures: [GEOCODER_TIMEOUT]")
    for n in range(12, 16):
        o.delete(F, n)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{P}:11: contracts-valid: failures must be a mapping with timeout, 4xx, 5xx and outage"
    )
    assert r.stderr == ""


def test_failures_missing_4xx(tmp_path, monkeypatch):
    """@prd T-180.4"""
    o = S0(tmp_path, monkeypatch)
    o.delete(F, 13)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:12: contracts-valid: failures: missing 4xx")
    assert r.stderr == ""


def test_subfolder_not_checked(tmp_path, monkeypatch):
    """@prd T-180.5"""
    o = S0(tmp_path, monkeypatch)
    o.write("contracts/dependencies/old/geocoder.yaml", "sends: x")
    r = run_lint(tmp_path)
    assert r.returncode == 0
    assert r.stdout == ""
    assert r.stderr == ""
