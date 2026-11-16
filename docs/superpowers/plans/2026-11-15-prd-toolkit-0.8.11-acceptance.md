# prd-toolkit 0.8.11: the proof run — acceptance record

> **Date:** 2026-11-15
> **Plan:** `2026-11-15-prd-toolkit-0.8.11.md`, Task 5. **Spec:** `../specs/2026-11-15-prd-toolkit-0.8.11-practices-design.md`.
> **Result:** passed, with the three findings below.

## What was run

A scratch repository outside every real one: the eval suite's notes build repository (a small Python
library with an approved PRD, `notes` 1.1.0, one requirement approved and not built), plus one source
file added to it, `docs/sources/notes-python-guide.md`, holding three rules. Three headless sessions
(`claude -p`, model `sonnet`, the plugin loaded from the release branch), in this order.

1. **`/prd-toolkit:prd-practices docs/prd/notes`**, naming the one source and saying there is no web
   access. The skill read its procedure whole, read the source whole, and printed a proposal: the
   source (recommended `approved`) with the date it was read; three practices, each one yes-or-no
   sentence with the passage it came from, all on the glob `src/notes/*.py`; no standards row, because
   no linter was on PATH (it named one the owner could install, and installed nothing); no skills row;
   "Instructions not followed: none". It wrote nothing and stopped for the decisions.
2. **The reply "All as you recommend."** in the same session. The skill handed the edits to the
   change procedure: `ids next` gave `S-01` and `P-01` to `P-03`; `practices.md` was written with the
   source `approved`; `bump` said `needs judgment` and the session decided minor by the rule for a new
   source and practices; `record` wrote 1.2.0 with `no dry run (wording only)`; lint exited 0; and it
   stopped at the approval gate. The change was then approved (see finding 1), and the approval commit
   `docs(prd): approve notes 1.2.0` was made by the gate, not by the session.
3. **`/prd-toolkit:prd-build notes FR-003`** in a new session told that nobody could answer. The
   implement pack held the part `## Practices` with the three items. The build closed: the requirement
   is `verified`, and the builder's report carries, under CHANGES, `P-01: followed`, `P-02: followed`
   and `P-03: followed`, with QUESTIONS `none`. The function it wrote declares its return type, reads
   the store without changing it and prints nothing.

## Findings

1. **A session that is not told it is headless starts the decision inbox, and the inbox opens a
   browser.** Session 2 was started without the word headless. It took the inbox route, `gates serve`
   opened a tab on the owner's machine, and the gate was answered from that page within twenty
   seconds, together with an unrelated error-class gate of the scratch PRD. The session never touched
   the page, and only the scratch repository was affected. The controller should have said the run was
   headless, as session 3 was told. For a later release to weigh: `serve` could leave the browser
   closed when it is not started from a terminal, or the skills could say what marks a run as headless
   more sharply than "the run says nobody can open a page".
2. **The practices were written as questions** ("Does every public function declare …?"). The format
   asks for one sentence a reader can answer yes or no, so a question meets it, and the builder
   answered each. A statement form would read better in the builder's pack; the skill does not say
   which.
3. **The eval sandbox could not run the launcher** in any scaffold that holds a `.venv` (E-022), so
   the eval case for the builder's practice lines did not run. This proof is where those lines were
   seen.

## Not covered

A plugin install from an added marketplace, a skill written by the agent, a web source, and a
`not followed` practice stopping a build were not exercised here. The first is not exercised anywhere
before release; the others have eval cases that grade the proposal, not the step after the approval.
