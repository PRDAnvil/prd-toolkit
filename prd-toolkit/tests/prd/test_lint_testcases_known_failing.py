"""The known-failing: and symptom: references of lint-testcases (test-cases/lint-testcases.yaml, T-163.*)."""

from __future__ import annotations

import pytest

from lint_testcases_support import check, lint_case, texts  # noqa: F401  (lint_case is a fixture)

T = texts()
IMPORT = "test-cases/import.yaml"


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", IMPORT, 38, T["kf_unknown"])]}], indirect=True)
def test_known_failing_unknown_entry(lint_case):
    """@prd T-163.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: known-failing 'E-099' must be an E-nnn entry of errors.md",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", IMPORT, 38, T["kf_e001"])]}], indirect=True)
def test_known_failing_resolved_entry(lint_case):
    """@prd T-163.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: known-failing E-001 is resolved in errors.md; remove the line",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{
    "setup": [("insert_after", IMPORT, 38, "  symptom: the importer crashes")],
    "runs": [{}, {"before": ("replace", IMPORT, 39, '  symptom: ""')}],
}], indirect=True)
def test_symptom_without_known_failing(lint_case):
    """@prd T-163.3"""
    line = "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: symptom: needs known-failing: on the same case"
    check(lint_case[0], {"exit": 1, "stdout_contains_line": line, "stderr": ""})
    check(lint_case[1], {"exit": 1, "stdout_contains_line": line, "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("replace", "errors.md", 7, "Resolution: open"),
        ("insert_after", IMPORT, 38, "  known-failing: E-001"),
    ],
    "runs": [{}, {"before": ("insert_after", IMPORT, 39, "  symptom: 3")}],
}], indirect=True)
def test_known_failing_without_symptom_warns(lint_case):
    """@prd T-163.4"""
    lines = ["docs/prd/orders/test-cases/import.yaml:39: warn: test-refs: T-001.3: known-failing E-001 names no symptom; any failure would pass as it"]
    check(lint_case[0], {"exit": 0, "stdout_exact_lines": lines, "stderr": ""})
    check(lint_case[1], {"exit": 0, "stdout_exact_lines": lines, "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("replace", "errors.md", 7, "Resolution: open"),
        ("insert_after", IMPORT, 38, T["kf_e001"]),
    ],
}], indirect=True)
def test_known_failing_open_entry_with_symptom_is_clean(lint_case):
    """@prd T-163.5"""
    check(lint_case[0], {"exit": 0, "stdout": "", "stderr": ""})
