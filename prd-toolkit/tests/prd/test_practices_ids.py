"""FR-054: the next source and practice ID (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import CHANGE, P0, PI1, check, run, setup  # noqa: E402

ORDERS = "docs/prd/orders"


def test_next_source_id(tmp_path):
    """@prd T-054.1"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, CHANGE, "ids", "next", ORDERS, "S")
    r2 = run(tmp_path, CHANGE, "ids", "next", ORDERS, "S", "--json")
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    check(r1, stdout="S-03\n")
    check(r2, stdout_json={"interface": 1, "kind": "change.ids", "next": "S-03"})


def test_next_practice_id(tmp_path):
    """@prd T-054.2"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, CHANGE, "ids", "next", ORDERS, "P")
    r2 = run(tmp_path, CHANGE, "ids", "next", ORDERS, "P", "--json")
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    check(r1, stdout="P-04\n")
    check(r2, stdout_json={"interface": 1, "kind": "change.ids", "next": "P-04"})


def test_unknown_kind(tmp_path):
    """@prd T-054.3"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, CHANGE, "ids", "next", ORDERS, "Q")
    r2 = run(tmp_path, CHANGE, "ids", "next", ORDERS, "s")  # the kinds are upper case
    for r in (r1, r2):
        check(r, exit=1, stdout="")
    check(r1, stderr="refused: unknown kind Q; use FR, NFR, UJ, S, P, AC-<nnn> or T-<nnn>\n")
    check(r2, stderr="refused: unknown kind s; use FR, NFR, UJ, S, P, AC-<nnn> or T-<nnn>\n")


def test_changelog_source_ids_count(tmp_path):
    """@prd T-054.4"""
    setup(tmp_path, P0, PI1)
    check(run(tmp_path, CHANGE, "ids", "next", ORDERS, "S"), exit=0, stderr="", stdout="S-06\n")


def test_changelog_practice_ids_count(tmp_path):
    """@prd T-054.5"""
    setup(tmp_path, P0, PI1)
    check(run(tmp_path, CHANGE, "ids", "next", ORDERS, "P"), exit=0, stderr="", stdout="P-08\n")
