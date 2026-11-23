"""The --check option, a marker in §2, the refusals and which CLAUDE.md is written
(FR-240, FR-244 to FR-246; test-cases/status.yaml)."""
from __future__ import annotations

import pytest

from status_support import (  # noqa: F401 (repo is a fixture)
    CLAUDE_BASE, README_BASE, KnownFailure, absent, block, orders, repo, rtmp, snapshot, steps,
)

STALE = ["stale: CLAUDE.md", "stale: docs/prd/orders/README.md", "stale: docs/prd/README.md"]


def _b(text: str) -> bytes:
    return text.encode("utf-8")


def _targets(repo):
    return [repo / "CLAUDE.md", repo / "docs/prd/orders/README.md", repo / "docs/prd/README.md"]


@steps("N0")
def test_t240_1_check_missing_files(repo):
    """@prd T-240.1"""
    r = block(repo, "python BLOCK docs/prd/orders --check")
    assert r.exit == 1
    assert r.err == b""
    assert r.stdout.splitlines() == STALE
    for path in _targets(repo):
        assert absent(path), path


@steps("N0", "SB0")
def test_t240_2_check_current(repo):
    """@prd T-240.2"""
    r = block(repo, "python BLOCK docs/prd/orders --check")
    assert (r.exit, r.out, r.err) == (0, b"", b"")


@steps("N0", "SB0", "SVER")
def test_t240_3_check_stale(repo):
    """@prd T-240.3"""
    before = snapshot(*_targets(repo))
    r = block(repo, "python BLOCK docs/prd/orders --check")
    assert r.exit == 1
    assert r.stdout.splitlines() == STALE
    assert snapshot(*_targets(repo)) == before


@steps("N0X")
def test_t240_4_check_no_checkout(repo):
    """@prd T-240.4"""
    r = block(repo, "python BLOCK docs/prd/orders --claude-md <tmp>/CLAUDE.md --check")
    assert r.exit == 1
    assert r.stdout.splitlines() == STALE
    assert absent(repo / "CLAUDE.md")


@steps("N0", "SX2")
def test_t240_5_check_broken_markers(repo):
    """@prd T-240.5"""
    before = snapshot(repo / "CLAUDE.md")
    r = block(repo, "python BLOCK docs/prd/orders --check")
    assert r.exit == 2
    assert r.out == b""
    assert r.err == _b(f"prd_block: {rtmp(repo)}/CLAUDE.md: prd-toolkit start and end markers are unbalanced\n")
    assert snapshot(repo / "CLAUDE.md") == before


MARKER = b"prd_block: prd.md \xc2\xa72 holds a prd-toolkit marker\n"


@steps("N0", "SS4")
def test_t244_1_marker_in_summary(repo):
    """@prd T-244.1"""
    r = block(repo, "python BLOCK docs/prd/orders")
    assert r.exit == 2
    assert r.out == b""
    assert r.err == MARKER
    for path in _targets(repo):
        assert absent(path), path


@steps("N0", "SS5")
def test_t244_2_marker_line_in_section_2(repo):
    """@prd T-244.2"""
    r = block(repo, "python BLOCK docs/prd/orders")
    assert r.exit == 2
    assert r.err == MARKER
    assert absent(repo / "CLAUDE.md")


@steps("N0")
def test_t245_1_no_prd_md(repo):
    """@prd T-245.1"""
    r = block(repo, "python BLOCK <tmp>/nowhere")
    assert r.exit == 2
    assert r.out == b""
    assert r.err == _b(f"prd_block: {rtmp(repo)}/nowhere: no prd.md\n")
    assert absent(repo / "CLAUDE.md")


@steps("N0", "SU8")
def test_t245_2_table_in_section_8(repo):
    """@prd T-245.2"""
    expected = _b(f"prd_block: {rtmp(repo)}/docs/prd/orders/prd.md: section 8: the adoption map moved to "
                  'adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."\n')
    for text in ("python BLOCK docs/prd/orders", "python BLOCK docs/prd/orders --check"):
        r = block(repo, text)
        assert r.exit == 2, text
        assert r.out == b"", text
        assert r.err == expected, text
    assert absent(repo / "CLAUDE.md")
    assert absent(repo / "docs/prd/orders/README.md")


@steps("N0")
def test_t245_3_no_folder(repo):
    """@prd T-245.3"""
    r = block(repo, "python BLOCK")
    assert r.exit == 2
    assert r.out == b""
    assert r.err == (b"usage: prd_block.py [-h] [--claude-md CLAUDE_MD] [--check] prd_dir\n"
                     b"prd_block.py: error: the following arguments are required: prd_dir\n")


@steps("N0")
def test_t246_1_checkout_root(repo):
    """@prd T-246.1"""
    r = block(repo, "python BLOCK .", cwd=orders(repo))
    assert r.exit == 0, r.stderr
    assert (repo / "CLAUDE.md").read_bytes() == _b(CLAUDE_BASE)
    assert absent(repo / "docs/prd/orders/CLAUDE.md")


@steps("N0")
def test_t246_2_claude_md_option(repo):
    """@prd T-246.2"""
    r = block(repo, "python BLOCK docs/prd/orders --claude-md <tmp>/agents/AGENTS.md")
    assert r.exit == 0, r.stderr
    assert (repo / "agents/AGENTS.md").read_bytes() == _b(CLAUDE_BASE)
    assert absent(repo / "CLAUDE.md")
    assert (repo / "docs/prd/orders/README.md").read_bytes() == _b(README_BASE)


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps("N0X")
def test_t246_3_no_checkout_refused(repo):
    """@prd T-246.3 known-failing E-072"""
    r = block(repo, "python BLOCK docs/prd/orders")
    if r.exit == 0 and (repo / "docs/prd/orders/CLAUDE.md").exists():
        raise KnownFailure("the run exits 0 and writes docs/prd/orders/CLAUDE.md")
    assert r.exit == 2
    assert r.out == b""
    assert r.stderr.splitlines() == [
        f"prd_block: {rtmp(repo)}/docs/prd/orders: not inside a git checkout; name the CLAUDE.md with --claude-md"]
    assert absent(repo / "docs/prd/orders/CLAUDE.md")
    assert absent(repo / "CLAUDE.md")
    assert absent(repo / "docs/prd/orders/README.md")
