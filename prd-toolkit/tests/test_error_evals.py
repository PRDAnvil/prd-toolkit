"""The 0.8.14 eval cases of handling-errors: a red run for code no adopted area covers, and a replay finding that is
never committed. Each scaffold runs clean in an empty directory, each grader is held to a passing and a failing
sample, and each case is walked on its start state as the skill says and as a wrong run does, with the graders read
on the end state."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
EVALS = ROOT / "evals"
RED = "error-uncovered-code-red-run"
REPLAY = "error-replay-finding-not-committed"
CASES = [RED, REPLAY]
STATE = {RED: "uncovered-bug", REPLAY: "green-before-fix"}
PRD = "docs/prd/greet"
LEDGER = f"{PRD}/errors.md"
GATE = '; echo "prd-error-exit=$?"'


def grader(case: str, name: str) -> dict:
    text = (EVALS / case / "graders" / f"{name}.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n")[1])


def names(case: str) -> list[str]:
    return sorted(g.stem for g in (EVALS / case / "graders").glob("*.md"))


def regex_passes(case: str, name: str, text: str) -> bool:
    g = grader(case, name)
    assert g["type"] == "regex" and "flags" not in g, (case, name)
    found = bool(re.search(g["pattern"], text))
    return not found if g.get("match") == "not_contains" else found


def file_text(ws: Path, case: str, name: str) -> str:
    """The text a file grader reads in `ws`; a missing file reads as empty."""
    p = ws / grader(case, name)["target"]["path"]
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def counted(case: str, name: str, tool_input: dict) -> bool:
    g = grader(case, name)
    assert g["type"] == "tool_used", (case, name)
    return bool(re.search(g["input_match"], json.dumps(tool_input, separators=(",", ":"))))


def tool_passes(case: str, name: str, session: list[dict]) -> bool:
    g = grader(case, name)
    n = sum(counted(case, name, x) for x in session)
    return g.get("min", 1) <= n <= g.get("max", float("inf"))


def use(i: str, cmd: str, tool: str = "Bash") -> str:
    key = "command" if tool == "Bash" else "file_path"
    return json.dumps({"type": "tool_use", "id": i, "name": tool, "input": {key: cmd}}, separators=(",", ":"))


def result(i: str, content: str) -> str:
    return json.dumps({"tool_use_id": i, "type": "tool_result", "content": content}, separators=(",", ":"))


def trace(*calls: tuple[str, str]) -> str:
    """A trace of Bash calls, each `(command, its output)`, in order, one tool_use and its tool_result per call."""
    return "\n".join(use(f"toolu_{n:02d}", c) + "\n" + result(f"toolu_{n:02d}", o) for n, (c, o) in enumerate(calls))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def commit(repo: Path, subject: str, refs: str, *paths: str) -> str:
    git(repo, "add", *paths)
    git(repo, "-c", "user.name=Eval", "-c", "user.email=eval@example.com", "-c", "commit.gpgsign=false",
        "commit", "-q", "-m", subject, "-m", f"Refs: {refs}")
    return git(repo, "rev-parse", "--short", "HEAD")


def committed(repo: Path, subject: str, refs: str, *paths: str) -> tuple[str, str]:
    """`git add` and `git commit` chained in one call, as a session writes it: (the command, git's own output)."""
    cmd = (f'git add {" ".join(paths)} && git -c user.name=Eval -c user.email=eval@example.com '
           f'-c commit.gpgsign=false commit -m "{subject}" -m "Refs: {refs}"')
    r = sh(repo, cmd)
    assert r.returncode == 0, r.stdout + r.stderr
    return cmd, r.stdout + r.stderr


def sh(repo: Path, cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, cwd=repo, capture_output=True, text=True)


def run_scaffold(tmp_path: Path, case: str) -> Path:
    ws = tmp_path / case
    ws.mkdir(parents=True)
    r = subprocess.run(["bash", str(EVALS / case / "scaffold.sh")], cwd=ws, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return ws


def copy(ws: Path, dst: Path) -> Path:
    """A second start state from the first, without its .venv (whose scripts name the first's path)."""
    shutil.copytree(ws, dst, symlinks=True, ignore=shutil.ignore_patterns(".venv"))
    return dst


# --- the cases and their scaffolds ---

def test_every_case_has_the_suite_form():
    for case in CASES:
        d = EVALS / case
        assert sorted(p.name for p in d.iterdir()) == ["case.yaml", "graders", "prompt.md", "scaffold.sh"], case
        cy = yaml.safe_load((d / "case.yaml").read_text(encoding="utf-8"))
        assert cy == {"schema_version": "1.1", "name": case, "context": {"scaffold_script": "scaffold.sh"}}
        s = (d / "scaffold.sh").read_text(encoding="utf-8")
        assert f'scaffolds/error_repo.py" "$PWD" {STATE[case]}\n' in s
        assert s.rstrip().endswith('test -z "$(git status --porcelain)"'), case
        text = (d / "prompt.md").read_text(encoding="utf-8")
        fm = yaml.safe_load(text.split("---\n")[1])
        assert fm["allowed_tools"] == ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash"]
        body = text.split("---\n", 2)[2].strip()
        assert body.startswith("/prd-toolkit:prd-error E-001\n"), case  # the command named in full
        assert "do not ask me questions" in body, case  # nobody to reply, as the other error cases say
        g = grader(case, "skill-fired")
        assert g["tool"] == "Skill" and "handling-errors" in g["input_match"] and g["min"] == 1


@pytest.mark.parametrize("case", CASES)
def test_the_scaffold_runs_clean_in_an_empty_directory(tmp_path, case):
    ws = run_scaffold(tmp_path, case)
    assert git(ws, "status", "--porcelain", "--untracked-files=all") == ""
    assert (ws / ".prd-toolkit/prdlint/errorreplay.py").is_file()  # this tree's replay, vendored
    # the start state passes every not_contains grader and every max-0 tool grader, and fails every other
    for n in names(case):
        g = grader(case, n)
        if g["type"] == "regex" and g.get("target", {}) != "trace" and "path" in g["target"]:
            want = g.get("match") == "not_contains" or n in ("prd-version-unchanged", "ledger-put-back")
            assert regex_passes(case, n, file_text(ws, case, n)) == want, n


# --- the samples: (passing, failing) for each regex grader ---

XCRUN = ("git: error: couldn't create cache file '<tmp>/xcrun_db-AbCd' (errno=Operation not permitted)\n"
         "git: error: couldn't create cache file '<tmp>/xcrun_db-EfGh' (errno=Operation not permitted)\n")
TEST = "tests/unit/test_count_names.py"
TOOL = "tools/count_names.py"
TEST_OUT = (f"[main bcd2623] test: failing test for E-001\n 1 file changed, 23 insertions(+)\n"
            f" create mode 100644 {TEST}")
FIX_OUT = "[main 8206135] fix: count only non-blank lines\n 1 file changed, 1 insertion(+), 1 deletion(-)"
BOTH_OUT = (f"[main 9d1c0aa] fix with its test\n 2 files changed, 24 insertions(+), 1 deletion(-)\n"
            f" create mode 100644 {TEST}")
LEDGER_OUT = "[main 2f3df44] docs(prd): resolve E-001\n 1 file changed, 1 insertion(+), 1 deletion(-)"
T_COMMIT = 'git commit -m "test: failing test for E-001" -m "Refs: E-001"'
F_COMMIT = 'git commit -m "fix: count only non-blank lines" -m "Refs: E-001"'
L_COMMIT = 'git commit -m "docs(prd): resolve E-001" -m "Refs: E-001"'
ADD_LEDGER = f"git add {LEDGER}"
AMEND = f'git add {TOOL} && git commit --amend -m "fix: count only non-blank lines" -m "Refs: E-001"'

RED_RUN = "Resolution: fixed in c002593, red run tests/unit/test_count_names.py [unit]\nRecurrence of: -\n"
RESOLVE = (".prd-toolkit/prd error resolve docs/prd/greet E-001 --commit c002593 --red-run "
           "tests/unit/test_count_names.py --level unit" + GATE)
CHECK = ".prd-toolkit/prd error check docs/prd/greet bcfddd2..HEAD" + GATE
COMMIT = 'git commit -m "docs(prd): resolve E-001" -m "Refs: E-001"'
SKILL_TEXT = ('<scripts>/prd error resolve docs/prd/<slug> <E-nnn> --commit <sha> --red-run <test id> --level <level>'
              '; echo "prd-error-exit=$?"\n... prd-error-exit=0 ... E-001 resolved code bug\n'
              "`<E-nnn>: <T-id> passes on <sha>^; <sha> did not turn it green`")
READ_SKILL = use("toolu_R", "/p/skills/handling-errors/running-an-error.md", "Read") + "\n" + result("toolu_R", SKILL_TEXT)

FIX = "027366e"
FINDING = f"E-001: T-001.2 passes on {FIX}^; {FIX} did not turn it green"
RESOLVE_T = f".prd-toolkit/prd error resolve docs/prd/greet E-001 --t T-001.2 --version 1.0.0 --commit {FIX}" + GATE
REPLAY_CMD = ".prd-toolkit/prd error replay docs/prd/greet E-001" + GATE
RESTORE = "git restore --staged --worktree docs/prd/greet/errors.md"
JSON_FINDING = json.dumps({"interface": 1, "kind": "error-replay", "entry": "E-001", "outcome": "findings",
                           "subject": "T-001.2", "reason": None, "findings": [FINDING], "runs": []})

HISTORY = trace((f"git add {TEST}", ""), (T_COMMIT, TEST_OUT), (f"git add {TOOL}", ""), (F_COMMIT, FIX_OUT),
                (RESOLVE, "E-001 resolved code bug"), (ADD_LEDGER, ""), (L_COMMIT, LEDGER_OUT))

REGEX_SAMPLES = {
    (RED, "test-committed-before-fix"): (
        [HISTORY,  # the shape of a real run: git's stderr noise first, then the commit's own report
         trace((f"git add {TEST}", XCRUN), (T_COMMIT, XCRUN + TEST_OUT), (F_COMMIT, XCRUN + FIX_OUT), (RESOLVE, "refused")),
         trace((f"git add {TEST} && {T_COMMIT}", TEST_OUT), (f"git add {TOOL} && {F_COMMIT}", FIX_OUT), (RESOLVE, "")),
         trace((f"git -C /w add {TEST}; git -C /w commit -q -m t", TEST_OUT), (f"git -C /w commit -m f", FIX_OUT),
               (RESOLVE, "")),
         trace((T_COMMIT.replace("git commit", "git -c user.name=E commit"), TEST_OUT), (F_COMMIT, FIX_OUT),
               (RESOLVE.removesuffix(GATE) + f" --level=unit", "")),
         trace((T_COMMIT, TEST_OUT.replace("test_count_names", "count_names_test")), (F_COMMIT, FIX_OUT),
               (RESOLVE, ""))],
        ["", trace((RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (RESOLVE, "")),  # no fix commit between the test and the resolve
         trace((T_COMMIT, TEST_OUT), (AMEND, BOTH_OUT), (RESOLVE, "")),  # the fix amended into the test's commit
         trace((T_COMMIT, TEST_OUT), (AMEND.replace("--amend -m", "-m") + " --amend", BOTH_OUT),
               (RESOLVE, "")),  # --amend after the messages
         trace((f"git add {TEST} {TOOL} && {F_COMMIT}", BOTH_OUT), (F_COMMIT, FIX_OUT), (RESOLVE, "")),  # one commit
         trace((F_COMMIT, FIX_OUT), (T_COMMIT, TEST_OUT), (RESOLVE, "")),  # the test after the fix
         trace((T_COMMIT, TEST_OUT), (F_COMMIT, FIX_OUT)),  # never resolved
         trace((RESOLVE, ""), (T_COMMIT, TEST_OUT), (F_COMMIT, FIX_OUT)),  # resolved first
         trace((T_COMMIT, TEST_OUT.replace(f"create mode 100644 {TEST}", f"create mode 100644 {TOOL}")),
               (F_COMMIT, FIX_OUT), (RESOLVE, "")),  # the first commit adds no test file
         trace((T_COMMIT, TEST_OUT.replace(" create mode 100644 " + TEST, "")), (F_COMMIT, FIX_OUT), (RESOLVE, "")),
         trace((T_COMMIT, "nothing to commit, working tree clean"), (F_COMMIT, FIX_OUT), (RESOLVE, "")),
         READ_SKILL + "\n" + trace((f"echo '{T_COMMIT}'", TEST_OUT))]),
    (RED, "fix-commit-cites-entry"): (
        [HISTORY,
         trace((T_COMMIT, TEST_OUT), (F_COMMIT.replace("Refs: E-001", "Refs: FR-001, E-001"), FIX_OUT), (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (f"git add {TOOL} && git commit -F - <<'EOF'\nfix\n\nRefs: E-001\nEOF", FIX_OUT),
               (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (f"git add {TOOL} && git -C /w commit -m fix -m 'Refs: E-001'", FIX_OUT),
               (RESOLVE, ""))],
        ["", trace((T_COMMIT, TEST_OUT), (F_COMMIT.replace("Refs: E-001", "Refs: none (no behaviour change)"), FIX_OUT),
                   (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (F_COMMIT.replace("E-001", "E-0011"), FIX_OUT), (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (F_COMMIT.replace("E-001", "E-002"), FIX_OUT), (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (F_COMMIT.replace("Refs: E-001", "Closes E-001"), FIX_OUT), (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (RESOLVE, ""), (F_COMMIT, FIX_OUT)),  # the fix after the resolve
         trace((F_COMMIT, BOTH_OUT), (RESOLVE, "")),  # no separate test commit before it
         trace((T_COMMIT, TEST_OUT), (RESOLVE, "")),
         trace((F_COMMIT, FIX_OUT), (T_COMMIT, TEST_OUT), (RESOLVE, "")),
         trace((T_COMMIT, TEST_OUT), (AMEND, BOTH_OUT), (RESOLVE, ""))]),  # the fix amended into the test's commit
    (RED, "resolution-committed"): (
        [HISTORY,
         trace((RESOLVE, "E-001 resolved code bug"), (ADD_LEDGER, ""), (L_COMMIT, LEDGER_OUT)),
         trace((RESOLVE, ""), (f"{ADD_LEDGER} && {L_COMMIT}", LEDGER_OUT)),
         trace((RESOLVE, ""), (f"git -C /w add {LEDGER} ; git -C /w commit -q -m x", "")),
         trace((RESOLVE + f" && {ADD_LEDGER} && {L_COMMIT}", "")),  # all in the resolve's own call
         trace((RESOLVE, ""), ("git add -A && git commit -m x", "")),
         trace((RESOLVE, ""), ("git add -u", ""), (L_COMMIT, "")),
         trace((RESOLVE, ""), ("git add .", ""), (L_COMMIT, "")),
         trace((RESOLVE, ""), ("git add . && git commit -m x", "")),
         trace((RESOLVE, ""), ("git add tests docs/prd/greet/errors.md", ""), (L_COMMIT, "")),
         trace((RESOLVE, ""), (f"git commit -a -m x", "")),
         trace((RESOLVE, ""), (f"git commit -am x", "")),
         trace((RESOLVE, ""), (f"git commit -m x -- {LEDGER}", "")),
         trace((RESOLVE, ""), (f"git commit -m x {LEDGER}", "")),
         trace((RESOLVE, ""), (f'git add "{LEDGER}"', ""), (L_COMMIT, "")),  # a quoted path
         trace((RESOLVE, ""), (f"git add {LEDGER}\n{L_COMMIT}", LEDGER_OUT)),  # two lines in one command
         trace((RESOLVE, ""), (f"git add {PRD}", ""), (L_COMMIT, "")),  # the folder
         trace((RESOLVE, ""), ("git add docs/prd", ""), (L_COMMIT, "")),
         trace((RESOLVE, ""), ("git add docs", ""), (L_COMMIT, ""))],
        ["", trace((RESOLVE, "E-001 resolved code bug")),  # left in the working tree
         trace((RESOLVE, ""), (ADD_LEDGER, "")),  # staged, never committed
         trace((ADD_LEDGER, ""), (L_COMMIT, ""), (RESOLVE, "")),  # committed before the resolve
         trace((RESOLVE, ""), (f"git add {TOOL}", ""), (L_COMMIT, "")),  # another file added
         trace((RESOLVE, ""), (L_COMMIT, "")),  # nothing named, nothing staged by name
         trace((RESOLVE, ""), (L_COMMIT, ""), (ADD_LEDGER, "")),  # the add after the commit
         trace((RESOLVE, ""), (f"git add {TOOL} && git commit -m 'update errors.md'", "")),  # the name only in a message
         trace((RESOLVE, ""), (f"git add {LEDGER}.bak && git commit -m x", "")),
         trace((RESOLVE, ""), ("git add .gitignore && git commit -m x", "")),
         trace((RESOLVE, ""), ("git commit --amend -m x", "")),
         use("toolu_R", "/p/skills/handling-errors/running-an-error.md", "Read") + "\n"
         + result("toolu_R", f"{RESOLVE}\n  git add {LEDGER}\n  git commit -m x")]),  # the skill's text, not a call
    (RED, "red-run-in-ledger"): (
        [RED_RUN, "Resolution: fixed in c002593277edbc3c05156d6ac5f6c214f3c78045, red run tests/unit/test_c.py::t [unit]"],
        ["Resolution: -\n", "Resolution: T-001.2 [unit], PRD 1.0.0, fixed in c002593\n",
         "Resolution: fixed in c002593, red run tests/unit/test_count_names.py [system]\n",
         "Resolution: 2026-11-20, fixed `count_names` to count only non-blank lines (tools/count_names.py)\n"]),
    (RED, "prd-version-unchanged"): (["---\nprd: greet\nversion: 1.0.0\nstatus: Approved\n"],
                                     ["---\nprd: greet\nversion: 1.0.1\nstatus: Approved\n"]),
    (RED, "resolved-with-red-run"): (
        [trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0")),
         trace((RESOLVE.removesuffix(GATE), "E-001 resolved code bug")),
         trace(("uv run --script /p/scripts/prd_error.py resolve docs/prd/greet E-001 --commit c002593 "
                "--red-run=tests/unit/test_count_names.py --level unit", "E-001 resolved code bug"))],
        [trace((RESOLVE, "refused: E-001: tests/unit/test_count_names.py passes on c002593^; c002593 did not turn "
                         "it green\nprd-error-exit=1")),
         trace((RESOLVE_T, "E-001 resolved code bug\nprd-error-exit=0")),
         READ_SKILL, trace(("git log --oneline", "E-001 resolved code bug"))]),
    (RED, "check-after-commit"): (
        [trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), ("git add docs/prd/greet/errors.md", ""),
               (COMMIT, "[main 2f3df44] docs(prd): resolve E-001"), (CHECK, "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"),
               ("git -C /w add docs/prd/greet/errors.md && git -C /w commit -m x", ""), (CHECK, "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), (COMMIT, ""),
               (CHECK.replace("bcfddd2..HEAD", "HEAD~4..HEAD"), "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), (COMMIT, ""),
               (CHECK.replace("bcfddd2..HEAD", "origin/main..HEAD"), "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"),
               (COMMIT + " && " + CHECK.replace("bcfddd2..HEAD", "HEAD~4..HEAD"), "prd-error-exit=0"))],
        [trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), (CHECK, "prd-error-exit=0"), (COMMIT, "")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), (COMMIT, ""),
               (CHECK, "errors.md: E-001: resolution is not one of the four forms\nprd-error-exit=1")),
         trace((COMMIT, ""), (CHECK, "prd-error-exit=0")),
         READ_SKILL + "\n" + trace((COMMIT, ""), (CHECK, "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), (COMMIT, ""),
               (".prd-toolkit/prd error list docs/prd/greet" + GATE, "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"), (COMMIT, ""),
               (CHECK.replace("bcfddd2..HEAD", "bcfddd2..HEAD~1"), "prd-error-exit=0")),
         trace((RESOLVE, "E-001 resolved code bug\nprd-error-exit=0"),
               (CHECK.removesuffix(GATE) + " && " + COMMIT + GATE, "prd-error-exit=0"))]),
    (REPLAY, "replay-reports-the-finding"): (
        [trace((RESOLVE_T, "E-001 resolved code bug\nprd-error-exit=0"), (REPLAY_CMD, FINDING + "\nprd-error-exit=1")),
         trace(("uv run --script /p/scripts/prd_error.py replay docs/prd/greet E-001 --json", JSON_FINDING))],
        [trace((REPLAY_CMD, "E-001 is not resolved\nprd-error-exit=1")),
         trace((REPLAY_CMD, f"E-001: T-001.2 fails on {FIX}^ and passes on {FIX}\nprd-error-exit=0")),
         READ_SKILL, trace((f"echo '{FINDING}'", FINDING))]),
    (REPLAY, "no-resolve-after-finding"): (
        [trace((RESOLVE_T, "E-001 resolved code bug"), (REPLAY_CMD, FINDING + "\nprd-error-exit=1"), (RESTORE, "")),
         trace((REPLAY_CMD, "E-001 is not resolved"), (RESOLVE_T, "E-001 resolved code bug"),
               (REPLAY_CMD, FINDING), (RESTORE, "")),
         READ_SKILL + "\n" + trace((RESOLVE_T, "E-001 resolved code bug"))],
        [trace((RESOLVE_T, "E-001 resolved code bug"), (REPLAY_CMD, FINDING), (RESTORE, ""),
               (RESOLVE_T.replace("T-001.2", "T-001.1"), "E-001 resolved code bug")),
         trace((RESOLVE_T, "E-001 resolved code bug"), (REPLAY_CMD, FINDING),
               (RESOLVE.replace("c002593", FIX), "refused: ..."))]),
    (REPLAY, "nothing-committed"): (
        ["", "0" * 40 + " " + "1" * 40 + " Eval <e@example.com> 1 +0000\tcheckout: moving from main to 027366e\n"],
        ["0" * 40 + " " + "1" * 40 + " Eval <e@example.com> 1 +0000\tcommit: docs(prd): resolve E-001\n",
         "a b c\treset: moving to HEAD~1\n", "a b c\trevert: Revert \"docs(prd): resolve E-001\"\n"]),
}


@pytest.mark.parametrize("key", list(REGEX_SAMPLES), ids=["/".join(k) for k in REGEX_SAMPLES])
def test_regex_grader_samples(key):
    good, bad = REGEX_SAMPLES[key]
    for s in good:
        assert regex_passes(*key, s), s
    for s in bad:
        assert not regex_passes(*key, s), s


# --- the samples for each tool_used grader: inputs it counts, and inputs it does not ---

ERRORS_EDIT = {"file_path": f"/w/{LEDGER}", "old_string": "Resolution: -", "new_string": "Resolution: x"}
SKILLS = [{"skill": "prd-toolkit:handling-errors"}, {"skill": "handling-errors"}]

TOOL_SAMPLES = {
    **{(c, "skill-fired"): (SKILLS, [{"skill": "prd-toolkit:changing-prds"}, {"skill": "prd-toolkit:prd-error"}])
       for c in CASES},
    (RED, "no-build-or-change"): (
        [{"skill": s} for s in ("prd-toolkit:prd-build", "prd-toolkit:prd-change", "prd-toolkit:building-from-prds",
                                "changing-prds", "prd-build")],
        [*SKILLS, {"skill": "prd-toolkit:prd-error"}, {"skill": "superpowers:systematic-debugging"}]),
    **{(c, "no-ledger-edit"): ([ERRORS_EDIT], [{"file_path": "/w/tools/count_names.py", "old_string": "a",
                                                "new_string": "b"}]) for c in CASES},
    **{(c, "no-ledger-write"): ([{"file_path": f"/w/{LEDGER}", "content": "x"}],
                                [{"file_path": "/t/tmp.x/evidence.txt", "content": "x"},
                                 {"file_path": "/w/tests/unit/test_count_names.py", "content": "x"}]) for c in CASES},
    (REPLAY, "resolve-ran"): (
        [{"command": RESOLVE_T}, {"command": f"uv run --script /p/scripts/prd_error.py resolve docs/prd/greet E-001 "
                                             f"--t=T-001.2 --version 1.0.0 --commit {FIX}"},
         {"command": f'"/p q/scripts/prd" error resolve docs/prd/greet E-001 --commit {FIX} --t T-001.2 --version 1.0.0'},
         {"command": RESOLVE_T.replace("--t T-001.2", '--t "T-001.2"')},
         {"command": RESOLVE_T.replace("--t T-001.2", "--t='T-001.2'")}],
        [{"command": REPLAY_CMD}, {"command": RESOLVE_T.replace("T-001.2", "T-001.21")},
         {"command": RESOLVE.replace("c002593", FIX)}, {"command": ".prd-toolkit/prd error list docs/prd/greet --open"},
         {"command": "grep -rn T-001.2 tests"}]),
    (REPLAY, "ledger-restored-with-git"): (
        [{"command": RESTORE}, {"command": RESTORE.replace("--staged --worktree", "--worktree --staged")},
         {"command": "git restore -S -W docs/prd/greet/errors.md"},
         {"command": "git restore -W -S docs/prd/greet/errors.md"},
         {"command": "git -C /w restore --staged --worktree docs/prd/greet/errors.md"},
         {"command": "cd docs/prd/greet && git restore errors.md"},
         {"command": RESTORE + GATE}],
        [{"command": "sed -i 's/^Resolution: .*/Resolution: -/' docs/prd/greet/errors.md"},
         {"command": "git checkout -- docs/prd/greet/errors.md"},
         {"command": "git checkout HEAD -- docs/prd/greet/errors.md"},
         {"command": "cp /w/orig.md docs/prd/greet/errors.md"},
         {"command": "git restore tests && echo docs/prd/greet/errors.md"},
         {"command": "git restore src/greet/cli.py; cat docs/prd/greet/errors.md"},
         {"command": "git diff docs/prd/greet/errors.md"}]),
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
    have = set(REGEX_SAMPLES) | set(TOOL_SAMPLES) | {(REPLAY, "ledger-put-back")}  # that one: on real files below
    assert have == {(c, n) for c in CASES for n in names(c)}


def test_no_grader_frontmatter_line_holds_three_dashes():
    # the eval runner ends a grader's frontmatter at the first `---` it meets, even inside a pattern
    for case in CASES:
        for g in sorted((EVALS / case / "graders").glob("*.md")):
            lines = g.read_text(encoding="utf-8").split("\n")
            end = lines.index("---", 1)
            assert lines[0] == "---" and not [x for x in lines[1:end] if "---" in x], g


def test_no_pattern_uses_inline_flags_the_runner_rejects():
    # the runner's regexes are JavaScript: no inline (?i), (?m), (?s) or named groups
    for case in CASES:
        for n in names(case):
            g = grader(case, n)
            for key in ("pattern", "input_match"):
                assert not re.search(r"\(\?[imsx]+\)|\(\?P<", g.get(key, "")), (case, n)


# --- the walks: each case on its start state, the right way and a wrong way ---

COUNT_TEST = '''"""tools/count_names.py prints the number of non-blank lines (E-001)."""
import importlib.util
from pathlib import Path

TOOL = Path(__file__).resolve().parents[2] / "tools/count_names.py"


def test_two_names_count_two():
    spec = importlib.util.spec_from_file_location("count_names", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.count_names("Ada\\nGrace\\n") == 2
'''
PLANTED = 'return len(text.split("\\n"))'
FIXED = "return sum(1 for line in text.splitlines() if line.strip())"


def _fix_helper(repo: Path) -> None:
    p = repo / TOOL
    p.write_text(p.read_text(encoding="utf-8").replace(PLANTED, FIXED), encoding="utf-8")


def _resolve_red_run(repo: Path, sha: str) -> tuple[str, subprocess.CompletedProcess]:
    cmd = f".prd-toolkit/prd error resolve {PRD} E-001 --commit {sha} --red-run {TEST} --level unit"
    return cmd, sh(repo, cmd)


def test_the_red_run_walk_passes_every_grader_and_a_wrong_run_fails_the_history(tmp_path):
    ws = run_scaffold(tmp_path, RED)
    wrong = copy(ws, tmp_path / "wrong")
    start = git(ws, "log", "--reverse", "--format=%P", "-G", "^### E-001 ", "--", LEDGER).split()[0]
    (ws / TEST).write_text(COUNT_TEST, encoding="utf-8")
    red = sh(ws, f"uv run pytest -q {TEST}")
    assert red.returncode == 1 and "assert 3 == 2" in red.stdout, red.stdout + red.stderr
    calls = [committed(ws, "test: failing test for E-001", "E-001", TEST)]
    _fix_helper(ws)
    calls.append(committed(ws, "fix: count only non-blank lines", "E-001", TOOL))
    sha = git(ws, "rev-parse", "--short", "HEAD")
    assert sh(ws, f"uv run pytest -q {TEST}").returncode == 0
    cmd, r = _resolve_red_run(ws, sha)
    assert (r.returncode, r.stdout) == (0, "E-001 resolved code bug\n"), r.stdout + r.stderr
    calls.append((cmd + GATE, r.stdout + "prd-error-exit=0"))
    calls.append(committed(ws, "docs(prd): resolve E-001", "E-001", LEDGER))
    check = sh(ws, f".prd-toolkit/prd error check {PRD} {start}..HEAD")
    assert (check.returncode, check.stdout) == (0, ""), check.stdout + check.stderr
    for n in ("red-run-in-ledger", "prd-version-unchanged"):
        assert regex_passes(RED, n, file_text(ws, RED, n)), n
    # the history graders read the trace, whose commit reports are git's own words
    for n in ("test-committed-before-fix", "fix-commit-cites-entry", "resolution-committed"):
        assert regex_passes(RED, n, trace(*calls)), n
    t = trace((cmd + GATE, r.stdout + "prd-error-exit=0"), (COMMIT, ""),
              (f".prd-toolkit/prd error check {PRD} {start}..HEAD" + GATE, "prd-error-exit=0"))
    for n in ("resolved-with-red-run", "check-after-commit"):
        assert regex_passes(RED, n, t), n

    # a wrong run: the test and the fix in one commit. With the test under tests/, which the greet area covers,
    # resolve refuses the commit.
    wrong2 = copy(wrong, tmp_path / "wrong2")
    (wrong / TEST).write_text(COUNT_TEST, encoding="utf-8")
    _fix_helper(wrong)
    sha = commit(wrong, "fix: count only non-blank lines, with its test", "E-001", TEST, TOOL)
    _, r = _resolve_red_run(wrong, sha)
    assert (r.returncode, r.stderr) == (1, f"refused: {sha} changes {TEST}, which area greet covers; resolve with a "
                                           "regression T-id\n"), r.stdout + r.stderr
    # with the test beside the helper, outside every area, the replay proves the one commit all the same (the test
    # is missing from the parent, so it fails there) and `check` passes: only the history graders see it.
    beside = "tools/test_count_names.py"
    (wrong2 / beside).write_text(COUNT_TEST.replace("parents[2]", "parents[1]"), encoding="utf-8")
    _fix_helper(wrong2)
    calls = [committed(wrong2, "fix: count only non-blank lines, with its test", "E-001", beside, TOOL)]
    sha = git(wrong2, "rev-parse", "--short", "HEAD")
    assert "2 files changed" in calls[0][1]
    r = sh(wrong2, f".prd-toolkit/prd error resolve {PRD} E-001 --commit {sha} --red-run {beside} --level unit")
    assert (r.returncode, r.stdout) == (0, "E-001 resolved code bug\n"), r.stdout + r.stderr
    calls.append((f".prd-toolkit/prd error resolve {PRD} E-001 --commit {sha} --red-run {beside} --level unit" + GATE,
                  r.stdout + "prd-error-exit=0"))
    calls.append(committed(wrong2, "docs(prd): resolve E-001", "E-001", LEDGER))
    assert sh(wrong2, f".prd-toolkit/prd error check {PRD} {start}..HEAD").returncode == 0
    for n in ("test-committed-before-fix", "fix-commit-cites-entry"):
        assert not regex_passes(RED, n, trace(*calls)), n
    assert regex_passes(RED, "resolution-committed", trace(*calls))
    assert regex_passes(RED, "red-run-in-ledger", file_text(wrong2, RED, "red-run-in-ledger"))


def test_a_hand_written_red_run_passes_check_and_fails_the_tool_graders(tmp_path):
    ws = run_scaffold(tmp_path, RED)
    (ws / TEST).write_text(COUNT_TEST, encoding="utf-8")
    commit(ws, "test: failing test for E-001", "E-001", TEST)
    _fix_helper(ws)
    sha = commit(ws, "fix: count only non-blank lines", "E-001", TOOL)
    ledger = ws / LEDGER
    line = f"Resolution: fixed in {sha}, red run {TEST} [unit]"
    ledger.write_text(ledger.read_text(encoding="utf-8").replace("Resolution: -", line), encoding="utf-8")
    commit(ws, "docs(prd): resolve E-001", "E-001", LEDGER)
    # check reads the form, not the runs, so a hand-written line passes it; the file graders pass too
    start = git(ws, "log", "--reverse", "--format=%P", "-G", "^### E-001 ", "--", LEDGER).split()[0]
    assert sh(ws, f".prd-toolkit/prd error check {PRD} {start}..HEAD").returncode == 0
    assert regex_passes(RED, "red-run-in-ledger", file_text(ws, RED, "red-run-in-ledger"))
    # what fails it: the Edit, and no resolve call in the trace
    assert not tool_passes(RED, "no-ledger-edit", [{"file_path": str(ledger), "old_string": "Resolution: -",
                                                    "new_string": line}])
    t = trace((COMMIT, ""), (f".prd-toolkit/prd error check {PRD} {start}..HEAD" + GATE, "prd-error-exit=0"))
    assert not regex_passes(RED, "resolved-with-red-run", t) and not regex_passes(RED, "check-after-commit", t)


def test_the_replay_walk_passes_every_grader_and_a_commit_after_findings_fails(tmp_path):
    ws = run_scaffold(tmp_path, REPLAY)
    wrong = copy(ws, tmp_path / "wrong")
    before = (ws / LEDGER).read_bytes()
    assert regex_passes(REPLAY, "ledger-put-back", before.decode("utf-8"))
    fix = git(ws, "rev-parse", "--short", "HEAD")
    resolve = f".prd-toolkit/prd error resolve {PRD} E-001 --t T-001.2 --version 1.0.0 --commit {fix}"
    r = sh(ws, resolve)
    assert (r.returncode, r.stdout) == (0, "E-001 resolved code bug\n"), r.stdout + r.stderr
    resolved = (ws / LEDGER).read_text(encoding="utf-8")
    assert f"Resolution: T-001.2 [unit], PRD 1.0.0, fixed in {fix}\n" in resolved
    assert not regex_passes(REPLAY, "ledger-put-back", resolved)
    replay = sh(ws, f".prd-toolkit/prd error replay {PRD} E-001")
    finding = f"E-001: T-001.2 passes on {fix}^; {fix} did not turn it green\n"
    assert (replay.returncode, replay.stdout) == (1, finding), replay.stdout + replay.stderr
    assert sh(ws, RESTORE).returncode == 0
    assert (ws / LEDGER).read_bytes() == before
    t = trace((resolve + GATE, r.stdout + "prd-error-exit=0"), (REPLAY_CMD, replay.stdout + "prd-error-exit=1"),
              (RESTORE, ""))
    for n in ("replay-reports-the-finding", "no-resolve-after-finding"):
        assert regex_passes(REPLAY, n, t), n
    for n in ("ledger-put-back", "nothing-committed"):
        assert regex_passes(REPLAY, n, file_text(ws, REPLAY, n)), n
    assert counted(REPLAY, "resolve-ran", {"command": resolve + GATE})
    assert counted(REPLAY, "ledger-restored-with-git", {"command": RESTORE})
    # a ledger staged before the replay is put back the same way
    assert sh(ws, resolve).returncode == 0 and sh(ws, f"git add {LEDGER}").returncode == 0
    assert sh(ws, f".prd-toolkit/prd error replay {PRD} E-001").returncode == 1
    assert sh(ws, RESTORE).returncode == 0
    assert (ws / LEDGER).read_bytes() == before and git(ws, "status", "--porcelain") == ""

    # the wrong run: the resolution committed after the finding
    assert sh(wrong, resolve).returncode == 0
    assert sh(wrong, f".prd-toolkit/prd error replay {PRD} E-001").returncode == 1
    commit(wrong, "docs(prd): resolve E-001", "E-001", LEDGER)
    for n in ("ledger-put-back", "nothing-committed"):
        assert not regex_passes(REPLAY, n, file_text(wrong, REPLAY, n)), n


def test_the_old_refusal_fails_only_the_resolve_and_the_replay(tmp_path):
    # the 0.8.13 baseline's B2 run: it ran the test on the parent by hand, then neither resolved nor committed. Its
    # end state is the start state; only the graders that need the resolve, the replay and the restore tell it apart.
    ws = run_scaffold(tmp_path, REPLAY)
    t = trace(("uv run --with pytest pytest -q -p no:cacheprovider test_greet.py", "2 passed"))
    session = [{"command": "uv run --with pytest pytest -q -p no:cacheprovider test_greet.py"}]
    failing = set()
    for n in names(REPLAY):
        g = grader(REPLAY, n)
        if g["type"] == "tool_used":
            ok = tool_passes(REPLAY, n, session if g["tool"] == "Bash" else
                             SKILLS[:1] if g["tool"] == "Skill" else [])
        else:
            ok = regex_passes(REPLAY, n, t if g["target"] == "trace" else file_text(ws, REPLAY, n))
        if not ok:
            failing.add(n)
    assert failing == {"resolve-ran", "replay-reports-the-finding", "ledger-restored-with-git"}
