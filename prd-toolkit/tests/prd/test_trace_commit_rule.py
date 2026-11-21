"""Characterization tests of FR-091 and FR-092 (test-cases/trace.yaml): the commit rule, through the commit-msg hook.

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/trace.yaml and testing.md (Setup steps,
the trace steps). Each run is `python HOOK commit-msg docs/prd/orders msg.txt` in <tmp>, on a staged src/app.py.
"""
from __future__ import annotations

from pathlib import Path

from trace_support import TM, given_steps, orders, run_hook, write_lines
from trace_support import scratch  # noqa: F401  (the fixture given_steps parametrizes)

ACCEPTED = "prd-toolkit: accepted forms: Refs: FR-001, E-002 | Refs: none (no behaviour change)\n"
NO_REFS = "prd-toolkit: no `Refs:` trailer (`Refs: FR-001`, or `Refs: none (no behaviour change)`)\n"


def tm(*lines: str):
    """Step TM:t, for a text t of several lines, as a named step."""
    def TM_lines(tmp: Path) -> None:
        TM(tmp, list(lines))
    return TM_lines


def run(tmp: Path):
    return run_hook(tmp, "commit-msg", "docs/prd/orders", "msg.txt")


def assert_result(r, exit: int, stderr: str) -> None:
    assert r.exit == exit, (r.exit, r.stderr)
    assert r.stdout == ""
    assert r.stderr == stderr


# -- FR-091 --

@given_steps("N0E", "TB", "TX", "TM:add app")
def test_no_refs_trailer(scratch):
    """@prd T-091.1"""
    assert_result(run(scratch), 1, NO_REFS + ACCEPTED)


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs:" + " " * 3, "refs: FR-001"))
def test_empty_refs_and_lowercase_refs_are_no_trailer(scratch):
    """@prd T-091.2"""
    # TM: the four lines `add app`, ``, `Refs:   ` (three spaces after the colon) and `refs: FR-001`.
    r = run(scratch)
    assert r.exit == 1, (r.exit, r.stderr)
    assert r.stdout == ""
    assert r.stderr == NO_REFS + ACCEPTED


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs:  none (no behaviour change)  "))
def test_refs_none_trimmed_is_accepted(scratch):
    """@prd T-091.3"""
    assert_result(run(scratch), 0, "")


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: none"))
def test_bare_none_is_refused(scratch):
    """@prd T-091.4"""
    assert_result(
        run(scratch), 1,
        "prd-toolkit: `none` alone is not accepted; write `Refs: none (no behaviour change)`\n" + ACCEPTED,
    )


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: FR-009, FR-001"))
def test_undefined_fr(scratch):
    """@prd T-091.5"""
    assert_result(run(scratch), 1, "prd-toolkit: FR-009 is not defined in the PRD\n" + ACCEPTED)


@given_steps("N0E", "TS:removed", "TB", "TX", tm("add app", "", "Refs: FR-001"))
def test_removed_fr(scratch):
    """@prd T-091.6"""
    assert_result(run(scratch), 1, "prd-toolkit: FR-001 is removed\n" + ACCEPTED)


@given_steps("N0E", "TEC", "TB", "TX", tm("add app", "", "Refs: E-007"))
def test_undefined_error_entry(scratch):
    """@prd T-091.7"""
    assert_result(run(scratch), 1, "prd-toolkit: E-007 is not defined in the PRD\n" + ACCEPTED)


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: JIRA-12"))
def test_foreign_key(scratch):
    """@prd T-091.8"""
    assert_result(
        run(scratch), 1,
        "prd-toolkit: `JIRA-12` is not a PRD ID; give other keys their own trailer\n" + ACCEPTED,
    )


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: FR-001", "Refs: FR-009 , ,UJ-01"))
def test_every_refs_line_and_item(scratch):
    """@prd T-091.9"""
    assert_result(
        run(scratch), 1,
        "prd-toolkit: FR-009 is not defined in the PRD\nprd-toolkit: UJ-01 is not defined in the PRD\n" + ACCEPTED,
    )


# -- FR-092 --

@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: FR-001", "Change-set: orders/CS-1"))
def test_malformed_change_set(scratch):
    """@prd T-092.1"""
    assert_result(run(scratch), 1, "prd-toolkit: `Change-set: orders/CS-1` must be orders/CS-nnn\n" + ACCEPTED)


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: FR-001", "Change-set: orders/CS-001"))
def test_change_set_without_record(scratch):
    """@prd T-092.2"""
    assert_result(run(scratch), 1, "prd-toolkit: Change-set: orders/CS-001 has no record in changes/\n" + ACCEPTED)


@given_steps("N0E", "TB", "TX", tm("add app", "", "Refs: FR-001", "Change-set: greet/CS-004"))
def test_change_set_of_another_prd(scratch):
    """@prd T-092.3"""
    assert_result(run(scratch), 0, "")


def change_record(tmp: Path) -> None:
    write_lines(orders(tmp) / "changes/CS-001.md", ["# CS-001 A change"])


@given_steps("N0E", change_record, "TB", "TX", tm("add app", "", "Refs: FR-001", "Change-set: orders/CS-001"))
def test_change_set_with_record(scratch):
    """@prd T-092.4"""
    assert_result(run(scratch), 0, "")
