"""card-context: a gate's areas (FR-062), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
from card_context_support import assert_json_at, given_steps, orders, run, scratch  # noqa: F401  (scratch: fixture)


@given_steps("N0", "C1", "CE", "CK")
def test_error_class_gate_areas(scratch):
    """@prd T-062.1"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "error-class:E-001",
        "gates.0.areas": ["import"],
        "gates.1.id": "error-class:E-002",
        "gates.1.areas": ["import", "reports"],
        "gates.2.id": "error-class:E-003",
        "gates.2.areas": ["reports", "import"],
        "gates.3.id": "error-class:E-004",
        "gates.3.areas": [],
    })


@given_steps("N0", "C1", "CS", "NA1", "CB")
def test_adoption_and_signoff_gate_areas(scratch):
    """@prd T-062.2"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "adoption:billing",
        "gates.0.areas": ["billing"],
        "gates.1.id": "signoff:T-005.3",
        "gates.1.areas": ["reports"],
    })


@given_steps("N0", "C1", "CA1")
def test_approval_gate_areas_one_block(scratch):
    """@prd T-062.3"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "approval:cards",
        "gates.0.areas": ["import"],
    })


@given_steps("N0", "C1", "CA2")
def test_approval_gate_areas_tid_ac_and_other(scratch):
    """@prd T-062.4"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "approval:cards",
        "gates.0.areas": ["import", "reports"],
        "gates.0.url": None,
    })


@given_steps("N0", "C1", "NR3", "NR4")
def test_deploy_step_gate_areas(scratch):
    """@prd T-062.5"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_at(r.stdout, {
        "gates.0.id": "deploy-step:20261111T090000Z-all:2",
        "gates.0.areas": [],
        "gates.1.id": "deploy-step:20261112T090000Z-all:unreadable",
        "gates.1.areas": [],
    })
