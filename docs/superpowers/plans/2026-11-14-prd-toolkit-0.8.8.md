# prd-toolkit 0.8.8: invocation — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A clone or worktree that vendors the toolkit adds no uv environment of its own, and one `prd` command runs every script.

**Architecture:** An `sh` launcher (`prd`) holds one uv line that uses `--with-requirements`, so uv keeps one environment per requirements list and none per script path. Behind it a dispatcher replaces its process with the named `prd_*.py`, so each script still prints its own usage, prefix and exit code. Only the callers that run a vendored copy move to the launcher.

**Tech stack:** POSIX `sh`, Python 3.11+, uv, pytest with pytest-xdist. No new Python dependency.

**Execution (owner, 2026-11-14):** subagent-driven. Subagents run on Opus 5.5, or on a cheaper model where the task is mechanical enough for it (Task 8's wording, Task 0's baseline).

**Spec:** `docs/superpowers/specs/2026-11-14-prd-toolkit-0.8.8-invocation-design.md`. Read it with this plan; where they differ, the spec wins and the difference is recorded in its Revisions note.

## Global constraints

- **Branch:** `feat/prd-toolkit-0.8.8`, in worktree `.worktrees/prd-toolkit-0.8.8`, cut from `main` after the spec branch (`docs/prd-toolkit-0.8.8-spec`) is merged. Never work in the main checkout.
- **Author:** Ivan Histand <ivan@badgeretl.com> (the clone's git config). Every commit carries `Refs: <IDs>` or `Refs: none (no behaviour change)`. Never `--no-verify`, never a bare `git stash`.
- **Unchanged:** every existing script's name, usage line, stderr prefix and exit codes; the scripts' uv headers; the 80 skill lines that run the plugin's own scripts; the README's examples.
- **The vendored copy** (`.prd-toolkit/`) matches the plugin byte for byte. After a change to a file vendoring copies, run `uv run --script prd-toolkit/scripts/prd_hooks.py vendor docs/prd/prd-toolkit` and commit the refresh in the same commit. Never edit it by hand.
- **Tests:** unit `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`; integration `uv run --directory prd-toolkit pytest -q -n auto tests/prd`. Never edit a test that cites a non-unit T-id (`@prd T-…`).
- **Skill text** (Task 6) follows `superpowers:writing-skills`. Code follows `superpowers:test-driven-development`.
- **Public repository:** no commit names a private organization, host, person or object.
- The launcher's uv line, exactly: `uv run --quiet --no-project --python ">=3.11" --with-requirements "$here/requirements.txt" python "$here/prd_dispatch.py" "$@"`.
- The 17 commands: `block`, `build-check`, `change`, `confirm`, `context`, `deploy`, `drift`, `error`, `gates`, `git-hook`, `hooks`, `judge`, `links`, `lint`, `publish`, `status`, `trace`.

## Facts already checked (2026-11-14, on bfb63da)

- `prd_tester_guard.py` does not match a vendored script by the `uv run --script` form; it needs no change. `scripts/ci-local.sh` reads the workflow's `run:` lines and matches no command text; it needs no change.
- The 18 vendored-path lines: `skills/coordinating-prds/running-a-change-set.md` (13), `skills/changing-prds/SKILL.md:372-373`, `skills/testing-from-prds/SKILL.md:150`, `skills/testing-from-prds/dispatching.md:111`, `agents/prd-tester.md:37`. Templates: `templates/claude-block.md:18`, `templates/readme-prds.md:21`, `templates/hooks/pre-commit`, `templates/hooks/commit-msg`.
- Tests that pin the old form: `tests/test_hooks_install.py:141`, `tests/test_hooks_stale.py:40-41,147`, `tests/test_hooks_ci.py` (3 lines), `tests/test_coordinating_skill.py:153,165-167`.
- Eval graders that match a script name in a command: `change-set-no-snapshot-edit/graders/no-bash-write.md`, `changing-hands-off-to-change-set/graders/impact-run.md`, `coordinating-not-for-one-repo/graders/no-changeset-new.md`, and the three under `tester-judged-calls-judge/graders/`.
- `packs.in_range("0.8.10", ">=0.8.0,<0.9")` is true, so pack manifests stay as they are.
- uv 0.13.8: `--script` keys an environment on the script path; `--with-requirements` keys one on the requirements. A uv-managed interpreter that already holds a required package needs no environment for it, so a count test must use the full five-line file.

## Review focus

Failure modes the spec implies and a careless build would miss. Each has its test in the task named.

1. **A host repository with its own `pyproject.toml`.** uv must not sync or lock it. Task 2, `test_launcher_ignores_host_project`.
2. **A branch whose vendored copy predates 0.8.8.** The new shim must skip, not fail the commit. Task 4, `test_shim_skips_without_launcher`.
3. **A path with a space**, in the clone's path or the PRD folder's. Task 2, `test_launcher_path_with_spaces`; Task 4, `test_shim_prd_path_with_space`.
4. **A checkout that lost the executable bit.** Shims and CI go through `sh`. Task 4, `test_shim_runs_launcher_without_exec_bit`.
5. **Graders that no longer see the command.** A grader matching `prd_links\.py` silently passes or fails once the skill types `prd links`. Task 6, the grader tests.

---

### Task 0: Branch and baseline

**Files:** none changed.

- [ ] **Step 1:** Confirm `git log origin/main --oneline -5` holds the merge of `docs/prd-toolkit-0.8.8-spec`. If not, stop and report.
- [ ] **Step 2:** `git worktree add -b feat/prd-toolkit-0.8.8 .worktrees/prd-toolkit-0.8.8 origin/main`. Check `git config user.email` prints `ivan@badgeretl.com`.
- [ ] **Step 3:** Run both test commands. Record the two pass counts in the progress ledger; a failure here is reported, not fixed.

---

### Task 1: The dispatcher and the requirements file

**Files:**
- Create: `prd-toolkit/scripts/prd_dispatch.py`, `prd-toolkit/scripts/requirements.txt`
- Test: `prd-toolkit/tests/test_dispatch.py`

**Interfaces:**
- Produces: `prd_dispatch.COMMANDS: dict[str, str]` (command → script file name); `prd_dispatch.main(argv: list[str]) -> int` (returns only for help, version and errors; otherwise `os.execv`); `scripts/requirements.txt`.

- [ ] **Step 1: Write the failing tests.** Each runs `[sys.executable, SCRIPTS / "prd_dispatch.py", *args]` as a subprocess, as `testing.md`'s Harness Lifecycle says.

```python
def test_dispatch_table_covers_every_script():
    have = {p.name for p in SCRIPTS.glob("prd_*.py")} - {"prd_dispatch.py", "prd_tester_guard.py"}
    assert set(prd_dispatch.COMMANDS.values()) == have
    assert all(cmd == f[4:-3].replace("_", "-") for cmd, f in prd_dispatch.COMMANDS.items())

def test_dispatch_output_is_the_scripts():
    a, b = run("lint", "--help"), run_script("prd_lint.py", "--help")
    assert (a.returncode, a.stdout, a.stderr) == (b.returncode, b.stdout, b.stderr)

def test_dispatch_exit_codes(prd):          # the orders fixture lints clean
    assert run("lint", str(prd)).returncode == 0
    edit(prd, "prd.md", "status: Approved", "status: Nonsense")
    assert run("lint", str(prd)).returncode == 1
    assert run("lint", str(prd / "missing")).returncode == 2

def test_dispatch_help():
    for args in ((), ("-h",), ("--help",)):
        r = run(*args)
        lines = r.stdout.splitlines()
        assert r.returncode == 0 and lines[0] == "usage: prd <command> [arguments]"
        assert [ln.split()[0] for ln in lines[1:]] == sorted(prd_dispatch.COMMANDS)

def test_dispatch_version():
    assert run("--version").stdout.strip() == PLUGIN_VERSION

def test_dispatch_unknown_command():
    r = run("nope")
    assert r.returncode == 2 and r.stderr.splitlines()[0] == "prd: unknown command 'nope'"

def test_dispatch_missing_script(tmp_path):  # a copy of the dispatcher with no prd_lint.py beside it
    r = run_copy(tmp_path, "lint")
    assert r.returncode == 2
    assert r.stderr.strip() == f"prd: prd_lint.py is not in {tmp_path}; run prd_hooks.py install"

def test_requirements_is_the_headers_union():
    union = sorted({dep for f in prd_dispatch.COMMANDS.values() for dep in header_deps(SCRIPTS / f)})
    assert (SCRIPTS / "requirements.txt").read_text().splitlines() == union
```

- [ ] **Step 2:** Run `pytest -q tests/test_dispatch.py`. Expected: every test fails on the missing module.
- [ ] **Step 3: Implement `prd_dispatch.py`.** It carries the same uv header as `prd_lint.py` and the module docstring `"""Run one prd-toolkit script by its command name. Exit 2 on an unknown command; otherwise the script's own exit code."""`. `COMMANDS` is built once from a literal tuple of the 17 names. Help's second column is the first line of each script's docstring, read with `ast.get_docstring` (no import). Version reads `VERSION` beside the file when it exists, else `../.claude-plugin/plugin.json`. Before `os.execv`, flush stdout and stderr.
- [ ] **Step 4:** Write `requirements.txt`: the five lines in the spec's section 3.3, sorted, LF, one trailing newline.
- [ ] **Step 5:** Run the file's tests. Expected: all pass.
- [ ] **Step 6: Commit** `feat(invocation): the prd dispatcher and requirements.txt`, `Refs: none (no behaviour change)`.

---

### Task 2: The launcher

**Files:**
- Create: `prd-toolkit/scripts/prd` (mode 755)
- Test: `prd-toolkit/tests/test_launcher.py`

**Interfaces:**
- Consumes: `prd_dispatch.py`, `requirements.txt` (Task 1).
- Produces: `scripts/prd`, run as `sh <dir>/prd <command> …` or directly.

- [ ] **Step 1: Write the failing tests.** A helper `copy_scripts(dest)` copies `prd`, `prd_dispatch.py`, `requirements.txt`, `prd_status.py` and `prdlint/` into `dest`. Every test passes its own `UV_CACHE_DIR` under `tmp_path`, so pytest-xdist workers cannot change the count.

```python
def test_launcher_two_clones_one_environment(tmp_path):
    cache = tmp_path / "cache"
    for name in ("clone a", "clone-b"):
        copy_scripts(tmp_path / name)
        r = launch(tmp_path / name, "--version", cache=cache)
        assert r.returncode == 0, r.stderr
    assert len(list((cache / "environments-v2").iterdir())) == 1

def test_launcher_ignores_host_project(tmp_path):
    host = tmp_path / "host"; copy_scripts(host / ".prd-toolkit")
    (host / "pyproject.toml").write_text('[project]\nname="h"\nversion="0"\ndependencies=["no-such-package-xyz==9.9.9"]\n')
    r = launch(host / ".prd-toolkit", "--version", cwd=host)
    assert r.returncode == 0, r.stderr
    assert not (host / ".venv").exists() and not (host / "uv.lock").exists()

def test_launcher_first_run_quiet(tmp_path):
    copy_scripts(tmp_path / "c")
    r = launch(tmp_path / "c", "--version", cache=tmp_path / "empty-cache")
    assert r.returncode == 0 and r.stderr == ""

def test_launcher_without_uv(tmp_path):
    copy_scripts(tmp_path / "c")
    r = launch(tmp_path / "c", "--version", path="/usr/bin:/bin")   # no uv there
    assert r.returncode == 2 and r.stderr == "prd: uv is not on PATH; install uv\n"

def test_launcher_from_another_cwd(tmp_path): ...     # cwd=tmp_path / "elsewhere": exit 0
def test_launcher_path_with_spaces(tmp_path): ...     # the "clone a" case, alone, with an argument holding a space passed through intact
def test_launcher_is_executable():
    assert os.access(SCRIPTS / "prd", os.X_OK)
```

- [ ] **Step 2:** Run them. Expected: fail, `prd` does not exist.
- [ ] **Step 3: Write `scripts/prd`** as the spec's section 3.1 gives it, the uv line exactly as in Global constraints. `chmod 755`, and `git update-index --chmod=+x` after `git add`.
- [ ] **Step 4:** Run the file's tests. Expected: all pass. If `test_launcher_without_uv` finds uv under `/usr/bin` on the runner, build the `PATH` from a temporary directory holding symlinks to `sh`, `dirname` and `pwd` only.
- [ ] **Step 5: Commit** `feat(invocation): the prd launcher`, `Refs: none (no behaviour change)`.

---

### Task 3: Vendoring

**Files:**
- Modify: `prd-toolkit/scripts/prdlint/hooks.py:15` (`VENDORED`)
- Test: `prd-toolkit/tests/test_hooks_vendor.py`, `prd-toolkit/tests/test_vendored_copy.py`
- Refresh: `.prd-toolkit/`

**Interfaces:**
- Produces: `.prd-toolkit/prd`, `.prd-toolkit/prd_dispatch.py`, `.prd-toolkit/requirements.txt` in every vendored copy; `hooks.LAUNCHER = "prd"`.

- [ ] **Step 1: Write the failing tests.** `test_vendor_copies_the_launcher`: after `hooks.install(repo, PRD)`, the three files exist, `.prd-toolkit/prd` is executable, and `sh .prd-toolkit/prd --version` run in `repo` prints the plugin version. `test_check_reports_missing_launcher`: unlink `.prd-toolkit/prd`; `hooks.check` returns `[".prd-toolkit/prd is missing"]`. Extend `test_vendored_copy.py` so the three files are compared byte for byte and the vendored launcher's mode is 755.
- [ ] **Step 2:** Run them. Expected: fail.
- [ ] **Step 3:** Add the three names to `VENDORED` and `LAUNCHER = "prd"` beside it. `_vendor` already copies with `shutil.copy2`, which keeps the mode; `check` already walks `VENDORED`.
- [ ] **Step 4:** Run `prd_hooks.py vendor docs/prd/prd-toolkit`; run both test files and `tests/test_hooks_install.py`. Expected: pass.
- [ ] **Step 5: Commit** with the refreshed `.prd-toolkit/`: `feat(invocation): vendor the launcher`, `Refs: none (no behaviour change)`.

---

### Task 4: The hook shims

**Files:**
- Modify: `prd-toolkit/templates/hooks/pre-commit`, `prd-toolkit/templates/hooks/commit-msg`, `prd-toolkit/scripts/prdlint/hooks.py` (`_append_line` at 248, `install` at 274, `check` at 377)
- Test: `prd-toolkit/tests/test_hooks_install.py`, `prd-toolkit/tests/test_git_hook.py`
- Refresh: `.prd-toolkit/`

**Interfaces:**
- Consumes: `hooks.LAUNCHER` (Task 3).
- Produces: `hooks.OLD_FORM: re.Pattern` matching a line that holds both `uv run --script` and `prd_git_hook.py`; `install` lines `replaced <shown>/<hook> (it used uv run --script)`; `check` lines `stale: <shown>/<hook>; run prd_hooks.py install`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_shim_uses_the_launcher(repo):
    hooks.install(repo, PRD)
    shim = (repo / ".git/hooks/pre-commit").read_text()
    assert 'exec sh "$top/.prd-toolkit/prd" git-hook pre-commit "$top/docs/prd/orders"' in shim
    assert "--script" not in shim

def test_shim_skips_without_launcher(repo):      # a vendored copy older than 0.8.8
    hooks.install(repo, PRD); (repo / ".prd-toolkit/prd").unlink()
    r = run_hook(repo, "pre-commit")
    assert r.returncode == 0 and hooks.SKIP in r.stderr

def test_shim_runs_launcher_without_exec_bit(repo):
    hooks.install(repo, PRD); (repo / ".prd-toolkit/prd").chmod(0o644)
    assert run_hook(repo, "pre-commit").returncode == 0

def test_shim_prd_path_with_space(tmp_path): ...  # PRD at "docs/prd/my orders": the hook runs and exits 0

def test_append_line_uses_the_launcher():
    line = hooks._append_line("commit-msg", PRD)
    assert 'sh "$prd_top/.prd-toolkit/prd" git-hook commit-msg "$prd_top/docs/prd/orders" "$@"' in line
    assert "--script" not in line and '[ -f "$prd_top/.prd-toolkit/prd" ]' in line

def test_install_rewrites_old_shims(repo):
    hooks.install(repo, PRD)
    write_087_shims(repo)                          # the 0.8.7 template text, kept as a fixture string
    lines = hooks.install(repo, PRD)
    assert "replaced .git/hooks/pre-commit (it used uv run --script)" in lines
    assert hooks.check(repo, PLUGIN_ROOT) == []

def test_check_reports_old_shim(repo):
    hooks.install(repo, PRD); write_087_shims(repo)
    assert "stale: .git/hooks/pre-commit; run prd_hooks.py install" in hooks.check(repo, PLUGIN_ROOT)

def test_check_reports_old_appended_line(repo):   # a user's own hook holding the 0.8.7 appended line
    ...                                            # same stale line; a user's hook without that line: no finding

def test_check_without_installed_hooks_is_clean(repo):   # CI: a fresh checkout has no shim
    hooks.install(repo, PRD); [p.unlink() for p in (repo / ".git/hooks").glob("*")]
    assert hooks.check(repo, PLUGIN_ROOT) == []
```

Replace the assertion at `tests/test_hooks_install.py:141` with the new appended-line form.

- [ ] **Step 2:** Run them. Expected: fail on the old form.
- [ ] **Step 3: Change the two templates.** The skip condition tests `-f "$top/.prd-toolkit/prd"` as well as `prd_git_hook.py` and the PRD folder; the last line is `exec sh "$top/.prd-toolkit/prd" git-hook {{hook}} "$top/{{prd}}"`. The uv guard line stays.
- [ ] **Step 4: Change `hooks.py`.** `_append_line` takes the same two conditions and the launcher call. `install` reads an existing shim before overwriting and reports `replaced …` when it matches `OLD_FORM`. `check` gains a loop over `HOOKS` in `_hooks_dir(repo_root)`: a file that exists and is `_ours` but differs from the rendered template, or is not ours and matches `OLD_FORM`, is one `stale:` line. `check` needs the PRD's relative path to render; when `prd_rel` is empty it compares only against `OLD_FORM`.
- [ ] **Step 5:** `vendor`, then run `tests/test_hooks_install.py tests/test_git_hook.py tests/test_hooks_vendor.py`. Expected: pass.
- [ ] **Step 6: Commit** `feat(invocation): hook shims run the launcher`, `Refs: none (no behaviour change)`.

---

### Task 5: The generated CI

**Files:**
- Modify: `prd-toolkit/scripts/prdlint/hooks.py` (`ci_jobs` at 454, `deploy_jobs` at 476)
- Test: `prd-toolkit/tests/test_hooks_ci.py`, `prd-toolkit/tests/test_hooks_stale.py`
- Regenerate: `.github/workflows/prd-toolkit.yml`; refresh `.prd-toolkit/`

**Interfaces:**
- Produces: CI lines of the form `sh .prd-toolkit/prd <command> <args>`.

- [ ] **Step 1: Write the failing tests.** Update `test_hooks_stale.py:40-41` to `["sh .prd-toolkit/prd lint --ci docs/prd/orders", "sh .prd-toolkit/prd hooks check --ci docs/prd/orders"]`, line 147 to `"sh .prd-toolkit/prd links check --ci docs/prd/orders"`, and the three lines in `test_hooks_ci.py` likewise (trace: `sh .prd-toolkit/prd trace <prd> --range <RANGE>`; drift: `sh .prd-toolkit/prd drift <prd> --env <env>`). Add:

```python
def test_no_generated_line_uses_script_mode(orders_prd):
    jobs = hooks.ci_jobs(orders_prd, PRD) + hooks.deploy_jobs(orders_prd, PRD)
    for text in (hooks.render_github(jobs), hooks.render_gitlab(jobs)):
        assert "--script" not in text and "sh .prd-toolkit/prd lint --ci" in text
```

- [ ] **Step 2:** Run them. Expected: fail.
- [ ] **Step 3:** Change the five command strings in `ci_jobs` and `deploy_jobs`. Standards and test-level jobs are the PRD's own commands and do not change.
- [ ] **Step 4:** `vendor`; then `uv run --script prd-toolkit/scripts/prd_hooks.py ci --github --force docs/prd/prd-toolkit`. Run the two test files and `tests/test_ci_local.py`. Expected: pass.
- [ ] **Step 5:** Run `CI_LOCAL_JOBS="prd-lint prd-trace" scripts/ci-local.sh`. Expected: `ci-local: prd-lint pass`, `ci-local: prd-trace pass`.
- [ ] **Step 6: Commit** with the workflow: `feat(invocation): generated CI runs the launcher`, `Refs: none (no behaviour change)`.

---

### Task 6: Templates, skill lines and graders

**REQUIRED SUB-SKILL:** superpowers:writing-skills.

**Files:**
- Modify: `prd-toolkit/templates/claude-block.md:18`, `prd-toolkit/templates/readme-prds.md:21`, and the 18 lines listed under Facts
- Modify: the six grader files listed under Facts
- Test: `prd-toolkit/tests/test_coordinating_skill.py`, `prd-toolkit/tests/test_eval_graders.py`, `prd-toolkit/tests/test_block.py`, new `prd-toolkit/tests/test_release_0_8_8.py` (created here, finished in Task 9)
- Refresh: `.prd-toolkit/`, `CLAUDE.md`, `docs/prd/README.md`, `docs/prd/prd-toolkit/README.md`

**Interfaces:**
- Produces: the line form `<prefix>.prd-toolkit/prd <command> <args>`, where `<prefix>` is whatever stood before `.prd-toolkit/` (`<start>/`, `<root>/` or nothing).

- [ ] **Step 1: Write the failing tests.**

```python
# test_release_0_8_8.py
def test_no_vendored_script_is_run_by_its_file():
    hits = [f"{p}:{n}" for p in tracked("skills", "commands", "agents", "templates")
            for n, line in enumerate(p.read_text().splitlines(), 1)
            if re.search(r"uv run --script \S*\.prd-toolkit/", line)]
    assert hits == []

def test_plugin_path_lines_are_untouched():
    n = sum(line.count("uv run --script <scripts>/") for p in tracked("skills", "commands", "agents")
            for line in p.read_text().splitlines())
    assert n == 80        # 77 in skills, 2 in commands, 1 in agents, counted on bfb63da
```

In `test_coordinating_skill.py`, lines 153 and 165-167 become: a line holding `.prd-toolkit/prd links ` starts with `<start>/.prd-toolkit/prd links ` or `<root>/.prd-toolkit/prd links ` and ends with the gate; and `.prd-toolkit/prd links changeset {action} `, `.prd-toolkit/prd links impact `, `.prd-toolkit/prd links sync ` are each in the text.

In `test_eval_graders.py`, for each of the six graders add a case in both forms: the command typed the 0.8.7 way and the 0.8.8 way give the same grade.

- [ ] **Step 2:** Run them. Expected: fail.
- [ ] **Step 3: Change the lines.** `uv run --script <p>.prd-toolkit/prd_links.py <rest>` becomes `<p>.prd-toolkit/prd links <rest>`; `prd_hooks.py` → `prd hooks`; `prd_judge.py` → `prd judge`. The `; echo "prd-links-exit=$?"` gates stay. Change nothing else in a skill.
- [ ] **Step 4: Change the graders** to accept both forms, so a recorded 0.8.7 transcript still grades: `prd_links\.py\s+impact` becomes `(?:prd_links\.py|\.prd-toolkit/prd\s+links)\s+impact`, and so on for `changeset\s+new`, the negative lookahead in `no-bash-write.md`, and `prd_judge\.py` → `(?:prd_judge\.py|\.prd-toolkit/prd\s+judge)`. The graders' prose names both.
- [ ] **Step 5:** `vendor`; `uv run --script prd-toolkit/scripts/prd_block.py docs/prd/prd-toolkit`. Run the four test files plus `tests/test_hooks_blocks.py tests/test_block_readmes.py`. Expected: pass. If the CLAUDE.md block's byte budget test fails, the new line is shorter than the old; report it rather than raising the budget.
- [ ] **Step 6: Commit** `feat(invocation): the block, the READMEs and the vendored skill lines run the launcher`, `Refs: none (no behaviour change)`.

---

### Task 6b: Every skill, command and agent line runs the launcher

Added 2026-11-14 on the owner's decision to widen the release (spec Revisions, §2). **REQUIRED SUB-SKILL:** superpowers:writing-skills.

**Why.** Nine files define `<scripts>` as `.prd-toolkit` whenever the repository has a vendored copy, so `uv run --script <scripts>/prd_lint.py …` runs the vendored copy by its file and keeps one uv environment per script and per clone. The launcher is in the plugin's `scripts` directory as well as in a vendored copy, mode 755 in both, so `<scripts>/prd <command>` works wherever `<scripts>` points.

**Files:**
- Modify: every line matching `uv run --script <scripts>/prd_<x>.py` under `prd-toolkit/skills`, `prd-toolkit/commands`, `prd-toolkit/agents` (80 lines in 13 files on 94a4ba2: `deploying-from-prds/running-a-deploy.md` 13, `deploying-from-prds/SKILL.md` 4, `handling-errors/running-an-error.md` 12, `building-from-prds/running-a-build.md` 12, `building-from-prds/SKILL.md` 1, `changing-prds/reviewing-a-change.md` 5, `changing-prds/SKILL.md` 12, `authoring-prds/SKILL.md` 4, `publishing-prds/SKILL.md` 1, `adopting-prds/SKILL.md` 11, `commands/prd-status.md` 1, `commands/prd-context.md` 1, `agents/prd-builder.md` 1)
- Modify: the "Which script" paragraph of each file that defines `<scripts>`
- Test: `prd-toolkit/tests/test_release_0_8_8.py`, and every test that pins a changed line

**Interfaces:**
- Produces: the line form `<scripts>/prd <command> <rest>`; a command is its script's name without `prd_` and `.py`, `_` written `-`.

- [ ] **Step 1: Write the failing tests** in `test_release_0_8_8.py`. Replace `test_plugin_path_lines_are_untouched` (it pinned 80 lines that must now be 0):

```python
def test_no_skill_line_runs_a_script_by_its_file():
    hits = [f"{p}:{n}" for p in tracked("skills", "commands", "agents", "templates")
            for n, line in enumerate(p.read_text().splitlines(), 1)
            if re.search(r"uv run --script\s+\S*prd_\w+\.py", line)]
    assert hits == []

def test_every_scripts_command_uses_the_launcher():
    n = sum(len(re.findall(r"<scripts>/prd [a-z][a-z-]*\b", p.read_text())) for p in tracked("skills", "commands", "agents"))
    assert n >= 80

def test_every_scripts_definition_checks_for_the_launcher():
    for p in tracked("skills", "commands"):
        text = p.read_text()
        if "`<scripts>` is `.prd-toolkit` when" in text:
            para = next(par for par in text.split("\n\n") if "`<scripts>` is `.prd-toolkit` when" in par)
            assert "predates 0.8.8" in para and "`prd`" in para, p
```

- [ ] **Step 2:** Run them. Expected: the first and third fail; the second fails (0 matches).
- [ ] **Step 3: Change the 80 lines.** `uv run --script <scripts>/prd_<x>.py <rest>` becomes `<scripts>/prd <x> <rest>`, with `_` in `<x>` written `-` (`prd_build_check.py` → `build-check`). Nothing else on a line changes: arguments, order, quoting and gate tails (`; echo "prd-…-exit=$?"`) stay. Where a line names the script only in prose (not as a command), leave it unless it is now false.
- [ ] **Step 4: Change each "Which script" paragraph**, the fewest words that keep it true:
  - It decides the copy by a Glob. `Glob for .prd-toolkit/*.py` cannot see `prd`; make the decision and the guard use a pattern that can (for example Glob `.prd-toolkit/prd*`), or name `.prd-toolkit/prd` as the file to look for.
  - Add the guard clause where the paragraph has version guards, and in every file that defines `<scripts>` as `.prd-toolkit`: "When `.prd-toolkit/` holds no `prd`, the vendored copy predates 0.8.8: stop, and tell the user to run `prd_hooks.py install docs/prd/<slug>` from the plugin (the README's form) and commit `.prd-toolkit/`." (`changing-prds/SKILL.md` has it since 94a4ba2.)
  - Where a paragraph lists the vendored scripts as "the copy its hooks and CI run" (`running-a-deploy.md`, `running-an-error.md`), keep the sentence true: the hooks and CI now run that copy through `.prd-toolkit/prd`.
  - `authoring-prds/SKILL.md` and `publishing-prds/SKILL.md` always use the plugin's path; their lines change form only. `prd publish` uses the plugin's `requirements-publish.txt`.
  - `building-from-prds`: the builder prompt's `Scripts:` line carries `<scripts>` as an absolute path; `agents/prd-builder.md`'s command follows the same form.
- [ ] **Step 5:** The install instruction a skill tells a user to run from the plugin (`prd_hooks.py install …`, "the README's form") names a script on purpose and stays; it is prose, not a `uv run --script` line, so the first test does not catch it. If a skill holds a literal `uv run --script <plugin path>/prd_hooks.py install` command, change it to the launcher form as well.
- [ ] **Step 6:** Run the suite, update each test that pins a changed line to the new text, and run it again. Expected: 0 failed. List every test file you changed in the report. Do not change graders (Task 6c) or `prd-toolkit/README.md` (Task 6d); if a test of a grader or of the README fails because of this task, stop and report.
- [ ] **Step 7: Commit** `feat(invocation): every skill, command and agent line runs the launcher`, `Refs: none (no behaviour change)`. Then `CI_LOCAL_JOBS="prd-lint" scripts/ci-local.sh` from the worktree root: `ci-local: prd-lint pass`.

---

### Task 6c: Graders accept both command forms

Added 2026-11-14 with Task 6b.

**Why.** 59 files under `prd-toolkit/evals/*/graders/` name a script file; about 50 of those are regular expressions over a recorded command (`prd_deploy\.py`, `prd_gates\.py`, `prd_error\.py`, `prd_change\.py`, `prd_lint\.py`, `prd_publish\.py`, `prd_build_check\.py`, `prd_context\.py`, and the `prd_links`/`prd_judge` ones Task 6 already changed). After Task 6b a correct session types `<scripts>/prd deploy …`, which those patterns no longer see.

**Files:**
- Modify: each grader under `prd-toolkit/evals/*/graders/` whose `input_match` (or other pattern field) holds a script file name
- Test: `prd-toolkit/tests/test_eval_graders.py`

**Interfaces:**
- Consumes: Task 6's pattern shape for `links` and `judge` (keep the 0.8.7 alternative first, byte for byte, and add the launcher alternative).

- [ ] **Step 1: Inventory.** List every grader file with a pattern that names a script, the pattern, and whether a match PASSES or FAILS the session. Put the table in the report. A grader whose only mention is prose gets its prose updated to name both forms and no pattern change.
- [ ] **Step 2: Write the failing tests** in `test_eval_graders.py`: for each changed grader, one case typed the 0.8.7 way and one typed the 0.8.8 way give the same grade; and for each grader that FAILS on a match or uses a negative lookahead, one near-miss in the new form that must not match (a different command, e.g. `prd lint` where the grader is about `prd deploy`; a command name that only starts the same, e.g. `prd deployed`). Use the file's existing helpers for building a tool-use line.
- [ ] **Step 3:** Run them. Expected: the 0.8.8 cases fail.
- [ ] **Step 4: Change the patterns.** For a pattern `prd_<x>\.py<tail>`: `(?:prd_<x>\.py|/prd(?:\\")?\s+<x-with-hyphens>)<tail>`, adapted to the pattern's own quoting and anchoring; the launcher alternative must require the `/prd` path segment and a whole command word (`\b` or `\s` after it). Keep every existing flag, lookahead and tail. Do not loosen what the 0.8.7 alternative matches.
- [ ] **Step 5:** Run `tests/test_eval_graders.py`, then the full unit suite. Expected: 0 failed.
- [ ] **Step 6: Commit** `feat(invocation): graders accept the launcher form of every script`, `Refs: none (no behaviour change)`.

Out of scope: evals' prompts, scaffolds and baselines (records of past runs). If a scaffold script or a `case.yaml` setup runs a toolkit script, leave it and list it in the report.

---

### Task 6d: The plugin README's vendored-path examples

Added 2026-11-14 with Task 6b.

**Files:**
- Modify: `prd-toolkit/README.md` — the 24 lines matching `uv run --script .prd-toolkit/prd_<x>.py` outside the `## Changelog` section
- Test: whichever tests pin those lines; `prd-toolkit/tests/test_release_0_8_8.py`

- [ ] **Step 1: Write the failing test** `test_readme_runs_the_vendored_copy_through_the_launcher`: outside `## Changelog` (and the `## Known limits (…)` sections, which are past records), `README.md` holds no `uv run --script .prd-toolkit/`.
- [ ] **Step 2:** Run it. Expected: fail.
- [ ] **Step 3:** Change each such line to `.prd-toolkit/prd <x> <rest>`. The examples that run the plugin's own copy by an absolute path (the first install, before a vendored copy exists) stay as `uv run --script <plugin path>/scripts/prd_hooks.py install …`: one path per installed version. The Changelog and Known limits sections are not edited.
- [ ] **Step 4:** Run the suite; update tests that pin a changed line. Expected: 0 failed.
- [ ] **Step 5: Commit** `docs(readme): vendored-copy examples run the launcher`, `Refs: none (no behaviour change)`.

---

### Task 7: The PRD patch (controller-run; stops for the owner)

**Files:** `docs/prd/prd-toolkit/adoption.md`, `docs/prd/prd-toolkit/prd.md`.

The controller runs this itself, through `/prd-toolkit:prd-change`; no subagent.

- [ ] **Step 1:** `adoption.md`, row `trace-and-hooks`: append `prd-toolkit/scripts/prd`, `prd-toolkit/scripts/prd_dispatch.py`, `prd-toolkit/scripts/requirements.txt` to its Boundary.
- [ ] **Step 2:** `prd.md` section 2: replace "Out of scope: the repository's other plugins and the `web/` docs site" with text true of PRDAnvil/prd-toolkit (the repository holds one plugin and no docs site); keep the rest of the sentence.
- [ ] **Step 3:** Patch bump 6.2.2 → 6.2.3; the §14 row reads "no dry run (wording only)".
- [ ] **Step 4:** Stop at the approval gate. The owner approves in the chat or the decision inbox; the reply is passed verbatim.
- [ ] **Step 5:** After the approval commit: `prd_lint.py docs/prd/prd-toolkit` and `prd_hooks.py check --ci docs/prd/prd-toolkit` print nothing.

---

### Task 8: The two documentation leftovers

**Files:** `prd-toolkit/README.md` (head of `## Changelog`, line 854), `prd-toolkit/evals/BASELINE.md` (head), `CLAUDE.md` (outside the managed block).

- [ ] **Step 1:** README and BASELINE each gain one sentence: "Commit SHAs in entries dated before 2026-11-10 resolve in `ihistand/claude-plugins`, where the toolkit lived until 0.8.6."
- [ ] **Step 2:** `CLAUDE.md`, under "Git workflow": "`prd_error.py check <range>` over a range that spans c8f48cf (the move's SHA rewrite) reports `Detected: changed` on older entries; start the range after it."
- [ ] **Step 3:** Run `tests/test_release_0_8_7.py` and the block tests: the managed block is untouched. **Commit** `docs: where older SHAs resolve, and check ranges across the move`, `Refs: none (no behaviour change)`.

---

### Task 9: Evals, release and proof

**Files:** `prd-toolkit/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `prd-toolkit/README.md` (changelog), `prd-toolkit/tests/test_release_0_8_8.py`, `prd-toolkit/evals/BASELINE.md`, `.prd-toolkit/`.

- [ ] **Step 1: Evals.** Since Task 6b every skill's text changed, so every case is in scope; the controller gives the owner the cost and asks before starting the run. Run `claude plugin eval` for the cases the owner agrees, `--runs 3`, with `--allow-tools Write Edit Bash Agent` and the two PyPI WebFetch grants. Record the scores under a `## 0.8.8 baseline` heading in `BASELINE.md`. A case that scored 1.00 at 0.8.7 and scores lower stops the release.
- [ ] **Step 2: Finish `test_release_0_8_8.py`:** `test_versions` (0.8.8 in `plugin.json`, `marketplace.json`, `.prd-toolkit/VERSION`, and `Version 0.8.8.` in the README); `test_changelog_has_the_upgrade_note` (the 0.8.8 entry holds `prd_hooks.py install`, `ci --`, `--force`, `environments-v2` and `6.2.3`). Update `test_release_0_8_7.py::test_versions` as each release has done for the one before it.
- [ ] **Step 3:** Bump the three version places (`vendor` writes `VERSION`). Write the changelog entry from the spec's sections 1, 4 and 5, with the upgrade note.
- [ ] **Step 4: Proof, in a scratch repository outside this one.** Install from the worktree's plugin; make one commit; count `environments-v2` in a scratch `UV_CACHE_DIR`; clone the scratch repository to a second path, install, commit; the count has not grown. Record both counts in the changelog entry's proof line.
- [ ] **Step 5:** `scripts/ci-local.sh`. Expected: all five jobs pass. Record the two test counts against Task 0's.
- [ ] **Step 6: Commit** `release 0.8.8: one prd command, and no uv environment per clone`, `Refs: none (no behaviour change)`. Stop. Push and the pull request wait for the owner's word.
- [ ] **Step 7, after the merge, on the owner's word:** install 0.8.8 at user scope; in this clone run the **vendored** `sh .prd-toolkit/prd hooks install docs/prd/prd-toolkit` to rewrite its two shims (the plugin's `install` is never run on this repository); remove the worktree and branch; update prdanvil.com's two pages; close PRDAnvil/prd-toolkit#2.

---

## Self-review

- **Spec coverage:** §3.1 → Task 2; §3.2, §3.3 → Task 1; §4 → Tasks 4, 5, 6; §5 → Tasks 3, 4, 9; §6 → Task 7 and the refreshes in 3 to 6; §7 → the tests in Tasks 1 to 6; §8 → Tasks 7, 8; §9 → Task 9. The spec's "plan checks the guard and ci-local" is answered under Facts.
- **Not in the spec, added here:** the six graders (Task 6). The spec said the evals' text is out of scope; the graders are code that reads commands, and they break without it. The spec's Revisions note records it.
- **Names:** `COMMANDS`, `main`, `LAUNCHER`, `OLD_FORM`, the `replaced …` and `stale: …` lines are used with one spelling throughout.
