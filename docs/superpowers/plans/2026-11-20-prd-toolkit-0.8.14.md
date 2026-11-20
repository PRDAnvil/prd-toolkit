# prd-toolkit 0.8.14: a replay that proves a fix, and a close for an error no area covers — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One command shows whether the commit an error entry names turned its test from failing to passing; an error in code no adopted area covers closes with that proof in place of a T-id; and E-017 is resolved in the toolkit's own ledger.

**Architecture:** One mechanical unit under the toolkit's own PRD, a new adopted area written before its code. `error-replay`: the replay, the fourth resolution form's rules and the `replay` command (`prdlint/errorreplay.py`), called from thin edits to `prd_error.py` and `prdlint/errors.py`; an optional `One test` column of the Levels table, read in `prdlint/model.py`. The `handling-errors` skill gains the route for uncovered code and the replay before a resolution is committed. The generated CI does not change.

**Tech stack:** Python 3.11+, pyyaml, git worktrees, the toolkit's `prdlint` package, pytest; Markdown skills; `claude plugin eval`. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-20-prd-toolkit-0.8.14-error-replay-design.md`. Where this plan and the spec differ, the spec wins and the difference goes in its Revisions note.

## Global constraints

- **Branch:** `feat/prd-toolkit-0.8.14`, worktree `.worktrees/prd-toolkit-0.8.14`, cut from `main` after the spec branch (`docs/prd-toolkit-0.8.14-spec`) is merged. Never work in the main checkout. Bring the branch up to date by merging `main`, never by a rebase.
- **Author:** the clone's git config. Commits cite the PRD IDs they touch (`Refs: FR-0nn`) or `Refs: none (no behaviour change)`. Never `--no-verify`, never a bare `git stash`.
- **Generic:** no file, test, commit, eval or PRD line names a client application, an organization, a person, a private plugin or marketplace, or holds a path under a home directory.
- **Unchanged:** a PRD with no `One test` column lints, reports, builds and deploys exactly as in 0.8.13; the three existing resolution forms are written, read and checked byte for byte, and `resolve` runs no replay for them; the generated CI file is byte-identical, so `prd hooks check --ci` stays clean in a repository that does not regenerate it; the lint rule count stays 41; every existing `prd error` subcommand keeps its exit codes and output.
- **What the replay may run:** a level's `One test` cell with one argument appended, as an argument list, never through a shell. It never writes the working tree or the index.
- **The vendored copy** matches the plugin byte for byte: after a change to a vendored file, `prd-toolkit/scripts/prd hooks vendor docs/prd/prd-toolkit`, committed with the change. Never `install` in this repository.
- **Tests:** unit `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`; integration `uv run --directory prd-toolkit pytest -q -n auto tests/prd`. Nobody but `prd-tester` writes or edits a test under `tests/prd/`. Baseline on 26b0455: unit 3897 passed, 1 skipped; integration 345 passed.
- **Where the agents run:** the tester's guard and the builder bind to the session's working directory, and a subagent may not start `claude -p` or `claude plugin eval`. The controller runs the dry runs, the builds and the evals itself, headless, started in the right directory, with the prompt on stdin.
- **Every headless session is told it is headless** and to start no decision inbox: `gates serve` opens a browser. A scratch gate is answered only with a scripted chat reply written by the controller, in a scratch repository.
- **The stops:** the owner approves the PRD change (Task 1), reads the changed skill text (Task 3), answers E-032's proposed class (Task 5), and gives the word to push (Task 6). Nothing else waits on a person.

## Review focus

What the spec implies and a build could miss. Each is pinned by an acceptance criterion in Task 1 or an eval in Task 4.

1. **A harness that cannot run in a fresh worktree** (no virtual environment, a missing dependency): the first run fails for the wrong reason. The second run fails too, so the outcome is findings, never `holds`.
2. **A worktree left behind.** After a finding, a timeout, an interrupt and an internal error, `git worktree list` reads as it did before the command, and no temporary folder remains. The same when the command is itself started inside a linked worktree, which is where this repository's own work happens.
3. **The fix commit is a merge or has no parent.** `<sha>^` is the first parent; a root commit is a finding. An abbreviated `<sha>` that names no commit, or more than one, is a finding and nothing runs.
4. **An argument that looks like something else.** A cited test file whose path holds a space is passed as one argument. A test id that starts with `-`, or holds white space, is refused before anything runs. A `$` or a `;` in a test id reaches the command as plain text.
5. **A refused `resolve --red-run` leaves `errors.md` byte for byte as it was,** whichever refusal it is, the replay's among them; and an uncommitted Resolution line is replayed with the tests of `HEAD`.

---

### Task 0: Branch and baseline

- [ ] **Step 1:** Confirm `origin/main` holds the merge of `docs/prd-toolkit-0.8.14-spec`. If not, stop and report.
- [ ] **Step 2:** `git worktree add -b feat/prd-toolkit-0.8.14 .worktrees/prd-toolkit-0.8.14 origin/main`; check `git config user.email`.
- [ ] **Step 3:** Run both test commands; record the counts in the ledger. A failure here is reported, not fixed.
- [ ] **Step 4:** Record, outside the repository, for the comparison in Task 2: `prd error list docs/prd/prd-toolkit`; `prd error check docs/prd/prd-toolkit <the 0.8.13 release's range>` with its exit code; `prd lint --json docs/prd/prd-toolkit`; and the text `prd hooks ci --github` writes for a scratch PRD.
- [ ] **Step 5: the two `One test` commands.** From the repository root, run `uv run --project prd-toolkit pytest -q -n auto prd-toolkit/tests/prd/test_tester_paths_check.py` and the same command with `prd-toolkit/tests/test_builtin_packs.py`. Expected: both pass (measured on 26b0455 while this plan was written: 5 passed, and 27 passed). If either cannot run from the root, stop and tell the owner: the command in spec §7 changes, by a Revisions note, before Task 1.

---

### Task 1: The PRD change (controller-run; stops for the owner)

The controller has a drafting subagent write the PRD side and runs the dry runs and the approval itself, as for 0.8.12. FR-a to FR-g are placeholders for the IDs the script prints.

**Files (all under `docs/prd/prd-toolkit/`):** create `features/error-replay.md`, `test-cases/error-replay.yaml`, `contracts/fixtures/error-replay/`; modify `contracts/cli.yaml`, `adoption.md`, `testing.md`, and what `record` writes in `prd.md`; `features/lint-cli.md` and its cases only if Step 3 puts the column's requirement there.

- [ ] **Step 1: `adoption.md`.** Row `| error-replay | adopted | prd-toolkit/scripts/prdlint/errorreplay.py |`.

- [ ] **Step 2: `features/error-replay.md`.** Every AC is EARS and carries the exact output text below.

  **UJ-x Anyone with the repository sees whether the commit an entry names fixed it.**

  **FR-a The `One test` column.** Found by its header; the cell is one simple command in backticks under the Harness command's rules (spec §3); a blank cell or no column means none. The lint finding for any other cell: `level '<level>': One test '<cell>' is not one simple command in backticks`.

  **FR-b The replay of an entry with a T-id.** The resolving commit (the first commit whose `errors.md` holds this Resolution line; `HEAD` when it is not committed); the cited files under the test roots of that commit; the first run on the tree of `<sha>^` with its test roots replaced, where at least one cited file must fail; the second run on the tree of `<sha>` with the same roots, where every cited file must pass.

  **FR-c The replay of an entry with a red run.** The test id as the one argument; the trees of `<sha>^` and `<sha>` as committed; must fail, then must pass.

  **FR-d Outcomes.** Exit 0 with `<E-nnn>: <T-id or test id> fails on <sha>^ and passes on <sha>`. Exit 0 with one of `skipped: <E-nnn>: resolved by an environment run`, `skipped: <E-nnn>: resolved as not a defect`, `skipped: <E-nnn>: <level> is a deploy-gate level`, `skipped: <E-nnn>: <level> has no One test command`. Exit 1 with the findings of spec §4, one per line on stdout, in the spec's wording, plus `<E-nnn>: <sha> names no commit` and `<E-nnn>: <sha> names more than one commit`. Exit 2 for usage. An entry that does not exist: `refused: <E-id> is not an entry`, exit 1, as `prd error url` answers. `--timeout <seconds>`; the level's Timeout; 600 s. `--json`: the document of spec §4, kind `error-replay`, `interface` 1.

  **FR-e Nothing is left and nothing is written.** One AC per ending (holds, findings, timeout, interrupt): the worktree list and the working tree are as before. One AC for a command started inside a linked worktree.

  **FR-f `resolve --red-run`.** The line it writes, `fixed in <sha>, red run <test id> [<level>]`; one AC per refusal, each `refused: …` on stderr with exit 1 and `errors.md` unchanged:
  - `<sha> changes <path>, which area <area> covers; resolve with a regression T-id`
  - `the PRD has no adoption map, so every path is covered; resolve with a regression T-id`
  - `<E-nnn> is classed <class>; a red run resolves a code bug only`
  - `<level> is not a level of testing.md`
  - `<level> is a deploy-gate level`
  - `<level> has no One test command; add the One test column to testing.md Levels through /prd-toolkit:prd-change`
  - `the test id must hold no white space and must not start with -`
  - each finding of the replay, as its own `refused:` line.

  Exit 2, with `--red-run takes --commit and --level, and no --t, --version, --run or --not-a-defect`, for any other mix of flags.

  **FR-g `check` and the older forms.** The four findings of spec §5 for a fourth-form line added in the range; the finding for a line of no form reads `resolution is not one of the four forms`; each of the three older forms is written and checked as before.

  Edge cases carry Review focus 1 to 5.

- [ ] **Step 3: where the column's requirement lives.** `prdlint/model.py`, which reads the Levels table, sits in the adopted `lint-cli` Boundary. Find what the commit hook and `prd build-check` require of a commit that touches a Boundary file of another area than the one being built, as 0.8.12 did; write FR-a where a build can cite it (`error-replay` if the checks allow it, else a new `lint-cli` requirement), choose the existing lint rule that reports the cell (`test-level` reads the Levels table today), and say both in the change's report.

- [ ] **Step 4: contracts, fixtures and cases.**
  - `contracts/cli.yaml`, under `prd_error`: the `replay` subcommand with its flags, outputs and exit codes; `resolve`'s `--red-run` and `--level`; the refusals above.
  - `testing.md`: the `One test` column, `uv run --project prd-toolkit pytest -q -n auto` for `unit` and for `integration`.
  - Fixtures: a recipe that builds a small git repository in the test's temporary folder, with a PRD that has an adoption map, a Levels table whose build level has the `One test` cell `python3 tools/one.py`, and a runner `tools/one.py` that runs the file it is given and exits with its status. Commits, in order: the code with its bug; a test that fails on it; the fix; a later test file; the ledger's resolve. Variants by recipe: the test committed after the fix; a test that passes on the bug; a fix that touches an adopted file; no adoption map; a level with no cell; a deploy-gate level; a runner that sleeps past the timeout; a runner that needs a file no commit holds (Review focus 1).
  - Cases: one per AC at least, level `integration`, whole-line and whole-JSON assertions, and `git worktree list` compared before and after wherever a run happens.

- [ ] **Step 5:** `bump`, `record` (expected: minor, 8.4.0, with the row `format: One test column (prd-toolkit 0.8.14)` for the toolkit's own `testing.md`), lint, the dry runs over every new non-unit T-id in rounds (each gap fixed and re-run), the verdict, and the approval. **Stop for the owner's approval**, asked in the chat.

---

### Task 2: The builds (controller-run, headless)

- [ ] **Step 1:** `/prd-toolkit:prd-build error-replay <IDs>` (and `lint-cli <IDs>` if Task 1 put FR-a there), one area per build.

  What the builds must produce:
  - `prdlint/errorreplay.py`:
    - `RED_RUN`, the fourth form's pattern: `fixed in ([0-9a-f]{7,40}), red run (\S+) \[([^\]\s][^\]]*)\]`.
    - `@dataclass Run`: `commit: str`, `when: str` (`before` or `after`), `argument: str`, `exit: int | None`, `seconds: float`, `timed_out: bool`.
    - `@dataclass Replay`: `entry: str`, `outcome: str` (`holds`, `skipped` or `findings`), `subject: str | None`, `reason: str | None`, `findings: list[str]`, `runs: list[Run]`.
    - `one_test_command(prd: Prd, level: str) -> list[str] | None`: the cell as an argument list, `None` for a blank cell or no column.
    - `replay(prd: Prd, repo_root: Path, eid: str, timeout: int | None = None) -> Replay`: reads the entry's Resolution line.
    - `replay_red_run(prd: Prd, repo_root: Path, eid: str, commit: str, test_id: str, level: str, timeout: int | None = None) -> Replay`: the same two runs for a line that is not written yet.
    - `red_run_refusals(prd: Prd, repo_root: Path, entry: ErrorEntry, commit: str, test_id: str, level: str) -> list[str]`: every refusal that needs no run.
    - `check_red_run(prd: Prd, repo_root: Path, head: str, entry: ErrorEntry) -> list[str]`: what `check` reports for a fourth-form line.
  - `prdlint/model.py`: `Testing.one_tests: dict[str, str]`, level to raw cell, filled only when the column exists, beside `timeouts`.
  - `prdlint/errors.py`: `resolve` takes `red_run: str | None` and its level, calls `red_run_refusals` then `replay_red_run`, and writes the line; `_resolution` hands a fourth-form line to `check_red_run`; the "four forms" message.
  - `prd_error.py`: the `replay` subcommand (`--timeout`, and `--json` through `prdlint/interface.py`); `resolve --red-run <test id> --level <level>`.
  - The lint rule Step 3 of Task 1 chose reports the malformed cell.
  - `references/prd-format.md`: the column, under Levels, and the fourth form, under `errors.md`. `references/help.yaml`: an entry for the column only if the help area's contract lists Levels columns.
  - The vendored copy refreshed in the same commit as each change to a vendored file.
- [ ] **Step 2:** The close: every requirement `verified`, lint and `check --ci` clean, both suites green, and the Task 0 recordings compared: `prd error list` and `prd error check` print what they printed, lint's JSON differs by the PRD version alone, and the generated CI text is byte-identical.

---

### Task 3: The skill text (subagents; stops for the owner's read)

One implementer, two reviewers, one fixer, a scoped re-review, as for 0.8.12. `superpowers:writing-skills` applies.

**Files:** modify `prd-toolkit/skills/handling-errors/SKILL.md` (rules 4 and 5 and their exception; two Red Flags; two rows of Common Rationalizations) and `prd-toolkit/skills/handling-errors/running-an-error.md` (steps 5 and 6; the stop for a vendored copy that holds no `prdlint/errorreplay.py`, which predates 0.8.14).

- [ ] **Step 1: the baselines,** in scratch repositories, with a session that has the 0.8.13 text:
  - an adopted area and a confirmed `code bug` whose faulty code lies outside every adopted Boundary, with "fix it and close the entry". Record what it does: a `/prd-toolkit:prd-change` with no block to change, a fix with no failing test first, the entry left open, or a hand-edited Resolution line.
  - an entry with a T-id whose named fix commit did not turn its test green (the test passed before it). Record that it resolves and commits all the same.
- [ ] **Step 2: the text,** covering spec §6 step by step, with the baselines' mistakes quoted in the Red Flags. The route for uncovered code names its four steps and its three conditions (outside every adopted Boundary, after `Confirmed:`, the test first). The replay step names the command, what a skip is, and how the ledger is put back on findings (`git restore docs/prd/<slug>/errors.md`, never an edit). Each command is confirmed by running it.
- [ ] **Step 3: two reviews.** One tries to find a path by which the skill lets a session edit code inside an adopted Boundary, fix before a failing test, skip the replay, or commit a resolution after findings. One reads both files for a contradiction with their own rules and runs the unit suite.
- [ ] **Step 4: one fixer,** the unit suite, and a scoped re-review.
- [ ] **Step 5:** Give the owner the changed passages in one file outside the repository, opened for review. **Stop.**

---

### Task 4: Evals (the controller runs them)

- [ ] **Step 1: new cases,** each with a scaffold that exits 0 in an empty directory and passes its own clean-tree check, graders that can fail, a prompt that names the command in full (`/prd-toolkit:prd-error`), and a unit test that tries each grader against a passing and a failing sample:
  - `error-uncovered-code-red-run`: a confirmed `code bug` in code no adopted area covers. The session commits a failing test before the fix, resolves with `--red-run`, starts no `/prd-toolkit:prd-build`, and the ledger's line is the fourth form.
  - `error-replay-finding-not-committed`: an entry with a T-id whose fix commit did not turn its test green. After `resolve`, the replay reports it, `errors.md` is put back, the entry is still `confirmed`, and nothing is committed.
- [ ] **Step 2: run** the new cases and every existing case of `handling-errors`, one run each, with the flags `evals/BASELINE.md` records. Record the results as the 0.8.14 section. A grader corrected after a trace is read is rerun once and the record says so.

---

### Task 5: The toolkit's own ledger (stops for the owner)

- [ ] **Step 1: the proof.** Run `prd-toolkit/scripts/prd error replay docs/prd/prd-toolkit <E-nnn>` for every resolved entry of the toolkit's ledger. Record each outcome (holds, skipped with its reason, or its findings) in `docs/superpowers/plans/2026-11-20-prd-toolkit-0.8.14-acceptance.md`. An older entry's findings are recorded with their cause and change nothing; a defect of the replay itself is an error entry.
- [ ] **Step 2: E-017.** `prd-toolkit/scripts/prd error resolve docs/prd/prd-toolkit E-017 --commit 6d6711b --red-run prd-toolkit/tests/test_builtin_packs.py --level unit`. Expected: `E-017 resolved code bug`. Commit `errors.md` alone (`docs(prd): resolve E-017`, `Refs: E-017`), then `prd error check` over the branch's range, exit 0.
- [ ] **Step 3: E-032,** through `/prd-toolkit:prd-error` from its step 2: reproduce, diagnose, propose the class, commit the proposal. **Stop for the owner's answer.** A fix joins this release only on the owner's confirmation and word; otherwise the entry stays open and the README's Known limits says so.
- [ ] **Step 4:** Finish the acceptance record: what was run, each outcome, and what is the owner's to decide.

---

### Task 6: Release

**Files:** the two manifests, `.prd-toolkit/VERSION`, `prd-toolkit/README.md`, `prd-toolkit/tests/test_release_0_8_14.py`, `prd-toolkit/tests/test_release_0_8_13.py` (its version pin relaxed, and its counts moved to "at least"), `docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md`.

- [ ] **Step 1:** `tests/test_release_0_8_14.py`: the three versions; eleven skills and twelve commands; the README sections for the replay, the fourth form and the `One test` column, with the commands and the JSON document; the changelog entry with the PRD version, the upgrade step, the known limits and the evals; the priority plan's row. See it fail.
- [ ] **Step 2:** Version 0.8.14; `vendor` writes `VERSION`.
- [ ] **Step 3:** README: Handling errors gains the replay, the fourth form and the route for uncovered code; the testing section gains the column; the limits of spec §4; the changelog entry, whose upgrade note says to re-run `prd hooks install` from the 0.8.14 plugin and commit `.prd-toolkit/` before a ledger holds a fourth-form line, that the generated CI file is unchanged, and that a PRD takes the column as a patch only if it wants the replay.
- [ ] **Step 4:** The priority plan: mark 0.8.14 delivered.
- [ ] **Step 5:** Merge `origin/main`; both suites; `scripts/ci-local.sh`, all five jobs; the final whole-branch review; the scan of the whole branch history for private names. Commit `release 0.8.14: a replay that proves a fix, and a close for an error no area covers`. **Stop: push and the pull request wait for the owner's word.**
- [ ] **Step 6, after the merge, on the owner's word:** install 0.8.14; re-vendor the repositories that use the toolkit; remove the worktrees and branches.

---

## Self-review

- **Spec coverage:** §3 → FR-a, Task 1 Step 3; §4 → FR-b to FR-e; §5 → FR-f, FR-g; §6 → Task 3, Task 4; §7 → Task 1, Task 2; §8 → Task 5; §9 → Tasks 4 to 6; §10 → nothing to build.
- **Left to the tools on purpose:** the IDs and the version level; where FR-a lives and which rule reports the cell (Task 1 Step 3 finds out from the checks); whether `help.yaml` gains an entry (the help area's contract decides).
- **Names:** `prd error replay`, `--red-run`, `--level`, `One test`, `error-replay`, `prdlint/errorreplay.py`, `replay`, `replay_red_run`, `red_run_refusals`, `check_red_run`, `one_test_command`, `Testing.one_tests` and "resolving commit" are spelled one way throughout.
- **Review focus:** each of the five has an AC in FR-d to FR-f and a fixture variant in Task 1 Step 4.
