"""status-next FR-041: the Next items in the JSON document (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, keys_at, next_items_json, next_part_lines, one_json_line, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)

ITEM_KEYS = ["part", "id", "text", "kind", "ids", "area", "command", "waits_on"]


@given_steps("N0")
def test_next_items_come_first_with_their_eight_keys(scratch):
    """@prd T-041.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "2. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "3. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "4. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
    doc = one_json_line(runs[1].stdout)
    assert keys_at(doc, "items.0") == ITEM_KEYS
    assert keys_at(doc, "items.3") == ITEM_KEYS


@given_steps("N0")
def test_other_items_keep_part_id_text_and_the_document_keeps_its_keys(scratch):
    """@prd T-041.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert runs[0].stdout.splitlines()[:1] == ["## Next"]
    doc = one_json_line(runs[1].stdout)
    assert doc == {
        "interface": 1,
        "kind": "status",
        "prd": "orders",
        "version": "1.0.0",
        "items": json_lines(r"""
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
{"part": "Header", "id": null, "text": "PRD: .\nversion 1.0.0\nstatus Approved"}
{"part": "Requirements", "id": null, "text": "import: approved 1, built 1, live 1, verified 1"}
{"part": "Requirements", "id": null, "text": "reports: approved 1, live 2"}
{"part": "Areas", "id": "import", "text": "import: pack service (default), output language en"}
{"part": "Areas", "id": "reports", "text": "reports: pack service (default), output language en"}
{"part": "Adoption map", "id": null, "text": "Not applicable: new project"}
{"part": "Not built", "id": "FR-001", "text": "FR-001 Refuse a file with no header (features/import.md)"}
{"part": "Not built", "id": "FR-005", "text": "FR-005 Print the monthly report (features/reports.md)"}
{"part": "Not verified", "id": "FR-002", "text": "FR-002 Skip a duplicate order (features/import.md)"}
{"part": "Open errors", "id": null, "text": "None."}
{"part": "Upstreams", "id": null, "text": "None."}
{"part": "Consumers", "id": null, "text": "None."}
{"part": "Change sets", "id": null, "text": "None."}
{"part": "CI", "id": null, "text": "stale: CLAUDE.md; run prd_block.py docs/prd/orders"}
{"part": "CI", "id": null, "text": "stale: docs/prd/orders/README.md; run prd_block.py docs/prd/orders"}
{"part": "CI", "id": null, "text": "stale: docs/prd/README.md; run prd_block.py docs/prd/orders"}
{"part": "Deployed", "id": null, "text": "None."}
{"part": "Matrix", "id": "FR-001", "text": "FR-001: T-001.1 integration build cited"}
{"part": "Matrix", "id": "FR-002", "text": "FR-002: T-002.1 integration build cited"}
{"part": "Matrix", "id": "FR-003", "text": "FR-003: T-003.1 integration build cited"}
{"part": "Matrix", "id": "FR-004", "text": "FR-004: T-004.1 integration build cited"}
{"part": "Matrix", "id": "FR-005", "text": "FR-005: T-005.1 integration build cited; T-005.2 judged build cited"}
{"part": "Matrix", "id": "FR-006", "text": "FR-006: T-006.1 integration build cited"}
{"part": "Matrix", "id": "FR-007", "text": "FR-007: T-007.1 integration build cited"}
"""),
    }
    assert keys_at(doc, "") == ["interface", "kind", "prd", "version", "items"]
    assert keys_at(doc, "items.4") == ["part", "id", "text"]
    assert keys_at(doc, "items.27") == ["part", "id", "text"]
