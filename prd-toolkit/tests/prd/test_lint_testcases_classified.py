"""The classified-fixtures rule of lint-testcases (test-cases/lint-testcases.yaml, T-166.* to T-168.*)."""

from __future__ import annotations

import pytest

from lint_testcases_support import KnownFailure, check, contains_line, lint_case, texts  # noqa: F401

T = texts()
CSV = "contracts/fixtures/customers/two_customers.csv"
API = "test-cases/api.yaml"


def inline(value: str) -> str:
    return f"docs/prd/orders/test-cases/api.yaml:25: classified-fixtures: T-002.2: inline input holds the real-looking PII value '{value}'; use a synthetic form"


@pytest.mark.parametrize("lint_case", [{"setup": [("replace", CSV, 2, T["csv_real_email"])]}], indirect=True)
def test_csv_fixture_real_email(lint_case):
    """@prd T-166.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/contracts/fixtures/customers/two_customers.csv:2: classified-fixtures: customers.email is classified pii but holds the real-looking value 'jane@gmail.com'",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("write", "contracts/fixtures/customers.csv", T["flat_csv"])]}], indirect=True)
def test_flat_csv_fixture_real_email(lint_case):
    """@prd T-166.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/contracts/fixtures/customers.csv:2: classified-fixtures: customers.email is classified pii but holds the real-looking value 'jane@gmail.com'",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("write", "contracts/fixtures/customers/more.yaml", T["yaml_fixture"]),
        ("write", "contracts/fixtures/customers/more.json", T["json_fixture"]),
    ],
}], indirect=True)
def test_yaml_and_json_fixtures(lint_case):
    """@prd T-166.3"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            "docs/prd/orders/contracts/fixtures/customers/more.json:1: classified-fixtures: customers.email is classified pii but holds the real-looking value 'json@gmail.com'",
            "docs/prd/orders/contracts/fixtures/customers/more.yaml:2: classified-fixtures: customers.email is classified pii but holds the real-looking value 'real@gmail.com'",
            "docs/prd/orders/contracts/fixtures/customers/more.yaml:3: classified-fixtures: customers.name is classified pii but holds the real-looking value 'other@gmail.com'",
        ],
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("replace", "contracts/data-classification.yaml", 5, "    columns: {id: internal, email: pii, name: internal}"),
        ("replace", CSV, 2, T["csv_real_name"]),
        ("write", "contracts/fixtures/customers/broken.yaml", T["broken_yaml"]),
    ],
}], indirect=True)
def test_unclassified_column_and_broken_yaml(lint_case):
    """@prd T-166.4"""
    check(lint_case[0], {"stdout_not_contains": "classified-fixtures:", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [("write", "contracts/fixtures/seed/customers.csv", T["flat_csv"])],
    "runs": [{}, {"before": ("write", "contracts/fixtures/seed/customers/extra.csv", T["flat_csv"])}],
}], indirect=True)
def test_table_from_file_or_folder_name(lint_case):
    """@prd T-166.5"""
    check(lint_case[0], {"exit": 0, "stdout": "", "stderr": ""})
    check(lint_case[1], {
        "exit": 1,
        "stdout_exact_lines": [
            "docs/prd/orders/contracts/fixtures/seed/customers/extra.csv:2: classified-fixtures: customers.email is classified pii but holds the real-looking value 'jane@gmail.com'",
        ],
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("write", "contracts/fixtures/customers/notes.txt", T["flat_csv"])]}], indirect=True)
def test_other_file_types_not_read(lint_case):
    """@prd T-166.6"""
    check(lint_case[0], {"exit": 0, "stdout": "", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_email"])]}], indirect=True)
def test_inline_email(lint_case):
    """@prd T-167.1"""
    check(lint_case[0], {"exit": 1, "stdout_contains_line": inline("bob@acme.io"), "stderr": ""})


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_key"])]}], indirect=True)
def test_inline_key_not_read(lint_case):
    """@prd T-167.2"""
    check(lint_case[0], {"stdout_not_contains": "classified-fixtures:", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_mixed"])]}], indirect=True)
def test_inline_mixed(lint_case):
    """@prd T-168.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [inline("bob@acme.io"), inline("123-45-6789"), inline("312-444-0142")],
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_blind"])]}], indirect=True)
def test_inline_phone_inside_email(lint_case):
    """@prd T-168.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": inline("3124440142@acme.io"),
        "stdout_not_contains": "PII value '3124440142'",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_runs"])]}], indirect=True)
def test_inline_digit_runs(lint_case):
    """@prd T-168.3"""
    check(lint_case[0], {"stdout_not_contains": "classified-fixtures:", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_emails"])]}], indirect=True)
def test_inline_synthetic_emails(lint_case):
    """@prd T-168.4"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": inline("g@example.co"),
        "stdout_not_contains": ["'a@example.com'", "'b@EXAMPLE.org'", "'c@mail.test'", "'d@x.example'", "'e@y.invalid'"],
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_ssns"])]}], indirect=True)
def test_inline_synthetic_ssns(lint_case):
    """@prd T-168.5"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": inline("123-45-6789"),
        "stdout_not_contains": ["'000-12-3456'", "'666-12-3456'", "'900-12-3456'"],
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_phones"])]}], indirect=True)
def test_inline_synthetic_phones(lint_case):
    """@prd T-168.6"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [inline("312-555-0242"), inline("312-555-0200")],
        "stdout_not_contains": ["'(312) 555-0142'", "'312.555.0199'", "'312 555 0100'"],
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{"setup": [("insert_after", API, 26, T["inline_subdomains"])]}], indirect=True)
def test_inline_subdomains_of_example(lint_case):
    """@prd T-168.7"""
    run = lint_case[0]
    if contains_line(run.stdout, inline("a@mail.example.com")):
        raise KnownFailure("stdout also holds the 'a@mail.example.com' finding (E-057)")
    check(run, {"exit": 1, "stdout_exact_lines": [inline("d@notexample.com")], "stderr": ""})
