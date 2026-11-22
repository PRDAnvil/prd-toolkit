"""lint-testcases: a test case's references (FR-159 to FR-162).

Written from docs/prd/prd-toolkit/test-cases/lint-testcases.yaml and testing.md only.
"""

from __future__ import annotations

import pytest

from lint_testcases_support import KnownFailure, check, contains_line, lint_case, texts  # noqa: F401  (lint_case is a fixture)

API = "test-cases/api.yaml"
IMPORT = "test-cases/import.yaml"
NFR = "test-cases/nfr.yaml"
D = "docs/prd/orders/"
T = texts()


def _one(*steps):
    return [{"setup": list(steps)}]


@pytest.mark.parametrize("lint_case", _one(("replace", API, 2, "  ac: AC-002.7")), indirect=True)
def test_ac_names_no_criterion(lint_case):
    """@prd T-159.1"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/api.yaml:2: test-refs: T-002.1: AC-002.7 is not an acceptance criterion in any requirement block",
            "stderr": "",
        },
    )


@pytest.mark.parametrize("lint_case", _one(("replace", API, 2, "  ac: AC-001.1")), indirect=True)
def test_ac_of_another_requirement(lint_case):
    """@prd T-159.2"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/api.yaml:2: test-refs: T-002.1: AC-001.1 belongs to requirement 001, but T-002.1 is numbered for requirement 002",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case", _one(("replace", API, 7, "  preconditions: [customers/two_customers, 3]")), indirect=True
)
def test_precondition_not_a_string(lint_case):
    """@prd T-160.1"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/api.yaml:7: test-refs: T-002.1: precondition 3 must be a fixture name or mock:<service>",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    _one(("replace", IMPORT, 8, "  preconditions: [customers/two_customers, mock:payments]")),
    indirect=True,
)
def test_precondition_mock_without_dependency(lint_case):
    """@prd T-160.2"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/import.yaml:8: test-refs: T-001.1: mock:payments has no contracts/dependencies/payments.yaml",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    _one(("replace", API, 7, "  preconditions: [customers/two_customers, orders/missing]")),
    indirect=True,
)
def test_precondition_fixture_in_neither_place(lint_case):
    """@prd T-160.3"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_lines_in_this_relative_order": [
                D
                + "test-cases/api.yaml:7: test-refs: T-002.1: fixture 'orders/missing' is not in the Fixtures table of testing.md",
                D
                + "test-cases/api.yaml:7: test-refs: T-002.1: fixture 'orders/missing' has no file or directory at contracts/fixtures/orders/missing",
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    _one(
        ("insert_after", "testing.md", 55, T["ghost_rows"]),
        ("replace", API, 7, "  preconditions: [customers/ghost, customers]"),
    ),
    indirect=True,
)
def test_precondition_fixture_in_table_without_file(lint_case):
    """@prd T-160.4"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/api.yaml:7: test-refs: T-002.1: fixture 'customers/ghost' has no file or directory at contracts/fixtures/customers/ghost",
            "stdout_not_contains": ["fixture 'customers/ghost' is not in the Fixtures table", "fixture 'customers' "],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case", _one(("replace", IMPORT, 27, "    file: orders/nope.csv")), indirect=True
)
def test_input_file_missing(lint_case):
    """@prd T-160.5"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/import.yaml:26: test-refs: T-001.2: input.file 'orders/nope.csv' does not exist under contracts/fixtures/",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case", _one(("replace", API, 32, "    errors: [ORDER_MISSING, 7]")), indirect=True
)
def test_expect_errors_unknown_code_and_non_string(lint_case):
    """@prd T-161.1"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_lines_in_this_relative_order": [
                D + "test-cases/api.yaml:27: test-refs: T-002.2: error code ORDER_MISSING is not in contracts/errors.yaml",
                D + "test-cases/api.yaml:27: test-refs: T-002.2: expect.errors item 7 must be an error code string",
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize("lint_case", _one(("replace", NFR, 5, "  environment: prod")), indirect=True)
def test_environment_not_in_table(lint_case):
    """@prd T-161.2"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/nfr.yaml:5: test-refs: T-004.1: environment 'prod' is not in the Environments table of testing.md",
            "stderr": "",
        },
    )


@pytest.mark.parametrize("lint_case", _one(("replace", NFR, 6, "  identity: test-nobody")), indirect=True)
def test_identity_unknown(lint_case):
    """@prd T-161.3"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/nfr.yaml:6: test-refs: T-004.1: identity 'test-nobody' is neither none nor a test identity in contracts/permissions.yaml",
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    _one(
        ("write", "<tmp>/docs/README.md", "# Docs"),
        (
            "replace",
            IMPORT,
            4,
            '  refs: ["contracts/events.md#import_orders", "testing.md#Harness", "contracts/nowhere.md", "../../README.md"]',
        ),
    ),
    indirect=True,
)
def test_refs_file_missing_or_outside(lint_case):
    """@prd T-162.1"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_lines_in_this_relative_order": [
                D
                + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 'contracts/nowhere.md': no file contracts/nowhere.md in the PRD folder",
                D
                + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry '../../README.md': no file ../../README.md in the PRD folder",
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    _one(
        ("write", "contracts/notes.md", T["fenced_notes"]),
        ("replace", IMPORT, 4, '  refs: ["contracts/events.md#export_orders", "contracts/notes.md#Hidden"]'),
    ),
    indirect=True,
)
def test_refs_heading_missing_or_fenced(lint_case):
    """@prd T-162.2"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_lines_in_this_relative_order": [
                D
                + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 'contracts/events.md#export_orders': contracts/events.md has no heading 'export_orders'",
                D
                + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 'contracts/notes.md#Hidden': contracts/notes.md has no heading 'Hidden'",
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case",
    _one(
        ("write", "contracts/notes.md", T["fenced_notes"]),
        (
            "replace",
            IMPORT,
            4,
            '  refs: ["prd.md#7. Contract types", "contracts/notes.md#Shown", "contracts/notes.md#Notes", "nfr.md", "testing.md#"]',
        ),
    ),
    indirect=True,
)
def test_refs_headings_found_at_any_level(lint_case):
    """@prd T-162.3"""
    check(lint_case[0], {"stdout_not_contains": "test-refs: T-001.1: refs entry", "stderr": ""})


@pytest.mark.parametrize(
    "lint_case",
    [
        {
            "setup": [("replace", IMPORT, 4, "  refs: testing.md#Nowhere")],
            "runs": [{"before": None}, {"before": ("replace", IMPORT, 4, '  refs: [7, ""]')}],
        }
    ],
    indirect=True,
)
def test_refs_scalar_and_list_items(lint_case):
    """@prd T-162.4"""
    assert len(lint_case) == 2
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 'testing.md#Nowhere': testing.md has no heading 'Nowhere'",
            "stderr": "",
        },
    )
    check(
        lint_case[1],
        {
            "exit": 1,
            "stdout_lines_in_this_relative_order": [
                D
                + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 7 must be a path in the PRD folder, optionally with #heading",
                D
                + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry '' must be a path in the PRD folder, optionally with #heading",
            ],
            "stderr": "",
        },
    )


@pytest.mark.parametrize(
    "lint_case", _one(("replace", IMPORT, 4, '  refs: ["testing.md#Harness", 7]')), indirect=True
)
def test_refs_entry_not_a_string(lint_case):
    """@prd T-162.5"""
    check(
        lint_case[0],
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 7 must be a path in the PRD folder, optionally with #heading",
            "stderr": "",
        },
    )


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-054")
@pytest.mark.parametrize(
    "lint_case",
    _one(
        ("write", "contracts/notes.md", T["code_span_notes"]),
        ("replace", IMPORT, 4, T["refs_code_span"]),
    ),
    indirect=True,
)
def test_refs_heading_with_code_span_found(lint_case):
    """@prd T-162.6 known-failing E-054"""
    run = lint_case[0]
    # The symptom of E-054: stdout holds this line.
    symptom = (
        D
        + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 'contracts/notes.md#The `orders` table': contracts/notes.md has no heading 'The `orders` table'"
    )
    if contains_line(run.stdout, symptom):
        raise KnownFailure("E-054: " + symptom)
    check(run, {"exit": 0, "stdout": "", "stderr": ""})


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-054")
@pytest.mark.parametrize(
    "lint_case",
    _one(
        ("write", "contracts/notes.md", T["code_span_notes"]),
        ("replace", IMPORT, 4, '  refs: ["contracts/notes.md#Totals"]'),
    ),
    indirect=True,
)
def test_refs_heading_without_its_code_span_not_found(lint_case):
    """@prd T-162.7 known-failing E-054"""
    run = lint_case[0]
    # The symptom of E-054 here: the exit code is 0 and stdout is empty.
    if run.exit == 0 and run.stdout == "":
        raise KnownFailure("E-054: exit 0 and empty stdout")
    check(
        run,
        {
            "exit": 1,
            "stdout_contains_line": D
            + "test-cases/import.yaml:4: test-refs: T-001.1: refs entry 'contracts/notes.md#Totals': contracts/notes.md has no heading 'Totals'",
            "stderr": "",
        },
    )
