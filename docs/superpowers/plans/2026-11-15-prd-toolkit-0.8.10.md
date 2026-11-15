# prd-toolkit 0.8.10: a Next part in the status report — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `prd status` starts with a part, Next: an ordered list of what the PRD needs, each item one sentence with the command that does it, and the same list as data in `--json`.

**Architecture:** One new module, `prdlint/nextpart.py`, takes the loaded PRD and the repository root and returns the items; it reads what the toolkit already computes (lint, trace, the gates list, the error ledger, the Deployed part, block statuses, the adoption map). `prdlint/status.py` puts those items first and prints them. The rule is written in the toolkit's own PRD first, as a new adopted area `status-next`, and built from it: `/prd-toolkit:prd-change` writes the requirements, `/prd-toolkit:prd-build` has the builder write the code and the black-box tester write the tests.

**Tech stack:** Python 3.11+, the toolkit's `prdlint` package, pytest. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.10-next-part-design.md`. Where this plan and the spec differ, the spec wins and the difference goes in its Revisions note.

## Global constraints

- **Branch:** `feat/prd-toolkit-0.8.10`, worktree `.worktrees/prd-toolkit-0.8.10`, cut from `main` after the spec branch (`docs/prd-toolkit-0.8.10-spec`) is merged. Never work in the main checkout. Bring the branch up to date by merging `main`, never by a rebase.
- **Author:** the clone's git config. Commits cite the PRD IDs they touch (`Refs: FR-0nn`) or `Refs: none (no behaviour change)`. Never `--no-verify`, never a bare `git stash`.
- **Generic:** no file, test, commit or PRD line names a client application, an organization or a person, or holds a path under a home directory. Before a push, the whole branch history is checked.
- **Unchanged:** every part of the status report other than Next, in text and in JSON, byte for byte after the Next part; lint's and trace's own output; every script's usage and exit codes.
- **The vendored copy** matches the plugin byte for byte: after a change to a vendored file, `prd-toolkit/scripts/prd hooks vendor docs/prd/prd-toolkit`, committed with the change. Never `install` in this repository.
- **Tests:** unit `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`; integration `uv run --directory prd-toolkit pytest -q -n auto tests/prd`. Nobody but `prd-tester` writes or edits a test under `tests/prd/`. Baseline on 7e6e813: unit 3717 passed, 1 skipped; integration 177 passed.
- **Where the agents run:** the tester's guard and the builder bind to the session's working directory. A controller whose session was opened elsewhere runs the dry runs and the build headless, started in the worktree (`claude -p` with the prompt on stdin), and reads the report file.
- **The stops:** the owner approves the PRD change (Task 1) and gives the word to push (Task 3). Nothing else waits on a person.

## Review focus

What the spec implies and a build could miss. Each is pinned by an acceptance criterion or an edge case in Task 1.

1. **The rest of the report must not move.** Record `prd status` and `prd status --json` on three fixture PRDs before the build; after it, the text after the Next part and the JSON items after the Next items are byte for byte the same.
2. **A PRD with almost nothing:** no `adoption.md`, no `errors.md` entries, no environment in `operations.md`, no deploy log. The part holds the one `idle` item, with the "verified" sentence.
3. **No git checkout.** The trace row is skipped, the gates list does not raise, and the report still prints.
4. **A deploy log that cannot be read** is a gate of its own in `prd gates list`; Next lists it as that gate and does not crash on it.
5. **Listed once.** A `proposed` error and a run stopped at an unconfirmed human step each appear as their gate and nowhere else; a `confirmed` error and a failed run appear as `error-open` and `deploy-stopped`.

---

### Task 0: Branch and baseline

- [ ] **Step 1:** Confirm `origin/main` holds the merge of `docs/prd-toolkit-0.8.10-spec`. If not, stop and report.
- [ ] **Step 2:** `git worktree add -b feat/prd-toolkit-0.8.10 .worktrees/prd-toolkit-0.8.10 origin/main`; check `git config user.email`.
- [ ] **Step 3:** Run both test commands; record the counts in the ledger. A failure here is reported, not fixed.
- [ ] **Step 4:** Record, outside the repository, `prd status` and `prd status --json` for the toolkit's own PRD and for the two existing fixture repositories the status tests use (Review focus 1).

---

### Task 1: The PRD change (controller-run; stops for the owner)

The controller runs `/prd-toolkit:prd-change` in the worktree and follows the skill: IDs from `prd change ids next`, the version from `bump` and `record`, the dry run from `prd-tester`. FR-a to FR-f are placeholders for the IDs the script prints.

**Files (all under `docs/prd/prd-toolkit/`):** create `features/status-next.md`, `test-cases/status-next.yaml`, `contracts/fixtures/status-next/`; modify `contracts/cli.yaml`, `adoption.md`, `testing.md` (the fixtures' rows and any setup step or assertion key the cases need), and what `record` writes in `prd.md`.

- [ ] **Step 1: `adoption.md`.** A row `| status-next | adopted | prd-toolkit/scripts/prdlint/nextpart.py |`. The `status` row is not touched.

- [ ] **Step 2: `features/status-next.md`.** Every AC is EARS and carries the exact text of spec sections 4 to 6.

  **UJ-x A person or a program asks what the PRD needs next.** Flow: run `prd status` → read the first part → run the command the first item names, or answer the decision it names; a program reads the items whose `part` is `Next` from `prd status --json`. Traces: FR-a to FR-f.

  **FR-a The Next part comes first, as text.** `## Next` before `## Header`; one line `<n>. <text>` per item, numbered from 1; a second line, two spaces and `run: <command>`, for an item with a command; then one empty line and the report as it was.

  **FR-b The Next items in the JSON document.** First in `items`; each with `part` `Next`, `id`, `text`, `kind`, `ids`, `area`, `command`, `waits_on`, in that key order; `id`, `ids` and `area` as spec sections 5 and 6 give them; the other items unchanged; `interface` 1.

  **FR-c The order.** The tiers Broken, You, Work; inside a tier the kinds in the spec's table order; inside a kind the order of its Items column. One AC states the whole order as a list of kinds.

  **FR-d Broken.** One AC per row: `lint` from lint errors (count, first finding, warnings not counted), `lint` from trace findings (skipped with no git checkout), `deploy-stopped` (one per environment; `unfinished` and `failed`), `error-open` (every open entry not `proposed`). Each AC gives the sentence, the command and `waits_on`.

  **FR-e Waiting on you.** `gate` (one per gate of `prd gates list` without `--worktrees`, in its order; the `id`, `ids` and `area` rule), `question` (an `awaiting <who>` row of section 12; a section 13 line that is not `None.`), `draft` (version below 1.0.0).

  **FR-f Work, and nothing.** `deploy` (only when `operations.md` names an environment), `verify` and `build` (one per area, in the Requirements part's order; `<IDs>` joined as the spec says; singular forms), `adopt` (a row not `adopted` and without an adoption gate), and `idle` with its two sentences.

  Edge cases carry the listed-once rules (a `proposed` entry; a run stopped at an unconfirmed human step), the full-stop rule, a block with the status `live (since X.Y.Z)` counting as live, `as-built` and `removed` blocks making no item, and an unreadable deploy log (Review focus 4).

  Each block carries `Status: approved`, its `Tests:` line and `Traces: cli:prd_status`.

- [ ] **Step 3: the contract.** `contracts/cli.yaml`, under `prd_status`: `next_item` (the eight keys and their types), `next_kinds` (the eleven kinds, `idle` included, in order), `next_text_line` and `next_run_line`.

- [ ] **Step 4: the fixtures and the cases.** Under `contracts/fixtures/status-next/`, PRD folders written as file maps in the form the existing `lint-cli` fixture uses, loaded into a scratch git repository by the harness:
  - `base`: version 1.0.0, Approved, one area with one block each `approved`, `built`, `verified` and `live`, a second area with two `approved` blocks, one environment, no adoption map, no open error. Expected items: `deploy`, `verify`, `build`, `build`.
  - `empty`: version 1.0.0, Approved, every block `verified`, no environment. Expected: the `idle` item, "verified" sentence.
  - Each other state is `base` plus a named setup step in `testing.md` (in the vocabulary the `lint-cli` cases already use for mutations): a lint error; a trace finding; an open `confirmed` entry; a `proposed` entry; an `awaiting` assumption and a section 13 question; version 0.3.0; an adoption map with one `extracted` row that has an answers file and one `not started` row; a deploy log stopped `failed`; a deploy log stopped at a human step; a deploy log that cannot be parsed; the folder copied outside any git checkout.
  - `test-cases/status-next.yaml`: one case per kind, one for the order across all three tiers (a fixture state that holds an item of every kind), one per listed-once rule, one per `idle` sentence, one for text form and one for JSON form on `base`, level `integration`, target `cli:prd_status`, run as the `help` cases run their script. Each case asserts whole lines or whole JSON items, never a substring.

- [ ] **Step 5:** `bump`, `record` (expected: minor, 6.4.0), lint, the dry runs over the new T-ids (at least half of them, in rounds, each gap fixed in the PRD and re-run), the verdict, and the approval gate. Show the owner the requirement list, the version and the dry-run record. **Stop for the owner's approval.**

---

### Task 2: The build (controller-run)

- [ ] **Step 1:** `/prd-toolkit:prd-build status-next <the UJ and FR IDs of Task 1>`, following the skill.

  What the build must produce, so the controller can check the round against it:
  - `prd-toolkit/scripts/prdlint/nextpart.py`: `next_items(prd, repo_root) -> list[NextItem]`, where `NextItem` has `kind`, `text`, `ids`, `area`, `command`, `waits_on` and `id`. It calls `registry.run`, `trace.run_trace`, `gates.list_gates`, the error ledger and the status module's own stopped-run reading; it computes none of them a second way.
  - `prdlint/status.py`: `PARTS` starts with `Next`; `build_status` puts the items first; `render_text` prints the numbered and `run:` lines; `render_document` writes the eight keys for a Next item and three for the others. `prd_status.py` changes only if the call needs it.
  - The vendored copy refreshed in the same commit.
  - Unit tests (the builder's) only for the unit T-ids the PRD holds.
- [ ] **Step 2:** The close: every requirement `verified`, lint and `check --ci` clean, both suites green, and the Task 0 recordings compared (Review focus 1). If the round stops on a gap in the PRD, follow the skill: a gap is a `/prd-toolkit:prd-change`, not a guess.
- [ ] **Step 3:** Run `prd status` on the toolkit's own PRD and read the Next part as a person would. Anything that reads wrong is a finding for the owner, listed in the release report, not a silent edit.

---

### Task 3: Release

**Files:** `prd-toolkit/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.prd-toolkit/VERSION`, `prd-toolkit/README.md`, `prd-toolkit/commands/prd-status.md`, `prd-toolkit/tests/test_release_0_8_10.py`, `prd-toolkit/tests/test_release_0_8_9.py` (its version pin relaxed, as each release does to the one before), `prd-toolkit/evals/BASELINE.md`, `docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md`.

- [ ] **Step 1:** `tests/test_release_0_8_10.py`: the three versions; the README names the Next part with its kinds and the two output forms; the changelog entry names `Next`, `--json`, the Header no longer being first, the upgrade step and the PRD version. See it fail.
- [ ] **Step 2:** Version 0.8.10 in the two manifests; `vendor` writes `VERSION`.
- [ ] **Step 3:** README: the status section and the Machine interface section, and the changelog entry (what it adds; the Header is no longer the first part or the first item; a repository gets it when `install` is run from the 0.8.10 plugin; the PRD version; the evals).
- [ ] **Step 4:** `commands/prd-status.md`, and any skill line that describes the report, say that it starts with Next. Rerun the eval cases that run `/prd-toolkit:prd-status` (three runs each) and record them in `evals/BASELINE.md`; the rest of the suite is not rerun.
- [ ] **Step 5:** The priority plan: mark 0.8.10 delivered.
- [ ] **Step 6:** Merge `origin/main`; both suites; `scripts/ci-local.sh`, all five jobs; the final whole-branch review; the scan of the whole branch history for private names. Commit `release 0.8.10: a Next part in prd status`. **Stop: push and the pull request wait for the owner's word.**
- [ ] **Step 7, after the merge, on the owner's word:** install 0.8.10; remove the worktree and branch; update the site's two pages; tell the client session that asked for the part the version and the exact fields.

---

## Self-review

- **Spec coverage:** §3 → FR-b; §4 → FR-c to FR-f; §5 → the sentences in FR-d to FR-f; §6 → FR-a, FR-b; §7 → Task 1; §8 → Task 3; §9's decisions are carried by the ACs they concern.
- **Left to the tools on purpose:** the IDs, the version level, and the setup vocabulary `testing.md` already has.
- **Names:** `nextpart.py`, `next_items`, `NextItem`, area `status-next`, part `Next` are spelled one way throughout.
