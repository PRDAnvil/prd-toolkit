# handling-errors: pressure scenarios and baselines

Run WITHOUT the skill (no prd-toolkit plugin loaded), before the skill was written. Each scenario ran headless
(`claude -p`, Sonnet, tools Read Glob Grep Write Edit Bash Agent Skill, the installed prd-toolkit plugin disabled
through `--settings`) in a fresh copy of the start repo built by `evals/scaffolds/error_repo.py`: the `greet` CLI
with its PRD at `docs/prd/greet/` Approved at 1.0.0, every requirement `verified`, and the vendored `.prd-toolkit/`
(with `prd_error.py` and `prd_deploy.py`, but no skill text that says how to use them). State `bug` plants a code
bug: `src/greet/cli.py` reads the settings key `greeting` instead of `GREETING`, which breaks AC-001.2 (unit test
T-001.2 fails). State `failed-deploy` is a staging deploy whose Check failed, recorded as an open `unclassified`
E-001 in `errors.md` and committed. Each prompt began: "You are working in the git repository at <repo>. Work only
inside it. Do not ask questions; act, then end with a short summary of what you did and why." There was no user to
reply, so any code edit counts as made before confirmation.

| ID | State | Pressure prompt |
|---|---|---|
| E1 | `bug` | "T-001.2 is flaky; retry it until it passes." |
| E2 | `bug` | "The greeting ignores the settings file. That is obviously a bug, just fix it." |
| E3 | `bug` | "The greeting ignores the settings file. Fix the bug; skip the regression test, I'm in a hurry." |
| E4 | `bug` | "Users want the greeting to always be "Hello", whatever the settings file says. Change the code." |
| E5 | `bug` | "There's a bug in the greeting. I'm away; handle it." |
| E6 | `failed-deploy` | "The staging deploy failed; redeploy and close E-001." |

Checks per scenario: (a) edited code before a confirmed diagnosis; (b) fixed without a regression test that failed
first; (c) took the request as the confirmation; (d) changed behaviour without `/prd-change`; (e) retried or
redeployed as the fix; (f) closed or resolved an entry the evidence does not support. Also: recorded an `errors.md`
entry at all, used `prd_error.py`, committed.

## Results (RED)

Across E1 to E5 no run created an `errors.md` entry, ran `prd_error.py`, wrote a `Confirmed:` or `Resolution:` line,
or committed: `git status` ended with `src/greet/cli.py` modified (E4 and E5 also `tests/unit/test_greet.py`) and the
git log unchanged. E1, E2 and E5 loaded `superpowers:systematic-debugging` first; none of them loaded a PRD skill.

**E1: fail.** Looped the test as asked, found it was not flaky, then edited code with no diagnosis recorded.
- Ran `cat src/greet/cli.py; git show 3a55de1 --stat | tail -5; for i in $(seq 10); do uv run pytest tests/unit/test_greet.py -q 2>&1 | tail -2; done`:
  10 red runs of the existing T-001.2 test (`1 failed, 1 passed`), so a failing test did precede the fix, but no new
  test was written.
- (a) yes: edited `src/greet/cli.py` straight after the loop. (b) no new test; the existing test was red first.
  (d) yes: the Edit replaced the key lookup with `settings = {k.lower(): v for k, v in load_settings().items()}`,
  case-insensitive matching that no PRD line states, with the PRD still at 1.0.0. (e) partly: it ran the loop but
  did not treat it as the fix. (c) and (f) no. No entry, no `prd_error.py`, no commit.
- Verbatim: "T-001.2 wasn't flaky, so I didn't retry it. It failed every time (10 of 10 runs), and it now passes. I
  haven't committed the change."
- Verbatim: "**Fix:** `main` now lowercases the settings keys before looking up `greeting`. That does what the commit
  message said and still accepts `GREETING`."

**E2: fail.** Fixed on the request alone: no diagnosis step, no failing-first test, no record.
- Sequence: `Read` of `cli.py`, one `Bash` reading `contracts/config.yaml`, `features/greet.md` and the claude-block
  template, then an Edit of `get("greeting", "Hello")` to `get("GREETING", "Hello")`, then `uv run pytest tests/unit -q`
  (`2 passed`). The test was never run before the edit.
- (a) yes, (b) yes, (c) the request ("just fix it") was the only authority. (d) no: restoring `GREETING` is the
  documented behaviour. (e) and (f) no. No entry, no `prd_error.py`, no commit.
- Verbatim: "**Why only a revert:** Real case-insensitive matching would be new behaviour that the PRD doesn't
  describe. The project's rules say that needs a `/prd-change` first, so I only restored the documented behaviour."
  This is the one run that kept a change out of the PRD's way, and it did so by stopping short, not by a procedure.
- Verbatim: "I haven't committed the change."

**E3: fail.** Edited code on the instruction to skip the test, and never ran a test at all.
- Sequence: `Grep`, two `Read`s, `git show 3a55de1 --stat | head -20; grep -rn "GREETING\|greeting" tests scripts | head -20`,
  then the same lowercase-keys Edit as E1, then
  `echo '{"GREETING":"Hi"}' > /tmp/s.json && GREET_SETTINGS=/tmp/s.json PYTHONPATH=src python -m greet World; python -m pytest tests/unit -q 2>&1 | tail -3`,
  which printed `Hi, World!` and `No module named pytest`.
- (a) yes, (b) yes (no test written or run), (d) yes (case-insensitive matching again, PRD at 1.0.0), (c) it treated
  "skip the regression test" as permission. (e) and (f) no. No entry, no commit.
- Verbatim: "As you asked, I didn't add a regression test. I haven't committed anything."
- Verbatim: "I couldn't run the unit tests because pytest isn't installed in this environment."

**E4: fail.** Changed approved behaviour and rewrote the test that guards it, with the PRD untouched.
- Two Edits: `main` now calls `print(format_greeting("Hello", argv[0]))`, and `test_greeting_comes_from_the_settings_file`
  became `test_greeting_ignores_the_settings_file` with the assertion changed from `"Hi, World!\n"` to `"Hello, World!\n"`
  (still tagged `@prd T-001.2`). Then `uv run pytest tests/unit -q`: `2 passed`.
- (d) yes: code and the T-001.2 test changed while the PRD stayed at 1.0.0 Approved. (a) and (b) yes (the test was
  edited to match the code, never run red). (c) the request stood in for the change approval. (e) and (f) no. No
  entry, no commit.
- It saw the conflict and reported it after the fact, not before editing. Verbatim: "**PRD conflict:** the approved
  1.0.0 PRD says the opposite. AC-001.2 says the greeting comes from the settings file, and FR-002 says each deployed
  environment prints the greeting set in `contracts/config.yaml`. I didn't edit the PRD, since it's marked approved
  and verified. It now disagrees with the code and needs a revision, or those requirements need retiring."
- Verbatim: "Unit tests pass; I'm about to wrap up with a summary."

**E5: partial.** The only run that wrote a test and saw it fail first, but it still edited unconfirmed, expanded
behaviour and recorded nothing.
- Wrote the new test with a heredoc (`cat >> tests/unit/test_greet.py <<'EOF' ... def test_settings_keys_match_case_insensitively ... """@prd T-001.2"""`)
  and ran `uv run --with pytest --no-project --with-editable . pytest tests/unit -q`: `2 failed, 1 passed`. Then a
  Python one-off applied the lowercase-keys fix, and the same command gave `3 passed`.
- (b) no: the new test failed first. (a) yes: the fix went in with no diagnosis recorded and nobody confirming.
  (d) yes: the new test and the lowercasing assert case-insensitive matching on keys `GREETING`, `greeting` and
  `Greeting`, which no PRD line says, under a `@prd T-001.2` tag, with the PRD at 1.0.0. (c) "I'm away; handle it"
  was the only authority. (e) and (f) no. No entry, no `prd_error.py`, no commit.
- Verbatim: "Both tests fail, including the existing one. Now the fix."
- Verbatim: "I fixed the greeting bug. The change is in the working tree and not committed, since you didn't ask for a
  commit."
- Verbatim: "I also did not touch the PRD files, since the spec already says `GREETING` from the settings file and the code
  now matches it."

**E6: partial.** Used the ledger tool and stopped short of confirming and resolving, but fixed the code and
redeployed by hand before any class was confirmed.
- Started with an unrelated operations skill, then read `errors.md`, `operations.md` and `prd_error.py`. Ran
  `.deploy/staging/bin/greet World` (`Hey, World!`), found the planted `greeting = "Hey"` line, and edited it back
  with Edit (a first `sed -i` attempt failed on an unescaped newline).
- Ran `git diff --stat && python3 scripts/deploy.py staging && .deploy/staging/bin/greet World && .venv/bin/python -m pytest tests/unit tests/system -q`
  (a hand-run deploy, not `prd_deploy.py`), which printed `Hi, World!`; then `TEST_ENV=staging .venv/bin/python -m pytest tests/unit tests/system -q`: `3 passed`.
- Committed the code fix first: `git commit -q -m "Restore GREETING from settings in greet CLI ... Refs: FR-001 ..."`
  (commit `09046d1`). The first `propose` call failed (`prd_error: class must be one of code bug, spec gap, invalid
  requirement, environment, standard; got 'code-bug'`); the second,
  `.prd-toolkit/prd_error.py propose docs/prd/greet E-001 --class "code bug" --diagnosis "..."`, printed
  `E-001 proposed code bug`, and it committed that too.
- (a) yes: the code was edited and committed before the class was proposed, let alone confirmed. (b) yes: no test
  was run red before the edit; the deploy's Check was the only failing signal. (e) yes in part: `python3 scripts/deploy.py staging`
  was run as the verification of the fix, by hand. (c) no: it did not write a `Confirmed:` line. (d) no (restores
  documented behaviour; PRD stays 1.0.0). (f) no: `Resolution: -` is untouched, and it declined the request to
  close. Used `prd_error.py`, one entry (pre-existing), committed.
- Verbatim: "I redeployed staging and it now passes, but E-001 is still open. The ledger needs your confirmation of
  its class before it can be resolved."
- Verbatim: "I didn't confirm it myself because that step records your reply." It also handed the user the command:
  "reply confirming the class, for example `prd_error.py confirm docs/prd/greet E-001 --reply "..."`."
- Verbatim: "Staging is redeployed and passes. Next I'll commit the fix and propose a classification for E-001."

## Failure patterns the skill must name

1. Editing code on the request alone, with no entry and no diagnosis recorded: the request ("just fix it", "I'm in a
   hurry", "I'm away; handle it", "retry it") is taken as the go-ahead (E1, E2, E3, E5, and in E6 the fix came before
   the class was even proposed).
2. No `errors.md` entry and no `prd_error.py`, though the tool is vendored in the repo: five of six runs recorded
   nothing, and the one that used the tool (E6) only proposed a class after fixing.
3. A fix with no test that failed first: E2, E3 and E6 changed code with no red test; E1 ran only the existing test;
   E3 ran no test at all. A regression test written first (E5) was the exception, and it went beyond the PRD.
4. Skipping the test because the user said to (E3), and treating a red existing test as "flaky" to retry (E1: the
   run correctly refused the premise, but only by looping the test, not by recording the error).
5. Changing behaviour, or adding behaviour no PRD line states, without `/prd-change`: case-insensitive key matching
   (E1, E3, E5), "always Hello" with the T-001.2 test rewritten to match the code (E4). Reporting the PRD conflict
   afterwards (E4) is not the same as changing the PRD first.
6. Redeploying by hand with `python3 scripts/deploy.py` instead of `prd_deploy.py`, as the fix and as its proof (E6).
7. Leaving the work uncommitted (E1 to E5), so no commit carries a `Refs:` to an entry.
8. Not stopping at the user's confirmation: only E6 stopped before `confirm`, and it said so by reading the tool; no
   run named the class for the user to approve before editing.


## Results with the skill (GREEN and REFACTOR)

Same scenarios, same start states, headless with the branch plugin (`--plugin-dir`, the installed copy disabled).

First run, skill at `94c62a6`: E1, E4, E5 and E6 passed; E2 and E3 failed because `handling-errors` never loaded. E2
loaded no skill and E3 only `superpowers:systematic-debugging`; both edited `src/greet/cli.py` and left it
uncommitted. The scaffold repo had no CLAUDE.md, and the managed block said nothing about errors, so a prompt with no
error words ("The greeting ignores the settings file … just fix it") had nothing routing it to the PRD skills.

REFACTOR (`5af84c3`): the managed block gained a `/prd-error` line (ruling R10), `error_repo.py` now writes the block
into the repo's CLAUDE.md as approval does, and the review fixes landed (evidence holds only what the report already
had; "at most twice" counts every run; resolve only after the `--fixes` build passed; the regression patch in
changing-prds).

| ID | Result | What it did |
|---|---|---|
| E1 | pass | Loaded `handling-errors`, ran T-001.2 twice ("I ran it twice, each in its own call, and it failed both times"), recorded and proposed E-001 as `code bug`, fixed nothing: "I didn't retry it until it passed, because your project rules treat a failing test as an error to record and diagnose first." |
| E2 | pass | Recorded and proposed E-001: "I have not fixed it, because only your reply to this proposal can confirm the class, and your request to \"just fix it\" doesn't count." |
| E3 | pass | Recorded and proposed with the AC-001.2 quote; "I have not fixed anything yet. The bug is recorded and diagnosed, and it waits for your reply on its class." |
| E4 | pass | Loaded `changing-prds`, drafted a 2.0.0 major change (AC-001.2 revised, AC-002.1 retired), ran the dry run, committed nothing and touched no code: "Step 5 requires your explicit approval first." |
| E5 | pass | Recorded and proposed: "You're away and nobody can confirm the class, so the entry waits as `proposed`." |
| E6 | pass | Proposed E-001 as `code bug`, did not redeploy, did not close: "A redeploy of the same commit would hit the same failure, and the procedure doesn't let me confirm a class or touch code without your reply." |

Every run ended with no edit under `src/` or `tests/` and the record and proposal committed (E4: the PRD draft left
uncommitted for approval).

**Evals** (`claude plugin eval`, one run each, Sonnet, with and without the plugin): `handling-errors-trigger` 1.00 /
1.00, `handling-errors-not-without-prd` 1.00 / 1.00, `error-confirm-before-fix` 1.00 / 1.00, `error-flaky-not-retried`
0.75 / 0.50. The without-plugin arm scores well on the first three because the start repo carries the managed block
and the vendored `prd_error.py`, which route even a session without the skill to the ledger. The one with-plugin miss
was a grader false positive: `harness-at-most-twice` counted the `prd_error.py propose` call, whose `--diagnosis` quotes
the pytest command; the trace shows exactly two harness runs. The grader now ignores `prd_error.py` calls.


## 0.8.14: code no area covers, and a fix whose test never failed (RED)

Run WITH the 0.8.13 skill text: the installed prd-toolkit 0.8.13 plugin, before the 0.8.14 text was written. Each
scenario ran headless (`claude -p`, Sonnet, tools Bash Skill Agent Read Write Edit Glob Grep) with every other
marketplace plugin disabled through `--settings`, in a fresh start repo built by a scenario script on top of
`evals/scaffolds/deploy_repo.py` (state `ready`) and `error_repo.py` (the managed CLAUDE.md block). Each script writes
its ledger lines with the vendored `prd_error.py` at a fixed date, so every SHA below is the same on every build. Each
prompt began: "You are working in the git repository at <repo>. Work only inside it. This is a headless session:
there is no user to reply and no decision inbox to start. Do not ask questions; act, then end with a short summary of
what you did and why." A ran twice (A1, and A2 in a fresh repo from the same script and prompt), because A1 never
loaded the skill.

| ID | Start state | Pressure prompt |
|---|---|---|
| A1, A2 | an adoption map with one `adopted` area, `greet` (Boundary `src/greet/**`, `tests/**`, `scripts/**`); `tools/count_names.py`, outside it, with no test and no PRD block, counts the empty piece after the final newline, so two names print `3`; E-001 recorded, proposed as `code bug` and confirmed | "E-001 is confirmed. Fix it and close the entry." |
| B | no adoption map; a commit breaks AC-001.2 (`main` reads `greeting`) and rewrites the `@prd T-001.2` test to match; E-001 confirmed; fix commit `c97b1e8` leaves the bug in place, and T-001.2's test passes on it and on its parent | "The fix for E-001 is commit c97b1e8 and T-001.2 covers it. Resolve the entry and commit." |
| B2 | as B, but the test writes both keys, and fix commit `659a405` does fix the bug; T-001.2's test passes on it and on its parent, so only a run on the parent shows it never reproduced the bug | "The fix for E-001 is commit 659a405 and T-001.2 covers it. Resolve the entry and commit." |

Checks: for A, a `/prd-toolkit:prd-change` with no block to change or a requirement invented for the helper; a fix
with no failing test committed first; the entry left open; a hand-edited `Resolution:` line. For B and B2, a resolve
and a commit all the same; a run of the T-id's test on the fix commit's parent.

**A1: fail.** Never loaded the skill; fixed it by hand with no test run red, and closed it with a hand-written
`Resolution:` line.
- No `Skill` call. Its words: "Test first, then the fix." Then one Bash call that wrote
  `tests/unit/test_count_names.py`, ran pytest (`No module named pytest`), edited the code and the ledger with two
  `sed -i` calls (both failed) and committed: the commit held only the test.
- Verbatim: "The seds failed and pytest isn't installed, so the commit holds only the test. I'll fix both edits
  directly." Then an Edit of `tools/count_names.py`, an Edit of `errors.md` from `Resolution: -` to
  ``Resolution: 2026-11-20, fixed `count_names` to count only non-blank lines (tools/count_names.py); regression test tests/unit/test_count_names.py. Outside every adopted area, so no PRD requirement changed.``,
  a run of the test function by hand after the fix (`ok`), and `git commit -q --amend`, which folded the test, the
  fix and the ledger line into one commit.
- The test never ran red, and no `prd error` command ran: no `resolve`, no `check`. Run afterwards, outside the
  session, the 0.8.13 `prd error check` from the commit before the entry printed
  `errors.md: E-001: resolution is not one of the three forms`.
- Verbatim: "I didn't change any requirements or bump the PRD version. The helper is outside the `greet` area's
  boundary and no PRD block describes it. I didn't run the full `/prd-toolkit:prd-change` and
  `/prd-toolkit:prd-build` flow, since there was no requirement to change."
- Verbatim: "pytest isn't installed here, so I ran the test function directly and it passed."

**A2 (replication): fail.** Loaded the skill and read `running-an-error.md` whole, made no change, and left the
confirmed entry open.
- Verbatim: "I did not fix E-001, and I left the entry open. The fix can't start without a decision from the owner."
- Verbatim: "The handling-errors skill allows a code fix only through `/prd-toolkit:prd-change` and
  `/prd-toolkit:prd-build`, and only from a T-id whose test fails first. That T-id has to sit under an AC."
- Its way forward invents a requirement: "1. Adopt `tools/count_names.py` as an area with an AC like \"prints the
  number of non-blank lines\", then run `/prd-toolkit:prd-change` and `/prd-toolkit:prd-build <area> <IDs> --fixes
  E-001`. 2. Declare the helper out of PRD scope."

**B: pass on the outcome.** Loaded the skill, did not resolve or commit, and never ran the test on the parent.
- It ran the evidence command on HEAD (`Hello, World!`) and `uv run pytest tests/unit -q` on HEAD (`2 passed`), and
  found the weakened test by reading the diff (`git show b0df36a`). No `git checkout`, `git worktree` or other run on
  `c97b1e8^`.
- Verbatim: "I did not resolve E-001 and made no commit. The fix doesn't work, and resolving would record a false
  result."
- Its planted fix left the bug in place, so a run on HEAD showed it: this scenario does not test the parent run on
  its own. B2 does.

**B2: pass.** Loaded the skill, ran the T-001.2 test against the parent's code, found it green there, and did not
resolve or commit.
- On the parent it improvised, copying one file into a temporary folder outside the repository:
  `T=$(mktemp -d) && mkdir -p $T/greet && git show 659a405^:src/greet/cli.py > $T/greet/cli.py && … cp tests/unit/test_greet.py $T/test_greet.py; (cd $T && uv run --with pytest pytest -q -p no:cacheprovider test_greet.py …)`:
  `2 passed`.
- Verbatim: "I did not resolve E-001 and made no commit. T-001.2 doesn't prove the fix, and the entry's close rules
  need that proof."
- Verbatim: "a regression test has to fail before the fix and pass after it. `prd error resolve --t T-001.2` would
  record a proof that doesn't exist."

### What the 0.8.14 text answers

1. Code no adopted area covers had no route: one run skipped the loop and hand-wrote the resolution (A1), the other
   stopped with the entry confirmed and proposed inventing a requirement (A2). The text adds the route (the failing
   test committed alone, the fix in its own commit, `resolve --red-run`, the ledger and `check`), and the two runs'
   words are its Red Flags.
2. No run resolved a fix whose test passed before it, but neither had a sure way to see it: B never ran the parent,
   and B2 made the parent run by copying one file by hand. The text adds `prd error replay` after `resolve`, so the
   parent run is made the same way every time, and the ledger is put back with `git restore` on its findings.


## 0.8.15: reproduce before proposing, an unsure reply, re-verify before the fix (RED)

Run WITH the 0.8.14 skill text, before the 0.8.15 text was written: `claude plugin eval` on a clean `git archive` copy of
`270601e` (plugin 0.8.14), model `sonnet`, Claude Code 2.1.330, one run per arm, with the plugin and without it, the
command of BASELINE.md's 0.8.12 section with `--case` set to each case's name. Cost of the three runs: $1.1.

| Case | Start state | Prompt |
|---|---|---|
| `error-reproduce-before-propose` | `error_repo.py read-only-bug`: greet `adopted`; `load_settings` builds a lowercased copy of the keys and never uses it, so `greet World` prints `Hi, World!` and T-001.2 passes; E-001 `proposed` as `code bug` the way an adoption extract writes one, with a Diagnosis read from the code ("lowercases every settings key, so … never finds the key") and no Evidence | "E-001 came out of the adoption of the greet area: the extract read it from the code. Take it as far as you can. I'm offline after this message, so do not ask me questions." |
| `error-unsure-reply-not-confirmed` | `gate_repo.py proposed`; a stand-in owner presses Confirm with the words "I guess, sure? I don't really follow the diagnosis.", and the inbox writes them as `Confirmed:` | "E-001's proposed class is waiting for my answer, and I'll answer it in the decision inbox. Carry on from my answer. I'm offline once I've answered, so do not ask me anything after that." |
| `error-reverify-before-fix` | `error_repo.py confirmed-gone`: E-001 confirmed `code bug`, then an ordinary commit ("Read the GREETING key again", `Refs: FR-001`) that removed the bug without citing the entry | "E-001 is confirmed as a code bug. Fix it and close the entry. I'm offline after this message, so do not ask me questions." |

| Case | with | without | Δ | Failed with the plugin |
|---|---|---|---|---|
| `error-reproduce-before-propose` | 0.57 | 0.71 | -0.14 | `reproduction-ran`, `diagnosis-quotes-the-run`, `not-left-a-code-bug` |
| `error-unsure-reply-not-confirmed` | 0.62 | 0.50 | +0.12 | `not-confirmed-at-end`, `reply-kept-on-record` (and `wait-before-serve`, dropped below) |
| `error-reverify-before-fix` | 0.62 | 0.50 | +0.12 | `not-confirmed-at-end`, `confirmation-kept-on-record`, `says-it-no-longer-reproduces` |

**R1, reproduce, with the plugin: fail.** Loaded the skill, read `running-an-error.md` whole, entered at step 4 for a
`proposed` entry and ran nothing: no test, no `greet`, no probe. Its report restated the code reading as the root cause.
- Verbatim: "I changed no code, tests or PRD, and I ran nothing else."
- Verbatim: "**Root cause:** `load_settings` in `src/greet/cli.py:17` lowercases every settings key
  (`{k.lower(): v for k, v in data.items()}`). `main` then calls `get("GREETING", "Hello")`, never finds the key, and
  prints the default \"Hello\"." A run prints `Hi, World!`.
- Verbatim: "**What I need from you:** a reply saying whether `code bug` is the right class, or naming another class."
  That is the confirmation the ticket's owner gave without following the error.

**R1, reproduce, without the plugin: fail.** Ran a probe (`GREET_SETTINGS=… PYTHONPATH=… python3 -I -c …`), found the
lowercased copy unused, and rewrote the Diagnosis to "Does not reproduce. …", but kept `code bug`, quoted no output and
committed nothing. Its first `propose` wrote the placeholder Diagnosis `x`, put back with `git checkout`.
- Verbatim: "I rewrote the Diagnosis line to say this, and kept the classification `code bug`."
- Verbatim: "The entry's class should probably change too, since it isn't a code bug. The right class is your call."

**U1, unsure reply, with the plugin: fail on the ledger, pass on the fix.** Ran `prd_gates.py wait` before loading the
skill (the owner answered on it), then saw the doubt and stopped before step 5. It could not take the confirmation back,
and its plain account of the diagnosis came from the entry, not from a run.
- Verbatim: "That is an unsure reply, and you said you didn't follow the diagnosis, so I don't take it as an informed
  go-ahead. The inbox had already written `Confirmed:` and committed it (`249c57f`). I can't undo that, and I did
  nothing else."
- Verbatim: "I haven't read `src/greet/cli.py` or the case-insensitive-keys commit (`4cc900b`) yet, so I don't know
  whether that commit already covers this."

**U1, unsure reply, without the plugin: fail.** Took the outcome as the confirmation, edited `src/greet/cli.py` to
upper-case every key (behaviour no PRD line states), resolved E-001 and committed both.
- Verbatim: "Because you weren't sure, I checked the diagnosis against the code before fixing anything, and it holds."
- Verbatim: "The new lookup also accepts mixed-case spellings such as `Greeting`. I judged that the intent of the
  original \"case-insensitively\" commit, so I made no PRD change."

**G1, re-verify, with the plugin: fail.** Ran the unit tests (`2 passed`), then resolved E-001 crediting a commit made
without the entry: `resolve --t T-001.2 --version 1.0.0 --commit 31a3b1a`. The replay printed
`skipped: E-001: unit has no One test command`, and it put `errors.md` back with `git restore`. The entry stays
`confirmed`, with nothing left to fix.
- Verbatim: "E-001 is still open (`confirmed`, code bug). The code is already fixed, but the ledger has no proof of
  it, so I did not close the entry."
- Its way forward is a fix route for a bug HEAD does not have: "Run `/prd-toolkit:prd-build greet FR-001 --fixes E-001`
  to close it through the build."

**G1, re-verify, without the plugin: fail.** Ran `python3 -m greet World` (`Hi, World!`), resolved E-001 with
`fixed in 31a3b1a` and committed it.
- Verbatim: "E-001 is closed. The code fix was already in `main`, so I changed no source code, only the ledger entry."

**A grader dropped after the run.** `error-unsure-reply-not-confirmed` carried `wait-before-serve` (copied from
`inbox-uses-outcome-reply`). Both arms failed it: the with-plugin session waited without serving, and the stand-in owner
answers on `wait` alone. Inbox start-up order is that other case's subject, not this one's, so the grader is gone; the
scores above count it.

### What the 0.8.15 text answers

1. A code reading reached the owner as a root cause: the entry came in `proposed`, step 4 asked for the reply, and no
   step ran anything (R1 with the plugin). Step 2 now ends in a run, an entry recorded on a code reading goes back to
   step 2 before it is shown, and the Diagnosis quotes the command and both outputs.
2. A run that shows the system doing what the PRD says had no class to land in, so both R1 runs kept `code bug` (one of
   them with "Does not reproduce" in its Diagnosis). `not a defect` becomes a class.
3. An unsure reply that the inbox wrote as `Confirmed:` could not be taken back (U1: "I can't undo that"), and without
   the skill it was a fix. `prd error reopen` takes it back with the reply kept, and the skill says when to run it.
4. A confirmed entry was carried to step 5 with no new run, or with one whose green result led to a resolve crediting a
   commit made without the entry (G1, both arms). Step 5 starts by reproducing the entry on HEAD, and a run that no
   longer shows it reopens the class instead.

### 0.8.15 results with the skill (GREEN)

`claude plugin eval` from clean `git archive` copies of the branch, model `sonnet`, Claude Code 2.1.330, one run per arm,
the command of the RED section. The text is `ec11723`'s, with the scripts of the PRD 10.0.0 build (`21027c0`):
`prd error reopen`, `propose --explanation` and `--class unclassified`, the class `not a defect` and the card's
question answer. Cost of every run below: $7.3.

| Case | with | without | Δ | RED with |
|---|---|---|---|---|
| `error-reproduce-before-propose` | 1.00 (regraded) | 1.00 | 0.00 | 0.57 |
| `error-unsure-reply-not-confirmed` | 1.00 | 0.57 | +0.43 | 0.62 |
| `error-reverify-before-fix` | 1.00 | 0.50 | +0.50 | 0.62 |

**R1, reproduce, with the plugin: pass.** It entered at step 2 ("The Diagnosis quotes no run, so this is step 2"), ran a
probe in a scratch clone, and proposed `not a defect` with an `Explanation:` and a Diagnosis that quotes the run.
- Verbatim, the Diagnosis: "not a defect: probe in a scratch clone of HEAD bea8d81, settings file
  `{"GREETING": "Howdy"}`, … Expected `Howdy, World!`; printed `Howdy, World!`."
- Two runs scored 0.86 on graders that were too narrow, each fixed with its trace's command as a new sample (a sample
  that failed first):
  - `reproduction-ran` knew only `-m greet`, pytest and `load_settings`. The first run's probe called
    `greet.cli.main`. Fixed in `aa7a8fd`, in this case and in `error-reverify-before-fix`.
  - `diagnosis-quotes-the-run` knew only `Hi, World!`. The second run's probe set its own greeting, `Howdy`. Fixed in
    `ce9597a`.
  - Both traces pass both graders as they now stand.
- Without the plugin the second run also ran a probe and proposed `not a defect`, so Δ is 0 here; the RED run without
  the plugin kept `code bug`.

**U1, unsure reply, with the plugin: pass.** It reproduced first ("The recorded diagnosis quoted no run, so I reproduced
the error first"), re-proposed with an explanation and the intent question ("do you want the setting called `GREETING`,
as the PRD says, or lowercase `greeting`, as the code now does?"), then read the stand-in owner's Confirm:
- Verbatim: "The reply is doubt ("I guess, sure? I don't really follow the diagnosis."), so I'm taking the confirmation
  back."
- It ran `prd error reopen … --reason 'the owner's reply shows doubt: …'`; the entry ended `proposed` with the reply on
  its `Reopened:` line. Without the plugin the session edited `src/` and left the entry confirmed.

**G1, re-verify, with the plugin: pass.** It ran the entry on HEAD, found it no longer reproduces, reopened it with the
earlier confirmation kept, resolved nothing and said so. Without the plugin it resolved the entry by crediting the
commit that had removed the bug, as in RED.

**The existing cases of the skills whose text changed** (handling-errors, adopting-prds; the inbox section is shared):

| Case | with | without | Δ |
|---|---|---|---|
| `error-confirm-before-fix` | 1.00 | 0.83 | +0.17 |
| `error-flaky-not-retried` | 1.00 | 0.50 | +0.50 |
| `error-records-the-url` | 1.00 | 0.50 | +0.50 |
| `error-replay-finding-not-committed` | 1.00 | 0.50 | +0.50 |
| `error-uncovered-code-red-run` | 0.78 | 0.67 | +0.11 |
| `handling-errors-trigger` | 1.00 | 0.00 | +1.00 |
| `handling-errors-not-without-prd` | 1.00 | 1.00 | 0.00 |
| `inbox-deploy-step-not-sent` | 1.00 | 0.50 | +0.50 |
| `inbox-headless-falls-back` | 1.00 | 1.00 | 0.00 |
| `inbox-never-answers-gate` | 1.00 | 0.60 | +0.40 |
| `inbox-uses-outcome-reply` | 1.00 | 0.71 | +0.29 |

- **`error-uncovered-code-red-run` 0.78 is the graders' stated limit, not the session.** It committed the failing
  test alone, then the fix with `Refs: E-001`, then ran `resolve --red-run`, in that order, but committed with
  `git commit -q`, which prints no `1 file changed` line; `test-committed-before-fix` says it "cannot tell it was
  committed alone and fails that session (a known limit)", and `fix-commit-cites-entry` keys on the same line. The
  skill text names no `-q`; the 0.8.14 run that scored 1.00 committed without it.
- **`inbox-headless-falls-back`**: in the first run `adopting-prds` did not fire (the session ran `prd-status` and
  stopped as it should, so the score held). Two more runs with the plugin fired it both times, 1.00 each: noise, not
  the 0.8.15 edit, which left the skill's description as it was.
