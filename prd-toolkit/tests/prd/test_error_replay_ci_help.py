"""Characterization test of the shipped help catalogue's `kind.E` (test-cases/error-replay.yaml, AC-081.10).

No step and no repository: the `case` fixture makes <tmp>/scratch and sets the git variables before the run
(testing.md, the error-replay paragraph); PRD_HELP_FILE is left out of the run's environment, so the shipped
catalogue is read.
"""
from __future__ import annotations

from error_replay_support import case, given  # noqa: F401  (case is the fixture)


@given()
def test_help_kind_e_names_ci_run(case):
    """@prd T-081.26"""
    res = case.run("python HELP --key kind.E", cwd=case.tmp)
    case.expect(res, exit=0, stderr="")
    for text in ("`-, PRD <X.Y.Z>, CI run <url>` (environment, standard)",
                 "`<T-id or ->, PRD <X.Y.Z>, run <run id>`",
                 "`fixed in <commit>, red run <test id> [<level>]` (code bug)"):
        assert text in res.stdout, f"stdout does not hold {text!r}:\n{res.stdout}"
