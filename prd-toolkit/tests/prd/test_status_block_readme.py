"""The PRD folder's README block (FR-241; test-cases/status.yaml)."""
from __future__ import annotations

import pytest

from status_support import (  # noqa: F401 (repo is a fixture)
    README_BASE, KnownFailure, assert_lines_in_order, block, file_lines, repo, steps,
)


def _readme(repo) -> list[str]:
    r = block(repo, "python BLOCK docs/prd/orders")
    assert r.exit == 0, r.stderr
    return file_lines(repo / "docs/prd/orders/README.md")


@steps("N0")
def test_t241_1_readme_block(repo):
    """@prd T-241.1"""
    r = block(repo, "python BLOCK docs/prd/orders")
    assert r.exit == 0, r.stderr
    assert (repo / "docs/prd/orders/README.md").read_bytes() == README_BASE.encode("utf-8")


@steps("N0", "SS1")
def test_t241_2_summary_lines(repo):
    """@prd T-241.2"""
    assert_lines_in_order(_readme(repo), [
        "## What this PRD covers", "", "> The orders service imports order files. It prints", "> monthly reports.",
        "", "## Areas"])


@steps("N0", "SS2")
def test_t241_3_no_summary(repo):
    """@prd T-241.3"""
    assert_lines_in_order(_readme(repo), [
        "## What this PRD covers", "", "_No summary yet: prd.md §2 is empty._", "", "## Areas"])
    assert "| [orders](orders/) | 1.0.0 | Approved | - |" in file_lines(repo / "docs/prd/README.md")


@steps("N0", "NA1")
def test_t241_4_areas_table(repo):
    """@prd T-241.4"""
    assert_lines_in_order(_readme(repo), [
        "## Areas", "", "| Area | Adoption | File |", "|---|---|---|",
        "| billing | extracted | [features/billing.md](features/billing.md) |",
        "| export | extracted | [features/export.md](features/export.md) |",
        "| import | adopted | [features/import.md](features/import.md) |",
        "| reports | adopted | [features/reports.md](features/reports.md) |", "", "## What is in this folder"])


@steps("N0", "NA1", "SK2")
def test_t241_5_files_table(repo):
    """@prd T-241.5"""
    assert_lines_in_order(_readme(repo), [
        "| Path | Holds |",
        "|---|---|",
        "| `prd.md` | The overview: goals, glossary, architecture, the requirement index, open questions, changelog |",
        "| `features/` | One file per area: requirements (`FR-nnn`) and their acceptance criteria (`AC-nnn.n`) |",
        "| `test-cases/` | The test cases for each criterion (`T-nnn.n`), which the tests cite |",
        "| `contracts/` | The interfaces the code must match: commands, configuration, schemas, APIs |",
        "| `testing.md` | How the tests are run, at which level and gate |",
        "| `errors.md` | The error ledger: every bug, its class and its fix (`E-nnn`) |",
        "| `operations.md` | Environments and the deploy runbook |",
        "| `nfr.md` | Non-functional requirements (`NFR-nnn`) |",
        "| `adoption.md` | Which areas of the existing code are under this PRD, and their state |",
        "| `links.md` | The PRDs whose contracts this one uses or provides |",
        "",
        "## Linked PRDs",
    ])


@steps("N0", "SK2")
def test_t241_6_linked_path(repo):
    """@prd T-241.6"""
    assert_lines_in_order(_readme(repo), [
        "| `links.md` | The PRDs whose contracts this one uses or provides |", "", "## Linked PRDs", "",
        "**Upstreams**", "", "- [../billing](../billing)", "", "**Consumers**", "", "- none", "",
        "## Reading and changing it"])


@steps("N0", "SK1")
def test_t241_7_linked_urls(repo):
    """@prd T-241.7"""
    assert_lines_in_order(_readme(repo), [
        "## Linked PRDs", "", "**Upstreams**", "", "- `https://example.com/greet.git#docs/prd/greet`", "",
        "**Consumers**", "", "- `git@example.com:org/bi.git#docs/prd/dashboards`", "", "## Reading and changing it"])


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps("N0", "SS7")
def test_t241_8_placeholder_in_summary(repo):
    """@prd T-241.8 known-failing E-069"""
    r = block(repo, "python BLOCK docs/prd/orders")
    readme = repo / "docs/prd/orders/README.md"
    if readme.exists():
        lines = file_lines(readme)
        if "## What this PRD covers" in lines:
            i = lines.index("## What this PRD covers")
            if i + 2 < len(lines) and lines[i + 2].startswith("> See | Area | Adoption | File |"):
                raise KnownFailure("the summary's {{areas}} was replaced by the areas table")
    assert r.exit == 0, r.stderr
    assert_lines_in_order(file_lines(readme), [
        "## What this PRD covers", "", "> See {{areas}} for the areas.", "", "## Areas"])
