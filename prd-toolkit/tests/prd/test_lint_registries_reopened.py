"""lint-registries AC-145.1 (`not a defect`) and AC-146.4 (the Reopened: line's form)
(test-cases/lint-registries.yaml)."""
from __future__ import annotations

from lint_registries_support import (  # noqa: F401  (case is a pytest fixture)
    S0,
    assert_exit,
    assert_stderr,
    assert_stdout,
    assert_stdout_exact_lines,
    case,
    insert_after,
    replace,
    steps,
)


@steps(S0, replace("errors.md", 5, "Classification: not a defect"))
def test_not_a_defect_is_a_class(case):
    """@prd T-145.5"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0, insert_after("errors.md", 5, "Reopened: 2026-11-04, the run passes now"))
def test_reopened_line_out_of_form(case):
    """@prd T-146.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [
        "docs/prd/orders/errors.md:6: error-entries: E-001: Reopened: must be "
        "'<YYYY-MM-DD>, \"<reason>\"; was Confirmed: <YYYY-MM-DD>, \"<reply>\"'",
    ])
    assert_stderr(r, "")


@steps(S0, insert_after(
    "errors.md", 5,
    'Reopened: 2026-11-04, "the run passes now"; was Confirmed: 2026-11-03, "yes, a code bug"',
))
def test_reopened_line_in_form(case):
    """@prd T-146.5"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")
