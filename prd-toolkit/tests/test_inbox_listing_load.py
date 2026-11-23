"""E-068: the decision inbox must keep answering in a repository with many worktrees.

Each listing loaded every worktree's PRD (seconds each), and the page asked again every 5 seconds whether or not the
last listing had returned, so the listings piled up and no answer came back. A listing reloads only a worktree whose
PRD folder changed, and the page has one GET /gates out at a time.
"""
import shutil
from pathlib import Path

import pytest
from inbox_fixture import E003, PRD, make_inbox_repo
from prdlint import gates, model
from test_inbox_page import run_page

STARTED = "2000-01-01T00:00:00Z"


def test_a_listing_reloads_only_the_worktree_whose_prd_changed(tmp_path, monkeypatch):
    made = make_inbox_repo(tmp_path)
    repo, second = made["repo"].resolve(), made["second"].resolve()
    state = gates._Inbox(repo, PRD, "orders", "", STARTED)
    first = state.listing()
    assert [Path(g["path"]) for g in first["worktrees"]] == [repo, second]

    loads = []
    real = model.load
    monkeypatch.setattr(model, "load", lambda d: loads.append(Path(d).resolve()) or real(d))

    # nothing changed: the listing is the same, and no PRD is loaded again
    assert state.listing() == first
    assert loads == []

    # an entry recorded in the second worktree: only its PRD is loaded again, and its new gate is listed
    ledger = second / PRD / "errors.md"
    ledger.write_text(ledger.read_text(encoding="utf-8") + E003.replace("E-003", "E-004"), encoding="utf-8")
    after = state.listing()
    assert loads == [(second / PRD).resolve()]
    ids = {Path(g["path"]): [x["id"] for x in g["gates"]] for g in after["worktrees"]}
    assert "error-class:E-004" in ids[second] and "error-class:E-004" not in ids[repo]
    assert after["worktrees"][0] == first["worktrees"][0]


PILE_UP = r"""
// a GET /gates that returns only when the driver lets it, with the listing as it stood when the request was sent
const docOf = (n) => ({ prd: 'orders', started: 't', answers: [], worktrees: [{ path: '/w', branch: 'main', gates: [
  { id: `error-class:E-00${n}`, kind: 'error-class', title: 't', question: 'q', evidence: [], waiting: true }] }] });
let doc = docOf(1);
let out = 0, most = 0, sent = 0;
const held = [];
fetch = (path) => new Promise((resolve) => {
  const body = doc;
  sent++; out++; most = Math.max(most, out);
  held.push(() => { out--; resolve({ status: 200, json: async () => body }); });
});
const tick = () => new Promise((r) => setTimeout(r, 20));
const first = refresh();      // a listing that takes long
await tick();
refresh(); refresh();         // the 5-second timer fires twice before it returns
doc = docOf(2);               // the gates change; then Done asks for the current question
const current = refresh();
await tick();
const during = sent;
while (held.length) { held.shift()(); await tick(); }
await Promise.all([first, current]);
console.log(JSON.stringify({ during, most, fresh: I.raw === JSON.stringify(doc) }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_page_has_one_listing_out_at_a_time_and_a_late_caller_sees_a_listing_sent_after_its_call(tmp_path):
    got = run_page(tmp_path, PILE_UP)
    assert got == {"during": 1, "most": 1, "fresh": True}
