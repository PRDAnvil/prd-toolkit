"""lint-testcases: a judged case's rubric, threshold, runs and output (FR-157, FR-158).

Written from docs/prd/prd-toolkit/test-cases/lint-testcases.yaml and testing.md only.
"""

from __future__ import annotations

import pytest

from lint_testcases_support import KnownFailure, check, lint_case, texts  # noqa: F401  (lint_case is a fixture)

IMPORT = "test-cases/import.yaml"
F = "docs/prd/orders/test-cases/import.yaml"
T = texts()


def _runs(*befores):
    return [{"before": None}] + [{"before": b} for b in befores]


@pytest.mark.parametrize(
    "lint_case", [{"setup": [("replace", IMPORT, 46, T["judged_ok"])]}], indirect=True
)
def test_judged_case_well_formed_lints_clean(lint_case):
    """@prd T-157.1"""
    check(lint_case[0], {"exit": 0, "stdout": "", "stderr": ""})


@pytest.mark.parametrize(
    "lint_case",
    [
        {
            "setup": [("replace", IMPORT, 46, T["rubric_empty"])],
            "runs": _runs(("replace", IMPORT, 46, "    rubric: [The importer reports status empty, 3]")),
        }
    ],
    indirect=True,
)
def test_judged_rubric_empty_or_not_strings(lint_case):
    """@prd T-157.2"""
    line = f"{F}:46: judged-case: T-001.3: rubric must be a non-empty list of non-empty strings"
    for run in lint_case:
        check(run, {"exit": 1, "stdout_contains_line": line, "stderr": ""})
    assert len(lint_case) == 2


@pytest.mark.parametrize(
    "lint_case", [{"setup": [("replace", IMPORT, 46, T["rubric_repeat"])]}], indirect=True
)
def test_judged_rubric_repeats(lint_case):
    """@prd T-157.3"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_lines_in_this_relative_order": [
                f"{F}:46: judged-case: T-001.3: rubric item 3 repeats item 1",
                f"{F}:46: judged-case: T-001.3: rubric item 4 repeats item 1",
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    [
        {
            "setup": [("replace", IMPORT, 46, T["threshold_zero"])],
            "runs": _runs(
                ("replace", IMPORT, 48, "    threshold: true"),
                ("replace", IMPORT, 48, "    threshold: 1.5"),
                ("replace", IMPORT, 48, "    threshold: high"),
                ("delete", IMPORT, 48),
            ),
        }
    ],
    indirect=True,
)
def test_judged_threshold_out_of_range(lint_case):
    """@prd T-157.4"""
    msg = "judged-case: T-001.3: threshold must be a number in (0, 1]"
    assert len(lint_case) == 5
    for run in lint_case[:4]:
        check(run, {"exit": 1, "stdout_contains_line": f"{F}:48: {msg}", "stderr": ""})
    check(lint_case[4], {"exit": 1, "stdout_contains_line": f"{F}:46: {msg}", "stderr": ""})


@pytest.mark.parametrize(
    "lint_case",
    [
        {
            "setup": [("replace", IMPORT, 46, T["runs_zero"])],
            "runs": _runs(
                ("replace", IMPORT, 49, "    runs: 2.5"),
                ("replace", IMPORT, 49, "    runs: true"),
                ("replace", IMPORT, 49, "    runs: 1"),
            ),
        }
    ],
    indirect=True,
)
def test_judged_runs_not_a_positive_integer(lint_case):
    """@prd T-157.5"""
    line = f"{F}:49: judged-case: T-001.3: runs must be an integer of at least 1"
    assert len(lint_case) == 4
    for run in lint_case[:3]:
        check(run, {"exit": 1, "stdout_contains_line": line, "stderr": ""})
    check(lint_case[3], {"stdout_not_contains": "runs must be an integer", "stderr": ""})


@pytest.mark.parametrize(
    "lint_case", [{"setup": [("replace", IMPORT, 46, T["judged_output"])]}], indirect=True
)
def test_judged_case_with_output(lint_case):
    """@prd T-157.6"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": f"{F}:49: judged-case: T-001.3: a judged case has no expect.output",
            "stdout_not_contains": "sufficiency: T-001.3: expect.output is missing",
            "stderr": "",
        },
    )


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-055")
@pytest.mark.parametrize(
    "lint_case", [{"setup": [("replace", IMPORT, 46, T["rubric_inner_space"])]}], indirect=True
)
def test_judged_rubric_repeat_by_inner_space(lint_case):
    """@prd T-157.7 known-failing E-055"""
    run = lint_case[0]
    # The symptom of E-055: the exit code is 0 and stdout is empty.
    if run.exit == 0 and run.stdout == "":
        raise KnownFailure("E-055: exit 0 and empty stdout")
    check(
        run,
        {
            "exit": 1,
            "stdout_contains_line": f"{F}:46: judged-case: T-001.3: rubric item 2 repeats item 1",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case", [{"setup": [("replace", IMPORT, 46, T["threshold_067"])]}], indirect=True
)
def test_judged_threshold_needs_every_item_of_three(lint_case):
    """@prd T-158.1"""
    check(
        lint_case[0],
        {
            "exit": 0,
            "stdout_exact_lines": [
                f"{F}:50: warn: judged-case: T-001.3: threshold 0.67 needs all 3 items (2 of 3 is 0.6667); write 0.66 to allow one miss, or 1.0"
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case", [{"setup": [("replace", IMPORT, 46, T["threshold_two"])]}], indirect=True
)
def test_judged_threshold_needs_every_item_of_two(lint_case):
    """@prd T-158.2"""
    check(
        lint_case[0],
        {
            "exit": 0,
            "stdout_exact_lines": [
                f"{F}:49: warn: judged-case: T-001.3: threshold 0.67 needs all 2 items (1 of 2 is 0.5); write 0.5 to allow one miss, or 1.0"
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    [
        {
            "setup": [("replace", IMPORT, 46, T["threshold_five"])],
            "runs": _runs(
                ("replace", IMPORT, 52, "    threshold: 0.5"),
                ("replace", IMPORT, 52, "    threshold: 1.0"),
            ),
        }
    ],
    indirect=True,
)
def test_judged_threshold_allowing_a_miss_no_warning(lint_case):
    """@prd T-158.3"""
    assert len(lint_case) == 3
    for run in lint_case:
        check(run, {"exit": 0, "stdout": "", "stderr": ""})
