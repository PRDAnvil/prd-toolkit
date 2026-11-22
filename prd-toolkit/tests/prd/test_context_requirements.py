"""Which blocks a pack selects, the Requirements part and the Glossary part (features/context.md FR-206 to FR-209)."""
from __future__ import annotations

import pytest

from context_support import (
    CXA, CXR, N0, KnownFailure, Scratch, assert_json_at, given, headings, in_dir, insert_after, part,
    replace_line, run, scratch, write_lines,  # noqa: F401  (scratch is the fixture)
)

ORDER_ROW = "| order | A customer's request for goods, stored once per order key | purchase |"


@given(CXR)
def test_area_selects_its_blocks(scratch: Scratch):
    """@prd T-206.1"""
    r = run(scratch, "python CTX docs/prd/orders --area reports")
    assert r.exit == 0
    assert headings(part(r.out, "Requirements")) == [
        "### FR-005 Print the monthly report", "### FR-006 Total the monthly report",
        "### FR-007 Refuse an unknown month", "### UJ-01 Read a month's orders",
    ]


@given(CXR)
def test_req_selects_named_blocks_and_traced_journeys(scratch: Scratch):
    """@prd T-206.2"""
    args = ["python", "CTX", "docs/prd/orders", "--area", "import", "--req", "fr-003, FR-001 ,FR-006,NFR-008"]
    r1 = run(scratch, args)
    r2 = run(scratch, args + ["--json"])
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert_json_at(r2.out, {"ids": ["FR-003", "FR-001", "FR-006", "NFR-008"]})
    assert headings(part(r1.out, "Requirements")) == [
        "### FR-001 Refuse a file with no header", "### FR-003 Store a new order",
        "### FR-006 Total the monthly report (area: reports)", "### UJ-01 Read a month's orders (area: reports)",
        "### NFR-008 Import speed",
    ]


def _ledger_and_known_failing(s: Scratch) -> None:
    write_lines(s.orders / "errors.md", [
        "# Error ledger", "", "### E-001 A duplicate order is stored twice", "Detected: 2026-11-02, a test run",
        "Classification: code bug", "Touches: FR-002, FR-099", "Diagnosis: the key lookup ignores the date",
        "Resolution: open", "Recurrence of: -", "", "### E-002 A file with no header is read",
        "Detected: 2026-11-03, a test run", "Classification: code bug", "Touches: FR-001",
        "Diagnosis: the header check came after the first row",
        "Resolution: T-001.1 [integration], PRD 1.0.0, fixed in abc1234", "Recurrence of: -",
    ])
    cases = s.orders / "test-cases/import.yaml"
    insert_after(cases, "  ac: AC-003.1", ["  known-failing: E-001"])
    replace_line(cases, "  ac: AC-004.1", ["  ac: AC-099.9", "  known-failing: E-001"])


@given(N0, _ledger_and_known_failing)
def test_errors_entry_in_req(scratch: Scratch):
    """@prd T-207.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req E-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req e-002")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Known defects") == [
        "## Known defects", "", "### E-001 A duplicate order is stored twice", "Detected: 2026-11-02, a test run",
        "Classification: code bug", "Touches: FR-002, FR-099", "Diagnosis: the key lookup ignores the date",
        "Resolution: open", "Recurrence of: -", "", "0 open errors.md entries name no requirement", "",
    ]
    assert part(r2.out, "Known defects") == [
        "## Known defects", "", "### E-002 A file with no header is read", "Detected: 2026-11-03, a test run",
        "Classification: code bug", "Touches: FR-001", "Diagnosis: the header check came after the first row",
        "Resolution: T-001.1 [integration], PRD 1.0.0, fixed in abc1234", "Recurrence of: -", "",
        "0 open errors.md entries name no requirement", "",
    ]
    assert headings(part(r1.out, "Requirements")) == [
        "### FR-002 Skip a duplicate order", "### FR-003 Store a new order", "### FR-004 Count the imported rows",
    ]
    assert headings(part(r2.out, "Requirements")) == ["### FR-001 Refuse a file with no header"]


@given(N0, in_dir(CXA, "b"))
def test_requirements_part(scratch: Scratch):
    """@prd T-208.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001,FR-006")
    r2 = run(scratch, {"cwd": "<tmp>/b", "command": "python CTX docs/prd/orders --area billing"})
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Requirements") == [
        "## Requirements",
        "",
        "### FR-001 Refuse a file with no header",
        "Status: approved",
        "Acceptance (EARS):",
        "- AC-001.1 If the import file has no header line, the importer shall exit 2 with error IMPORT_NO_HEADER.",
        "Errors: IMPORT_NO_HEADER (contracts/errors.yaml)",
        "Tests: T-001.1 [integration]  (test-cases/import.yaml)",
        "",
        "### FR-006 Total the monthly report (area: reports)",
        "Status: live (since 1.0.0)",
        "Acceptance (EARS):",
        "- AC-006.1 When it prints a monthly report, the report command shall end it with the month's total.",
        "Errors: -",
        "Tests: T-006.1 [integration]  (test-cases/reports.yaml)",
        "",
    ]
    assert part(r2.out, "Requirements") == ["## Requirements", "", "None.", ""]


def _two_terms(s: Scratch) -> None:
    insert_after(s.orders / "prd.md", ORDER_ROW,
                 ["| Header line | The first line of an import file | none |", "| dup | A repeated order key | none |"])


@given(N0, _two_terms)
def test_glossary_part(scratch: Scratch):
    """@prd T-209.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-002")
    r3 = run(scratch, "python CTX docs/prd/orders --area import --req FR-004")
    for r in (r1, r2, r3):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Glossary") == [
        "## Glossary", "", "| Term | Meaning | Banned synonyms |", "|---|---|---|",
        "| Header line | The first line of an import file | none |", "",
    ]
    assert part(r2.out, "Glossary") == [
        "## Glossary", "", "| Term | Meaning | Banned synonyms |", "|---|---|---|", ORDER_ROW, "",
    ]
    assert part(r3.out, "Glossary") == ["## Glossary", "", "None.", ""]


REPORTS_ROW = "| reports | The report command's output | none |"


def _reports_term(s: Scratch) -> None:
    insert_after(s.orders / "prd.md", ORDER_ROW, [REPORTS_ROW])


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-067")
@given(N0, _reports_term)
def test_glossary_ignores_the_area_label(scratch: Scratch):
    """@prd T-209.2 known-failing E-067"""
    r = run(scratch, "python CTX docs/prd/orders --area import --req FR-007")
    lines = r.out.splitlines()
    if "## Glossary" in lines:
        start = lines.index("## Glossary")
        end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
        if REPORTS_ROW in lines[start:end]:
            raise KnownFailure(f"the Glossary part holds the row {REPORTS_ROW}")
    assert r.exit == 0
    assert r.err_b == b""
    assert part(r.out, "Glossary") == ["## Glossary", "", "None.", ""]
