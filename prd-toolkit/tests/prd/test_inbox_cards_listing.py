"""inbox-cards: the inbox shows an error entry's card in the first worktree that holds it (FR-071, AC-071.1)."""
from __future__ import annotations

from inbox_cards_support import build, groups, listing, orders, resolved

E001 = "error-class:E-001"


def test_first_group_holds_the_card(tmp_path, monkeypatch):
    """@prd T-071.1"""
    build(tmp_path, monkeypatch, "IC0")
    monkeypatch.chdir(tmp_path / "main")
    MAIN, WT = resolved(tmp_path / "main"), resolved(tmp_path / "wt")

    L1 = listing(orders(tmp_path / "main"))
    L2 = listing(orders(tmp_path / "wt"))
    got = {"first": groups(L1), "second": groups(L2)}

    assert got == {
        "first": [
            {"path": MAIN, "branch": "main", "ids": [E001]},
            {"path": WT, "branch": "other", "ids": []},
        ],
        "second": [
            {"path": WT, "branch": "other", "ids": [E001]},
            {"path": MAIN, "branch": "main", "ids": []},
        ],
    }


def _later(G: list[dict]) -> dict:
    return {
        "count": len(G),
        "first": G[0],
        "later_ids": [g["ids"] for g in G[1:]],
        "later_paths": sorted(g["path"] for g in G[1:]),
    }


def test_first_other_group_holding_the_entry(tmp_path, monkeypatch):
    """@prd T-071.2"""
    build(tmp_path, monkeypatch, "IC0", "IC2", "ICN")
    monkeypatch.chdir(tmp_path / "main")
    MAIN, WT, WT2 = (resolved(tmp_path / name) for name in ("main", "wt", "wt2"))

    got = _later(groups(listing(orders(tmp_path / "main"))))

    assert got == {
        "count": 3,
        "first": {"path": MAIN, "branch": "main", "ids": []},
        "later_ids": [[E001], []],
        "later_paths": [WT, WT2],
    }


def test_another_title_or_detected_is_another_entry(tmp_path, monkeypatch):
    """@prd T-071.3"""
    build(tmp_path, monkeypatch, "IC0", "IC2", "ICT", "ICD")
    monkeypatch.chdir(tmp_path / "main")
    MAIN, WT, WT2 = (resolved(tmp_path / name) for name in ("main", "wt", "wt2"))

    got = _later(groups(listing(orders(tmp_path / "main"))))

    assert got == {
        "count": 3,
        "first": {"path": MAIN, "branch": "main", "ids": [E001]},
        "later_ids": [[E001], [E001]],
        "later_paths": [WT, WT2],
    }
