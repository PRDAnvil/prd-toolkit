"""inbox-cards: `prd_gates.py list` reads the PRD folder it is given alone (FR-071, AC-071.3)."""
from __future__ import annotations

from inbox_cards_support import build, run_gates


def test_list_reads_its_own_prd_folder(tmp_path, monkeypatch):
    """@prd T-071.5"""
    build(tmp_path, monkeypatch, "IC0")

    r = run_gates(tmp_path / "wt", "list", "docs/prd/orders")

    assert (r.exit, r.stdout, r.stderr) == (0, "error-class:E-001 The importer stops at row 1000\n", "")
