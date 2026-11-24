"""Black-box tests of a standards row's files mode in the generated CI (docs/prd/prd-toolkit/test-cases/
standards-run.yaml, T-264.1 to T-264.5; features/standards-run.md, AC-264.1 to AC-264.3)."""
from __future__ import annotations

from pathlib import Path

from standards_run_support import (  # noqa: F401  (scratch: a fixture)
    GITHUB_YML, GITLAB_YML, base_of, given_steps, lint_log_lines, run, run_sh, scratch, texts, yaml_at,
)

PRD_DIR = "docs/prd/orders"
GITHUB_JOB = "jobs.standards-1.steps.2.run"
GITLAB_JOB = "standards-1.script.0"


def _show(r) -> str:
    return f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"


@given_steps("SR0", "SM1", "SG5")
def test_none_row_job_runs_the_command_once_with_no_path(scratch: Path):
    """@prd T-264.1"""
    run_1 = run(scratch, "HOOKS", "ci", "--github", PRD_DIR)
    run_2 = run_sh(scratch, texts("none_job_line"))

    assert run_1.exit == 0, _show(run_1)
    assert run_1.stdout == "wrote .github/workflows/prd-toolkit.yml\n"
    assert run_1.stderr == ""
    assert run_2.exit == 0, _show(run_2)

    assert yaml_at(scratch / GITHUB_YML, GITHUB_JOB) == texts("none_job_line")
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the job's linter never ran"
    assert lint_log_lines(scratch) == [""], "lint.log does not hold exactly one empty line"


@given_steps("SR0", "SM1", "SM5", "SG5")
def test_none_row_job_runs_nothing_when_no_tracked_file_matches(scratch: Path):
    """@prd T-264.2"""
    run_1 = run(scratch, "HOOKS", "ci", "--gitlab", PRD_DIR)
    assert run_1.exit == 0, _show(run_1)
    assert run_1.stderr == ""

    job = yaml_at(scratch / GITLAB_YML, GITLAB_JOB)
    assert isinstance(job, str), f"{GITLAB_JOB} holds {job!r}, not a string"
    run_2 = run_sh(scratch, job)
    assert run_2.exit == 0, _show(run_2)
    assert run_2.stdout == ""
    assert run_2.stderr == ""

    assert not (scratch / "lint.log").exists(), "lint.log exists: the linter ran"


@given_steps("SR0", "SM2", "SC1")
def test_changed_row_gitlab_job_lints_the_changed_files(scratch: Path):
    """@prd T-264.3"""
    run_1 = run(scratch, "HOOKS", "ci", "--gitlab", PRD_DIR)
    run_2 = run_sh(scratch, texts("changed_job_gitlab"),
                   env={"CI_MERGE_REQUEST_DIFF_BASE_SHA": base_of(scratch)})

    assert run_1.exit == 0, _show(run_1)
    assert run_1.stderr == ""
    assert run_2.exit == 0, _show(run_2)

    assert yaml_at(scratch / GITLAB_YML, GITLAB_JOB) == texts("changed_job_gitlab")
    assert yaml_at(scratch / GITLAB_YML, "standards-1.variables.GIT_DEPTH") == "0"
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the job's linter never ran"
    assert lint_log_lines(scratch) == ["./src/new.py ./src/ok.py"]


@given_steps("SR0", "SM2")
def test_changed_row_github_job(scratch: Path):
    """@prd T-264.4"""
    r = run(scratch, "HOOKS", "ci", "--github", PRD_DIR)
    assert r.exit == 0, _show(r)
    assert r.stdout == "wrote .github/workflows/prd-toolkit.yml\n"
    assert r.stderr == ""
    assert yaml_at(scratch / GITHUB_YML, GITHUB_JOB) == texts("changed_job_github")


@given_steps("SR0", "SM3")
def test_unknown_mode_runs_as_an_appended_row(scratch: Path):
    """@prd T-264.5"""
    r = run(scratch, "HOOKS", "ci", "--github", PRD_DIR)
    assert r.exit == 0, _show(r)
    assert r.stdout == "wrote .github/workflows/prd-toolkit.yml\n"
    assert r.stderr == ""
    assert yaml_at(scratch / GITHUB_YML, GITHUB_JOB) == texts("job_line")
