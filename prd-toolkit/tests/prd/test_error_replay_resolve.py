"""error-replay, FR-080: resolve a fix outside every adopted Boundary with a red run (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import (  # noqa: F401
    REPLAY, assert_left_as_it_was, assert_worktrees_same_and_scratch_empty, case, files, given, ledger_with,
)

RESOLVE = "python ERROR resolve docs/prd/orders E-001"
RED = f"{RESOLVE} --commit <fix> --red-run tests/test_total.py --level integration"


def _refused_each(case, commands, stderr, ledger_key, left=True):
    """Each command exits 1 (or the case's code) with the stderr given; errors.md stays the ledger's text."""
    for command, (exit, err) in zip(commands, stderr):
        res = case.run(command)
        case.expect(res, exit=exit, stdout="", stderr=err)
        case.expect_errors_md(files(ledger_key))
        if left:
            assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RO")
def test_red_run_written_and_replayed(case):
    """@prd T-080.1"""
    run_1 = case.run(RED)
    case.expect(run_1, exit=0, stdout="E-001 resolved code bug\n", stderr="")
    case.expect_errors_md(ledger_with("ledger_open", "Resolution: fixed in <fix>, red run tests/test_total.py [integration]"))
    assert_worktrees_same_and_scratch_empty(run_1)
    run_2 = case.run(REPLAY)
    case.expect(run_2, exit=0, stdout="E-001: tests/test_total.py fails on <fix>^ and passes on <fix>\n", stderr="")


@given("R0", "RT", "RF", "RL", "RO")
def test_flags_that_do_not_go_with_red_run(case):
    """@prd T-080.2"""
    commands = [
        f"{RESOLVE} --commit <fix> --red-run tests/test_total.py",
        f"{RESOLVE} --red-run tests/test_total.py --level integration",
        f"{RED} --t T-006.1",
        f"{RED} --version 1.0.0",
        f"{RED} --run 20261110T090000Z-all",
        f"{RED} --not-a-defect 'it was not'",
        f"{RESOLVE} --t T-006.1 --version 1.0.0 --commit <fix> --level integration",
    ]
    err = "prd_error: --red-run takes --commit and --level, and no --t, --version, --run or --not-a-defect\n"
    _refused_each(case, commands, [(2, err)] * len(commands), "ledger_open")


@given("R0", "RT", "RF", "RL", "RO")
def test_commit_not_lowercase_hex(case):
    """@prd T-080.3"""
    values = ["XYZ1234", "ABCDEF1", "abc12"]
    commands = [f"{RESOLVE} --commit {v} --red-run tests/test_total.py --level integration" for v in values]
    stderr = [(2, f"prd_error: commit must be 7 to 40 lowercase hex digits; got '{v}'\n") for v in values]
    _refused_each(case, commands, stderr, "ledger_open")


@given("R0", "RT", "RF", "RO")
def test_no_such_entry(case):
    """@prd T-080.4"""
    _refused_each(case, ["python ERROR resolve docs/prd/orders E-009 --commit <fix> --red-run tests/test_total.py "
                         "--level integration"],
                  [(1, "refused: E-009 is not an entry\n")], "ledger_open")


@given("R0", "RT", "RF", "RE", resolution="not a defect: the total was read from the wrong report")
def test_already_resolved(case):
    """@prd T-080.5"""
    committed = case.git(case.repo, "show", "HEAD:docs/prd/orders/errors.md")
    assert committed.returncode == 0, committed.stderr.decode("utf-8", "replace")
    res = case.run(RED)
    case.expect(res, exit=1, stdout="", stderr="refused: E-001 is already resolved\n")
    assert_left_as_it_was(res)
    assert case.errors_md() == committed.stdout, case.errors_md().decode("utf-8")


@given("R0", "RT", "RF", "RP")
def test_not_confirmed(case):
    """@prd T-080.6"""
    _refused_each(case, [RED], [(1, "refused: E-001 is not confirmed\n")], "ledger_proposed")


@given("R0", "RT", "RF", "RG")
def test_not_a_code_bug(case):
    """@prd T-080.7"""
    _refused_each(case, [RED], [(1, "refused: E-001 is classed spec gap; a red run resolves a code bug only\n")],
                  "ledger_spec")


@given("R0", "RT", "RF", "RO")
def test_level_refusals(case):
    """@prd T-080.8"""
    base = f"{RESOLVE} --commit <fix> --red-run tests/test_total.py --level"
    _refused_each(case, [f"{base} nosuch", f"{base} system", f"{base} unit"], [
        (1, "refused: nosuch is not a level of testing.md\n"),
        (1, "refused: system is a deploy-gate level\n"),
        (1, "refused: unit has no One test command; add the One test column to testing.md Levels through "
            "/prd-toolkit:prd-change\n"),
    ], "ledger_open")


@given("R0", "RT", "RF", "RO")
def test_test_id_refusals(case):
    """@prd T-080.9"""
    err = "refused: the test id must hold no white space and must not start with -\n"
    _refused_each(case, [
        f"{RESOLVE} --commit <fix> --red-run 'tests/a b.py' --level integration",
        f"{RESOLVE} --commit <fix> --red-run=-x --level integration",
    ], [(1, err), (1, err)], "ledger_open")


@given("R0", "RT", "RFA", "RO")
def test_fix_changes_a_covered_path(case):
    """@prd T-080.10"""
    _refused_each(case, [RED], [
        (1, "refused: <fix> changes src/importer.py, which area import covers; resolve with a regression T-id\n"),
    ], "ledger_open")


@given("R0", "RT", "RF", "RX", "RO")
def test_no_adoption_map(case):
    """@prd T-080.11"""
    _refused_each(case, [RED], [
        (1, "refused: the PRD has no adoption map, so every path is covered; resolve with a regression T-id\n"),
    ], "ledger_open")


@given("R0", "RTP", "RF", "RO")
def test_replay_does_not_hold(case):
    """@prd T-080.12"""
    _refused_each(case, [RED], [
        (1, "refused: E-001: tests/test_total.py passes on <fix>^; <fix> did not turn it green\n"),
    ], "ledger_open")


@given("R0", "RT", "RF", "RO")
def test_replay_findings_as_refusals(case):
    """@prd T-080.13"""
    run_1 = case.run(f"{RESOLVE} --commit <fix> --red-run tests/test_total.py --level slow")
    case.expect(run_1, exit=1, stdout="")
    case.expect_lines(run_1.stderr, ["refused: E-001: timed out after 2 s on <fix>^",
                                     "refused: E-001: timed out after 2 s on <fix>"])
    case.expect_errors_md(files("ledger_open"))
    assert_left_as_it_was(run_1)
    run_2 = case.run(f"{RESOLVE} --commit 0000000 --red-run tests/test_total.py --level integration")
    case.expect(run_2, exit=1, stdout="", stderr="refused: E-001: 0000000 names no commit\n")
    case.expect_errors_md(files("ledger_open"))
    assert_left_as_it_was(run_2)


@given("R0", "RT", "RF", "RG")
def test_class_refused_first(case):
    """@prd T-080.14"""
    _refused_each(case, [f"{RESOLVE} --commit <fix> --red-run 'a b' --level nosuch"], [
        (1, "refused: E-001 is classed spec gap; a red run resolves a code bug only\n"),
    ], "ledger_spec", left=False)


@given("R0", "RT", "RFA", "RO")
def test_test_id_and_level_refused_before_paths(case):
    """@prd T-080.15"""
    _refused_each(case, [
        f"{RESOLVE} --commit <fix> --red-run 'tests/a b.py' --level integration",
        f"{RESOLVE} --commit <fix> --red-run=-x --level system",
    ], [
        (1, "refused: the test id must hold no white space and must not start with -\n"),
        (1, "refused: system is a deploy-gate level\n"),
    ], "ledger_open", left=False)
