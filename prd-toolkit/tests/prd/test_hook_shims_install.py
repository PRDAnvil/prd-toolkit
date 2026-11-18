"""hook-shims: install where core.hooksPath is set (test-cases/hook-shims.yaml, FR-070)."""
from __future__ import annotations

from hook_shims_support import (  # noqa: F401  (scratch is a fixture)
    PRD_DIR, assert_lines_in_relative_order, executable_by_owner, given_steps, run_hooks, scratch, texts,
)

HOOK_LINES = [
    "replaced .git/hooks/commit-msg (it used uv run --script)",
    "replaced .git/hooks/pre-commit (it used uv run --script)",
]


def _hook_lines(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if line.startswith("replaced ") or line.startswith("installed ")]


@given_steps("HS0")
def test_install_rewrites_toolkit_hooks_where_hooks_path_is_git_hooks(scratch):
    """@prd T-070.1"""
    a, b = scratch / "a", scratch / "b"
    run_1 = run_hooks(b, "install", PRD_DIR)
    run_2 = run_hooks(a, "install", PRD_DIR)

    for name, r in (("run_1", run_1), ("run_2", run_2)):
        assert r.exit == 0, f"{name} exited {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        assert r.stderr == "", f"{name} stderr:\n{r.stderr}"
        assert_lines_in_relative_order(r.stdout, HOOK_LINES)

    assert _hook_lines(run_2.stdout) == _hook_lines(run_1.stdout), (
        f"run_2's replaced/installed lines differ from run_1's:\nrun_1:\n{run_1.stdout}\nrun_2:\n{run_2.stdout}")

    for hook in ("commit-msg", "pre-commit"):
        a_hook, b_hook = a / ".git/hooks" / hook, b / ".git/hooks" / hook
        assert a_hook.read_bytes() == b_hook.read_bytes(), f"{a_hook} differs from {b_hook}"
        assert executable_by_owner(a_hook), f"{a_hook} is not executable by its owner"
        assert executable_by_owner(b_hook), f"{b_hook} is not executable by its owner"


@given_steps("HS2")
def test_install_leaves_absent_and_own_hooks_where_hooks_path_is_set(scratch):
    """@prd T-070.3"""
    r = run_hooks(scratch, "install", PRD_DIR)

    assert r.exit == 0, f"exited {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stderr == "", f"stderr:\n{r.stderr}"
    for want in (
        "core.hooksPath is set to hooks; no shim written; add this line to hooks/commit-msg "
        "(an sh hook; place it before any `exit 0` in it): ",
        "core.hooksPath is set to hooks; no shim written; add this line to hooks/pre-commit "
        "(an sh hook; place it before any `exit 0` in it): ",
    ):
        assert want in r.stdout, f"stdout lacks {want!r}:\n{r.stdout}"
    for unwanted in ("installed hooks/", "replaced hooks/"):
        assert unwanted not in r.stdout, f"stdout holds {unwanted!r}:\n{r.stdout}"

    assert (scratch / "hooks/pre-commit").read_bytes() == texts()["own_pre_commit"].encode("utf-8")
    assert not (scratch / "hooks/commit-msg").exists(), "hooks/commit-msg exists"
