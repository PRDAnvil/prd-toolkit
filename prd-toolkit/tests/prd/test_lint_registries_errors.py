"""lint-registries characterization tests: error-entries on errors.md
(test-cases/lint-registries.yaml, T-144 to T-147)."""
from __future__ import annotations

import pytest

from lint_registries_support import (  # noqa: F401  (case is a fixture)
    S0, assert_exit, assert_stderr, assert_stdout, assert_stdout_contains_line,
    assert_stdout_exact_lines, assert_stdout_not_contains, case, insert_after, replace, steps, text,
)


class KnownFailure(Exception):
    """The symptom a known-failing case's `symptom:` names was seen."""


def append_lines(rel: str, *parts):
    """append to F: each part is a line, or a list of lines taken from texts.<key>, in order."""
    def step(c):
        lines: list[str] = []
        for p in parts:
            if callable(p):
                p = p()
            lines.extend(p if isinstance(p, list) else [p])
        c.append(rel, lines)
    return step


def T(key: str):
    return lambda: text(key)


# ---- FR-144: entries numbered from E-001 upward ----

@steps(S0, replace("errors.md", 3, "### E-002 Empty import file crashed the importer"))
def test_first_entry_above_one(case):
    """@prd T-144.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/errors.md:3: error-entries: E-002 is the first entry: E-001 is missing; entries are never deleted, restore it from git")
    assert_stderr(r, "")


@steps(S0, replace("errors.md", 3, "### E-003 Empty import file crashed the importer"))
def test_first_entry_two_and_many_missing(case):
    """@prd T-144.2"""
    r1 = case.lint()
    case.replace_now("errors.md", 3, "### E-012 Empty import file crashed the importer")
    r2 = case.lint()
    assert_exit(r1, 1)
    assert_stdout_contains_line(r1, "docs/prd/orders/errors.md:3: error-entries: E-003 is the first entry: E-001, E-002 are missing; entries are never deleted, restore them from git")
    assert_exit(r2, 1)
    assert_stdout_contains_line(r2, "docs/prd/orders/errors.md:3: error-entries: E-012 is the first entry: E-001 to E-011 are missing; entries are never deleted, restore them from git")


@steps(S0, append_lines("errors.md", "", "### E-003 A later entry", T("entry_tail")))
def test_later_entry_one_missing(case):
    """@prd T-144.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:10: error-entries: E-003 follows E-001: E-002 is missing; entries are never deleted, restore it from git"])
    assert_stderr(r, "")


@steps(S0, append_lines("errors.md", "", "### E-005 A later entry", T("entry_tail")))
def test_later_entry_three_missing(case):
    """@prd T-144.4"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:10: error-entries: E-005 follows E-001: E-002 to E-004 are missing; entries are never deleted, restore them from git"])
    assert_stderr(r, "")


@steps(S0, append_lines("errors.md", "", T("short_id_heading"), T("entry_tail")))
def test_later_entry_out_of_order_short_id(case):
    """@prd T-144.5"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_contains_line(r, text("short_id_expect"))
    assert_stdout_not_contains(r, "is missing")
    assert_stderr(r, "")


@steps(S0, append_lines("errors.md", "", "### E-002 A later entry", T("entry_tail"),
                        "", "### E-003 The latest entry", T("entry_tail_later")))
def test_entries_in_sequence(case):
    """@prd T-144.6"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps(S0, append_lines("errors.md", T("later_entries")))
def test_skipped_number_later_is_no_gap(case):
    """@prd T-144.7 known-failing E-052"""
    r = case.lint()
    symptom = "docs/prd/orders/errors.md:10: error-entries: E-003 follows E-001: E-002 is missing; entries are never deleted, restore it from git"
    if symptom in r.lines:
        raise KnownFailure(symptom)
    assert_exit(r, 1)
    assert_stdout_contains_line(r, "docs/prd/orders/errors.md:15: error-entries: E-002 follows E-003: entries run from E-001 upward, newest last")
    assert_stdout_not_contains(r, "is missing")
    assert_stderr(r, "")


# ---- FR-145: Classification and Evidence ----

@steps(S0, replace("errors.md", 5, "Classification: typo"))
def test_unknown_classification(case):
    """@prd T-145.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:5: error-entries: E-001: Classification: 'typo' is not one of code bug, spec gap, invalid requirement, environment, standard, unclassified"])
    assert_stderr(r, "")


@steps(S0, insert_after("errors.md", 5, "Evidence: run 1", *[f"  run {i}" for i in range(2, 22)]))
def test_evidence_21_lines(case):
    """@prd T-145.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:6: error-entries: E-001: Evidence: is 21 lines; at most 20"])
    assert_stderr(r, "")


@steps(S0, insert_after("errors.md", 5, "Evidence: run 1", *[f"  run {i}" for i in range(2, 21)]))
def test_evidence_20_lines(case):
    """@prd T-145.3"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0, insert_after("errors.md", 5, "Evidence:", *[f"  run {i}" for i in range(1, 22)]))
def test_evidence_empty_first_line(case):
    """@prd T-145.4"""
    r1 = case.lint()
    case.delete_now("errors.md", 27, was="  run 21")
    r2 = case.lint()
    assert_exit(r1, 1)
    assert_stdout_exact_lines(r1, ["docs/prd/orders/errors.md:6: error-entries: E-001: Evidence: is 21 lines; at most 20"])
    assert_exit(r2, 0)
    assert_stdout(r2, "")


# ---- FR-146: the Confirmed line ----

@steps(S0, insert_after("errors.md", 5, "Confirmed: yesterday"))
def test_confirmed_malformed(case):
    """@prd T-146.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:6: error-entries: E-001: Confirmed: must be '<YYYY-MM-DD>, \"<reply>\"'"])
    assert_stderr(r, "")


@steps(S0, replace("errors.md", 5, "Classification: unclassified"),
       replace("errors.md", 7, "Resolution: open"),
       insert_after("errors.md", 5, 'Confirmed: 2026-11-01, "yes"'))
def test_confirmed_on_unclassified(case):
    """@prd T-146.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:6: error-entries: E-001: Confirmed: on an unclassified entry"])
    assert_stderr(r, "")


@steps(S0, insert_after("errors.md", 5, 'Confirmed: 2026-11-01, "yes, a code bug"'))
def test_confirmed_well_formed(case):
    """@prd T-146.3"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


# ---- FR-147: Detected and Recurrence of on an entry with Confirmed ----

@steps(S0, replace("errors.md", 4, "Detected: yesterday"),
       insert_after("errors.md", 5, 'Confirmed: 2026-11-01, "yes"'))
def test_detected_malformed(case):
    """@prd T-147.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:4: error-entries: E-001: Detected: must be \"<YYYY-MM-DD>, <source>\""])
    assert_stderr(r, "")


@steps(S0, replace("errors.md", 4, "Detected: 2026-10-29,test failure"),
       insert_after("errors.md", 5, 'Confirmed: 2026-11-01, "yes"'))
def test_detected_no_space_after_comma(case):
    """@prd T-147.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:4: error-entries: E-001: Detected: must be \"<YYYY-MM-DD>, <source>\""])
    assert_stderr(r, "")


@steps(S0, replace("errors.md", 8, "Recurrence of: E-001, E-009"),
       insert_after("errors.md", 5, 'Confirmed: 2026-11-01, "yes"'))
def test_recurrence_not_an_entry(case):
    """@prd T-147.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/errors.md:9: error-entries: E-001: Recurrence of: E-009 is not an entry"])
    assert_stderr(r, "")
