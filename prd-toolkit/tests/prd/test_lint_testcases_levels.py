"""lint-testcases, FR-151 to FR-153: the Levels table, its Gate column and each case's level
(test-cases/lint-testcases.yaml)."""

import pytest

from lint_testcases_support import check, lint_case  # noqa: F401  (lint_case is a fixture)

T = "testing.md"
NO_GATE = "docs/prd/orders/testing.md:5: test-level: testing.md Levels: add a Gate column (build or deploy), new in prd-toolkit 0.4"


def collect(row: int, build: str, deploy: str, path: str) -> str:
    return (
        f"docs/prd/orders/testing.md:{row}: test-level: level '{build}' (Gate build) would collect "
        f"level '{deploy}' (Gate deploy) tests: {path}"
    )


def case(**spec):
    return pytest.mark.parametrize("lint_case", [spec], indirect=True)


def before(n, line):
    return {"before": ("replace", T, n, line)}


# FR-151


@case(setup=[("replace", T, 5, "| Level | Harness command | Environment | Stage |")])
def test_levels_table_without_gate_column(lint_case):
    """@prd T-151.1"""
    check(lint_case[0], {"exit": 1, "stdout_count_of_line": {"line": NO_GATE, "count": 1}, "stderr": ""})


@case(setup=[("replace", T, 9, "| component | `pytest tests/component` | ci | `nightly` |")])
def test_gate_value_not_build_or_deploy(lint_case):
    """@prd T-151.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/testing.md:9: test-level: level 'component': Gate 'nightly' is not one of build, deploy",
        "stderr": "",
    })


@case(setup=[
    ("replace", T, 5, "| Level | Harness command | Environment | Stage |"),
    ("replace", T, 7, "| unit | `pytest tests` | local | build |"),
    ("replace", T, 9, "| component | `pytest tests/component` | ci | nightly |"),
])
def test_no_gate_column_suppresses_gate_and_overlap(lint_case):
    """@prd T-151.3"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": NO_GATE,
        "stdout_not_contains": ["(Gate build) would collect", "is not one of build, deploy"],
        "stderr": "",
    })


@case(setup=[("replace", T, 3, "## Stages")])
def test_no_levels_table(lint_case):
    """@prd T-151.4"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/api.yaml:3: test-level: T-002.1: level 'integration' is not a row of the Levels table in testing.md",
        "stdout_not_contains": ["test-level: testing.md Levels", "(Gate build) would collect", "is not one of build, deploy"],
        "stderr": "",
    })


# FR-152


@case(setup=[("replace", T, 7, "| unit | `pytest tests` | local | build |")])
def test_build_command_collects_deploy_paths(lint_case):
    """@prd T-152.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            collect(7, "unit", "system", "tests/system"),
            collect(7, "unit", "e2e", "tests/e2e"),
            collect(7, "unit", "smoke", "tests/smoke"),
        ],
        "stdout_not_contains": "level 'acceptance' (Gate deploy)",
        "stderr": "",
    })


@case(
    setup=[("replace", T, 8,
            "| integration | `TEST_ENV=ci python -m pytest -q -n auto --basetemp build/tmp ./tests/` | ci | build |")],
    runs=[
        {},
        before(8, "| integration | `uv run pytest .` | ci | build |"),
        before(8, "| integration | `pytest tests/unit/test_a.py tests` | ci | build |"),
    ],
)
def test_path_word_is_found(lint_case):
    """@prd T-152.2"""
    want = {"exit": 1, "stdout_contains_line": collect(8, "integration", "system", "tests/system"), "stderr": ""}
    for run in lint_case:
        check(run, want)


@case(runs=[
    before(7, "| unit | `bash tools/gate.sh unit` | local | build |"),
    before(7, "| unit | `pytest tests/systematic` | local | build |"),
    before(7, "| unit | `cd tools && pytest unit` | local | build |"),
])
def test_words_that_are_no_overlapping_path(lint_case):
    """@prd T-152.3"""
    for run in lint_case:
        check(run, {"stdout_not_contains": "level 'unit' (Gate build) would collect", "stderr": ""})


@case(runs=[
    before(7, "| unit | `pytest --ignore tests/system tests` | local | build |"),
    before(7, "| unit | `pytest tests --ignore-glob 'tests/[se]*'` | local | build |"),
    before(7, "| unit | `pytest --ignore=tests tests` | local | build |"),
    before(7, "| unit | `pytest --deselect tests/system/test_a.py tests` | local | build |"),
])
def test_excluded_deploy_paths(lint_case):
    """@prd T-152.4"""
    run_1, run_2, run_3, run_4 = lint_case
    check(run_1, {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            collect(7, "unit", "e2e", "tests/e2e"),
            collect(7, "unit", "smoke", "tests/smoke"),
        ],
        "stdout_not_contains": "would collect level 'system'",
        "stderr": "",
    })
    check(run_2, {"stdout_not_contains": "level 'unit' (Gate build) would collect", "stderr": ""})
    check(run_3, {"stdout_not_contains": "level 'unit' (Gate build) would collect", "stderr": ""})
    check(run_4, {"exit": 1, "stdout_contains_line": collect(7, "unit", "system", "tests/system"), "stderr": ""})


@case(runs=[
    before(7, '| unit | `pytest -m "not system" tests` | local | build |'),
    before(7, "| unit | `pytest -k=quick tests` | local | build |"),
    before(7, "| unit | `python -m pytest tests` | local | build |"),
])
def test_selection_by_expression(lint_case):
    """@prd T-152.5"""
    run_1, run_2, run_3 = lint_case
    check(run_1, {"stdout_not_contains": "level 'unit' (Gate build) would collect", "stderr": ""})
    check(run_2, {"stdout_not_contains": "level 'unit' (Gate build) would collect", "stderr": ""})
    check(run_3, {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            collect(7, "unit", "system", "tests/system"),
            collect(7, "unit", "e2e", "tests/e2e"),
            collect(7, "unit", "smoke", "tests/smoke"),
        ],
        "stderr": "",
    })


@case(setup=[
    ("replace", T, 7, "| unit | `pytest tests` | local | build |"),
    ("replace", T, 10, "| system | none | staging | deploy |"),
])
def test_level_without_harness_command(lint_case):
    """@prd T-152.6"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            collect(7, "unit", "e2e", "tests/e2e"),
            collect(7, "unit", "smoke", "tests/smoke"),
        ],
        "stdout_not_contains": "would collect level 'system'",
        "stderr": "",
    })


# FR-153


@case(setup=[("delete", "test-cases/import.yaml", 38)])
def test_case_with_no_level(lint_case):
    """@prd T-153.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:36: test-level: T-001.3 has no level",
        "stderr": "",
    })


@case(setup=[("replace", "test-cases/import.yaml", 38, "  level: nightly")])
def test_level_not_a_levels_row(lint_case):
    """@prd T-153.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:38: test-level: T-001.3: level 'nightly' is not a row of the Levels table in testing.md",
        "stderr": "",
    })
