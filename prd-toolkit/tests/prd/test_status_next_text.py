"""status-next FR-040: the Next part comes first in the text report (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, keys_at, next_items_json, next_part_lines, one_json_line, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0")
def test_next_part_first_with_numbered_items_and_run_lines(scratch):
    """@prd T-040.1"""
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


@given_steps("N0")
def test_thirteen_parts_follow_the_next_part_unchanged(scratch):
    """@prd T-040.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert runs[0].stdout.splitlines() == [
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
        "## Header",
        "",
        "PRD: .",
        "version 1.0.0",
        "status Approved",
        "",
        "## Requirements",
        "",
        "import: approved 1, built 1, live 1, verified 1",
        "reports: approved 1, live 2",
        "",
        "## Areas",
        "",
        "import: pack service (default), output language en",
        "reports: pack service (default), output language en",
        "",
        "## Adoption map",
        "",
        "Not applicable: new project",
        "",
        "## Not built",
        "",
        "FR-001 Refuse a file with no header (features/import.md)",
        "FR-005 Print the monthly report (features/reports.md)",
        "",
        "## Not verified",
        "",
        "FR-002 Skip a duplicate order (features/import.md)",
        "",
        "## Open errors",
        "",
        "None.",
        "",
        "## Upstreams",
        "",
        "None.",
        "",
        "## Consumers",
        "",
        "None.",
        "",
        "## Change sets",
        "",
        "None.",
        "",
        "## CI",
        "",
        "stale: CLAUDE.md; run prd_block.py docs/prd/orders",
        "stale: docs/prd/orders/README.md; run prd_block.py docs/prd/orders",
        "stale: docs/prd/README.md; run prd_block.py docs/prd/orders",
        "",
        "## Deployed",
        "",
        "None.",
        "",
        "## Matrix",
        "",
        "FR-001: T-001.1 integration build cited",
        "FR-002: T-002.1 integration build cited",
        "FR-003: T-003.1 integration build cited",
        "FR-004: T-004.1 integration build cited",
        "FR-005: T-005.1 integration build cited; T-005.2 judged build cited",
        "FR-006: T-006.1 integration build cited",
        "FR-007: T-007.1 integration build cited",
    ]
    assert keys_at(one_json_line(runs[1].stdout), "") == ["interface", "kind", "prd", "version", "items"]
