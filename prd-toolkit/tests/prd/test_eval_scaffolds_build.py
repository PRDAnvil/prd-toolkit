"""Black-box tests of the eval scaffolds' start states (features/eval-scaffolds.md, FR-073)."""
from eval_scaffolds_support import (
    REVIEW_EDITS_NOTHING_SCAFFOLD,
    deploy_repo,
    describe,
    git_lines,
    git_stdout,
    run,
)


def test_ready_commits_what_install_wrote_and_leaves_a_clean_tree(tmp_path):
    """@prd T-073.1"""
    dst = tmp_path / "repo"
    proc = deploy_repo(dst, "ready", cwd=tmp_path)
    assert proc.returncode == 0, describe(proc)

    assert git_stdout(dst, "status", "--porcelain") == ""
    assert git_lines(dst, "ls-files", "CLAUDE.md", "docs/prd/README.md", "docs/prd/greet/README.md") == [
        "CLAUDE.md",
        "docs/prd/README.md",
        "docs/prd/greet/README.md",
    ]


def test_at_gate_prints_its_run_and_leaves_a_clean_tree(tmp_path):
    """@prd T-073.2"""
    dst = tmp_path / "repo"
    proc = deploy_repo(dst, "at-gate", cwd=tmp_path)
    assert proc.returncode == 0, describe(proc)

    lines = proc.stdout.splitlines()
    assert lines, describe(proc)
    last = lines[-1]
    assert last.startswith("run=") and len(last) > len("run="), describe(proc)
    assert git_stdout(dst, "status", "--porcelain") == ""


def test_failing_check_puts_the_install_commit_after_the_vendor_commit(tmp_path):
    """@prd T-073.3"""
    dst = tmp_path / "repo"
    proc = deploy_repo(dst, "failing-check", cwd=tmp_path)
    assert proc.returncode == 0, describe(proc)

    assert git_lines(dst, "log", "--format=%s") == [
        "Try a friendlier greeting",
        "Add the files install wrote",
        "Vendor the PRD toolkit",
        "Ignore the judge record",
        "PRD: greet 1.0.0 Approved, every requirement verified",
        "Add the deploy script and tests",
        "Add the greet command",
    ]
    assert git_lines(dst, "log", "-1", "--format=%B", "HEAD~1") == [
        "Add the files install wrote",
        "",
        "Refs: none (no behaviour change)",
    ]
    assert git_lines(dst, "log", "-1", "--format=%ad%n%cd", "--date=raw", "HEAD~1") == [
        "1767618000 +0000",
        "1767618000 +0000",
    ]
    assert git_lines(dst, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD~1") == [
        "CLAUDE.md",
        "docs/prd/README.md",
        "docs/prd/greet/README.md",
    ]
    assert git_lines(dst, "log", "--format=%ad", "--date=raw", "HEAD~2") == [
        "1767614400 +0000",
        "1767610800 +0000",
        "1767528000 +0000",
        "1767441600 +0000",
        "1767355200 +0000",
    ]
    assert git_stdout(dst, "status", "--porcelain") == ""


def test_review_edits_nothing_scaffold_expects_the_row_record_writes(tmp_path):
    """@prd T-073.4"""
    work = tmp_path / "work"
    work.mkdir()
    proc = run(["bash", REVIEW_EDITS_NOTHING_SCAFFOLD], cwd=work)
    assert proc.returncode == 0, describe(proc)

    prd_md = work / "docs/prd/orders/prd.md"
    assert prd_md.is_file(), describe(proc)
    lines = prd_md.read_text(encoding="utf-8").splitlines()
    assert "| FR-001 | Import an orders file | approved | features/import.md |  |" in lines
