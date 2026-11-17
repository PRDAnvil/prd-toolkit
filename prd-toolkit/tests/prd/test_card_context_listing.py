"""card-context: where the area and the URL show (FR-067), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
from card_context_support import (  # noqa: F401  (scratch: fixture)
    FULL_STATE, assert_json_at, assert_json_keys_at, given_steps, one_json_line, orders, run, scratch,
)

GATE_KEYS = ["id", "kind", "title", "question", "evidence", "choices", "source", "areas", "url"]


@given_steps(*FULL_STATE)
def test_text_listing_unchanged(scratch):
    """@prd T-067.1"""
    r = run(orders(scratch), "GATES", "list", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert r.stdout.splitlines() == [
        "approval:cards Approve orders 1.1.0",
        "error-class:E-001 The importer stops at row 1000",
        "error-class:E-002 A monthly report printed no total",
        "error-class:E-003 A report lists a cancelled order",
        "error-class:E-004 A rerun printed a warning",
        "deploy-step:20261111T090000Z-all:2 Run 20261111T090000Z-all step 2: Approve production",
        "adoption:billing Adopt area billing",
        "signoff:T-005.3 Sign off T-005.3",
    ]


@given_steps(*FULL_STATE)
def test_json_listing_keys(scratch):
    """@prd T-067.2"""
    r = run(orders(scratch), "GATES", "list", "--json", ".")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert_json_keys_at(r.stdout, {
        "": ["interface", "kind", "prd", "gates"],
        "gates.0": GATE_KEYS,
        "gates.4": GATE_KEYS,
        "gates.5": GATE_KEYS,
        "gates.6": ["id", "kind", "title", "question", "evidence", "choices", "source", "items", "areas", "url"],
    })
    assert_json_at(r.stdout, {
        "interface": 1,
        "kind": "gates",
        "prd": "orders",
        "gates.4.areas": [],
        "gates.4.url": None,
        "gates.6.areas": ["billing"],
        "gates.6.url": "https://example.com/orders/billing",
    })


@given_steps(*FULL_STATE)
def test_status_next_lists_gates_as_before(scratch):
    """@prd T-067.5"""
    folder = orders(scratch)
    r1 = run(folder, "STATUS", "--json", ".")
    r2 = run(folder, "GATES", "list", "--json", ".")
    for n, r in enumerate((r1, r2), start=1):
        assert r.exit == 0, (n, r)
        assert r.stderr == "", (n, r.stderr)

    # Relation 1: each stdout is one JSON line; run_1's Next items and run_2's gates.
    doc1, doc2 = one_json_line(r1.stdout), one_json_line(r2.stdout)
    next_items = [item for item in doc1["items"] if item.get("part") == "Next"]
    gates = doc2["gates"]

    # Relation 2: the gate items, in order, one per gate, id and text from the gate.
    gate_items = [item for item in next_items if item.get("kind") == "gate"]
    assert [item.get("id") for item in gate_items] == [g["id"] for g in gates]
    for item, gate in zip(gate_items, gates):
        assert item.get("text") == f"{gate['title']} waits for your answer.", (item, gate)

    # Relation 3: area and ids.
    for item in gate_items:
        gid = item["id"]
        if gid == "adoption:billing":
            assert item.get("area") == "billing", item
        else:
            assert "area" in item and item["area"] is None, item
        if gid.startswith("error-class:"):
            ids = item.get("ids")
            assert isinstance(ids, list) and ids == [gid.split(":", 1)[1]], item
        if gid == "signoff:T-005.3":
            ids = item.get("ids")
            assert isinstance(ids, list) and ids == ["T-005.3"], item


def test_help_kind_e_names_url_line(tmp_path):
    """@prd T-067.6"""
    r = run(tmp_path, "HELP", "--key", "kind.E")
    assert r.exit == 0, r
    assert r.stderr == ""
    assert "`URL: <address>`" in r.stdout, r.stdout
