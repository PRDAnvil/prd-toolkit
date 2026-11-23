"""The Deployed part (FR-233; test-cases/status.yaml)."""
from __future__ import annotations

from status_support import part_lines, repo, status, steps  # noqa: F401


def _deployed(repo) -> list[str]:
    r = status(repo, "python STATUS .")
    assert r.exit == 0, r.stderr
    return part_lines(r.stdout, "Deployed")


PRODUCTION = "production: 1.0.0 at 3f2c1a9, 2026-11-02"
FAILED = "staging: run 20261110T090000Z-all stopped (failed) at step 1"
NONE = ["## Deployed", "", "None.", ""]


@steps("N0", "SD0", "SD1")
def test_t233_1_row(repo):
    """@prd T-233.1"""
    assert _deployed(repo) == ["## Deployed", "", PRODUCTION, ""]


@steps("N0", "SD0", "SD3", "SD1")
def test_t233_2_row_order(repo):
    """@prd T-233.2"""
    assert _deployed(repo) == ["## Deployed", "", PRODUCTION, "qa: 1.0.0 at abc1234, 2026-11-03", ""]


@steps("N0", "NR1")
def test_t233_3_failed_run(repo):
    """@prd T-233.3"""
    assert _deployed(repo) == ["## Deployed", "", FAILED, ""]


@steps("N0", "NR2")
def test_t233_4_unfinished_run(repo):
    """@prd T-233.4"""
    assert _deployed(repo) == [
        "## Deployed", "", "staging: run 20261110T100000Z-all stopped (unfinished) at step 1", ""]


@steps("N0", "NR3")
def test_t233_5_human_step(repo):
    """@prd T-233.5"""
    assert _deployed(repo) == [
        "## Deployed", "", "production: run 20261111T090000Z-all stopped (human) at step 2", ""]


@steps("N0", "SD0", "SD1", "NR1")
def test_t233_6_run_line_and_row(repo):
    """@prd T-233.6"""
    assert _deployed(repo) == ["## Deployed", "", FAILED, PRODUCTION, ""]


@steps("N0", "SD0", "SD2", "NR1")
def test_t233_7_older_run_not_read(repo):
    """@prd T-233.7"""
    assert _deployed(repo) == ["## Deployed", "", "staging: 1.0.0 at 3f2c1a9, 2026-11-12", ""]


@steps("N0", "NR1", "SG1")
def test_t233_8_newer_run_finished(repo):
    """@prd T-233.8"""
    assert _deployed(repo) == NONE


@steps("N0", "NR1", "NR4")
def test_t233_9_unreadable_log_skipped(repo):
    """@prd T-233.9"""
    assert _deployed(repo) == ["## Deployed", "", FAILED, ""]


@steps("N0", "SG2")
def test_t233_10_other_prd_log_skipped(repo):
    """@prd T-233.10"""
    assert _deployed(repo) == NONE


@steps("N0")
def test_t233_11_none(repo):
    """@prd T-233.11"""
    assert _deployed(repo) == NONE
