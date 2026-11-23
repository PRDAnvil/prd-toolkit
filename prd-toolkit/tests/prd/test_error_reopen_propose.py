"""error-reopen FR-253: propose with an explanation, as unclassified, or as not a defect
(test-cases/error-reopen.yaml)."""
from __future__ import annotations

from error_reopen_support import assert_line, assert_lines, assert_run, build, entry_lines, files


def test_propose_writes_the_explanation_before_the_diagnosis(tmp_path, monkeypatch):
    """@prd T-253.1"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    r1 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 1000' "
        "--explanation 'An import of a file of 1,200 rows stored 1,000 of them.\n"
        "  FR-003 says the importer stores every new row.'"
    )
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")
    assert_lines(
        c.errors_lines(),
        [
            "# Error ledger",
            "",
            "### E-001 The importer stops at row 1000",
            "Detected: 2026-11-03, a run on the October file",
            "Classification: code bug",
            "Touches: FR-003",
            "Explanation: An import of a file of 1,200 rows stored 1,000 of them. "
            "FR-003 says the importer stores every new row.",
            "Diagnosis: the loop stops at row 1000",
            "Resolution: -",
            "Recurrence of: -",
        ],
        c.dates,
        "the lines of errors.md after run_1",
    )


def test_a_second_explanation_replaces_the_first(tmp_path, monkeypatch):
    """@prd T-253.2"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    r1 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 1000' "
        "--explanation 'The first words.'"
    )
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")
    r2 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class 'spec gap' --diagnosis 'FR-003 names no row limit' "
        "--explanation 'The second words.'"
    )
    assert_run(r2, 0, stdout="E-001 proposed spec gap\n", stderr="")
    lines = c.errors_lines()
    explanations = [x for x in lines if x.startswith("Explanation:")]
    assert explanations == ["Explanation: The second words."], "\n".join(lines)
    assert_line(c, 7, "Explanation: The second words.")
    assert_line(c, 8, "Diagnosis: FR-003 names no row limit")
    assert_line(c, 5, "Classification: spec gap")


def test_propose_without_an_explanation_keeps_it(tmp_path, monkeypatch):
    """@prd T-253.3"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    for text in (
        "python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 1000' "
        "--explanation 'The first words.'",
        "python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 999'",
    ):
        assert_run(c.run(text), 0, stdout="E-001 proposed code bug\n", stderr="")
    assert_line(c, 7, "Explanation: The first words.")
    assert_line(c, 8, "Diagnosis: the loop stops at row 999")


def test_propose_refuses_an_empty_or_fenced_explanation(tmp_path, monkeypatch):
    """@prd T-253.4"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    proposed = files("errors_proposed").encode("utf-8")
    r1 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 1000' "
        "--explanation '  '"
    )
    assert_run(r1, 2, stdout="", stderr="prd_error: the explanation is empty\n")
    assert c.errors_bytes() == proposed, "errors.md changed after run_1"
    r2 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 1000' "
        "--explanation '~~~ text'"
    )
    assert_run(r2, 1, stdout="",
               stderr="refused: --explanation would open a code fence; drop it or put text before it\n")
    assert c.errors_bytes() == proposed, "errors.md changed after run_2"


def test_propose_as_unclassified_opens_no_gate(tmp_path, monkeypatch):
    """@prd T-253.5"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run(
        "python ERROR propose docs/prd/orders E-002 --class unclassified --diagnosis "
        "'not reproduced: the report of 2026-10 printed the total, and the reader names no other month'"
    )
    assert_run(r1, 0, stdout="E-002 unclassified\n", stderr="")
    lines = c.errors_lines()
    assert_lines(
        entry_lines(lines, "E-002"),
        [
            "### E-002 A monthly report printed no total",
            "Detected: 2026-11-05, a reader of the October report",
            "Classification: unclassified",
            "Touches: FR-006",
            "Diagnosis: not reproduced: the report of 2026-10 printed the total, and the reader names no other month",
            "Resolution: -",
            "Recurrence of: -",
        ],
        c.dates,
        "the lines of E-002 after run_1",
    )
    want_e1 = entry_lines(files("errors_confirmed").splitlines(), "E-001")
    assert entry_lines(lines, "E-001") == want_e1, "E-001 changed:\n" + "\n".join(lines)
    r2 = c.run("python GATES list docs/prd/orders")
    assert_run(r2, 0, stdout="", stderr="")


def test_propose_returns_a_proposed_entry_to_unclassified(tmp_path, monkeypatch):
    """@prd T-253.6"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    r1 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class unclassified "
        "--diagnosis 'not reproduced: the October file imports whole'"
    )
    assert_run(r1, 0, stdout="E-001 unclassified\n", stderr="")
    assert_line(c, 5, "Classification: unclassified")
    lines = c.errors_lines()
    assert not [x for x in lines if x.startswith("Confirmed:")], "errors.md holds a Confirmed: line:\n" + "\n".join(lines)
    r2 = c.run("python ERROR list docs/prd/orders")
    assert_run(r2, 0, stdout="E-001 unclassified FR-003 The importer stops at row 1000\n", stderr="")


def test_not_a_defect_is_proposed_and_confirmed(tmp_path, monkeypatch):
    """@prd T-253.7"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    r1 = c.run(
        "python ERROR propose docs/prd/orders E-001 --class 'not a defect' "
        "--diagnosis 'not a defect: the October file ends at row 1000'"
    )
    assert_run(r1, 0, stdout="E-001 proposed not a defect\n", stderr="")
    r2 = c.run("python ERROR confirm docs/prd/orders E-001 --reply 'Yes, the file was short.'")
    assert_run(r2, 0, stdout="E-001 confirmed not a defect\n", stderr="")
    assert_line(c, 5, "Classification: not a defect")
    assert_line(c, 6, 'Confirmed: <today>, "Yes, the file was short."')
    r3 = c.run("python LINT docs/prd/orders")
    assert_run(r3, 0, stderr="")
    bad = [x for x in r3.stdout.splitlines() if x.startswith("docs/prd/orders/errors.md:")]
    assert not bad, "run_3's stdout holds errors.md findings:\n" + "\n".join(bad)


def test_confirm_takes_not_a_defect_as_a_class(tmp_path, monkeypatch):
    """@prd T-253.8"""
    c = build(tmp_path, monkeypatch, "O0", "OP")
    r1 = c.run(
        "python ERROR confirm docs/prd/orders E-001 --reply 'It is not a defect: the file was short.' "
        "--class 'not a defect'"
    )
    assert_run(r1, 0, stdout="E-001 confirmed not a defect\n", stderr="")
    assert_line(c, 5, "Classification: not a defect")
    assert_line(c, 6, 'Confirmed: <today>, "It is not a defect: the file was short."')
