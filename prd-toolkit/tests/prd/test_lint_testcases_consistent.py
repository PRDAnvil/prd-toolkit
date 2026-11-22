"""lint-testcases, FR-150: each Tests line tied to its test-cases file (test-cases/lint-testcases.yaml)."""

import pytest

from lint_testcases_support import KnownFailure, check, count_of_line, lint_case, texts  # noqa: F401

NO_FILE_LINE = (
    "docs/prd/orders/nfr.md:8: test-cases-consistent: the Tests line of NFR-004 names no test-cases file; "
    "end it with (test-cases/<area>.yaml)"
)


def case(**spec):
    return pytest.mark.parametrize("lint_case", [spec], indirect=True)


@case(setup=[("replace", "nfr.md", 8, "Tests: T-004.1 [system]")])
def test_tests_line_naming_no_file(lint_case):
    """@prd T-150.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            NO_FILE_LINE,
            "docs/prd/orders/test-cases/nfr.yaml:1: test-cases-consistent: T-004.1 is cited by no Tests line naming test-cases/nfr.yaml",
        ],
        "stderr": "",
    })


@case(setup=[("replace", "features/api.md", 31,
              "Tests: T-003.1 [integration], T-003.2 [integration]  (test-cases/orders.yaml)")])
def test_named_file_does_not_exist(lint_case):
    """@prd T-150.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            "docs/prd/orders/features/api.md:31: test-cases-consistent: T-003.1: the named file test-cases/orders.yaml does not exist",
            "docs/prd/orders/features/api.md:31: test-cases-consistent: T-003.2: the named file test-cases/orders.yaml does not exist",
        ],
        "stderr": "",
    })


@case(setup=[("replace", "features/api.md", 18,
              "Tests: T-002.1 [integration], T-002.2 [integration], T-002.9 [unit]  (test-cases/api.yaml)")])
def test_t_id_with_no_entry(lint_case):
    """@prd T-150.3"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/features/api.md:18: test-cases-consistent: T-002.9 has no entry in test-cases/api.yaml",
        "stderr": "",
    })


@case(setup=[("replace", "features/api.md", 18, "Tests: T-002.1 [unit], T-002.2 [integration]  (test-cases/api.yaml)")])
def test_level_disagrees(lint_case):
    """@prd T-150.4"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/features/api.md:18: test-cases-consistent: T-002.1 is [unit] on the Tests line but level: integration in test-cases/api.yaml:3",
        "stderr": "",
    })


@case(setup=[("append", "test-cases/import.yaml", texts()["uncited_case"])])
def test_case_cited_by_no_tests_line(lint_case):
    """@prd T-150.5"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:72: test-cases-consistent: T-001.9 is cited by no Tests line naming test-cases/import.yaml",
        "stderr": "",
    })


@case(setup=[("replace", "test-cases/api.yaml", 3, "  level: 3")])
def test_non_string_level_is_not_compared(lint_case):
    """@prd T-150.6"""
    check(lint_case[0], {"stdout_not_contains": "T-002.1 is [integration] on the Tests line", "stderr": ""})


@case(setup=[("replace", "nfr.md", 8, "Tests: T-004.1 [system], T-004.2 [smoke]")])
def test_no_file_finding_once_per_line(lint_case):
    """@prd T-150.7"""
    run = lint_case[0]
    check(run, {"exit": 1, "stderr": ""})
    # symptom: stdout holds that line twice, once for each T-id of the Tests line
    if count_of_line(run.stdout, NO_FILE_LINE) == 2:
        raise KnownFailure("the no-file finding is printed once for each of the two T-ids")
    check(run, {"stdout_count_of_line": {"line": NO_FILE_LINE, "count": 1}})
