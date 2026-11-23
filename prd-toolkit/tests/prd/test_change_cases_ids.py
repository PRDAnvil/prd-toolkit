"""The next free requirement, AC and T-id (features/change.md FR-256; test-cases/change.yaml)."""
from __future__ import annotations

from change_support import G0, GL, GM, TEXTS, case, diff, exit_is, given, snapshot, stderr_is, stdout_is, stdout_json

__all__ = ["case"]


@given(G0)
def test_t256_1_next_fr_and_nfr(case):
    """@prd T-256.1"""
    before = snapshot(case.tmp)
    r1 = case.run("python CHANGE ids next docs/prd/orders FR")
    r2 = case.run("python CHANGE ids next docs/prd/orders NFR")
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    stdout_is(r1, "FR-008\n")
    stdout_is(r2, "NFR-008\n")
    assert diff(before, snapshot(case.tmp)) == [], "a file under <tmp> changed"


@given(G0)
def test_t256_2_next_uj(case):
    """@prd T-256.2"""
    r = case.run("python CHANGE ids next docs/prd/orders UJ")
    exit_is(r, 0)
    stderr_is(r, "")
    stdout_is(r, "UJ-01\n")


@given(G0)
def test_t256_3_next_ac(case):
    """@prd T-256.3"""
    r1 = case.run("python CHANGE ids next docs/prd/orders texts.ac_001")
    case.steps(GM)
    r2 = case.run("python CHANGE ids next docs/prd/orders texts.ac_001")
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    stdout_is(r1, "AC-001.2\n")
    stdout_is(r2, "AC-001.3\n")


@given(G0)
def test_t256_4_next_t_id(case):
    """@prd T-256.4"""
    r = case.run("python CHANGE ids next docs/prd/orders texts.t_005")
    exit_is(r, 0)
    stderr_is(r, "")
    stdout_is(r, "T-005.3\n")


@given(G0)
def test_t256_5_no_such_block(case):
    """@prd T-256.5"""
    r1 = case.run("python CHANGE ids next docs/prd/orders texts.t_099")
    r2 = case.run("python CHANGE ids next docs/prd/orders texts.ac_12")
    for r in (r1, r2):
        exit_is(r, 1)
        stdout_is(r, "")
    stderr_is(r1, "refused: no block FR-099 or NFR-099\n")
    stderr_is(r2, TEXTS["refused_12"])


@given(G0)
def test_t256_6_json(case):
    """@prd T-256.6"""
    r = case.run("python CHANGE ids next docs/prd/orders FR --json")
    exit_is(r, 0)
    stderr_is(r, "")
    stdout_json(r, {"interface": 1, "kind": "change.ids", "next": "FR-008"})


@given(G0, GL)
def test_t256_7_ids_only_in_the_changelog_count(case):
    """@prd T-256.7"""
    r1 = case.run("python CHANGE ids next docs/prd/orders texts.t_001")
    r2 = case.run("python CHANGE ids next docs/prd/orders FR")
    r3 = case.run("python CHANGE ids next docs/prd/orders UJ")
    for r in (r1, r2, r3):
        exit_is(r, 0)
        stderr_is(r, "")
    stdout_is(r1, "T-001.5\n")
    stdout_is(r2, "FR-013\n")
    stdout_is(r3, "UJ-04\n")
