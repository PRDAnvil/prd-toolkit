"""lint-testcases, FR-154 and FR-155: a case's sufficiency elements (test-cases/lint-testcases.yaml)."""

import pytest

from lint_testcases_support import check, lint_case  # noqa: F401  (lint_case is a fixture)

IMP = "test-cases/import.yaml"
AT = "docs/prd/orders/test-cases/import.yaml"
KINDS = "(known: code, component, event, job, lookml, op, page, table)"


def case(**spec):
    return pytest.mark.parametrize("lint_case", [spec], indirect=True)


def suff(line: int, msg: str) -> str:
    return f"{AT}:{line}: sufficiency: T-001.3: {msg}"


# FR-154


@case(setup=[("delete", IMP, 37), ("delete", IMP, 40), ("delete", IMP, 41)])
def test_missing_scalar_keys(lint_case):
    """@prd T-154.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            suff(36, "ac is missing"),
            suff(36, "environment is missing"),
            suff(36, "identity is missing"),
        ],
        "stderr": "",
    })


@case(setup=[("replace", IMP, 40, "  environment: 3"), ("replace", IMP, 41, "  identity: []")])
def test_non_string_scalar_keys(lint_case):
    """@prd T-154.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            suff(36, "environment is missing"),
            suff(36, "identity is missing"),
        ],
        "stderr": "",
    })


@case(setup=[("delete", IMP, 39)],
      runs=[{}, {"before": ("insert_after", IMP, 38, "  target: 5")}])
def test_missing_or_non_string_target(lint_case):
    """@prd T-154.3"""
    for run in lint_case:
        check(run, {"exit": 1, "stdout_contains_line": suff(36, "target is missing"), "stderr": ""})


@case(setup=[("replace", IMP, 39, "  target: importer")],
      runs=[{}, {"before": ("replace", IMP, 39, '  target: "code:"')}])
def test_target_not_kind_colon_name(lint_case):
    """@prd T-154.4"""
    run_1, run_2 = lint_case
    check(run_1, {"exit": 1, "stdout_contains_line": suff(39, "target 'importer' must be <kind>:<name>"), "stderr": ""})
    check(run_2, {"exit": 1, "stdout_contains_line": suff(39, "target 'code:' must be <kind>:<name>"), "stderr": ""})


@case(setup=[("replace", IMP, 39, "  target: widget:importer")],
      runs=[
          {},
          {"before": ("replace", IMP, 39, "  target: openapi:orders")},
          {"before": ("replace", IMP, 39, "  target: lookml:orders_explore")},
      ])
def test_unknown_target_kind(lint_case):
    """@prd T-154.5"""
    run_1, run_2, run_3 = lint_case
    check(run_1, {"exit": 1, "stdout_contains_line": suff(39, f"target kind 'widget' is unknown {KINDS}"), "stderr": ""})
    check(run_2, {"exit": 1, "stdout_contains_line": suff(39, f"target kind 'openapi' is unknown {KINDS}"), "stderr": ""})
    check(run_3, {"stdout_not_contains": "sufficiency: T-001.3: target kind", "stderr": ""})


@case(setup=[
    ("insert_after", "prd.md", 19, "- Pack: document 1.0.0 (prd-toolkit)"),
    ("replace", IMP, 39, "  target: doc:install-guide"),
])
def test_pack_target_kind_is_known(lint_case):
    """@prd T-154.6"""
    check(lint_case[0], {"stdout_not_contains": "sufficiency: T-001.3: target kind", "stderr": ""})


@case(setup=[
    ("replace", "test-cases/nfr.yaml", 1, "T-004.1: oops"),
    ("insert_after", "test-cases/nfr.yaml", 1, "T-004.9:"),
])
def test_case_that_is_not_a_mapping(lint_case):
    """@prd T-154.7"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/nfr.yaml:1: sufficiency: T-004.1: a test case must be a mapping",
        "stdout_not_contains": [
            "sufficiency: T-004.1: ac is missing",
            "test-level: T-004.1 has no level",
            "test-refs: T-004.1",
            "ac-has-test:",
        ],
        "stderr": "",
    })


# FR-155


@case(setup=[("replace", IMP, 42, "  preconditions: none")],
      runs=[{}, {"before": ("delete", IMP, 42)}])
def test_preconditions_must_be_a_list(lint_case):
    """@prd T-155.1"""
    msg = "preconditions must be a list (use [] for none)"
    run_1, run_2 = lint_case
    check(run_1, {"exit": 1, "stdout_contains_line": suff(42, msg), "stderr": ""})
    check(run_2, {"exit": 1, "stdout_contains_line": suff(36, msg), "stderr": ""})


@case(setup=[("replace", IMP, 43, "  input: {}"), ("delete", IMP, 44)],
      runs=[
          {},
          {"before": ("replace", IMP, 43, "  input: ~")},
          {"before": ("delete", IMP, 43)},
      ])
def test_input_missing_or_empty(lint_case):
    """@prd T-155.2"""
    msg = "input is missing or empty"
    run_1, run_2, run_3 = lint_case
    check(run_1, {"exit": 1, "stdout_contains_line": suff(43, msg), "stderr": ""})
    check(run_2, {"exit": 1, "stdout_contains_line": suff(43, msg), "stderr": ""})
    check(run_3, {"exit": 1, "stdout_contains_line": suff(36, msg), "stderr": ""})


EXPECT_FINDINGS = [
    "expect is missing",
    "expect.output is missing",
    "expect.effects must be a list (use [] for none)",
    "expect.errors must be a list (use [] for none)",
    "expect.leaks is missing (use 'none')",
]


@case(setup=[("delete_range", IMP, 45, 51)])
def test_expect_absent(lint_case):
    """@prd T-155.3"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [suff(36, m) for m in EXPECT_FINDINGS],
        "stderr": "",
    })


@case(setup=[("replace", IMP, 46, "    output: {}")],
      runs=[{}, {"before": ("delete", IMP, 46)}])
def test_expect_output_missing(lint_case):
    """@prd T-155.4"""
    run_1, run_2 = lint_case
    check(run_1, {"exit": 1, "stdout_contains_line": suff(46, "expect.output is missing"), "stderr": ""})
    check(run_2, {"exit": 1, "stdout_contains_line": suff(45, "expect.output is missing"), "stderr": ""})


@case(setup=[("replace", IMP, 50, "    errors: IMPORT_EMPTY"), ("delete_range", IMP, 47, 49)])
def test_effects_and_errors_must_be_lists(lint_case):
    """@prd T-155.5"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [
            suff(45, "expect.effects must be a list (use [] for none)"),
            suff(47, "expect.errors must be a list (use [] for none)"),
        ],
        "stderr": "",
    })


@case(setup=[("delete", IMP, 51)])
def test_leaks_missing(lint_case):
    """@prd T-155.6"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": suff(45, "expect.leaks is missing (use 'none')"),
        "stderr": "",
    })


@case(setup=[("replace", IMP, 45, "  expect: oops"), ("delete_range", IMP, 46, 51)])
def test_expect_not_a_mapping(lint_case):
    """@prd T-155.7"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_lines_in_this_relative_order": [suff(45, m) for m in EXPECT_FINDINGS],
        "stderr": "",
    })
