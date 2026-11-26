"""edit-hook, FR-278: the edit tier reminds once per session and area when nothing is approved at HEAD.

Every input and expected value is test-cases/edit-hook.yaml's.
"""
from edit_hook_support import (  # noqa: F401  (edit_case is a fixture)
    assert_text,
    each_run,
    edit_case,
    given,
    stderr_single_line_starts,
    stdout_json,
    stdout_json_at,
)

POST = "python <repo>/prd-toolkit/scripts/prd_edit_hook.py post"
REMINDER_IMPORT = (
    "prd-toolkit: src/orders/importer.py is in area import of docs/prd/orders, and no block of that area is "
    "approved at HEAD; a behaviour change there starts with /prd-toolkit:prd-change before any code, and a change "
    "of no behaviour cites Refs: none (no behaviour change)."
)
REMINDER_BOUNDARY = (
    "prd-toolkit: notebooks/report.ipynb is in the Boundary of docs/prd/orders, and no block of that PRD is "
    "approved at HEAD; a behaviour change there starts with /prd-toolkit:prd-change before any code, and a change "
    "of no behaviour cites Refs: none (no behaviour change)."
)


def _edit(path: str, session: str = "<sid>", **extra) -> dict:
    return {"session_id": session, "cwd": "<tmp>", **extra, "tool_name": "Edit", "tool_input": {"file_path": path}}


@given("H0", "HA", "HL")
def test_edit_in_adopted_area_with_nothing_approved_reminds(edit_case):
    """@prd T-278.1"""
    r = edit_case.run(POST, stdin={"session_id": "<sid>", "cwd": "<tmp>", "hook_event_name": "PostToolUse",
                                   "tool_name": "Edit", "tool_input": {"file_path": "<tmp>/src/orders/importer.py"}})
    assert r.exit == 0
    assert_text(r.stderr, "")
    assert stdout_json(r.stdout) == {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                            "additionalContext": REMINDER_IMPORT}}


@given("H0", "HL")
def test_notebook_edit_in_new_project_reminds_of_the_boundary(edit_case):
    """@prd T-278.2"""
    r = edit_case.run(POST, stdin={"session_id": "<sid>", "cwd": "<tmp>", "hook_event_name": "PostToolUse",
                                   "tool_name": "NotebookEdit",
                                   "tool_input": {"notebook_path": "<tmp>/notebooks/report.ipynb"}})
    assert r.exit == 0
    assert_text(r.stderr, "")
    assert stdout_json(r.stdout) == {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                            "additionalContext": REMINDER_BOUNDARY}}


@given("H0", "HA")
def test_a_block_approved_at_head_means_no_reminder(edit_case):
    """@prd T-278.3"""
    r = edit_case.run(POST, stdin={"session_id": "<sid>", "cwd": "<tmp>", "hook_event_name": "PostToolUse",
                                   "tool_name": "Write",
                                   "tool_input": {"file_path": "<tmp>/src/orders/importer.py", "content": "x = 1\n"}})
    assert r.exit == 0
    assert_text(r.stdout, "")
    assert_text(r.stderr, "")


@given("H0", "HA", "HL", "HW")
def test_an_uncommitted_approval_still_gets_the_reminder(edit_case):
    """@prd T-278.4"""
    r = edit_case.run(POST, stdin={"session_id": "<sid>", "cwd": "<tmp>", "hook_event_name": "PostToolUse",
                                   "tool_name": "Edit", "tool_input": {"file_path": "<tmp>/src/orders/importer.py"}})
    assert r.exit == 0
    assert_text(r.stderr, "")
    assert stdout_json(r.stdout) == {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                            "additionalContext": REMINDER_IMPORT}}


@given("H0", "HA", "HL")
def test_once_per_session_and_area(edit_case):
    """@prd T-278.5"""
    runs = [
        _edit("<tmp>/src/orders/importer.py"),
        _edit("<tmp>/src/orders/export.py"),
        _edit("<tmp>/src/orders/importer.py", session="<sid2>"),
        _edit("<tmp>/src/orders/importer.py", session="not a session id"),
        _edit("<tmp>/src/orders/importer.py", session="not a session id"),
    ]
    results = [edit_case.run(POST, stdin=stdin) for stdin in runs]
    each_run(results)
    stdout_json_at(results[0].stdout, {"hookSpecificOutput.additionalContext": REMINDER_IMPORT})
    assert_text(results[1].stdout, "")
    stdout_json_at(results[2].stdout, {"hookSpecificOutput.additionalContext": REMINDER_IMPORT})
    stdout_json_at(results[3].stdout, {"hookSpecificOutput.hookEventName": "PostToolUse"})
    stdout_json_at(results[4].stdout, {"hookSpecificOutput.hookEventName": "PostToolUse"})


@given("H0", "HA", "HL")
def test_quiet_inputs_remind_of_nothing(edit_case):
    """@prd T-278.6"""
    runs = [
        ({}, "not json"),
        ({}, {"session_id": "<sid>", "cwd": "<tmp>", "tool_name": "Read",
              "tool_input": {"file_path": "<tmp>/src/orders/importer.py"}}),
        ({}, _edit("src/orders/importer.py")),
        ({}, _edit("")),
        ({}, _edit("<tmp>/src/reports/monthly.py")),
        ({}, _edit("<tmp>/docs/prd/orders/features/import.md")),
        ({}, {"session_id": "<sid>", "cwd": "<tmp>", "tool_name": "Write",
              "tool_input": {"file_path": "<tmp>/.prd-toolkit/VERSION", "content": "0.0.0\n"}}),
        ({}, _edit("<tmp>/src/orders/importer.py", agent_type="prd-toolkit:prd-tester")),
        ({"PRD_TOOLKIT_EDIT_HOOK": "off"}, _edit("<tmp>/src/orders/importer.py")),
        ({}, {"session_id": "<sid>", "cwd": "<outside>", "tool_name": "Edit",
              "tool_input": {"file_path": "<outside>/x.py"}}),
        ({}, _edit("<tmp>/src/orders/importer.py")),
    ]
    results = [edit_case.run(POST, stdin=stdin, env=env) for env, stdin in runs]
    each_run(results)
    for number in range(1, 11):
        assert results[number - 1].stdout == b"", f"run_{number} stdout: {results[number - 1].stdout!r}"
    stdout_json_at(results[10].stdout, {"hookSpecificOutput.additionalContext": REMINDER_IMPORT})


@given("H0", "HX")
def test_any_other_failure_is_one_stderr_line(edit_case):
    """@prd T-278.7"""
    r = edit_case.run(POST, stdin={"session_id": "<sid>", "cwd": "<tmp>", "tool_name": "Edit",
                                   "tool_input": {"file_path": "<tmp>/src/orders/importer.py"}})
    assert r.exit == 0
    assert_text(r.stdout, "")
    stderr_single_line_starts(r.stderr, "prd-toolkit edit hook: ")


@given("H0", "HA", "HL")
def test_runs_with_no_site_packages(edit_case):
    """@prd T-278.8"""
    r = edit_case.run("python -S <repo>/prd-toolkit/scripts/prd_edit_hook.py post",
                      stdin={"session_id": "<sid>", "cwd": "<tmp>", "tool_name": "Edit",
                             "tool_input": {"file_path": "<tmp>/src/orders/importer.py"}})
    assert r.exit == 0
    assert_text(r.stderr, "")
    assert stdout_json(r.stdout) == {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                            "additionalContext": REMINDER_IMPORT}}
