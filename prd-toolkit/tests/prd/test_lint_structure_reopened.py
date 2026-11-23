"""lint-structure AC-026.2: the prose rules blank a Reopened: line (test-cases/lint-structure.yaml)."""
from __future__ import annotations

from lint_structure_support import Orders, check


def test_reopened_line_is_blanked_for_the_prose_rules(tmp_path, monkeypatch):
    """@prd T-026.6"""
    orders = Orders(tmp_path, monkeypatch)
    orders.lines("errors.md").insert_before(
        6, 'Reopened: 2026-11-04, "a purchase arrives late"; was Confirmed: 2026-11-03, "a purchase arrives"'
    )
    r = orders.run()
    check(
        r,
        not_contains=[
            "docs/prd/orders/errors.md:6: glossary-synonym",
            "docs/prd/orders/errors.md:6: error-entries",
        ],
        stderr="",
    )
