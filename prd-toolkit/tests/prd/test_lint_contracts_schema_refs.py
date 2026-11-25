"""lint-contracts FR-183: check each backticked table.column against schema.sql.

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml
and features/lint-contracts.md. Output is captured as bytes (testing.md, Assertions): stdout is
decoded as UTF-8 for the line assertions, and stderr is compared with the expected text encoded
as UTF-8.
"""
from __future__ import annotations

from lint_contracts_support import S0, assert_exact_lines, assert_not_contains, run_lint_bytes

TRACES_BAD = "Traces: `orders.order_kee` UNIQUE; fixtures orders/one_existing, customers/two_customers"
ORDER_KEE_FINDING = (
    "docs/prd/orders/features/import.md:17: schema-refs: `orders.order_kee`: table orders has no column order_kee"
)


def _out(r) -> str:
    return r.stdout.decode("utf-8")


def test_t183_1_unknown_column_is_reported(tmp_path, monkeypatch):
    """@prd T-183.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace("features/import.md", 17, TRACES_BAD)
    r = run_lint_bytes(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_exact_lines(_out(r), [ORDER_KEE_FINDING])
    assert r.stderr == "".encode("utf-8")


def test_t183_2_spans_that_are_not_checked(tmp_path, monkeypatch):
    """@prd T-183.2"""
    p = S0(tmp_path, monkeypatch)
    p.replace("features/import.md", 17, "Traces: `orders.csv`, `nosuch.thing` and `orders.order_key` UNIQUE")
    p.append("features/import.md", "```")
    p.append("features/import.md", "`orders.order_kee`")
    p.append("features/import.md", "```")
    p.replace(
        "errors.md", 6, "Diagnosis: the importer read `orders.order_kee` of an empty file; AC-001.3 was right"
    )
    r = run_lint_bytes(tmp_path)
    assert_not_contains(_out(r), "schema-refs:")
    assert r.stderr == "".encode("utf-8")


def test_t183_3_no_schema_sql_no_finding(tmp_path, monkeypatch):
    """@prd T-183.3"""
    p = S0(tmp_path, monkeypatch)
    p.delete_file("contracts/schema.sql")
    p.replace("features/import.md", 17, TRACES_BAD)
    r = run_lint_bytes(tmp_path)
    assert_not_contains(_out(r), "schema-refs:")
    assert r.stderr == "".encode("utf-8")


TRACES_EXTENSIONS = (
    "Traces: `orders.parquet`, `orders.avro`, `orders.orc`, `orders.ndjson`, `orders.jsonl`, "
    "`orders.xml`, `orders.xlsx`, `orders.gz`, `orders.zip`, `orders.html`, `orders.log`, "
    "`orders.toml`, `orders.ini`, `orders.py`, `orders.ts`, `orders.js` and `orders.order_kee` UNIQUE"
)


def test_t183_4_file_extension_spans_are_not_columns(tmp_path, monkeypatch):
    """@prd T-183.4"""
    p = S0(tmp_path, monkeypatch)
    p.replace("features/import.md", 17, TRACES_EXTENSIONS)
    r = run_lint_bytes(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_exact_lines(_out(r), [ORDER_KEE_FINDING])
    assert r.stderr == "".encode("utf-8")
