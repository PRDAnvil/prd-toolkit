"""Build the start repo for the handling-errors and publishing-prds baselines and evals: the `greet`
repo of deploy_repo.py (Approved PRD at docs/prd/greet, every requirement `verified`, a vendored
`.prd-toolkit/`), put into a state that has an error.

Usage (from the eval workspace; never write into the plugin tree):
    python3 -B <this file> <dst> <bug|failed-deploy|killed-step|uncovered-bug|green-before-fix>

Every state first writes the managed CLAUDE.md block with the vendored `prd_block.py` and, when that
leaves `CLAUDE.md` or `docs` changed, commits it (`Refs: none (no behaviour change)`), as approval does:
the block is what routes a plain prompt to the skills. deploy_repo.py already commits the CLAUDE.md that
install wrote, so with the block unchanged there is no commit. The state's own commits come after it.

bug            `ready`, then one ordinary code commit ("Match settings keys case-insensitively",
               `Refs: FR-001`) that makes `greet <name>` read the key `greeting`, so a settings file
               holding `GREETING` is ignored and the command prints `Hello`. That breaks AC-001.2
               (GREETING from the settings file of its install) and, once the build is deployed,
               AC-002.1 too (both go through the changed line). At start only one test fails: the
               unit test citing T-001.2 (tests/unit/test_greet.py); T-001.1 passes, and T-002.1
               (a system test on a deployed install) fails once the build is deployed. Every requirement
               keeps its status: the bug is undetected, and the PRD, lint and trace are untouched.
failed-deploy  `failing-check` plus a real failed `prd_deploy.py run --until staging` and its close,
               committed: an open `unclassified` E-001 in errors.md (written by the vendored
               `prd_error.py new`, source "deploy run <id>, failed step <n>", n read from the log), so
               `prd_deploy.py check` passes on the close. Last stdout line `run=<id>`.
killed-step    `ready` plus a real run whose log is cut back to its header and one unfinished `start`
               record on step 1, as a killed process leaves it (the way test_deploy_recover.py builds
               it). Last stdout line `run=<id>`.
uncovered-bug  `ready` with a One test command on the unit level (`uv run pytest -q`), then an adoption
               map with one `adopted` area, greet (Boundary `src/greet/**`, `tests/**`, `scripts/**`),
               and `tools/count_names.py`, outside it, with no test and no PRD block: it counts the empty
               piece after a file's final newline as a name, so two names print 3, while its docstring
               says it prints the number of non-blank lines. E-001 for that bug is recorded, proposed as
               `code bug` and confirmed, each its own commit. Last, a post-commit hook (not tracked)
               appends one record per later commit to `.git/eval-commits.log`: its SHA, its Refs, the
               paths it changes, whether its tree still holds the bug, and whether its errors.md holds a
               red run, so a grader reads the order of the session's commits and what each holds.
green-before-fix  `ready` with the same One test command, then a commit that makes `main` read the key
               `greeting` (breaking AC-001.2) and rewrites the T-001.2 test to write both keys, so it
               passes whichever key the code reads; E-001 for the bug, recorded, proposed as `code bug`
               and confirmed; then the fix commit "fix(greet): read GREETING from the settings file"
               (`Refs: FR-001, E-001`), which does fix it and leaves the test as it is. FR-001 stays
               `verified` and no `known-failing` marker exists, so nothing on HEAD looks wrong: the
               T-001.2 test passes on the fix and on its parent, which only a replay shows. E-001 stays
               `confirmed`. Last stdout line `fix=<short sha>`.

In the last two states every ledger line is written by the vendored `prd_error.py` at a fixed date,
so every commit SHA is the same on every build of the same plugin tree.

The tracked tree is clean in every state. The vendored `.prd-toolkit/` comes from the plugin tree
this file sits in.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PLUGIN / "tests"))
import deploy_repo  # noqa: E402
from legacy import commit, git  # noqa: E402

STATES = ("bug", "failed-deploy", "killed-step", "uncovered-bug", "green-before-fix")
PRD = "docs/prd/greet"


def _tool(repo: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return deploy_repo._tool(repo, script, *args)


def _run(repo: Path, *args: str, expect: int) -> str:
    """Run the vendored prd_deploy.py; return the run id from its last stdout line."""
    r = _tool(repo, str(repo / ".prd-toolkit/prd_deploy.py"), "run", PRD, *args)
    if r.returncode != expect:
        sys.exit(f"error_repo: the run exited {r.returncode}, not {expect}:\n{r.stdout}{r.stderr}")
    return r.stdout.strip().splitlines()[-1].rsplit("run=", 1)[1]


def _log(repo: Path, run_id: str) -> Path:
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    return Path(common) / "prd-toolkit/deploys" / f"{run_id}.jsonl"


def _claude_md(repo: Path, date: str) -> None:
    r = _tool(repo, str(repo / ".prd-toolkit/prd_block.py"), PRD)
    if r.returncode != 0 or not (repo / "CLAUDE.md").is_file():
        sys.exit(f"error_repo: prd_block failed:\n{r.stdout}{r.stderr}")
    if git(repo, "status", "--porcelain", "--", "CLAUDE.md", "docs").strip():
        commit(repo,"Add the CLAUDE.md block\n\nRefs: none (no behaviour change)", "CLAUDE.md", "docs", date=date)


def _bug(repo: Path) -> None:
    cli = repo / "src/greet/cli.py"
    text = cli.read_text(encoding="utf-8")
    broken = text.replace('load_settings().get("GREETING", "Hello")', 'load_settings().get("greeting", "Hello")')
    if broken == text:
        sys.exit("error_repo: the greet source changed; update the planted bug")
    cli.write_text(broken, encoding="utf-8")
    commit(repo, "Match settings keys case-insensitively\n\nRefs: FR-001", "src", date="2026-01-06T12:00:00+0000")


def _failed_deploy(repo: Path) -> str:
    run_id = _run(repo, "--until", "staging", expect=4)
    records = [json.loads(line) for line in _log(repo, run_id).read_text(encoding="utf-8").splitlines()]
    base = records[0]["head"]
    failed = [r["step"] for r in records if r["kind"] == "step" and r["result"] == "fail"]
    if len(failed) != 1:
        sys.exit(f"error_repo: expected one failed step in the log, found {failed}")
    r = _tool(repo, str(repo / ".prd-toolkit/prd_error.py"), "new", PRD, "--title", "Staging deploy failed",
              "--source", f"deploy run {run_id}, failed step {failed[0]}")
    if r.returncode != 0:
        sys.exit(f"error_repo: prd_error new failed:\n{r.stdout}{r.stderr}")
    commit(repo, "Record the failed staging deploy as E-001", "docs", date="2026-01-07T12:00:00+0000")
    c = _tool(repo, str(repo / ".prd-toolkit/prd_deploy.py"), "check", PRD, "--run", run_id, "--diff", f"{base}..HEAD")
    if c.returncode != 0:
        sys.exit(f"error_repo: the close does not pass prd_deploy check:\n{c.stdout}{c.stderr}")
    return run_id


def _killed_step(repo: Path) -> str:
    run_id = _run(repo, expect=3)
    path = _log(repo, run_id)
    header = path.read_text(encoding="utf-8").splitlines()[0]
    start = {"kind": "start", "step": 1, "env": "staging", "command": "python3 scripts/deploy.py staging", "at": "2026-01-06T10:00:00+00:00"}
    path.write_text(header + "\n" + json.dumps(start) + "\n", encoding="utf-8")
    shutil.rmtree(repo / ".deploy", ignore_errors=True)
    return run_id


# --- the two red-run states: a ledger written at fixed dates, and a One test command ---

# Runs the vendored prd_error.py's own main() with a fixed date, inside the uv environment the
# `.prd-toolkit/prd` launcher uses, so every Detected:/Confirmed: date, and every SHA after it, is fixed.
_LEDGER = """import sys
from datetime import date
sys.path.insert(0, sys.argv[1])
import prd_error
sys.exit(prd_error.main(sys.argv[3:], today=date.fromisoformat(sys.argv[2])))
"""

LEVELS = """| Level | Harness command | Environment | Gate |
|---|---|---|---|
| unit | `uv run pytest tests/unit` | local | build |
| system | `uv run pytest tests/system` | staging | deploy |
| smoke | `uv run pytest tests/smoke` | production | deploy |
"""

LEVELS_ONE_TEST = """| Level | Harness command | Environment | Gate | One test |
|---|---|---|---|---|
| unit | `uv run pytest tests/unit` | local | build | `uv run pytest -q` |
| system | `uv run pytest tests/system` | staging | deploy |  |
| smoke | `uv run pytest tests/smoke` | production | deploy |  |
"""

ADOPTION = """# Adoption map

| Area | State | Boundary |
|---|---|---|
| greet | adopted | `src/greet/**`, `tests/**`, `scripts/**` |
"""

COUNT_NAMES = '''#!/usr/bin/env python3
"""Count the names in a guest-list file (one name per line): python3 tools/count_names.py <file>.

Prints the number of non-blank lines, so a list can be checked before `greet` is run for each name.
"""
import sys
from pathlib import Path


def count_names(text: str) -> int:
    return len(text.split("\\n"))


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: count_names.py <file>")
        return 2
    print(count_names(Path(argv[0]).read_text(encoding="utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

# The planted line of tools/count_names.py, as the file holds it; the recorder greps for it.
COUNT_BUG = 'return len(text.split("\\n"))'

COUNT_EVIDENCE = [
    "printf 'Ada\\nGrace\\n' > names.txt",
    "python3 tools/count_names.py names.txt",
    "3",
    "The file holds two names; the docstring says it prints the number of non-blank lines.",
]

COUNT_DIAGNOSIS = (
    "`count_names` returns `len(text.split(\"\\n\"))`, which counts the empty piece after the final "
    "newline (and any blank line) as a name, so a file of two names prints 3. The docstring says "
    "`Prints the number of non-blank lines`. tools/count_names.py lies outside the Boundary of the "
    "only adopted area, greet, and no PRD block describes it."
)

# The recorder: one record per commit the session makes, appended to .git/eval-commits.log.
RECORDER = """#!/bin/sh
# Eval recorder (scaffolds/error_repo.py uncovered-bug): one record per commit, for the graders.
log="$(git rev-parse --git-common-dir)/eval-commits.log"
{
  echo "commit $(git rev-parse HEAD)"
  echo "refs: $(git log -1 --format='%(trailers:key=Refs,valueonly,separator=%x2C )' HEAD)"
  git diff-tree --no-commit-id --name-only -r --root HEAD | sed 's/^/path: /'
  if git show HEAD:tools/count_names.py 2>/dev/null | grep -qF 'BUG'; then echo "helper: bug"; else echo "helper: no bug"; fi
  if git show HEAD:docs/prd/greet/errors.md 2>/dev/null | grep -qE '^Resolution: fixed in [0-9a-f]{7,40}, red run [^ ]+ [[]'; then
    echo "ledger: red run"
  else
    echo "ledger: no red run"
  fi
  echo "end"
} >> "$log"
""".replace("BUG", COUNT_BUG)

GREET_EVIDENCE = [
    "settings.json holds {\"GREETING\": \"Hi\"}",
    "GREET_SETTINGS=settings.json PYTHONPATH=src python3 -m greet World",
    "Hello, World!",
    "Expected Hi, World!",
]

GREET_DIAGNOSIS = (
    "`main` in src/greet/cli.py reads `load_settings().get(\"greeting\", \"Hello\")`, so a settings file "
    "holding `GREETING` is ignored and the default Hello is printed. AC-001.2: \"When `greet <name>` "
    "runs, it shall print `<GREETING>, <name>!`, taking GREETING from the settings file of its install.\""
)

GOOD = 'load_settings().get("GREETING", "Hello")'
BAD = 'load_settings().get("greeting", "Hello")'


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        sys.exit(f"error_repo: {path.name} changed; update the scaffold ({old!r} not found)")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _ledger(repo: Path, day: str, *args: str) -> str:
    """Run the vendored prd_error.py with `args` on the date `day`; exit on anything but 0."""
    kit = repo / ".prd-toolkit"
    cmd = ["uv", "run", "--quiet", "--no-project", "--project", str(kit), "--with-requirements",
           str(kit / "requirements.txt"), "python", "-I", "-c", _LEDGER, str(kit), day, *args]
    r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(f"error_repo: prd_error {args[0]} exited {r.returncode}:\n{r.stdout}{r.stderr}")
    return r.stdout.strip()


def _entry(repo: Path, days: tuple[str, str, str], title: str, evidence: list[str], cls: str, diagnosis: str,
           reply: str, touches: str = "") -> None:
    """E-001 recorded, proposed and confirmed, each its own commit, as running-an-error.md steps 1, 3 and 4."""
    ev = Path(tempfile.mkdtemp(prefix="error-repo-evidence-")) / "evidence.txt"
    ev.write_text("\n".join(evidence) + "\n", encoding="utf-8")
    t = ["--touches", touches] if touches else []
    if _ledger(repo, days[0], "new", PRD, "--title", title, "--source", "user report (/prd-toolkit:prd-error)",
               "--evidence-file", str(ev), *t) != "E-001":
        sys.exit("error_repo: the entry is not E-001")
    shutil.rmtree(ev.parent)
    commit(repo, "docs(prd): record E-001\n\nRefs: E-001", f"{PRD}/errors.md", date=f"{days[0]}T09:00:00+0000")
    _ledger(repo, days[1], "propose", PRD, "E-001", "--class", cls, "--diagnosis", diagnosis, *t)
    commit(repo, "docs(prd): propose E-001\n\nRefs: E-001", f"{PRD}/errors.md", date=f"{days[1]}T10:00:00+0000")
    _ledger(repo, days[2], "confirm", PRD, "E-001", "--reply", reply)
    commit(repo, "docs(prd): confirm E-001\n\nRefs: E-001", f"{PRD}/errors.md", date=f"{days[2]}T11:00:00+0000")


def _one_test(repo: Path) -> None:
    _replace(repo / PRD / "testing.md", LEVELS, LEVELS_ONE_TEST)
    commit(repo, "PRD: a One test command for the unit level\n\nRefs: none (no behaviour change)", "docs",
           date="2026-01-05T19:00:00+0000")


def _uncovered_bug(repo: Path) -> None:
    _one_test(repo)
    _replace(repo / PRD / "prd.md", "## 8. Adoption map\n\nNot applicable: new project.",
             "## 8. Adoption map\n\nSee adoption.md.")
    (repo / PRD / "adoption.md").write_text(ADOPTION, encoding="utf-8")
    _tool(repo, str(repo / ".prd-toolkit/prd_block.py"), PRD)
    commit(repo, "PRD: map the greet area as adopted\n\nRefs: none (no behaviour change)", "docs", "CLAUDE.md",
           date="2026-01-06T12:00:00+0000")
    tool = repo / "tools/count_names.py"
    tool.parent.mkdir()
    tool.write_text(COUNT_NAMES, encoding="utf-8")
    commit(repo, "Add a guest-list counter", "tools", date="2026-01-07T12:00:00+0000")
    _entry(repo, ("2026-01-08", "2026-01-08", "2026-01-09"), "tools/count_names.py counts one name too many",
           COUNT_EVIDENCE, "code bug", COUNT_DIAGNOSIS, "Yes, that is a code bug in the helper.")
    hook = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()) / "hooks/post-commit"
    if hook.exists():
        sys.exit(f"error_repo: {hook} exists; the recorder would replace it")
    hook.write_text(RECORDER, encoding="utf-8")
    hook.chmod(0o755)


def _green_before_fix(repo: Path) -> str:
    _one_test(repo)
    cli = repo / "src/greet/cli.py"
    test = repo / "tests/unit/test_greet.py"
    _replace(cli, GOOD, BAD)
    _replace(test, "settings.write_text('{\"GREETING\": \"Hi\"}', encoding=\"utf-8\")",
             "settings.write_text('{\"GREETING\": \"Hi\", \"greeting\": \"Hi\"}', encoding=\"utf-8\")")
    _replace(test, 'assert load_settings() == {"GREETING": "Hi"}', 'assert load_settings()["GREETING"] == "Hi"')
    commit(repo, "Match settings keys case-insensitively\n\nRefs: FR-001", "src", "tests", date="2026-01-06T12:00:00+0000")
    _entry(repo, ("2026-01-07", "2026-01-07", "2026-01-08"), "greet ignores GREETING in the settings file",
           GREET_EVIDENCE, "code bug", GREET_DIAGNOSIS, "Yes, it is a code bug.", touches="FR-001")
    _replace(cli, BAD, GOOD)
    commit(repo, "fix(greet): read GREETING from the settings file\n\nRefs: FR-001, E-001", "src",
           date="2026-01-09T12:00:00+0000")
    return git(repo, "rev-parse", "--short", "HEAD").strip()


def main(dst: str, state: str) -> None:
    repo = Path(dst).resolve()
    deploy_repo.main(dst, "failing-check" if state == "failed-deploy" else "ready")
    _claude_md(repo, "2026-01-06T18:00:00+0000" if state == "failed-deploy" else "2026-01-05T18:00:00+0000")
    last = ""
    if state == "bug":
        _bug(repo)
    elif state == "failed-deploy":
        last = f"run={_failed_deploy(repo)}"
    elif state == "killed-step":
        last = f"run={_killed_step(repo)}"
    elif state == "uncovered-bug":
        _uncovered_bug(repo)
    else:
        last = f"fix={_green_before_fix(repo)}"
    status = git(repo, "status", "--porcelain", "--untracked-files=no").strip()
    if status:
        sys.exit(f"error_repo: the tracked tree is not clean:\n{status}")
    if state in ("uncovered-bug", "green-before-fix"):
        lint = subprocess.run(["sh", ".prd-toolkit/prd", "lint", PRD], cwd=repo, capture_output=True, text=True,
                              encoding="utf-8")
        if lint.returncode != 0:
            sys.exit(f"error_repo: prd lint exited {lint.returncode}:\n{lint.stdout}{lint.stderr}")
    if last:
        print(last)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in STATES:
        sys.exit(f"usage: error_repo.py <dst> <{'|'.join(STATES)}>")
    main(sys.argv[1], sys.argv[2])
