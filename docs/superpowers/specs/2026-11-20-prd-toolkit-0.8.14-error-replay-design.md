# prd-toolkit 0.8.14: a replay that proves a fix, and a close for an error no area covers — design

> **Date:** 2026-11-20
> **Author:** Ivan Histand & Claude Code
> **Status:** Draft, for the owner's review.
> **Extends:** the priority plan `../plans/2026-11-14-prd-toolkit-engine-ports.md` (its "Phase 1: red
> replay", which this spec supersedes where they differ) and the backlog
> `2026-11-08-prd-toolkit-0.8.6-backlog.md` (item 5).
> **Needs:** 0.8.13 (released).

## 1. Why

**Nothing shows that the fix fixed it.** An error entry closes with a line such as
`T-005.3 [integration], PRD 1.0.1, fixed in 0dd4037`. `prd error check` verifies that the T-id has a
test case and a test, that the version has a changelog row and that the commit is in history. It does
not verify the claim itself: that this commit is what turned the test green. The only red proof is a
line in the tester agent's report, which nobody can recompute.

**An error in code no adopted area covers cannot close.** `prd error resolve` refuses a fix that has
no T-id, and a T-id belongs to a requirement. Code outside every adopted Boundary has no requirement,
so `/prd-toolkit:prd-build --fixes` has no block to build and the entry stays `confirmed` for good.
E-017 in the toolkit's own ledger has been open that way since 2026-11-11, though its fix is on
`main`.

**Success:** anyone with the repository can run one command and see whether the commit an entry
names turned its test from failing to passing; an error in uncovered code closes with that proof in
place of a T-id; E-017 is resolved; and every ledger line written before this release reads and
checks as it did.

## 2. Scope

In scope:

1. An optional `One test` column in `testing.md` Levels: the command that runs one test (§3).
2. `prd error replay <prd dir> <E-nnn>`: fails before the fix, passes on it (§4).
3. A fourth resolution form, for a fix outside every adopted Boundary, which `resolve` writes only
   when its replay holds (§5).
4. The `handling-errors` skill: the route for such an error, and the replay before a resolution is
   committed (§6).
5. The toolkit's own PRD, E-017's close, the evals, the proof and the release (§7 to §9).

Out of scope: a replay job in the generated CI; reading a harness's per-test results; a replay that
runs a whole level; a replay of an entry whose level is a deploy-gate level; adopting the rest of the
`errors` area; conversion (§10).

## 3. The `One test` column

A Levels table may hold one more optional column, `One test`, found by its header name as
`Environment` and `Timeout` are:

```
| Level | Harness command | Environment | Gate | One test |
|---|---|---|---|---|
| unit | `uv run pytest -q tests --ignore tests/system` | local | build | `uv run pytest -q` |
| system | `uv run pytest -q tests/system` | staging | deploy | |
```

- The cell is **one simple command** in backticks, under the rules a `Harness command` follows: no
  `cd`, `env`, `sh`, `bash`, `zsh`, `eval` or `exec` as its first word, no `$`, `{` or `~`, no
  env-var prefix, no chain. A blank cell, or no column, means the level has no such command.
- The replay appends **exactly one argument** to it, a path or a test id, and runs the result from
  the repository root without a shell. So the command must accept a path relative to the repository
  root: for a project in a subfolder, `uv run --project <folder> pytest -q`, not
  `uv run --directory <folder> pytest -q`.
- Lint reports a malformed cell through an existing rule; the rule count stays 41. The format
  reference and `prd help` describe the column.
- Nothing else reads it: the level's `Harness command` still runs the level at a build and at a
  deploy, and the tester guard allows what it allowed.
- A PRD that adds the column takes a patch with the §14 row
  `format: One test column (prd-toolkit 0.8.14)`. A PRD that never adds it needs no change, and its
  entries are skipped by the replay (§4).

The command is PRD text, so it changes only through a change the owner approves. That is why the
replay may run it.

## 4. The replay: `prd error replay <prd dir> <E-nnn>`

**The claim.** "`<sha>` fixed it" means two runs: the test fails on the commit before `<sha>`, and
passes on `<sha>`. The replay makes both runs and reports what they show. It reads the entry from
`errors.md` in the working tree, so it works on a resolution that is written and not yet committed.

**What it runs.** Always the `One test` command of the entry's level, from `testing.md` in the
working tree, with one argument appended:

| | An entry with a T-id (`T-005.3 [integration], PRD 1.0.1, fixed in <sha>`) | An entry with a red run (§5) |
|---|---|---|
| The argument | each file under the test roots that cites the T-id (`@prd <T-id>`) | the test id the resolution holds |
| Where the tests come from | the **resolving commit**: the commit whose `errors.md` first holds this Resolution line, or `HEAD` when the line is not committed | the commit under test |
| Before | the tree of `<sha>^`, with its test roots replaced by the resolving commit's: **at least one cited file must fail** | the tree of `<sha>^` as committed: **must fail** |
| After | the tree of `<sha>`, with its test roots replaced the same way: **every cited file must pass** | the tree of `<sha>` as committed: **must pass** |

- **Why the resolving commit.** A regression test is often committed after its fix: the builder's
  commit comes first and the tester's test follows. The fix commit then holds no test for the T-id,
  so a replay that took the tests from it would call a real fix unproven. At the resolving commit
  the test exists and is no longer marked known-failing, because `check` refuses a resolution whose
  T-id is.
- **Why the test roots whole, and only the cited files run.** A test file finds the helpers it was
  written with. The other tests of the resolving commit are not run, because a test written later
  can fail on older code for reasons that have nothing to do with the entry.
- **`<sha>^`** is the commit's first parent. A commit with no parent is a finding.
- **A run** is the command started from the worktree's root, with the process's environment, in its
  own process group. Exit 0 is a pass; any other exit is a failure. The level's `Timeout` applies
  (600 s without one), and `--timeout <seconds>` overrides it. A run that times out is killed and is
  a finding, never a proof.
- **Worktrees.** Each run happens in a temporary git worktree outside the repository, removed when
  the run ends, on a finding, on a timeout and on an interrupt alike. The working tree and the index
  are never written.

**Outcomes.**

| Exit | Meaning | Output |
|---|---|---|
| 0 | the proof holds | `<E-nnn>: <T-id or test id> fails on <sha>^ and passes on <sha>` |
| 0 | skipped | `skipped: <E-nnn>: <reason>` |
| 1 | findings, one per line | below |
| 2 | usage or tool error | as the other `prd error` commands |

Skipped, each with its reason: the entry is resolved by an environment run or as not a defect (it
names no fix commit); its level is a deploy-gate level (its proof is the deploy run); its level has
no `One test` command.

Findings (the wording is settled in the PRD's acceptance criteria):

- `<E-nnn> is not resolved`.
- `<E-nnn>: <T-id> is cited by no test in <resolving commit>`.
- `<E-nnn>: <T-id or test id> passes on <sha>^; <sha> did not turn it green`.
- `<E-nnn>: <T-id or test id> fails on <sha>: <file or test id>`.
- `<E-nnn>: <sha> has no parent`, `<E-nnn>: <level> is not a level of testing.md`, and
  `<E-nnn>: timed out after <N> s on <commit>`.

`--json` prints one document with `interface: 1`: the entry, `outcome` (`holds`, `skipped` or
`findings`), the reason or the findings, and one record per run (the commit, `before` or `after`,
the argument, the exit code and the seconds it took).

**Limits, stated in the README.**

- An exit code cannot tell a test that failed from one that could not run. The second run catches a
  harness that cannot run in a fresh checkout, because it fails there too and the proof does not
  hold.
- The proof is per file. Two entries fixed together whose tests share a file share one proof.
- For an entry with a T-id, a test added to the same file between the fix and the resolve can fail
  the second run.

## 5. The fourth resolution form

A Resolution line is today one of three forms: a fix with a T-id, an environment run, or
`not a defect: <why>`. The fourth is a fix with no T-id:

```
fixed in <sha>, red run <test id> [<level>]
```

`<sha>` is 7 to 40 lowercase hex digits, `<test id>` is what the level's `One test` command takes as
its argument, and `<level>` is a build-gate level. It holds no PRD version: no requirement changed.

```bash
prd error resolve docs/prd/<slug> <E-nnn> --commit <sha> --red-run <test id> --level <level>
```

`resolve` refuses this form, and writes nothing, when:

- **The fix commit changes a file an adopted area covers.** That code has requirements, so the fix
  takes a regression T-id and `/prd-toolkit:prd-build --fixes`. The refusal names the file and its
  area. A PRD with no adoption map covers every path outside the PRD folder and `.prd-toolkit/`, so
  it can never use this form.
- **The entry's class is not `code bug`.** The other classes have their own routes: a change to
  the PRD, or an environment run.
- **The level** is not in Levels, is a deploy-gate level, or has no `One test` command. The last
  refusal says to add the column through `/prd-toolkit:prd-change`.
- **The test id** holds white space or starts with `-`: it becomes a command argument.
- **`--t` or `--version`** is given with `--red-run`, or `--red-run` without `--commit` and
  `--level`.
- **The replay does not hold** (§4). `resolve` runs it before it writes the line and prints its
  findings as the refusal. A fix with a T-id is proven by its build; this form has no build, so the
  replay is its only proof and the command makes it.

The entry must be `confirmed`, as for every form.

**`prd error check`** accepts the fourth form on a resolution added in its range and reports, without
running a test: a line that is none of the four forms; a commit that is not an ancestor of `HEAD`; a
commit that changes a file an adopted area covers; and a level that is not in Levels.

**Unchanged.** The three existing forms are written, read and checked as before, byte for byte, and
`resolve` runs no replay for them. Nothing else parses a Resolution line: the published page prints
it as text.

**An older vendored copy** reports a fourth-form line as none of the three forms it knows, so a
repository re-vendors before its ledger holds one (§9, the upgrade note).

## 6. The skill: `handling-errors`

**An error in code no adopted area covers.** After the owner confirms the class `code bug`, and when
the diagnosis shows the faulty code outside every adopted Boundary, the entry takes its own route in
place of `/prd-toolkit:prd-change` and `/prd-toolkit:prd-build`:

1. **The failing test first.** An existing test that fails on the error, or a new one, committed on
   its own before any fix (`Refs: <E-nnn>`), and run with the level's `One test` command to show it
   failing.
2. **The fix**, in its own commit citing the entry.
3. **`resolve --red-run`,** which replays and refuses a fix whose test did not fail before it and
   pass on it.
4. **The ledger committed, then `prd error check`,** as for every entry.

- **The session writes that test and that fix itself.** The skill's rule is that an agent never
  edits code or tests, because the builder and the tester do, each from the PRD. Those agents work
  from requirement blocks, and this code has none. The exception holds only for code outside every
  adopted Boundary, only after the owner's confirmation, and only with the test first. Everything
  else in the loop stands: record first, no fix before `Confirmed:`, no retry in place of a
  diagnosis.
- **No `One test` command is a stop.** The skill says so and sends the column through
  `/prd-toolkit:prd-change`, so the owner approves the command before anything runs it.
- **A fix that turns out to touch an adopted file** is refused by `resolve`; the skill then takes the
  usual route for that part.

**An entry with a T-id** gains one step. After `resolve` and before `errors.md` is committed, the
skill runs `prd error replay`. On findings it puts `errors.md` back, leaves the entry `confirmed`,
reports each finding and returns to the build. A skip is named in its report, with its reason.

The skill's text changes under `superpowers:writing-skills`: baseline runs without the new text
first, then the text, then the evals of §9. The owner reads the changed text before the build
closes.

## 7. The toolkit's own PRD

One new adopted area, written before its code, as the areas of 0.8.12 and 0.8.13 were:

- **`error-replay`:** the replay, the fourth form's rules, and the `replay` command. Boundary: one
  new file, `prdlint/errorreplay.py`. The edits to `prd_error.py` and `prdlint/errors.py`, in the
  `errors` area that is not yet adopted, are made by the same build and stay thin: they parse the
  new flags and call the new module.
- **The `One test` column** is read by the Levels loader in `prdlint/model.py`, inside the adopted
  `lint-cli` Boundary, and its malformed-cell finding belongs to a lint rule. The change's first
  step settles where each requirement is written, as 0.8.12 did for its two parse requirements.
- **The toolkit's own `testing.md`** gains the column for its two levels:
  `uv run --project prd-toolkit pytest -q -n auto` for `unit` and for `integration` (measured for
  `unit`, §8; the plan measures `integration`).
- Expected level: minor (8.3.1 to 8.4.0), unless an existing test case pins something these touch,
  which the change's `bump` step decides.
- The skill's behaviour is not specified in the PRD: the `skills` area is adopted last. It is
  covered by the evals.

**Tests the PRD's cases must cover,** each on a small git repository built for the test, with a
commit that holds the bug, a commit that holds the test and a commit that holds the fix:

- a real fix holds, for an entry with a T-id and for one with a red run;
- a test that passed before the fix is a finding;
- a test committed after its fix still proves it (the resolving commit supplies the test);
- the first run executes the old code: only the test roots are replaced;
- a harness that cannot run in a fresh checkout fails the second run and proves nothing;
- the worktrees are gone after a finding and after a timeout;
- each skip, with its reason;
- each refusal of the fourth form, and that a refused `resolve` leaves `errors.md` as it was;
- `check` on a fourth-form line, and the three older forms unchanged.

## 8. E-017 and E-032

- **E-017 closes by the fourth form,** in the toolkit's own ledger, once the build is verified:
  `fixed in 6d6711b, red run prd-toolkit/tests/test_builtin_packs.py [unit]`. Measured while this
  spec was written, on copies of the tree before and after `6d6711b`: the `unit` command above with
  that path failed on the earlier tree in two runs of two, and passed on `6d6711b` in two runs of
  two. Without `-n auto` the earlier tree passed, which is why the command carries it.
- **E-032 is not part of this design.** It goes through the error loop: reproduced, diagnosed, its
  class proposed to the owner. A fix joins this release only when the owner confirms the class and
  says so.

## 9. Evals, proof and release

- **Rerun** every eval case of `handling-errors`, whose text changes.
- **New eval cases:** an error in code no adopted area covers is fixed test first and resolved with
  `--red-run`, never through `/prd-toolkit:prd-build`; and replay findings after `resolve` leave the
  ledger uncommitted and the entry `confirmed`.
- **The proof,** in an acceptance record: `prd error replay` run on every resolved entry of the
  toolkit's own ledger, with what each showed (holds, skipped or findings). The older entries are
  not required to hold: several were fixed by one commit, and the record says what the replay makes
  of that. E-017 is the entry that must hold.
- **Version 0.8.14;** README sections for the replay, the fourth form and the `One test` column; the
  changelog entry with its upgrade note: re-run `prd hooks install` from the 0.8.14 plugin and
  commit `.prd-toolkit/` before a ledger holds a fourth-form line; the generated CI file is
  unchanged; a PRD needs no change unless it wants the replay, which takes the column as a patch.
- The priority plan marks 0.8.14 delivered.

## 10. Decisions and what was set aside

- **0.8.14 is this release** (owner, 2026-11-19). Conversion, which held the number, is still
  wanted and goes to the backlog with no release.
- **A resolution with no T-id** (owner), over adopting the area first: an error in uncovered code
  does not wait on an adoption.
- **A command and a step of the skill, with no CI job** (owner). The generated CI is unchanged and
  no repository regenerates it. An agent that skips the skill's step is not caught for an entry
  with a T-id; for the fourth form `resolve` itself replays.
- **Exit codes and an owner-approved one-test command** (owner), over a command stored in the
  resolution line, which no gate would review, and over reading per-test results, which every
  harness would have to produce.
- **No whole-level replay.** The plan's sketch ran the T-id's whole level with the fix commit's
  tests. In this repository's own history a regression test follows its fix, so the fix commit holds
  no test; and with the tests of a later commit a whole level fails on older code whatever the
  entry.
- **`resolve` replays the fourth form** (owner), because nothing else proves it.
- **The session writes the test and the fix for uncovered code** (owner), as a stated exception.
- **A small new area** (owner), over adopting the whole `errors` area in this release.
- **Set aside:** the CI job; per-test results (a JUnit report or the like); a replay of deploy-gate
  entries; a filter finer than a file for an entry with a T-id; adopting the rest of `errors`.
