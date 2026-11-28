"""FR-283: the prd-status command runs prd status once and prints the report (test-cases/commands.yaml)."""
from __future__ import annotations

from commands_support import body, flat, missing, present, step


def test_status_body_starts_with_arguments():
    """@prd T-283.1"""
    text = flat(body("prd-status"))
    assert text.startswith("Print the prd-toolkit status report. Arguments: $ARGUMENTS"), text[:200]


def test_status_step_2_runs_prd_status_once_unfiltered():
    """@prd T-283.2"""
    text = flat(step("prd-status", 2))
    assert missing(text, [
        'Run the script in one Bash call, with the literal PRD folder: `<scripts>/prd status docs/prd/<slug>; echo "prd-status-exit=$?"`',
        "Add `--json` only when asked for JSON.",
        "Never pipe, filter or truncate the output (no `| head`, no `| grep`)",
    ]) == [], text


def test_status_step_3_prints_report_and_names_parts():
    """@prd T-283.3"""
    text = flat(step("prd-status", 3))
    assert missing(text, [
        "Print the output as it is.",
        "The report starts with the part Next, the ordered list of what the PRD needs, each item with its command when a command does it; then Header, Requirements, Areas, Adoption map, Not built, Not verified, Open errors, Upstreams, Consumers, Change sets, CI, Deployed and Matrix.",
        "A vendored copy older than 0.8.10 prints no Next part.",
        "The script changes nothing itself; to find the Next items it runs lint, which runs the PRD's section 7 validator commands.",
    ]) == [], text


def test_status_step_4_reads_exit_2_by_cause():
    """@prd T-283.4"""
    text = flat(step("prd-status", 4))
    problems = [f"lacks {m!r}" for m in missing(text, ["prd-status-exit=2", "path", "unmigrated", "internal error"])]
    problems += [f"holds {h!r}" for h in present(text, ["nothing printed"])]
    assert problems == [], text
