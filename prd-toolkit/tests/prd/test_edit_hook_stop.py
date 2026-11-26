"""edit-hook, FR-279: the Stop tier reports lint's new error findings for the PRD folders the session edited.

Every input and expected value is test-cases/edit-hook.yaml's. Each case's preconditions name
lint-cli/plugins_superpowers, so `given(..., plugins=True)` sets PRD_PLUGINS_FILE and warms the launcher up.
"""
from edit_hook_support import (  # noqa: F401  (edit_case is a fixture)
    additional_context,
    assert_text,
    each_run,
    edit_case,
    given,
    stdout_json,
    stdout_json_at,
)

POST = "python <repo>/prd-toolkit/scripts/prd_edit_hook.py post"
STOP = "python <repo>/prd-toolkit/scripts/prd_edit_hook.py stop"
HEADER_ORDERS = "prd-toolkit: prd lint fails on docs/prd/orders after this session's edits:"
HEADER_ORDERS2 = "prd-toolkit: prd lint fails on docs/prd/orders2 after this session's edits:"
FINISH = "Finish the PRD edit through /prd-toolkit:prd-change, which runs lint itself."


def _edit(path: str, tool: str = "Edit", session: str = "<sid>") -> dict:
    return {"session_id": session, "cwd": "<tmp>", "tool_name": tool, "tool_input": {"file_path": path}}


def _stop(session: str = "<sid>", **extra) -> dict:
    return {"session_id": session, "cwd": "<tmp>", "hook_event_name": "Stop", **extra}


@given("H0", "NL1", plugins=True)
def test_stop_reports_the_error_findings_of_an_edited_folder(edit_case):
    """@prd T-279.1"""
    r1 = edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders/contracts/errors.yaml"))
    r2 = edit_case.run(STOP, stdin=_stop(stop_hook_active=False))
    each_run([r1, r2])
    assert_text(r1.stdout, "")
    stdout_json_at(r2.stdout, {"hookSpecificOutput.hookEventName": "Stop"})
    lines = additional_context(r2.stdout).splitlines()
    assert lines[0] == HEADER_ORDERS, lines
    assert lines[-1] == FINISH, lines
    middle = lines[1:-1]
    assert all(line.startswith("docs/prd/orders/") for line in middle), middle
    assert not any(": warn: " in line for line in middle), middle
    assert any(line.startswith("docs/prd/orders/contracts/errors.yaml:9: ") for line in middle), middle


@given("H0", "NL1", plugins=True)
def test_only_an_edit_inside_a_prd_folder_notes_it(edit_case):
    """@prd T-279.2"""
    results = [
        edit_case.run(POST, stdin=_edit("<tmp>/src/app.py")),
        edit_case.run(STOP, stdin=_stop()),
        edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders/prd.md", tool="MultiEdit")),
        edit_case.run(STOP, stdin=_stop()),
    ]
    each_run(results)
    assert_text(results[0].stdout, "")
    assert_text(results[1].stdout, "")
    assert_text(results[2].stdout, "")
    stdout_json_at(results[3].stdout, {"hookSpecificOutput.hookEventName": "Stop"})
    assert additional_context(results[3].stdout).splitlines()[0] == HEADER_ORDERS


@given("H0", "NL1", "H2", plugins=True)
def test_two_folders_are_reported_in_path_order_joined_by_an_empty_line(edit_case):
    """@prd T-279.3"""
    results = [
        edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders2/prd.md")),
        edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders/prd.md")),
        edit_case.run(STOP, stdin=_stop()),
    ]
    each_run(results)
    stdout_json_at(results[2].stdout, {"hookSpecificOutput.hookEventName": "Stop"})
    lines = additional_context(results[2].stdout).splitlines()
    assert lines.count("") == 1, lines
    empty = lines.index("")
    before, after = lines[:empty], lines[empty + 1:]
    assert before and before[0] == HEADER_ORDERS, before
    assert after and after[0] == HEADER_ORDERS2, after
    assert any(line.startswith("docs/prd/orders2/prd.md:2: frontmatter: ") for line in after), after
    assert before[-1] == FINISH, before
    assert after[-1] == FINISH, after


@given("H0", "NL1", plugins=True)
def test_a_finding_is_told_once_per_session(edit_case):
    """@prd T-279.4"""
    errors_yaml = "<tmp>/docs/prd/orders/contracts/errors.yaml"
    results = [
        edit_case.run(POST, stdin=_edit(errors_yaml)),
        edit_case.run(STOP, stdin=_stop()),
        edit_case.run(POST, stdin=_edit(errors_yaml)),
        edit_case.run(STOP, stdin=_stop()),
        edit_case.run(POST, stdin=_edit(errors_yaml, session="<sid2>")),
        edit_case.run(STOP, stdin=_stop(session="<sid2>")),
    ]
    each_run(results)
    stdout_json_at(results[1].stdout, {"hookSpecificOutput.hookEventName": "Stop"})
    assert_text(results[3].stdout, "")
    stdout_json_at(results[5].stdout, {"hookSpecificOutput.hookEventName": "Stop"})
    assert results[5].stdout == results[1].stdout


@given("H0", plugins=True)
def test_a_clean_lint_says_nothing(edit_case):
    """@prd T-279.5"""
    results = [
        edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders/prd.md")),
        edit_case.run(STOP, stdin=_stop()),
    ]
    each_run(results, stdout="")


@given("H0", "HB", plugins=True)
def test_a_lint_that_cannot_run_is_reported_once(edit_case):
    """@prd T-279.6"""
    prd_md = "<tmp>/docs/prd/orders/prd.md"
    results = [
        edit_case.run(POST, stdin=_edit(prd_md)),
        edit_case.run(STOP, stdin=_stop()),
        edit_case.run(POST, stdin=_edit(prd_md)),
        edit_case.run(STOP, stdin=_stop()),
    ]
    each_run(results)
    assert stdout_json(results[1].stdout) == {"hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": "prd-toolkit: prd lint could not run on docs/prd/orders: stub lint broke"}}
    assert_text(results[3].stdout, "")


@given("H0", "HG", plugins=True)
def test_a_stop_with_nothing_edited_since_runs_no_lint(edit_case):
    """@prd T-279.7"""
    results = [
        edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders/prd.md")),
        edit_case.run(STOP, stdin=_stop()),
        edit_case.run(STOP, stdin=_stop()),
    ]
    each_run(results, stdout="")
    log = edit_case.tmp / ".prd-toolkit" / "lint.log"
    assert log.read_text(encoding="utf-8").splitlines() == ["lint docs/prd/orders"]


@given("H0", "HG", plugins=True)
def test_quiet_stop_inputs_run_no_lint(edit_case):
    """@prd T-279.8"""
    results = [
        edit_case.run(POST, stdin=_edit("<tmp>/docs/prd/orders/prd.md")),
        edit_case.run(STOP, stdin=_stop(), env={"PRD_TOOLKIT_EDIT_HOOK": "off"}),
        edit_case.run(STOP, stdin="not json"),
        edit_case.run(STOP, stdin={"cwd": "<tmp>", "hook_event_name": "Stop"}),
    ]
    each_run(results, stdout="")
    assert not (edit_case.tmp / ".prd-toolkit" / "lint.log").exists()
