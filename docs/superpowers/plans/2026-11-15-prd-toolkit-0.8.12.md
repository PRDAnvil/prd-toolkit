# prd-toolkit 0.8.12: a pack written from two adopted PRDs, and cards that say where — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** From two adopted PRDs of one kind, one command proposes a pack, the owner decides what goes in, and the pack is written into a plugin, checked, and adopted by both PRDs as a patch; and every card in the decision inbox says its area and links to where the trouble is.

**Architecture:** Two mechanical halves under the toolkit's own PRD, each a new adopted area written before its code. `pack-authoring`: `prd pack compare` and `prd pack check` (`prd_pack.py`, `prdlint/packcompare.py`, `prdlint/packcheck.py`) and the `--lift` form of `prd change pack` (`prdlint/change.py`). `card-context`: a gate's `area` and `url` (`prdlint/cardcontext.py`, read by `gates.py` and the inbox page), the `URL:` line of an error entry and the `url` part of a `Target:` line (parsed in `prdlint/model.py`, written by `prd error`). One judgment half as skill text, proven by evals and a proof: the new skill `authoring-packs` with `/prd-toolkit:prd-pack`, and small edits to the error and adoption skills.

**Tech stack:** Python 3.11+, pyyaml, the toolkit's `prdlint` package, pytest; Markdown skills; `claude plugin eval`. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.12-pack-authoring-design.md`. Where this plan and the spec differ, the spec wins and the difference goes in its Revisions note.

## Global constraints

- **Branch:** `feat/prd-toolkit-0.8.12`, worktree `.worktrees/prd-toolkit-0.8.12`, cut from `main` after the spec branch (`docs/prd-toolkit-0.8.12-spec`) is merged. Never work in the main checkout. Bring the branch up to date by merging `main`, never by a rebase.
- **Author:** the clone's git config. Commits cite the PRD IDs they touch (`Refs: FR-0nn`) or `Refs: none (no behaviour change)`. Never `--no-verify`, never a bare `git stash`.
- **Generic:** no file, test, commit, eval or PRD line names a client application, an organization, a person, a private plugin or marketplace, or holds a path under a home directory. The proof's repositories are described by their kind ("two static web sites"), never by name, in everything committed here.
- **Unchanged:** a PRD with no `URL:` line and no `url` part lints, reports and builds exactly as in 0.8.11; `prd change pack` for a version move behaves as before; every existing pack manifest stays valid; the lint rule count stays 41.
- **The vendored copy** matches the plugin byte for byte: after a change to a vendored file, `prd-toolkit/scripts/prd hooks vendor docs/prd/prd-toolkit`, committed with the change. Never `install` in this repository.
- **Tests:** unit `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`; integration `uv run --directory prd-toolkit pytest -q -n auto tests/prd`. Nobody but `prd-tester` writes or edits a test under `tests/prd/`. Baseline on d9b6761: unit 3800 passed, 1 skipped; integration 251 passed.
- **Where the agents run:** the tester's guard and the builder bind to the session's working directory, and a subagent may not start `claude -p` or `claude plugin eval`. The controller runs the dry runs, the builds, the evals and the proof's sessions itself, headless, started in the right directory, with the prompt on stdin.
- **Every headless session is told it is headless** and to start no decision inbox: `gates serve` opens a browser. A scratch gate is answered only with a scripted chat reply written by the controller, in a scratch repository.
- **The stops:** the owner approves the PRD change (Task 1), reads the new skill's text (Task 3), confirms the two adoptions and decides the pack's contents in the proof (Task 5), and gives the word to push (Task 6). Nothing else waits on a person.

## Review focus

What the spec implies and a build could miss. Each is pinned by an acceptance criterion in Task 1, an eval in Task 4 or a step of the proof.

1. **A lift must change nothing a PRD produces.** After `--lift` and `hooks install`, lint's findings, the context packs and the test suite of the lifted PRD are what they were, apart from the `Pack:` line, the section 7 Validator cells and the changelog row. A lift that would change a glob, or name a type the PRD lacks, is refused before anything is written.
2. **A validator that cannot fail.** `prd pack check` fails a type with no bad sample, and a sample the validator accepts.
3. **Two PRDs that share nothing, or one with no custom type:** `compare` exits 1 with one line, and the skill stops before proposing.
4. **Differences are never merged.** The same slot with two texts, the same type with two globs or two validators: both sides are printed, in `compare` and in the skill's proposal.
5. **An error that touches nothing, and a gate of an area with no URL:** `area` is the empty list and `url` is null; the card says `Area: none` and shows no link. A URL with white space or another scheme is a lint finding, never a broken link on the page.

---

### Task 0: Branch and baseline

- [ ] **Step 1:** Confirm `origin/main` holds the merge of `docs/prd-toolkit-0.8.12-spec`. If not, stop and report.
- [ ] **Step 2:** `git worktree add -b feat/prd-toolkit-0.8.12 .worktrees/prd-toolkit-0.8.12 origin/main`; check `git config user.email`.
- [ ] **Step 3:** Run both test commands; record the counts in the ledger. A failure here is reported, not fixed.
- [ ] **Step 4:** Record, outside the repository, `prd gates list` and `prd gates list --json` on a scratch PRD that holds one gate of each kind, the inbox's `/gates` JSON for it, and `prd change pack` on a scratch PRD for a version move, for the before/after comparison in Task 2.

---

### Task 1: The PRD change (controller-run; stops for the owner)

The controller has a drafting subagent write the PRD side and runs the dry runs and the approval itself, as for 0.8.11. FR-a to FR-j are placeholders for the IDs the script prints.

**Files (all under `docs/prd/prd-toolkit/`):** create `features/pack-authoring.md`, `features/card-context.md`, their `test-cases/*.yaml`, `contracts/fixtures/pack-authoring/`, `contracts/fixtures/card-context/`; modify `contracts/cli.yaml`, `adoption.md`, `testing.md`, and what `record` writes in `prd.md`; `features/lint-cli.md` only if Step 3 puts a parse requirement there.

- [ ] **Step 1: `adoption.md`.** Rows `| pack-authoring | adopted | prd-toolkit/scripts/prd_pack.py, prd-toolkit/scripts/prdlint/packcompare.py, prd-toolkit/scripts/prdlint/packcheck.py |` and `| card-context | adopted | prd-toolkit/scripts/prdlint/cardcontext.py |`.

- [ ] **Step 2: `features/pack-authoring.md`.** Every AC is EARS and carries the exact output text.

  **UJ-x An owner with two adopted PRDs of one kind gets a pack from what they share.**

  **FR-a `prd pack compare`, as text.** The parts in the spec's order, each line marked `both`, `A` or `B`; the exact line form per part; what "the same" means; the vocabulary rule.

  **FR-b `prd pack compare --json` and its refusals.** The document; exit 1 with its one line when no custom contract type is shared; exit 2 for usage and a folder that is not a PRD, with the JSON error document.

  **FR-c `prd pack check`.** One AC per check of spec §6, each with its finding line; the bad-sample rule; exit codes; `--json`.

  **FR-d `prd change pack … --lift`.** What it writes, the record's text, and one AC per refusal with its message; the version-move form unchanged.

  Edge cases carry Review focus 1 to 4.

- [ ] **Step 3: `features/card-context.md`.**

  **UJ-y An owner reading a card sees which area it is for and can open the thing it is about.**

  **FR-e A gate's area.** One AC per gate kind, in the spec's table; the order and the empty list.

  **FR-f The `URL:` line of an error entry.** Its place in the entry, its form, `prd error new --url`, `prd error url` (set, replace, remove), and the lint finding for a malformed one.

  **FR-g The `url` part of a `Target:` line.** The grammar with one, two and three parts, a line with the URL alone, and the finding for a malformed one.

  **FR-h A gate's URL.** Which URL each kind takes, in the spec's order; null otherwise.

  **FR-i Where they show.** `prd gates list` text and `--json`; the inbox's card JSON; `interface` 1.

  `prdlint/model.py` parses the entry and the `Target:` line and sits in the adopted `lint-cli` Boundary. Find what the commit hook and `prd build-check` require of a commit that touches a Boundary file of another area than the one being built; write the two parse requirements where a build can cite them (the new area if the checks allow it, else as new `lint-cli` requirements), and say which in the change's report.

- [ ] **Step 4: contracts, fixtures and cases.** `contracts/cli.yaml`: `prd_pack` (both subcommands), the `--lift` form under `prd_change`, `prd_gates` (the gate's fields with `area` and `url`) and `prd_error`'s two additions. Fixtures: two small PRD folders of one invented kind that share two custom contract types, differ in one harness slot and one Levels row, and each hold one type the other lacks; a pack folder written from them, with samples; a PRD with one gate of each kind, an entry with and without a URL and touching nothing, and areas with and without a `Target:` URL. Cases: one per AC at least, level `integration`, whole-line and whole-JSON assertions.

- [ ] **Step 5:** `bump`, `record` (expected: minor, 7.1.0), lint, the dry runs over every new non-unit T-id in rounds (each gap fixed and re-run), the verdict, and the approval. **Stop for the owner's approval**, asked in the chat.

---

### Task 2: The builds (controller-run, headless)

- [ ] **Step 1:** `/prd-toolkit:prd-build pack-authoring <IDs>`, then `/prd-toolkit:prd-build card-context <IDs>` (and `lint-cli <IDs>` if Task 1 put requirements there), one area per build.

  What the builds must produce:
  - `prdlint/packcompare.py` (`compare(prd_a, prd_b) -> Comparison`), `prdlint/packcheck.py` (`check(pack_dir, prds) -> list[Finding]`), `prd_pack.py` on `interface.py`; `pack` in `prd_dispatch.COMMANDS` and in `hooks.VENDORED`.
  - `prdlint/change.py`: the `--lift` form, sharing the version move's refusals where they are the same.
  - `prdlint/cardcontext.py` (`areas(prd, gate) -> list[str]`, `url(prd, gate) -> str | None`); `gates.py` and `templates/gates/inbox.html` carrying and showing both; `prdlint/model.py`, `errors.py` and `prd_error.py` for the `URL:` line; the `Target:` grammar and its message.
  - `references/prd-format.md`: the entry's `URL:` line and the `Target:` line's third part. `references/contract-types.md`: how a pack is written from two PRDs, the samples folder, and the lift. `references/help.yaml`: an entry for each new field (the help area's contract follows in Task 1 if it pins them).
  - The vendored copy refreshed in the same commit as each change to a vendored file.
- [ ] **Step 2:** The close: every requirement `verified`, lint and `check --ci` clean, both suites green, and the Task 0 recordings compared: the gate listings gain only the two fields, a version move is unchanged.

---

### Task 3: The skill text (subagents; stops for the owner's read)

One implementer, two reviewers, one fixer, a scoped re-review, as for 0.8.11.

**Files:** create `prd-toolkit/skills/authoring-packs/SKILL.md` with a procedure file read whole as its first instruction, and `prd-toolkit/commands/prd-pack.md`; modify `skills/handling-errors/` (a URL the report gives goes to `prd error new --url`; the proposal names the entry's areas), `skills/adopting-prds/SKILL.md` (where an area is adopted with custom contract types, a line that a second repository of the kind is the moment for `/prd-toolkit:prd-pack`; where a `Target:` line is written, the optional URL, asked of the owner and never guessed), `skills/changing-prds/SKILL.md` (Packs and retargeting: the lift, beside the version move, with its commands and its dry-run record), `references/quality-checklist.md` only if a line there names what a card shows.

- [ ] **Step 1: the baseline.** In a scratch directory with two small adopted PRDs of one kind (the Task 1 fixtures, as repositories), ask a session without the new skill to "write a pack these two can share". Record what it does wrong: items in the manifest that neither PRD holds, differences merged, helper code invented, the PRDs edited, a push or an install.
- [ ] **Step 2: the skill**, covering spec §4 and §5 step by step in the toolkit's skill form, with the baseline's mistakes quoted in its Red Flags. Its rules, verbatim from the spec. It names the exact commands (`prd pack compare`, `prd pack check`, `prd change pack … --lift`, `hooks install`), each confirmed by running it.
- [ ] **Step 3: the edits** to the three existing skills, each as small as its job.
- [ ] **Step 4: two reviews.** One tries to find a path by which the skill adds what no PRD holds, merges a difference, edits a PRD, or pushes or installs. One reads the edited files for a contradiction with their own rules and runs the unit suite.
- [ ] **Step 5: one fixer**, the unit suite, and a scoped re-review.
- [ ] **Step 6:** Give the owner the new skill's text in one file outside the repository, opened for review, and the list of edits. **Stop.**

---

### Task 4: Evals (the controller runs them)

- [ ] **Step 1: new cases**, each with a scaffold that exits 0 in an empty directory and passes its own clean-tree check, graders that can fail, and a unit test that tries each grader against a passing and a failing sample and refuses three dashes inside a grader's frontmatter line:
  - `pack-stops-without-custom-types`: one PRD has no custom contract type; the skill says so and proposes nothing.
  - `pack-proposal-names-its-sources`: every manifest item in the proposal is marked `both`, `A` or `B`, and the two planted differences are shown with both sides.
  - `pack-writes-nothing-before-decisions`: no file is written anywhere and nothing is pushed or installed.
  - `pack-drafts-no-helpers`: with the owner's decisions scripted in the prompt, the pack folder holds `pack.yaml`, the validators, the samples and a README, and no helper, clarify file or skill.
  - `error-records-the-url`: a report that gives an address ends with `prd error new … --url <that address>`.
- [ ] **Step 2: run** the new cases and the existing cases of the skills whose text changed, one run each, with the flags `evals/BASELINE.md` records. Before the run, try one case that needs the launcher: if E-022 still stops it, say so to the owner with the count of cases that will not run, and run only those that can. Record the results as the 0.8.12 section. A grader corrected after a trace is read is rerun once and the record says so.

---

### Task 5: The proof (stops for the owner, more than once)

Two static web sites hosted on the same platform, each in its own repository, neither with a PRD. Everything committed in this repository about them is by kind, never by name. The work in those repositories is on a branch of each and is pushed only on the owner's word.

- [ ] **Step 1: adopt one area of each** (`/prd-toolkit:prd-adopt`, controller-run headless, the owner confirming each area in the adoption form or the chat): the site's pages and its hosting configuration, with the contract types the two need declared as custom types, each with a validator that can fail. The same type names in both, since the second adoption reads the first.
- [ ] **Step 2: `/prd-toolkit:prd-pack`** on the two PRDs: the comparison, the proposal, **the owner's decisions**, the pack written into the plugin the owner names (or a new one), the check.
- [ ] **Step 3: the lift** in each repository: the plugin installed from its checkout, `prd change pack … --lift`, `hooks install`, lint, and **the owner's approval** of each patch. Then each PRD's suite, which must pass as before.
- [ ] **Step 4: the cards:** a `Target:` URL on one area and a recorded error with a `URL:`; `prd gates list --json` and the inbox page (opened by the owner, on purpose) show the area and both links.
- [ ] **Step 5:** The acceptance record, `docs/superpowers/plans/2026-11-15-prd-toolkit-0.8.12-acceptance.md`: what was run, what the pack holds, what its to-do list names, and every finding. Defects are fixed and their step rerun; what is the owner's to decide is listed in the release report.

---

### Task 6: Release

**Files:** the two manifests, `.prd-toolkit/VERSION`, `prd-toolkit/README.md`, `prd-toolkit/tests/test_release_0_8_12.py`, `prd-toolkit/tests/test_release_0_8_11.py` (its version pin relaxed, and its counts of skills and commands moved to "at least"), `docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md`.

- [ ] **Step 1:** `tests/test_release_0_8_12.py`: the three versions; eleven skills and twelve commands, each command in the README's table; the README sections for pack authoring and for the cards, with the commands and the JSON documents; the changelog entry with the PRD version, the upgrade step, the known limits and the evals. See it fail.
- [ ] **Step 2:** Version 0.8.12; the manifest description gains pack authoring in a few words; `vendor` writes `VERSION`.
- [ ] **Step 3:** README: a section on writing a pack (the three commands, what is written, what is not, the lift), the cards' area and URL in the Decision inbox and Handling errors sections, the new command's row, and the changelog entry.
- [ ] **Step 4:** The priority plan: mark 0.8.12 delivered.
- [ ] **Step 5:** Merge `origin/main`; both suites; `scripts/ci-local.sh`, all five jobs; the final whole-branch review; the scan of the whole branch history for private names, the proof's repositories' names among them. Commit `release 0.8.12: a pack from two PRDs, cards that say where`. **Stop: push and the pull request wait for the owner's word.**
- [ ] **Step 6, after the merge, on the owner's word:** install 0.8.12; remove the worktree and branch; update the site's two pages; tell the client session the version, the gate's two new fields and the two new commands.

---

## Self-review

- **Spec coverage:** §3 → FR-a, FR-b; §4, §5 → Task 3, Task 4, Task 5; §6 → FR-c; §7 → FR-d, Task 5 Step 3; §8 → FR-e to FR-i; §9 → Task 1, Task 2; §10 → Tasks 4 to 6.
- **Left to the tools on purpose:** the IDs and the version level; where the two parse requirements live (Task 1 Step 3 finds out from the checks).
- **Names:** `prd pack compare`, `prd pack check`, `--lift`, `authoring-packs`, `/prd-toolkit:prd-pack`, `pack-authoring`, `card-context`, `prdlint/cardcontext.py`, `area`, `url` are spelled one way throughout.
