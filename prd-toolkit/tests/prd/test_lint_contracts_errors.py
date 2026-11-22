"""lint-contracts: contracts-valid on contracts/errors.yaml (FR-175)."""
from lint_contracts_support import (
    S0,
    assert_contains_line,
    assert_lines_in_relative_order,
    assert_not_contains,
    run_lint,
)

ER = "contracts/errors.yaml"
F = "docs/prd/orders/contracts/errors.yaml"


def test_code_must_match_pattern(tmp_path, monkeypatch):
    """@prd T-175.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace(ER, 25, "Forbidden:")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{F}:25: contracts-valid: error code 'Forbidden' must match ^[A-Z][A-Z0-9_]*$"
    )
    assert r.stderr == ""


def test_code_value_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-175.2"""
    p = S0(tmp_path, monkeypatch)
    p.append(ER, "NOT_A_MAP: 3")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        f"{F}:41: contracts-valid: NOT_A_MAP: must be a mapping with meaning, when, status, message, log_level, retryable, metric",
    )
    assert_not_contains(r.stdout, "NOT_A_MAP: missing")
    assert r.stderr == ""


def test_missing_keys_in_order(tmp_path, monkeypatch):
    """@prd T-175.3"""
    p = S0(tmp_path, monkeypatch)
    p.delete(ER, 27)
    p.delete(ER, 32)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:25: contracts-valid: FORBIDDEN: missing when",
            f"{F}:25: contracts-valid: FORBIDDEN: missing metric",
        ],
    )
    assert r.stderr == ""


def test_status_must_be_an_integer(tmp_path, monkeypatch):
    """@prd T-175.4"""
    p = S0(tmp_path, monkeypatch)
    p.replace(ER, 28, "  status: true")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{F}:28: contracts-valid: FORBIDDEN: status must be an integer")
    assert r.stderr == ""


def test_retryable_must_be_boolean(tmp_path, monkeypatch):
    """@prd T-175.5"""
    p = S0(tmp_path, monkeypatch)
    p.replace(ER, 31, '  retryable: "no"')
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{F}:31: contracts-valid: FORBIDDEN: retryable must be true or false"
    )
    assert r.stderr == ""
