---
name: authoring-packs
description: Use when writing a prd-toolkit pack (prd-packs/<name>/, pack.yaml) from two adopted PRDs of one kind (two repos with a docs/prd/ folder whose areas declare the same custom contract types), when asked what two PRDs share, to share their contract types, validators, levels or harness between repositories, to put a pack into a plugin, or on /prd-toolkit:prd-pack - and when asked to add to the pack what neither PRD holds, merge the two PRDs' differences, write helper code, clarify questions or a skill for it, edit the PRDs, or push, publish or install the plugin
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/authoring-packs/running-a-pack.md` whole before anything else
(no offset, no limit; it sits beside this file, in the skill's base directory): it is your next
tool call, and you follow it step by step, steps 1 to 7.
Run no command, read no PRD file and write no file before you have read it.

# Authoring packs

## Overview

**Compare, propose, the owner decides, write only what the PRDs hold.** A pack is written from two
adopted PRDs of one kind, never from memory of what such a pack should hold. `prd pack compare`
prints what the two share and where they differ, each line marked `both`, `A` or `B`. You propose
each manifest item with the PRD lines it comes from, show each difference with both sides, and
write nothing until the owner has decided every item. Then you write the manifest, the validators
the PRDs already use, one bad sample per type and a README with a to-do list into the plugin the
owner names, run `prd pack check`, and commit on a new branch there. The two PRDs move onto the pack
later, each by its own `/prd-toolkit:prd-change` (the lift), on the owner's approval.

**Violating the letter of these rules is violating the spirit.** "A stricter validator is better",
"every site of this kind needs these standards", "I'll just merge the two harness texts", "I'll make
a plugin to hold it" and "they'll want it installed" change nothing below.

## Non-negotiable rules

1. **Two adopted PRDs are the input.** Both PRDs are Approved and lint clean, and each holds one or
   more custom contract types. Otherwise say what is missing and stop: a repository with no PRD is
   adopted first (`/prd-toolkit:prd-adopt`). Never a pack from one PRD, or from a repository that
   has none.
2. **Every manifest item comes from a line of one or both PRDs and the report says which; nothing a
   PRD does not hold is added (no helper, no rule, no level).** The four header keys are the
   exception: the name and the description the owner decides, `version: 0.1.0`, and the built-in
   packs' `toolkit` range. A validator is the command the
   PRD's section 7 row gives, copied as it stands, or the repository file it runs, copied
   unchanged: never rewritten, widened or made stricter. No word, standard, source, slot or
   default enters the manifest from what you know of the platform.
3. **A difference is the owner's to settle, never averaged.** Two texts of one slot, two commands of
   one level, two globs or two validators of one type: both sides are shown, with a recommended
   resolution and its reason (take A's, take B's, or leave it out so each PRD keeps its own). When
   the two PRDs' validators differ, the owner picks one; the skill merges none. A contract type one
   PRD lacks never goes in.
4. **The owner decides every item: in, out, or which side.** One reply may decide them all, after
   the proposal is shown. The request is never that reply, nor your own text, and "do it all"
   given before the proposal decides nothing. Nothing is written before the reply. With no one to
   answer, the proposal is the report: write nothing.
5. **It goes into the plugin the owner names,** as `prd-packs/<name>/` on a new branch of that
   repository; a new minimal plugin (a manifest, a README and the pack) only when the owner says so,
   at the path the owner gives, with no marketplace. It never pushes, publishes or installs.
6. **What is written:** `pack.yaml`, the carried-over validators, `samples/<type>/bad.*` and a
   README with the to-do list. Nothing else. No helper code, `clarify.md`, `rubrics.md` or skill
   is drafted: the to-do list names them, and the files a person would start from.
7. **Each validator can fail.** `prd pack check` exits 0 before anything is committed: every type
   has a `samples/<type>/bad.*` its validator refuses, made by breaking a copy of a real contract
   file in one named way, and the same validator runs from the pack folder on each PRD's own
   files. A validator that refuses no such break, or fails from the pack folder, is reported; it
   is never replaced.
8. **The PRDs themselves are not edited by this skill.** No `Pack:` line, no Validator cell, no
   copy of a PRD edited to try the pack. Moving each PRD onto the pack is the lift, a separate
   `/prd-toolkit:prd-change` in its own repository, after the plugin is installed and with the
   owner's approval.

## Red Flags - STOP

Quoted from a run without this skill (evals/baselines/authoring-packs.md: two scratch leaflet-site
repositories, each with an adopted PRD, and the prompt "Write a pack these two can share."), except
where marked.

- "**Contract types:** `pages` and `routes` (both sites), `forms` (north) and `feeds` (south)."
  One-PRD types in the manifest. The check runs each type on both PRDs (`glob matches no file`),
  and the other PRD's lift refuses a type its section 7 lacks.
- "Each is checked by `validate_leaflet.py`, which replaces the old one-line checks with real shape
  checks". A validator invented over the PRDs' own. Copy the command the section 7 row gives.
- "a list of hosting words (nginx, S3, CDN, JavaScript and so on) that the linter warns about in
  requirements, extra interview questions in `clarify.md`, and four reference standards (WHATWG
  HTML, RFC 9110, WCAG 2.2, RSS 2.0)". A vocabulary, clarify questions and sources neither PRD
  holds.
- "I wrote a shared prd-toolkit pack called `leaflet 1.0.0` and put it in its own local plugin,
  `leaflet-prd-pack/`, so neither repo owns it." A plugin nobody named, and a version nobody chose:
  a new pack is `0.1.0`, in the plugin the owner names.
- "`leaflet-prd-pack/.claude-plugin/marketplace.json`", then "To use the pack, run `/plugin
  marketplace add ./leaflet-prd-pack` and then `/plugin install leaflet-prd-pack@leaflet-packs`." A
  marketplace made up, and its install given as the next step. Publishing is the owner's.
- "an inline Python script that edited each copy's `prd.md` (added a `Pack:` line and set the
  validator cells to `pack`)". A PRD edited by hand, even a throwaway copy. The lift is
  `prd change pack … --lift`, through `/prd-toolkit:prd-change`.
- "Until a toolkit release supports that conversion, the two PRDs can only use the pack in a new
  area." A lift is not a conversion: a PRD that names no pack moves onto one that declares its own
  custom types.
- "south runs integration tests from `tests/site`, needs a headless browser, and targets T-001.2 at
  `code:site.serve`. The README lists these, and each repo keeps them in its own files." Two
  differences settled for the owner, who was asked nothing: the session ended with no question.
- A `pack.yaml`, a sample or a plugin file written before the owner's reply to the proposal.
  (Spec §4.)
- A type with no `samples/<type>/bad.*`, or a commit made while `prd pack check` prints a finding.
  (Spec §6.)
- `git push`, `claude plugin install`, `claude plugin marketplace add`, or a settings file edited
  to enable the plugin. (Spec §4.)

**All of these mean: stop, remove what you wrote outside the steps, and return to the step of
`running-a-pack.md` whose gate is open.**

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The PRDs' validators are one-liners; real shape checks are better." | The PRDs' validators are what the owner confirmed in adoption, and what lint runs today. A stricter one is a change to each PRD, through `/prd-toolkit:prd-change` in its own repository. |
| "`forms` is only in north, but south will want it." | The check refuses a type one PRD lacks, and south's lift would be refused. The pack holds what both declare. |
| "Every site of this kind needs these standards." | Neither PRD holds them. Name what is missing in the README's to-do list; add nothing. |
| "The two harness texts say almost the same; I'll merge them." | Nothing is matched by resemblance. Show both texts; the owner takes one or leaves the slot out. |
| "The vocabulary candidates are the kind's words, so they go in." | A pack's vocabulary is the platform words a requirement should not name: each word kept warns `platform-word` on every requirement of both PRDs that uses it. They go in only when the owner puts them in. |
| "Nobody named a plugin; I'll make one so the pack has a home." | A new plugin is written only when the owner says so, at the path they give. Ask. |
| "I'll draft `clarify.md` and a skill so the pack is complete." | Helpers, clarify questions and skills are written by a person. The to-do list names them and the files to start from. |
| "I'll lift a copy of each PRD to prove it lints." | The skill edits no PRD, not even a copy. `prd pack check` runs the pack's validators on both PRDs' files; the lift is the owner's change. |
| "They asked for a pack, so the request approves the contents." | The request starts the proposal. Each item is decided by the reply to it. |
| "Installing it is one command; they'll want it." | Installing and publishing are the owner's. Name the next steps in the report and run none. |

## Related skills

- **prd-toolkit:adopting-prds** (`/prd-toolkit:prd-adopt`) adopts a repository with its custom
  contract types; the second adoption of a kind is the moment for this command.
- **prd-toolkit:changing-prds** (`/prd-toolkit:prd-change`, "Packs and retargeting") lifts each PRD
  onto the written pack, as a patch the owner approves.
- **superpowers-developing-for-claude-code:developing-claude-code-plugins**, when it is in your
  skills list, for the plugin's own layout.
