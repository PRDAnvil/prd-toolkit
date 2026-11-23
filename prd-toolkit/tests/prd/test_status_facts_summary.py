"""§2's summary paragraph, first sentence, Principles and Getting started (FR-247, FR-248; test-cases/status.yaml)."""
from __future__ import annotations

import pytest

from status_support import KnownFailure, as_json, facts, repo, steps  # noqa: F401 (facts and repo are fixtures)

SUMMARY = "The orders service imports order files and prints monthly reports."


@steps("N0")
def test_t247_1_summary(repo, facts):
    """@prd T-247.1"""
    F = facts(repo)
    assert as_json({"summary": F.summary, "first_sentence": F.first_sentence}) == {
        "summary": SUMMARY, "first_sentence": SUMMARY}


@steps("N0", "SS1")
def test_t247_2_summary_lines(repo, facts):
    """@prd T-247.2"""
    assert as_json(facts(repo).summary) == "The orders service imports order files. It prints\nmonthly reports."


@steps("N0", "SS2")
def test_t247_3_no_summary(repo, facts):
    """@prd T-247.3"""
    F = facts(repo)
    assert as_json({"summary": F.summary, "first_sentence": F.first_sentence}) == {
        "summary": None, "first_sentence": ""}


@steps("N0", "SS1")
def test_t247_4_first_sentence(repo, facts):
    """@prd T-247.4"""
    assert as_json(facts(repo).first_sentence) == "The orders service imports order files."


@steps("N0", "SS6")
def test_t247_5_first_sentence_question(repo, facts):
    """@prd T-247.5"""
    assert as_json(facts(repo).first_sentence) == "Does it import files?"


@pytest.mark.xfail(strict=True, raises=KnownFailure)
@steps("N0", "SS9")
def test_t247_6_comment_inside_line(repo, facts):
    """@prd T-247.6 known-failing E-071"""
    value = as_json(facts(repo).summary)
    if value == "Intro" + " " * 15 + "text":
        raise KnownFailure("the comment's width is left as spaces")
    assert value == "Intro  text"


@steps("N0", "SS3")
def test_t248_1_principles_getting_started(repo, facts):
    """@prd T-248.1"""
    F = facts(repo)
    assert as_json({"principles": F.principles, "getting_started": F.getting_started, "summary": F.summary}) == {
        "principles": "Keep it small.\n\n- **Plain.** One command, one answer.",
        "getting_started": "1. Install the service.\n2. Import a file.",
        "summary": SUMMARY,
    }


@steps("N0")
def test_t248_2_no_parts(repo, facts):
    """@prd T-248.2"""
    F = facts(repo)
    assert as_json({"principles": F.principles, "getting_started": F.getting_started}) == {
        "principles": None, "getting_started": None}
