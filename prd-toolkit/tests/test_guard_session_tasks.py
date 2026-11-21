"""The tester's Read of its own background run's output when the hook input names no scratchpad.

A headless session's hook input carries `session_id` and no `scratchpad_dir`, and its background tasks write
their output to `<session id>/tasks/<task id>.output`. The guard then takes that folder as the tasks folder.
"""
from pathlib import Path

from test_guard import assert_blocked, make_repo, run

SESSION = "5f0c1e2a-7b3d-4c9e-8a11-2d6f0b9c4e77"
OTHER = "0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"


def read(repo: Path, file_path, session: str | None = SESSION):
    payload = {"tool_name": "Read", "agent_type": "prd-toolkit:prd-tester", "cwd": str(repo),
               "tool_input": {"file_path": str(file_path)}}
    if session is not None:
        payload["session_id"] = session
    return run(payload)


def make_session_tasks(tmp_path: Path, session: str = SESSION) -> Path:
    tasks = tmp_path / "project" / session / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "b1x9.output").write_text("1 passed\n")
    (tasks / "notes.txt").write_text("n\n")
    return tasks


def test_a_session_with_no_scratchpad_reads_its_own_runs_output(tmp_path):
    repo = make_repo(tmp_path)
    tasks = make_session_tasks(tmp_path)
    assert read(repo, tasks / "b1x9.output").returncode == 0


def test_only_an_output_file_of_this_sessions_tasks_folder_is_readable(tmp_path):
    repo = make_repo(tmp_path)
    tasks = make_session_tasks(tmp_path)
    other = make_session_tasks(tmp_path, OTHER)
    (tasks / "sub").mkdir()
    (tasks / "sub/b1x9.output").write_text("x\n")
    (tmp_path / "outside.txt").write_text("o\n")
    (tasks / "l.output").symlink_to(tmp_path / "outside.txt")
    assert_blocked(read(repo, other / "b1x9.output"), "read")  # another session's tasks folder
    assert_blocked(read(repo, tasks / "b1x9.output", session=None), "read")  # no session id, no scratchpad
    assert_blocked(read(repo, tasks / "b1x9.output", session=""), "read")
    assert_blocked(read(repo, tasks / "notes.txt"), "read")  # not an output file
    assert_blocked(read(repo, tasks / "sub/b1x9.output"), "read")  # not directly in the folder
    assert_blocked(read(repo, tasks / "l.output"), "read")  # a symlink out of the folder
    assert_blocked(read(repo, tasks), "read")


def test_a_folder_that_only_looks_like_the_sessions_is_no_tasks_folder(tmp_path):
    repo = make_repo(tmp_path)
    named = tmp_path / "project" / SESSION / "other"  # the session's folder, but not `tasks`
    named.mkdir(parents=True)
    (named / "b1x9.output").write_text("x\n")
    assert_blocked(read(repo, named / "b1x9.output"), "read")
    real = make_session_tasks(tmp_path / "real", OTHER)  # another session's real folder
    link = tmp_path / "linked" / SESSION
    link.mkdir(parents=True)
    (link / "tasks").symlink_to(real, target_is_directory=True)  # a symlinked `tasks` is no tasks folder
    assert_blocked(read(repo, link / "tasks/b1x9.output"), "read")
