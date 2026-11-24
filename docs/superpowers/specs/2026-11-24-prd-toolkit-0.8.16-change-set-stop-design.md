# prd-toolkit 0.8.16: a change set stopped before its first approval

## Problem

A session that meets a blocker in a member's step 2 (its lint or dry run) records it with
`prd_links.py changeset stop`. After the blocker is fixed and the owner replies to the PRD diffs:

- `changeset approve <record> --reply '<reply>'` refuses with `<CS> is stopped: …, not proposed; a
  later approval is an --amendment`;
- `changeset approve … --amendment` refuses with `<CS> has no approval to amend`.

The only way on is `changeset abandon` and a new change set: new branches, a new record and a second
reply for the same diffs (E-081). And `changeset set <prd> state=…` checks the Status text
`proposed`, not the Approval line, so once Status reads `stopped: …` a row can reach `approved` or
`built` with no approval at all (E-082).

## Decision

`approve` takes the first approval of a stopped record. No new `resume` action: it would take a
second command for the same reply, and a new subcommand reaches the adopted `help` area.

- `approve`, without `--amendment`, on a record whose Status is `stopped: <prd>: …`, that has no
  Approval line and whose every row is `proposed`: writes the Approval line, moves every row and
  Status to `approved`, and appends the Log line `<date> <prd> stop cleared by the first approval`.
- The same record with a row past `proposed` (possible only through E-082) is refused:
  `<CS> is <status> with no approval, and <prd> is <state>; abandon it and start a new change set`.
- A stopped record with an Approval line keeps its route: `--amendment`, or the next `set` of a State.
- `set … state=…` is refused, `<CS> is not approved yet`, whenever the record has no Approval line,
  whatever its Status. Branch, Version and IDs can still be set, as step 2 needs.

The one-approval rule is unchanged: a stop never counts as an approval, and no row leaves `proposed`
without an Approval line.

## The skill

`coordinating-prds/running-a-change-set.md`:

- Step 2 records its own blocker with `changeset stop`, and step 3's one approval clears it.
- Step 5's `--amendment` is only for a record that has an Approval line.
- Where to enter sends `stopped: …` with no Approval line to step 2 (that row, once the blocker is
  fixed) or step 3 (every Version has `→`), and one with an Approval line to step 5 as before.

## Proof

- E-081 and E-082 are in `prdlint/changeset.py`, area `links`, not adopted: each closes by a red run
  (`tests/test_changeset.py`: a stop then the first approval; a stop then `set state=` refused; the
  refused record past `proposed`).
- Eval `change-set-stopped-before-approval` (scaffold state `cs-stopped`): RED 0.33 on 0.8.15, GREEN
  1.00, and a control with the fixed code and the 0.8.15 text at 1.00, so the case measures the code
  fix. It ran outside `claude plugin eval`, whose sandbox stops every `link_repo.py` scaffold
  (evals/BASELINE.md).
