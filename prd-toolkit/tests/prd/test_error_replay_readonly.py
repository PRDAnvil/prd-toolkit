"""FR-079, AC-079.2: a run leaves a folder of its clone without write permission (test-cases/error-replay.yaml,
T-079.8).

Every value comes from the test case, AC-079.2 (features/error-replay.md) and testing.md (Setup steps, the
error-replay paragraph and step RRO). Step RRO ends the test as skipped when it runs as root, and resets the mode of
every folder under <tmp>/scratch to 0o700 when the test ends.
"""
from __future__ import annotations

import os

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, worktree_paths  # noqa: F401

FIX = "T-006.1 [integration], PRD 1.0.0, fixed in <fix>"


@given("R0", "RTP", "RRO", "RF", "RE", resolution=FIX)
def test_replay_with_findings_removes_its_clones_whatever_a_run_left_read_only(case):
    """@prd T-079.8"""
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=1, stdout="E-001: T-006.1 passes on <fix>^; <fix> did not turn it green\n")
    assert_left_as_it_was(run_1)
    assert worktree_paths(run_1.after["worktrees"]) == [os.path.realpath(case.repo)], run_1.after["worktrees"]
