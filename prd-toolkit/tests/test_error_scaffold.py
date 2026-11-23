"""The error_repo eval scaffold: seven start states of the greet repo (a planted bug, a failed deploy, a killed step, a
confirmed bug in code no adopted area covers, a confirmed bug whose fix commit its T-id's test never saw fail, a
proposed code bug read from the code that a run does not show, and a confirmed bug that HEAD no longer has)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "evals/scaffolds/error_repo.py"
PRD = "docs/prd/greet"
STATES = ["bug", "failed-deploy", "killed-step", "uncovered-bug", "green-before-fix", "read-only-bug", "confirmed-gone"]


def build(tmp_path: Path, state: str) -> tuple[Path, str]:
    dst = tmp_path / state
    r = subprocess.run([sys.executable, "-B", str(SCRIPT), str(dst), state], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return dst, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""


def tool(repo: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["uv", "run", "--script", script, *args], cwd=repo, capture_output=True, text=True)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


@pytest.fixture(params=STATES)
def built(request, tmp_path):
    repo, last = build(tmp_path, request.param)
    return request.param, repo, last


def test_every_state_is_clean_lints_and_traces(built):
    state, repo, _ = built
    assert git(repo, "status", "--porcelain", "--untracked-files=no") == ""
    assert (repo / ".prd-toolkit/prd_error.py").is_file()
    assert tool(repo, str(ROOT / "scripts/prd_lint.py"), PRD).returncode == 0
    assert tool(repo, str(ROOT / "scripts/prd_trace.py"), PRD).returncode == 0
    # R10: the managed CLAUDE.md block, as approval writes it, committed (it routes a plain prompt to the skills)
    claude = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- prd-toolkit:start -->" in claude and "<!-- prd-toolkit:end -->" in claude
    assert "goes to `/prd-toolkit:prd-error` (skill `prd-toolkit:handling-errors`) before any code changes" in " ".join(claude.split())
    assert git(repo, "ls-files", "CLAUDE.md").strip() == "CLAUDE.md"
    r = tool(repo, ".prd-toolkit/prd_block.py", PRD, "--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_bug_fails_one_test_and_keeps_every_status(tmp_path):
    repo, last = build(tmp_path, "bug")
    assert last == ""
    subject = git(repo, "log", "-1", "--format=%B")
    assert "Refs: FR-001" in subject
    assert git(repo, "diff", "--name-only", "HEAD~1", "HEAD").split() == ["src/greet/cli.py"]
    r = subprocess.run(["uv", "run", "pytest", "-q", "tests/unit"], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "1 failed, 1 passed" in r.stdout
    assert "test_greeting_comes_from_the_settings_file" in r.stdout
    feats = (repo / PRD / "features/greet.md").read_text(encoding="utf-8")
    assert feats.count("Status: verified (since 1.0.0)") == 2


def test_failed_deploy_has_an_open_unclassified_entry_and_a_passing_close(tmp_path):
    repo, last = build(tmp_path, "failed-deploy")
    assert last.startswith("run=")
    run_id = last.removeprefix("run=")
    errors = (repo / PRD / "errors.md").read_text(encoding="utf-8")
    assert "### E-001" in errors and "Classification: unclassified" in errors
    assert f"deploy run {run_id}, failed step " in errors
    log = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    head = (Path(log) / "prd-toolkit/deploys" / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines()[0]
    base = json.loads(head)["head"]
    fails = [r for r in map(json.loads, (Path(log) / "prd-toolkit/deploys" / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines())
             if r["kind"] == "step" and r["result"] == "fail"]
    assert len(fails) == 1
    assert f"deploy run {run_id}, failed step {fails[0]['step']}" in errors
    r = tool(repo, ".prd-toolkit/prd_deploy.py", "check", PRD, "--run", run_id, "--diff", f"{base}..HEAD")
    assert r.returncode == 0, r.stdout + r.stderr


def test_killed_step_refuses_to_resume(tmp_path):
    repo, last = build(tmp_path, "killed-step")
    assert last.startswith("run=")
    run_id = last.removeprefix("run=")
    r = tool(repo, ".prd-toolkit/prd_deploy.py", "resume", PRD, "--run", run_id)
    assert r.returncode == 1 and "started and did not finish" in r.stdout, r.stdout + r.stderr


def test_refuses_a_non_empty_destination_and_an_unknown_state(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "x/f").write_text("a")
    r = subprocess.run([sys.executable, "-B", str(SCRIPT), str(tmp_path / "x"), "bug"], capture_output=True, text=True)
    assert r.returncode != 0 and "is not empty" in r.stderr and "Traceback" not in r.stderr, r.stderr
    assert [p.name for p in (tmp_path / "x").iterdir()] == ["f"]
    r = subprocess.run([sys.executable, "-B", str(SCRIPT), str(tmp_path / "y"), "nope"], capture_output=True, text=True)
    assert r.returncode != 0 and "usage: error_repo.py" in r.stderr and "Traceback" not in r.stderr, r.stderr
    assert not (tmp_path / "y").exists()


def prd(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["sh", ".prd-toolkit/prd", *args], cwd=repo, capture_output=True, text=True)


ONE_TEST = "| unit | `uv run pytest tests/unit` | local | build | `uv run pytest -q` |"


def test_uncovered_bug_confirms_a_bug_outside_every_boundary(tmp_path):
    repo, last = build(tmp_path, "uncovered-bug")
    assert last == ""
    assert ONE_TEST in (repo / PRD / "testing.md").read_text(encoding="utf-8")
    assert "## 8. Adoption map\n\nSee adoption.md." in (repo / PRD / "prd.md").read_text(encoding="utf-8")
    assert "| greet | adopted | `src/greet/**`, `tests/**`, `scripts/**` |" in (repo / PRD / "adoption.md").read_text(encoding="utf-8")
    names = tmp_path / "names.txt"
    names.write_text("Ada\nGrace\n", encoding="utf-8")
    out = subprocess.run([sys.executable, "tools/count_names.py", str(names)], cwd=repo, capture_output=True, text=True)
    assert out.stdout == "3\n"  # the bug: two names print 3
    assert not list((repo / "tests").rglob("*count_names*"))
    r = prd(repo, "error", "list", PRD, "--open")
    assert r.returncode == 0 and r.stdout.startswith("E-001 confirmed code bug - tools/count_names.py counts"), r.stdout + r.stderr
    assert git(repo, "log", "--format=%s", "-3").splitlines() == [
        "docs(prd): confirm E-001", "docs(prd): propose E-001", "docs(prd): record E-001"]
    assert not (repo / ".git/hooks/post-commit").exists()  # no hook: the graders read the trace


def test_green_before_fix_hides_a_test_that_never_failed(tmp_path):
    repo, last = build(tmp_path, "green-before-fix")
    assert last == "fix=" + git(repo, "rev-parse", "--short", "HEAD").strip()
    assert git(repo, "log", "-1", "--format=%s%n%b", "HEAD").split("\n")[:3] == [
        "fix(greet): read GREETING from the settings file", "Refs: FR-001, E-001", ""]
    assert git(repo, "diff", "--name-only", "HEAD~1", "HEAD").split() == ["src/greet/cli.py"]
    assert ONE_TEST in (repo / PRD / "testing.md").read_text(encoding="utf-8")
    r = prd(repo, "error", "list", PRD, "--open")
    assert r.returncode == 0 and r.stdout.startswith("E-001 confirmed code bug FR-001 "), r.stdout + r.stderr
    feats = (repo / PRD / "features/greet.md").read_text(encoding="utf-8")
    assert feats.count("Status: verified (since 1.0.0)") == 2
    assert subprocess.run(["git", "grep", "-q", "known-failing", "--", f"{PRD}/test-cases", "tests"], cwd=repo).returncode == 1
    for rev in ("HEAD", "HEAD~1"):  # the T-001.2 test passes on the fix and on its parent
        wt = tmp_path / f"wt-{rev.replace('~', '-')}"
        git(repo, "worktree", "add", "-q", "--detach", str(wt), rev)
        r = subprocess.run(["uv", "run", "pytest", "-q", "tests/unit/test_greet.py"], cwd=wt, capture_output=True, text=True)
        assert r.returncode == 0 and "2 passed" in r.stdout, rev + r.stdout + r.stderr
        git(repo, "worktree", "remove", "--force", str(wt))


@pytest.mark.parametrize("state", ["uncovered-bug", "green-before-fix", "read-only-bug", "confirmed-gone"])
def test_the_red_run_states_build_the_same_commits(tmp_path, state):
    a, _ = build(tmp_path / "a", state)
    b, _ = build(tmp_path / "b", state)
    assert git(a, "rev-parse", "HEAD") == git(b, "rev-parse", "HEAD")


def greet_with_hi(repo: Path, tmp_path: Path) -> str:
    """What `greet World` prints with a settings file holding GREETING Hi, run from the source tree."""
    settings = tmp_path / "settings.json"
    settings.write_text('{"GREETING": "Hi"}', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "greet", "World"], cwd=repo, capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "PYTHONPATH": "src", "GREET_SETTINGS": str(settings)})
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def unit_tests(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["uv", "run", "pytest", "-q", "tests/unit"], cwd=repo, capture_output=True, text=True)


def test_read_only_bug_proposes_a_code_bug_from_a_code_reading_that_a_run_does_not_show(tmp_path):
    repo, last = build(tmp_path, "read-only-bug")
    assert last == ""
    cli = (repo / "src/greet/cli.py").read_text(encoding="utf-8")
    assert "{k.lower(): v for k, v in data.items()}" in cli  # reads as if keys were lowercased
    assert 'load_settings().get("GREETING", "Hello")' in cli
    assert greet_with_hi(repo, tmp_path) == "Hi, World!\n"  # but a run shows GREETING is read
    r = unit_tests(repo)
    assert r.returncode == 0 and "2 passed" in r.stdout, r.stdout + r.stderr
    assert "| greet | adopted |" in (repo / PRD / "adoption.md").read_text(encoding="utf-8")
    r = prd(repo, "error", "list", PRD, "--open")
    assert r.returncode == 0 and r.stdout.startswith("E-001 proposed code bug FR-001 "), r.stdout + r.stderr
    errors = (repo / PRD / "errors.md").read_text(encoding="utf-8")
    assert "adoption extract of greet (src/greet/cli.py:" in errors
    assert "Confirmed:" not in errors and "Evidence:" not in errors  # never run, never confirmed
    assert git(repo, "log", "--format=%s", "-2").splitlines() == ["docs(prd): propose E-001", "docs(prd): record E-001"]


def test_confirmed_gone_holds_a_confirmed_bug_that_head_no_longer_has(tmp_path):
    repo, last = build(tmp_path, "confirmed-gone")
    assert last == ""
    r = prd(repo, "error", "list", PRD, "--open")
    assert r.returncode == 0 and r.stdout.startswith("E-001 confirmed code bug FR-001 "), r.stdout + r.stderr
    body = git(repo, "log", "-1", "--format=%B")
    assert "E-001" not in body and "Refs: FR-001" in body  # the commit that fixed it never cites the entry
    assert git(repo, "diff", "--name-only", "HEAD~1", "HEAD").split() == ["src/greet/cli.py"]
    assert git(repo, "log", "--format=%s", "-4").splitlines()[1:] == [
        "docs(prd): confirm E-001", "docs(prd): propose E-001", "docs(prd): record E-001"]
    assert greet_with_hi(repo, tmp_path) == "Hi, World!\n"
    r = unit_tests(repo)
    assert r.returncode == 0 and "2 passed" in r.stdout, r.stdout + r.stderr
