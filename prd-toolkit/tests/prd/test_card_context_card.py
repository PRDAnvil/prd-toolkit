"""card-context: the inbox's card of a gate (AC-067.3), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
import importlib

from card_context_support import (  # noqa: F401  (scratch: fixture)
    FULL_STATE, SCRIPTS_DIR, clear_env, given_steps, json_equal, orders, scratch,
)

BASE = ["id", "kind", "title", "question", "evidence", "choices", "source"]

IDS = [
    "approval:cards",
    "error-class:E-001",
    "error-class:E-002",
    "error-class:E-003",
    "error-class:E-004",
    "deploy-step:20261111T090000Z-all:2",
    "adoption:billing",
    "signoff:T-005.3",
]

KEYS_BY_KIND = {
    "approval": BASE + ["areas", "url", "restate", "touches", "bump", "impact", "dry_run", "diff_truncated", "diff",
                        "version", "waiting"],
    "error-class": BASE + ["areas", "url", "class", "diagnosis", "waiting"],
    "deploy-step": BASE + ["areas", "url", "run", "step", "env", "actor", "do", "check", "waiting"],
    "adoption": BASE + ["items", "areas", "url", "area", "waiting"],
    "signoff": BASE + ["areas", "url", "tid", "owner", "input", "expect", "waiting"],
}

WHOLE_CARDS = {
    "error-class:E-001": {
        "id": "error-class:E-001",
        "kind": "error-class",
        "title": "The importer stops at row 1000",
        "question": "Proposed class: code bug. Confirm it, or correct it to another class.",
        "evidence": [],
        "choices": ["confirm", "correct"],
        "source": "errors.md:3",
        "areas": ["import"],
        "url": "https://example.com/runs/1001",
        "class": "code bug",
        "diagnosis": "",
        "waiting": False,
    },
    "deploy-step:20261111T090000Z-all:2": {
        "id": "deploy-step:20261111T090000Z-all:2",
        "kind": "deploy-step",
        "title": "Run 20261111T090000Z-all step 2: Approve production",
        "question": 'Approve production. read the staging result and reply "deploy production"',
        "evidence": ['Check: the reply says "deploy production"'],
        "choices": ["confirm"],
        "source": "operations.md",
        "areas": [],
        "url": None,
        "run": "20261111T090000Z-all",
        "step": 2,
        "env": "production",
        "actor": "human",
        "do": 'read the staging result and reply "deploy production"',
        "check": 'the reply says "deploy production"',
        "waiting": False,
    },
    "adoption:billing": {
        "id": "adoption:billing",
        "kind": "adoption",
        "title": "Adopt area billing",
        "question": "0 of 0 items of area billing are open. Answer each, then mark the area done.",
        "evidence": [],
        "choices": ["done"],
        "source": ".prd-confirm-billing.json",
        "items": [],
        "areas": ["billing"],
        "url": "https://example.com/orders/billing",
        "area": "billing",
        "waiting": False,
    },
    "signoff:T-005.3": {
        "id": "signoff:T-005.3",
        "kind": "signoff",
        "title": "Sign off T-005.3",
        "question": "Sample Owner walks the steps of T-005.3 and reports the result: pass or fail.",
        "evidence": ["Ask for the October report", "Read each line against the October orders"],
        "choices": ["pass", "fail"],
        "source": "test-cases/reports.yaml:60",
        "areas": ["reports"],
        "url": None,
        "tid": "T-005.3",
        "owner": "Sample Owner",
        "input": {"month": "2026-10"},
        "expect": {"output": {"lines": 2}, "effects": [], "errors": [], "leaks": "none"},
        "waiting": False,
    },
}

AREAS_AND_URL = {
    "approval:cards": {"areas": ["import"], "url": "https://example.com/orders/import"},
    "error-class:E-002": {"areas": ["import", "reports"], "url": "https://example.com/orders/import"},
    "error-class:E-003": {"areas": ["reports", "import"], "url": "https://example.com/orders/import"},
    "error-class:E-004": {"areas": [], "url": None},
}


@given_steps(*FULL_STATE)
def test_card_holds_areas_and_url(scratch, monkeypatch):
    """@prd T-067.3"""
    folder = orders(scratch)
    clear_env(monkeypatch)
    monkeypatch.chdir(folder)
    monkeypatch.syspath_prepend(str(SCRIPTS_DIR))
    model = importlib.import_module("prdlint.model")
    gates_mod = importlib.import_module("prdlint.gates")

    prd = model.load(folder)
    gates = gates_mod.list_gates(prd, scratch)
    cards = [gates_mod.card(gate, prd, scratch, "docs/prd/orders") for gate in gates]
    for c in cards:
        assert isinstance(c, dict), c

    assert [c.get("id") for c in cards] == IDS

    for c in cards:
        assert c.get("kind") in KEYS_BY_KIND, c
        assert list(c.keys()) == KEYS_BY_KIND[c["kind"]], (c["id"], list(c.keys()))

    by_id = {c["id"]: c for c in cards}
    for gid, want in WHOLE_CARDS.items():
        assert json_equal(by_id[gid], want), f"card {gid}:\n{by_id[gid]!r}\n!=\n{want!r}"

    for gid, want in AREAS_AND_URL.items():
        assert json_equal(by_id[gid]["areas"], want["areas"]), (gid, by_id[gid]["areas"])
        assert json_equal(by_id[gid]["url"], want["url"]), (gid, by_id[gid]["url"])
