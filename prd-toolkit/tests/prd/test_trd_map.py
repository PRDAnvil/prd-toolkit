"""FR-266: map the areas and the requirements to the code (test-cases/trd.yaml, T-266.1 to T-266.4)."""
from __future__ import annotations

from trd_support import given_steps, pack_part_lines, run, trd_repo, with_sha7  # noqa: F401

VIEW = "python TRD docs/prd/orders"


@given_steps("V0", "VA")
def test_trd_components_from_the_adoption_map(trd_repo):
    """@prd T-266.1"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    assert pack_part_lines(r.out, "Components") == with_sha7([
        "## Components",
        "",
        "From: adoption.md and the files at <sha7>.",
        "",
        "| Area | State | Boundary | Files | Requirements |",
        "|---|---|---|---|---|",
        "| import | adopted | `src/importer.py`, `src/lib/**` | 3 | FR-001 approved, FR-002 built, FR-003 verified, FR-004 live |",
        "| reports | not started | `src/reports.py` | 1 | FR-005 approved, FR-006 live, FR-007 live |",
        "| billing | not started | `src/billing/*.py` | 1 | - |",
        "",
    ], tmp)


@given_steps("V0")
def test_trd_no_adoption_map(trd_repo):
    """@prd T-266.2"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    out = r.out
    assert pack_part_lines(out, "Components") == with_sha7([
        "## Components",
        "",
        "From: the features files and the files at <sha7>.",
        "",
        "| Area | State | Boundary | Files | Requirements |",
        "|---|---|---|---|---|",
        "| import | - | - | - | FR-001 approved, FR-002 built, FR-003 verified, FR-004 live |",
        "| reports | - | - | - | FR-005 approved, FR-006 live, FR-007 live |",
        "",
    ], tmp)
    assert pack_part_lines(out, "Requirements to code") == with_sha7([
        "## Requirements to code",
        "",
        "From: the Source: lines of the requirement blocks, checked at <sha7>.",
        "",
        "No requirement block has a Source: line.",
        "",
    ], tmp)
    assert pack_part_lines(out, "Uncovered code") == [
        "## Uncovered code",
        "",
        "From: prd.md section 8.",
        "",
        "No adoption map: every path outside the PRD folder and .prd-toolkit/ is covered.",
    ]


@given_steps("V0", "VA", "VS")
def test_trd_requirements_to_code(trd_repo):
    """@prd T-266.3"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    assert pack_part_lines(r.out, "Requirements to code") == with_sha7([
        "## Requirements to code",
        "",
        "From: the Source: lines of the requirement blocks, checked at <sha7>.",
        "",
        "| ID | Status | Source | At HEAD |",
        "|---|---|---|---|",
        "| FR-002 | built | src/importer.py:1 @abc1234 | yes |",
        "| FR-003 | verified | src/gone.py:4 @abc1234 | no |",
        "| FR-004 | live | src/importer.py:5 @abc1234 | no |",
        "",
    ], tmp)


@given_steps("V0", "VA", "VW")
def test_trd_uncovered_code(trd_repo):
    """@prd T-266.4"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    assert pack_part_lines(r.out, "Uncovered code") == with_sha7([
        "## Uncovered code",
        "",
        "From: the files at <sha7> that no Boundary glob of adoption.md matches.",
        "",
        "- `.prd-toolkit-notes.md`",
        "- `notes/readme.md`",
        "- `src/billing/deep/x.py`",
        "- `tests/test_orders.py`",
    ], tmp)
