# Status: the Next part

`prd status` starts with a part, Next: what the PRD needs now, in order, each item one sentence with the
command that does it, and the same list as data in `--json`. The rule lives in
`prd-toolkit/scripts/prdlint/nextpart.py`; the status report prints what it returns. The other thirteen parts
belong to the area `status`, which is not adopted.

### UJ-03 A person or a program asks what the PRD needs next
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:1 @3fc3086
Flow: 1. run `prd status` and read its first part, Next
      → 2. run the command the first item names, or answer the decision it names
      → 3. a program runs `prd status --json` and reads the items whose `part` is `Next`
Traces: FR-040, FR-041, FR-042, FR-043, FR-044, FR-045, FR-046, FR-047

### FR-040 The Next part comes first in the text report
Status: verified
Source: prd-toolkit/scripts/prd_status.py:57 @3fc3086
Acceptance (EARS):
- AC-040.1 When run on a PRD folder without `--json`, the status command shall print the line `## Next`
  as its first line, then one empty line, then for each Next item, in the order FR-042 gives and
  numbered from 1, the line `<n>. <text>` and, when the item has a command, the line `  run: <command>`
  (two spaces, `run: ` and the command); then one empty line, and then the line `## Header`.
- AC-040.2 When run without `--json`, the status command shall print after the Next part and its empty
  line the thirteen parts it prints without a Next part, `## Header` to `## Matrix`, in that order,
  each part's heading and lines unchanged byte for byte.
- AC-040.3 If computing the Next part raises an error, the status command shall fail as it does when any
  other part fails: it shall print the one stderr line
  `prd_status: internal error: <exception type>: <message>`, print no part of the report and exit 2;
  with `--json`, its stdout shall be only the one line
  `{"interface": 1, "kind": "status", "error": "internal error: <exception type>: <message>"}`.
Errors: -
Edge cases: the Next part is never empty, since with no other item it holds the `idle` item (FR-046) → AC-040.1; an item with no command prints one line → AC-040.1; Next fetches nothing and reads no repository other than the working trees the Upstreams part already reads; lint and trace run in the process that prints the report; the report is written as UTF-8 whatever the locale, as the rest of the status report is (a title may hold text outside ASCII)
Tests: T-040.1 [integration], T-040.2 [integration], T-040.3 [unit]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status

### FR-041 The Next items in the JSON document
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:21 @3fc3086
Acceptance (EARS):
- AC-041.1 When run with `--json`, the status command shall put the Next items first in the document's
  `items`, in the order FR-042 gives, each an object with the keys `part`, `id`, `text`, `kind`, `ids`,
  `area`, `command` and `waits_on`, in that order, where `part` is `Next`; `text` is the item's
  sentence as the text report prints it after `<n>. `; `kind` is its kind; `ids` is the list of IDs
  its kind's criterion names, empty when it names none; `area` is the area its kind's criterion names,
  or null; `command` is its command, or null; `waits_on` is `you`, `agent` or null, as its kind's
  criterion gives; and `id` is the gate's ID for a `gate` item, the entry's ID for an `error-open`
  item, and null for every other kind.
- AC-041.2 When run with `--json`, the status command shall print every item after the Next items with
  exactly the keys `part`, `id` and `text`, in the order and with the values it has without a Next
  part, and shall keep the document's keys `interface`, `kind`, `prd`, `version` and `items`, in that
  order, `interface` being 1 and `kind` being `status`.
Errors: -
Edge cases: the first item is no longer the Header, so a reader selects the Header by `part` → AC-041.1; `interface` stays 1, since a field is added and none is removed or renamed → AC-041.2
Tests: T-041.1 [integration], T-041.2 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status; `prdlint/interface.py`

### FR-042 The order of the items, each listed once
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:202 @3fc3086
Acceptance (EARS):
- AC-042.1 The status command shall order the Next items in three tiers, Broken (FR-043), then Waiting
  on you (FR-044), then Work (FR-045); inside the tiers by kind, in this order: `lint` (the lint item,
  then the trace item), `deploy-stopped`, `error-open`, `gate`, `question`, `draft`, `deploy`,
  `verify`, `build`, `adopt`; inside a kind, in the order its criterion gives; and when no item of
  these kinds exists, the part shall hold the one `idle` item of FR-046 alone.
- AC-042.2 While an `errors.md` entry is open in the state `proposed`, the status command shall list it
  only as the `gate` item of its gate `error-class:<E-id>` (AC-044.1), and never as an `error-open`
  item.
- AC-042.3 While a deploy run of the PRD is stopped at a human step that has no confirmation, so that
  `prd gates list` lists its gate `deploy-step:<run id>:<N>`, the status command shall list the run
  only as that `gate` item (AC-044.1), and never as a `deploy-stopped` item; once the step is
  confirmed and the gate is no longer listed, the run's `stopped (human)` line in the Deployed part
  is a `deploy-stopped` item (AC-043.3) until the run is resumed.
Errors: -
Edge cases: the Work tier runs furthest along first, so what is closest to live is finished before anything new starts → AC-042.1; an entry that is `confirmed` and a run that `failed` are listed as `error-open` and `deploy-stopped` → AC-043.3, AC-043.4
Tests: T-042.1 [integration], T-042.2 [integration], T-042.3 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status

### FR-043 Broken: what must be fixed before anything else is trusted
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:48 @3fc3086
Acceptance (EARS):
- AC-043.1 When lint, run on the PRD folder as `prd lint` runs it, reports one or more errors, the
  status command shall list one `lint` item with the text
  `Lint reports <N> errors; the first is <file>:<line>: <rule>: <message>.`, or, when `<N>` is 1,
  `Lint reports 1 error; the first is <file>:<line>: <rule>: <message>.`, where `<N>` counts lint's
  error findings and `<file>:<line>: <rule>: <message>` is the first of them in lint's order, its
  `<file>` the path inside the PRD folder that the finding holds (its `file` in `prd lint --json`),
  whatever the working directory; with no command, `ids` empty, `area` null and `waits_on` `agent`. A finding of severity `warn` is neither
  counted nor named, so findings of severity `warn` alone make no `lint` item.
- AC-043.2 When the PRD folder is inside a git checkout and trace, run on it with no range, reports one
  or more findings, the status command shall list one `lint` item, after the lint item when there is
  one, with the text `Trace reports <N> findings; the first is <the finding's line>.`, or, when `<N>`
  is 1, `Trace reports 1 finding; the first is <the finding's line>.`, where `<N>` counts trace's
  findings and the finding's line is the first of them in trace's order, written
  `<file>:<line>: <rule>: <message>` with `<file>` the path inside the PRD folder that the finding
  holds (its `file` in `prd trace --json`), whatever the working directory; with no command, `ids` empty, `area` null and
  `waits_on` `agent`. When the PRD folder is in no git checkout, it shall not run trace, list no
  trace item, and still print the whole report.
- AC-043.3 When the Deployed part reports for an environment the line
  `<env>: run <run id> stopped (<state>) at step <N>`, `<state>` being `unfinished`, `failed` or
  `human`, and `prd gates list` lists no gate `deploy-step:<run id>:<step>` of that run, the status
  command shall list one `deploy-stopped` item for that environment, in the Deployed part's order,
  with the text `The deploy to <env> stopped: <that line's text after "<env>: ">.`, the command
  `/prd-toolkit:prd-deploy`, `ids` empty, `area` null and `waits_on` `agent`. A run that has such a
  gate is that gate's item (AC-042.3).
- AC-043.4 When an `errors.md` entry is open and its state is `unclassified` or `confirmed`, the status
  command shall list one `error-open` item for it, the entries in the order of their IDs, with the
  text `<E-id> is open (<state>): <title>.`, the command `/prd-toolkit:prd-error <E-id>`, `id` the
  entry's ID, `ids` a list of that one ID, `area` null and `waits_on` `agent`.
Errors: -
Edge cases: lint's order sorts its findings by file, then line, then rule, and trace's by file, line, rule and message → AC-043.1, AC-043.2; an entry in the state `proposed` is its gate's item → AC-042.2; a run log that cannot be read makes no `deploy-stopped` item: the Deployed part passes over it to the next older log of the PRD, and `prd gates list` lists the log as a gate of its own → AC-043.3, AC-044.1; a human step that was confirmed and not resumed waits for `/prd-toolkit:prd-deploy` to resume the run, so it is a `deploy-stopped` item → AC-043.3
Tests: T-043.1 [integration], T-043.2 [integration], T-043.3 [integration], T-043.4 [integration], T-043.5 [integration], T-043.6 [integration], T-043.7 [integration], T-043.8 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status; cli:prd_lint

### FR-044 Waiting on you: the decisions only the owner can make
Status: approved
Source: prd-toolkit/scripts/prdlint/nextpart.py:96 @3fc3086
Acceptance (EARS):
- AC-044.1 When `prd gates list`, run on the PRD folder in this checkout without `--worktrees`, lists
  one or more gates, the status command shall list one `gate` item per gate, in that command's order,
  with the text `<the gate's title> waits for your answer.`, the title being the one `prd gates list`
  prints after the gate's ID; no command; `waits_on` `you`; `id` the gate's ID; `ids` a list of the
  entry's ID for an `error-class:<E-id>` gate, a list of the T-id for a `signoff:<T-id>` gate, and
  empty for every other gate; and `area` the area for an `adoption:<area>` gate and null for every
  other gate.
- AC-044.2 When section 12 of `prd.md` holds rows whose status is `awaiting <who>`, the status command
  shall list one `question` item per such row, in the table's order, with the text
  `<A-id> waits on <who>: <the assumption's text>.` and `ids` a list of that A-id; then, when
  section 13 holds lines other than the single line `None.`, one `question` item per question, in
  the section's order, with the text `An open question waits: <the question's text>.` and `ids`
  empty, where a line that starts with `- ` begins a question whose text is the line without its
  `- `, each following line indented by one or more spaces continues that question, its text
  without the leading spaces joined to the question's with one space, and each other non-empty line
  that is not `None.` is a question of its own whose text is the line, and a question's text is taken
  without the white space at its start and at its end; each item with no command, `area` null and
  `waits_on` `you`.
- AC-044.3 When the `version` in the frontmatter of `prd.md` is below 1.0.0, the status command shall
  list one `draft` item with the text `The PRD is a draft at version <version>, not yet approved.`,
  the command `/prd-toolkit:prd-new`, `ids` empty, `area` null and `waits_on` `you`.
Errors: -
Edge cases: the titles `prd gates list` prints are `Approve <slug> <version>` (approval), the entry's title (error-class), `Run <run id> step <N>: <step title>` (deploy-step), `run log <run id> could not be read` (deploy-step, for a run log that cannot be read), `Adopt area <area>` (adoption) and `Sign off <T-id>` (signoff) → AC-044.1; a `deploy-step` gate names a run, not an entry or a T-id, so its `ids` is empty → AC-044.1; the gates of other worktrees are not listed → AC-044.1; an assumption whose status is `open`, `confirmed` or `corrected` makes no item → AC-044.2; a section 13 line that ends in spaces gives a question that ends in its last mark, so FR-047 adds no second full stop → AC-044.2
Tests: T-044.1 [integration], T-044.2 [integration], T-044.3 [integration], T-044.4 [integration], T-044.5 [integration], T-044.6 [integration], T-044.7 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status; `prd gates list`

### FR-045 Work: furthest along first
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:155 @3fc3086
Acceptance (EARS):
- AC-045.1 When `operations.md` names one or more environments in its Environments table and one or
  more blocks have the status `verified`, the status command shall list one `deploy` item with the
  text `<N> requirements are verified and not live.`, or `1 requirement is verified and not live.`
  when `<N>` is 1, `<N>` counting those blocks, with the command `/prd-toolkit:prd-deploy`, `ids` the
  blocks' IDs in the PRD's order, `area` null and `waits_on` `agent`. When `operations.md` names no
  environment, it shall list no `deploy` item, however many blocks are verified.
- AC-045.2 When an area has one or more blocks with the status `built`, the status command shall list
  one `verify` item for the area, the areas in the order the Requirements part lists them, with the
  text `<IDs> are built and not verified.`, or `<ID> is built and not verified.` when the area has one
  such block, where in the text `<IDs>` is those blocks' IDs in the PRD's order joined by `, ` with
  ` and ` before the last; with the command `/prd-toolkit:prd-build <area>` followed by those
  blocks' IDs in the PRD's order, each after one space (`/prd-toolkit:prd-build import FR-001 FR-002`),
  since only the text joins them with `, ` and ` and `; `ids` those blocks' IDs in the PRD's order,
  `area` the area and `waits_on` `agent`.
- AC-045.3 When an area has one or more blocks with the status `approved`, the status command shall
  list one `build` item for the area, the areas in the order the Requirements part lists them, with
  the text `<IDs> are approved and not built.`, or `<ID> is approved and not built.` when the area
  has one such block, `<IDs>` in the text as AC-045.2 gives it; with the command
  `/prd-toolkit:prd-build <area>` followed by those blocks' IDs in the PRD's order, each after one
  space, as AC-045.2 gives it (`/prd-toolkit:prd-build reports FR-005 FR-006 FR-007`); `ids` those
  blocks' IDs in the PRD's order, `area` the area and `waits_on` `agent`.
- AC-045.4 When a row of `adoption.md` has a state other than `adopted` and no `gate` item is its gate
  `adoption:<area>`, the status command shall list one `adopt` item for the row, in the map's order,
  with the text `Area <area> is not adopted (<state>).`, the command `/prd-toolkit:prd-adopt <area>`,
  `ids` empty, `area` the row's area and `waits_on` `agent`.
Errors: -
Edge cases: a block whose status is `live (since X.Y.Z)` is live and makes no item → AC-045.1; a block `as-built` or `removed` makes no item → AC-045.2, AC-045.3; the blocks of `nfr.md` count as the area `nfr`, which the Requirements part lists last, and `nfr` is an area the build command takes (`/prd-toolkit:prd-build nfr NFR-nnn`) → AC-045.2, AC-045.3; an `extracted` row has an adoption gate only while its answers file exists and is not marked done → AC-045.4
Tests: T-045.1 [integration], T-045.2 [integration], T-045.3 [integration], T-045.4 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status

### FR-046 Nothing waits
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:196 @3fc3086
Acceptance (EARS):
- AC-046.1 When no item of the kinds AC-042.1 lists exists and `operations.md` names one or more
  environments, the status command shall list one item of kind `idle` with the text
  `Nothing waits. Everything approved is live.`, no command, `id` null, `ids` empty, `area` null and
  `waits_on` null.
- AC-046.2 When no item of the kinds AC-042.1 lists exists and `operations.md` names no environment, the
  status command shall list one item of kind `idle` with the text
  `Nothing waits. Everything approved is verified.`, no command, `id` null, `ids` empty, `area` null
  and `waits_on` null.
Errors: -
Edge cases: a PRD with no environment ends at `verified`, so it gets no `deploy` item and its `idle` sentence ends at verified → AC-045.1, AC-046.2
Tests: T-046.1 [integration], T-046.2 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status

### FR-047 A sentence ends with one full stop
Status: verified
Source: prd-toolkit/scripts/prdlint/nextpart.py:35 @3fc3086
Acceptance (EARS):
- AC-047.1 Where the text a sentence of FR-043 to FR-046 inserts last already ends in `.`, `?` or `!`, the
  status command shall end the sentence with that text and add no full stop of its own.
Errors: -
Edge cases: a title, a message, an assumption, a question, a Deployed line or a finding line is inserted as it stands → AC-047.1
Tests: T-047.1 [integration]  (test-cases/status-next.yaml)
Traces: UJ-03; cli:prd_status
