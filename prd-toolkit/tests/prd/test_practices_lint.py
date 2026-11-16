"""FR-049: the lint rule practices (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import (LINT, P0, PB1, PB2, PB3, PB4, PB5, PB6, PB7, PB8, PB9, PB10,  # noqa: E402
                               PB11, PN, PR1, check, run, setup)

ORDERS = "docs/prd/orders"
PMD = "docs/prd/orders/practices.md"


def lint(tmp_path):
    return run(tmp_path, LINT, ORDERS)


def test_id_form(tmp_path):
    """@prd T-049.1"""
    setup(tmp_path, P0, PB1)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:8: practices: source ID 'S-2' is not S- and two digits",
        f"{PMD}:16: practices: practice ID 'P-3' is not P- and two digits",
    ])


def test_id_already_defined(tmp_path):
    """@prd T-049.2"""
    setup(tmp_path, P0, PB2)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:8: practices: S-01 is already defined at practices.md:7",
        f"{PMD}:16: practices: P-02 is already defined at practices.md:15",
    ])


def test_decision_value(tmp_path):
    """@prd T-049.3"""
    setup(tmp_path, P0, PB3)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:8: practices: source S-02: Decision 'maybe' is not one of approved, declined, proposed",
    ])


def test_proposed_source_on_an_approved_prd(tmp_path):
    """@prd T-049.4"""
    setup(tmp_path, P0, PB4)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:8: practices: source S-02 is still 'proposed' but the PRD is Approved",
    ])


def test_practice_source_absent_or_declined(tmp_path):
    """@prd T-049.5"""
    setup(tmp_path, P0, PB5, PB11)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:15: practices: practice P-02: source 'S-09' is not in the Sources table",
        f"{PMD}:16: practices: practice P-03: source S-02 is 'declined', not approved",
    ])


def test_practice_source_proposed_on_an_approved_prd(tmp_path):
    """@prd T-049.6"""
    setup(tmp_path, P0, PB4, PB11)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:8: practices: source S-02 is still 'proposed' but the PRD is Approved",
        f"{PMD}:16: practices: practice P-03: source S-02 is 'proposed', not approved",
    ])


def test_practice_source_proposed_while_in_review(tmp_path):
    """@prd T-049.7"""
    setup(tmp_path, P0, PB4, PB11, PR1)
    check(lint(tmp_path), exit=0, stdout="", stderr="")


def test_applies_to_value(tmp_path):
    """@prd T-049.8"""
    setup(tmp_path, P0, PB6)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:15: practices: practice P-02: Applies to 'docs' is not code or prd",
    ])


def test_code_practice_needs_a_glob(tmp_path):
    """@prd T-049.9"""
    setup(tmp_path, P0, PB7)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:14: practices: practice P-01: a code practice needs a glob in Object (glob)",
        f"{PMD}:15: practices: practice P-02: a code practice needs a glob in Object (glob)",
    ])


def test_read_date(tmp_path):
    """@prd T-049.10"""
    setup(tmp_path, P0, PB8)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        f"{PMD}:7: practices: source S-01: Read 'November 2026' is not a date YYYY-MM-DD",
        f"{PMD}:8: practices: source S-02: Read '2026-02-30' is not a date YYYY-MM-DD",
    ])


def test_standards_row_sources(tmp_path):
    """@prd T-049.11"""
    setup(tmp_path, P0, PB9)
    check(lint(tmp_path), exit=1, stderr="", stdout_exact_lines=[
        "docs/prd/orders/prd.md:45: practices: standards row names S-02, which is 'declined' in practices.md, not approved",
        "docs/prd/orders/prd.md:45: practices: standards row names S-07, which is not in practices.md",
    ])


def test_rule_registered_and_clean_fixture(tmp_path):
    """@prd T-049.12"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, LINT, ORDERS)
    r2 = run(tmp_path, LINT, "--list-rules")
    r3 = run(tmp_path, LINT, "--json", ORDERS)
    for r in (r1, r2, r3):
        check(r, exit=0, stderr="")
    check(r1, stdout="")
    check(r2, stdout_contains_line="practices error")
    check(r3, stdout_json_at={"findings": [], "errors": 0, "warnings": 0})


def test_no_practices_md_no_finding(tmp_path):
    """@prd T-049.13"""
    setup(tmp_path, P0, PN)
    check(lint(tmp_path), exit=0, stdout="", stderr="")


def test_glob_matching_no_file_is_not_a_fault(tmp_path):
    """@prd T-049.14"""
    setup(tmp_path, P0, PB10)
    check(lint(tmp_path), exit=0, stdout="", stderr="")
