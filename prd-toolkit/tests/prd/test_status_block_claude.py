"""The CLAUDE.md block and its change line (FR-235, FR-236; test-cases/status.yaml)."""
from __future__ import annotations

import pytest

from status_support import CLAUDE_BASE, KnownFailure, assert_lines_in_order, block, file_lines, repo, steps  # noqa: F401

GAP = "- Gap rule: if the PRD is silent on what you need, stop and raise it with"


def _run(repo):
    r = block(repo, "python BLOCK docs/prd/orders")
    assert r.exit == 0, r.stderr
    return file_lines(repo / "CLAUDE.md")


@steps("N0")
def test_t235_1_block(repo):
    """@prd T-235.1"""
    r = block(repo, "python BLOCK docs/prd/orders")
    assert (r.exit, r.out, r.err) == (0, b"", b"")
    assert (repo / "CLAUDE.md").read_bytes() == CLAUDE_BASE.encode("utf-8")


@steps("N0", "SR6")
def test_t235_2_required_skills(repo):
    """@prd T-235.2"""
    lines = _run(repo)
    assert_lines_in_order(lines, ["Required skills:", "- `superpowers:test-driven-development` for a code change", "",
                                  "Adopted areas: all (new project)"])
    assert not [line for line in lines if "code-review" in line]


@steps("N0", "NA1")
def test_t235_3_adopted_areas(repo):
    """@prd T-235.3"""
    assert_lines_in_order(_run(repo), ["Adopted areas: import, reports", "<!-- prd-toolkit:end -->"])


@steps("N0", "S8")
def test_t235_4_adopted_none_yet(repo):
    """@prd T-235.4"""
    assert_lines_in_order(_run(repo), ["Adopted areas: none yet", "<!-- prd-toolkit:end -->"])


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps("N0", "SR8")
def test_t235_5_placeholder_in_value(repo):
    """@prd T-235.5 known-failing E-069"""
    r = block(repo, "python BLOCK docs/prd/orders")
    claude = repo / "CLAUDE.md"
    if claude.exists() and \
            "- `superpowers:test-driven-development` for a change to all (new project)" in file_lines(claude):
        raise KnownFailure("CLAUDE.md holds the skill line with {{adopted_areas}} replaced")
    assert r.exit == 0, r.stderr
    assert_lines_in_order(file_lines(claude), [
        "Required skills:", "- `superpowers:test-driven-development` for a change to {{adopted_areas}}", "",
        "Adopted areas: all (new project)"])


@steps("N0")
def test_t236_1_change_line(repo):
    """@prd T-236.1"""
    assert_lines_in_order(_run(repo), [
        "- Every behaviour change starts with `/prd-toolkit:prd-change` (`prd-toolkit:changing-prds`), before code.",
        GAP])


@steps("N0", "SK1")
def test_t236_2_change_line_links(repo):
    """@prd T-236.2"""
    assert_lines_in_order(_run(repo), [
        "- Every behaviour change starts with `/prd-toolkit:prd-change`, before code;",
        "  one to a cited item, with `/prd-toolkit:prd-change-set`.", GAP])


@steps("N0", "NA1")
def test_t236_3_change_line_adopted(repo):
    """@prd T-236.3"""
    assert_lines_in_order(_run(repo), [
        "  lacks.", "- Every behaviour change in an adopted area starts with `/prd-toolkit:prd-change`, before code.",
        GAP])


@steps("N0", "NA1", "SK1")
def test_t236_4_change_line_adopted_links(repo):
    """@prd T-236.4"""
    assert_lines_in_order(_run(repo), [
        "  lacks.",
        "- Every behaviour change in an adopted area starts with `/prd-toolkit:prd-change`, before code; one",
        "  to a cited item, with `/prd-toolkit:prd-change-set`.", GAP])
