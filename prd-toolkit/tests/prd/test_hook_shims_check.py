"""hook-shims: check after an install where core.hooksPath is set (test-cases/hook-shims.yaml, FR-070, E-024)."""
from __future__ import annotations

from hook_shims_support import (  # noqa: F401  (scratch is a fixture)
    PRD_DIR, assert_lines_in_relative_order, executable_by_owner, given_steps, run_hooks, scratch,
)


@given_steps("HS1")
def test_check_calls_no_rewritten_hook_stale(scratch):
    """@prd T-070.2"""
    run_1 = run_hooks(scratch, "install", PRD_DIR)

    assert run_1.exit == 0, f"run_1 exited {run_1.exit}\nstdout:\n{run_1.stdout}\nstderr:\n{run_1.stderr}"
    assert run_1.stderr == "", f"run_1 stderr:\n{run_1.stderr}"
    assert_lines_in_relative_order(run_1.stdout, [
        "installed hooks/commit-msg",
        "replaced hooks/pre-commit (it used uv run --script)",
    ])
    assert "core.hooksPath is set to" not in run_1.stdout, f"run_1 stdout:\n{run_1.stdout}"

    for hook in ("commit-msg", "pre-commit"):
        path = scratch / "hooks" / hook
        assert executable_by_owner(path), f"after run_1, {path} is not executable by its owner"

    run_2 = run_hooks(scratch, "check", PRD_DIR)

    assert run_2.stderr == "", f"run_2 stderr:\n{run_2.stderr}"
    for unwanted in ("stale: hooks/commit-msg", "stale: hooks/pre-commit"):
        assert unwanted not in run_2.stdout, f"run_2 stdout holds {unwanted!r}:\n{run_2.stdout}"
