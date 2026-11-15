"""status-next FR-043: Broken, what must be fixed before anything else is trusted (test-cases/status-next.yaml)."""
from status_next_support import (AT_PRD, given_steps, json_at, json_lines, next_items_json, next_part_lines,
                                 one_json_line, orders, run)
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0", "NL2")
def test_lint_item_counts_errors_only(scratch):
    """@prd T-043.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", "."), run(folder, "LINT", ".")]
    for r in runs:
        assert r.stderr == "", r
    assert runs[0].exit == 0, runs[0]
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Lint reports 2 errors; the first is contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9).",
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
    assert runs[1].exit == 0, runs[1]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "Lint reports 2 errors; the first is contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9).", "kind": "lint", "ids": [], "area": null, "command": null, "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
    assert runs[2].exit == 1, runs[2]
    assert runs[2].stdout.splitlines() == [
        "contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9)",
        "test-cases/import.yaml:56: id-unique: duplicate key 'T-001.1' (first at line 1, again at line 56)",
        "test-cases/reports.yaml:27: warn: judged-case: T-005.2: threshold 0.9 needs all 2 items (1 of 2 is 0.5); write 0.5 to allow one miss, or 1.0",
    ]


@given_steps("N0", "NT1")
def test_trace_item_after_the_lint_item(scratch):
    """@prd T-043.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", "."), run(folder, "TRACE", ".")]
    for r in runs:
        assert r.stderr == "", r
    finding = ("features/import.md:15: t-implemented: T-002.1 (FR-002) is cited by no test; add `"
               + AT_PRD + " T-002.1` to the test that proves it")
    assert runs[0].exit == 0, runs[0]
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Trace reports 1 finding; the first is " + finding + ".",
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
    assert runs[1].exit == 0, runs[1]
    assert next_items_json(runs[1].stdout) == [
        {"part": "Next", "id": None, "text": "Trace reports 1 finding; the first is " + finding + ".", "kind": "lint",
         "ids": [], "area": None, "command": None, "waits_on": "agent"},
        *json_lines(r"""
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
"""),
    ]
    assert runs[2].exit == 1, runs[2]
    assert runs[2].stdout.splitlines() == [finding]


@given_steps("N0X")
def test_no_trace_item_outside_a_git_checkout(scratch):
    """@prd T-043.3"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", "."), run(folder, "TRACE", ".")]
    for r in runs:
        assert r.stderr == "", r
    assert runs[0].exit == 0, runs[0]
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
    assert "## Matrix" in runs[0].stdout.splitlines()
    assert runs[1].exit == 0, runs[1]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
    assert runs[2].exit == 1, runs[2]


@given_steps("N0", "NR1")
def test_a_failed_run_is_a_deploy_stopped_item(scratch):
    """@prd T-043.4"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The deploy to staging stopped: run 20261110T090000Z-all stopped (failed) at step 1.",
        "  run: /prd-toolkit:prd-deploy",
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
    assert "staging: run 20261110T090000Z-all stopped (failed) at step 1" in runs[0].stdout.splitlines()
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "The deploy to staging stopped: run 20261110T090000Z-all stopped (failed) at step 1.", "kind": "deploy-stopped", "ids": [], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NR2")
def test_an_unfinished_run_is_a_deploy_stopped_item(scratch):
    """@prd T-043.5"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The deploy to staging stopped: run 20261110T100000Z-all stopped (unfinished) at step 1.",
        "  run: /prd-toolkit:prd-deploy",
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
    assert "staging: run 20261110T100000Z-all stopped (unfinished) at step 1" in runs[0].stdout.splitlines()
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "The deploy to staging stopped: run 20261110T100000Z-all stopped (unfinished) at step 1.", "kind": "deploy-stopped", "ids": [], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NE1")
def test_confirmed_and_unclassified_entries_are_error_open_items_in_id_order(scratch):
    """@prd T-043.6"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. E-001 is open (confirmed): The importer stops at row 1000.",
        "  run: /prd-toolkit:prd-error E-001",
        "2. E-002 is open (unclassified): A monthly report printed no total.",
        "  run: /prd-toolkit:prd-error E-002",
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
{"part": "Next", "id": "E-001", "text": "E-001 is open (confirmed): The importer stops at row 1000.", "kind": "error-open", "ids": ["E-001"], "area": null, "command": "/prd-toolkit:prd-error E-001", "waits_on": "agent"}
{"part": "Next", "id": "E-002", "text": "E-002 is open (unclassified): A monthly report printed no total.", "kind": "error-open", "ids": ["E-002"], "area": null, "command": "/prd-toolkit:prd-error E-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")


@given_steps("N0", "NL1")
def test_lint_item_quotes_the_path_inside_the_prd_folder_from_the_repository_root(scratch):
    """@prd T-043.7"""
    runs = [
        run(scratch, "STATUS", "docs/prd/orders"),
        run(scratch, "STATUS", "--json", "docs/prd/orders"),
        run(scratch, "LINT", "docs/prd/orders"),
        run(scratch, "LINT", "--json", "docs/prd/orders"),
    ]
    for r in runs:
        assert r.stderr == "", r
    assert runs[0].exit == 0, runs[0]
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Lint reports 1 error; the first is contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9).",
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
    assert runs[1].exit == 0, runs[1]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "Lint reports 1 error; the first is contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' (first at line 1, again at line 9).", "kind": "lint", "ids": [], "area": null, "command": null, "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
    assert runs[2].exit == 1, runs[2]
    assert ("docs/prd/orders/contracts/errors.yaml:9: contracts-valid: duplicate key 'IMPORT_NO_HEADER' "
            "(first at line 1, again at line 9)") in runs[2].stdout.splitlines()
    assert runs[3].exit == 1, runs[3]
    doc = one_json_line(runs[3].stdout)
    assert json_at(doc, "findings.0.file") == "contracts/errors.yaml"
    assert json_at(doc, "findings.0.line") == 9


@given_steps("N0", "NR3", "NR5")
def test_a_confirmed_human_step_not_resumed_is_a_deploy_stopped_item(scratch):
    """@prd T-043.8"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", "."), run(folder, "GATES", "list", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. The deploy to production stopped: run 20261111T090000Z-all stopped (human) at step 2.",
        "  run: /prd-toolkit:prd-deploy",
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
{"part": "Next", "id": null, "text": "The deploy to production stopped: run 20261111T090000Z-all stopped (human) at step 2.", "kind": "deploy-stopped", "ids": [], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "1 requirement is verified and not live.", "kind": "deploy", "ids": ["FR-003"], "area": null, "command": "/prd-toolkit:prd-deploy", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-002 is built and not verified.", "kind": "verify", "ids": ["FR-002"], "area": "import", "command": "/prd-toolkit:prd-build import FR-002", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-001 is approved and not built.", "kind": "build", "ids": ["FR-001"], "area": "import", "command": "/prd-toolkit:prd-build import FR-001", "waits_on": "agent"}
{"part": "Next", "id": null, "text": "FR-005 is approved and not built.", "kind": "build", "ids": ["FR-005"], "area": "reports", "command": "/prd-toolkit:prd-build reports FR-005", "waits_on": "agent"}
""")
    assert runs[2].stdout == ""
