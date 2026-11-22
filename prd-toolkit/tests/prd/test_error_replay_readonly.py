"""FR-079, AC-079.2: a test leaves a folder of its clone without write permission (test-cases/error-replay.yaml,
T-079.8)."""
from __future__ import annotations

import os

from error_replay_support import assert_left_as_it_was, case, given, worktree_paths  # noqa: F401


@given("R0", "RTP", "RRO", "RF", "RE", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_replay_with_findings_removes_its_folder_whatever_a_test_left_in_it(case):
    """@prd T-079.8"""
    run_1 = case.run("python ERROR replay docs/prd/orders E-001")
    case.expect(run_1, exit=1, stdout="E-001: T-006.1 passes on <fix>^; <fix> did not turn it green\n")
    assert_left_as_it_was(run_1)
    assert worktree_paths(run_1.after["worktrees"]) == [os.path.realpath(case.repo)], run_1.after["worktrees"]
