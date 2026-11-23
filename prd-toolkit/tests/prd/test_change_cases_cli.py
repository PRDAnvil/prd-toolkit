"""The change command's exit codes and usage errors (features/change.md FR-255; test-cases/change.yaml)."""
from __future__ import annotations

from change_support import (
    G0, case, exit_is, given, one_json_line, snapshot, stderr_first_line_starts, stderr_is,
    stderr_single_line_starts, stdout_is,
)

__all__ = ["case"]


@given(G0)
def test_t255_1_no_subcommand_is_a_usage_error(case):
    """@prd T-255.1"""
    for command in ("python CHANGE", "python CHANGE ids docs/prd/orders"):
        r = case.run(command)
        exit_is(r, 2)
        stdout_is(r, "")
        stderr_first_line_starts(r, "usage: prd_change.py")


def test_t255_2_interface(case):
    """@prd T-255.2"""
    r = case.run("python CHANGE --interface")
    exit_is(r, 0)
    stdout_is(r, "1\n")
    stderr_is(r, "")


@given(G0)
def test_t255_3_unsupported_interface(case):
    """@prd T-255.3"""
    r = case.run("python CHANGE digest docs/prd/orders --json=2")
    exit_is(r, 2)
    assert "prd_change: unsupported interface 2; this toolkit speaks 1" in r.err_lines, str(r)


def test_t255_4_folder_without_prd_md(case):
    """@prd T-255.4"""
    (case.tmp / "empty").mkdir()
    r = case.run("python CHANGE digest empty")
    exit_is(r, 2)
    stdout_is(r, "")
    stderr_single_line_starts(r, "prd_change: ")


@given(G0)
def test_t255_5_refusal_is_one_stderr_line(case):
    """@prd T-255.5"""
    r = case.run("python CHANGE ids next docs/prd/orders texts.ac_099")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: no block FR-099 or NFR-099\n")


@given(G0)
def test_t255_6_json_error_line(case):
    """@prd T-255.6"""
    before = snapshot(case.orders)["prd.md"]
    r = case.run("python CHANGE record docs/prd/orders --base nope --bump minor --change x --json")
    exit_is(r, 2)
    stderr_is(r, "bump: nope has no docs/prd/orders\n")
    assert one_json_line(r) == {"interface": 1, "kind": "change.record",
                                "error": "bump: nope has no docs/prd/orders"}, str(r)
    assert (case.orders / "prd.md").read_bytes() == before, "prd.md changed"
