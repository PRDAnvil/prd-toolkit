"""The Matrix part (FR-234; test-cases/status.yaml)."""
from __future__ import annotations

from status_support import assert_lines_in_order, part_lines, repo, status, steps  # noqa: F401


def _report(repo):
    r = status(repo, "python STATUS .")
    assert r.exit == 0, r.stderr
    return r


@steps("N0")
def test_t234_1_matrix(repo):
    """@prd T-234.1"""
    assert part_lines(_report(repo).stdout, "Matrix") == [
        "## Matrix", "", "FR-001: T-001.1 integration build cited", "FR-002: T-002.1 integration build cited",
        "FR-003: T-003.1 integration build cited", "FR-004: T-004.1 integration build cited",
        "FR-005: T-005.1 integration build cited; T-005.2 judged build cited",
        "FR-006: T-006.1 integration build cited", "FR-007: T-007.1 integration build cited"]


@steps("N0", "NT1")
def test_t234_2_missing(repo):
    """@prd T-234.2"""
    assert "FR-002: T-002.1 integration build missing" in _report(repo).stdout.splitlines()


@steps("N0", "SM1")
def test_t234_3_level_without_row(repo):
    """@prd T-234.3"""
    assert "FR-001: T-001.1 system - cited" in _report(repo).stdout.splitlines()


@steps("N0", "SU1")
def test_t234_4_no_tests(repo):
    """@prd T-234.4"""
    assert_lines_in_order(_report(repo).stdout.splitlines(), [
        "## Matrix", "FR-004: T-004.1 integration build cited", "UJ-01: no tests",
        "FR-005: T-005.1 integration build cited; T-005.2 judged build cited"])


@steps("N0", "SZ")
def test_t234_5_matrix_none(repo):
    """@prd T-234.5"""
    assert part_lines(_report(repo).stdout, "Matrix") == ["## Matrix", "", "None."]
