"""status-next FR-044: Waiting on you, the decisions only the owner can make (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, next_items_json, next_part_lines, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0", "NE2", "NR3", "NA1")
def test_one_gate_item_per_listed_gate_in_gates_list_order(scratch):
    """@prd T-044.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", "."), run(folder, "GATES", "list", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The importer stops at row 1000 waits for your answer.",
        "2. Run 20261111T090000Z-all step 2: Approve production waits for your answer.",
        "3. Adopt area billing waits for your answer.",
        "4. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "5. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "6. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "7. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "8. Area export is not adopted (extracted).",
        "  run: /prd-toolkit:prd-adopt export",
        "9. Area audit is not adopted (not started).",
        "  run: /prd-toolkit:prd-adopt audit",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": "error-class:E-001", "text": "The importer stops at row 1000 waits for your answer.", "kind": "gate", "ids": ["E-001"], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": "deploy-step:20261111T090000Z-all:2", "text": "Run 20261111T090000Z-all step 2: Approve production waits for your answer.", "kind": "gate", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": "adoption:billing", "text": "Adopt area billing waits for your answer.", "kind": "gate", "ids": [], "area": "billing", "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Area export is not adopted (extracted).", "kind": "adopt", "ids": [], "area": "export", "command": "/prd-toolkit:prd-adopt export", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Area audit is not adopted (not started).", "kind": "adopt", "ids": [], "area": "audit", "command": "/prd-toolkit:prd-adopt audit", "waits_on": "agent"}
""")
    assert runs[2].stdout.splitlines() == [
        "error-class:E-001 The importer stops at row 1000",
        "deploy-step:20261111T090000Z-all:2 Run 20261111T090000Z-all step 2: Approve production",
        "adoption:billing Adopt area billing",
    ]


@given_steps("N0", "NR1", "NR4")
def test_an_unreadable_run_log_is_its_gate_item_and_the_older_failed_run_stays(scratch):
    """@prd T-044.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The deploy to staging stopped: run 20261110T090000Z-all stopped (failed) at step 1.",
        "  run: /prd-toolkit:prd-deploy",
        "2. run log 20261112T090000Z-all could not be read waits for your answer.",
        "3. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "4. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "5. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "6. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "The deploy to staging stopped: run 20261110T090000Z-all stopped (failed) at step 1.", "kind": "deploy-stopped", "ids": [], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": "deploy-step:20261112T090000Z-all:unreadable", "text": "run log 20261112T090000Z-all could not be read waits for your answer.", "kind": "gate", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NQ1")
def test_an_awaiting_assumption_is_a_question_item(scratch):
    """@prd T-044.3"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. A-01 waits on Sample Owner: Reports count only shipped orders.",
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
{"part": "Next", "id": null, "text": "A-01 waits on Sample Owner: Reports count only shipped orders.", "kind": "question", "ids": ["A-01"], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NQ2")
def test_an_open_question_is_a_question_item(scratch):
    """@prd T-044.4"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. An open question waits: Who signs off the monthly report?",
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
{"part": "Next", "id": null, "text": "An open question waits: Who signs off the monthly report?", "kind": "question", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "ND1")
def test_a_version_below_one_is_a_draft_item(scratch):
    """@prd T-044.5"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The PRD is a draft at version 0.3.0, not yet approved.",
        "  run: /prd-toolkit:prd-new",
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
{"part": "Next", "id": null, "text": "The PRD is a draft at version 0.3.0, not yet approved.", "kind": "draft", "ids": [], "area": null, "command": "/prd-toolkit:prd-new", "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NQ3")
def test_a_wrapped_question_joins_and_a_plain_line_is_a_question_of_its_own(scratch):
    """@prd T-044.6"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. An open question waits: Who signs off the monthly report before it is sent?",
        "2. An open question waits: Which month is the first one?",
        "3. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "4. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "5. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "6. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "An open question waits: Who signs off the monthly report before it is sent?", "kind": "question", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "An open question waits: Which month is the first one?", "kind": "question", "ids": [], "area": null, "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
