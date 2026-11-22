"""lint-registries: FR-135 to FR-138, the runbook-steps rule (test-cases/lint-registries.yaml)."""
from lint_registries_support import (  # noqa: F401  (case is a pytest fixture)
    S0, assert_exit, assert_stderr, assert_stdout, assert_stdout_contains_line,
    assert_stdout_exact_lines, assert_stdout_not_contains, case, delete_file, delete_line,
    insert_after, replace, steps, text,
)

OPS = "docs/prd/orders/operations.md"


@steps(S0, replace("operations.md", 27, "6. Smoke on production (actor: agent) (env: production)"))
def test_step_number_after_last(case):
    """@prd T-135.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:27: runbook-steps: step 6: expected step 5"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 20, "4. Approve production (actor: human) (env: production)"))
def test_step_number_repeated(case):
    """@prd T-135.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [
        f"{OPS}:20: runbook-steps: step 4: expected step 3",
        f"{OPS}:23: runbook-steps: step 4: expected step 5",
    ])
    assert_stderr(r, "")


@steps(S0, insert_after("operations.md", 17, "   Rollback: `./deploy.sh staging --previous`"))
def test_label_twice(case):
    """@prd T-135.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:18: runbook-steps: step 1: label Rollback appears twice"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 20, "3. Approve production (env: production)"))
def test_step_line_without_actor(case):
    """@prd T-135.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, f"{OPS}:20: runbook-steps: step 3: the step line needs (actor: agent|human) (env: <environment>)")
    assert_stdout_not_contains(r, ["operations.md:21: runbook-steps", "operations.md:22: runbook-steps",
                                   "(prd-toolkit 0.5 runbook format)"])
    assert_stderr(r, "")


@steps(S0,
       replace("operations.md", 14, "1. Deploy to staging (actor: agent)"),
       replace("operations.md", 18, "2. System tests on staging (actor: agent)"),
       replace("operations.md", 20, "3. Approve production (actor: human)"),
       replace("operations.md", 23, "4. Deploy to production (actor: agent)"),
       replace("operations.md", 27, "5. Smoke on production (actor: agent)"))
def test_old_runbook_format_hint(case):
    """@prd T-135.5"""
    r = case.lint()
    assert_exit(r, 1)
    needs = "the step line needs (actor: agent|human) (env: <environment>)"
    assert_stdout_exact_lines(r, [
        f"{OPS}:14: runbook-steps: step 1: {needs} (prd-toolkit 0.5 runbook format)",
        f"{OPS}:18: runbook-steps: step 2: {needs}",
        f"{OPS}:20: runbook-steps: step 3: {needs}",
        f"{OPS}:23: runbook-steps: step 4: {needs}",
        f"{OPS}:27: runbook-steps: step 5: {needs}",
    ])
    assert_stderr(r, "")


@steps(S0, delete_file("operations.md"))
def test_no_operations_file_steps(case):
    """@prd T-135.6"""
    r = case.lint()
    assert_stdout_not_contains(r, "runbook-steps")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 21, "   Run: `./deploy.sh production`"))
def test_human_step_with_run(case):
    """@prd T-136.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:21: runbook-steps: step 3: a human step takes Do: and Check:, not Run:"])
    assert_stderr(r, "")


@steps(S0, insert_after("operations.md", 22, "   Run: `./deploy.sh production`",
                        "   Rollback: `./deploy.sh production --previous`"))
def test_human_step_with_run_and_rollback(case):
    """@prd T-136.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:23: runbook-steps: step 3: a human step takes Do: and Check:, not Run: or Rollback:"])
    assert_stderr(r, "")


@steps(S0, delete_line("operations.md", 22))
def test_human_step_without_check(case):
    """@prd T-136.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:20: runbook-steps: step 3: a human step needs Do: and Check:"])
    assert_stderr(r, "")


@steps(S0, insert_after("operations.md", 15, "   Do: press the button"))
def test_agent_step_with_do(case):
    """@prd T-137.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:16: runbook-steps: step 1: an agent step takes Run:, Check: and Rollback:, not Do:"])
    assert_stderr(r, "")


@steps(S0, delete_line("operations.md", 15))
def test_agent_step_without_run(case):
    """@prd T-137.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:14: runbook-steps: step 1: an agent step needs Run:"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 15, "   Run: ./deploy.sh staging"))
def test_run_without_backticks(case):
    """@prd T-137.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:15: runbook-steps: step 1: Run: must be one backticked command or tests <level>[, <level>]; got './deploy.sh staging'"])
    assert_stderr(r, "")


@steps(S0, delete_line("operations.md", 16))
def test_agent_step_without_check(case):
    """@prd T-137.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:14: runbook-steps: step 1: an agent step needs Check:"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 16, "   Check: curl it"))
def test_check_without_backticks(case):
    """@prd T-137.5"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:16: runbook-steps: step 1: Check: must be one backticked command, optionally followed by prints `<text>`; got 'curl it'"])
    assert_stderr(r, "")


@steps(S0,
       replace("operations.md", 15, text("run_marker")),
       replace("operations.md", 16, text("check_marker")),
       replace("operations.md", 17, text("rollback_marker")))
def test_clarification_markers_skip_form(case):
    """@prd T-137.7"""
    r = case.lint()
    assert_stdout_not_contains(r, "runbook-steps")
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 17, "   Rollback: ./deploy.sh staging --previous"))
def test_rollback_without_backticks(case):
    """@prd T-137.6"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:17: runbook-steps: step 1: Rollback: must be one backticked command; got './deploy.sh staging --previous'"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 16,
                   "   Check: `curl -fsS https://orders-staging.example.com/health` prints `ok` prints `ok`"))
def test_check_with_prints_twice(case):
    """@prd T-137.8"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:16: runbook-steps: step 1: Check: must be one backticked command, optionally followed by prints `<text>`; got '`curl -fsS https://orders-staging.example.com/health` prints `ok` prints `ok`'"])
    assert_stderr(r, "")


@steps(S0, replace("operations.md", 19, "   Run: tests ,"))
def test_tests_step_names_no_levels(case):
    """@prd T-138.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:19: runbook-steps: step 2: a tests step names no levels"])
    assert_stderr(r, "")


@steps(S0, insert_after("operations.md", 19, "   Check: `true`"))
def test_tests_step_with_check(case):
    """@prd T-138.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:20: runbook-steps: step 2: a tests step has no Check:"])
    assert_stderr(r, "")


@steps(S0, insert_after("operations.md", 19, "   Rollback: undo it"))
def test_tests_step_rollback_without_backticks(case):
    """@prd T-138.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [f"{OPS}:20: runbook-steps: step 2: Rollback: must be one backticked command; got 'undo it'"])
    assert_stderr(r, "")


@steps(S0)
def test_tests_steps_need_no_check(case):
    """@prd T-138.4"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")
