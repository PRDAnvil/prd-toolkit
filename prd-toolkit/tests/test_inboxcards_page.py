"""The decision inbox's error-class card: the explanation first, the diagnosis folded, and Ask a question (inbox-cards)."""
import json
import shutil

import pytest
from test_inbox_page import run_page

DIAGNOSIS = "the loop stops at row 1000"
EXPLANATION = "<b>An import</b> stored 1,000 rows."
CARD = {"id": "error-class:E-001", "kind": "error-class", "title": "The importer stops at row 1000",
        "question": "Proposed class: code bug. Confirm it, or correct it to another class.", "evidence": [],
        "choices": ["confirm", "correct", "question"], "source": "errors.md:3", "areas": ["import"],
        "url": "https://example.com/runs/1001", "class": "code bug", "diagnosis": DIAGNOSIS, "explanation": EXPLANATION,
        "waiting": False}

DRIVER = r"""
// record each listener h() adds, so the driver can type in the card's box and click its buttons
const P = Object.getPrototypeOf(document.createElement('x'));
P.addEventListener = function (type, fn) { (this._on = this._on || {})[type] = fn; };
const sent = [];
route.handler = (path, body) => {
  if (path === '/answer') { sent.push(body); return { status: 200, body: { gate: body.gate, result: { stdout: [], exit: 0 } } }; }
  return { body: { prd: 'orders', started: 't', worktrees: [], answers: [] } };
};
const order = (card) => { const out = []; const walk = (n) => { out.push(n); n.childNodes.forEach(walk); }; walk(card); return out; };
const shape = async (key, g) => {
  const entry = { key, gone: false, wt: { path: '/w', branch: 'main' }, g };
  const card = gateCard(entry, new Map());
  const nodes = order(card);
  const at = (test) => nodes.findIndex(test);
  const explained = at((n) => n.tagName !== '#TEXT' && n.textContent === EXPLANATION && n.childNodes.every((c) => c.tagName === '#TEXT'));
  const details = nodes.filter((n) => n.tagName === 'DETAILS');
  const summary = details.map((d) => d.childNodes.filter((c) => c.tagName === 'SUMMARY').map((c) => c.textContent));
  const label = at((n) => n.tagName === 'SPAN' && n.textContent === 'Diagnosis');
  const shown = label >= 0 ? nodes[label].parentNode.childNodes[nodes[label].parentNode.childNodes.indexOf(nodes[label]) + 1] : null;
  const ask = nodes.filter((n) => n.tagName === 'BUTTON' && n.textContent === 'Ask a question');
  const box = nodes.find((n) => n.tagName === 'TEXTAREA');
  box._on.input({ target: { value: 'why row 1000?' } });
  if (ask.length) ask[0]._on.click();
  await new Promise((r) => setTimeout(r, 50));
  return {
    explained, details: details.map((d) => at((n) => n === d)), summary,
    diagnosisInDetails: details.map((d) => d.childNodes.some((c) => c.tagName !== 'SUMMARY' && c.textContent === DIAGNOSIS)),
    shown: shown ? [shown.className, shown.textContent] : null,
    ask: ask.length, sent: sent.splice(0).map((b) => ({ gate: b.gate, choice: b.choice, words: b.words })),
    html: nodes.filter((n) => Object.prototype.hasOwnProperty.call(n, 'innerHTML') || Object.prototype.hasOwnProperty.call(n, 'outerHTML')).length,
    bold: nodes.filter((n) => n.tagName === 'B').length,
  };
};
await refresh();  // the page lists before any card exists, as it does on load
const first = await shape('k1', FIRST);
const second = await shape('k1b', SECOND);
console.log(JSON.stringify({ first, second }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_error_class_card_shows_its_explanation_first_and_takes_a_question(tmp_path):
    """@prd T-254.8"""
    head = (f"const EXPLANATION = {json.dumps(EXPLANATION)};\nconst DIAGNOSIS = {json.dumps(DIAGNOSIS)};\n"
            f"const FIRST = {json.dumps(CARD)};\nconst SECOND = {json.dumps({**CARD, 'explanation': None})};\n")
    got = run_page(tmp_path, head + DRIVER)
    first, second = got["first"], got["second"]
    # with an explanation: its text, as text, before a details element whose summary reads Diagnosis and holds it
    assert first["explained"] >= 0
    assert len(first["details"]) == 1 and first["explained"] < first["details"][0]
    assert first["summary"] == [["Diagnosis"]] and first["diagnosisInDetails"] == [True]
    # with none: the diagnosis as the card showed it before, a Diagnosis fact, and no details element
    assert second["explained"] == -1 and second["details"] == []
    assert second["shown"] == ["gv", DIAGNOSIS]
    # both: an Ask a question button that sends the choice question with the words typed on the card
    for card in (first, second):
        assert card["ask"] == 1
        assert card["sent"] == [{"gate": "error-class:E-001", "choice": "question", "words": "why row 1000?"}]
        assert card["html"] == 0 and card["bold"] == 0
