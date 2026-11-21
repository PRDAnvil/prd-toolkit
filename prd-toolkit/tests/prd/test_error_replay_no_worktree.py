"""FR-079, AC-079.6: a git folder that cannot take a new worktree (test-cases/error-replay.yaml, T-079.7)."""
from __future__ import annotations

import os
import re
import stat

import pytest

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, worktree_paths  # noqa: F401


class E035Symptom(Exception):
    """The symptom T-079.7 names for E-035 showed: the only failure the strict marker accepts."""


_SYMPTOM_LINE = re.compile(
    r"prd_error: internal error: RuntimeError: git worktree add --detach .*"
    r" failed: Preparing worktree \(detached HEAD (?P<h>[0-9a-f]{7,})\)"
)


def _symptom(res, full_fix_parent: str, full_fix: str) -> bool:
    """run_1 exits 2 and its stderr is exactly the one line the case's `symptom:` gives."""
    if res.exit != 2:
        return False
    lines = res.stderr.splitlines()
    if len(lines) != 1:
        return False
    m = _SYMPTOM_LINE.fullmatch(lines[0])
    if m is None:
        return False
    h = m.group("h")
    return full_fix_parent.startswith(h) or full_fix.startswith(h)


@given("R0", "RT", "RF", "RL", "RE", "RNW", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_replay_where_the_git_folder_cannot_take_a_worktree(case):
    """@prd T-079.7"""
    res = case.run(REPLAY)

    # The effects hold whether or not the symptom shows.
    assert_left_as_it_was(res)
    entry = case.repo / ".git" / "worktrees"
    mode = os.lstat(entry).st_mode
    assert stat.S_ISREG(mode), f"{entry} is no longer a regular file"
    assert os.lstat(entry).st_size == 0, f"{entry} is no longer 0 bytes"
    assert worktree_paths(res.after["worktrees"]) == [os.path.realpath(case.repo)], res.after["worktrees"]

    if _symptom(res, case.full("fix^"), case.full("fix")):
        raise E035Symptom(res.detail())

    case.expect(res, exit=0, stdout="E-001: T-006.1 fails on <fix>^ and passes on <fix>\n", stderr="")
