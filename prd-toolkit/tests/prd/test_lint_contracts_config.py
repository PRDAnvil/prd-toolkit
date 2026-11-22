"""lint-contracts: the settings of config.yaml (FR-178).

Cases from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml.
"""
from __future__ import annotations

from lint_contracts_support import S0, assert_contains_line, assert_not_contains, run_lint

F = "contracts/config.yaml"
P = "docs/prd/orders/contracts/config.yaml"


def test_settings_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-178.1"""
    o = S0(tmp_path, monkeypatch)
    o.write(F, "settings: [1]")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        f"{P}:1: contracts-valid: settings must be a mapping of name to {{type, default, environments, owner}}",
    )
    assert_not_contains(r.stdout, "contracts-valid: setting ")
    assert r.stderr == ""


def test_setting_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-178.2"""
    o = S0(tmp_path, monkeypatch)
    o.append(F, "  RETRY_LIMIT: 3")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:7: contracts-valid: setting RETRY_LIMIT: must be a mapping")
    assert_not_contains(r.stdout, "setting RETRY_LIMIT: missing")
    assert r.stderr == ""


def test_setting_missing_owner(tmp_path, monkeypatch):
    """@prd T-178.3"""
    o = S0(tmp_path, monkeypatch)
    o.delete(F, 6)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{P}:2: contracts-valid: setting IMPORT_BATCH_SIZE: missing owner")
    assert r.stderr == ""


def test_environments_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-178.4"""
    o = S0(tmp_path, monkeypatch)
    o.replace(F, 5, "    environments: [local, ci]")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{P}:5: contracts-valid: setting IMPORT_BATCH_SIZE: environments must be a mapping"
    )
    assert r.stderr == ""
