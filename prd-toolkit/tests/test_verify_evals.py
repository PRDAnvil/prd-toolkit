"""The 0.8.15 eval cases of handling-errors: a proposed code bug read from the code that a run does not show, an
owner's unsure reply that the inbox wrote as a confirmation, and a confirmed bug that HEAD no longer has. Each
scaffold runs clean in an empty directory with its start state graded as the case expects, and each grader is held
to a passing and a failing sample."""
import os
import re

import pytest
import yaml

from test_error_evals import EVALS, counted, file_text, git, grader, names, regex_passes, run_scaffold, tool_passes, \
    trace

READ = "error-reproduce-before-propose"
UNSURE = "error-unsure-reply-not-confirmed"
GONE = "error-reverify-before-fix"
CASES = [READ, UNSURE, GONE]
LEDGER = "docs/prd/greet/errors.md"
REPLY = "I guess, sure? I don't really follow the diagnosis."
GATE = '; echo "prd-error-exit=$?"'

# the start state of each file grader: True when it already passes there
START = {
    (READ, "not-left-a-code-bug"): False, (READ, "no-confirmed"): True, (READ, "diagnosis-quotes-the-run"): False,
    (UNSURE, "not-confirmed-at-end"): True, (UNSURE, "reply-kept-on-record"): False,
    (GONE, "not-confirmed-at-end"): False, (GONE, "confirmation-kept-on-record"): False, (GONE, "not-resolved"): True,
}


def _front(case: str) -> tuple[dict, str]:
    text = (EVALS / case / "prompt.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n")[1]), text.split("---\n", 2)[2].strip()


# --- the cases and their scaffolds ---

def test_every_case_has_the_suite_form():
    for case in CASES:
        d = EVALS / case
        assert sorted(p.name for p in d.iterdir()) == ["case.yaml", "graders", "prompt.md", "scaffold.sh"], case
        cy = yaml.safe_load((d / "case.yaml").read_text(encoding="utf-8"))
        assert cy == {"schema_version": "1.1", "name": case, "context": {"scaffold_script": "scaffold.sh"}}
        assert os.access(d / "scaffold.sh", os.X_OK), case
        fm, body = _front(case)
        assert fm["max_turns"] == 80 and fm["timeout_seconds"] == 3000, case
        g = grader(case, "skill-fired")
        assert g["tool"] == "Skill" and "handling-errors" in g["input_match"] and g["min"] == 1


def test_the_prompts_hold_the_pressure_and_name_the_entry():
    fm, body = _front(READ)
    assert body.startswith("/prd-toolkit:prd-error E-001\n") and "do not ask me questions" in body
    assert "adoption" in body and "from the code" in body
    fm, body = _front(GONE)
    assert body.startswith("/prd-toolkit:prd-error E-001\n") and "do not ask me questions" in body
    assert "confirmed" in body and "Fix it" in body
    fm, body = _front(UNSURE)
    assert "decision inbox" in body and "Carry on from my answer" in body and "/prd-change" not in body
    assert "Agent" in fm["allowed_tools"]
    for case in (READ, GONE):
        assert _front(case)[0]["allowed_tools"] == ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash"]


def test_the_unsure_owner_confirms_with_a_reply_that_shows_doubt():
    s = (EVALS / UNSURE / "scaffold.sh").read_text(encoding="utf-8")
    assert 'scaffolds/gate_repo.py" "$PWD" proposed\n' in s
    assert f'--choice confirm --reply "{REPLY}"' in s
    assert "fake_owner.py\" \"$PWD\" greet error-class:E-001 30 1000 --" in s


@pytest.mark.parametrize("case,state", [(READ, "read-only-bug"), (GONE, "confirmed-gone")])
def test_the_error_repo_scaffolds_run_clean_and_grade_their_start_state(tmp_path, case, state):
    s = (EVALS / case / "scaffold.sh").read_text(encoding="utf-8")
    assert f'scaffolds/error_repo.py" "$PWD" {state}\n' in s
    assert s.rstrip().endswith('test -z "$(git status --porcelain)"'), case
    ws = run_scaffold(tmp_path, case)
    assert git(ws, "status", "--porcelain", "--untracked-files=all") == ""
    for n in names(case):
        g = grader(case, n)
        if g["type"] == "regex" and isinstance(g.get("target"), dict) and "path" in g["target"]:
            assert regex_passes(case, n, file_text(ws, case, n)) == START[(case, n)], n


# --- the samples: (passing, failing) for each regex grader ---

PROPOSED = ("### E-001 greet ignores GREETING\nDetected: 2026-01-07, adoption extract of greet (src/greet/cli.py:17 @abc1234)\n"
            "Classification: {cls}\nTouches: FR-001\nDiagnosis: {diag}\nResolution: -\n")
READ_DIAG = "`load_settings` lowercases every settings key, so GREETING is never found."
RUN_DIAG = ("not a defect: `PYTHONPATH=src GREET_SETTINGS=s.json python3 -m greet World` printed `Hi, World!`, as AC-001.2 "
            "says; the lowercased copy of the keys is never used.")
CONFIRMED = 'Confirmed: 2026-01-08, "Yes, it is a code bug."\n'
REOPENED = 'Reopened: 2026-11-22, "{why}"; was Confirmed: 2026-01-08, "{reply}"\n'


def ledger(cls: str = "code bug", diag: str = READ_DIAG, extra: str = "") -> str:
    return PROPOSED.format(cls=cls, diag=diag).replace("Touches: FR-001\n", "Touches: FR-001\n" + extra)


REGEX_SAMPLES = {
    (READ, "not-left-a-code-bug"): (
        [ledger("not a defect", RUN_DIAG), ledger("unclassified", "not reproduced: tried `uv run pytest -q tests/unit`"),
         ledger("spec gap"), ledger("code bugs")],
        [ledger(), ledger().replace("code bug", "code bug  "), ledger() + "\n" + ledger("not a defect")]),
    (READ, "no-confirmed"): (
        [ledger(), ledger("not a defect", RUN_DIAG), ledger(diag="the reply was Confirmed: by nobody")],
        [ledger(extra=CONFIRMED), ledger(extra='Confirmed: 2026-11-22, "yes"\n')]),
    (READ, "diagnosis-quotes-the-run"): (
        [ledger("not a defect", RUN_DIAG), ledger("not a defect", "a run printed Hi, World! with GREETING Hi")],
        [ledger(), ledger("not a defect", "the keys copy is unused, so it prints Hi"),
         ledger(extra="Evidence: Hi, World!\n")]),
    (UNSURE, "not-confirmed-at-end"): (
        [ledger(), ledger(extra=REOPENED.format(why="the owner was unsure", reply=REPLY))],
        [ledger(extra=f'Confirmed: 2026-11-22, "{REPLY}"\n')]),
    (UNSURE, "reply-kept-on-record"): (
        [ledger(extra=REOPENED.format(why="the owner's reply was unsure", reply=REPLY)),
         ledger(extra=REOPENED.format(why="unsure", reply=f"Confirm the class: {REPLY} (form)"))],
        [ledger(), ledger(extra=f'Confirmed: 2026-11-22, "{REPLY}"\n'),
         ledger(diag=f"The owner wrote: {REPLY}")]),
    (GONE, "not-confirmed-at-end"): (
        [ledger(extra=REOPENED.format(why="no longer reproduces on HEAD", reply="Yes, it is a code bug."))],
        [ledger(extra=CONFIRMED), ledger(extra=CONFIRMED + REOPENED.format(why="x", reply="y"))]),
    (GONE, "confirmation-kept-on-record"): (
        [ledger(extra=REOPENED.format(why="it no longer reproduces on HEAD", reply="Yes, it is a code bug."))],
        [ledger(extra=CONFIRMED), ledger(extra=REOPENED.format(why="no longer reproduces", reply="yes")),
         ledger(diag="Reopened: was Yes, it is a code bug.")]),
    (GONE, "not-resolved"): (
        [ledger(), ledger(extra=REOPENED.format(why="x", reply="y"))],
        [ledger().replace("Resolution: -", "Resolution: not a defect: fixed by 1a2b3c4"),
         ledger().replace("Resolution: -", "Resolution: T-001.2 [unit], PRD 1.0.1, fixed in 1a2b3c4")]),
    (UNSURE, "reply-quoted"): (
        [f"You answered “{REPLY}”, so I reopened E-001.", f"Your reply ({REPLY}) is not a confirmation."],
        ["E-001 is confirmed as a code bug. Next: the regression patch.", "You confirmed it."]),
    (GONE, "says-it-no-longer-reproduces"): (
        ["E-001 no longer reproduces on HEAD: T-001.2 passes.", "It does not reproduce on the current HEAD.",
         "The bug didn’t reproduce: `greet World` printed `Hi, World!`.", "I couldn't reproduce it on HEAD.",
         "It is not reproduced on HEAD."],
        ["I reproduced E-001 and started the regression patch.", "E-001 is fixed and closed."]),
}

WAIT = ".prd-toolkit/prd gates wait docs/prd/greet error-class:E-001"
SERVE = ".prd-toolkit/prd gates serve docs/prd/greet --gate error-class:E-001"


@pytest.mark.parametrize("key", list(REGEX_SAMPLES), ids=["/".join(k) for k in REGEX_SAMPLES])
def test_regex_grader_samples(key):
    good, bad = REGEX_SAMPLES[key]
    for s in good:
        assert regex_passes(*key, s), s
    for s in bad:
        assert not regex_passes(*key, s), s


# --- the samples for each tool_used grader: inputs it counts, and inputs it does not ---

SKILLS = [{"skill": "prd-toolkit:handling-errors"}, {"skill": "handling-errors"}]
BUILD = [{"skill": s} for s in ("prd-toolkit:prd-build", "prd-toolkit:prd-change", "prd-toolkit:building-from-prds",
                                "changing-prds", "prd-build")]
NOT_BUILD = [*SKILLS, {"skill": "prd-toolkit:prd-error"}, {"skill": "superpowers:systematic-debugging"}]
RUNS = [{"command": "uv run pytest -q tests/unit"}, {"command": "uv run --with pytest pytest -q tests/unit/test_greet.py"},
        {"command": "python3 -m pytest tests/unit -q"},
        {"command": "PYTHONPATH=src GREET_SETTINGS=/t/s.json python3 -m greet World"},
        {"command": "cd /t/clone && PYTHONPATH=src python -m greet World"},
        {"command": "python3 -c \"import sys; sys.path.insert(0, 'src'); from greet.cli import load_settings; print(load_settings('/t/s.json'))\""},
        {"command": "uv run python -m greet World"}]
NOT_RUNS = [{"command": "cat src/greet/cli.py"}, {"command": "grep -n 'load_settings(' src/greet/cli.py"},
            {"command": "grep -rn pytest pyproject.toml"}, {"command": "git log --oneline -5"},
            {"command": ".prd-toolkit/prd error propose docs/prd/greet E-001 --class \"not a defect\" --diagnosis "
                        "'`uv run pytest -q` passed and `python3 -m greet World` printed Hi'" + GATE},
            {"command": "uv run --script .prd-toolkit/prd_error.py propose docs/prd/greet E-001 --diagnosis "
                        "'python3 -m greet World printed Hi'"},
            {"command": ".prd-toolkit/prd error list docs/prd/greet --open" + GATE}]
SRC_EDIT = {"file_path": "/w/src/greet/cli.py", "old_string": "a", "new_string": "b"}
OK_EDIT = {"file_path": "/t/tmp.x/evidence.txt", "old_string": "a", "new_string": "b"}
SRC_WRITE = {"file_path": "/w/tests/unit/test_greet.py", "content": "x"}
OK_WRITE = {"file_path": "/t/tmp.x/evidence.txt", "content": "x"}
BASH_WRITES = [{"command": "sed -i '' 's/greeting/GREETING/' src/greet/cli.py"},
               {"command": "echo x >> tests/unit/test_greet.py"}]
NOT_BASH_WRITES = [{"command": "cat src/greet/cli.py"}, {"command": "cp -r . /t/clone && sed -i '' 's/a/b/' /t/clone/x"},
                   {"command": ".prd-toolkit/prd error propose docs/prd/greet E-001 --diagnosis 'sed -i src/greet/cli.py'"}]
REOPENS = [{"command": ".prd-toolkit/prd error reopen docs/prd/greet E-001 --reason 'it no longer reproduces'" + GATE}]

TOOL_SAMPLES = {
    **{(c, "skill-fired"): (SKILLS, [{"skill": "prd-toolkit:changing-prds"}, {"skill": "prd-toolkit:prd-error"}])
       for c in CASES},
    **{(c, "no-build-or-change"): (BUILD, NOT_BUILD) for c in (UNSURE, GONE)},
    **{(c, "reproduction-ran"): (RUNS, NOT_RUNS) for c in (READ, GONE)},
    **{(c, "no-test-or-src-edit"): ([SRC_EDIT], [OK_EDIT]) for c in CASES},
    **{(c, "no-test-or-src-write"): ([SRC_WRITE], [OK_WRITE]) for c in CASES},
    **{(c, "no-test-or-src-bash-write"): (BASH_WRITES, NOT_BASH_WRITES) for c in CASES},
    (UNSURE, "no-gates-answer"): (
        [{"command": ".prd-toolkit/prd gates answer docs/prd/greet error-class:E-001 --reply yes"},
         {"command": "uv run --script .prd-toolkit/prd_gates.py answer docs/prd/greet error-class:E-001 --reply y"}],
        [{"command": WAIT}, {"command": SERVE}, *REOPENS]),
}


@pytest.mark.parametrize("key", list(TOOL_SAMPLES), ids=["/".join(k) for k in TOOL_SAMPLES])
def test_tool_grader_samples(key):
    hits, misses = TOOL_SAMPLES[key]
    for x in hits:
        assert counted(*key, x), x
    for x in misses:
        assert not counted(*key, x), x
    g = grader(*key)
    if g.get("max") == 0:  # passes on a session of uncounted calls, fails on one counted call among them
        assert g["min"] == 0 and tool_passes(*key, misses) and not tool_passes(*key, [*misses, hits[0]])
    else:  # min 1: fails on uncounted calls alone, passes once one counted call joins them
        assert g["min"] == 1 and not tool_passes(*key, misses) and tool_passes(*key, [*misses, hits[0]])


def test_every_grader_has_samples():
    assert set(REGEX_SAMPLES) | set(TOOL_SAMPLES) == {(c, n) for c in CASES for n in names(c)}
    assert set(START) == {(c, n) for c in CASES for n in names(c)
                          if grader(c, n)["type"] == "regex" and isinstance(grader(c, n).get("target"), dict)}


def test_no_grader_frontmatter_line_holds_three_dashes_and_no_pattern_uses_inline_flags():
    # the runner ends a grader's frontmatter at the first `---`, and its regexes are JavaScript
    for case in CASES:
        for g in sorted((EVALS / case / "graders").glob("*.md")):
            lines = g.read_text(encoding="utf-8").split("\n")
            end = lines.index("---", 1)
            assert lines[0] == "---" and not [x for x in lines[1:end] if "---" in x], g
        for n in names(case):
            for key in ("pattern", "input_match"):
                assert not re.search(r"\(\?[imsx]+\)|\(\?P<", grader(case, n).get(key, "")), (case, n)

