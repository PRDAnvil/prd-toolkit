"""lint-contracts: contracts-valid on contracts/openapi.yaml (FR-170, FR-171)."""
from lint_contracts_support import (
    S0,
    assert_contains,
    assert_contains_line,
    assert_lines_in_relative_order,
    assert_not_contains,
    run_lint,
)

OA = "contracts/openapi.yaml"
F = "docs/prd/orders/contracts/openapi.yaml"
SIX = " " * 6


def test_validator_failure_still_checks_fields(tmp_path, monkeypatch):
    """@prd T-170.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace(OA, 1, "openapi: 9.9.9")
    p.replace(OA, 25, SIX + "x-effect: []")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains(r.stdout, f"{F}:1: contracts-valid: openapi validation failed: ")
    assert_contains_line(
        r.stdout, f"{F}:19: contracts-valid: GET /orders/{{id}}: x-effects must be a list (use [] for none)"
    )
    assert r.stderr == ""


def test_webhooks_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-170.2"""
    p = S0(tmp_path, monkeypatch)
    p.append(OA, "webhooks: [x]")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{F}:74: contracts-valid: webhooks must be a mapping")
    assert r.stderr == ""


def test_webhook_value_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-170.3"""
    p = S0(tmp_path, monkeypatch)
    p.append(OA, "webhooks: {orderShipped: 3}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{F}:74: contracts-valid: orderShipped: must be a mapping")
    assert r.stderr == ""


def test_operation_not_a_mapping_null_skipped(tmp_path, monkeypatch):
    """@prd T-170.4"""
    p = S0(tmp_path, monkeypatch)
    p.append(OA, "webhooks: {orderShipped: {post: 3, get: null}}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{F}:74: contracts-valid: POST orderShipped: operation must be a mapping"
    )
    assert_not_contains(r.stdout, "GET orderShipped")
    assert r.stderr == ""


def test_missing_operation_id(tmp_path, monkeypatch):
    """@prd T-170.5"""
    p = S0(tmp_path, monkeypatch)
    p.replace(OA, 19, SIX + "operationId: 3")
    p.replace(OA, 40, SIX + 'operationId: ""')
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:18: contracts-valid: GET /orders/{{id}}: missing operationId",
            f"{F}:39: contracts-valid: DELETE /orders/{{id}}: missing operationId",
        ],
    )
    assert r.stderr == ""


def test_x_prd_ids_not_a_non_empty_list(tmp_path, monkeypatch):
    """@prd T-170.6"""
    p = S0(tmp_path, monkeypatch)
    p.replace(OA, 22, SIX + "x-prd: [FR-002]")
    p.replace(OA, 43, SIX + "x-prd-ids: []")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:19: contracts-valid: GET /orders/{{id}}: x-prd-ids must be a non-empty list",
            f"{F}:43: contracts-valid: DELETE /orders/{{id}}: x-prd-ids must be a non-empty list",
        ],
    )
    assert r.stderr == ""


def test_x_prd_ids_undefined_items(tmp_path, monkeypatch):
    """@prd T-170.7"""
    p = S0(tmp_path, monkeypatch)
    p.replace(OA, 43, SIX + "x-prd-ids: [FR-003, AC-003.1, AC-003.9, T-002.1]")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:43: contracts-valid: DELETE /orders/{{id}}: x-prd-ids item 'AC-003.9' is not a defined requirement or AC id",
            f"{F}:43: contracts-valid: DELETE /orders/{{id}}: x-prd-ids item 'T-002.1' is not a defined requirement or AC id",
        ],
    )
    assert r.stderr == ""


def test_x_lists_absent_or_not_a_list(tmp_path, monkeypatch):
    """@prd T-170.8"""
    p = S0(tmp_path, monkeypatch)
    p.replace(OA, 23, SIX + "x-error-codes: ORDER_NOT_FOUND")
    p.replace(OA, 25, SIX + "x-effect: []")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:19: contracts-valid: GET /orders/{{id}}: x-effects must be a list (use [] for none)",
            f"{F}:23: contracts-valid: GET /orders/{{id}}: x-error-codes must be a list (use [] for none)",
        ],
    )
    assert r.stderr == ""


_HEAD = "operationId: {n}, x-prd-ids: [FR-002], x-error-codes: [], x-preconditions: [], x-effects: []"


def test_responses_absent(tmp_path, monkeypatch):
    """@prd T-171.1"""
    p = S0(tmp_path, monkeypatch)
    p.append(OA, "webhooks: {orderShipped: {post: {" + _HEAD.format(n="orderShipped") + "}}}")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{F}:74: contracts-valid: POST orderShipped: responses must be a mapping"
    )
    assert r.stderr == ""


def test_response_not_a_mapping(tmp_path, monkeypatch):
    """@prd T-171.2"""
    p = S0(tmp_path, monkeypatch)
    p.append(
        OA,
        "webhooks: {orderShipped: {post: {"
        + _HEAD.format(n="orderShipped")
        + ', responses: {"200": 5}}}}',
    )
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{F}:74: contracts-valid: POST orderShipped: response 200 must be a mapping"
    )
    assert r.stderr == ""


def test_response_without_content_example(tmp_path, monkeypatch):
    """@prd T-171.3"""
    p = S0(tmp_path, monkeypatch)
    p.delete(OA, 32)
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(
        r.stdout, f"{F}:27: contracts-valid: GET /orders/{{id}}: response 200 has no content example"
    )
    assert r.stderr == ""


def test_response_204_string_or_number_not_checked(tmp_path, monkeypatch):
    """@prd T-171.4"""
    p = S0(tmp_path, monkeypatch)
    p.append(
        OA,
        "webhooks: {shipped: {post: {"
        + _HEAD.format(n="shipped")
        + ', responses: {"204": 5}}}, cancelled: {post: {'
        + _HEAD.format(n="cancelled")
        + ", responses: {204: 5}}}}",
    )
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, ["response 204", "responses must be a mapping"])
    assert r.stderr == ""


def test_examples_and_ref_count(tmp_path, monkeypatch):
    """@prd T-171.5"""
    p = S0(tmp_path, monkeypatch)
    p.replace(
        OA,
        32,
        " " * 14 + "examples: {one: {value: {id: 1, order_key: K-1000, customer_id: 1, status: open}}}",
    )
    p.append(
        OA,
        "webhooks: {orderShipped: {post: {"
        + _HEAD.format(n="orderShipped")
        + ', responses: {"400": {$ref: "#/components/responses/Bad"}}}}}',
    )
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, ["has no content example", "response 400 must be a mapping"])
    assert r.stderr == ""
