"""Trace: uncited T-ids, statuses that claim a test, and known-failing tags (FR-084 to FR-086; test-cases/trace.yaml)."""
from __future__ import annotations

from pathlib import Path

from trace_support import (  # noqa: F401  (scratch is a fixture)
    AT_PRD, assert_exact_lines, cite, given_steps, replace_line, run_trace, scratch,
)

ADD = "add `" + AT_PRD + " T-001.1` to the test that proves it"
T_IMPLEMENTED = "docs/prd/orders/features/import.md:8: t-implemented: T-001.1 (FR-001) is cited by no test; " + ADD


def _status_current(status: str) -> str:
    return f"docs/prd/orders/features/import.md:8: status-current: FR-001 is {status} but T-001.1 has no citing test"


# -- FR-084 --

@given_steps("N0E", "TU", "TS:as-built")
def test_t084_1_as_built_uncited(scratch):
    """@prd T-084.1"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (1, T_IMPLEMENTED + "\n", "")


@given_steps("N0E", "TU", "TS:as-built", "TL:smoke")
def test_t084_2_level_without_levels_row(scratch):
    """@prd T-084.2"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (1, T_IMPLEMENTED + "\n", "")


@given_steps("N0E", "TU", "TD", "TS:live (since 1.0.0)", "TL:system")
def test_t084_3_live_any_level(scratch):
    """@prd T-084.3"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [_status_current("live"), T_IMPLEMENTED])
    assert r.stderr == ""


@given_steps("N0E", "TU", "TS:approved")
def test_t084_4_approved_not_reported(scratch):
    """@prd T-084.4"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


@given_steps("N0E", "TU", "TD", "TL:system")
def test_t084_5_deploy_gate_not_reported(scratch):
    """@prd T-084.5"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


@given_steps("N0E", "TU", "TA:extracted")
def test_t084_6_area_not_adopted(scratch):
    """@prd T-084.6"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


@given_steps("N0E", "TU", "TS:as-built", "TA:adopted")
def test_t084_7_area_adopted(scratch):
    """@prd T-084.7"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (1, T_IMPLEMENTED + "\n", "")


# -- FR-085 --

@given_steps("N0E", "TU")
def test_t085_1_verified_status_current(scratch):
    """@prd T-085.1"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [_status_current("verified"), T_IMPLEMENTED])
    assert r.stderr == ""


@given_steps("N0E", "TU", "TS:built", "TL:unit")
def test_t085_2_built_unit_status_current(scratch):
    """@prd T-085.2"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [_status_current("built"), T_IMPLEMENTED])
    assert r.stderr == ""


@given_steps("N0E", "TU", "TS:built")
def test_t085_3_built_integration_no_status_current(scratch):
    """@prd T-085.3"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (1, T_IMPLEMENTED + "\n", "")


@given_steps("N0E", "TU", "TS:as-built", "TL:unit")
def test_t085_4_as_built_no_status_current(scratch):
    """@prd T-085.4"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert "status-current" not in r.stdout, r.stdout
    assert r.stdout.splitlines().count(T_IMPLEMENTED) == 1, r.stdout
    assert r.stderr == ""


# -- FR-086 --

@given_steps("N0E", "TE", "TK:E-001")
def test_t086_1_known_failing_case_without_tag(scratch):
    """@prd T-086.1"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (
        1,
        "docs/prd/orders/test-cases/import.yaml:1: known-failing-tags: T-001.1 is known-failing on E-001 "
        "but no citation is tagged `known-failing E-001`\n",
        "",
    )


def _tag(text: str):
    def step(tmp: Path) -> None:
        replace_line(tmp / "tests/test_orders.py", 2, cite("T-001.1", text))
    step.__name__ = "tag" + text.replace(" ", "_").replace(":", "")
    step.__doc__ = f"in <tmp>/tests/test_orders.py line 2 becomes the comment citing T-001.1, then {text!r}"
    return step


@given_steps("N0E", "TE", "TK:E-001", _tag("  known-failing: E-001"))
def test_t086_2_tag_with_colon_matches(scratch):
    """@prd T-086.2"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


@given_steps("N0E", "TE", _tag(" known-failing E-001"))
def test_t086_3_tag_on_case_not_known_failing(scratch):
    """@prd T-086.3"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (
        1,
        "tests/test_orders.py:2: known-failing-tags: tags T-001.1 known-failing E-001, "
        "but its test case is not known-failing on E-001\n",
        "",
    )


@given_steps("N0E", "TE", "TK:E-002", _tag(" known-failing E-002"))
def test_t086_4_tag_of_resolved_entry(scratch):
    """@prd T-086.4"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (
        1, "tests/test_orders.py:2: known-failing-tags: tags T-001.1 known-failing E-002, which is resolved\n", "")


@given_steps("N0E", "TE", "TK:E-009", _tag(" known-failing E-009"))
def test_t086_5_tag_of_missing_entry(scratch):
    """@prd T-086.5"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")
