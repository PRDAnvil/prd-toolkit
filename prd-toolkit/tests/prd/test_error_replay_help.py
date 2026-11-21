"""error-replay, AC-081.5: the shipped help catalogue names the red run beside the other three forms
(test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import case, given  # noqa: F401

FORMS = [  # T-081.14 stdout_contains, as written: no name in them is replaced
    "`fixed in <commit>, red run <test id> [<level>]` (code bug)",
    "`<T-id> [<level>], PRD <X.Y.Z>, fixed in <commit>`",
    "`<T-id or ->, PRD <X.Y.Z>, run <run id>`",
    "`not a defect: <why>`",
]


@given()
def test_help_kind_e_names_the_four_forms_of_resolution(case):
    """@prd T-081.14"""
    res = case.run("python HELP --key kind.E", cwd=case.tmp)
    case.expect(res, exit=0, stderr="")
    missing = [form for form in FORMS if form not in res.stdout]
    assert missing == [], f"stdout lacks {missing}\n{res.detail()}"
