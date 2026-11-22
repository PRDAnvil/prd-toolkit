"""lint-contracts: contracts-valid on contracts/events.md (FR-173)."""
import pytest

from lint_contracts_support import (
    S0,
    KnownFailure,
    assert_contains_line,
    assert_exact_lines,
    assert_lines_in_relative_order,
    assert_not_contains,
    run_lint,
)

EV = "contracts/events.md"
F = "docs/prd/orders/contracts/events.md"
FENCE = "```"


def test_missing_retries_line(tmp_path, monkeypatch):
    """@prd T-173.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace(EV, 7, "Retried: 3 attempts, 30 s apart")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_contains_line(r.stdout, f"{F}:3: contracts-valid: event 'import_orders' has no Retries: line")
    assert r.stderr == ""


def test_each_missing_field_in_order(tmp_path, monkeypatch):
    """@prd T-173.2"""
    p = S0(tmp_path, monkeypatch)
    p.append(EV, "### `order_shipped`")
    p.append(EV, "Trigger: a shipment is booked")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:9: contracts-valid: event 'order_shipped' has no Payload: line",
            f"{F}:9: contracts-valid: event 'order_shipped' has no Delivery: line",
            f"{F}:9: contracts-valid: event 'order_shipped' has no Retries: line",
            f"{F}:9: contracts-valid: event 'order_shipped' has no Failure: line",
        ],
    )
    assert_not_contains(r.stdout, "has no Trigger: line")
    assert r.stderr == ""


def test_level_two_heading_ends_section(tmp_path, monkeypatch):
    """@prd T-173.3"""
    p = S0(tmp_path, monkeypatch)
    p.insert_after(EV, 6, "## Notes")
    r = run_lint(tmp_path)
    assert r.returncode == 1
    assert_lines_in_relative_order(
        r.stdout,
        [
            f"{F}:3: contracts-valid: event 'import_orders' has no Retries: line",
            f"{F}:3: contracts-valid: event 'import_orders' has no Failure: line",
        ],
    )
    assert_not_contains(r.stdout, "has no Delivery: line")
    assert r.stderr == ""


def test_fenced_heading_is_no_event(tmp_path, monkeypatch):
    """@prd T-173.4"""
    p = S0(tmp_path, monkeypatch)
    p.append(EV, FENCE)
    p.append(EV, "### fenced_event")
    p.append(EV, FENCE)
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "event 'fenced_event'")
    assert r.stderr == ""


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_fenced_field_line_counts_for_no_event(tmp_path, monkeypatch):
    """@prd T-173.5 known-failing E-060"""
    p = S0(tmp_path, monkeypatch)
    for line in [
        "### fenced_trigger",
        FENCE,
        "Trigger: a file arrives.",
        FENCE,
        "Payload: one row.",
        "Delivery: at least once.",
        "Retries: none.",
        "Failure: the owner is paged.",
    ]:
        p.append(EV, line)
    r = run_lint(tmp_path)
    if r.returncode == 0 and r.stdout == "":
        raise KnownFailure("E-060: the exit code is 0 and stdout is empty")
    assert r.returncode == 1
    assert_exact_lines(
        r.stdout, [f"{F}:9: contracts-valid: event 'fenced_trigger' has no Trigger: line"]
    )
    assert r.stderr == ""
