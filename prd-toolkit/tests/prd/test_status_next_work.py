"""status-next FR-045: Work, furthest along first (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, next_items_json, next_part_lines, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0", "NV2")
def test_one_deploy_item_counts_every_verified_block(scratch):
    """@prd T-045.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. 2 requirements are verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "2. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "3. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "2 requirements are verified and not live.", "kind": "deploy", "ids": ["FR-002", "FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NB2")
def test_one_verify_item_per_area_joins_two_ids_with_and(scratch):
    """@prd T-045.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "2. FR-001 and FR-002 are built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-001 FR-002",
        "3. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 and FR-002 are built and not verified.", "kind": "verify", "ids": ["FR-001", "FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001 FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NB3")
def test_one_build_item_per_area_joins_three_ids_with_commas_and_and(scratch):
    """@prd T-045.3"""
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
        "4. FR-005, FR-006 and FR-007 are approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005 FR-006 FR-007",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005, FR-006 and FR-007 are approved and not built.", "kind": "build", "ids": ["FR-005", "FR-006", "FR-007"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005 FR-006 FR-007", "waits_on": "agent"}
""")


@given_steps("N0", "NA1")
def test_an_adopt_item_per_row_not_adopted_and_without_a_gate(scratch):
    """@prd T-045.4"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Adopt area billing waits for your answer.",
        "2. 1 requirement is verified and not live.",
        "  run: /prd-toolkit:prd-deploy",
        "3. FR-002 is built and not verified.",
        "  run: /prd-toolkit:prd-build import FR-002",
        "4. FR-001 is approved and not built.",
        "  run: /prd-toolkit:prd-build import FR-001",
        "5. FR-005 is approved and not built.",
        "  run: /prd-toolkit:prd-build reports FR-005",
        "6. Area export is not adopted (extracted).",
        "  run: /prd-toolkit:prd-adopt export",
        "7. Area audit is not adopted (not started).",
        "  run: /prd-toolkit:prd-adopt audit",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": "adoption:billing", "text": "Adopt area billing waits for your answer.", "kind": "gate", "ids": [], "area": "billing", "command": null, "waits_on": "you"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Area export is not adopted (extracted).", "kind": "adopt", "ids": [], "area": "export", "command": "/prd-toolkit:prd-adopt export", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "Area audit is not adopted (not started).", "kind": "adopt", "ids": [], "area": "audit", "command": "/prd-toolkit:prd-adopt audit", "waits_on": "agent"}
""")
