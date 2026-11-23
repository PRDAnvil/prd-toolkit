"""The areas and the other PRD facts (FR-249, FR-250; test-cases/status.yaml)."""
from __future__ import annotations

from status_support import as_json, facts, repo, steps  # noqa: F401 (facts and repo are fixtures)


def _areas(F):
    return as_json([[a.name, a.file, a.adoption, list(a.counts.items())] for a in F.areas])


@steps("N0")
def test_t249_1_areas(repo, facts):
    """@prd T-249.1"""
    assert _areas(facts(repo)) == [
        ["import", "features/import.md", "-", [["live", 1], ["verified", 1], ["built", 1], ["approved", 1]]],
        ["reports", "features/reports.md", "-", [["live", 2], ["approved", 1]]],
    ]


@steps("N0", "NA1", "SU1", "SR7", "SAB")
def test_t249_2_areas_adopted(repo, facts):
    """@prd T-249.2"""
    assert _areas(facts(repo)) == [
        ["billing", "features/billing.md", "extracted", []],
        ["export", "features/export.md", "extracted", []],
        ["import", "features/import.md", "adopted", [["verified", 1], ["built", 1], ["approved", 1], ["as-built", 1]]],
        ["reports", "features/reports.md", "adopted", [["live", 1], ["approved", 1]]],
    ]


@steps("N0")
def test_t250_1_other_facts(repo, facts):
    """@prd T-250.1"""
    F = facts(repo)
    assert as_json({"slug": F.slug, "version": F.version, "status": F.status, "owner": F.owner,
                    "updated": F.updated, "open_errors": F.open_errors, "upstreams": F.upstreams,
                    "consumers": F.consumers, "files": F.files}) == {
        "slug": "orders", "version": "1.0.0", "status": "Approved", "owner": "Sample Owner", "updated": "2026-11-01",
        "open_errors": 0, "upstreams": [], "consumers": [],
        "files": ["prd.md", "features/", "test-cases/", "contracts/", "testing.md", "errors.md", "operations.md",
                  "nfr.md"],
    }


@steps("N0", "NA1", "NE1", "SK1", "SH0")
def test_t250_2_other_facts_with_links(repo, facts):
    """@prd T-250.2"""
    F = facts(repo)
    assert as_json({"status": F.status, "open_errors": F.open_errors, "upstreams": F.upstreams,
                    "consumers": F.consumers, "files": F.files}) == {
        "status": "unknown", "open_errors": 2,
        "upstreams": ["`https://example.com/greet.git#docs/prd/greet`"],
        "consumers": ["`git@example.com:org/bi.git#docs/prd/dashboards`"],
        "files": ["prd.md", "features/", "test-cases/", "contracts/", "testing.md", "errors.md", "operations.md",
                  "nfr.md", "adoption.md", "links.md"],
    }
