"""FR-079, AC-079.6: a git folder that cannot take a new worktree (test-cases/error-replay.yaml, T-079.7)."""
from __future__ import annotations

import os
import stat

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, worktree_paths  # noqa: F401


@given("R0", "RT", "RF", "RL", "RE", "RNW", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_replay_where_the_git_folder_cannot_take_a_worktree(case):
    """@prd T-079.7"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="E-001: T-006.1 fails on <fix>^ and passes on <fix>\n", stderr="")
    assert_left_as_it_was(res)
    entry = case.repo / ".git" / "worktrees"
    mode = os.lstat(entry).st_mode
    assert stat.S_ISREG(mode), f"{entry} is no longer a regular file"
    assert os.lstat(entry).st_size == 0, f"{entry} is no longer 0 bytes"
    assert worktree_paths(res.after["worktrees"]) == [os.path.realpath(case.repo)], res.after["worktrees"]
