"""FR-284: the prd-context command maps its arguments and prints the pack (test-cases/commands.yaml)."""
from __future__ import annotations

import pytest

from commands_support import body, flat, known_failure, missing, present, step

# E-097's symptom, as T-284.6's `symptom:` states it: a substring of flat(STEP(prd-context, 2)).
E097_SYMPTOM = "find the area each ID's block lives in from the repo pack, or ask"


def test_context_body_starts_with_arguments():
    """@prd T-284.1"""
    text = flat(body("prd-context"))
    assert text.startswith("Print the prd-toolkit context pack. Arguments: $ARGUMENTS"), text[:200]


def test_context_step_2_maps_arguments():
    """@prd T-284.2"""
    text = flat(step("prd-context", 2))
    assert missing(text, [
        "A token that starts with `UJ-`, `FR-`, `NFR-`, `AC-`, `T-` or `E-` is an ID, never the area.",
        "The first argument that is neither an ID nor `implement` is the area: pass it as `--area <area>`.",
        "Pass only UJ, FR, NFR and E IDs, together as one `--req <ID>[,<ID>…]`",
        "an AC or T id maps to its FR (`AC-005.2` and `T-005.1` map to `FR-005`), and an `E-nnn` passes as it is",
        "The word `implement` becomes `--for implement`.",
        "With no area and no IDs, the pack is the repo pack: the stack and one line per area.",
    ]) == [], text


def test_context_step_3_runs_prd_context_once_unfiltered():
    """@prd T-284.3"""
    text = flat(step("prd-context", 3))
    assert missing(text, [
        'Run the script in one Bash call, with the literal PRD folder: `<scripts>/prd context docs/prd/<slug> --area <area> --req <IDs> --for implement; echo "prd-context-exit=$?"`',
        "Leave out the options the arguments did not give.",
        "`--req` and `--for implement` both need `--area`.",
        "Never pipe, filter or truncate the pack's output (no `| head`, no `| grep`)",
    ]) == [], text


def test_context_steps_4_and_5_print_and_reread_stale():
    """@prd T-284.4"""
    step4 = flat(step("prd-context", 4))
    step5 = flat(step("prd-context", 5))
    assert missing(step4, ["Print the output as it is, and work from it."]) == [], step4
    assert missing(step5, [
        "On `prd-context-exit=1`, at least one source is STALE: re-read the regions marked STALE before relying on them.",
    ]) == [], step5


def test_context_step_5_reads_exit_2_by_cause():
    """@prd T-284.5"""
    text = flat(step("prd-context", 5))
    problems = [f"lacks {m!r}" for m in missing(text, ["prd-context-exit=2", "arguments", "unmigrated", "internal error"])]
    problems += [f"holds {h!r}" for h in present(text, ["nothing printed"])]
    assert problems == [], "; ".join(problems) + " | " + text


@pytest.mark.xfail(strict=True, raises=pytest.xfail.Exception)
def test_context_step_2_finds_area_from_features_file():
    """@prd T-284.6 known-failing E-097"""
    text = flat(step("prd-context", 2))
    problems = [f"lacks {m!r}" for m in missing(text, ["features/<area>.md", "`### <ID>`"])]
    problems += [f"holds {h!r}" for h in present(text, ["from the repo pack"])]
    known_failure(problems, E097_SYMPTOM in text, "flat(STEP(prd-context, 2)) holds " + repr(E097_SYMPTOM))
