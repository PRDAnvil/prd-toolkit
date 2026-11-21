"""Trace: the citations under the test roots (FR-082, FR-083; test-cases/trace.yaml)."""
from __future__ import annotations

from pathlib import Path

from trace_support import (  # noqa: F401  (scratch is a fixture)
    AT_PRD, N0E_NO_GIT, SetupError, append_line, assert_exact_lines, cite, given_steps, orders, replace_in_line,
    replace_line, run_trace, scratch, write_lines,
)

ADD = "add `" + AT_PRD + " T-001.1` to the test that proves it"
STATUS_CURRENT = "docs/prd/orders/features/import.md:8: status-current: FR-001 is verified but T-001.1 has no citing test"
T_IMPLEMENTED = "docs/prd/orders/features/import.md:8: t-implemented: T-001.1 (FR-001) is cited by no test; " + ADD


def _cite_t009_line3(tmp: Path) -> None:
    """append the comment line citing T-009.1 to <tmp>/tests/test_orders.py (it becomes line 3)"""
    if append_line(tmp / "tests/test_orders.py", cite("T-009.1")) != 3:
        raise SetupError("the appended citation is not line 3")


@given_steps("N0E", _cite_t009_line3)
def test_t082_1_cites_absent_tid(scratch):
    """@prd T-082.1"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (
        1, "tests/test_orders.py:3: test-cites-live: cites T-009.1, which does not exist in the PRD\n", "")


@given_steps("N0E", "TS:removed")
def test_t082_2_cites_removed_tid(scratch):
    """@prd T-082.2"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (
        1, "tests/test_orders.py:2: test-cites-live: cites T-001.1, which belongs to removed requirement FR-001\n", "")


def _roots_checks(tmp: Path) -> None:
    """in testing.md line 18 the text `Test roots: `tests/`` becomes `Test roots: `checks/``"""
    replace_in_line(orders(tmp) / "testing.md", 18, "Test roots: `tests/`", "Test roots: `checks/`")


def _write_checks(tmp: Path) -> None:
    """write <tmp>/checks/test_more.py with the comment line citing T-001.1"""
    write_lines(tmp / "checks/test_more.py", [cite("T-001.1")])


@given_steps("N0E", _roots_checks, _write_checks, "TC9")
def test_t083_1_reads_only_named_roots(scratch):
    """@prd T-083.1"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


def _roots_deleted(tmp: Path) -> None:
    """in testing.md line 18 the text ` Test roots: `tests/`` is deleted (the line then ends with the citation of T-001.1 and a full stop)"""
    path = orders(tmp) / "testing.md"
    replace_in_line(path, 18, " Test roots: `tests/`", "")
    line = path.read_text(encoding="utf-8").split("\n")[17]
    if not line.endswith("e.g. `" + AT_PRD + " T-001.1`."):
        raise SetupError(f"testing.md line 18 does not end as the step says: {line!r}")


@given_steps("N0E", _roots_deleted)
def test_t083_2_no_roots_text_reads_tests(scratch):
    """@prd T-083.2"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


def _roots_none(tmp: Path) -> None:
    """in testing.md line 18 the text `Test roots: `tests/`` becomes `Test roots: none`"""
    replace_in_line(orders(tmp) / "testing.md", 18, "Test roots: `tests/`", "Test roots: none")


@given_steps("N0E", _roots_none)
def test_t083_3_roots_without_path_reads_tests(scratch):
    """@prd T-083.3"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


@given_steps(N0E_NO_GIT)
def test_t083_4_no_git_resolves_against_prd_folder(scratch):
    """@prd T-083.4"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [STATUS_CURRENT, T_IMPLEMENTED])
    assert r.stderr == ""


def _cite_t001_10(tmp: Path) -> None:
    """in <tmp>/tests/test_orders.py line 2 becomes the comment line citing T-001.10"""
    replace_line(tmp / "tests/test_orders.py", 2, cite("T-001.10"))


@given_steps("N0E", _cite_t001_10)
def test_t083_5_tid_ends_at_word_boundary(scratch):
    """@prd T-083.5"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [
        "tests/test_orders.py:2: test-cites-live: cites T-001.10, which does not exist in the PRD",
        STATUS_CURRENT, T_IMPLEMENTED,
    ])
    assert r.stderr == ""


def _cite_split(tmp: Path) -> None:
    """in <tmp>/tests/test_orders.py line 2 becomes the two lines `# @prd` and `# T-001.1`"""
    replace_line(tmp / "tests/test_orders.py", 2, ["# " + AT_PRD, "# T-001.1"])


@given_steps("N0E", _cite_split)
def test_t083_6_citation_on_one_line(scratch):
    """@prd T-083.6"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [STATUS_CURRENT, T_IMPLEMENTED])
    assert r.stderr == ""


def _skipped_files(tmp: Path) -> None:
    """write <tmp>/tests/.prd-dry-run-x/test_dry.py and <tmp>/tests/__pycache__/cached.py, each citing T-001.1"""
    write_lines(tmp / "tests/.prd-dry-run-x/test_dry.py", [cite("T-001.1")])
    write_lines(tmp / "tests/__pycache__/cached.py", [cite("T-001.1")])


def _latin(tmp: Path) -> None:
    """write <tmp>/tests/latin.py with the bytes of the comment citing T-001.1, a space, then e9 0a: not UTF-8"""
    (tmp / "tests/latin.py").write_bytes((cite("T-001.1") + " ").encode("ascii") + bytes([0xE9, 0x0A]))


@given_steps("N0E", "TU", _skipped_files, _latin)
def test_t083_7_skips_dry_runs_caches_and_non_utf8(scratch):
    """@prd T-083.7"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [STATUS_CURRENT, T_IMPLEMENTED])
    assert r.stderr == ""
