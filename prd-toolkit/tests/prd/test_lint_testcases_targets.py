"""The target references of lint-testcases (test-cases/lint-testcases.yaml, T-164.*)."""

from __future__ import annotations

import pytest

from lint_testcases_support import check, lint_case, texts  # noqa: F401  (lint_case is a fixture)

T = texts()
IMPORT = "test-cases/import.yaml"
NFR = "test-cases/nfr.yaml"
PACK_LINE = "- Pack: document 1.0.0 (prd-toolkit)"


@pytest.mark.parametrize("lint_case", [{"setup": [("replace", NFR, 4, "  target: op:getOrdr")]}], indirect=True)
def test_target_op_unknown_operation(lint_case):
    """@prd T-164.1"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/nfr.yaml:4: test-refs: T-004.1: target op:getOrdr: no operationId 'getOrdr' in contracts/openapi.yaml",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{
    "setup": [("replace", IMPORT, 39, "  target: table:order")],
    "runs": [{}, {"before": ("replace", IMPORT, 39, "  target: table:ORDERS")}],
}], indirect=True)
def test_target_table(lint_case):
    """@prd T-164.2"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: target table:order: no table 'order' in contracts/schema.sql",
        "stderr": "",
    })
    check(lint_case[1], {"stdout_not_contains": "test-refs: T-001.3: target table:", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [("replace", IMPORT, 22, "  target: job:import_order")],
    "runs": [{}, {"before": ("replace", IMPORT, 22, "  target: event:import_orders")}],
}], indirect=True)
def test_target_job_and_event(lint_case):
    """@prd T-164.3"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:22: test-refs: T-001.2: target job:import_order: no '### import_order' heading in contracts/events.md and no such asyncapi channel or operation",
        "stderr": "",
    })
    check(lint_case[1], {"stdout_not_contains": "test-refs: T-001.2: target", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("insert_after", "prd.md", 19, PACK_LINE),
        ("replace", IMPORT, 39, "  target: doc:install-guide"),
    ],
}], indirect=True)
def test_target_pack_type_without_row(lint_case):
    """@prd T-164.4"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: target doc:install-guide: contract type outline has no §7 row (Validator pack)",
        "stderr": "",
    })


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("insert_after", "prd.md", 19, PACK_LINE),
        ("insert_after", "prd.md", 80, T["outline_row"]),
        ("write", "contracts/outline.yaml", T["outline_yaml"]),
        ("replace", IMPORT, 39, "  target: doc:upgrade-guide"),
    ],
    "runs": [{}, {"before": ("replace", IMPORT, 39, "  target: doc:install-guide")}],
}], indirect=True)
def test_target_pack_type_outline_entry(lint_case):
    """@prd T-164.5"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: target doc:upgrade-guide: no outline entry 'upgrade-guide'",
        "stderr": "",
    })
    check(lint_case[1], {"stdout_not_contains": "test-refs: T-001.3: target doc:", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("insert_after", "prd.md", 80, T["looker_row"]),
        ("write", "contracts/looker/kpi.yaml", ["orders_summary: {kind: explore}"]),
        ("write", "contracts/looker/more.yaml", ["returns_summary: {kind: explore}"]),
        ("replace", IMPORT, 39, "  target: looker:no_such_explore"),
    ],
    "runs": [{}, {"before": ("replace", IMPORT, 39, "  target: looker:returns_summary")}],
}], indirect=True)
def test_target_custom_type_items(lint_case):
    """@prd T-164.6"""
    check(lint_case[0], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/import.yaml:39: test-refs: T-001.3: target looker:no_such_explore: 'no_such_explore' is not an item of the looker files (items: orders_summary, returns_summary)",
        "stderr": "",
    })
    check(lint_case[1], {"stdout_not_contains": "test-refs: T-001.3: target looker:", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [],
    "runs": [
        {"before": ("replace", IMPORT, 39, "  target: lookml:anything")},
        {"before": ("replace", IMPORT, 39, "  target: component:Anything")},
        {"before": ("replace", IMPORT, 39, "  target: code:whatever.at_all")},
    ],
}], indirect=True)
def test_target_kinds_not_resolved(lint_case):
    """@prd T-164.7"""
    for run in lint_case:
        check(run, {"stdout_not_contains": "test-refs: T-001.3", "stderr": ""})


@pytest.mark.parametrize("lint_case", [{
    "setup": [
        ("write", "links.md", ["# Links"]),
        ("replace", NFR, 4, "  target: widget:greet/getOrder"),
    ],
    "runs": [{}, {"before": ("delete_file", "links.md")}],
}], indirect=True)
def test_target_link_file(lint_case):
    """@prd T-164.8"""
    check(lint_case[0], {"stdout_not_contains": ["sufficiency: T-004.1", "test-refs: T-004.1"], "stderr": ""})
    check(lint_case[1], {
        "exit": 1,
        "stdout_contains_line": "docs/prd/orders/test-cases/nfr.yaml:4: sufficiency: T-004.1: target kind 'widget' is unknown (known: code, component, event, job, lookml, op, page, table)",
        "stderr": "",
    })
