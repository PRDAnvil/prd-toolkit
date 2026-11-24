"""Black-box tests of a standards row's files mode in the pre-commit hook (docs/prd/prd-toolkit/test-cases/
standards-run.yaml, T-264.6 to T-264.9; features/standards-run.md, AC-264.4 to AC-264.6)."""
from __future__ import annotations

from pathlib import Path

from standards_run_support import given_steps, lint_log_lines, run, scratch  # noqa: F401  (scratch: a fixture)

PRD_DIR = "docs/prd/orders"

# The row's linter commands as the cases' expected stderr writes them between backticks.
LINTER = '''python3 -c "import sys; open('lint.log', 'a').write(' '.join(sys.argv[1:]) + chr(10)); bad = [a for a in sys.argv[1:] if '.prd-toolkit/' in a or a.endswith('bad.py')]; print(*bad, file=sys.stderr); sys.exit(1 if bad else 0)"'''
FAILING_LINTER = '''python3 -c "import sys; print('whole tree refused', file=sys.stderr); sys.exit(3)"'''


def _show(r) -> str:
    return f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"


@given_steps("SR0", "SM1", "SG4")
def test_none_row_runs_the_linter_once_with_no_path(scratch: Path):
    """@prd T-264.6"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 0, _show(r)
    assert r.stdout == ""
    assert r.stderr == ""
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the linter never ran"
    assert lint_log_lines(scratch) == [""], "lint.log does not hold exactly one empty line"


@given_steps("SR0", "SM1", "SG3")
def test_none_row_with_only_the_vendored_copy_staged_runs_nothing(scratch: Path):
    """@prd T-264.7"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 0, _show(r)
    assert r.stdout == ""
    assert r.stderr == ""
    assert not (scratch / "lint.log").exists(), "lint.log exists: the linter ran"


@given_steps("SR0", "SM4", "SG1")
def test_failing_none_row_reported_without_paths(scratch: Path):
    """@prd T-264.8"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 1, _show(r)
    assert r.stdout == ""
    assert r.stderr == "prd-toolkit: `" + FAILING_LINTER + "` failed (exit 3):\nwhole tree refused\n"


@given_steps("SR0", "SM2", "SG4")
def test_changed_row_is_given_the_staged_paths(scratch: Path):
    """@prd T-264.9"""
    r = run(scratch, "HOOK", "pre-commit", PRD_DIR)
    assert r.exit == 1, _show(r)
    assert r.stdout == ""
    assert r.stderr == (
        "prd-toolkit: `" + LINTER + "` failed (exit 1) on src/bad.py, src/ok.py:\n"
        "src/bad.py\n"
    )
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the linter never ran"
    assert lint_log_lines(scratch) == ["src/bad.py src/ok.py"]
