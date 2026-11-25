"""FR-266: Source: lines with several refs and continuation lines (test-cases/trd.yaml, T-266.5)."""
from __future__ import annotations

from trd_support import given_steps, pack_part_lines, run, trd_repo, with_sha7  # noqa: F401


@given_steps("V0", "VA", "VC")
def test_requirements_to_code_several_refs(trd_repo):
    """@prd T-266.5"""
    r = run(trd_repo, "python TRD docs/prd/orders")
    assert r.exit == 0, r.err
    assert pack_part_lines(r.out, "Requirements to code") == with_sha7([
        "## Requirements to code",
        "",
        "From: the Source: lines of the requirement blocks, checked at <sha7>.",
        "",
        "| ID | Status | Source | At HEAD |",
        "|---|---|---|---|",
        "| FR-002 | built | src/importer.py:1 @abc1234, src/lib/a.py:1 @abc1234, src/reports.py:1 @abc1234 | yes |",
        "| FR-003 | verified | src/importer.py:1 @abc1234, src/gone.py:2 @abc1234 | no |",
        "",
    ], trd_repo)
