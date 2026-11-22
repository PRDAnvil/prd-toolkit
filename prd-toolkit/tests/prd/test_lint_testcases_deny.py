"""The deny-tested rule of lint-testcases (test-cases/lint-testcases.yaml, T-165.*)."""

from __future__ import annotations

import pytest

from lint_testcases_support import check, lint_case  # noqa: F401  (lint_case is a fixture)

PERMS = "contracts/permissions.yaml"


@pytest.mark.parametrize("lint_case", [{"setup": [("replace", PERMS, 3, "  rep: {secret: ORDERS_TEST_REP_TOKEN}")]}], indirect=True)
def test_deny_role_without_identity(lint_case):
    """@prd T-165.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/contracts/permissions.yaml:6: deny-tested: deny cell (deleteOrder, rep): role 'rep' has no test identity",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("replace", "test-cases/api.yaml", 66, "    errors: []")]}], indirect=True)
def test_deny_cell_without_case(lint_case):
    """@prd T-165.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/contracts/permissions.yaml:6: deny-tested: deny cell (deleteOrder, rep) has no test case with target op:deleteOrder, identity test-rep and expect.errors",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{
    "setup": [("replace", PERMS, 6, "  deleteOrder: {allow: [admin], deny: [[rep]]}")],
    "runs": [{}, {"before": ("delete_file", PERMS)}],
}], indirect=True)
def test_deny_not_checked(lint_case):
    """@prd T-165.3"""
    check(lint_case[0], {"stdout_not_contains": "deny-tested:", "stderr": ""})
    check(lint_case[1], {"stdout_not_contains": "deny-tested:", "stderr": ""})
