"""error-replay, FR-079: a replay started with GIT_INDEX_FILE set writes nothing (test-cases/error-replay.yaml)."""
from __future__ import annotations

import os

import pytest

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, worktree_paths  # noqa: F401

FIX = "T-006.1 [integration], PRD 1.0.0, fixed in <fix>"
PROOF = "E-001: T-006.1 fails on <fix>^ and passes on <fix>\n"


class E033Symptom(Exception):
    """The symptom T-079.6 names for E-033, seen: the only failure its strict xfail accepts."""


def _is_the_symptom(case, res) -> bool:
    """T-079.6 symptom: proof line, exit 0, status in <tmp>/repo from empty to the one line
    `MM docs/prd/orders/errors.md`; the stderr, the worktree list and the empty scratch as the case expects."""
    return (
        res.exit == 0
        and res.stdout == case.expand(PROOF)
        and res.stderr == ""
        and res.before["status"] == ""
        and res.after["status"].splitlines() == ["MM docs/prd/orders/errors.md"]
        and res.after["status"].endswith("\n")
        and res.after["worktrees"] == res.before["worktrees"]
        and worktree_paths(res.after["worktrees"]) == [os.path.realpath(case.repo)]
        and res.scratch_after == []
    )


@pytest.mark.xfail(strict=True, raises=E033Symptom, reason="E-033")
@given("R0", "RT", "RF", "RE", resolution=FIX)
def test_replay_with_git_index_file_set_writes_nothing(case):
    """@prd T-079.6 known-failing E-033"""
    res = case.run(REPLAY, env={"GIT_INDEX_FILE": "<tmp>/repo/.git/index"})
    if _is_the_symptom(case, res):
        raise E033Symptom(f"git status went from empty to {res.after['status']!r}")
    case.expect(res, exit=0, stdout=PROOF, stderr="")
    assert_left_as_it_was(res)
    paths = worktree_paths(res.after["worktrees"])
    assert paths == [os.path.realpath(case.repo)], res.after["worktrees"]
