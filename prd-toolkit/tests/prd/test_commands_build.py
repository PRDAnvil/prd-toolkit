"""FR-288: the prd-build command reads the build procedure first and maps its arguments (test-cases/commands.yaml)."""
from __future__ import annotations

import pytest

from commands_support import body, flat, known_failure, missing, present, step

# E-097's symptom, as T-288.7's `symptom:` states it: a substring of flat(STEP(prd-build, 4)).
E097_SYMPTOM = "find the area each ID's block lives in from the repo pack, or ask"


def test_build_body_names_arguments():
    """@prd T-288.1"""
    text = flat(body("prd-build"))
    assert text.startswith(
        "Build an approved PRD change. Arguments, `<area> <IDs> [--fixes E-nnn]`: $ARGUMENTS"
    ), text[:200]


def test_build_step_1_reads_procedure_first():
    """@prd T-288.2"""
    text = flat(step("prd-build", 1))
    assert text.startswith(
        "1. Before anything else, make a Read of `${CLAUDE_PLUGIN_ROOT}/skills/building-from-prds/running-a-build.md`, whole (no offset, no limit)."
    ), text
    assert missing(text, ["Run no test, read no code and dispatch no agent before it."]) == [], text


def test_build_step_2_invokes_skill_as_caller():
    """@prd T-288.3"""
    text = flat(step("prd-build", 2))
    assert missing(text, [
        "Invoke the prd-toolkit:building-from-prds skill for the caller's Red Flags.",
        "You are the caller: the Read its opening asks for is the one in step 1, and you never write the code or the tests yourself.",
    ]) == [], text


def test_build_step_4_maps_arguments_to_one_req():
    """@prd T-288.4"""
    text = flat(step("prd-build", 4))
    assert missing(text, [
        "Map the arguments as `/prd-toolkit:prd-context` does.",
        "A token that starts with `UJ-`, `FR-`, `NFR-`, `AC-`, `T-` or `E-` is an ID; the first other token is the area.",
        "An AC or T-id maps to its FR (`AC-005.2` and `T-005.1` map to `FR-005`); an `E-nnn` passes as it is.",
        "The IDs are joined with commas for `--req`, as `--req FR-006,FR-001`, never space-separated: a space-separated list is a usage error (exit 2).",
        "With no IDs, ask: a build never guesses its scope.",
    ]) == [], text


def test_build_step_4_states_fixes():
    """@prd T-288.5"""
    text = flat(step("prd-build", 4))
    assert missing(text, [
        "`--fixes E-nnn` builds the fix for a confirmed entry.",
        "The E-nnn also goes to `--req`; step 1 of the procedure runs `prd_error.py list <prd> --open` and refuses unless the entry is `confirmed`.",
    ]) == [], text


def test_build_step_5_follows_procedure():
    """@prd T-288.6"""
    text = flat(step("prd-build", 5))
    assert missing(text, [
        "Follow `${CLAUDE_PLUGIN_ROOT}/skills/building-from-prds/running-a-build.md` exactly, steps 1 to 8, and report as its close says.",
    ]) == [], text


@pytest.mark.xfail(strict=True, raises=pytest.xfail.Exception)
def test_build_step_4_finds_area_from_features_file():
    """@prd T-288.7 known-failing E-097"""
    text = flat(step("prd-build", 4))
    problems = [f"lacks {m!r}" for m in missing(text, ["features/<area>.md", "`### <ID>`"])]
    problems += [f"holds {h!r}" for h in present(text, ["from the repo pack"])]
    known_failure(problems, E097_SYMPTOM in text, "flat(STEP(prd-build, 4)) holds " + repr(E097_SYMPTOM))
