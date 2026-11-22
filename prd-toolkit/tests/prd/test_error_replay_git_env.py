"""A replay started with GIT_INDEX_FILE naming the scratch repository's own index (test-cases/error-replay.yaml).

Every value comes from the test case, AC-079.2 (features/error-replay.md) and testing.md (Setup steps, the
error-replay paragraph and step RGA). The case carries `known-failing: E-036` and a `symptom:`: only that symptom,
a line of `git status --porcelain` after run_1 whose path is `junk`, is the expected failure.
"""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, given  # noqa: F401 (case is the fixture)


class KnownFailureE036(Exception):
    """The symptom of E-036 was seen: the test's `git add -A` staged junk in the index GIT_INDEX_FILE names."""


def _junk_lines(status: str) -> list[str]:
    """The lines of `git status --porcelain` whose path, the text after their first three characters, is junk."""
    return [line for line in status.splitlines() if line[3:] == "junk"]


@given("R0", "RT", "RF", "RGA", "RE", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_replay_with_git_index_file_leaves_the_index(case):
    """@prd T-079.9"""
    res = case.run(REPLAY, env={"GIT_INDEX_FILE": "<tmp>/repo/.git/index"})
    case.expect(res, exit=1, stdout="E-001: T-006.1 passes on <fix>^; <fix> did not turn it green\n")
    junk = _junk_lines(res.after["status"])
    if junk:
        raise KnownFailureE036(f"git status --porcelain after run_1 holds {junk}")
    assert_left_as_it_was(res)
    assert not (case.repo / "junk").exists(), "<tmp>/repo holds the file junk after run_1"
