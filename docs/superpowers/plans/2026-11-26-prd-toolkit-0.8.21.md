# prd-toolkit 0.8.21 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 0.8.20's four deferred review minors (M5, M10, M12, M14) and release 0.8.21.

**Architecture:** One rule edit in `adopting-prds/SKILL.md`, one README paragraph, two graders on an existing eval,
two new eval cases. Executed natively, as the owner chose for 0.8.20.

**Tech Stack:** Markdown skill text, `claude plugin eval` cases (case.yaml, prompt.md, scaffold.sh, graders), pytest.

**Spec:** `docs/superpowers/specs/2026-11-26-prd-toolkit-0.8.21-memory-minors-design.md`

## Global Constraints

- Version 0.8.21 in plugin.json, marketplace.json and `.prd-toolkit/VERSION` (via `prd_hooks.py vendor`).
- Commits: `Refs: none (no behaviour change)` (the `skills` area is not adopted), plus the session trailers.
- Fixture names, tokens and paths are invented.
- Unit suite: `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`.

## Review Focus

1. A new scaffold run with a real `HOME`: it must refuse before writing, like `adopting-memory-conflict`'s.
2. A last-message grader that passes on a message that merely mentions memory without saying no note applies.
3. The headless-owner case's owner grader passing because the bootstrap never wrote `prd.md` at all.
4. A Bash grader that fails on a legitimate read of the token note's file name (input, not output, is matched).
5. The README's three-place sentence drifting from the Memory section's Where line.

---

### Task 1: Rule 3 names memory notes (M10)

**Files:** Modify `prd-toolkit/skills/adopting-prds/SKILL.md` (Non-negotiable rule 3); Test
`prd-toolkit/tests/test_adopting_skill.py`.

- [ ] Write `test_0821_rule_3_names_memory_notes`: rule 3's text (from `**An apparent bug never becomes a
  requirement.**` to rule 4) contains `or an owner's memory note`.
- [ ] Run it: FAIL.
- [ ] Edit rule 3: "its commit messages, its siblings or an owner's memory note".
- [ ] Run it and the adopting tests: PASS. Commit.

### Task 2: The conflict eval checks Agent and Bash (M5)

**Files:** Create `prd-toolkit/evals/adopting-memory-conflict/graders/no-agent-token.md` and `no-bash-token.md`
(`tool_used`, `input_match: 'tok_live_7Qx9ZRm2'`, `min: 0`, `max: 0`).

- [ ] Write a unit pin `test_0821_the_conflict_eval_checks_every_tool_for_the_token`: graders exist for Write,
  Edit, Agent and Bash, each with that `input_match` and `max: 0`. FAIL, then add the graders, PASS. Commit.

### Task 3: Two new eval cases (M14)

**Files:** Create `prd-toolkit/evals/adopting-memory-unrelated/` and
`prd-toolkit/evals/adopting-memory-headless-owner/` (case.yaml, prompt.md, scaffold.sh, graders/).

- **unrelated:** scaffold = `notes_repo.py bare` + the billing-api token note only (both memory places).
  Graders: skill-fired; `features/notes.md` exists; errors.md has no `memory note` (file may be absent: use
  `not_contains` on the file only if it exists, else grade via `features/notes.md` not citing memory); token in no
  Write/Edit/Agent/Bash; last message says no memory note names the repo.
- **headless-owner:** scaffold = `notes_repo.py bare` + a note `project_notes_owner.md` naming the notes service's
  owner (an invented name) + the billing note. Prompt: start the PRD and adopt the notes area through extraction,
  headless. Graders: skill-fired; `prd.md` exists; `prd.md`'s `owner:` line is a `NEEDS CLARIFICATION` marker and
  the name is nowhere in `docs/prd/`; the last message names the owner and the note.
- [ ] Unit pins: both scaffolds refuse a HOME outside the sandbox (as the 0.8.20 pin); both build a clean repo with
  the notes in both places in a fake sandbox.
- [ ] RED: run each case on 0.8.19 (a `git archive` of 5cb2df4 plus the new case dirs). Expected: the last-message
  grader fails.
- [ ] GREEN: run each case on the branch. Expected: 1.00. Record both in `evals/BASELINE.md`. Commit.

### Task 4: README and release 0.8.21 (M12)

**Files:** `prd-toolkit/README.md`, plugin.json, marketplace.json, `.prd-toolkit/VERSION`,
`prd-toolkit/tests/test_release_0_8_21.py` (new), `test_release_0_8_20.py` (unpin the version).

- [ ] Write `test_release_0_8_21.py`: version pins; the adoption section names the three places (`the system
  prompt names`, `` `~/.claude/projects/` ``, `a directory you name`); changelog entry needles
  (`adopting-memory-unrelated`, `adopting-memory-headless-owner`, `The lint rule count stays 41`, `**Upgrade:**`).
  FAIL.
- [ ] Bump, vendor, write README text. PASS. Full unit suite green. Commit.

Then: final whole-branch review on the most capable model, one fix pass, push, PR. The owner merges.
