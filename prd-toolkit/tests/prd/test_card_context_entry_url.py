"""card-context: the URL: line of an error entry (FR-063), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
from card_context_support import (  # noqa: F401  (scratch: fixture)
    assert_json_at, assert_lines_in_relative_order, assert_not_contains, given_steps, run, scratch,
)

ORDERS = "docs/prd/orders"


@given_steps("N0", "C1", "CE")
def test_entry_url_line_is_read(scratch):
    """@prd T-063.1"""
    r1 = run(scratch, "LINT", ORDERS)
    assert r1.exit == 0, r1
    assert r1.stderr == ""
    assert_not_contains(r1.stdout, ["error-entries", "pack-resolves"])

    r2 = run(scratch, "GATES", "list", "--json", ORDERS)
    assert r2.exit == 0, r2
    assert r2.stderr == ""
    assert_json_at(r2.stdout, {
        "gates.0.id": "error-class:E-001",
        "gates.0.url": "https://example.com/runs/1001",
    })


@given_steps("N0", "CL1")
def test_malformed_entry_url_is_a_finding_and_never_the_card_url(scratch):
    """@prd T-063.2"""
    r1 = run(scratch, "LINT", ORDERS)
    assert r1.exit == 1, r1
    assert r1.stderr == ""
    assert_lines_in_relative_order(r1.stdout, [
        "docs/prd/orders/errors.md:6: error-entries: E-001: URL: must start with http:// or https:// and hold no white space",
        "docs/prd/orders/errors.md:13: error-entries: E-002: URL: must start with http:// or https:// and hold no white space",
        "docs/prd/orders/errors.md:20: error-entries: E-003: URL: must start with http:// or https:// and hold no white space",
    ])

    r2 = run(scratch, "GATES", "list", "--json", ORDERS)
    assert r2.exit == 0, r2
    assert r2.stderr == ""
    assert_json_at(r2.stdout, {
        "gates.0.id": "error-class:E-001",
        "gates.0.areas": [],
        "gates.0.url": None,
    })


@given_steps("N0", "NE1")
def test_no_url_line_prints_as_before(scratch):
    """@prd T-063.3"""
    r1 = run(scratch, "LINT", ORDERS)
    assert r1.exit == 0, r1
    assert r1.stderr == ""
    assert r1.stdout.splitlines() == [
        "docs/prd/orders/test-cases/reports.yaml:27: warn: judged-case: T-005.2: threshold 0.9 needs all 2 items "
        "(1 of 2 is 0.5); write 0.5 to allow one miss, or 1.0",
    ]

    r2 = run(scratch, "ERROR", "list", ORDERS)
    assert r2.exit == 0, r2
    assert r2.stderr == ""
    assert r2.stdout.splitlines() == [
        "E-001 confirmed code bug FR-003 The importer stops at row 1000",
        "E-002 unclassified FR-006 A monthly report printed no total",
    ]
