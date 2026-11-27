"""FR-285, FR-286, FR-287: prd-new, prd-adopt and prd-change hand the run to a skill (test-cases/commands.yaml)."""
from __future__ import annotations

from commands_support import body, flat, missing


def test_new_body_is_the_handoff():
    """@prd T-285.2"""
    assert flat(body("prd-new")) == (
        "Invoke the prd-toolkit:authoring-prds skill and follow it exactly. "
        "$ARGUMENTS, when given, is the project slug."
    )


def test_adopt_body_is_the_handoff():
    """@prd T-286.2"""
    assert flat(body("prd-adopt")) == (
        "Invoke the prd-toolkit:adopting-prds skill and follow it exactly. "
        "$ARGUMENTS, when given, is the area to adopt."
    )


def test_change_body_invokes_changing_prds():
    """@prd T-287.2"""
    text = flat(body("prd-change"))
    assert text.startswith(
        "Invoke the prd-toolkit:changing-prds skill and follow it exactly. Arguments: $ARGUMENTS"
    ), text[:200]
    assert missing(text, ["Otherwise the arguments are the change to make."]) == [], text


def test_change_body_states_review_mode():
    """@prd T-287.3"""
    text = flat(body("prd-change"))
    assert missing(text, [
        "When the arguments begin with `--review <dir>`, this is review mode: read `${CLAUDE_PLUGIN_ROOT}/skills/changing-prds/reviewing-a-change.md` whole and follow it, not the skill's five steps.",
        "Review mode edits nothing.",
        "`<dir>` is the PRD folder, and a `--base <ref>` after it is the base.",
        "Any other words are a request the review answers in its report, never an edit, whatever they ask for.",
    ]) == [], text
