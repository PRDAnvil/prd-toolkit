"""edit-hook, FR-280: the plugin's hooks.json wires both tiers, and the script refuses another mode.

Every input and expected value is test-cases/edit-hook.yaml's.
"""
from edit_hook_support import (  # noqa: F401  (edit_case is a fixture)
    REPO,
    assert_text,
    each_run,
    edit_case,
    given,
    stdout_json,
    stdout_json_keys_at,
)


@given()
def test_hooks_json_holds_the_three_entries(edit_case):
    """@prd T-280.1"""
    r = edit_case.run(
        "python -c \"import json, sys; print(json.dumps(json.load(open(sys.argv[1], encoding='utf-8'))))\" "
        "prd-toolkit/hooks/hooks.json",
        cwd=REPO,
    )
    assert r.exit == 0
    assert_text(r.stderr, "")
    assert stdout_json(r.stdout) == {
        "hooks": {
            "PreToolUse": [
                {"matcher": "Read|Glob|Grep|Write|Edit|NotebookEdit|Bash",
                 "hooks": [{"type": "command",
                            "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prd_tester_guard.py"'}]},
            ],
            "PostToolUse": [
                {"matcher": "Edit|Write|MultiEdit|NotebookEdit",
                 "hooks": [{"type": "command",
                            "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prd_edit_hook.py" post',
                            "timeout": 5}]},
            ],
            "Stop": [
                {"hooks": [{"type": "command",
                            "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prd_edit_hook.py" stop',
                            "timeout": 60}]},
            ],
        }
    }
    stdout_json_keys_at(r.stdout, {"": ["hooks"], "hooks": ["PreToolUse", "PostToolUse", "Stop"]})


@given()
def test_no_mode_or_another_mode_is_a_usage_error(edit_case):
    """@prd T-280.2"""
    results = [
        edit_case.run("python <repo>/prd-toolkit/scripts/prd_edit_hook.py", stdin={"session_id": "<sid>"}),
        edit_case.run("python <repo>/prd-toolkit/scripts/prd_edit_hook.py pre", stdin={"session_id": "<sid>"}),
    ]
    each_run(results, exit_code=2, stderr="usage: prd_edit_hook.py post|stop\n", stdout="")
