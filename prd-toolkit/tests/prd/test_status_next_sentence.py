"""status-next FR-047: a sentence ends with one full stop (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, next_items_json, next_part_lines, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0", "NE3")
def test_a_title_ending_in_a_question_mark_gets_no_full_stop(scratch):
    """@prd T-047.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. E-001 is open (confirmed): Why does the importer stop at row 1000?",
        "  run: /prd-toolkit:prd-error E-001",
        "2. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "3. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "4. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "5. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": "E-001", "text": "E-001 is open (confirmed): Why does the importer stop at row 1000?", "kind": "error-open", "ids": ["E-001"], "area": null, "command": "/prd-toolkit:prd-error E-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
