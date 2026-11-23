"""error-reopen FR-252: `prd error check` over a reopen (test-cases/error-reopen.yaml)."""
from __future__ import annotations

from error_reopen_support import assert_run, build

CHECK = "python ERROR check docs/prd/orders start..HEAD"


def test_check_accepts_a_reopen(tmp_path, monkeypatch):
    """@prd T-252.1"""
    c = build(tmp_path, monkeypatch, "O0", "OC", "OK", "OX")
    assert_run(c.run(CHECK), 0, stdout="", stderr="")


def test_check_accepts_a_reopen_a_confirmation_and_a_second_reopen(tmp_path, monkeypatch):
    """@prd T-252.2"""
    c = build(tmp_path, monkeypatch, "O0", "OC", "OK", "OX", "OY", "OZ")
    assert_run(c.run(CHECK), 0, stdout="", stderr="")


def test_check_reports_a_deleted_confirmation(tmp_path, monkeypatch):
    """@prd T-252.3"""
    c = build(tmp_path, monkeypatch, "O0", "OC", "OK", "OW")
    assert_run(c.run(CHECK), 1, stdout="errors.md: E-001: Confirmed: changed\n", stderr="")


def test_check_reports_an_edited_reopened_line(tmp_path, monkeypatch):
    """@prd T-252.4"""
    c = build(tmp_path, monkeypatch, "O0", "OC", "OK", "OX", "OE")
    assert_run(c.run(CHECK), 1, stdout="errors.md: E-001: Reopened: changed\n", stderr="")


def test_check_reports_a_reopened_line_without_its_confirmation(tmp_path, monkeypatch):
    """@prd T-252.5"""
    c = build(tmp_path, monkeypatch, "O0", "OC", "OK", "OH")
    assert_run(c.run(CHECK), 1, stdout="errors.md: E-002: Reopened: added without its Confirmed:\n", stderr="")


def test_check_reports_code_that_cites_a_reopened_entry(tmp_path, monkeypatch):
    """@prd T-252.6"""
    c = build(tmp_path, monkeypatch, "O0", "OC", "OK", "OX", "OS")
    head8 = c.head8()
    assert_run(
        c.run(CHECK), 1,
        stdout=f"errors.md: E-001: commit {head8} changes code and cites E-001, "
               "which was not confirmed at that commit\n",
        stderr="",
    )
