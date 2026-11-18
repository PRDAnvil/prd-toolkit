"""inbox-cards: an error-class answer runs in its card's worktree alone (FR-071, AC-071.2)."""
from __future__ import annotations

from inbox_cards_support import build, git, groups, make_inbox, orders, resolved

E001 = "error-class:E-001"


def test_answer_commits_in_the_cards_worktree_alone(tmp_path, monkeypatch):
    """@prd T-071.4"""
    build(tmp_path, monkeypatch, "IC0")
    main, wt = tmp_path / "main", tmp_path / "wt"
    monkeypatch.chdir(main)
    MAIN, WT = resolved(main), resolved(wt)

    wt_errors = orders(wt) / "errors.md"
    wt_errors_before = wt_errors.read_bytes()
    main_before = git(main, "rev-parse", "main")
    other_before = git(main, "rev-parse", "other")
    assert main_before.exit == 0, main_before.stderr
    assert other_before.exit == 0, other_before.stderr

    server = make_inbox(orders(main))[0]
    try:
        L1 = server.state.listing()
        cards = [c for c in L1["worktrees"][0]["gates"] if c["id"] == E001]
        assert cards, f"the first group holds no card {E001}: {groups(L1)}"
        card = cards[0]
        status, result = server.state.answer({
            "worktree": MAIN, "gate": E001, "question": card["question"], "choice": "confirm", "words": "",
        })
        L2 = server.state.listing()
    finally:
        server.server_close()

    got = {"status": status, "exit": result["result"]["exit"], "before": groups(L1), "after": groups(L2)}
    assert got == {
        "status": 200,
        "exit": 0,
        "before": [
            {"path": MAIN, "branch": "main", "ids": [E001]},
            {"path": WT, "branch": "other", "ids": []},
        ],
        "after": [
            {"path": MAIN, "branch": "main", "ids": []},
            {"path": WT, "branch": "other", "ids": []},
        ],
    }

    # effects
    count = git(main, "rev-list", "--count", f"{main_before.stdout.strip()}..main")
    assert count.exit == 0, count.stderr
    assert count.stdout == "1\n"
    subject = git(main, "log", "-1", "--format=%s", "main")
    assert subject.exit == 0, subject.stderr
    assert subject.stdout == "docs(prd): confirm E-001\n"
    other_after = git(main, "rev-parse", "other")
    assert other_after.exit == 0, other_after.stderr
    assert other_after.stdout == other_before.stdout

    assert wt_errors.read_bytes() == wt_errors_before
    status_wt = git(wt, "status", "--porcelain")
    assert status_wt.exit == 0, status_wt.stderr
    assert status_wt.stdout == ""
