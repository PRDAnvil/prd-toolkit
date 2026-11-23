"""The proposed version bump and how it classifies each item (features/change.md FR-258, FR-259)."""
from __future__ import annotations

from change_support import (
    G0, GA, GC, GD, GE, GG, GI, GK, GL, GP, GS, GT, GW, GX, N0X_here, UNDO_GX, case, append, exit_is,
    given, line_becomes, line_in_section, stderr_is, stderr_single_line_starts, stdout_contains,
    stdout_contains_line, stdout_is, stdout_json, stdout_lines_in_this_relative_order, text_in_yaml_entry, write,
)

__all__ = ["case"]

BUMP = "python CHANGE bump docs/prd/orders --base HEAD"
NOTE = append("errors.md", "A note.", name="append the line `A note.` to errors.md")


@given(G0, GS)
def test_t258_1_bump_lines_and_json(case):
    """@prd T-258.1"""
    r1 = case.run(BUMP)
    r2 = case.run(BUMP + " --json")
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    stdout_is(r1, "patch FR-002 features/import.md:11 status built → verified\nlevel patch\n")
    stdout_json(r2, {"interface": 1, "kind": "change.bump", "level": "patch",
                     "items": [{"id": "FR-002", "file": "features/import.md", "line": 11, "change": "changed",
                                "level": "patch", "reason": "status built → verified"}]})
    status = case.git("status", "--porcelain")
    assert status.lines == [" M docs/prd/orders/features/import.md"], str(status)


@given(G0)
def test_t258_2_the_overall_level(case):
    """@prd T-258.2"""
    r1 = case.run(BUMP)
    case.steps(GA, GD)
    r2 = case.run(BUMP)
    case.steps(NOTE)
    r3 = case.run(BUMP)
    for r in (r1, r2, r3):
        exit_is(r, 0)
    stdout_is(r1, "level patch\n")
    stdout_contains_line(r2, "level major")
    stdout_contains_line(r3, "needs judgment errors.md errors.md:1 unclassified change in errors.md")
    assert r3.lines and r3.lines[-1] == "level needs judgment", str(r3)


@given(G0)
def test_t258_3_base_with_no_prd_folder(case):
    """@prd T-258.3"""
    r = case.run("python CHANGE bump docs/prd/orders --base no-such-ref")
    exit_is(r, 2)
    stdout_is(r, "")
    stderr_is(r, "bump: no-such-ref has no docs/prd/orders\n")


@given(N0X_here)
def test_t258_4_not_in_a_git_repository(case):
    """@prd T-258.4"""
    r = case.run(BUMP)
    exit_is(r, 2)
    stdout_is(r, "")
    stderr_single_line_starts(r, "bump: ")
    assert r.err_lines[0].endswith("is not in a git repository"), str(r)


@given(G0, GA)
def test_t259_1_a_new_block(case):
    """@prd T-259.1"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_lines_in_this_relative_order(r, [
        "minor FR-008 features/import.md:31 a new block or AC",
        "minor AC-008.1 features/import.md:34 a new block or AC",
        "level minor",
    ])
    stdout_contains(r, ["minor T-008.1 test-cases/import.yaml:", " a new test case under a new AC"])
    assert len(r.lines) == 4, str(r)


@given(G0, GD)
def test_t259_2_a_removed_block(case):
    """@prd T-259.2"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_lines_in_this_relative_order(r, [
        "major FR-007 features/reports.md:17 a removed block or AC",
        "major AC-007.1 features/reports.md:20 a removed block or AC",
        "level major",
    ])
    stdout_contains(r, ["major T-007.1 test-cases/reports.yaml:"])
    assert len(r.lines) == 4, str(r)


@given(G0)
def test_t259_3_ac_wording(case):
    """@prd T-259.3"""
    case.steps(GX)
    r1 = case.run(BUMP)
    case.steps(UNDO_GX, GW)
    r2 = case.run(BUMP)
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    stdout_is(r1, "needs judgment AC-001.1 features/import.md:6 an AC whose text changed (not equal after "
                  "lowercasing, removing punctuation and collapsing whitespace)\nlevel needs judgment\n")
    stdout_is(r2, "patch AC-001.1 features/import.md:6 an AC whose text is equal after that normalization, "
                  "a changed title, Flow, Edge cases or glossary meaning\nlevel patch\n")


EXIT_3 = text_in_yaml_entry("test-cases/import.yaml", "T-001.1", "output: {exit: 2}", "output: {exit: 3}",
                            name="T-001.1's `output: {exit: 2}` becomes `output: {exit: 3}`")
EXIT_2 = text_in_yaml_entry("test-cases/import.yaml", "T-001.1", "output: {exit: 3}", "output: {exit: 2}",
                            name="undo T-001.1's `output: {exit: 3}`")


@given(G0)
def test_t259_4_a_changed_test_case_or_contract_item(case):
    """@prd T-259.4"""
    case.steps(EXIT_3)
    r1 = case.run(BUMP)
    case.steps(GX)
    r2 = case.run(BUMP)
    case.steps(EXIT_2, UNDO_GX, GK)
    r3 = case.run(BUMP)
    for r in (r1, r2, r3):
        exit_is(r, 0)
    stdout_contains(r1, ["needs judgment T-001.1 test-cases/import.yaml:",
                         "a changed test case or contract item under an unchanged AC"])
    stdout_contains(r2, ["major T-001.1 test-cases/import.yaml:", "a changed test case under a changed AC"])
    stdout_contains(r3, ["needs judgment IMPORT_NO_HEADER contracts/errors.yaml:",
                         "a changed test case or contract item under an unchanged AC"])


@given(G0, GE, GC, GT)
def test_t259_5_new_case_citing_an_open_entry(case):
    """@prd T-259.5"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_contains(r, ["patch T-001.2 test-cases/import.yaml:",
                        "a new test case under an unchanged AC that cites an open errors.md entry"])
    stdout_contains_line(r, "level patch")


@given(G0, GS)
def test_t259_6_status_move(case):
    """@prd T-259.6"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_is(r, "patch FR-002 features/import.md:11 status built → verified\nlevel patch\n")


@given(G0, GP, GC, line_becomes("prd.md", 14, "- Pack: service 0.9.0 (prd-toolkit)",
                                "- Pack: service 1.0.0 (prd-toolkit)"))
def test_t259_7_pack_version(case):
    """@prd T-259.7"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_contains(r, ["patch service prd.md:",
                        "a changed version on a `Pack:` or `Target: pack` line, the pack's name and source unchanged"])
    assert len(r.lines) == 2 and r.lines[-1] == "level patch", str(r)


@given(G0, GI, line_becomes("prd.md", 6, "updated: 2026-11-01", "updated: 2030-01-01"), GL,
       write("README.md", "hi"), write(".prd-review.json", "{}"))
def test_t259_8_no_item(case):
    """@prd T-259.8"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stderr_is(r, "")
    stdout_is(r, "level patch\n")


@given(G0, NOTE,
       line_becomes("features/import.md", 7, "Errors: IMPORT_NO_HEADER (contracts/errors.yaml)", "Errors: -"),
       line_in_section("prd.md", "## 4. Architecture", "The importer stores orders; the report command reads them.",
                       "The importer stores orders.", name="prd.md: §4's line becomes `The importer stores orders.`"))
def test_t259_9_unclassified(case):
    """@prd T-259.9"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_contains_line(r, "needs judgment errors.md errors.md:1 unclassified change in errors.md")
    stdout_contains(r, ["needs judgment FR-001 features/import.md:3 unclassified change in features/import.md",
                        "needs judgment section 4 prd.md:", "unclassified change in prd.md"])
    assert r.lines and r.lines[-1] == "level needs judgment", str(r)


@given(G0, GG)
def test_t259_10_glossary(case):
    """@prd T-259.10"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_contains(r, ["patch glossary prd.md:",
                        "an AC whose text is equal after that normalization, a changed title, Flow, Edge cases or "
                        "glossary meaning"])
    assert len(r.lines) == 2 and r.lines[-1] == "level patch", str(r)


@given(G0, GT)
def test_t259_11_other_new_case(case):
    """@prd T-259.11"""
    r = case.run(BUMP)
    exit_is(r, 0)
    stdout_contains(r, ["needs judgment T-001.2 test-cases/import.yaml:", "any other new test case under an unchanged AC"])
    stdout_contains_line(r, "level needs judgment")
