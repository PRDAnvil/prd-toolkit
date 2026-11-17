"""Black-box tests of the generated CI's standards job (docs/prd/prd-toolkit/test-cases/standards-run.yaml,
T-068.5 to T-068.7; features/standards-run.md, AC-068.4 and AC-068.5)."""
from __future__ import annotations

from pathlib import Path

from standards_run_support import (  # noqa: F401  (scratch: a fixture)
    GITHUB_YML, GITLAB_YML, SO, given_steps, lint_log_lines, run, run_sh, scratch, texts, yaml_at,
)

PRD_DIR = "docs/prd/orders"


def _show(r) -> str:
    return f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"


@given_steps("SR0", "SG5")
def test_github_job_leaves_out_the_vendored_copy(scratch: Path):
    """@prd T-068.5"""
    run_1 = run(scratch, "HOOKS", "ci", "--github", PRD_DIR)
    run_2 = run_sh(scratch, texts("job_line"))

    assert run_1.exit == 0, _show(run_1)
    assert run_1.stdout == "wrote .github/workflows/prd-toolkit.yml\n"
    assert run_1.stderr == ""

    # relations: run_2's exit code is not 0.
    assert run_2.exit != 0, _show(run_2)

    assert yaml_at(scratch / GITHUB_YML, "jobs.standards-1.steps.2.run") == texts("job_line")
    assert (scratch / "lint.log").is_file(), "lint.log does not exist: the job's linter never ran"
    assert lint_log_lines(scratch) == ["./src/.prd-toolkit/x.py ./src/ok.py ./tests/test_orders.py"]


@given_steps("SR0")
def test_gitlab_job_leaves_out_the_vendored_copy(scratch: Path):
    """@prd T-068.6"""
    r = run(scratch, "HOOKS", "ci", "--gitlab", PRD_DIR)
    assert r.exit == 0, _show(r)
    assert r.stderr == ""
    assert r.stdout.splitlines() == [
        "wrote .gitlab/prd-toolkit.yml",
        "include: '.gitlab/prd-toolkit.yml'",
    ]
    assert yaml_at(scratch / GITLAB_YML, "standards-1.script.0") == texts("job_line")


@given_steps("SR0")
def test_include_from_an_earlier_release_is_stale(scratch: Path):
    """@prd T-068.7"""
    run_1 = run(scratch, "HOOKS", "ci", "--github", PRD_DIR)
    run_2 = run(scratch, "HOOKS", "check", "--ci", PRD_DIR)
    assert run_1.exit == 0, _show(run_1)
    assert ".github/workflows/prd-toolkit.yml" not in run_2.stdout, _show(run_2)

    SO(scratch)  # the job line a release before this area wrote (texts.old_job_line)
    run_3 = run(scratch, "HOOKS", "check", "--ci", PRD_DIR)
    assert run_3.exit == 1, _show(run_3)
    assert "stale: .github/workflows/prd-toolkit.yml: re-run prd_hooks.py ci --github --force" \
        in run_3.stdout.splitlines(), _show(run_3)
