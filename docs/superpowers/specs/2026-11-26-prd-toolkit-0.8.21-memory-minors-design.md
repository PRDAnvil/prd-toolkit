# prd-toolkit 0.8.21: the deferred minors from 0.8.20's review

Approved by the owner on 2026-11-26 ("approved, go ahead"). A small change: this note is the short design.

## Intent

0.8.20 made `adopting-prds` read the owner's Claude Code memory. Its final review deferred four minors (M5, M10,
M12, M14). They leave a rule list incomplete, one README paragraph under-described, and two of the review's focuses
(no relevant memory; headless with a note that answers a marker) guarded only by unit pins. This release closes
them, so a later prompt change that breaks either focus fails an eval.

## Goals

- **M10.** Non-negotiable rule 3's list of what code may contradict names an owner's memory note, as extract rule 2
  already does.
- **M12.** The README's adoption paragraph names the three places the skill reads memory from: the directory the
  system prompt names, `~/.claude/projects/<repo root, encoded>/memory/`, and a directory the user names.
- **M5.** `adopting-memory-conflict` also fails if the other project's token is in any Agent or Bash call.
- **M14.** Two new eval cases:
  - `adopting-memory-unrelated`: the session's memory holds only another project's notes. Extraction finishes, no
    `errors.md` entry names a memory note, the token reaches no Write, Edit, Agent or Bash call, and the final
    message says no memory note names this repository.
  - `adopting-memory-headless-owner`: an empty PRD, a headless prompt, and a memory note naming the repository's
    owner. The PRD's `owner:` stays a `[NEEDS CLARIFICATION]` marker and the final message proposes the owner,
    naming the note.

## Non-goals and anti-goals

- No new rule about memory. The Memory section's rules stand; this release only completes a list and adds
  evals and README text.
- An anti-goal: an eval that a toolkit which never reads memory passes. Each new case has a grader 0.8.19 fails.

## Constraints

- Release 0.8.21: plugin.json, marketplace.json and `.prd-toolkit/VERSION` together; `test_release_0_8_21.py`
  pins it and `test_release_0_8_20.py` stops pinning the version.
- Eval scaffolds follow `adopting-memory-conflict`: the runner-sandbox guard on `HOME`, notes in both the config
  memory dir and `$HOME/.claude/projects/<encoded cwd>/memory/`, a clean git status.
- Fixture names and tokens are invented. No real person, login or path.
- Spend: about five eval runs.

## Approaches

1. **(Chosen) Evals plus text.** Two new cases, two new graders, one rule edit, one README edit.
2. **Unit pins only.** Cheaper, but the review's point was that unit pins cannot catch a behavioural regression.
3. **One combined eval** (unrelated notes and a headless owner note in one case). Fewer runs, but a failure would
   not say which focus broke.

## Left to the builder

The fixture owner's name, the notes' wording, and the regexes of the last-message graders.
