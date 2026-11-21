# prd-toolkit 0.8.14: the toolkit's own ledger — acceptance record

> **Date:** 2026-11-20 and 2026-11-21
> **Plan:** `2026-11-20-prd-toolkit-0.8.14.md`, Task 5. **Spec:** `../specs/2026-11-20-prd-toolkit-0.8.14-error-replay-design.md`.
> **Result:** passed, with the findings below. The toolkit's own PRD is 9.0.0; one entry, E-034, is left open.

## What was run

`prd-toolkit/scripts/prd error replay docs/prd/prd-toolkit <E-nnn>` for every entry of the toolkit's own
ledger, E-001 to E-035, on the release branch, twice: once on the first build of the area (trees made
with `git worktree add`) and once after E-035's fix (trees made as clones). Both runs gave the same
outcome for every entry they share, and after each the repository's worktree list and `git status`
were as before.

| Outcome | Entries |
|---|---|
| The proof holds (23) | E-010 to E-017, E-019 to E-028, E-030 to E-033, E-035 |
| Skipped: resolved as not a defect (2) | E-018, E-029 |
| Findings (9) | E-001 to E-009 |
| Not resolved (1) | E-034 |

Two of the 23 are closed by the fourth form, a red run: E-017
(`fixed in 6d6711b, red run prd-toolkit/tests/test_builtin_packs.py [unit]`) and E-032
(`fixed in 4514ecb, red run prd-toolkit/tests/test_guard_session_tasks.py [unit]`).

## The nine findings

None is a defect of the replay: each time the command did what FR-076 to FR-078 say. Each was checked
by hand, on trees exported from the two commits with the test roots replaced as the replay replaces
them. The entries stay resolved as written.

| Entries | Finding | Cause |
|---|---|---|
| E-001 to E-007 | `<T-id> fails on <sha>: <file>` | The trees of those fixes predate the commit that added the parallel test runner, so the level's One test command (`pytest -q -n auto`) is a usage error, exit 4, on both trees. Without `-n`, E-003, E-004, E-006 and E-007 would hold; E-001, E-002 and E-005 would still fail, because another test of the same file, or the cited test itself, asserts behaviour a later commit added. |
| E-008 | `T-019.2 passes on <sha>^; <sha> did not turn it green` | The fix lies wholly inside a test root (a `conftest.py`). Both trees get the resolving commit's test roots, so they are the same tree. With the parent's own `conftest.py` the test fails, so the fix is the right one. |
| E-009 | `T-022.4 fails on <sha>: <file>` | The proof is per file. Another test of the file, T-022.5, tests behaviour that E-014's later fix added, and fails on E-009's fix commit. |

The README's known limits now name the three causes: a tree older than what the One test command
needs, a fix inside a test root, and the proof per file.

## What the release's own work added to the ledger

Four entries were recorded while 0.8.14 was built. Each was classed by the owner before any fix.

- **E-032** (`code bug`): the tester guard refused the tester's Read of its own background run's
  output in a headless session, whose hook input names no scratchpad. The guard now finds the tasks
  folder by the session id. It was the first use of the route for code no adopted area covers: the
  failing test committed alone (`2cf8b04`), the fix (`4514ecb`), `resolve --red-run`, `check`.
- **E-033** (`code bug`): the replay wrote the index of the repository it was started in when
  `GIT_INDEX_FILE` was set. A code review of the first build found it. PRD 8.5.0, regression case
  T-079.6, fixed in `005cbd8`.
- **E-035** (`environment`): the replay could not add its worktree where the repository's git folder
  cannot take one, as in the Bash sandbox of a Claude Code session, so both new eval cases ended with
  an internal error. The owner chose to change the replay, not to ship the limit. PRD 9.0.0 (a major
  version: a test that relied on its tree being a linked worktree can now fail): each run's tree is a
  clone, and the replay writes nothing in the repository's git folder. Regression case T-079.7, fixed
  in `efcbe2e`. The two eval cases then scored 1.00 with the plugin.
- **E-034** (`code bug`, open): a unit test of the inbox page acts on the panel a fixed 300 ms after
  opening it, so it fails now and then in a whole parallel run and passes alone. The red-run route
  cannot close it as written: the faulty test passes when run alone, so it has no red run to give.
  The owner left it open for this release.

## What is the owner's to decide

- **E-034:** whether the `handling-errors` skill's exception for a faulty test is widened, so that a
  new test that reproduces the race stands as the red run while the fix changes the faulty test.
- **Older trees:** whether the One test command of the `unit` and `integration` levels should run
  without `-n auto`, which would let the replay prove E-003, E-004, E-006 and E-007.
- **The repositories that use the toolkit:** each re-runs `prd hooks install` from the 0.8.14 plugin
  and commits `.prd-toolkit/` before its ledger holds a fourth-form line.
