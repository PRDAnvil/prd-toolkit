"""lint-contracts: contracts-valid on contracts/schema.sql (FR-174)."""
from lint_contracts_support import (
    S0,
    assert_contains,
    assert_contains_line,
    assert_not_contains,
    run_lint,
)

SQL = "contracts/schema.sql"
F = "docs/prd/orders/contracts/schema.sql"


def test_does_not_parse_in_named_dialect(tmp_path, monkeypatch):
    """@prd T-174.1"""
    p = S0(tmp_path, monkeypatch)
    p.delete(SQL, 5)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains(r.stdout, f"{F}:1: contracts-valid: schema.sql does not parse (postgres): ")
    assert_not_contains(r.stdout, "has no COMMENT ON")
    assert r.stderr == ""


def test_does_not_parse_in_default_dialect(tmp_path, monkeypatch):
    """@prd T-174.2"""
    p = S0(tmp_path, monkeypatch)
    p.delete("prd.md", 7)
    p.delete(SQL, 5)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains(
        r.stdout, f"{F}:1: contracts-valid: schema.sql does not parse (default dialect): "
    )
    assert r.stderr == ""


def test_table_without_comment(tmp_path, monkeypatch):
    """@prd T-174.3"""
    p = S0(tmp_path, monkeypatch)
    p.delete(SQL, 15)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        f"{F}:1: contracts-valid: table customers has no COMMENT ON TABLE or OPTIONS(description=...)",
    )
    assert r.stderr == ""


def test_column_without_comment(tmp_path, monkeypatch):
    """@prd T-174.4"""
    p = S0(tmp_path, monkeypatch)
    p.delete(SQL, 23)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        f"{F}:11: contracts-valid: column orders.status has no COMMENT ON COLUMN or OPTIONS(description=...)",
    )
    assert r.stderr == ""


def test_bigquery_description_options(tmp_path, monkeypatch):
    """@prd T-174.5"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 7, "sql-dialect: bigquery")
    p.write(
        SQL,
        'CREATE TABLE customers (id INT64 OPTIONS(description="k"), email STRING OPTIONS(description="e"), name STRING) OPTIONS(description="t");',
    )
    p.append(
        SQL,
        'CREATE TABLE orders (id INT64 OPTIONS(description="k"), order_key STRING OPTIONS(description="k"), customer_id INT64 OPTIONS(description="c"), status STRING OPTIONS(description="s"), sales_rep_name STRING OPTIONS(description="r")) OPTIONS(description="t");',
    )
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout,
        f"{F}:1: contracts-valid: column customers.name has no COMMENT ON COLUMN or OPTIONS(description=...)",
    )
    assert_not_contains(
        r.stdout,
        [
            "table customers has no",
            "table orders has no",
            "column orders.",
            "column customers.id",
            "column customers.email",
        ],
    )
    assert r.stderr == ""
