"""Trace: the printed findings, the JSON document and the refusals (FR-087 to FR-089; test-cases/trace.yaml)."""
from __future__ import annotations

from pathlib import Path

from trace_support import (  # noqa: F401  (scratch is a fixture)
    AT_PRD, assert_exact_lines, assert_single_line_starts, given_steps, one_json_line, orders, replace_line,
    run_trace, scratch,
)

ADD = "add `" + AT_PRD + " T-001.1` to the test that proves it"
CITES_T009 = "test-cites-live: cites T-009.1, which does not exist in the PRD"
STATUS_CURRENT = "status-current: FR-001 is verified but T-001.1 has no citing test"
T_IMPLEMENTED = "t-implemented: T-001.1 (FR-001) is cited by no test; " + ADD


def _mkdir(name: str):
    def step(tmp: Path) -> None:
        (tmp / name).mkdir()
    step.__name__ = f"mkdir_{name}"
    step.__doc__ = f"create the empty folder <tmp>/{name}"
    return step


# -- FR-087 --

@given_steps("N0E")
def test_t087_1_no_finding_prints_nothing(scratch):
    """@prd T-087.1"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


@given_steps("N0E", "TC9")
def test_t087_2_findings_sorted_with_prefix(scratch):
    """@prd T-087.2"""
    r = run_trace(scratch, "docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [
        "tests/test_orders.py:2: " + CITES_T009,
        "docs/prd/orders/features/import.md:8: " + STATUS_CURRENT,
        "docs/prd/orders/features/import.md:8: " + T_IMPLEMENTED,
    ])
    assert r.stderr == ""


@given_steps("N0E", "TC9")
def test_t087_3_cwd_is_prd_folder(scratch):
    """@prd T-087.3"""
    r = run_trace(orders(scratch), ".")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [
        "../../../tests/test_orders.py:2: " + CITES_T009,
        "features/import.md:8: " + STATUS_CURRENT,
        "features/import.md:8: " + T_IMPLEMENTED,
    ])
    assert r.stderr == ""


@given_steps("N0E", "TC9", _mkdir("elsewhere"))
def test_t087_4_folder_outside_cwd_absolute_prefix(scratch):
    """@prd T-087.4"""
    r = run_trace(scratch / "elsewhere", f"{scratch}/docs/prd/orders")
    assert r.exit == 1
    assert_exact_lines(r.stdout, [
        f"{scratch}/tests/test_orders.py:2: " + CITES_T009,
        f"{scratch}/docs/prd/orders/features/import.md:8: " + STATUS_CURRENT,
        f"{scratch}/docs/prd/orders/features/import.md:8: " + T_IMPLEMENTED,
    ])
    assert r.stderr == ""


# -- FR-088 --

@given_steps("N0E", "TC9")
def test_t088_1_json_document(scratch):
    """@prd T-088.1"""
    r = run_trace(scratch, "docs/prd/orders", "--json")
    assert r.exit == 1
    doc = one_json_line(r.stdout)
    first = ["interface", "kind", "prd", "version", "dir", "errors", "warnings", "findings"]
    assert list(doc.keys())[:len(first)] == first, r.stdout
    assert doc == {
        "interface": 1, "kind": "trace", "prd": "orders", "version": "1.0.0", "dir": "docs/prd/orders",
        "errors": 3, "warnings": 0,
        "findings": [
            {"file": "../../../tests/test_orders.py", "line": 2, "rule": "test-cites-live", "severity": "error",
             "message": "cites T-009.1, which does not exist in the PRD"},
            {"file": "features/import.md", "line": 8, "rule": "status-current", "severity": "error",
             "message": "FR-001 is verified but T-001.1 has no citing test"},
            {"file": "features/import.md", "line": 8, "rule": "t-implemented", "severity": "error",
             "message": "T-001.1 (FR-001) is cited by no test; " + ADD},
        ],
    }
    assert r.stderr == ""


@given_steps("N0E")
def test_t088_2_json_equals_1_no_finding(scratch):
    """@prd T-088.2"""
    r = run_trace(scratch, "--json=1", "docs/prd/orders")
    assert r.exit == 0
    assert one_json_line(r.stdout) == {
        "interface": 1, "kind": "trace", "prd": "orders", "version": "1.0.0", "dir": "docs/prd/orders",
        "errors": 0, "warnings": 0, "findings": [],
    }
    assert r.stderr == ""


@given_steps(_mkdir("nothing"))
def test_t088_3_json_error_object(scratch):
    """@prd T-088.3"""
    r = run_trace(scratch, "nothing", "--json")
    assert r.exit == 2
    assert one_json_line(r.stdout) == {"interface": 1, "kind": "trace", "error": f"{scratch}/nothing: no prd.md"}
    assert r.stderr == f"prd_trace: {scratch}/nothing: no prd.md\n"


@given_steps(_mkdir("nothing"))
def test_t088_4_unsupported_interface(scratch):
    """@prd T-088.4"""
    r = run_trace(scratch, "nothing", "--json=2")
    assert r.exit == 2
    assert one_json_line(r.stdout) == {
        "interface": 1, "kind": "trace", "error": "unsupported interface 2; this toolkit speaks 1"}
    assert r.stderr == "prd_trace: unsupported interface 2; this toolkit speaks 1\n"
    assert "no prd.md" not in r.stdout + r.stderr  # effects: the folder is not read


@given_steps(_mkdir("nothing"))
def test_t088_5_interface(scratch):
    """@prd T-088.5"""
    r = run_trace(scratch, "nothing", "--interface")
    assert (r.exit, r.stdout, r.stderr) == (0, "1\n", "")


# -- FR-089 --

@given_steps()
def test_t089_1_no_folder_prints_usage(scratch):
    """@prd T-089.1"""
    r = run_trace(scratch)
    assert r.exit == 2
    assert r.stdout == ""
    assert r.stderr.splitlines()[:1] and r.stderr.splitlines()[0].startswith("usage: prd_trace.py"), r.stderr


@given_steps(_mkdir("nothing"))
def test_t089_2_no_prd_md(scratch):
    """@prd T-089.2"""
    r = run_trace(scratch, "nothing")
    assert (r.exit, r.stdout, r.stderr) == (2, "", f"prd_trace: {scratch}/nothing: no prd.md\n")


def _section8_table(tmp: Path) -> None:
    """in prd.md line 57, `Not applicable: new project.`, becomes the three lines of an adoption table"""
    replace_line(orders(tmp) / "prd.md", 57,
                 ["| Area | State | Boundary |", "|---|---|---|", "| import | adopted | `src/**` |"],
                 old="Not applicable: new project.")


@given_steps("N0E", _section8_table)
def test_t089_3_section8_table_without_adoption_md(scratch):
    """@prd T-089.3"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (
        2, "",
        f"prd_trace: {scratch}/docs/prd/orders/prd.md: section 8: the adoption map moved to adoption.md in "
        "prd-toolkit 0.3; move the table there and leave \"See adoption.md.\"\n",
    )


@given_steps("N0E", "TB")
def test_t089_4_bad_range(scratch):
    """@prd T-089.4"""
    r = run_trace(scratch, "docs/prd/orders", "--range", "nosuch..HEAD")
    assert r.exit == 2
    assert r.stdout == ""
    assert_single_line_starts(r.stderr, "prd_trace: bad --range nosuch..HEAD: ")
