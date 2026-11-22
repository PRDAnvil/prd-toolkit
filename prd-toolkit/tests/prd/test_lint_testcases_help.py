"""The help entries of the lint-testcases rules (test-cases/lint-testcases.yaml, T-169.*)."""

from __future__ import annotations

from pathlib import Path

import pytest

from lint_testcases_support import HELP, Run, check


@pytest.fixture
def help_runs(request, tmp_path: Path) -> list[Run]:
    """Run HELP once per argument list, with <tmp> as the working directory; the test body only asserts."""
    return [HELP(tmp_path, *args) for args in request.param]


RULES = [
    "ac-has-test",
    "test-cases-consistent",
    "test-level",
    "sufficiency",
    "judged-case",
    "test-refs",
    "deny-tested",
    "classified-fixtures",
]


def first_line(run: Run) -> str | None:
    lines = run.stdout.splitlines()
    return lines[0] if lines else None


def second_line(run: Run) -> str | None:
    lines = run.stdout.splitlines()
    return lines[1] if len(lines) > 1 else None


@pytest.mark.parametrize("help_runs", [[["--rule", r] for r in RULES]], indirect=True)
def test_rule_heads(help_runs):
    """@prd T-169.1"""
    for rule, run in zip(RULES, help_runs):
        check(run, {"exit": 0, "stderr": ""})
        assert first_line(run) == f"{rule} (error)", f"--rule {rule}: first line {first_line(run)!r}\nstdout:\n{run.stdout}"


def _assert_second(run: Run, text: str) -> None:
    check(run, {"exit": 0, "stderr": ""})
    assert second_line(run) == text, f"second line {second_line(run)!r}\nstdout:\n{run.stdout}"


@pytest.mark.parametrize("help_runs", [[["--rule", "ac-has-test"]]], indirect=True)
def test_help_ac_has_test(help_runs):
    """@prd T-169.2"""
    _assert_second(help_runs[0], "Checks that every live acceptance criterion of a requirement that is not removed has at least one test case whose ac: names it. Add a case to the area's test-cases file with ac: set to that AC.")


@pytest.mark.parametrize("help_runs", [[["--rule", "test-cases-consistent"]]], indirect=True)
def test_help_test_cases_consistent(help_runs):
    """@prd T-169.3"""
    _assert_second(help_runs[0], "Checks that each block's Tests line names its test-cases file, that the file exists and holds an entry for every T-id listed, at the level the line gives, and that every test case is cited by a Tests line naming its file. End the Tests line with (test-cases/<area>.yaml) for a file that exists, add the missing entry or Tests item, or make the level on the line and in the case agree.")


@pytest.mark.parametrize("help_runs", [[["--rule", "test-level"]]], indirect=True)
def test_help_test_level(help_runs):
    """@prd T-169.4"""
    _assert_second(help_runs[0], "Checks that testing.md's Levels table has a Gate column whose values are build or deploy, that no build-gate Harness command would collect a deploy-gate level's tests, and that each test case's level: is a row of that table. Add the level or the Gate value, or exclude the deploy-gate path from the build command with --ignore.")


@pytest.mark.parametrize("help_runs", [[["--rule", "sufficiency"]]], indirect=True)
def test_help_sufficiency(help_runs):
    """@prd T-169.5"""
    _assert_second(help_runs[0], "Checks that each test-cases file parses as YAML mapping each T-id to a mapping, and that each case has the eight sufficiency elements: ac, level, environment and identity as strings, target as <kind>:<name> of a known kind, preconditions as a list, a non-empty input, and expect with output (unless judged), effects and errors lists and leaks; an acceptance case also needs steps: and signoff:. Fix the YAML, or fill the element the message names in its form, with a target kind that is built in, a pack's, or a section 7 custom type. An entry named .md or .yaml in the PRD folder that is not a file is reported here too; rename or remove it.")


@pytest.mark.parametrize("help_runs", [[["--rule", "judged-case"]]], indirect=True)
def test_help_judged_case(help_runs):
    """@prd T-169.6"""
    _assert_second(help_runs[0], "Checks a judged case's expect: rubric a non-empty list of distinct non-empty strings, threshold a number in (0, 1], runs an integer of at least 1, and no output beside rubric; it warns when a threshold below 1.0 still needs every rubric item. Fix the key the message names, or lower the threshold to allow one miss.")


@pytest.mark.parametrize("help_runs", [[["--rule", "test-refs"]]], indirect=True)
def test_help_test_refs(help_runs):
    """@prd T-169.7"""
    _assert_second(help_runs[0], "Checks that each test case's references resolve: ac names an AC of the requirement its T-id is numbered for, preconditions name fixtures in testing.md and contracts/fixtures/ or mock services in contracts/dependencies/, input.file, error codes, refs entries, environment, identity and target exist, known-failing names an open errors.md entry and has a symptom: beside it (a warning when it has none), and a symptom: has a known-failing: beside it. Point the reference at something that exists or add what it names; delete a known-failing: line whose entry is resolved, and a symptom: with no known-failing: beside it.")


@pytest.mark.parametrize("help_runs", [[["--rule", "deny-tested"]]], indirect=True)
def test_help_deny_tested(help_runs):
    """@prd T-169.8"""
    _assert_second(help_runs[0], "Checks that every deny cell of contracts/permissions.yaml has a role with a test identity and a test case with target op:<operation>, that identity and a non-empty expect.errors. Give the role an identity, or add the case that proves the denial.")


@pytest.mark.parametrize("help_runs", [[["--rule", "classified-fixtures"]]], indirect=True)
def test_help_classified_fixtures(help_runs):
    """@prd T-169.9"""
    _assert_second(help_runs[0], "Checks that no fixture file under contracts/fixtures/ holds a real-looking email, phone number or SSN in a column contracts/data-classification.yaml classifies pii, and that no test case's inline input holds one in any value. Use a synthetic form: an example.com address, a 555-01xx phone number, or an SSN starting 000, 666 or 9.")
