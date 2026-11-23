"""Record a change in the version, §14 and §11 (features/change.md FR-260; test-cases/change.yaml)."""
from __future__ import annotations

import pytest

from change_support import (
    G0, GA, GC, GD, GK, GN, GR, GS, GW, UNDO_GK, KnownFailure, append, case, command, exit_is, given,
    line_becomes, named, one_json_line, stderr_first_line_starts, stderr_is, stdout_is,
)

__all__ = ["case"]

RECORD = "python CHANGE record docs/prd/orders --base HEAD"
ROW_1_0_0 = ("| 1.0.0 | 2026-11-01 | Initial release; no dry run (fixture) | FR-001, FR-002, FR-003, FR-004, "
             "FR-005, FR-006, FR-007 |")
NOTE = append("errors.md", "A note.", name="append the line `A note.` to errors.md")


def prd_lines(case) -> list[str]:
    return (case.orders / "prd.md").read_bytes().decode("utf-8").splitlines()


def section(lines: list[str], heading: str) -> list[str]:
    start = lines.index(heading) + 1
    end = next((j for j in range(start, len(lines)) if lines[j].startswith("## ")), len(lines))
    return lines[start:end]


def rows(lines: list[str], heading: str) -> list[str]:
    return [line for line in section(lines, heading) if line.startswith("|")]


@given(G0, GA)
def test_t260_1_record_writes_version_updated_and_row(case):
    """@prd T-260.1"""
    r1 = case.run(RECORD + " --bump minor --change 'Refuse an empty file'")
    r2 = case.run(RECORD + " --bump minor --change 'Refuse an empty file' --json")
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    rows_today = case.today("| 1.1.0 | <today> | Refuse an empty file; pending | FR-008, AC-008.1, T-008.1 |")
    assert any(r1.lines == ["1.1.0", row] for row in rows_today), str(r1)
    doc = one_json_line(r2)
    assert any(doc == {"interface": 1, "kind": "change.record", "version": "1.1.0", "row": row}
               for row in rows_today), str(r2)
    lines = prd_lines(case)
    assert lines[2] == "version: 1.1.0", lines[2]
    assert lines[5] in case.today("updated: <today>"), lines[5]
    assert lines[-1] == r1.lines[1], f"prd.md's last line is {lines[-1]!r}"
    assert lines[-2] == ROW_1_0_0, f"the line before it is {lines[-2]!r}"
    staged = case.git("diff", "--cached", "--name-only")
    exit_is(staged, 0)
    stdout_is(staged, "")


@given(G0)
def test_t260_2_ids_cell(case):
    """@prd T-260.2"""
    case.steps(GK)
    r1 = case.run(RECORD + " --bump patch --change 'the message names FR-001'")
    case.steps(UNDO_GK, NOTE)
    r2 = case.run(RECORD + " --bump patch --change 'a ledger note'")
    for r in (r1, r2):
        exit_is(r, 0)
    assert set(r1.lines) & set(case.today("| 1.0.1 | <today> | the message names FR-001; pending | FR-001 |")), str(r1)
    assert set(r2.lines) & set(case.today("| 1.0.1 | <today> | a ledger note; pending | - |")), str(r2)


@given(G0, GA, GS, GD)
def test_t260_3_requirement_index_rows(case):
    """@prd T-260.3"""
    r = case.run(RECORD + " --bump major --change 'three moves'")
    exit_is(r, 0)
    assert "2.0.0" in r.lines, str(r)
    index = rows(prd_lines(case), "## 11. Requirement index")
    for row in ("| FR-001 | Refuse a file with no header | approved | features/import.md | 1.0.0 |",
                "| FR-002 | Skip a duplicate order | verified | features/import.md |  |",
                "| FR-007 | Refuse an unknown month | removed | features/reports.md |  |"):
        assert row in index, f"§11 lacks {row!r}:\n" + "\n".join(index)
    assert index[-1] == "| FR-008 | Refuse an empty file | approved | features/import.md |  |", index[-1]


@given(G0, GA, GR)
def test_t260_4_rerun_replaces_the_pending_row(case):
    """@prd T-260.4"""
    before = (case.orders / "prd.md").read_bytes()
    r = case.run(RECORD + " --bump minor --change 'Refuse an empty file'")
    exit_is(r, 0)
    after = (case.orders / "prd.md").read_bytes()
    assert after == before, "prd.md differs from the file GR left"
    assert after.decode("utf-8").count("; pending") == 1


@given(G0, GA)
def test_t260_5_refusals(case):
    """@prd T-260.5"""
    expected = [
        ("--bump needs-judgment --change 'x | y'", "refused: a needs-judgment bump must be decided first\n"),
        ("--bump minor --change 'x | y'", "refused: the change text must be one non-empty line without |\n"),
        ("--bump patch --change 'Refuse an empty file'", "refused: the diff needs minor, not patch\n"),
    ]
    for args, stderr in expected:
        before = (case.orders / "prd.md").read_bytes()
        r = case.run(f"{RECORD} {args}")
        exit_is(r, 1)
        stdout_is(r, "")
        stderr_is(r, stderr)
        assert (case.orders / "prd.md").read_bytes() == before, f"prd.md changed after `{args}`"


@given(G0, GA)
def test_t260_6_unknown_bump_is_a_usage_error(case):
    """@prd T-260.6"""
    before = (case.orders / "prd.md").read_bytes()
    r = case.run(RECORD + " --bump huge --change x")
    exit_is(r, 2)
    stderr_first_line_starts(r, "usage: prd_change.py")
    assert (case.orders / "prd.md").read_bytes() == before, "prd.md changed"


@named("rewrite prd.md with every line ending in CRLF")
def _crlf(c):
    path = c.path("prd.md")
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))


@given(G0, _crlf, GC, GA)
def test_t260_7_crlf_kept(case):
    """@prd T-260.7"""
    r = case.run(RECORD + " --bump minor --change 'Refuse an empty file'")
    exit_is(r, 0)
    data = (case.orders / "prd.md").read_bytes()
    pieces = data.split(b"\n")
    assert pieces[-1] == b"", "prd.md does not end in a line ending"
    bare = [i + 1 for i, piece in enumerate(pieces[:-1]) if not piece.endswith(b"\r")]
    assert bare == [], f"lines ending in a bare \\n: {bare}"
    assert any(piece.startswith(b"| 1.1.0 |") for piece in pieces), "no new §14 row"


@given(G0, GN)
def test_t260_8_no_changelog_table(case):
    """@prd T-260.8"""
    before = (case.orders / "prd.md").read_bytes()
    r = case.run(RECORD + " --bump patch --change x")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: §14 has no changelog table\n")
    assert (case.orders / "prd.md").read_bytes() == before, "prd.md changed"


@given(G0, GA, command("git branch before"), GC, GS)
def test_t260_9_base_is_a_branch(case):
    """@prd T-260.9"""
    r = case.run("python CHANGE record docs/prd/orders --base before --bump minor --change 'two moves'")
    exit_is(r, 0)
    assert "1.1.0" in r.lines, str(r)


_UJ_BLOCK = append("features/import.md", "", "### UJ-01 Import a file", "Status: live (since 1.0.0)",
                   "Flow: the user runs the importer on a file.", name="append the UJ-01 block to features/import.md")
_UJ_MESSAGE = line_becomes("contracts/errors.yaml", 5, "  message: The import file has no header line.",
                           "  message: The import file has no header line (FR-001, UJ-01).")


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@given(G0, _UJ_BLOCK, GC, _UJ_MESSAGE)
def test_t260_10_ids_cell_holds_a_cited_journey(case):
    """@prd T-260.10 known-failing E-076"""
    r = case.run(RECORD + " --bump patch --change 'cite a journey'")
    if r.exit == 0 and len(r.lines) >= 2 and r.lines[1] in case.today(
            "| 1.0.1 | <today> | cite a journey; pending | FR-001 |"):
        raise KnownFailure(f"E-076: the row leaves out UJ-01: {r.lines[1]!r}")
    exit_is(r, 0)
    assert set(r.lines) & set(case.today("| 1.0.1 | <today> | cite a journey; pending | UJ-01, FR-001 |")), str(r)


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@given(G0, GW)
def test_t260_11_rerun_at_another_level_replaces_the_pending_row(case):
    """@prd T-260.11 known-failing E-077"""
    r1 = case.run(RECORD + " --bump minor --change first")
    r2 = case.run(RECORD + " --bump major --change second")
    changelog = rows(prd_lines(case), "## 14. Changelog")
    first = case.today("| 1.1.0 | <today> | first; pending | FR-001, AC-001.1 |")
    second = case.today("| 2.0.0 | <today> | second; pending | FR-001, AC-001.1 |")
    if set(changelog) & set(first) and set(changelog) & set(second):
        raise KnownFailure("E-077: §14 holds the 1.1.0 and the 2.0.0 pending rows")
    for r in (r1, r2):
        exit_is(r, 0)
    assert "2.0.0" in r2.lines, str(r2)
    text = (case.orders / "prd.md").read_bytes().decode("utf-8")
    assert text.count("; pending") == 1, "\n".join(changelog)
    assert changelog[-1] in second, changelog[-1]
    assert not any(row.startswith("| 1.1.0 |") for row in changelog), "\n".join(changelog)
