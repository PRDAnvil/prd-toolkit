"""Where each block goes, what counts as a marker, links and modes (FR-237 to FR-239; test-cases/status.yaml)."""
from __future__ import annotations

import os

import pytest

from status_support import (  # noqa: F401 (H and repo are fixtures)
    CLAUDE_BASE, H, README_BASE, KnownFailure, absent, block, parent_p, repo, rtmp, snapshot, steps, write_files,
)

RUN = "python BLOCK docs/prd/orders"


def _b(text: str) -> bytes:
    return text.encode("utf-8")


@steps("N0")
def test_t237_1_empty_and_missing_files(repo, H):
    """@prd T-237.1"""
    write_files({repo / "CLAUDE.md": ""})
    r = block(repo, RUN)
    assert (r.exit, r.out, r.err) == (0, b"", b"")
    assert (repo / "CLAUDE.md").read_bytes() == _b(CLAUDE_BASE)
    assert (repo / "docs/prd/orders/README.md").read_bytes() == _b(README_BASE)
    assert (repo / "docs/prd/README.md").read_bytes() == _b(parent_p(H))


@steps("N0")
def test_t237_2_claude_md_appended(repo):
    """@prd T-237.2"""
    write_files({repo / "CLAUDE.md": "# Mine\n"})
    r = block(repo, RUN)
    assert (r.exit, r.out) == (0, b"")
    assert (repo / "CLAUDE.md").read_bytes() == _b("# Mine" + "\n" + "\n" + CLAUDE_BASE)


@steps("N0")
def test_t237_3_claude_md_no_final_newline(repo):
    """@prd T-237.3"""
    write_files({repo / "CLAUDE.md": "# Mine"})
    r = block(repo, RUN)
    assert r.exit == 0, r.stderr
    assert (repo / "CLAUDE.md").read_bytes() == _b("# Mine" + "\n\n" + CLAUDE_BASE)


@steps("N0")
def test_t237_4_readme_prepended(repo):
    """@prd T-237.4"""
    write_files({repo / "docs/prd/orders/README.md": "# Mine\n\nold text\n"})
    r = block(repo, RUN)
    assert r.exit == 0, r.stderr
    assert (repo / "docs/prd/orders/README.md").read_bytes() == _b(README_BASE + "\n" + "# Mine\n\nold text\n")


@steps("N0")
def test_t237_5_block_replaced(repo):
    """@prd T-237.5"""
    write_files({
        repo / "CLAUDE.md": "top\r\n\n<!-- prd-toolkit:start -->\nold\n<!-- prd-toolkit:end -->\r\nafter\r\n",
        repo / "docs/prd/orders/README.md": "# Mine\n<!-- prd-toolkit:start -->\nold\n<!-- prd-toolkit:end -->",
    })
    r = block(repo, RUN)
    assert r.exit == 0, r.stderr
    assert (repo / "CLAUDE.md").read_bytes() == _b("top\r\n\n" + CLAUDE_BASE[:-1] + "\r\nafter\r\n")
    assert (repo / "docs/prd/orders/README.md").read_bytes() == _b("# Mine\n" + README_BASE[:-1])


@steps("N0", "SB0")
def test_t237_6_nothing_to_write(repo):
    """@prd T-237.6"""
    files = [repo / "CLAUDE.md", repo / "docs/prd/orders/README.md", repo / "docs/prd/README.md"]
    before = snapshot(*files)
    r = block(repo, RUN)
    assert (r.exit, r.out, r.err) == (0, b"", b"")
    assert snapshot(*files) == before


SF1_TEXT = "# Docs\n\n```\n<!-- prd-toolkit:start -->\nexample\n<!-- prd-toolkit:end -->\n```\n"
SF2_TEXT = "# D\n\n```\nunclosed example\n"


@steps("N0", "SF1")
def test_t238_1_marker_in_closed_fence(repo):
    """@prd T-238.1"""
    r = block(repo, RUN)
    assert r.exit == 0, r.stderr
    assert (repo / "CLAUDE.md").read_bytes() == _b(SF1_TEXT + "\n" + CLAUDE_BASE)


@steps("N0", "SF2")
def test_t238_2_unclosed_fence(repo):
    """@prd T-238.2"""
    r1 = block(repo, RUN)
    after_1 = (repo / "CLAUDE.md").read_bytes()
    r2 = block(repo, RUN)
    after_2 = (repo / "CLAUDE.md").read_bytes()
    r3 = block(repo, RUN + " --check")
    for r in (r1, r2, r3):
        assert r.exit == 0, r.stderr
    assert r3.out == b""
    assert after_1 == _b(SF2_TEXT + "\n" + CLAUDE_BASE)
    assert after_2 == after_1


@steps("N0", "SX1")
def test_t238_3_two_start_markers(repo):
    """@prd T-238.3"""
    readme = repo / "docs/prd/orders/README.md"
    before = snapshot(readme)
    r = block(repo, RUN)
    assert r.exit == 2
    assert r.out == b""
    assert r.err == _b(f"prd_block: {rtmp(repo)}/docs/prd/orders/README.md: more than one prd-toolkit block\n")
    assert snapshot(readme) == before
    assert absent(repo / "CLAUDE.md")
    assert absent(repo / "docs/prd/README.md")


UNBALANCED = "prd-toolkit start and end markers are unbalanced"


@steps("N0", "SX2")
def test_t238_4_start_without_end(repo):
    """@prd T-238.4"""
    claude = repo / "CLAUDE.md"
    before = snapshot(claude)
    r = block(repo, RUN)
    assert r.exit == 2
    assert r.out == b""
    assert r.err == _b(f"prd_block: {rtmp(repo)}/CLAUDE.md: {UNBALANCED}\n")
    assert snapshot(claude) == before
    assert absent(repo / "docs/prd/orders/README.md")
    assert absent(repo / "docs/prd/README.md")


@steps("N0", "SX3")
def test_t238_5_end_before_start(repo):
    """@prd T-238.5"""
    claude = repo / "CLAUDE.md"
    before = snapshot(claude)
    r = block(repo, RUN)
    assert r.exit == 2
    assert r.err == _b(f"prd_block: {rtmp(repo)}/CLAUDE.md: {UNBALANCED}\n")
    assert snapshot(claude) == before


@steps("N0", "SY")
def test_t239_1_symbolic_link(repo):
    """@prd T-239.1"""
    r = block(repo, RUN)
    assert r.exit == 0, r.stderr
    claude = repo / "CLAUDE.md"
    assert claude.is_symlink() and os.readlink(claude) == "real.md"
    assert (repo / "real.md").read_bytes() == _b("# Agents\n" + "\n" + CLAUDE_BASE)


@steps("N0", "SMODE")
def test_t239_2_mode_kept(repo):
    """@prd T-239.2"""
    r = block(repo, RUN)
    assert r.exit == 0, r.stderr
    readme = repo / "docs/prd/orders/README.md"
    assert readme.read_bytes() == _b(README_BASE + "\n" + "# Mine\n")
    assert readme.stat().st_mode & 0o7777 == 0o640


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps("N0")
def test_t239_3_mode_from_umask(repo):
    """@prd T-239.3 known-failing E-070"""
    claude = repo / "CLAUDE.md"
    assert absent(claude)
    old = os.umask(0o022)
    try:
        r = block(repo, RUN)
    finally:
        os.umask(old)
    if claude.exists() and claude.stat().st_mode & 0o7777 == 0o600:
        raise KnownFailure("the created CLAUDE.md has mode 0o600")
    assert r.exit == 0, r.stderr
    assert claude.stat().st_mode & 0o7777 == 0o644
