"""error-replay, FR-079: the replay leaves nothing behind and writes nothing (test-cases/error-replay.yaml)."""
from __future__ import annotations

import os
import subprocess

from error_replay_support import (  # noqa: F401
    REPLAY, assert_left_as_it_was, case, given, send_sigint, wait_for_number, wait_until_gone, worktree_paths,
)

FIX = "T-006.1 [integration], PRD 1.0.0, fixed in <fix>"
SLOW = "fixed in <fix>, red run tests/test_total.py [slow]"


def _only_the_repository(case, res) -> None:
    paths = worktree_paths(res.after["worktrees"])
    assert paths == [os.path.realpath(case.repo)], res.after["worktrees"]


@given("R0", "RT", "RF", "RL", "RE", resolution=FIX)
def test_nothing_left_when_the_proof_holds(case):
    """@prd T-079.1"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="E-001: T-006.1 fails on <fix>^ and passes on <fix>\n")
    assert_left_as_it_was(res)
    _only_the_repository(case, res)


@given("R0", "RTP", "RF", "RE", resolution=FIX)
def test_nothing_left_with_findings(case):
    """@prd T-079.2"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: T-006.1 passes on <fix>^; <fix> did not turn it green\n")
    assert_left_as_it_was(res)
    _only_the_repository(case, res)


@given("R0", "RT", "RF", "RE", resolution=SLOW)
def test_nothing_left_after_a_timeout(case):
    """@prd T-079.3"""
    res = case.run(REPLAY)
    case.expect(res, exit=1)
    case.expect_lines(res.stdout, ["E-001: timed out after 2 s on <fix>^", "E-001: timed out after 2 s on <fix>"])
    assert_left_as_it_was(res)
    _only_the_repository(case, res)


@given("R0", "RT", "RF", "RE", resolution=SLOW)
def test_sigint_kills_the_run_and_cleans_up(case):
    """@prd T-079.4"""
    started = case.tmp / "started"
    before = case.state()
    proc = case.popen(REPLAY + " --timeout 60", env={"ONE_STARTED": "<tmp>/started"})
    try:
        pid = wait_for_number(started, 30)
        send_sigint(proc)
        try:
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired as exc:
            raise AssertionError("the replay did not end within 30 seconds of SIGINT") from exc
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate()
    after = case.state()
    detail = f"exit {proc.returncode}\n--- stdout\n{stdout.decode('utf-8')}--- stderr\n{stderr.decode('utf-8')}"
    assert proc.returncode == 130, detail
    assert after["worktrees"] == before["worktrees"], \
        f"git worktree list changed:\n--- before\n{before['worktrees']}--- after\n{after['worktrees']}"
    assert after["status"] == before["status"], \
        f"git status changed:\n--- before\n{before['status']}--- after\n{after['status']}"
    assert case.scratch_entries() == [], f"<tmp>/scratch holds {case.scratch_entries()}"
    assert wait_until_gone(pid, 5), f"process {pid} still exists 5 seconds after the replay ended"


@given("R0", "RT", "RF", "RL", "RE", "RWT", resolution=FIX)
def test_started_in_a_linked_worktree(case):
    """@prd T-079.5"""
    wt = case.tmp / "wt"
    res = case.run(REPLAY, cwd=wt, status_in=wt)
    case.expect(res, exit=0, stdout="E-001: T-006.1 fails on <fix>^ and passes on <fix>\n", stderr="")
    assert res.after["worktrees"] == res.before["worktrees"], \
        f"git worktree list changed:\n--- before\n{res.before['worktrees']}--- after\n{res.after['worktrees']}"
    assert sorted(worktree_paths(res.after["worktrees"])) == sorted([os.path.realpath(case.repo),
                                                                     os.path.realpath(wt)]), \
        res.after["worktrees"]
    assert res.after["status"] == res.before["status"], \
        f"git status in <tmp>/wt changed:\n--- before\n{res.before['status']}--- after\n{res.after['status']}"
    assert res.scratch_after == [], f"<tmp>/scratch holds {res.scratch_after}"
