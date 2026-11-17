"""card-context: a gate's URL (FR-066), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
from card_context_support import assert_json_at, given_steps, orders, run, scratch  # noqa: F401  (scratch: fixture)


@given_steps("N0", "C1", "CE", "CK")
def test_error_class_gate_url(scratch):
    """@prd T-066.1"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.url": "https://example.com/runs/1001",
        "gates.1.url": "https://example.com/orders/import",
        "gates.2.url": "https://example.com/orders/import",
        "gates.3.url": None,
    })


@given_steps("N0", "C1", "CS", "NA1", "CB")
def test_adoption_and_signoff_gate_url(scratch):
    """@prd T-066.2"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "adoption:billing",
        "gates.0.url": "https://example.com/orders/billing",
        "gates.1.id": "signoff:T-005.3",
        "gates.1.url": None,
    })


@given_steps("N0", "C1", "CA1")
def test_approval_gate_url(scratch):
    """@prd T-066.3"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "approval:cards",
        "gates.0.url": "https://example.com/orders/import",
    })


@given_steps("N0", "C1", "NR3")
def test_deploy_step_gate_url(scratch):
    """@prd T-066.4"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "deploy-step:20261111T090000Z-all:2",
        "gates.0.url": None,
    })
