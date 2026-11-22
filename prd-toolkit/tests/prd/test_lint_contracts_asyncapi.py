"""lint-contracts: contracts-valid on contracts/asyncapi.yaml (FR-172)."""
from lint_contracts_support import S0, assert_contains_line, assert_not_contains, run_lint

AA = "contracts/asyncapi.yaml"


def test_missing_asyncapi_key(tmp_path, monkeypatch):
    """@prd T-172.1"""
    p = S0(tmp_path, monkeypatch)
    p.write(AA, "channels: {}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        "docs/prd/orders/contracts/asyncapi.yaml:1: contracts-valid: missing top-level key asyncapi",
    )
    assert r.stderr == ""


def test_channels_and_operations_not_checked(tmp_path, monkeypatch):
    """@prd T-172.2"""
    p = S0(tmp_path, monkeypatch)
    p.write(AA, "asyncapi: 3.0.0")
    p.append(AA, "channels: [x]")
    p.append(AA, "operations: 4")
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "contracts/asyncapi.yaml:")
    assert r.stderr == ""
