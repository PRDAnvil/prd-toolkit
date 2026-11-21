"""error-replay, FR-078: what the replay prints and how it exits (test-cases/error-replay.yaml)."""
from __future__ import annotations

from error_replay_support import REPLAY, assert_left_as_it_was, case, given, one_json_line  # noqa: F401

RED_RUN = "fixed in <fix>, red run tests/test_total.py [integration]"
NOT_A_DEFECT = "not a defect: the total was read from the wrong report"
KEYS = ["interface", "kind", "entry", "outcome", "subject", "reason", "findings", "runs"]
RUN_KEYS = ["commit", "when", "argument", "exit", "seconds", "timed_out"]


@given("R0", "RT", "RF", "RE", resolution=RED_RUN)
def test_no_such_entry(case):
    """@prd T-078.1"""
    for command in ("python ERROR replay docs/prd/orders E-009", "python ERROR replay docs/prd/orders E-009 --json"):
        res = case.run(command)
        case.expect(res, exit=1, stdout="", stderr="refused: E-009 is not an entry\n")
        assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RO")
def test_open_entry(case):
    """@prd T-078.2"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001 is not resolved\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="fixed it in the end")
def test_free_text_resolution(case):
    """@prd T-078.3"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: resolution is not one of the four forms\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="-, PRD 1.0.0, run 20261110T090000Z-all")
def test_environment_run_skipped(case):
    """@prd T-078.4"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: resolved by an environment run\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution=NOT_A_DEFECT)
def test_not_a_defect_skipped(case):
    """@prd T-078.5"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: resolved as not a defect\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="fixed in <fix>, red run tests/test_total.py [nosuch]")
def test_level_not_in_levels(case):
    """@prd T-078.6"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: nosuch is not a level of testing.md\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="T-006.1 [system], PRD 1.0.0, fixed in <fix>")
def test_deploy_gate_level_skipped(case):
    """@prd T-078.7"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: system is a deploy-gate level\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="T-006.1 [unit], PRD 1.0.0, fixed in <fix>")
def test_empty_one_test_cell_skipped(case):
    """@prd T-078.8"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: unit has no One test command\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="fixed in 0000000, red run tests/test_total.py [integration]")
def test_sha_names_no_commit(case):
    """@prd T-078.9"""
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=1, stdout="E-001: 0000000 names no commit\n", stderr="")
    assert_left_as_it_was(run_1)
    run_2 = case.run(REPLAY + " --json")
    case.expect(run_2, exit=1, stderr="")
    case.expect_json(run_2, {
        "interface": 1,
        "kind": "error-replay",
        "entry": "E-001",
        "outcome": "findings",
        "subject": "tests/test_total.py",
        "reason": None,
        "findings": ["E-001: 0000000 names no commit"],
        "runs": [],
    })
    assert_left_as_it_was(run_2)


@given("R0", "RT", "RF", "RE", resolution="fixed in <bug>, red run tests/test_total.py [integration]")
def test_sha_has_no_parent(case):
    """@prd T-078.10"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: <bug> has no parent\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RMANY", "RE", resolution="fixed in <many>, red run tests/test_total.py [integration]")
def test_sha_names_more_than_one_commit(case):
    """@prd T-078.11"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: <many> names more than one commit\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="fixed in 0000000, red run tests/test_total.py [nosuch]")
def test_level_checked_before_commit(case):
    """@prd T-078.12"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: nosuch is not a level of testing.md\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="T-007.1 [system], PRD 1.0.0, fixed in 0000000")
def test_deploy_gate_checked_first(case):
    """@prd T-078.13"""
    res = case.run(REPLAY)
    case.expect(res, exit=0, stdout="skipped: E-001: system is a deploy-gate level\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="T-007.1 [integration], PRD 1.0.0, fixed in 0000000")
def test_commit_checked_before_citation(case):
    """@prd T-078.14"""
    res = case.run(REPLAY)
    case.expect(res, exit=1, stdout="E-001: 0000000 names no commit\n", stderr="")
    assert_left_as_it_was(res)


@given("R0", "RTI", "RF", "RE", resolution="T-006.1 [integration], PRD 1.0.0, fixed in <fix>")
def test_every_run_made_and_findings_in_order(case):
    """@prd T-078.15"""
    findings = [
        "E-001: T-006.1 passes on <fix>^; <fix> did not turn it green",
        "E-001: T-006.1 fails on <fix>: tests/test_a.py",
        "E-001: T-006.1 fails on <fix>: tests/test_b.py",
    ]
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=1, stderr="")
    case.expect_lines(run_1.stdout, findings)
    assert_left_as_it_was(run_1)
    run_2 = case.run(REPLAY + " --json")
    case.expect(run_2, exit=1, stderr="")
    doc = case.expect_json_at(run_2, {
        "outcome": "findings",
        "findings": findings,
        "runs.0.when": "before", "runs.0.argument": "tests/test_a.py", "runs.0.exit": 0,
        "runs.1.when": "before", "runs.1.argument": "tests/test_b.py", "runs.1.exit": 0,
        "runs.2.when": "after", "runs.2.argument": "tests/test_a.py", "runs.2.exit": 1,
        "runs.3.when": "after", "runs.3.argument": "tests/test_b.py", "runs.3.exit": 1,
    })
    assert isinstance(doc["runs"], list) and len(doc["runs"]) == 4, doc
    assert_left_as_it_was(run_2)


@given("R0", "RT", "RF", "RE", resolution="fixed in <fix>, red run tests/test_total.py [slow]")
def test_timeout_from_cell_and_flag(case):
    """@prd T-078.16"""
    run_1 = case.run(REPLAY)
    case.expect(run_1, exit=1, stderr="")
    case.expect_lines(run_1.stdout, ["E-001: timed out after 2 s on <fix>^", "E-001: timed out after 2 s on <fix>"])
    assert_left_as_it_was(run_1)
    run_2 = case.run(REPLAY + " --timeout 1")
    case.expect(run_2, exit=1, stderr="")
    case.expect_lines(run_2.stdout, ["E-001: timed out after 1 s on <fix>^", "E-001: timed out after 1 s on <fix>"])
    assert_left_as_it_was(run_2)
    run_3 = case.run(REPLAY + " --json")
    case.expect(run_3, exit=1, stderr="")
    case.expect_json_at(run_3, {
        "outcome": "findings",
        "findings": ["E-001: timed out after 2 s on <fix>^", "E-001: timed out after 2 s on <fix>"],
        "runs.0.when": "before", "runs.0.exit": None, "runs.0.timed_out": True,
        "runs.1.when": "after", "runs.1.exit": None, "runs.1.timed_out": True,
    })
    assert_left_as_it_was(run_3)
    for n, res in enumerate((run_1, run_2, run_3), 1):
        assert res.seconds < 30, f"run_{n} took {res.seconds:.1f} s"


@given("R0", "RT", "RF", "RE", resolution=RED_RUN)
def test_bad_timeout_values(case):
    """@prd T-078.17"""
    for flag in ("--timeout 0", "--timeout abc", "--timeout 1.5", "--timeout=-3"):
        res = case.run(f"{REPLAY} {flag}")
        case.expect(res, exit=2, stdout="",
                    stderr="prd_error: --timeout must be a whole number of seconds of at least 1\n")
        assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RL", "RE", resolution=RED_RUN)
def test_json_document_when_the_proof_holds(case):
    """@prd T-078.18"""
    for flag in ("--json", "--json=1"):
        res = case.run(f"{REPLAY} {flag}")
        case.expect(res, exit=0, stderr="")
        doc = one_json_line(res.stdout)
        assert list(doc.keys()) == KEYS, doc
        assert list(doc["runs"][0].keys()) == RUN_KEYS, doc
        assert list(doc["runs"][1].keys()) == RUN_KEYS, doc
        case.expect_json_at(res, {
            "interface": 1,
            "kind": "error-replay",
            "entry": "E-001",
            "outcome": "holds",
            "subject": "tests/test_total.py",
            "reason": None,
            "findings": [],
            "runs.0.commit": "FULL(fix^)",
            "runs.0.when": "before",
            "runs.0.argument": "tests/test_total.py",
            "runs.0.exit": 1,
            "runs.0.timed_out": False,
            "runs.1.commit": "FULL(fix)",
            "runs.1.when": "after",
            "runs.1.argument": "tests/test_total.py",
            "runs.1.exit": 0,
            "runs.1.timed_out": False,
        })
        assert len(doc["runs"]) == 2, doc
        for run in doc["runs"]:
            seconds = run["seconds"]
            assert isinstance(seconds, (int, float)) and not isinstance(seconds, bool), run
        assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution=NOT_A_DEFECT)
def test_json_document_when_skipped(case):
    """@prd T-078.19"""
    res = case.run(REPLAY + " --json")
    case.expect(res, exit=0, stderr="")
    doc = case.expect_json(res, {
        "interface": 1,
        "kind": "error-replay",
        "entry": "E-001",
        "outcome": "skipped",
        "subject": None,
        "reason": "resolved as not a defect",
        "findings": [],
        "runs": [],
    })
    assert list(doc.keys())[:len(KEYS)] == KEYS, doc
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution="T-006.1 [nosuch], PRD 1.0.0, fixed in <fix>")
def test_json_document_of_a_finding(case):
    """@prd T-078.20"""
    res = case.run(REPLAY + " --json")
    case.expect(res, exit=1, stderr="")
    case.expect_json(res, {
        "interface": 1,
        "kind": "error-replay",
        "entry": "E-001",
        "outcome": "findings",
        "subject": "T-006.1",
        "reason": None,
        "findings": ["E-001: nosuch is not a level of testing.md"],
        "runs": [],
    })
    assert_left_as_it_was(res)


@given("R0", "RT", "RF", "RE", resolution=RED_RUN)
def test_json_error_object(case):
    """@prd T-078.21"""
    run_1 = case.run(REPLAY + " --timeout 0 --json")
    case.expect(run_1, exit=2, stderr="prd_error: --timeout must be a whole number of seconds of at least 1\n")
    case.expect_json(run_1, {"interface": 1, "kind": "error-replay",
                             "error": "--timeout must be a whole number of seconds of at least 1"})
    assert_left_as_it_was(run_1)
    run_2 = case.run("python ERROR replay nowhere E-001 --json=2")
    case.expect(run_2, exit=2, stderr="prd_error: unsupported interface 2; this toolkit speaks 1\n")
    case.expect_json(run_2, {"interface": 1, "kind": "error-replay",
                             "error": "unsupported interface 2; this toolkit speaks 1"})
    assert_left_as_it_was(run_2)


@given()
def test_interface(case):
    """@prd T-078.22"""
    for command in ("python ERROR replay --interface", "python ERROR replay nowhere E-001 --json=2 --interface"):
        res = case.run(command, cwd=case.tmp)
        case.expect(res, exit=0, stdout="1\n", stderr="")
