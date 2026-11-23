"""inbox-cards FR-254: an error-class card's explanation and choices (test-cases/inbox-cards.yaml)."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

from inbox_cards_support import before, build, run_gates

ERROR_CLASS = "error-class:E-001"
CARD_KEYS = ["id", "kind", "title", "question", "evidence", "choices", "source", "areas", "url",
             "class", "diagnosis", "explanation", "waiting"]


def _gate_id(gate) -> str:
    """A Gate's id: its attribute `id` (a mapping's key `id`)."""
    return gate["id"] if isinstance(gate, dict) else gate.id


def test_card_holds_the_explanation(tmp_path, monkeypatch):
    """@prd T-254.1"""
    build(tmp_path, monkeypatch, "IC0", "ICE")
    before(tmp_path)
    monkeypatch.chdir(tmp_path / "main")
    model = importlib.import_module("prdlint.model")
    gates = importlib.import_module("prdlint.gates")

    cards = {}
    for name in ("main", "wt"):
        P = tmp_path / name
        prd = model.load(P / "docs/prd/orders")
        found = [g for g in gates.list_gates(prd, P) if _gate_id(g) == ERROR_CLASS]
        assert len(found) == 1, f"{name}: list_gates holds {len(found)} gates {ERROR_CLASS}"
        cards[name] = gates.card(found[0], prd, P, "docs/prd/orders")

    got = {
        "main": {"keys": list(cards["main"]), "choices": cards["main"]["choices"],
                 "explanation": cards["main"]["explanation"]},
        "wt": {"keys": list(cards["wt"]), "explanation": cards["wt"]["explanation"]},
    }
    want = {
        "main": {"keys": CARD_KEYS, "choices": ["confirm", "correct", "question"],
                 "explanation": "An import of a file of 1,200 rows stored 1,000 of them."},
        "wt": {"keys": CARD_KEYS, "explanation": None},
    }
    assert json.loads(json.dumps(got, default=str)) == want


def test_list_json_offers_a_question(tmp_path, monkeypatch):
    """@prd T-254.2"""
    build(tmp_path, monkeypatch, "IC0")
    before(tmp_path)
    r = run_gates(Path(tmp_path / "main"), "list", "docs/prd/orders", "--json")
    assert r.exit == 0, r
    assert r.stdout.endswith("\n") and len(r.stdout.splitlines()) == 1, f"stdout is not one line: {r.stdout!r}"
    doc = json.loads(r.stdout)
    assert isinstance(doc, dict), r.stdout
    assert doc["gates"][0]["id"] == ERROR_CLASS, r.stdout
    assert doc["gates"][0]["choices"] == ["confirm", "correct", "question"], r.stdout
    assert r.stderr == "", r.stderr
