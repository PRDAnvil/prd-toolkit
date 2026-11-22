"""The Known defects, Open questions and History parts (features/context.md FR-212 to FR-214)."""
from __future__ import annotations

from context_support import (
    CX0, N0, Scratch, append_lines, given, in_dir, load_texts, part, replace_under, run,
    scratch, write_lines,  # noqa: F401  (scratch is the fixture)
)


def _five_entries(s: Scratch) -> None:
    write_lines(s.orders / "errors.md", [
        "# Error ledger", "",
        "### E-001 The importer accepts a file with no header", "Detected: 2026-11-01, a test run",
        "Classification: code bug", "Touches: FR-001", "Resolution: open", "",
        "### E-002 The monthly report skips a day", "Detected: 2026-11-02, a test run", "Classification: code bug",
        "Touches: FR-005", "Resolution: open", "",
        "### E-003 A header in lower case was refused", "Detected: 2026-11-03, a test run",
        "Classification: code bug", "Touches: FR-001", "Resolution: not a defect: the header is case-sensitive", "",
        "### E-004 The import log is empty", "Detected: 2026-11-04, a test run", "Classification: unclassified",
        "Touches: -", "",
        "### E-005 A run stopped without a message", "Detected: 2026-11-05, a deploy run",
        "Classification: unclassified",
    ])


@given(N0, _five_entries)
def test_known_defects_part(scratch: Scratch):
    """@prd T-212.1"""
    r = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    assert r.exit == 0
    assert r.err_b == b""
    assert part(r.out, "Known defects") == [
        "## Known defects", "", "### E-001 The importer accepts a file with no header",
        "Detected: 2026-11-01, a test run", "Classification: code bug", "Touches: FR-001", "Resolution: open", "",
        "2 open errors.md entries name no requirement", "",
    ]


def _questions(s: Scratch) -> None:
    replace_under(s.orders / "prd.md", "## 13. Open questions", "None.", [
        "- Does FR-001 also refuse an empty file?", "- How should import treat", "  a header in lower case?",
        "- Who signs off the monthly report?", "- Is AC-001.1 final?", load_texts()["q_fr0010_line"],
    ])


@given(N0, _questions)
def test_open_questions_part(scratch: Scratch):
    """@prd T-213.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-002")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Open questions") == [
        "## Open questions", "", "- Does FR-001 also refuse an empty file?", "", "- How should import treat",
        "  a header in lower case?", "", "- Is AC-001.1 final?", "", "2 other open questions in prd.md §13", "",
    ]
    assert part(r2.out, "Open questions") == [
        "## Open questions", "", "- How should import treat", "  a header in lower case?", "",
        "4 other open questions in prd.md §13", "",
    ]


def _changelog_rows(s: Scratch) -> None:
    append_lines(s.orders / "prd.md", [
        "| 1.0.1 | 2026-11-02 | import: first fix; no dry run (fixture) | FR-001 |",
        "| 1.1.0 | 2026-11-03 | import: a header check; no dry run (fixture) | FR-001 |",
        "| 1.2.0 | 2026-11-04 | import: skip duplicates; no dry run (fixture) | FR-002 |",
        "| 1.3.0 | 2026-11-05 | reports: a total; no dry run (fixture) | FR-006 |",
        "| 1.4.0 | 2026-11-06 | import: store new orders; no dry run (fixture) | FR-003 |",
        "| 1.5.0 | 2026-11-07 | import-tools: a helper; no dry run (fixture) | - |",
    ])


@given(N0, _changelog_rows, in_dir(CX0, "alone"))
def test_history_part(scratch: Scratch):
    """@prd T-214.1"""
    runs = [
        "python CTX docs/prd/orders --area import",
        "python CTX docs/prd/orders --area reports",
        {"cwd": "<tmp>/alone", "command": "python CTX docs/prd/orders --area import"},
    ]
    r1, r2, r3 = (run(scratch, spec) for spec in runs)
    for spec, r in zip(runs, (r1, r2, r3)):  # each_run: {exit: 0, stderr: ""}
        assert r.exit == 0, spec
        assert r.err_b == b"", spec
    head = ["## History", "", "| Version | Date | Change | IDs |", "|---|---|---|---|"]
    assert part(r1.out, "History") == head + [
        "| 1.1.0 | 2026-11-03 | import: a header check; no dry run (fixture) | FR-001 |",
        "| 1.2.0 | 2026-11-04 | import: skip duplicates; no dry run (fixture) | FR-002 |",
        "| 1.4.0 | 2026-11-06 | import: store new orders; no dry run (fixture) | FR-003 |",
    ]
    assert part(r2.out, "History") == head + [
        "| 1.3.0 | 2026-11-05 | reports: a total; no dry run (fixture) | FR-006 |",
    ]
    assert part(r3.out, "History") == ["## History", "", "None."]
