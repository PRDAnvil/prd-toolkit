# prd-toolkit 0.8.15: a class settled on a run, explained for the owner, and taken back when wrong — design

> **Date:** 2026-11-23
> **Author:** Ivan Histand & Claude Code
> **Status:** Approved by the owner 2026-11-22 (the decisions of §11).
> **Extends:** `2026-11-20-prd-toolkit-0.8.14-error-replay-design.md`, whose ledger, replay and
> fourth resolution form are unchanged.
> **Needs:** 0.8.14 (released) and the toolkit's PRD at 9.9.0. The change of §9 is PRD 10.0.0, FR-251 to
> FR-254.

## 1. Why

**An owner confirmed a class they did not understand.** In a decision-inbox session, an entry
reached the owner as `Proposed class: code bug` with a Diagnosis written from reading the code. No
run had shown the error. The owner pressed Confirm, and a fix route started for an error nobody had
seen happen. Four gaps let that through:

- **Step 2 of the error loop does not have to end in a run.** For a report that names no command,
  or an entry an adoption extract read from the code, the skill accepted a code reading as the
  diagnosis. An entry that arrived `proposed` entered at step 4, where nothing runs.
- **A run that shows the system doing what the PRD says has no class.** Step 3 kept the class the
  report claimed and started the Diagnosis with `not a defect:`, so such an entry still reached the
  card as `code bug`.
- **The proposal is written for someone who has read the code.** The card shows the Diagnosis: file
  paths, line numbers, a root cause. It does not say what was run, what the PRD line says should
  happen, or why this class rather than the nearest one.
- **A confirmation cannot be taken back.** The inbox's Confirm button runs `prd error confirm` at
  once, so "I guess, sure?" typed beside it is written as `Confirmed:`. `prd error check` reports
  any later change to that line, and no command removes it. The skill's own words: no command
  changes a confirmed class.

**The 0.8.14 baseline shows each gap** (`prd-toolkit/evals/baselines/handling-errors.md`, section
"0.8.15 … (RED)"). With the plugin:

- an entry read from the code went to the owner with "I ran nothing else" and the reading restated
  as the root cause, though a run prints the right greeting;
- an unsure Confirm stopped the fix, but "I can't undo that";
- a confirmed entry that HEAD no longer has was resolved by crediting a commit made without the
  entry, and the session then pointed at a fix build for a bug HEAD does not have.

**Success:** no class reaches the owner without a run behind it; a run that matches the PRD is
proposed as `not a defect`; the owner reads what was run and why this class before they answer; a
reply that doubts is answered, never taken as a confirmation; and a confirmation shown wrong by a
later run is taken back with the owner's words kept, before any fix starts.

## 2. Scope

In scope:

1. The skill `handling-errors`: a run ends step 2, three outcomes from it, the explanation, the
   intent question, a doubtful reply, and a second run at the start of step 5 (§3, §5, §6, §8).
2. A sixth class, `not a defect` (§4).
3. An optional `Explanation:` entry line, written by `prd error propose --explanation` (§5).
4. A third answer on the inbox's error-class card, "Ask a question" (§6).
5. `prd error reopen`, and `prd error check` accepting what it writes (§7).
6. The skill `adopting-prds` and its extract prompt: apparent bugs are recorded `unclassified`
   (§10).
7. The toolkit's own PRD, the evals and the release (§9, §12).

Out of scope: running a probe for the session (the skill says how to write one; no command does);
a check that a Diagnosis quotes a run; any change to the replay or the four resolution forms; the
inbox cards of other gates; the `notes_repo.py` eval scaffold, whose adoption entry stays
`code bug` because seven other cases start from it (§12).

## 3. Step 2 ends in a run

A code reading is a hypothesis, not a reproduction. Step 2 ends in a run that shows the failure, or
one that shows the system doing what the PRD says:

- **A failing test:** the test, run twice, as before.
- **A deploy run or a stopped build:** their records, as before.
- **A report that names a command:** that command once, when it changes nothing.
- **A report that names no command, or an entry read from the code:** the test of the AC it
  concerns when one exists. Otherwise a probe in a scratch clone (`mktemp -d`, then
  `git clone -q <repository root> <tmp>/repo`), a script or a `python3 -c` one-off that drives the
  code with the reported input. A probe never writes inside the repository, and never runs a deploy,
  a migration or a runbook step.

Each run's line in the Diagnosis holds the command, the output the quoted PRD line expects and the
output it printed, each in backticks. Then one of three outcomes:

| The run | Next |
|---|---|
| shows the failure | step 3 with it |
| shows the system doing what the quoted PRD line says | step 3 proposes `not a defect` (§4), even when the report insists |
| shows neither (no input to drive, a host out of reach) | `propose --class unclassified --diagnosis 'not reproduced: <each run and what it printed>, and <what would reproduce it>'`, committed as `docs(prd): diagnose <E-nnn>`; ask the reporter for a reproduction and end the turn |

The third outcome opens no gate: an `unclassified` entry is not a proposal. The reporter's answer
re-enters at step 2.

**Where to enter** gains two cases. A `proposed` entry whose Diagnosis quotes no run (an adoption
extract's, or one proposed on a reading), and a `proposed` entry holding a `Reopened:` line, enter
at step 2 rather than step 4, so a run settles the class before the owner sees it again.

## 4. The class `not a defect`

`not a defect` joins `code bug`, `spec gap`, `invalid requirement`, `environment` and `standard`.
It means the PRD is right and the code does what it says. Its Diagnosis starts `not a defect:` and
quotes the run. A confirmation leads to `prd error resolve --not-a-defect`, the resolution form that
already exists. Step 5's route table gains the row "nothing changes"; step 5's second run (§8) has
nothing to run for it.

The class reaches every list of classes: lint's (`error-entries`, lint-registries AC-145.1),
`model.CLASSES`, the help catalogue's `kind.E`, the inbox's class list and the classes of
`contracts/cli.yaml`.

## 5. The explanation and the intent question

**`Explanation:`** is a new optional entry line, written by
`prd error propose … --explanation '<plain words>'`, for an owner who has not read the code. The
skill gives it four parts, in this order:

1. what was run;
2. what it printed;
3. what the quoted PRD line says should happen;
4. why this class and not the nearest other one: a `code bug` means the PRD is right and the code is
   wrong; `invalid requirement` and `spec gap` mean the PRD is wrong or silent; `not a defect` means
   both are right.

It names no file and no line. Those stay in the Diagnosis, which keeps the root cause, the run and
the AC quoted. The skill shows the explanation first in the chat, and the inbox card shows it
first, with the Diagnosis behind a disclosure (`<details>`). An entry without the line shows its
Diagnosis as today. The prose rules read the line, as they read the Diagnosis: it is the session's
text, not the owner's.

**When the class turns on intent.** A run can show the code doing something the quoted line does
not say, with nothing in the PRD to settle which of the two the owner wants. Then the explanation
ends with that question in plain words: "Do you want <the PRD line>, or <what the code does>? The
first makes it a code bug, fixed in the code; the second an invalid requirement, fixed in the PRD."
The proposal still names the class the PRD line gives; the owner's answer confirms or corrects it.

## 6. A doubtful reply

**The skill reads the reply's words, not only its choice.** A reply that asks a question or shows
doubt ("I guess, sure?", "I don't follow", "maybe", "let me check") is not a confirmation. In the
chat the session confirms nothing: it answers in plain words (the explanation again, simpler) and
asks again. From the inbox, two cases:

- **The owner pressed Confirm with doubting words.** The inbox has already written and committed
  `Confirmed:`. The session takes it back with `prd error reopen` (§7), the reason quoting the
  reply, commits `docs(prd): reopen <E-nnn>`, answers the doubt and asks again.
- **The owner used the new third answer, "Ask a question".** It needs words, writes nothing to
  `errors.md` and makes no commit. It logs one answer line with `choice: question`, so
  `prd gates wait` returns that outcome while the gate stays pending. The session answers the
  question and waits again.

A prompt that says the owner is away leaves nobody to answer: the session confirms nothing and
fixes nothing, reports the explanation and the question, and ends its turn.

## 7. `prd error reopen <prd dir> <E-nnn> --reason '<why>'`

**What it writes.** On a `confirmed`, unresolved entry, it replaces the `Confirmed:` line with:

```
Reopened: <date>, "<reason>"; was Confirmed: <date>, "<reply>"
```

The earlier `Confirmed:` date and reply are copied verbatim. Every other line stays as it is. It
prints `E-<nnn> proposed <class>` and exits 0.

- **Why the line is removed, not kept beside.** The trace hook (AC-093.5, AC-093.9) and `check`'s
  code-commit gate treat a `Confirmed:` line as leave to cite the entry from a code commit. Kept, it
  would let a fix in for a class the owner has taken back. Removed, the entry's state is `proposed`
  by the rule that already exists, with no change to the state model.
- **A second reopen.** A later `confirm` writes a fresh `Confirmed:` line, and a further reopen adds
  one more `Reopened:` line. The history reads top to bottom.
- **Refusals** (exit 1, `refused:` lines, nothing written): an entry that is `unclassified`,
  `proposed` or resolved; an empty reason, or one that holds a fence.

**`prd error check`** accepts, in its range, a write that removes a `Confirmed:` line and adds a
`Reopened:` line whose `was Confirmed:` part quotes it verbatim: no `Confirmed: changed` finding for
it. It still reports a removal with no matching `Reopened:` line, and any edit to a `Reopened:` line
already committed.

**Lint.** A `Reopened:` line must have its form (a new finding beside lint-registries FR-146). The
prose rules blank it, as they blank `Confirmed:` (lint-structure AC-026.2), because it holds the
owner's words verbatim.

**The skill runs it in two places only**: a doubtful Confirm (§6) and a second run that no longer
reproduces (§8). "No command changes a confirmed class" becomes "only `prd error reopen` changes a
confirmed class, and only on a reply or a run that shows it wrong".

## 8. Step 5 reproduces again

Step 5 starts by running again what the Diagnosis says reproduced the error, on the current HEAD,
once. When step 2 ran it in the same session and HEAD has not moved, that run stands.

- **It still fails as the Diagnosis says:** the route table, as before.
- **It no longer reproduces, or the run points to another class:** stop, change nothing outside
  `errors.md`, tell the owner in plain words what was run and what it printed, then `prd error
  reopen` with that run as the reason, commit it, and return to step 3.

Never resolve the entry by crediting a commit made without it, and never start a fix route for an
error HEAD does not have. Whether such an entry ends `not a defect` (a commit already fixed it) or
`unclassified` is step 3's to settle from the run, and the owner's to confirm.

## 9. The toolkit's own PRD

One change through `/prd-toolkit:prd-change`, then `/prd-toolkit:prd-build`: PRD 10.0.0, FR-251 to FR-254
from `prd change ids next`. It is major, not minor: lint's class list, and with it the finding of an unknown
class (T-145.1), and the error-class card's choices (T-067.3) change.

- **A new adopted area, `error-reopen`,** Boundary `prd-toolkit/scripts/prdlint/errorreopen.py`,
  written before its code, as `error-replay` was in 0.8.14. Its requirements: `reopen` (§7), what
  `check` accepts of it (§7), `propose --explanation` (§5), and `propose --class unclassified`
  (§3), which 0.8.14 refuses: it writes the Diagnosis and opens no gate. `prd_error.py` and
  `prdlint/errors.py`, in the `errors` area that is not yet adopted, stay thin: they parse the new
  flags and call the new module. `ORDER` gains `Reopened` and `Explanation`.
- **lint-structure AC-026.2:** `Reopened:` joins the lines the prose rules blank.
- **lint-registries:** `not a defect` joins AC-145.1's list; a new AC for the `Reopened:` form.
- **help `kind.E`:** the `Explanation:` and `Reopened:` lines, and the sixth class.
- **inbox-cards:** FR-254, for the error-class card: the explanation first, the Diagnosis behind a
  disclosure, and the question answer (§6). Contract `inbox_answer` and `prd gates answer --choice`
  gain `question`. The code is `prdlint/gates.py` (`_error_class`, `card`, `BUTTONS`,
  `_answer_error_class`, `FLAGS`) and `templates/gates/inbox.html` (`renderErrorClass`).
- **`contracts/cli.yaml`:** the `prd_error` invocation gains `reopen` and `propose --explanation`;
  its class lists gain `not a defect`.

The builder writes unit tests first for `reopen`, for `check` over a reopen, for the sixth class and
for the question answer. The tester writes the integration tests from the T-ids. The build closes
`verified`. The skills' behaviour is covered by the evals, not the PRD: the `skills` area is adopted
last.

## 10. Adoption

The adoption extractor reads the code and never runs it (extract-prompt rule 4), so it cannot
reproduce. An apparent bug it finds is therefore written `Classification: unclassified`, never as a
`code bug`, with a Diagnosis that starts `read from the code, not reproduced:`. Adoption step 3
still asks the owner whether the behaviour is a bug or intended; that answer settles intent, not the
class. The class comes from `/prd-toolkit:prd-error <E-nnn>`, which starts at step 2 and runs it.
The skill `adopting-prds`, its worked example, its Red Flags and `extract-prompt.md` say so.

## 11. Decisions and what was set aside

- **A sixth class** (owner, 2026-11-22), over keeping the reported class with a `not a defect:`
  Diagnosis, which is how a correct system reached the card as `code bug`.
- **A non-reproducing entry is `unclassified`** with a `not reproduced:` Diagnosis (owner), over a
  class of its own: it is not yet a proposal, and it opens no gate.
- **An `Explanation:` line** (owner), over putting plain words in the Diagnosis, which also has to
  hold the file, the line and the run for the fix.
- **`reopen` swaps the line** rather than marking it, because the hook and the code-commit gate key
  on a `Confirmed:` line; and it keeps the reply verbatim, so the record shows what the owner said.
- **A question answer on the card** that writes nothing, over a Confirm that the session later
  undoes: an owner who asks has not confirmed.
- **The skill reads the words of a Confirm**, because the button alone cannot tell "Yes" from
  "I guess, sure?".
- **A small new area**, following `error-replay`, over adopting the whole `errors` area now.
- **Set aside:** a command that runs the reproduction; a lint or `check` finding for a Diagnosis
  that quotes no run (a run's output has no form a check could trust); a reopen of a resolved
  entry (a recurrence is a new entry); a change to `notes_repo.py` (§12).

## 12. Evals, proof and release

- **New cases**, each with a 0.8.14 baseline recorded before the skill text changed:
  - `error-reproduce-before-propose`: an entry an adoption extract proposed from a misleading
    reading; the code is right. The session must run something, quote the run in the Diagnosis and
    not leave the entry a `code bug` or `Confirmed:`.
  - `error-unsure-reply-not-confirmed`: a stand-in owner presses Confirm with "I guess, sure? I
    don't really follow the diagnosis." The entry must not end confirmed, a `Reopened:` line must
    quote the reply, and no change or build may start.
  - `error-reverify-before-fix`: a confirmed entry that an ordinary commit has already fixed. The
    session must run it on HEAD, reopen rather than resolve, keep the earlier confirmation on record
    and say it no longer reproduces.
  - Two scaffold states back them, `read-only-bug` and `confirmed-gone` in
    `evals/scaffolds/error_repo.py`.
- **Rerun** every `error-*`, `handling-errors-*` and `inbox-*` case, with and without the plugin.
  The three new cases need §9's scripts, so their GREEN runs follow the build. Results go in
  `evals/baselines/handling-errors.md` ("Results with the skill") and a 0.8.15 section of
  `evals/BASELINE.md`.
- **The `notes_repo.py` scaffold** still writes its adoption entry as `code bug`. Seven cases
  (adoption, build, tester) start from it, and changing it would move their baselines. The new
  **Where to enter** rule sends such an entry to step 2 all the same.
- **Version 0.8.15:** `plugin.json`, the `marketplace.json` entry and `.prd-toolkit/VERSION`
  together, the vendored copy refreshed, `tests/test_release_0_8_15.py`, and the README sections
  for the sixth class, `--explanation`, `reopen` and the card's question answer.
- **Upgrade note:** re-run `prd hooks install` from the 0.8.15 plugin and commit `.prd-toolkit/`. A
  copy vendored before 0.8.15 has no `prdlint/errorreopen.py`. On such a copy the skill still runs
  step 2, proposes a run that matches the PRD with the reported class and a `not a defect:`
  Diagnosis, keeps the explanation in the chat, stops where a reopen or an `unclassified` record is
  needed, and says to re-vendor. The generated CI file is unchanged, and a PRD needs no
  change.
