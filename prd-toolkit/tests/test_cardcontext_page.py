"""The decision inbox card's area line and URL link (card-context)."""
import shutil

import pytest
from test_inbox_page import run_page

# the T-067.3 card of error-class:E-001 (its choices and explanation as inbox-cards FR-254 gives them), with two areas
CARD_E001 = {"id": "error-class:E-001", "kind": "error-class", "title": "The importer stops at row 1000",
             "question": "Proposed class: code bug. Confirm it, or correct it to another class.", "evidence": [],
             "choices": ["confirm", "correct", "question"], "source": "errors.md:3", "areas": ["import", "reports"],
             "url": "https://example.com/runs/1001", "class": "code bug", "diagnosis": "", "explanation": None,
             "waiting": False}
CARD_E004 = {**CARD_E001, "id": "error-class:E-004", "title": "A crash with no requirement", "source": "errors.md:20",
             "areas": [], "url": None}

DRIVER = r"""
const entry = (key, g) => ({ key, gone: false, wt: { path: '/w', branch: 'main' }, g });
const shape = (card) => {
  const kids = card.childNodes;
  const title = kids.findIndex((n) => n.tagName === 'H3');
  const next = kids[title + 1];
  const links = card.all((n) => n.tagName === 'A').map((a) => ({ text: a.textContent, href: a.getAttribute('href'),
    target: a.getAttribute('target'), rel: a.getAttribute('rel') }));
  return { tag: card.tagName, afterTitle: next ? next.textContent : null,
    afterTitleKids: next ? next.childNodes.map((n) => n.tagName) : null, links };
};
console.log(JSON.stringify({ first: shape(gateCard(entry('k1', FIRST), new Map())), second: shape(gateCard(entry('k2', SECOND), new Map())) }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_a_card_shows_its_areas_under_the_title_and_links_its_url(tmp_path):
    """@prd T-067.4"""
    import json

    got = run_page(tmp_path, f"const FIRST = {json.dumps(CARD_E001)};\nconst SECOND = {json.dumps(CARD_E004)};\n" + DRIVER)
    first, second = got["first"], got["second"]
    assert first["tag"] == "SECTION" and second["tag"] == "SECTION"
    # directly after the h3 title: the Area line, its text a text node only (set as text, never as HTML)
    assert first["afterTitle"] == "Area: import, reports" and first["afterTitleKids"] == []
    assert second["afterTitle"] == "Area: none" and second["afterTitleKids"] == []
    assert first["links"] == [{"text": "https://example.com/runs/1001", "href": "https://example.com/runs/1001",
                               "target": "_blank", "rel": "noopener"}]
    assert not [a for a in second["links"] if (a["href"] or "").startswith(("http://", "https://"))]
