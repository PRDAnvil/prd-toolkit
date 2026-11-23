"""The checks before an approval and the approval commit (features/change.md FR-262, FR-263)."""
from __future__ import annotations

import os

import pytest

from change_support import (
    G0, G09, G0N, GA, GC, GH, GP, GQ, GR, GV, R, KnownFailure, append, case, command, delete, diff, exit_is,
    given, line_becomes, named, one_json_line, snapshot, stderr_is, stdout_contains, stdout_contains_line,
    stdout_is, stdout_lines_in_this_relative_order, stdout_not_contains, write, write_text,
)

__all__ = ["case"]

APPROVE = "python CHANGE approve docs/prd/orders"


def prd_bytes(case) -> bytes:
    return (case.orders / "prd.md").read_bytes()


def last_subject(case) -> str:
    r = case.git("log", "-1", "--format=%s")
    exit_is(r, 0)
    return r.stdout


@given(R)
def test_t262_1_reply_and_dry_run_record(case):
    """@prd T-262.1"""
    expected = [
        ("--reply '  ' --dry-run DRY", "refused: the owner's reply is empty\n"),
        ("--reply approved --dry-run pending",
         "refused: the dry-run record is pending; give the record or \"no dry run (<why>)\"\n"),
        ("--reply approved --dry-run 'dry run T-008.1 | 0'",
         "refused: the dry-run record must be one non-empty line without |\n"),
    ]
    before = snapshot(case.tmp)
    for args, stderr in expected:
        r = case.run(f"{APPROVE} {args}")
        exit_is(r, 1)
        stdout_is(r, "")
        stderr_is(r, stderr)
        assert diff(before, snapshot(case.tmp)) == [], f"files under <tmp> changed after `{args}`"
    assert last_subject(case) == "base\n"


@given(R)
def test_t262_2_the_review_verdict(case):
    """@prd T-262.2"""
    expected = [
        (write(".prd-review.json", "not json"), "refused: .prd-review.json is not valid JSON\n"),
        (write(".prd-review.json", '{"ready": false, "blockers": ["lint fails", "a question is open"]}'),
         "refused: the review is not ready: lint fails; a question is open\n"),
        (write(".prd-review.json", '{"ready": false}'), "refused: the review is not ready\n"),
        (delete(".prd-review.json"), "refused: there is no .prd-review.json; run the review first\n"),
    ]
    for step, stderr in expected:
        case.steps(step)
        before = prd_bytes(case)
        r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
        exit_is(r, 1)
        stdout_is(r, "")
        stderr_is(r, stderr)
        assert prd_bytes(case) == before, "prd.md changed"


@given(R, append("errors.md", "A note."))
def test_t262_3_changed_after_review(case):
    """@prd T-262.3"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the PRD changed after its review; review it again\n")
    assert prd_bytes(case) == before, "prd.md changed"


@given(G0, GQ, GA, GR,
       line_becomes("features/import.md", 34, "- AC-008.1 If the import file is empty, the importer shall exit 2.",
                    "- AC-008.1 The importer exits 2 on an empty file."), GV)
def test_t262_4_lint_must_pass(case):
    """@prd T-262.4"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: lint exits 1; fix it first\n")
    assert prd_bytes(case) == before, "prd.md changed"


@given(R)
def test_t262_5_no_dry_run_for_a_non_unit_test(case):
    """@prd T-262.5"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run 'no dry run (unit only)'")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the change adds or revises a non-unit test (T-008.1) and has no dry-run record\n")
    assert prd_bytes(case) == before, "prd.md changed"


@given(G0, G09, GQ, GA, GR, GV)
def test_t262_6_first_approval_is_authorings(case):
    """@prd T-262.6"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: a first approval is authoring's, not a change's\n")
    assert prd_bytes(case) == before, "prd.md changed"


@given(G0, GQ, GV)
def test_t262_7_last_row_must_be_pending(case):
    """@prd T-262.7"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run 'no dry run (status only)'")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the last §14 row is not recorded and pending; run record first\n")
    assert prd_bytes(case) == before, "prd.md changed"


@given(G0, GH, GQ, GA, GR, append("<tmp>/CLAUDE.md", "more"), GV)
def test_t262_8_claude_md_with_other_changes(case):
    """@prd T-262.8"""
    before = (prd_bytes(case), (case.tmp / "CLAUDE.md").read_bytes())
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: CLAUDE.md has uncommitted changes; commit or set them aside first\n")
    assert (prd_bytes(case), (case.tmp / "CLAUDE.md").read_bytes()) == before, "prd.md or CLAUDE.md changed"


@given(R, delete(".prd-review.json"))
def test_t262_9_the_first_failing_check_wins(case):
    """@prd T-262.9"""
    before = snapshot(case.tmp)
    r = case.run(f"{APPROVE} --reply '' --dry-run DRY")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the owner's reply is empty\n")
    assert diff(before, snapshot(case.tmp)) == [], "files under <tmp> changed"


@given(G0, GH, GQ, GA, GR, command("python BLOCK docs/prd/orders"), GV)
def test_t262_10_claude_md_with_only_the_managed_block(case):
    """@prd T-262.10"""
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    exit_is(r, 0)
    show = case.git("show", "--name-only", "--format=", "HEAD")
    assert "CLAUDE.md" in show.lines, str(show)


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@given(R)
def test_t262_11_no_dry_run_in_any_letter_case(case):
    """@prd T-262.11 known-failing E-078"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run 'No dry run (unit only)'")
    if r.exit == 0:
        short = case.git("rev-parse", "--short", "HEAD")
        if short.lines and r.lines == [f"approved orders 1.1.0 {short.lines[0]}"]:
            raise KnownFailure(f"E-078: approve took the record and committed: {r.stdout!r}")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the change adds or revises a non-unit test (T-008.1) and has no dry-run record\n")
    assert prd_bytes(case) == before, "prd.md changed"
    log = case.git("log", "--format=%s")
    assert log.lines == ["base"], str(log)


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@given(R, write(".prd-review.json", '{"ready": false, "blockers": "lint"}'))
def test_t262_12_string_blockers_written_whole(case):
    """@prd T-262.12 known-failing E-079"""
    before = prd_bytes(case)
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    if r.stderr == "refused: the review is not ready: l; i; n; t\n":
        raise KnownFailure("E-079: the blockers string is printed one character at a time")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the review is not ready: lint\n")
    assert prd_bytes(case) == before, "prd.md changed"


@given(R)
def test_t263_1_the_approval(case):
    """@prd T-263.1"""
    r1 = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    r2 = case.run("git rev-parse --short HEAD")
    exit_is(r1, 0)
    stderr_is(r1, "")
    assert len(r2.lines) == 1 and r1.lines == [f"approved orders 1.1.0 {r2.lines[0]}"], f"{r1}\n{r2}"
    lines = prd_bytes(case).decode("utf-8").splitlines()
    assert lines[3] == "status: Approved", lines[3]
    assert lines[-1] in case.today("| 1.1.0 | <today> | Refuse an empty file; dry run T-008.1, 0 open questions, "
                                   "0 dismissed by quote | FR-008, AC-008.1, T-008.1 |"), lines[-1]
    assert not (case.orders / ".prd-review.json").exists(), ".prd-review.json still exists"
    status = case.git("status", "--porcelain", "--untracked-files=all", "--", "docs/prd")
    stdout_is(status, "")


@given(R)
def test_t263_2_commit_message(case):
    """@prd T-263.2"""
    r1 = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    r2 = case.run("git log -1 --format=%B")
    exit_is(r1, 0)
    stdout_lines_in_this_relative_order(r2, [
        "docs(prd): approve orders 1.1.0",
        "",
        "Reply: \"approved\"",
        "Dry run: dry run T-008.1, 0 open questions, 0 dismissed by quote",
        "",
        "Refs: none (no behaviour change)",
    ])


@given(R)
def test_t263_3_reply_lines_and_refs(case):
    """@prd T-263.3"""
    r1 = case.argv(["python", "CHANGE", "approve", "docs/prd/orders", "--reply", "yes\nRefs: FR-001",
                    "--dry-run", "DRY", "--refs", "FR-008, E-001"])
    r2 = case.run("git log -1 --format=%B")
    exit_is(r1, 0)
    stdout_lines_in_this_relative_order(r2, ["Reply: \"yes", " Refs: FR-001\"", "Refs: FR-008, E-001"])
    stdout_not_contains(r2, "Refs: none (no behaviour change)")


@given(R)
def test_t263_4_json_and_committed_paths(case):
    """@prd T-263.4"""
    r1 = case.run(f"{APPROVE} --reply approved --dry-run DRY --json")
    r2 = case.run("git rev-parse HEAD")
    r3 = case.run("git show --name-only --format= HEAD")
    exit_is(r1, 0)
    stdout_contains_line(r3, "docs/prd/orders/prd.md")
    stdout_not_contains(r3, ".prd-review.json")
    assert len(r2.lines) == 1, str(r2)
    assert one_json_line(r1) == {"interface": 1, "kind": "change.approve", "commit": r2.lines[0]}, str(r1)
    staged = case.git("diff", "--cached", "--name-only")
    stdout_is(staged, "")


@given(G0N)
def test_t263_5_pack_move_commits_the_vendored_pack(case):
    """@prd T-263.5"""
    case.steps(GP, GC)
    r1 = case.run("python CHANGE pack docs/prd/orders service 1.0.0")
    r2 = case.run("python HOOKS install docs/prd/orders")
    case.steps(command("git config core.hooksPath /dev/null"), GV)
    r3 = case.run(f"{APPROVE} --reply approved --dry-run 'no dry run (pack version only)'")
    r4 = case.run("git show --name-only --format= HEAD")
    for r in (r1, r2, r3, r4):
        exit_is(r, 0)
    stdout_contains_line(r4, ".prd-toolkit/pack-sources.json")
    stdout_contains(r4, [".prd-toolkit/packs/service/pack.yaml"])
    status = case.git("status", "--porcelain", "--untracked-files=all", "--", ".prd-toolkit/packs",
                      ".prd-toolkit/pack-sources.json")
    stdout_is(status, "")


@given(R)
def test_t263_6_refs_must_be_one_line(case):
    """@prd T-263.6"""
    before = snapshot(case.tmp)
    r = case.argv(["python", "CHANGE", "approve", "docs/prd/orders", "--reply", "approved", "--dry-run", "DRY",
                   "--refs", "FR-008\nE-001"])
    exit_is(r, 2)
    stdout_is(r, "")
    stderr_is(r, "approve: --refs must be one line\n")
    assert diff(before, snapshot(case.tmp)) == [], "files under <tmp> changed"


@named("write <tmp>/hooks/pre-commit, mode 0755, as the two lines `#!/bin/sh` and `echo 'hook says no' >&2; exit 1`")
def _refusing_hook(c):
    hook = c.path("<tmp>/hooks/pre-commit")
    write_text(hook, "#!/bin/sh\necho 'hook says no' >&2; exit 1\n")
    os.chmod(hook, 0o755)


@given(R, _refusing_hook, command("git config core.hooksPath <tmp>/hooks"))
def test_t263_7_a_failed_commit_puts_everything_back(case):
    """@prd T-263.7"""
    others = [case.tmp / "CLAUDE.md", case.tmp / "docs/prd/README.md", case.tmp / "docs/prd/orders/README.md"]
    assert not any(p.exists() for p in others), "a README or CLAUDE.md exists before the run"
    prd_before = prd_bytes(case)
    review_before = (case.orders / ".prd-review.json").read_bytes()
    r = case.run(f"{APPROVE} --reply approved --dry-run DRY")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: git commit failed: hook says no\n")
    assert prd_bytes(case) == prd_before, "prd.md differs from the file R left"
    review = case.orders / ".prd-review.json"
    assert review.exists() and review.read_bytes() == review_before, ".prd-review.json is gone or changed"
    staged = case.git("diff", "--cached", "--name-only")
    stdout_is(staged, "")
    assert last_subject(case) == "base\n"
    assert [p for p in others if p.exists()] == [], "the run left a README or CLAUDE.md"
