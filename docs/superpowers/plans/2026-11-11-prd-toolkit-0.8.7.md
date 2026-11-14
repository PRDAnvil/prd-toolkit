# prd-toolkit 0.8.7: fixes and full command names — plan

> **Date:** 2026-11-11
> **Author:** Ivan Histand & Claude Code
> **Decision:** owner, 2026-11-11: "cut 0.8.7 your way". The merged lint-structure fixes ship now,
> with no feature; best practices move to 0.8.8 and conversion to 0.8.9
> (`docs/superpowers/specs/2026-11-03-prd-toolkit-0.8-umbrella.md`).
> **Branch:** `release/0.8.7`, from main 044e624.

## Scope

1. **The fixes since 0.8.6**, already merged: E-009, E-013, E-014 (PR #4), E-010 (#6), E-011 (#7),
   E-012 (#8), E-015 and E-016 (#9); E-017's flaky test (`--quiet`, on this branch; the entry stays
   `confirmed`, backlog item 5); E-018 resolved as not a defect.
2. **Full command names.** Current Claude Code lists a plugin's commands only under the plugin's
   name, so a bare `/prd-build` is "Unknown command". Every template (`templates/claude-block.md`,
   `templates/readme-prd.md`, `templates/readme-prds.md`), skill, command, agent and script message
   names them in full (`/prd-toolkit:prd-build`), and the tests that quote them follow. The
   toolkit's own generated blocks are refreshed with `prd_hooks.py vendor` and `prd_block.py`.
   Past records stay as written: `errors.md`, the evals' baselines, the changelog's older entries and
   the dated specs and plans.
3. **Deferred minors from the move:** the umbrella's rows (done here), the backlog's issue #24 →
   PRDAnvil/prd-toolkit#2, and `test_no_old_marketplace_names` reading tracked files only
   (`git ls-files`), not ignored ones.
4. **The release:** version 0.8.7 in `plugin.json` and `marketplace.json`, the changelog entry
   naming the PRD version (6.2.2), and the upgrade note.

## Upgrade note (for the changelog)

A repository that vendors the toolkit keeps its old command names in `CLAUDE.md`'s managed block and
in `docs/prd/README.md` and `docs/prd/<slug>/README.md` until it runs `prd_hooks.py install
docs/prd/<slug>` from the 0.8.7 plugin and commits `.prd-toolkit/` and the refreshed blocks. Until
then its own CI stays green: the check reads the vendored templates.

## Verify

`scripts/ci-local.sh` (the CI jobs with an empty HOME), then push and one PR on the owner's word.
