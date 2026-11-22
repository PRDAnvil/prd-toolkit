"""lint-testcases, FR-149: a test case for every live acceptance criterion (test-cases/lint-testcases.yaml)."""

import pytest

from lint_testcases_support import check, lint_case  # noqa: F401  (lint_case is a fixture)


def case(**spec):
    return pytest.mark.parametrize("lint_case", [spec], indirect=True)


@case(setup=[("replace", "test-cases/api.yaml", 19, "  ac: AC-002.1")])
def test_uncovered_criterion_is_reported(lint_case):
    """@prd T-149.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/features/api.md:16: ac-has-test: AC-002.2 has no test case whose ac: is AC-002.2",
        "stderr": "",
    })


@case(setup=[
    ("replace", "test-cases/api.yaml", 19, "  ac: AC-002.1"),
    ("replace", "test-cases/import.yaml", 20, "  ac: AC-002.2"),
])
def test_case_in_another_areas_file_counts(lint_case):
    """@prd T-149.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/features/import.md:10: ac-has-test: AC-001.2 has no test case whose ac: is AC-001.2",
        "stdout_not_contains": "ac-has-test: AC-002.2",
        "stderr": "",
    })


@case(setup=[
    ("replace", "features/api.md", 16,
     "- AC-002.2 (removed in 1.0.0) If the order id does not exist, the API shall respond 404 with error ORDER_NOT_FOUND."),
    ("replace", "test-cases/api.yaml", 19, "  ac: AC-002.1"),
    ("replace", "features/api.md", 22, "Status: removed"),
    ("replace", "test-cases/api.yaml", 52, "  ac: AC-003.1"),
])
def test_removed_criterion_and_block_are_not_reported(lint_case):
    """@prd T-149.3"""
    check(lint_case[0], {"stdout_not_contains": "ac-has-test:", "stderr": ""})
