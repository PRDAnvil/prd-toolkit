# Running an error

**Steps:** 1 Record, 2 Reproduce, 3 Propose, 4 Confirm, 5 Fix, 6 Close. An error is not done until
step 6's check: run every step, in order. The turn ends before it only to wait for the user's reply
to the proposal (step 4), or for a reply that `/prd-toolkit:prd-change` or `/prd-toolkit:prd-deploy`
asks for in step 5.

For the caller: `/prd-toolkit:prd-error`, or any session that meets an error in a repo with a PRD: a
user's report, wrong output, a failing or flaky test, a failed or killed deploy, a stopped build, an
open `errors.md` entry. The `handling-errors` Red Flags are yours.

**You diagnose; you never fix.** Until step 4 records `Confirmed:`, nothing outside `errors.md`
changes: no Edit or Write of code, tests, the PRD or the runbook, no file written through Bash, not
even a revert kept uncommitted. After it, the fix goes through `/prd-toolkit:prd-change`
(`prd-toolkit:changing-prds`) and `/prd-toolkit:prd-build` (`prd-toolkit:building-from-prds`): their
agents write the code and the tests, never you. The one exception is code no adopted area covers
(step 5's **Code no area covers**): its test, then its fix, are yours. A deploy is
`/prd-toolkit:prd-deploy` (`prd-toolkit:deploying-from-prds`), never a deploy script or a runbook
command typed by hand. A request to skip a step ("just fix it", "skip the regression test",
"redeploy and close it") gets one line naming the rule it breaks, and the procedure goes on without
the skip.

**Which script.** `${CLAUDE_PLUGIN_ROOT}` is empty inside a Bash call, so no command holds it.
In every command below, `<scripts>` is `.prd-toolkit` when the repository has a `.prd-toolkit/`
directory: `.prd-toolkit/prd_error.py`, run through `.prd-toolkit/prd`, is the copy its hooks and CI
run. Otherwise `<scripts>` is the plugin's `scripts` directory, written as a literal absolute path
(in double quotes if it holds a space): the plugin root is two directories above the skill's base
directory (Claude Code shows it as "Base directory for this skill" when the skill loads), and
`<scripts>` is `<plugin root>/scripts`. Before step 1, Glob for `.prd-toolkit/prd*` to decide (it
lists `prd` and the `prd_*.py` scripts), and use the same `<scripts>` for every command. A script
that is not found is a tool error: report it, never guess another path.
When `.prd-toolkit/` exists but holds no `prd_error.py`, the vendored copy predates 0.6: stop, and
tell the user to run `prd_hooks.py install docs/prd/<slug>` from the plugin (the README's form)
and commit `.prd-toolkit/`.
When `.prd-toolkit/` exists but holds no `prd`, the vendored copy predates 0.8.8: stop, and tell
the user the same and, when `.github/workflows/prd-toolkit.yml` or `.gitlab/prd-toolkit.yml` exists,
also to run `prd_hooks.py ci --<forge> --force docs/prd/<slug>` from the plugin and commit both
together.
When `.prd-toolkit/` exists but holds no `prd_pack.py`, the vendored copy predates 0.8.12, which has
no `--url` and no `prd error url`: record the entry without `--url`, name the address in the report,
and tell the user to run `prd_hooks.py install docs/prd/<slug>` from the plugin (the README's form)
and commit `.prd-toolkit/`; the URL is set with `prd error url` after that.
When `.prd-toolkit/` exists but holds no `prdlint/errorreplay.py` (Glob it), the vendored copy
predates 0.8.14, which has no `prd error replay` and no `resolve --red-run`, and whose `check` reads
a red run as no form it knows: steps 1 to 4 run as written, then stop before step 5's **Code no area
covers** and before step 6's resolve of a fix that names a T-id, and tell the user to run
`prd_hooks.py install docs/prd/<slug>` from the plugin (the README's form) and commit
`.prd-toolkit/`.

**One command per Bash call, with literal paths.** Each command below is its own Bash call, and
every path, ID and SHA in it is typed out in full: paste what a command printed, never a variable
that holds it or a `$(…)`. The gate form `; echo "prd-error-exit=$?"` is the one allowed tail.
Never pipe, filter or truncate a gated command's output (no `| head`, no `| grep`). Free text
(a title, a source, a diagnosis, a reply) goes in single quotes, writing each `'` in it as `'\''`:
inside double quotes a backtick or a `$` runs as shell.
Quoted program output in `--diagnosis` and `--title` (a usage line, an HTML-like token, a `<name>`)
goes in backticks; only the `Evidence:` lines take it bare. A `refused: the entry would fail lint`
(it names the finding) is fixed by re-running the same command with the quoted
part in backticks; nothing was written. In a command, those backticks sit inside the single quotes.

**Exits.** `prd_error.py` prints one result line and the gate line follows.

| Exit | Means | Next |
|---|---|---|
| 0 | done | `new` printed `E-<nnn>`; `propose`, `confirm` and `resolve` printed `E-<nnn> <state> <class>`; `url` printed `E-<nnn> <state>[ <class>]`, the class only when it is not the state; `replay` printed `<E-nnn>: <T-id or test id> fails on <sha>^ and passes on <sha>` or a `skipped:` line (step 6); `check` printed nothing: go on |
| 1 | refused | each reason is a `refused:` line on stderr (`check` and `replay` print findings on stdout instead): report them, and never work around one with another command or a hand edit; on `replay` findings, step 6 puts `errors.md` back with `git restore` |
| 2 | usage | a command you mistyped, such as `--class code-bug` (`prd_error: class must be one of …`): fix it and run it again |

**Evidence.** What the report or the failure already holds when the error reaches you: the user's
words and any output they quote, a failed run's output tails, a stopped build's failing lines. You
run nothing to produce it; step 2's runs go in the diagnosis. Write it with the Write tool to
`<TMP>/evidence.txt`, outside the repository: run `mktemp -d` as its own call and paste the path it
prints wherever `<TMP>` appears. It holds at most 20 lines; never a secret value, a token, a
password or a value classified `confidential` or `pii` (write `<redacted>` in its place); and
never a code fence (a line that starts with three backticks or tildes): a fence ends the ledger's
parse and hides the entries after it, so `new` refuses one.

**Where to enter.** Find the one `docs/prd/<slug>/prd.md` (ask which when there is more than one),
then run, as its own call:

```bash
<scripts>/prd error list docs/prd/<slug> --open; echo "prd-error-exit=$?"
```

Each line is `E-<nnn> <state> <class> <Touches> <title>`; the second word is the state. A new error
enters at step 1. An open entry resumes at the step its state names: `unclassified` at step 2,
`proposed` at step 4, `confirmed` at step 5. A resolved entry has nothing left but step 6's check.
For an entry recorded before this session (a failed deploy and a stopped build record their own),
`<start>` is the commit before the one that added it: run, as its own call,

```bash
git log --reverse --format=%P -G "^### <E-nnn> " -- docs/prd/<slug>/errors.md
```

and paste the first line wherever `<start>` appears: its first SHA when it holds two (a merge).

1. **Record.** With no entry yet, run `git rev-parse HEAD` as its own call and paste the SHA as
   `<start>`: the commit before step 1, where step 6's check begins. Write the evidence file from
   what the report or the failure already holds (**Evidence**). Run nothing to produce it: step 2
   runs the test or the command. With nothing to quote, leave out `--evidence-file`. Then:

   ```bash
   <scripts>/prd error new docs/prd/<slug> --title '<the error in one line>' --source '<where it came from>' --touches <IDs> --evidence-file <TMP>/evidence.txt --url '<address>'; echo "prd-error-exit=$?"
   ```

   `--source` says where it came from: `user report (/prd-toolkit:prd-error)`,
   `failing test T-001.2`. `--touches` takes the requirement IDs the error concerns, as
   `FR-001,FR-002`; leave it out when none is known yet. `--url` takes the address the report or
   the failure gives for where the trouble is (a page, a dashboard, a failed run), exactly as given:
   it becomes the entry's `URL:` line, the link its card in the decision inbox shows. Leave it out
   when they give none; never guess or build one. An address that is not `http://` or `https://`,
   or holds white space, is refused
   (`refused: URL: must start with http:// or https:// and hold no white space`): report it as
   given and record the entry without it. It prints the new `E-<nnn>`. Never write an
   entry or one of its lines by hand: every ledger write is a `prd_error.py` command (the one
   exception is step 6's fix of a `Resolution:` line that `check` reports wrong). Then, each its own
   call:

   ```bash
   git add docs/prd/<slug>/errors.md
   git commit -m "docs(prd): record <E-nnn>" -m "Refs: <E-nnn>"
   ```

   The commit holds `errors.md` alone. A failed deploy or a stopped build has already recorded its
   entry and committed it: start at step 2 with that entry.

   **A URL given later.** At any step, except with a vendored copy that predates 0.8.12 (above), an
   address for an entry that has none (or a new one) is set, or replaced, its own call:

   ```bash
   <scripts>/prd error url docs/prd/<slug> <E-nnn> '<address>'; echo "prd-error-exit=$?"
   ```

   `-` in place of the address removes it. It prints the line `prd error propose` prints
   (`E-001 proposed code bug`, `E-002 unclassified`). Then, each its own call:

   ```bash
   git add docs/prd/<slug>/errors.md
   git commit -m "docs(prd): set the URL of <E-nnn>" -m "Refs: <E-nnn>"
   ```
2. **Reproduce.** Run the evidence and find the root cause, with `superpowers:systematic-debugging`
   when it is in your skills list. You may read the code and its history (`git log`, `git show`):
   you are not the black-box tester. Nothing is fixed here.
   - **A failing test, or one called flaky.** Run its level's harness command from `testing.md`
     Levels, narrowed to the test's file, as its own call: at most twice, never in a loop (no
     `for`, `while`, `seq`, `--count` or rerun plugin). "At most twice" counts every run of the
     harness in this loop, a whole-suite run included; step 5's red and green runs of the test
     **Code no area covers** writes are not counted. A test that fails twice is failing, not
     flaky. One that passes once and fails once is nondeterministic, which is an error too. The
     runs and their results go in the `--diagnosis` of step 3: the evidence is already written. A
     missing test tool is reported, never a reason to edit untested.
   - **A deploy run.** Run `git rev-parse --git-common-dir` from the repository root as its own
     call and Read `<that dir>/prd-toolkit/deploys/<run id>.jsonl`: the failed step's command,
     exit and output tails. You never rerun a deploy, a runbook command or the deploy script. A
     step with a `start` record and no result (a killed run) ends only through
     `prd_deploy.py recover`, on the user's words, as `running-a-deploy.md` step 2 says.
   - **A stopped build.** Its evidence holds the failing lines; read the round records it names.
   - **A user's report.** Run the command it names once, as its own call, when that command
     changes nothing (never a deploy, a migration or a runbook step).

   An error that does not reproduce still goes to step 3, with a diagnosis that starts
   `not reproduced:` and says what was tried; the entry then waits for the user.
3. **Propose.** Settle the class against the PRD, never against what the code does:

   | Class | When |
   |---|---|
   | code bug | the code does not do what an AC says; or, for code no adopted area covers, the code does not do what its own account says (its documentation, the rule or convention it implements, the test it fails), quoted in the diagnosis in place of an AC; for such code with no account of its own, the report's own words are the account, quoted in the diagnosis, and the owner confirms the class as always |
   | spec gap | the PRD says nothing about what happened: no AC, contract or test case covers it; for behaviour of an adopted area the PRD does not state, never a reason to write a requirement for code no area covers |
   | invalid requirement | the code does what an AC says, and the AC is wrong; or a test case or a contract that contradicts its own AC (the AC stands, the PRD's test case or contract is wrong) |
   | environment | the code and the PRD agree; an environment, its config or the runbook is wrong |
   | standard | the code or the PRD breaks a standard in the PRD's registries |

   When the system does what the PRD says and the PRD is right, keep the class the report claims
   and start the diagnosis with `not a defect:`. Look for a recurrence among every entry, resolved
   ones included:

   ```bash
   <scripts>/prd error list docs/prd/<slug>; echo "prd-error-exit=$?"
   ```

   An entry with the same `Touches:` and the same symptom is its `--recurrence`. Then:

   ```bash
   <scripts>/prd error propose docs/prd/<slug> <E-nnn> --class "<class>" --diagnosis '<the root cause, with the AC quoted>' --touches <IDs> --recurrence <E-mmm>; echo "prd-error-exit=$?"
   ```

   `--touches` takes the blocks the diagnosis names, as `FR-001,FR-002`: an entry recorded before
   diagnosis has no `Touches:` line, and the recurrence check needs it; it replaces a line already
   there, and is left out only when the diagnosis names none. Leave out `--recurrence` when there
   is none. The class is one of five strings, exactly:
   `code bug`, `spec gap`, `invalid requirement`, `environment`, `standard`; `code-bug` is a
   usage error. Then, each its own call:

   ```bash
   git add docs/prd/<slug>/errors.md
   git commit -m "docs(prd): propose <E-nnn>" -m "Refs: <E-nnn>"
   ```

   Then take the entry's areas and URL from its card, its own call:

   ```bash
   <scripts>/prd gates list docs/prd/<slug> --json; echo "prd-gates-exit=$?"
   ```

   The gate `error-class:<E-nnn>` carries `areas` (a list, in the PRD's area order; empty means
   none) and `url` (the entry's, else its first area's, or null). A vendored copy that predates
   0.8.12 prints neither: name the areas of the blocks `Touches:` names instead.

   Show the user: the entry and its class; its areas (`Area: <names>`, or `Area: none`) and its
   URL, as the card shows them; the PRD line quoted verbatim (for a spec gap, the sections
   searched and found silent; for code no adopted area covers, its own account); the evidence; the
   root cause; the entry
   named in `Recurrence of:`, if any; and the route step 5 takes for that class. Ask whether the
   class is right through **The decision inbox** below, with the gate `error-class:<E-nnn>`, or
   headless or in the chat as step 4 says, and end the turn to wait for the reply.
4. **Confirm.** Only a reply given after the proposal counts; the request that started the loop is
   never one. Entering here for a `proposed` entry that has no reply yet, show the proposal as step
   3 says and ask the same way, with the gate `error-class:<E-nnn>`. An outcome from `wait` is the
   reply: the inbox already ran `prd_error.py confirm` with it (and `--class` for a `correct`
   choice) and committed `docs(prd): confirm <E-nnn>`. Run neither again: run `prd_error.py list
   docs/prd/<slug> --open` for the class the entry now holds, and go to step 5 with it. In the chat,
   the reply is what the user wrote after seeing the proposal, in this session or in a later message
   of theirs that names the entry (by number, or as the only `proposed` one), never from an earlier
   message, a summary or your own text. "Just fix it", "it's obviously a bug", "I'm away; handle
   it", "retry it" and "close E-001" are never one. A reply that does not settle the class (a
   question, "maybe", "let me check") is not a confirmation: answer it and wait. Never hand the user
   the `confirm` command to run instead of replying. When the reply settles it:

   ```bash
   <scripts>/prd error confirm docs/prd/<slug> <E-nnn> --reply '<the reply, verbatim>'; echo "prd-error-exit=$?"
   ```

   A reply that names another class adds `--class "<their class>"` to the same call; a reply that
   it is not a defect is confirmed as it stands, and step 5 takes the not-a-defect row. Then,
   each its own call:

   ```bash
   git add docs/prd/<slug>/errors.md
   git commit -m "docs(prd): confirm <E-nnn>" -m "Refs: <E-nnn>"
   ```

   **With no one to ask, commit the proposal and stop.** A headless session, "do not ask me
   questions" or "I'm away; handle it" leaves nobody to reply: confirm nothing, fix nothing.
   Step 3's commit holds the proposal. Report the entry, its class, the quote and the route, and
   end the turn. The entry stays `proposed`, and nothing may cite it from a code commit: the
   commit-msg hook refuses one.
5. **Fix, by class.** Every fix starts from a T-id whose test fails first (for code no adopted area
   covers, from a test committed alone: **Code no area covers** below), and every change and
   commit made for the entry cites it in `Refs:` beside the requirement (`Refs: FR-001, E-001`):
   each `/prd-toolkit:prd-change`'s commits, its approval commit included, and the `--fixes` build's
   removal commits; the build's other commits cite its IDs, as every build commit does.

   | Class | Route |
   |---|---|
   | code bug | as **A code bug** below; as **Code no area covers** below when the faulty code lies outside every adopted Boundary |
   | spec gap | `/prd-toolkit:prd-change` adds the AC and its T-ids (minor; major if existing behaviour changes), then `/prd-toolkit:prd-build <area> <IDs> --fixes <E-nnn>` |
   | invalid requirement | `/prd-toolkit:prd-change` revises the AC and its test cases (major when existing behaviour changes), or, when a test case or a contract contradicts its own AC, revises the test case or contract (a patch when no AC or behaviour changes: see the version rules in `prd-toolkit:changing-prds`), and the block returns to `approved`; then `/prd-toolkit:prd-build <area> <IDs> --fixes <E-nnn>` |
   | environment | `/prd-toolkit:prd-change` on `operations.md` or `contracts/config.yaml` when the PRD holds what is wrong, then a new `/prd-toolkit:prd-deploy` run: never a deploy by hand |
   | standard | the user chooses the side that changes, the registry row or the PRD, through `/prd-toolkit:prd-change`; then `/prd-toolkit:prd-build <area> <IDs> --fixes <E-nnn>` when code must follow |
   | not a defect | nothing changes |

   **An environment.** A new `/prd-toolkit:prd-deploy` run without a PRD change follows only the
   user's word on what they fixed in the environment (a host restarted, a secret set); a request to
   "redeploy" is not that word. The entry still closes only by `resolve --run` and `check`.

   **A code bug.** First a patch `/prd-toolkit:prd-change` (**A regression patch** in
   `prd-toolkit:changing-prds`: its version, §14 row and dry-run record) adds a regression T-id
   under the quoted AC, at the lowest level that reproduces the error (a patch: the AC is
   unchanged, and the T-id tests what it already says). When an existing T-id under that AC
   already fails on the error at that level (step 2 ran it red), it is the regression T-id, and
   the change adds none. Prefer a build-gate level whenever one can reproduce the error, and
   take the lowest level that reproduces it: a deploy-gate regression T-id's test runs only at
   `/prd-toolkit:prd-deploy`, so the fix is proven only there. A non-unit regression
   T-id's case carries `known-failing: <E-nnn>`; a unit one is written failing by the builder in
   the `--fixes` build, as always. Write the case's `symptom:` from the entry's Evidence or
   Diagnosis, never invented; a symptom the entry does not show is a question for the owner. As
   with any change, the block returns to `approved`. When the
   regression T-id's case already carries `known-failing: <E-nnn>` and its block is `approved` (an
   entry from 0.5, or from adoption), the PRD already says it all: skip the patch, and the
   tester-only round below marks and tags its test.
   For a non-unit regression T-id, a tester-only round comes next: dispatch `prd-toolkit:prd-tester`
   alone, as `testing-from-prds/dispatching.md` says (snapshot, dispatch, state check), with
   `Mode: suite` and only the regression T-ids (`Mode: write` for a deploy-gate level, whose red
   proof is the failed run in the evidence). Its test is a strict expected failure cited
   `@prd <T-id> known-failing <E-nnn>`, and its RESULTS line `<T-id>: known-failing <E-nnn>` is the
   red proof; `fail: unexpected pass` means the T-id does not reproduce the error, so it goes back
   to `/prd-toolkit:prd-change`. The failing test is committed, each its own call:

   ```bash
   git add <tester path>
   git commit -m "test(<area>): <T-id> known-failing <E-nnn>" -m "Refs: <IDs>, <E-nnn>"
   ```

   Then `/prd-toolkit:prd-build <area> <IDs> --fixes <E-nnn>`: it un-marks the regression tests, the
   builder fixes the code, the build removes their `known-failing:` lines before its full run (a
   deploy-gate one's once the un-mark is committed, a build-gate one's once it passes), and the
   close takes the block to `verified`; a later `/prd-toolkit:prd-deploy` takes it to `live`.

   **Code no area covers.** When step 2's diagnosis shows the faulty code outside every adopted
   Boundary (no Boundary glob of an `adopted` row of `adoption.md` matches it; a PRD with no
   adoption map covers every path, so its code bugs take **A code bug**), the confirmed `code bug`
   takes this route in place of `/prd-toolkit:prd-change` and `/prd-toolkit:prd-build`. You write
   its test and its fix yourself, because the builder and the tester work from requirement blocks,
   and this code has none. It holds only for faulty code outside every adopted Boundary, only after
   `Confirmed:`, and only with the test first; everything else in the loop stands. Invent no
   requirement and adopt no area for it. The route has four steps, in order:

   1. **The failing test first.** Take the lowest build-gate level that reproduces the error, and
      its `One test` command in `testing.md` Levels. When no build-gate level reproduces it, stop
      and report it: the entry stays `confirmed`. A level with no `One test` command is a stop too:
      report it, and add the column through `/prd-toolkit:prd-change` only (a patch), so the owner
      approves the command before anything runs it; resume here once it is approved. The test is a
      new file, or an existing test that already fails on the error, left exactly as it is in this
      step (no new file and no commit, but still run red as below; only step 2's fix commit changes
      it, and only when the confirmed diagnosis names it as the faulty code). A new file goes where
      `testing.md`'s Layout puts that level's tests (the unit tests, for the unit level), or beside
      the code when it names no such place, even when an adopted Boundary's glob matches that place
      (its commit cites the confirmed entry). It cites no T-id, and you never edit a file that
      cites one: those are the black-box tester's. Run it once,
      as its own Bash call from the repository root, with its output unpiped: the level's `One test`
      command with the test's path or id appended. It must fail on the error; one that passes does
      not reproduce it, so write one that does, never the fix first. Then commit it alone, each its
      own call:

      ```bash
      git add <test path>
      git commit -m "test: failing test for <E-nnn>" -m "Refs: <E-nnn>"
      ```
   2. **The fix,** in its own commit. Before any edit, match every path the fix will change
      against the Boundary globs of the `adopted` rows of `adoption.md`: a path an area covers is
      never yours to edit, and the entry then takes **A code bug** whole, as step 6 says after the
      covered-path refusal. The fix commit changes only the faulty code the confirmed diagnosis
      names, and other code outside every adopted Boundary that the fix needs, named in the report:
      never a file of the PRD folder or of `.prd-toolkit/`, and never a test, with one exception.
      When the diagnosis names a test as the faulty code (the test itself is wrong, the code it
      tests is right and the diagnosis names no other faulty code, and the owner confirmed that
      diagnosis), that test is step 1's existing failing test, it cites no T-id, and the fix commit
      changes it only as the diagnosis says it is wrong, removing, skipping or weakening none of
      its assertions. A new test stays out of the fix commit because a test missing from the
      commit before the fix fails there too, so the replay would call any fix proven. Commit it,
      each its own call:

      ```bash
      git add <fixed paths>
      git commit -m "fix: <what it fixes>" -m "Refs: <E-nnn>"
      git rev-parse HEAD
      ```

      Then run the test once more, the same way, as its own unpiped call: it must pass. A test
      that still fails means another fix commit, never a change to the committed test, except the
      faulty test of step 2's exception, in that further fix commit; `--commit` names the commit
      that turns it green, the SHA `git rev-parse HEAD` printed after it. Before the resolve,
      check the paths of every fix commit made for the entry the same way, not only the one
      `--commit` names: `git show --name-only --format= <sha>`, each its own call. A covered path
      in any of them is the covered case of step 6.
   3. **`resolve --red-run`,** in step 6, with that commit, the test's path or id and the level: it
      replays, and refuses a fix whose test did not fail on the commit before it and pass on it.
   4. **The ledger committed, then `prd error check`,** in step 6, as for every entry.
6. **Close.** For a fix (code bug, spec gap, invalid requirement, standard) by a `--fixes` build,
   the rule is this.
   Resolve only when the `--fixes` build closed with every regression T-id `pass` (its suite
   RESULTS, or the builder's unit result) and the block `verified`; otherwise run
   `/prd-toolkit:prd-build <area> <IDs> --fixes <E-nnn>` again. A build-gate and a unit regression
   T-id are proven by that build. A deploy-gate regression T-id is not run in it (its
   `known-failing:` line came off once the tester's un-mark was committed), so a deploy-gate
   regression T-id's entry is resolved only after a `/prd-toolkit:prd-deploy` run whose `tests` step
   record passed that T-id's level: Read the run's log
   (`<that dir>/prd-toolkit/deploys/<run id>.jsonl`, as in the deploy skill) and check that the
   `tests` step record for that level is `pass` before resolving; with no such run, deploy first.
   The resolution keeps the code-bug form (T-id, level, version, fix commit). A unit regression T-id
   carries no marker to grep, so the build's close is its only proof. A code bug fixed by **Code no
   area covers** (step 5) has no build: it resolves by the red run below once its fix commit is in.
   An environment fix resolves on the new run that finished; not a defect resolves at once.
   Before the resolve, Grep
   `known-failing: <E-nnn>` with the path `docs/prd/<slug>/test-cases/`, and `known-failing <E-nnn>`
   with each test root: a match means the `--fixes` build did not finish, so run it again (its
   un-mark is idempotent). Then resolve by the class's form, one of:

   ```bash
   <scripts>/prd error resolve docs/prd/<slug> <E-nnn> --t <T-id> --version <X.Y.Z> --commit <sha>; echo "prd-error-exit=$?"
   <scripts>/prd error resolve docs/prd/<slug> <E-nnn> --run <run id> --t <T-id> --version <X.Y.Z>; echo "prd-error-exit=$?"
   <scripts>/prd error resolve docs/prd/<slug> <E-nnn> --not-a-defect '<why>'; echo "prd-error-exit=$?"
   <scripts>/prd error resolve docs/prd/<slug> <E-nnn> --commit <sha> --red-run <test id> --level <level>; echo "prd-error-exit=$?"
   ```

   The first is a fix (code bug, spec gap, invalid requirement, standard): the regression T-id,
   the PRD `version:` after the change, and the commit of the `--fixes` build that fixed the code
   (its merge, or the builder's commit). The second is an environment fix: the new deploy run's id,
   with `--t` only when a deploy-gate T-id proves it. The third is not a defect, with the PRD line
   quoted. The fourth is a red run, for **Code no area covers**: step 5's fix commit, the path or
   id its test ran with, and that level. It replays before it writes, and a refusal writes
   nothing: each `refused:` line names its reason; report it, and the entry stays `confirmed`. A
   replay finding, such as
   `refused: <E-nnn>: <test id> passes on <sha>^; <sha> did not turn it green`, means the test did
   not prove the fix: stop there. Never resolve again with another test id, level or commit to
   make it hold.
   `refused: <sha> changes <path>, which area <area> covers; resolve with a regression T-id` means
   a fix commit changed covered code. A covered path in any fix commit made for the entry, or one
   the path check shows before the edit, means the same: the fix needs covered code. An entry
   holds one `Resolution:` line, so the entry is not this route's. Undo every commit made on this
   route for the entry, newest first: each fix commit, and the commit of a new test (an existing
   test was never committed on this route, so nothing of it is undone; before the edit, the test
   commit is the only one). Each is a new commit that cites the entry, never a reset or an amend,
   each its own call:

   ```bash
   git revert --no-commit <sha>
   git commit -m "revert: <sha>, for a fix that needs covered code" -m "Refs: <E-nnn>"
   ```

   Nothing of the route is left for the `--fixes` build to trip on: its regression T-id's test is
   the black-box tester's. Then the entry takes **A code bug** in step 5 whole, under the AC of the
   covered area that states the behaviour, quoted in the regression patch. When no AC of the
   covered area states it, report that and stop: the entry stays `confirmed` with its class (no
   command changes a confirmed class), and the owner decides whether a `/prd-toolkit:prd-change`
   adds that AC. Once that change is approved, **A code bug** goes on from its regression patch.
   `refused: <level> has no One test command; …` is step 5's stop.

   **The replay.** After a `resolve` that names a T-id (`--t`), and before `errors.md` is
   committed, its own call:

   ```bash
   <scripts>/prd error replay docs/prd/<slug> <E-nnn>; echo "prd-error-exit=$?"
   ```

   It runs the test files that cite the T-id on the commit before `<sha>` and on `<sha>`, each in a
   git clone of its own, and writes nothing. Exit 0 with
   `<E-nnn>: <T-id> fails on <sha>^ and passes on <sha>`: the proof holds; go on. Exit 0 with
   `skipped: <E-nnn>: <reason>` (an environment run, a deploy-gate level, a level with no
   `One test` command): nothing could be replayed; go on, and name the skip and its reason in the
   report. Exit 1 prints one finding per line, such as
   `<E-nnn>: <T-id> passes on <sha>^; <sha> did not turn it green` or
   `<E-nnn>: <T-id> fails on <sha>: <file>`: the fix is not proven. Put the ledger back, staged or
   not, its own call, never by an edit:

   ```bash
   git restore --staged --worktree docs/prd/<slug>/errors.md
   ```

   The entry stays `confirmed`: report each finding, and return to step 5's `--fixes` build; never
   resolve again with another T-id, version or commit to make it hold. Exit 2 is a mistyped
   command: fix it and run it again. One that still exits 2 is a tool error: put the ledger back
   the same way, report its message, and the entry stays `confirmed`. A red run needs no replay
   here: its `resolve` made one.

   Then commit `errors.md` alone, each its own call:

   ```bash
   git add docs/prd/<slug>/errors.md
   git commit -m "docs(prd): resolve <E-nnn>" -m "Refs: <E-nnn>"
   ```

   Then, with `<start>` from step 1 or from **Where to enter**:

   ```bash
   <scripts>/prd error check docs/prd/<slug> <start>..HEAD; echo "prd-error-exit=$?"
   ```

   Exit 0 is clean. Exit 1 prints `errors.md: E-<nnn>: <finding>` lines. A finding is fixed and
   the check rerun on the same range; it is never left for the user, with one exception. A finding
   on the `Resolution:` line you wrote (its form, its T-id, its version, its commit) is fixed by an
   Edit of that one line, committed the same way as a new commit (never an amend). The Edit never
   writes a red run and never changes one: only `resolve --red-run` writes it, so a finding on a
   red run is reported. An edited T-id line is replayed, as **The replay** says, before it is
   committed. When that replay prints findings, put the line back the same way and commit nothing:
   report the finding with the commit that resolved the entry. The exception:
   a finding on a commit already made (a code commit that cited the entry before `Confirmed:`, a
   changed `Detected:` line) cannot be fixed by an edit, and history is never rewritten, so report
   it with its commit. Exit 2 is a usage error: fix the command.

   **Report:** the entry and its class; the user's reply, quoted verbatim; each change, build and
   deploy made for it, with their commits (for **Code no area covers**, the test commit, every fix
   commit and their reverts, and the code they changed that the diagnosis does not name); the
   resolution; the replay's result (the proof, or the skip and its reason); and the check's result.

## The decision inbox

The owner answers a gate in a local page, the decision inbox, unless nobody can open it. The step
that asks names the gate; `<gate id>` below is its id. One command per Bash call, with literal
paths, written with the skill's `<scripts>` path, never `${CLAUDE_PLUGIN_ROOT}`.

- **`wait`, first.** Start it with the Bash tool's `run_in_background`, before the owner sees any
  URL, so no answer can come before it is watching:
  `<scripts>/prd gates wait docs/prd/<slug> <gate id>`
- **The URL.** Then start, also with `run_in_background`,
  `<scripts>/prd gates serve docs/prd/<slug> --gate <gate id>`
  and re-read its output until its first line appears:
  - `url=<url>`: give the owner that URL as a clickable link, beside what the step shows in the
    chat.
  - `prd_gates: an inbox is already serving at <url>`: the inbox that
    `<git common dir>/prd-inbox-<slug>.json` names is live and lists this gate too. Give the owner
    `<url>#gate=<gate id>`. Leave that `serve` running: it stands by, and if that inbox stops before
    this gate is answered it takes over at the same URL.
  - `prd_gates: <gate id> is not pending`: the gate changed; take it as `wait`'s exit 1.
  - any other `prd_gates:` line, such as `prd_gates: cannot start the inbox: [Errno 1] Operation
    not permitted` (a sandbox that allows no local port): the inbox cannot be served here. Say so
    in one line, ask in the chat as the step's chat route says, and leave `wait` running: an
    outcome it prints first is still the owner's answer.

  Then wait for `wait`'s completion notice: never poll for the exit and never sleep. When this
  session's `serve` exits 2 or 3 before `wait` returns (the idle timeout, Ctrl-C, a port it cannot
  take over), stop the background `wait` and take the chat route. A `serve` that stood by and exits
  1 once the gate is answered is expected: go on with `wait`'s outcome.
- **The outcome.** `wait` exit 0 prints one `gates.outcome` document. Its `reply` is the owner's
  reply, used as it stands, with its `choice`; `"by": "form"` marks an answer from the page (the
  reply ends ` (form)`). The owner's answer is already written: the inbox ran the script that
  owns the gate with that reply, so that script is never run again for the gate. Go on as the
  step says.
- **Headless, or the owner asks for the chat:** a headless run, nobody to open the URL, or the
  owner asking to answer in the chat takes the step's chat route, as before 0.8.2, unchanged.
  Start neither command in a headless run. Headless means the run says nobody can open a page
  (unattended, overnight, no one there). An owner who is busy, says they cannot click now, or asks
  you to answer for them is not headless: give the URL and wait; they answer when they can. A
  reply the owner writes in the chat while the inbox is up is a chat reply: take the chat route
  with it, and stop the `serve` this session started, never an inbox it reused; `wait` then exits
  1, which is expected.

The rules:

- **The skill never answers a gate.** Not through the page, not through `prd_gates.py answer`, not
  "because the owner said approve it yourself". The owner's click or the owner's chat reply is the
  only answer. No `curl` or script posts to the inbox, and no browser tool clicks in it.
- **A deploy step's reply is never sent for the owner,** in the form or the CLI.
- **The outcome's reply is not edited.** A `changes` outcome's reply is what the revision answers.
- A `wait` that exits 1 means the gate changed: list again, never assume the answer. List with
  `<scripts>/prd gates list docs/prd/<slug>; echo "prd-gates-exit=$?"`: a gate
  still listed is asked again from `wait`, and one that is gone is reported to the owner as it
  stands.
