"""lint-testcases: an acceptance case's steps: and signoff: (FR-156).

Written from docs/prd/prd-toolkit/test-cases/lint-testcases.yaml and testing.md only.
"""

from __future__ import annotations

import pytest

from lint_testcases_support import check, lint_case, texts  # noqa: F401  (lint_case is a fixture)

IMPORT = "test-cases/import.yaml"
P = "docs/prd/orders/"


@pytest.mark.parametrize(
    "lint_case",
    [{"setup": [("replace", IMPORT, 67, "  steps: Do it"), ("delete_range", IMPORT, 68, 70)]}],
    indirect=True,
)
def test_acceptance_steps_not_a_list(lint_case):
    """@prd T-156.1"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": P
            + "test-cases/import.yaml:67: sufficiency: T-001.4: an acceptance case needs steps: a non-empty list of strings",
            "stderr": "",
        },
    )


@pytest.mark.parametrize("lint_case", [{"setup": [("delete", IMPORT, 71)]}], indirect=True)
def test_acceptance_signoff_absent(lint_case):
    """@prd T-156.2"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": P
            + "test-cases/import.yaml:53: sufficiency: T-001.4: an acceptance case needs signoff: the business owner",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    [{"setup": [("insert_after", IMPORT, 51, texts()["acceptance_keys_on_unit"])]}],
    indirect=True,
)
def test_acceptance_keys_on_a_unit_case_not_checked(lint_case):
    """@prd T-156.3"""
    check(lint_case[0], {"stdout_not_contains": "an acceptance case needs", "stderr": ""})
