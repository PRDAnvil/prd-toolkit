# prd-toolkit 0.8.22: the last deferred minors of 0.8.21's review

Approved by the owner on 2026-11-26 ("approved, go ahead"). A small change: this note is the short design.

## Intent

0.8.21's final review deferred three minors in the Memory section's second place and in its eval check. None
changes what the skill does; each makes a statement true or says what a check can and cannot see.

## Goals

- **M4.** Where step 2 no longer says the folder names "match whenever the session has its own config
  directory": that holds only for a session started at the repository root. It says the names can match
  while the directories differ, and keeps "compare the two full paths; skip only when identical".
- **M5.** The README's adoption paragraph names the second place as the skill does
  (`$HOME/.claude/projects/<the repository root, each non-alphanumeric as ->/memory/`), drops 0.8.20's "when
  that is another directory", and is rewrapped. A unit test ties the README's wording to the skill's.
- **M6.** `lists-the-home-memory-place` says in its body what it checks: a mention of the expanded path in the
  trace, not proof of a listing; a listing written with `$HOME` or `~` does not match; it depends on the
  runner's sandbox home being named `home`.

## Non-goals and anti-goals

- No new memory rule and no change to the order or number of places.
- The grader's pattern stays: without the runner's trace format in hand, a stricter pattern risks false fails.

## Constraints

- Release 0.8.22: the three version places; `test_release_0_8_22.py` pins it, `test_release_0_8_21.py` stops
  pinning. The bump commit cites `Refs: FR-270` (IDs only).
- The changelog entry names no spec file (the release area's AC-276.2, which the PRDAnvil session's branch makes
  pass).
- One regression run of `adopting-memory-conflict`, since the Where text changes.

## Approaches

1. **(Chosen) Wording and documentation.** Three text edits, pinned by unit tests.
2. **A stricter trace pattern for M6** (only inside a tool call's input). Better in principle, but it needs the
   trace format, which the runner does not document.

## Left to the builder

The exact rewording.
