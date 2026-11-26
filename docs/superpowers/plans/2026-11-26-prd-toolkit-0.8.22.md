# prd-toolkit 0.8.22 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 0.8.21's three deferred review minors (M4, M5, M6) and release 0.8.22.

**Architecture:** One phrase in `adopting-prds/SKILL.md`, one README paragraph, one grader body, a release.
Executed natively.

**Tech Stack:** Markdown, pytest, `claude plugin eval`.

**Spec:** `docs/superpowers/specs/2026-11-26-prd-toolkit-0.8.22-memory-wording-design.md`

## Global Constraints

- Version 0.8.22 in plugin.json, marketplace.json and `.prd-toolkit/VERSION` (via `prd_hooks.py vendor`).
- Commits: `Refs: FR-270` on the bump, else `Refs: none (no behaviour change)`; trailers.
- The changelog entry names no spec file.

## Review Focus

1. The new wording still tells a normal session (identical paths) to skip the second place.
2. The README test pins wording the skill really holds, so the two cannot drift silently.
3. The grader body's claims match its pattern.
4. The `$HOME`/`~` choice is the same in the skill, the README and the changelog entry.
5. The README paragraph stays under the file's wrap width.

---

### Task 1: M4 and M5

**Files:** `prd-toolkit/skills/adopting-prds/SKILL.md`, `prd-toolkit/README.md`, `prd-toolkit/tests/test_adopting_skill.py`.

- [ ] Tests (fail first): the Memory section holds "the folder names can match while the directories differ" and
  not "match whenever"; the README's adoption section holds the skill's
  `$HOME/.claude/projects/<the repository root, each non-alphanumeric as ->/memory/`, not "when that is another
  directory", and no line of that paragraph is over 110 characters.
- [ ] Edit both. Tests pass. Commit.

### Task 2: M6

**Files:** `prd-toolkit/evals/*/graders/lists-the-home-memory-place.md` (three copies), the test file.

- [ ] Test (fail first): each copy's body says "a mention", "`$HOME` or `~`" and "named `home`". Edit, pass, commit.

### Task 3: Release 0.8.22

- [ ] `test_release_0_8_22.py` (fail first), bump, vendor, changelog entry, unpin 0.8.21. Full unit suite; one
  `adopting-memory-conflict` run; BASELINE line; ci-local; commit, push, PR. The owner merges.
