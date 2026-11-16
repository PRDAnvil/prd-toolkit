"""Black-box tests of the pre-commit hook's standards run (docs/prd/prd-toolkit/test-cases/standards-run.yaml,
T-068.1 to T-068.4; features/standards-run.md, AC-068.1 to AC-068.3)."""
from __future__ import annotations

from pathlib import Path

from standards_run_support import given_steps, lint_log_lines, run, scratch  # noqa: F401  (scratch: a fixture)

PRD_DIR = "docs/prd/orders"

# The row's linter command as the cases' expected stderr writes it between backticks.
LINTER = '''python3 -c "import sys; open('lint.log', 'a').write(' '.join(sys.argv[1:]) + chr(10)); bad = [a for a in sys.argv[1:] if '.prd-toolkit/' in a or a.endswith('bad.py')]; print(*bad, file=sys.stderr); sys.exit(1 if bad else 0)"'''


@given_steps("SR0", "SG1")
def test_vendored_copy_left_out_of_the_staged_paths(scratch: Path):
    """@prd T-068.1"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 0, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout == ""
    assert r.stderr == ""
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the linter never ran"
    assert lint_log_lines(scratch) == ["src/ok.py"]


@given_steps("SR0", "SG2")
def test_other_prd_toolkit_names_are_ordinary_paths(scratch: Path):
    """@prd T-068.2"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 1, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout == ""
    assert r.stderr == (
        "prd-toolkit: `" + LINTER + "` failed (exit 1) on .prd-toolkit-notes.py, src/.prd-toolkit/x.py:\n"
        "src/.prd-toolkit/x.py\n"
    )
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the linter never ran"
    assert lint_log_lines(scratch) == [".prd-toolkit-notes.py src/.prd-toolkit/x.py"]


@given_steps("SR0", "SG3")
def test_vendor_only_commit_runs_no_linter(scratch: Path):
    """@prd T-068.3"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 0, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout == ""
    assert r.stderr == ""
    assert not (scratch / "lint.log").exists(), "lint.log exists: the linter ran"


@given_steps("SR0", "SG4")
def test_failing_linter_reported_on_the_paths_it_was_given(scratch: Path):
    """@prd T-068.4"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 1, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout == ""
    assert r.stderr == (
        "prd-toolkit: `" + LINTER + "` failed (exit 1) on src/bad.py, src/ok.py:\n"
        "src/bad.py\n"
    )
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the linter never ran"
    assert lint_log_lines(scratch) == ["src/bad.py src/ok.py"]
