"""card-context: the url part of a Target: line (FR-065), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
from card_context_support import (  # noqa: F401  (scratch: fixture)
    assert_json_at, assert_lines_in_relative_order, assert_not_contains, given_steps, run, scratch,
)

ORDERS = "docs/prd/orders"


@given_steps("N0", "C1", "CE", "CT3")
def test_three_part_target_line(scratch):
    """@prd T-065.1"""
    r1 = run(scratch, "LINT", ORDERS)
    assert r1.exit == 0, r1
    assert r1.stderr == ""
    assert_not_contains(r1.stdout, "pack-resolves")

    r2 = run(scratch, "GATES", "list", "--json", ORDERS)
    assert r2.exit == 0, r2
    assert r2.stderr == ""
    assert_json_at(r2.stdout, {
        "gates.1.id": "error-class:E-002",
        "gates.1.url": "https://example.com/orders/import?a=1,b=2",
    })


@given_steps("N0", "C1", "CE", "CT2")
def test_malformed_target_url(scratch):
    """@prd T-065.2"""
    r1 = run(scratch, "LINT", ORDERS)
    assert r1.exit == 1, r1
    assert r1.stderr == ""
    assert_lines_in_relative_order(r1.stdout, [
        "docs/prd/orders/features/import.md:3: pack-resolves: Target: url must start with http:// or https:// "
        "and hold no white space",
        "docs/prd/orders/features/reports.md:3: pack-resolves: Target: url must start with http:// or https:// "
        "and hold no white space",
    ])

    r2 = run(scratch, "GATES", "list", "--json", ORDERS)
    assert r2.exit == 0, r2
    assert_json_at(r2.stdout, {
        "gates.0.url": "https://example.com/runs/1001",
        "gates.1.id": "error-class:E-002",
        "gates.1.url": None,
    })


@given_steps("N0", "C1", "CT5")
def test_target_parts_out_of_order(scratch):
    """@prd T-065.3"""
    r = run(scratch, "LINT", ORDERS)
    assert r.exit == 1, r
    assert r.stderr == ""
    want = ("docs/prd/orders/features/reports.md:3: pack-resolves: Target: must be one or more of "
            "pack <name> <X.Y.Z> (<source>), output language <code> and url <address>, comma-separated, "
            "in that order")
    assert want in r.stdout.splitlines(), f"no line {want!r} in stdout:\n{r.stdout}"
