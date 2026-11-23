"""The Upstreams, Consumers, Change sets and CI parts (FR-230 to FR-232; test-cases/status.yaml)."""
from __future__ import annotations

from status_support import absent, part_lines, repo, rtmp, status, steps  # noqa: F401

NONE = ["", "None.", ""]


def _report(repo, **kw):
    r = status(repo, "python STATUS .", **kw)
    assert r.exit == 0, r.stderr
    return r


@steps("N0")
def test_t230_1_no_links(repo):
    """@prd T-230.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Upstreams") == ["## Upstreams", *NONE]
    assert part_lines(r.stdout, "Consumers") == ["## Consumers", *NONE]


@steps("N0", "SK1")
def test_t230_2_git_url_upstream(repo):
    """@prd T-230.2"""
    r = _report(repo, env={"XDG_CACHE_HOME": str(repo / "cache")})
    assert part_lines(r.stdout, "Upstreams") == [
        "## Upstreams", "",
        "greet 1.1.0 at 4f1c9a2, needs default, check: not run (git URL; run prd_links.py check)", ""]
    assert absent(repo / "cache")


@steps("N0", "SK2")
def test_t230_3_unreachable_path_upstream(repo):
    """@prd T-230.3"""
    r = _report(repo)
    assert part_lines(r.stdout, "Upstreams") == ["## Upstreams", "", "billing 1.0.0 at abc1234, needs verified", ""]
    assert part_lines(r.stdout, "Consumers") == ["## Consumers", *NONE]


@steps("N0", "SK3")
def test_t230_4_self_link(repo):
    """@prd T-230.4"""
    r = _report(repo)
    assert part_lines(r.stdout, "Upstreams") == [
        "## Upstreams", "",
        "orders 1.0.0 at abc1234, needs default, check: error (a PRD cannot link to itself)", ""]


@steps("N0", "SK1")
def test_t230_5_consumers(repo):
    """@prd T-230.5"""
    r = _report(repo)
    assert part_lines(r.stdout, "Consumers") == [
        "## Consumers", "", "dashboards git@example.com:org/bi.git#docs/prd/dashboards", ""]


@steps("N0", "SC1")
def test_t231_1_change_sets(repo):
    """@prd T-231.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Change sets") == [
        "## Change sets", "", "CS-001 running: billing approved; orders proposed", ""]


STALE = ["stale: CLAUDE.md; run prd_block.py docs/prd/orders",
         "stale: docs/prd/orders/README.md; run prd_block.py docs/prd/orders",
         "stale: docs/prd/README.md; run prd_block.py docs/prd/orders"]


@steps("N0")
def test_t232_1_ci_stale(repo):
    """@prd T-232.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "CI") == ["## CI", "", *STALE, ""]


@steps("N0", "SB0")
def test_t232_2_ci_none(repo):
    """@prd T-232.2"""
    r = _report(repo)
    assert part_lines(r.stdout, "CI") == ["## CI", *NONE]


@steps("N0", "SG3")
def test_t232_3_ci_ignored_claude_md(repo):
    """@prd T-232.3"""
    r = _report(repo)
    assert part_lines(r.stdout, "CI") == ["## CI", "", *STALE[1:], ""]


@steps("N0X")
def test_t232_4_ci_no_checkout(repo):
    """@prd T-232.4"""
    r = _report(repo)
    assert part_lines(r.stdout, "CI") == [
        "## CI", "", f"{rtmp(repo)}/docs/prd/orders is not inside a git checkout", ""]
    assert part_lines(r.stdout, "Deployed") == ["## Deployed", *NONE]
