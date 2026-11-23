"""The parent README block and its install line (FR-242, FR-243; test-cases/status.yaml)."""
from __future__ import annotations

import pytest

from status_support import (  # noqa: F401 (H and repo are fixtures)
    PARENT_V, H, KnownFailure, absent, assert_lines_in_order, block, file_lines, repo, steps,
)

ORDERS_ROW = "| [orders](orders/) | 1.0.0 | Approved | The orders service imports order files and prints monthly reports. |"


def _parent(repo, text="python VBLOCK docs/prd/orders", stderr_empty=False) -> list[str]:
    r = block(repo, text)
    assert r.exit == 0, r.stderr
    if stderr_empty:
        assert r.err == b""
    return file_lines(repo / "docs/prd/README.md")


@steps("N0", "SV0")
def test_t242_1_parent_block(repo):
    """@prd T-242.1"""
    r = block(repo, "python VBLOCK docs/prd/orders")
    assert r.exit == 0, r.stderr
    assert r.err == b""
    assert (repo / "docs/prd/README.md").read_bytes() == PARENT_V.encode("utf-8")


@steps("N0", "SV0", "SB2", "SB4", "SB5")
def test_t242_2_sibling_rows(repo):
    """@prd T-242.2"""
    lines = _parent(repo, stderr_empty=True)
    assert_lines_in_order(lines, [
        "| PRD | Version | Status | Covers |",
        "|---|---|---|---|",
        r"| [billing](billing/) | 0.2.0 | Approved | Billing sends invoices \| credits. |",
        "| [my notes](my%20notes/) | 1.0.0 | Approved | The orders service imports order files and prints monthly reports. |",
        ORDERS_ROW,
        "",
        "## How it works",
    ])
    assert not [line for line in lines if line.startswith("| [notes](notes/) |")]
    assert not [line for line in lines if ".hidden" in line]


@steps("N0", "SV0", "SB3")
def test_t242_3_unreadable_sibling(repo):
    """@prd T-242.3"""
    r = block(repo, "python VBLOCK docs/prd/orders")
    assert r.exit == 0, r.stderr
    err_lines = r.stderr.splitlines()
    assert len(err_lines) == 1, r.stderr
    assert err_lines[0].startswith("prd_block: broken: could not be read (UnicodeDecodeError: ")
    assert_lines_in_order(file_lines(repo / "docs/prd/README.md"), [
        "|---|---|---|---|", "| broken | - | could not be read | - |", ORDERS_ROW])


@steps("N0", "SQ")
def test_t242_4_parent_not_prd(repo):
    """@prd T-242.4"""
    r = block(repo, "python BLOCK docs/requirements/orders")
    assert r.exit == 0, r.stderr
    assert absent(repo / "docs/requirements/README.md")
    assert_lines_in_order(file_lines(repo / "docs/requirements/orders/README.md"), [
        "the code. It is maintained with prd-toolkit, a Claude Code plugin."])
    assert_lines_in_order(file_lines(repo / "CLAUDE.md"), [
        "The PRD at `docs/requirements/orders` (version 1.0.0) is the authority."])


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps("N0", "SV0", "SS8")
def test_t242_5_placeholder_in_covers(repo):
    """@prd T-242.5 known-failing E-069"""
    r = block(repo, "python VBLOCK docs/prd/orders")
    parent = repo / "docs/prd/README.md"
    if parent.exists() and \
            "| [orders](orders/) | 1.0.0 | Approved | Prints https://example.com/toolkit as text. |" in file_lines(parent):
        raise KnownFailure("the Covers cell's {{homepage}} was replaced by the homepage")
    assert r.exit == 0, r.stderr
    assert r.err == b""
    assert_lines_in_order(file_lines(parent), [
        "| PRD | Version | Status | Covers |", "|---|---|---|---|",
        "| [orders](orders/) | 1.0.0 | Approved | Prints {{homepage}} as text. |"])


@steps("N0", "SV0")
def test_t243_1_vendored_homepage(repo):
    """@prd T-243.1"""
    assert_lines_in_order(_parent(repo), [
        "## Getting started", "", "- Install the prd-toolkit plugin for Claude Code: https://example.com/toolkit"])


@steps("N0", "SV0", "SV1")
def test_t243_2_vendored_empty_homepage(repo):
    """@prd T-243.2"""
    lines = _parent(repo)
    assert_lines_in_order(lines, ["## Getting started", "", "- Install the prd-toolkit plugin for Claude Code."])
    assert "https://example.com/host" not in (repo / "docs/prd/README.md").read_bytes().decode("utf-8")


@steps("N0", "SV0", "SV2")
def test_t243_3_vendored_no_homepage(repo):
    """@prd T-243.3"""
    assert_lines_in_order(_parent(repo), [
        "## Getting started", "", "- Install the prd-toolkit plugin for Claude Code."])


@steps("N0")
def test_t243_4_plugin_homepage(repo, H):
    """@prd T-243.4"""
    assert_lines_in_order(_parent(repo, "python BLOCK docs/prd/orders"), [
        "## Getting started", "", f"- Install the prd-toolkit plugin for Claude Code: {H}"])
