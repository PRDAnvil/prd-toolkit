# prd-toolkit 0.8.9: a help catalogue — design

> **Date:** 2026-11-15
> **Author:** Ivan Histand & Claude Code
> **Status:** Draft, for the owner's review. The design in sections 2 to 9 was agreed in conversation
> on 2026-11-15; this document is not yet approved.
> **Extends:** `2026-11-03-prd-toolkit-0.8-umbrella.md` (its 0.8.9 row) and the specs it extends.
> **Needs:** 0.8.8 (the `prd` launcher).

## 1. Why

A PRD folder has a strict grammar: requirement blocks with fixed field labels, EARS acceptance
criteria, test cases with seven sufficiency elements, registry tables, markers. Its rules live in
`references/prd-format.md`, 711 lines written for agents, and in 40 lint rules known by name only. A
lint finding says in one line what is wrong, and not what the rule wants.

A person in a terminal, a Claude Code session and a client application that shows a PRD each need the
same three answers about whatever is in front of them: **what it is**, **why it is needed** and **its
formatting rules**. If each wrote its own text, the three would drift from each other and from what
lint checks. So the toolkit owns that text and serves it in one machine-readable catalogue.

**Outcome.** One command prints, for every field of the grammar and every lint rule, what it is, why
it is there and how it is written, as text for a person and as JSON for a program.

**Success.** A person who has not read `prd-format.md` can fill any field and fix any lint finding
from the catalogue alone.

## 2. Scope

**In:** the catalogue file; a description on every lint rule; `prd_help.py` and the launcher command
`prd help`; vendoring both; the area `help` in the toolkit's own PRD.

**Out:** help in a language other than English; entries for a pack's own contract types or levels (a
later extension of the catalogue); descriptions shown in `prd lint` output; help for any client's own
screens, which is the client's.

The toolkit stays generic: nothing in the catalogue, the code, the tests or the PRD names a client
application.

## 3. The catalogue: `references/help.yaml`

A YAML list. Each entry:

| Field | Required | Is |
|---|---|---|
| `key` | yes | a unique dotted name, as below |
| `name` | yes | the plain name a person would use ("Acceptance criterion") |
| `what` | yes | one or two sentences: what the thing is |
| `why` | yes | one or two sentences: what depends on it |
| `rules` | no | a list of formatting rules, each one sentence; inline Markdown code spans allowed |
| `checked_by` | no | a list of lint rule names that check it |
| `see` | no | the exact text of a heading in `references/prd-format.md` |

An entry, to show the shape (the real text is written from the references, section 8):

```yaml
- key: block.ac
  name: Acceptance criterion
  what: One testable statement of what the system does, in EARS form.
  why: Each criterion gets at least one test case, and a build is verified against them.
  rules:
    - "`- AC-nnn.n <text>`, where nnn is the requirement's number."
    - The text starts with an EARS opener of the PRD's language table, or with "The <thing> shall".
    - A removed AC keeps its line, with `(removed in X.Y.Z)` after the ID.
  checked_by: [ac-ears, ac-has-test, vague-word]
  see: Requirement blocks
```

**The keys.** Every one of these is present; the catalogue may hold more.

- **Kinds:** `kind.UJ`, `kind.FR`, `kind.NFR`, `kind.T`, `kind.E`, `kind.CS`. Their `name` is the
  plain name: User journey, Requirement, Quality requirement, Test case, Error, Change set.
- **Requirement block:** `block.title`, `block.status`, `block.flow`, `block.acceptance`, `block.ac`,
  `block.errors`, `block.edge_cases`, `block.tests`, `block.traces`, `block.source`.
- **Test case:** `case.ac`, `case.level`, `case.target`, `case.environment`, `case.identity`,
  `case.preconditions`, `case.input`, `case.expect`, `case.expect.output`, `case.expect.effects`,
  `case.expect.errors`, `case.expect.leaks`, `case.rubric`, `case.threshold`, `case.runs`,
  `case.steps`, `case.signoff`, `case.known_failing`, `case.symptom`, `case.refs`.
- **Tables in `prd.md`:** `table.glossary` (§3), `table.standards` (§5), `table.skills` (§6),
  `table.index` (§11), `table.assumptions` (§12).
- **Markers:** `marker.assumption`, `marker.needs_clarification`.

A key uses `_` where the YAML key of the PRD uses `-` (`case.known_failing` is `known-failing:`); the
entry's `rules` name the real spelling.

## 4. Rule descriptions

`@rule(name, severity="error", description="…")` in `prdlint/registry.py`: the registry keeps
`DESCRIPTION: dict[str, str]` beside `SEVERITY`. Every registered rule carries one: what the rule
checks, and how to fix a finding, in one to three sentences, with no line break. All 40 rules get one
in this release, in the rule modules under `prdlint/rules/`.

`prd lint` output does not change: the finding lines, `--list-rules` and `--json` are byte for byte
what 0.8.8 prints. The descriptions appear only in `prd help`.

## 5. The command: `prd_help.py`, `prd help`

It takes no PRD folder. It reads `help.yaml` beside it (section 6) and the rule registry.

| Call | Prints | Exit |
|---|---|---|
| `prd help` | an index: one line per entry, `<key>  <name>`, in the catalogue's order; a blank line; one line per rule, `<name>  <severity>`, sorted by name | 0 |
| `prd help --key <K>` | that entry as text: its name and key, `what`, `why`, the rules as a list, `Checked by:` with each rule's name and description, `See:` with the heading | 0 |
| `prd help --rule <R>` | that rule: its name, severity and description, and the keys of the entries that name it in `checked_by` | 0 |
| `prd help --json` | one document, below | 0 |
| `prd help --json --key <K>` | the document with `entries` limited to that entry; `rules` unchanged | 0 |
| `prd help --json --rule <R>` | the document with `rules` limited to that rule; `entries` limited to those that name it | 0 |
| `prd help --interface` | `1` | 0 |
| an unknown key or rule | stderr `prd_help: no entry '<K>'` or `prd_help: no rule '<R>'`; with `--json`, the error document on stdout | 2 |
| `--key` and `--rule` together, or any other usage error | argparse's usage and error lines; with `--json`, the error document | 2 |
| a `help.yaml` that is missing or not valid | stderr `prd_help: <path>: <reason>`; with `--json`, the error document | 2 |

The document, one line, ending in a newline, as every interface document:

```json
{"interface": 1, "kind": "help",
 "entries": [{"key": "block.ac", "name": "…", "what": "…", "why": "…", "rules": ["…"], "checked_by": ["ac-ears"], "see": "Requirement blocks"}],
 "rules": {"ac-ears": {"severity": "error", "description": "…"}}}
```

An entry carries `rules`, `checked_by` and `see` only when the catalogue gives them. `rules` (the
map) lists every registered rule, sorted by name. The error document is
`{"interface": 1, "kind": "help", "error": "<message>"}` (`interface.error`).

Exit 2 for an unknown key follows the toolkit's convention: 1 means findings, 2 means the command
could not do what was asked, and the shared interface code writes an error document on exit 2.

The interface number stays 1: the document is new, and nothing existing changes.

## 6. Vendoring

- `VENDORED` gains `prd_help.py`. `help.yaml` is vendored as `.prd-toolkit/help.yaml`, the way the
  language tables are vendored from `references/languages/`.
- `prd_help.py` finds the catalogue the way `prdlint/languages.py` finds its tables: from the plugin
  it is `<plugin>/references/help.yaml`; from a vendored copy it is beside the scripts.
- `prd_dispatch.COMMANDS` gains `help`. A vendored copy older than 0.8.9 answers `prd help` with the
  dispatcher's existing `prd: unknown command 'help'` (exit 2); a client checks for that and falls
  back.
- The catalogue's `see` headings point into `references/prd-format.md`, which is not vendored. They
  are names for a reader, not paths.

## 7. The toolkit's own PRD

Through `/prd-toolkit:prd-change`, before any code:

- **A new area, `help`,** written spec-first: `features/help.md` with the requirements,
  `test-cases/help.yaml`, and a `prd_help` entry in `contracts/cli.yaml` (invocation, arguments, the
  output forms and exit codes of section 5). It is the first area of this PRD written before its code;
  the others were adopted from code that existed.
- **`adoption.md`** gains the area's row, with `prd-toolkit/scripts/prd_help.py` and
  `prd-toolkit/references/help.yaml` in its Boundary. The change decides, by the lint rules and the
  change script, which state a spec-first area takes there.
- **`lint-cli`** owns `prdlint/registry.py`. Its requirements say that a rule may carry a description
  and that lint's output does not show it; the change script decides whether that is wording or a new
  acceptance criterion.
- **Version:** minor, 6.2.3 to 6.3.0, unless the change script's diff says otherwise.
- **Dry run:** the black-box tester writes tests for a sample of the new T-ids from the PRD alone; a
  question it cannot answer from the PRD is a gap, fixed in the PRD before approval.

Then `/prd-toolkit:prd-build help <IDs>`: the builder writes the unit tests and the code, the tester
the other tests, and the requirements move to `verified`.

## 8. The text, and how it is kept true

About 45 entries and 40 descriptions are written from `references/prd-format.md`, `references/ears.md`
and `references/test-levels.md`, and from each rule's own code and messages. A wrong formatting rule
in help is worse than none, so:

- **Tests on the content** (unit, the builder's): every registered rule has a non-empty one-line
  description; every `checked_by` names a registered rule; every `see` is the exact text of a heading
  in `prd-format.md` outside a code fence; keys are unique and match `[a-z]+(\.[A-Za-z_]+)+`; every
  key of section 3 is present; every entry has `key`, `name`, `what` and `why`; no entry and no
  description names a client application or an organization.
- **A review of the text against its sources,** before the release: each entry's `rules` checked
  against the passage of the reference its `see` names, and each description against the rule's code
  and its finding messages. Wrong text is corrected in the catalogue; a reference that turns out wrong
  is a separate change.
- **The owner reads the catalogue** before the release.

## 9. Release

Version 0.8.9 in `plugin.json`, `marketplace.json` and `.prd-toolkit/VERSION`; a release test; the
README gains a short section on `prd help` and the changelog entry. Nothing existing changes for a
repository that vendors the toolkit; it gets the command when it next runs `install`. The eval suite
is not rerun: no skill's text changes.

## 10. Decisions and what was set aside

- **The toolkit owns the grammar help** (owner, 2026-11-14), over each client writing its own: the
  formatting rules would drift from what lint checks.
- **A command on the machine interface** (owner, 2026-11-14), over a client reading
  `references/help.yaml` itself (an unversioned contract, and a client may not know the toolkit's
  path) and over parsing `prd-format.md` (prose, and it breaks when a heading moves).
- **A new area written spec-first** (owner, 2026-11-15), over new requirements inside `lint-cli`,
  which is the lint command and the loader.
- **Descriptions live on the rule,** in its `@rule` registration, so a rule cannot be added without
  one; the catalogue names rules and does not repeat their text.
- **`--rule`** is added to what the owner first asked for (owner, 2026-11-15): a person with a lint
  finding looks the rule up directly.
- **An unknown key exits 2,** not 1 as first written (owner, 2026-11-15), to follow the toolkit's
  exit codes.
- **`prd help` alone prints an index,** not the whole catalogue, which runs to several hundred lines.
