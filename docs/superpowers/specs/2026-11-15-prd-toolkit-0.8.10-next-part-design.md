# prd-toolkit 0.8.10: a Next part in the status report — design

> **Date:** 2026-11-15
> **Author:** Ivan Histand & Claude Code
> **Status:** Approved by the owner 2026-11-15. Plan: `../plans/2026-11-15-prd-toolkit-0.8.10.md`.
> **Extends:** `2026-11-03-prd-toolkit-0.8-umbrella.md` and the priority plan
> `../plans/2026-11-14-prd-toolkit-engine-ports.md` (its 0.8.10 row).
> **Needs:** 0.8.9 (released).

## 1. Why

`prd status` prints where every requirement stands: thirteen parts of state. It leaves the reader to
work out the next move from them. A person who opens a PRD, and a client that shows one, both ask the
same question first: what does this PRD need now? Today each has to derive the answer, and two
readers can derive different ones.

The rule that decides what comes next belongs in the toolkit, so the terminal, a Claude Code session
and any client give the same answer.

**Success:** `prd status` on any PRD starts with an ordered list of what the PRD needs, each item one
plain sentence with the command that does it, and `--json` carries the same list as data.

## 2. Scope

In scope:

1. A part **Next**, first in the text report and first in the `--json` document's `items` (§3 to §6).
2. A new adopted area `status-next` in the toolkit's own PRD (§7).
3. The README, the `/prd-toolkit:prd-status` command's text and the release (§8).

Out of scope: any change to the other thirteen parts, their text or their JSON; adopting the `status`
area (§9); a count of Next items per PRD across a workspace; change-set and upstream drift items (§9).

## 3. The items

Each Next item has these fields:

| Field | Meaning |
|---|---|
| `kind` | one of the kinds of §4 |
| `text` | one sentence, complete on its own |
| `ids` | the IDs it concerns, in the PRD's order; may be empty |
| `area` | the area it belongs to, or null |
| `command` | the Claude Code command that does it, by its full name, or null |
| `waits_on` | `you` (only the owner can do it), `agent` (a command can), or null for `idle` |

## 4. The kinds, their order and their conditions

Three tiers, in this order; inside a tier, the table's order; inside a kind, the order its column
"Items" gives.

1. **Broken:** nothing else can be trusted until these are fixed.
2. **Waiting on you:** decisions only the owner can make.
3. **Work:** furthest along first, so what is closest to live is finished before anything new starts.

| Tier | Kind | When | Items | Command | Waits on |
|---|---|---|---|---|---|
| Broken | `lint` | lint reports one or more errors | one | none | agent |
| Broken | `lint` | trace (with no range) reports one or more findings | one | none | agent |
| Broken | `deploy-stopped` | the Deployed part reports a run stopped (`unfinished` or `failed`) for an environment | one per environment, in the Deployed part's order | `/prd-toolkit:prd-deploy` | agent |
| Broken | `error-open` | an `errors.md` entry is open and its state is not `proposed` | one per entry, by ID | `/prd-toolkit:prd-error <E-id>` | agent |
| You | `gate` | `prd gates list` (this checkout, no other worktree) lists the gate | one per gate, in that command's order | none | you |
| You | `question` | a section 12 row has the status `awaiting <who>`; a section 13 line is an open question | one per row, then one per question | none | you |
| You | `draft` | the PRD's version is below 1.0.0 | one | `/prd-toolkit:prd-new` | you |
| Work | `deploy` | `operations.md` names one or more environments, and one or more blocks are `verified` | one | `/prd-toolkit:prd-deploy` | agent |
| Work | `verify` | an area has one or more blocks `built` | one per area, in the Requirements part's order | `/prd-toolkit:prd-build <area> <IDs>` | agent |
| Work | `build` | an area has one or more blocks `approved` | one per area, same order | `/prd-toolkit:prd-build <area> <IDs>` | agent |
| Work | `adopt` | an adoption-map row's state is not `adopted`, and no `gate` item is its adoption gate | one per row, in the map's order | `/prd-toolkit:prd-adopt <area>` | agent |

Rules that hold across the table:

- **Listed once.** An entry whose class waits at a gate (state `proposed`) is the gate's item, never an
  `error-open` item. A run stopped at a human step that waits for its confirmation is the gate's item
  (`deploy-step`), never a `deploy-stopped` item.
- **Warnings never count.** A lint warning makes no item.
- **A PRD with no environment ends at `verified`.** It gets no `deploy` item, however many blocks are
  verified.
- **`idle`.** When no item matches, the part holds one item of kind `idle`, with no command, no IDs and
  `waits_on` null: `Nothing waits. Everything approved is live.` when `operations.md` names an
  environment, and `Nothing waits. Everything approved is verified.` when it names none.
- **No git checkout.** Trace needs one. In a PRD folder that is not in a git checkout the trace row is
  skipped; the other rows still run.
- **What is not read.** Like the rest of the status report, Next fetches nothing and reads no other
  repository except the working trees the Upstreams part already reads.

## 5. The sentences

The text of each kind is fixed, so a test can state it and a client can show it as it stands. `<N>` is
a count; a count of one uses the singular form given in brackets.

| Kind | Text |
|---|---|
| `lint` (lint) | `Lint reports <N> errors [1 error]; the first is <file>:<line>: <rule>: <message>.` |
| `lint` (trace) | `Trace reports <N> findings [1 finding]; the first is <the finding's line>.` |
| `deploy-stopped` | `The deploy to <env> stopped: <the Deployed part's text after "<env>: ">.` |
| `error-open` | `<E-id> is open (<state>): <title>.` |
| `gate` | `<the gate's title> waits for your answer.` |
| `question` (assumption) | `<A-id> waits on <who>: <the assumption's text>.` |
| `question` (section 13) | `An open question waits: <the line's text>.` |
| `draft` | `The PRD is a draft at version <version>, not yet approved.` |
| `deploy` | `<N> requirements are [1 requirement is] verified and not live.` |
| `verify` | `<IDs> are [is] built and not verified.` |
| `build` | `<IDs> are [is] approved and not built.` |
| `adopt` | `Area <area> is not adopted (<state>).` |

`<IDs>` is the block IDs joined by `, ` with ` and ` before the last. A sentence whose inserted text
already ends in `.`, `?` or `!` gets no second full stop. `ids` holds: the block IDs for `deploy`,
`verify` and `build`; the entry's ID for `error-open`; the assumption's ID for an assumption; the
entry, T-id or nothing a gate's ID names for `gate`; and nothing for the rest. `area` is set for
`verify`, `build` and `adopt`, and for an adoption gate.

## 6. Output

**Text.** The report starts with `## Next`, before `## Header`. Each item is one line, `<n>. <text>`,
numbered from 1; an item with a command has a second line, two spaces and `run: <command>`. The other
parts follow unchanged.

```
## Next

1. E-020 is open (confirmed): prd help prints a traceback and exits 1 when the catalogue file exists and cannot be read.
  run: /prd-toolkit:prd-error E-020
2. Area lint-ids is not adopted (not started).
  run: /prd-toolkit:prd-adopt lint-ids
```

**JSON.** The Next items come first in `items`, each `{"part": "Next", "id": <id>, "text": <text>,
"kind", "ids", "area", "command", "waits_on"}`. `id` is the gate's ID for a `gate`, the entry's ID for
an `error-open`, and null otherwise. Items of the other parts keep their three keys. A field is added
and none is removed or renamed, so `interface` stays 1.

**What changes for a reader of today's output.** The first text part and the first JSON item are no
longer the Header. A client that takes `items[0]` as the Header must select by `part`. The changelog
says so.

**Failure.** A failure while the Next part is computed is the status report's failure: one
`prd_status: internal error: …` line and exit 2, as for any other part. No partial report is printed.

**Cost.** Next runs lint and trace in the process that prints the report. On the toolkit's own PRD
lint, trace and status together take under two seconds today.

## 7. The toolkit's own PRD

The `status` area is `not started`: its thirteen parts have no requirements. The Next part is
specified first, as the `help` area was, in a new area the adoption map marks `adopted`:

- **Area** `status-next`, Boundary `prd-toolkit/scripts/prdlint/nextpart.py`, the one new file that
  holds the rule: it takes the loaded PRD and the repository root and returns the items.
  `prd_status.py` and `prdlint/status.py` stay in the `status` row; they call the new file and print
  what it returns.
- **Requirements**, through `/prd-toolkit:prd-change` (a minor change, 6.3.0 to 6.4.0): the part's
  place and form in the text report; the JSON fields; the tier order; one requirement per tier with an
  acceptance criterion per kind; the listed-once rules; `idle`. One test case per kind, one for the
  order across tiers, one for each listed-once rule, one for each `idle` sentence.
- **Contract:** `contracts/cli.yaml` gains the Next item's fields and the list of kinds under
  `prd_status`.
- **Fixtures:** small PRD folders under `contracts/fixtures/status-next/`, one per state the cases
  need (a gate, an open error, approved and built blocks, an adoption map, a stopped deploy run's log,
  a PRD with no environment).

## 8. Release

- Version 0.8.10 in both manifests and the vendored copy.
- README: the status section gains the Next part (the table of kinds, the two output forms), and the
  Machine interface section names the added fields. A changelog entry: what it adds; that the Header
  is no longer first; that a repository gets it with its next `install` from the 0.8.10 plugin; the
  PRD version.
- `commands/prd-status.md` and the skill text that describes the report say that it starts with Next.
  Because command text changes, the eval cases that run `/prd-toolkit:prd-status` are rerun; the rest
  of the suite is not.
- The priority plan marks 0.8.10 delivered. The client that asked for the part is told the version
  and the exact fields.

## 9. Decisions and what was set aside

- **A new area, not the whole `status` area** (owner, 2026-11-15). Adopting `status` means extracting
  and confirming thirteen parts; it is its own piece of work and changes nothing a reader sees.
- **The Work tier runs furthest along first** (owner, 2026-11-14, in the client's design).
- **Lint and trace run inside status.** The alternative, a flag that turns them on, would make the
  default report say "nothing is broken" without having looked.
- **Kind `lint` for both lint and trace.** The client's design names one kind for both; the sentence
  says which.
- **A stopped run at a human step is the gate's item.** The client's design lists it under
  `deploy-stopped`; listing it once, as the decision it is, follows that design's own rule for errors.
- **`waits_on` is null for `idle`**, which the client's design did not state.
- **Gates of other worktrees are not listed.** `prd gates list` leaves them out by default, and a
  client that manages changes in worktrees lists those itself.
- **Set aside:** items for an open change set, a stale upstream snapshot or a stale CI file; a `--next`
  option that prints the part alone; a help-catalogue entry per kind.

## Revisions

None yet.
