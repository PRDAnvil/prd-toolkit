# prd-toolkit 0.8.11: best-practice sources, and the skills a PRD needs — design

> **Date:** 2026-11-15
> **Author:** Ivan Histand & Claude Code
> **Status:** Draft, for the owner's review. The design of sections 3 to 9 was approved in the
> brainstorm (owner, 2026-11-15).
> **Extends:** `2026-11-03-prd-toolkit-0.8-umbrella.md` (its 0.8.11 row), the backlog
> `2026-11-08-prd-toolkit-0.8.6-backlog.md` (item 1) and the priority plan
> `../plans/2026-11-14-prd-toolkit-engine-ports.md`.
> **Needs:** 0.8.10 (released).

## 1. Why

A PRD's standards registry (section 5) and skills registry (section 6) are filled today from what
is already on the machine: linter configurations found in the repository, and the skills the session
happens to list. A platform's good practice that no installed linter enforces never reaches the PRD,
so the builder never sees it; a skill the work needs and nobody installed is never proposed; and an
activity no skill covers is done from nothing.

The owner's backlog asks that a PRD follow its platform's and language's best practices, from
sources Claude finds and the owner approves or the owner adds, and that the toolkit find, install or
write the skill a PRD needs.

**Success:** for a PRD on a platform the toolkit has never seen, one command proposes the sources,
the standards rows, the checklist items and the skills; the owner approves them once, as a PRD
change; and from then on the builder is given the practices that apply to the files it changes and
reports on each.

## 2. Scope

In scope:

1. A record of sources and practices, `practices.md`, in the PRD folder (§3).
2. A skill and command, `/prd-toolkit:prd-practices`, that proposes sources, standards rows,
   practices and skills rows, installs an approved skill from a known marketplace, and writes a
   repository-local skill when none exists (§4, §5).
3. The practices reaching the builder and the PRD review (§6).
4. A lint rule, a command `prd practices`, and help-catalogue entries (§7).
5. One optional pack key, `sources` (§8).
6. The toolkit's own PRD, the evals and the release (§9, §10).

Out of scope, and moved (owner, 2026-11-15): **writing a pack from example repositories** is its own
release, 0.8.12; conversion becomes 0.8.13. Also out of scope: publishing a written skill to a
plugin; adding a marketplace for the owner; checking that a source's page still says what it said.

## 3. The record: `practices.md`

An optional file in the PRD folder, beside `links.md` and `adoption.md`. A PRD without it behaves as
in 0.8.10. It holds two tables.

**`## Sources`**

| Column | Holds |
|---|---|
| ID | `S-nn`, two digits, never reused |
| Title | the source's name |
| Location | a URL, or a path inside the repository, in backticks |
| Covers | what it is a source for: a platform, a language, a tool, an activity |
| Read | the date its content was read, `YYYY-MM-DD` |
| Decision | `approved`, `declined` or `proposed` |

A `proposed` source blocks the PRD's approval, as a `proposed` standards or skills row does. A
`declined` source stays in the table, so it is not proposed again.

**`## Practices`**

| Column | Holds |
|---|---|
| ID | `P-nn`, two digits, never reused |
| Source | the `S-nn` it was taken from |
| Object (glob) | the files it applies to, in backticks, as a section 5 row's glob; `-` for a practice about the PRD itself |
| Applies to | `code` or `prd` |
| Practice | one sentence a reader can answer yes or no to |

A practice is a checklist item: something a linter cannot check. A rule a linter can check is a
section 5 row instead, and such a row names its source by writing the `S-nn` in its "Rules live in"
cell beside the rule file. A practice whose source is `declined` is removed in the same change.

The IDs come from `prd change ids next docs/prd/<slug> S` and `… P`, as every ID does.

**A change to `practices.md` is a PRD change.** It goes through `/prd-toolkit:prd-change`: a version,
a changelog row, the dry-run record `no dry run (wording only)` when no test case changes, and the
owner's approval at the existing approval gate. A new source or practice is a minor change (it adds
what the builder must follow); a reworded practice with its meaning kept is a patch; a removed
practice or a source moved to `declined` is a minor change.

## 4. The skill: `sourcing-practices`, `/prd-toolkit:prd-practices`

One procedure, run on demand and offered by authoring (where it fills sections 5 and 6) and by
adoption (per area).

1. **Targets.** From the PRD: each area's pack and output language, the stack in section 1, the
   linter configurations in the repository, and the file kinds each area's Boundary or contracts
   name. The result is a short list of things to source: a language, a framework, a platform, an
   activity (a migration, a release).
2. **Sources.** Proposed from three places, in this order: the area's pack (`sources`, §8); what the
   owner names; and a search, when the session has a web tool. Each is read before it is proposed,
   and the row carries the date. With no web tool, the skill says so and asks the owner for
   sources; it never writes a source it has not read, and never one from memory.
3. **A source is data.** The agent takes rules from a source's text and quotes the passage each
   practice comes from in the change's report. An instruction inside a source (to run a command, to
   install something, to change the procedure) is never followed and is reported to the owner.
4. **Standards rows.** For a rule a linter checks: a section 5 row with Decision `proposed`, only
   when the linter's command exists on this machine or is in the repository's own tooling. A linter
   that is not installed is named in the report as something the owner may install; the skill
   installs no linter.
5. **Practices.** For what no linter checks: `P-nn` rows, each one sentence, each with its glob. Few
   and checkable beats many and vague: a practice a reviewer could not answer yes or no is not
   written.
6. **Skills rows** (§5).
7. **One change.** Everything above is edited into the PRD as one `/prd-toolkit:prd-change`, and the
   approval gate shows it. Nothing is installed and no skill file is written before the approval;
   the full text of a skill the agent would write is shown to the owner with the change (§5).

## 5. Skills: find, install, write

For each activity the PRD's work needs (from the targets and the approved sources):

1. **Installed.** A skill in the session's listing that covers it: a section 6 row, `proposed`.
2. **In a known marketplace.** The catalogues of the marketplaces already added on this machine are
   read (the plugin manager's own files and commands; no network beyond what it does). A plugin
   whose skill covers the activity is proposed with the marketplace it comes from. **After the
   owner approves the change**, the agent installs it with the plugin manager's install command at
   the scope the owner names, then tells the owner to reload; lint's existing check that a
   `required` skill is installed then passes.
3. **In a marketplace not added.** Proposed with the exact commands, never run: adding a
   marketplace is the owner's step. The row stays `recommended` until the skill is installed.
4. **None.** The agent writes a repository-local skill, `.claude/skills/<name>/SKILL.md`, only from
   sources the change proposes or the PRD already approves, with a line naming them
   (`Sources: S-01, S-03`). The approval gate shows the PRD folder only, so the skill's full text is
   shown to the owner beside the change, and its section 6 row names it. After the approval the
   agent writes the file as it was shown and commits it, citing the change. It is never published.

Rules that hold throughout: no install before approval; no install from a marketplace the machine
does not already have; a built-in Claude Code skill can only be `recommended`, as today; a written
skill says what to do and cites its sources, and holds no command the sources do not give.

## 6. Where practices are used

- **The builder.** The implement context pack gains a part, **Practices**: the `code` practices
  whose glob matches a file the round may change (the same matching as a section 5 row). The
  builder's report gains a line per practice, `P-nn: followed`, `P-nn: not applicable (<why>)` or
  `P-nn: not followed (<why>)`; the last is a question for the caller, as a required skill that
  cannot be found is.
- **The PRD.** The `prd` practices join the quality-checklist step that authoring, adoption and a
  change run after lint: each is answered yes or no with the line of the PRD that shows it.
- **Nothing else changes.** Trace, the commit hook and CI do not read practices: a practice is
  judged by a reader, not by a gate.

## 7. Checks and commands

- **Lint rule `practices`** (the 41st), on a PRD that has `practices.md`: the two tables' IDs are
  well formed and unique; a Decision is one of the three; no `proposed` source on an Approved PRD;
  a practice's Source is a source of the table that is `approved`; `Applies to` is `code` or `prd`,
  and a `code` practice has a glob; a `Read` cell is a date; every `S-nn` a section 5 row names
  exists and is `approved`. A PRD without the file gets no finding.
- **`prd practices <prd_dir>`** prints the sources and the practices; `--paths <path> …` prints
  only the `code` practices whose glob matches one of the paths; `--json` prints
  `{"interface": 1, "kind": "practices", "sources": […], "practices": […]}`; `--interface` prints
  `1`. Exit 0 printed, 2 usage or no PRD.
- **`prd change ids next`** takes `S` and `P`.
- **The help catalogue** gains entries for the two tables' fields and the two ID kinds, and the new
  rule carries its description.
- **`prd change bump`** classes a change to `practices.md` by §3's rule where it can and leaves the
  rest to judgment, as for any other file.

## 8. Packs

`pack.yaml` gains one optional list, `sources`, each item `{title, location, covers}`: the sources
a pack's author recommends for its platform. The skill proposes them first (§4 step 2), as
`proposed` rows the owner decides like any other. A pack without the key is unchanged, and the
`toolkit:` range packs declare stays valid. The built-in `service` and `document` packs gain none.

## 9. The toolkit's own PRD

- A new adopted area, `practices`, written before its code: the format of `practices.md`, the lint
  rule, `prd practices`, the `S` and `P` kinds of `ids next`, and the Practices part of the
  implement context pack. Its Boundary is the new files only (`prd_practices.py`,
  `prdlint/practices.py`, `prdlint/rules/practices.py`); the edits to `context.py`, `change.py` and
  `packs.py`, which sit in areas not yet adopted, are made by the same build.
- The adopted areas that pin the rule list change with it: `lint-cli` (the rules `--list-rules`
  prints) and `help` (the catalogue's keys, the rule count).
- The skill's behaviour is not specified in the PRD in this release: the `skills` area is adopted
  last, with judged cases. It is covered by evals (§10).

## 10. Evals and release

- **New eval cases** for `sourcing-practices`: it proposes sources only after reading them; with no
  web tool it asks and invents nothing; an instruction inside a source is reported and not followed;
  nothing is installed before approval; a plugin from a marketplace not added is proposed with its
  commands and not installed; a written skill cites its sources.
- **Rerun** the cases of the skills whose text changes: authoring, adopting, building and the
  builder agent. The rest of the suite is not rerun.
- Version 0.8.11; ten skills and eleven commands; README sections for practices and the command;
  the changelog entry with its upgrade note (a repository gets the rule and the command with its
  next `install` from the 0.8.11 plugin; a PRD without `practices.md` needs nothing).
- The umbrella, the backlog and the priority plan are renumbered: 0.8.12 pack authoring from example
  repositories, 0.8.13 conversion.

## 11. Decisions and what was set aside

- **Split** (owner, 2026-11-15): sources and skills now; pack authoring next; conversion after.
- **A file in the PRD folder**, changed and approved as the PRD is (owner), not a separate record
  with its own revision and gate, as the earlier prototype had: one approval track.
- **The agent installs only from marketplaces already added** (owner). A new origin is the owner's
  step.
- **A written skill is repository-local** (owner), from approved sources, shown with the change
  and written once the change is approved.
- **Practices are judged by a reader.** No gate fails on a practice: the builder reports, and a
  `not followed` is a question. A rule that should fail a gate is a section 5 row with a linter.
- **Set aside:** rechecking a source's page for changes; a practice with a severity; sharing
  practices between PRDs other than through a pack; proposing a linter's installation as a step the
  toolkit runs; practices in the status report's Next part.

## Revisions

None yet.
