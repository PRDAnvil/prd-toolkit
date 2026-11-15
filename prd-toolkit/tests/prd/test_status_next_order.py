"""status-next FR-042: the order of the items, each listed once (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, next_items_json, next_part_lines, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0", "NL1", "NT2", "NR1", "NE1", "NQ1", "NQ2", "ND1", "NA1")
def test_tiers_and_kinds_in_order_with_every_kind_but_idle(scratch):
    """@prd T-042.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Lint reports 1 error; the first is contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9).",
        "2. Trace reports 2 findings; the first is features/import.md:22: status-current: FR-003 is verified but T-003.1 has no citing test.",
        "3. The deploy to staging stopped: run 20261110T090000Z-all stopped (failed) at step 1.",
        "  run: /prd-toolkit:prd-deploy",
        "4. E-001 is open (confirmed): The importer stops at row 1000.",
        "  run: /prd-toolkit:prd-error E-001",
        "5. E-002 is open (unclassified): A monthly report printed no total.",
        "  run: /prd-toolkit:prd-error E-002",
        "6. Adopt area billing waits for your answer.",
        "7. A-01 waits on Sample Owner: Reports count only shipped orders.",
        "8. An open question waits: Who signs off the monthly report?",
        "9. The PRD is a draft at version 0.3.0, not yet approved.",
        "  run: /prd-toolkit:prd-new",
        "10. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "11. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "12. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "13. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "14. Area export is not adopted (extracted).",
        "  run: /prd-toolkit:prd-adopt export",
        "15. Area audit is not adopted (not started).",
        "  run: /prd-toolkit:prd-adopt audit",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "Lint reports 1 error; the first is contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9).", "kind": "lint", "ids": [], "area": null, "command": null, "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Trace reports 2 findings; the first is features/import.md:22: status-current: FR-003 is verified but T-003.1 has no citing test.", "kind": "lint", "ids": [], "area": null, "command": null, "waits_on": "agent"}
{"part": "Next", "id": null, "text": "The deploy to staging stopped: run 20261110T090000Z-all stopped (failed) at step 1.", "kind": "deploy-stopped", "ids": [], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": "E-001", "text": "E-001 is open (confirmed): The importer stops at row 1000.", "kind": "error-open", "ids": ["E-001"], "area": null, "command": "/prd-toolkit:prd-error E-001", "waits_on": "agent"}
{"part": "Next", "id": "E-002", "text": "E-002 is open (unclassified): A monthly report printed no total.", "kind": "error-open", "ids": ["E-002"], "area": null, "command": "/prd-toolkit:prd-error E-002", "waits_on": "agent"}
{"part": "Next", "id": "adoption:billing", "text": "Adopt area billing waits for your answer.", "kind": "gate", "ids": [], "area": "billing", "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "A-01 waits on Sample Owner: Reports count only shipped orders.", "kind": "question", "ids": ["A-01"], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "An open question waits: Who signs off the monthly report?", "kind": "question", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "The PRD is a draft at version 0.3.0, not yet approved.", "kind": "draft", "ids": [], "area": null, "command": "/prd-toolkit:prd-new", "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Area export is not adopted (extracted).", "kind": "adopt", "ids": [], "area": "export", "command": "/prd-toolkit:prd-adopt export", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Area audit is not adopted (not started).", "kind": "adopt", "ids": [], "area": "audit", "command": "/prd-toolkit:prd-adopt audit", "waits_on": "agent"}
""")


@given_steps("N0", "NE2")
def test_a_proposed_entry_is_only_its_gate_item(scratch):
    """@prd T-042.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The importer stops at row 1000 waits for your answer.",
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
    assert "E-001 proposed code bug — The importer stops at row 1000" in runs[0].stdout.splitlines()
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": "error-class:E-001", "text": "The importer stops at row 1000 waits for your answer.", "kind": "gate", "ids": ["E-001"], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NR3")
def test_a_run_stopped_at_an_unconfirmed_human_step_is_only_its_gate_item(scratch):
    """@prd T-042.3"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Run 20261111T090000Z-all step 2: Approve production waits for your answer.",
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
    assert "production: run 20261111T090000Z-all stopped (human) at step 2" in runs[0].stdout.splitlines()
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": "deploy-step:20261111T090000Z-all:2", "text": "Run 20261111T090000Z-all step 2: Approve production waits for your answer.", "kind": "gate", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
