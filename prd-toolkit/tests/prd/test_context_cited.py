"""The Cited part and the Upstream contracts part (features/context.md FR-210, FR-211)."""
from __future__ import annotations

from context_support import (
    CXC, CXK, CXL, N0, Scratch, assert_relative_order, given, one_json, part, run,
    scratch, titles,  # noqa: F401  (scratch is the fixture)
)

NFR_HEADING = "### NFR-008 Import speed"
A01_ROW = "| A-01 | Import files are UTF-8 | open |"


def _entries(out: str, id_: str) -> list[dict]:
    return [entry for entry in one_json(out)["parts"] if entry.get("id") == id_]


@given(CXC)
def test_cited_part(scratch: Scratch):
    """@prd T-210.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001,NFR-008")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Cited") == [
        "## Cited",
        "",
        NFR_HEADING,
        "Status: approved",
        "Acceptance (EARS):",
        "- AC-008.1 The importer shall store a 10,000-row file in under 60 seconds.",
        "Errors: -",
        "Tests: T-008.1 [integration]  (test-cases/nfr.yaml)",
        "",
        "IMPORT_NO_HEADER:",
        "  meaning: The import file has no header line.",
        "  when: The first line of the file is not the header.",
        "  status: 2",
        "  message: The import file has no header line.",
        "  log_level: error",
        "  retryable: false",
        "  metric: orders_import_no_header_total",
        "",
        "IMPORT_BAD_DATE: not in contracts/errors.yaml",
        "",
        "IMPORT_EMPTY: not in contracts/errors.yaml",
        "",
        "importer:",
        "  invocation: python import.py",
        "  exit: 2",
        "",
        "| ID | Assumption | Status |",
        "|---|---|---|",
        A01_ROW,
        "",
    ]
    assert r2.out.splitlines().count(NFR_HEADING) == 1
    assert NFR_HEADING in part(r2.out, "Requirements")
    assert NFR_HEADING not in part(r2.out, "Cited")


@given(CXC)
def test_cited_error_codes(scratch: Scratch):
    """@prd T-210.2"""
    r = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    assert r.exit == 0
    assert_relative_order(r.out, [
        "## Cited", "IMPORT_NO_HEADER:", "  meaning: The import file has no header line.",
        "  when: The first line of the file is not the header.", "  status: 2",
        "  message: The import file has no header line.", "  log_level: error", "  retryable: false",
        "  metric: orders_import_no_header_total", "IMPORT_BAD_DATE: not in contracts/errors.yaml",
        "IMPORT_EMPTY: not in contracts/errors.yaml", "## Known defects",
    ])


@given(CXC)
def test_cited_custom_contract(scratch: Scratch):
    """@prd T-210.3"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --json")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert_relative_order(r1.out, ["## Cited", "importer:", "  invocation: python import.py", "  exit: 2",
                                   "## Known defects"])
    assert _entries(r2.out, "cli:importer") == [{
        "title": "Cited", "id": "cli:importer", "file": "contracts/cli.yaml", "line": 1,
        "text": "importer:\n  invocation: python import.py\n  exit: 2", "stale": False, "counted": True, "moved": None,
    }]


@given(CXC)
def test_cited_assumption(scratch: Scratch):
    """@prd T-210.4"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-002")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert_relative_order(r1.out, ["## Cited", "| ID | Assumption | Status |", "|---|---|---|", A01_ROW,
                                   "## Known defects"])
    assert A01_ROW not in r2.out


@given(CXK)
def test_cited_pack_target(scratch: Scratch):
    """@prd T-210.5"""
    r1 = run(scratch, "python CTX docs/prd/orders --area reports --req FR-005 --json")
    r2 = run(scratch, "python CTX docs/prd/orders --area reports --req FR-006 --json")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert _entries(r1.out, "outline:guide") == [{
        "title": "Cited", "id": "outline:guide", "file": "contracts/outline.yaml", "line": 1,
        "text": "guide:\n  title: Install guide", "stale": False, "counted": True, "moved": None,
    }]
    assert _entries(r2.out, "outline:guide") == []


@given(N0)
def test_cited_none(scratch: Scratch):
    """@prd T-210.6"""
    r = run(scratch, "python CTX docs/prd/orders --area import --req FR-002")
    assert r.exit == 0
    assert part(r.out, "Cited") == ["## Cited", "", "None.", ""]


@given(N0)
def test_no_links_md_no_upstream_part(scratch: Scratch):
    """@prd T-211.1"""
    for spec in ("python CTX docs/prd/orders --area import --req FR-001",
                 "python CTX docs/prd/orders --area import --for implement"):
        r = run(scratch, spec)
        assert r.exit == 0, spec
        assert r.err_b == b"", spec
        assert "## Upstream contracts" not in r.out, spec


@given(CXL)
def test_upstream_contracts_part(scratch: Scratch):
    """@prd T-211.2"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-002")
    r3 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --json")
    for r in (r1, r2, r3):
        assert r.exit == 0
        assert r.err_b == b""
    assert titles(r1.out) == ["## Header", "## Stack", "## Glossary", "## Requirements", "## Cited",
                              "## Upstream contracts", "## Known defects", "## Open questions", "## History"]
    assert part(r1.out, "Upstream contracts") == [
        "## Upstream contracts", "", "op:greet/hello: not in the snapshot", "",
    ]
    assert part(r2.out, "Upstream contracts") == ["## Upstream contracts", "", "None.", ""]
    assert {
        "title": "Upstream contracts", "id": "op:greet/hello", "file": "contracts/upstream/greet", "line": None,
        "text": "op:greet/hello: not in the snapshot", "stale": False, "counted": True, "moved": None,
    } in one_json(r3.out)["parts"]
