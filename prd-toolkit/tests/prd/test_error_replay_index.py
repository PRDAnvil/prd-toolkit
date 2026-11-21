"""error-replay, FR-079: a replay started with GIT_INDEX_FILE set writes nothing (test-cases/error-replay.yaml)."""
from __future__ import annotations

import os

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, worktree_paths  # noqa: F401

FIX = "T-006.1 [integration], PRD 1.0.0, fixed in <fix>"
PROOF = "E-001: T-006.1 fails on <fix>^ and passes on <fix>\n"


@given("R0", "RT", "RF", "RE", resolution=FIX)
def test_replay_with_git_index_file_set_writes_nothing(case):
    """@prd T-079.6"""
    res = case.run(REPLAY, env={"GIT_INDEX_FILE": "<tmp>/repo/.git/index"})
    case.expect(res, exit=0, stdout=PROOF, stderr="")
    assert_left_as_it_was(res)
    paths = worktree_paths(res.after["worktrees"])
    assert paths == [os.path.realpath(case.repo)], res.after["worktrees"]
