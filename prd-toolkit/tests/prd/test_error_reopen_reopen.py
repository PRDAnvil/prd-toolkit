"""error-reopen FR-251: `prd error reopen` (test-cases/error-reopen.yaml)."""
from __future__ import annotations

from error_reopen_support import (
    OM_TEXT,
    assert_line,
    assert_lines,
    assert_run,
    build,
    entry_lines,
    files,
    matches,
)

CONFIRMED_LINE = 'Confirmed: 2026-11-04, "Yes, it is a code bug."'
REOPENED_NOW = 'Reopened: <today>, "the run passes now"; was Confirmed: 2026-11-04, "Yes, it is a code bug."'


def test_reopen_a_confirmed_entry(tmp_path, monkeypatch):
    """@prd T-251.1"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes now'")
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")

    lines = files("errors_confirmed").split("\n")
    assert lines[5] == CONFIRMED_LINE, "fixture status-next/files errors_confirmed: line 6 is not the Confirmed: line"
    lines[5] = REOPENED_NOW
    expected = "\n".join(lines)
    actual = c.errors_bytes().decode("utf-8")
    assert matches(actual, expected, c.dates), f"errors.md after run_1:\n{actual}\nexpected:\n{expected}"

    r2 = c.run("python ERROR list docs/prd/orders")
    assert_run(
        r2, 0,
        stdout="E-001 proposed code bug FR-003 The importer stops at row 1000\n"
               "E-002 unclassified FR-006 A monthly report printed no total\n",
        stderr="",
    )


def test_reopen_collapses_the_reason(tmp_path, monkeypatch):
    """@prd T-251.2"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run("python ERROR reopen docs/prd/orders E-001 --reason '  the run\n   passes    now  '")
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")
    assert_line(c, 6, REOPENED_NOW)
    want = len(files("errors_confirmed").splitlines())
    got = len(c.errors_lines())
    assert got == want, f"errors.md has {got} lines, files.errors_confirmed {want}"


def test_reopen_refuses_an_entry_that_is_not_confirmed(tmp_path, monkeypatch):
    """@prd T-251.3"""
    c = build(tmp_path, monkeypatch, "O0", "OM")
    runs = [
        ("python ERROR reopen docs/prd/orders E-009 --reason 'the run passes now'",
         "refused: E-009 is not an entry\n"),
        ("python ERROR reopen docs/prd/orders E-003 --reason 'the run passes now'",
         "refused: E-003 is resolved\n"),
        ("python ERROR reopen docs/prd/orders E-002 --reason 'the run passes now'",
         "refused: E-002 is not confirmed\n"),
        ("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes now'",
         "refused: E-001 is not confirmed\n"),
    ]
    for n, (text, stderr) in enumerate(runs, start=1):
        r = c.run(text)
        assert_run(r, 1, stdout="", stderr=stderr)
        assert c.errors_bytes() == OM_TEXT.encode("utf-8"), f"errors.md changed after run_{n}"


def test_reopen_refuses_an_empty_reason(tmp_path, monkeypatch):
    """@prd T-251.4"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run("python ERROR reopen docs/prd/orders E-001 --reason '   '")
    assert_run(r1, 2, stdout="", stderr="prd_error: the reason is empty\n")
    assert c.errors_bytes() == files("errors_confirmed").encode("utf-8"), "errors.md changed after run_1"


def test_reopen_refuses_a_fence_or_the_separator(tmp_path, monkeypatch):
    """@prd T-251.5"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    runs = [
        ("python ERROR reopen docs/prd/orders E-001 --reason '```text'",
         "refused: --reason would open a code fence; drop it or put text before it\n"),
        ("python ERROR reopen docs/prd/orders E-001 --reason 'it passes; was Confirmed: never'",
         'refused: --reason must not hold "; was Confirmed:"\n'),
    ]
    for n, (text, stderr) in enumerate(runs, start=1):
        r = c.run(text)
        assert_run(r, 1, stdout="", stderr=stderr)
        assert c.errors_bytes() == files("errors_confirmed").encode("utf-8"), f"errors.md changed after run_{n}"


def test_propose_and_confirm_keep_the_reopened_line(tmp_path, monkeypatch):
    """@prd T-251.6"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes now'")
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")
    r2 = c.run("python ERROR propose docs/prd/orders E-001 --class 'code bug' --diagnosis 'the loop stops at row 1000'")
    assert_run(r2, 0, stdout="E-001 proposed code bug\n", stderr="")
    assert_line(c, 6, REOPENED_NOW)
    r3 = c.run("python ERROR confirm docs/prd/orders E-001 --reply 'Yes, a code bug after all.'")
    assert_run(r3, 0, stdout="E-001 confirmed code bug\n", stderr="")
    assert_lines(
        entry_lines(c.errors_lines(), "E-001"),
        [
            "### E-001 The importer stops at row 1000",
            "Detected: 2026-11-03, a run on the October file",
            "Classification: code bug",
            REOPENED_NOW,
            'Confirmed: <today>, "Yes, a code bug after all."',
            "Touches: FR-003",
            "Diagnosis: the loop stops at row 1000",
            "Resolution: -",
            "Recurrence of: -",
        ],
        c.dates,
        "the lines of E-001 after run_3",
    )


def test_a_second_reopen_keeps_the_first(tmp_path, monkeypatch):
    """@prd T-251.7"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes now'")
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")
    r2 = c.run("python ERROR confirm docs/prd/orders E-001 --reply 'Yes, a code bug after all.'")
    assert_run(r2, 0, stdout="E-001 confirmed code bug\n", stderr="")
    r3 = c.run("python ERROR reopen docs/prd/orders E-001 --reason 'the run passes again'")
    assert_run(r3, 0, stdout="E-001 proposed code bug\n", stderr="")

    assert_line(c, 6, REOPENED_NOW)
    assert_line(c, 7, 'Reopened: <today>, "the run passes again"; was Confirmed: <today>, "Yes, a code bug after all."')
    lines = c.errors_lines()
    e1 = entry_lines(lines, "E-001")
    assert not [x for x in e1 if x.startswith("Confirmed:")], "E-001 holds a Confirmed: line:\n" + "\n".join(e1)
    want_e2 = entry_lines(files("errors_confirmed").splitlines(), "E-002")
    assert entry_lines(lines, "E-002") == want_e2, "E-002 changed:\n" + "\n".join(lines)


def test_reopen_writes_a_quoted_reason_that_lints_clean(tmp_path, monkeypatch):
    """@prd T-251.9"""
    c = build(tmp_path, monkeypatch, "O0", "OC")
    r1 = c.run(
        "python ERROR reopen docs/prd/orders E-001 --reason "
        "'the reply was unsure: \"I guess, sure? I do not follow it.\"'"
    )
    assert_run(r1, 0, stdout="E-001 proposed code bug\n", stderr="")
    assert_line(
        c, 6,
        'Reopened: <today>, "the reply was unsure: "I guess, sure? I do not follow it.""; '
        'was Confirmed: 2026-11-04, "Yes, it is a code bug."',
    )
    r2 = c.run("python LINT docs/prd/orders")
    assert_run(r2, 0, stderr="")
    bad = [x for x in r2.stdout.splitlines() if x.startswith("docs/prd/orders/errors.md:")]
    assert not bad, "run_2's stdout holds errors.md findings:\n" + "\n".join(bad)
