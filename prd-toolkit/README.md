# prd-toolkit

A living PRD as the single authority agents build, test and deploy from: a PRD folder in the
repo with contracts and black-box test cases, a 41-rule linter and trace checks, a test agent
that cannot read your code, skills to author, adopt and change it, and a builder that takes an
approved change to verified code, a deploy script that takes verified code to a running
environment, an error ledger that carries every failure from record to a checked fix, and a
publisher that renders the PRD as one page to share, and change sets that link PRDs across
repositories. Packs, languages and judged test cases extend it to documents and to PRDs written in other languages, and a machine interface (JSON output, the change bookkeeping as scripts, one list of pending decisions) lets clients other than Claude Code drive it, and a local decision inbox puts every pending decision in one browser page. Each PRD folder has a README that says what it is, and the published page opens on an Overview. `prd help` says what each field of a PRD and each lint rule means, and `prd status` starts with what the PRD needs next. `practices.md` records where a platform's good practice comes from, and the builder is given the practices that apply. `/prd-toolkit:prd-pack` writes a pack from what two adopted PRDs share, and every card in the decision inbox names its area and links to where the trouble is. `prd error replay` shows whether the commit an error entry names turned its test from failing to passing, and an error in code no adopted area covers closes with that proof. A proposed error class rests on a run, the inbox's error card explains it in plain words and takes a question, and `prd error reopen` takes back a confirmation that a reply doubts or a later run shows wrong. `prd trd` prints a technical view that sets what the PRD says about how the system is built beside what the repository holds. Version 0.8.20.

Design: [docs/superpowers/specs/2026-10-29-prd-toolkit-design.md](../docs/superpowers/specs/2026-10-29-prd-toolkit-design.md),
for 0.2 [docs/superpowers/specs/2026-10-29-prd-toolkit-0.2-design.md](../docs/superpowers/specs/2026-10-29-prd-toolkit-0.2-design.md),
for 0.3 [docs/superpowers/specs/2026-10-30-prd-toolkit-0.3-design.md](../docs/superpowers/specs/2026-10-30-prd-toolkit-0.3-design.md),
for 0.4 [docs/superpowers/specs/2026-10-31-prd-toolkit-0.4-design.md](../docs/superpowers/specs/2026-10-31-prd-toolkit-0.4-design.md),
for 0.5 [docs/superpowers/specs/2026-11-01-prd-toolkit-0.5-design.md](../docs/superpowers/specs/2026-11-01-prd-toolkit-0.5-design.md),
for 0.6 [docs/superpowers/specs/2026-11-01-prd-toolkit-0.6-design.md](../docs/superpowers/specs/2026-11-01-prd-toolkit-0.6-design.md),
for 0.7 [docs/superpowers/specs/2026-11-02-prd-toolkit-0.7-design.md](../docs/superpowers/specs/2026-11-02-prd-toolkit-0.7-design.md),
for 0.7.1 [docs/superpowers/specs/2026-11-03-prd-toolkit-0.7.1-confirm-form-design.md](../docs/superpowers/specs/2026-11-03-prd-toolkit-0.7.1-confirm-form-design.md),
for 0.8.0 [docs/superpowers/specs/2026-11-03-prd-toolkit-0.8.0-design.md](../docs/superpowers/specs/2026-11-03-prd-toolkit-0.8.0-design.md),
for 0.8.1 [docs/superpowers/specs/2026-11-03-prd-toolkit-0.8.1-design.md](../docs/superpowers/specs/2026-11-03-prd-toolkit-0.8.1-design.md),
for 0.8.2 [docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.2-decision-inbox-design.md](../docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.2-decision-inbox-design.md),
for 0.8.3 [docs/superpowers/specs/2026-11-06-prd-toolkit-0.8.3-backlog-design.md](../docs/superpowers/specs/2026-11-06-prd-toolkit-0.8.3-backlog-design.md),
for 0.8.4 [docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.4-prd-readmes-design.md](../docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.4-prd-readmes-design.md),
for 0.8.5 [docs/superpowers/specs/2026-11-08-prd-toolkit-0.8.5-design.md](../docs/superpowers/specs/2026-11-08-prd-toolkit-0.8.5-design.md),
for 0.8.6, the move to PRDAnvil, the plan [docs/superpowers/plans/2026-11-10-prd-toolkit-move-to-prdanvil.md](../docs/superpowers/plans/2026-11-10-prd-toolkit-move-to-prdanvil.md),
for 0.8.7, the fixes, the plan [docs/superpowers/plans/2026-11-11-prd-toolkit-0.8.7.md](../docs/superpowers/plans/2026-11-11-prd-toolkit-0.8.7.md),
for 0.8.8 [docs/superpowers/specs/2026-11-14-prd-toolkit-0.8.8-invocation-design.md](../docs/superpowers/specs/2026-11-14-prd-toolkit-0.8.8-invocation-design.md),
for 0.8.9 [docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.9-help-catalogue-design.md](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.9-help-catalogue-design.md),
for 0.8.10 [docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.10-next-part-design.md](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.10-next-part-design.md),
for 0.8.11 [docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.11-practices-design.md](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.11-practices-design.md),
and for 0.8.12 [docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.12-pack-authoring-design.md](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.12-pack-authoring-design.md).

## Install

```
/plugin marketplace add PRDAnvil/prd-toolkit
/plugin install prd-toolkit@prdanvil
```

Restart Claude Code. To update an installed copy, run `claude plugin update prd-toolkit@prdanvil`,
then `/reload-plugins` (or restart). The scripts run with `uv` (https://docs.astral.sh/uv/); each declares its own
dependencies (`pyyaml`, `sqlglot`, `openapi-spec-validator`) inline. A missing dependency prints an
install hint and exits 2.

## Commands and skills

Claude Code lists a plugin's commands under the plugin's name, so type each in full: `/prd-toolkit:prd-new`, not `/prd-new`, which it answers with "Unknown command".

| Command | Skill | Use |
|---|---|---|
| `/prd-toolkit:prd-new [slug]` | `prd-toolkit:authoring-prds` | Interview to a PRD folder `docs/prd/<slug>/`, lint it, dry-run it with prd-tester, approve it, install the CLAUDE.md block |
| `/prd-toolkit:prd-adopt [area]` | `prd-toolkit:adopting-prds` | Bring an existing repo under a PRD one area at a time, from the code, with the user's word on each requirement |
| `/prd-toolkit:prd-change <description>` | `prd-toolkit:changing-prds` | Change the PRD first, with new IDs and a version bump, before any code; `prd_change.py` keeps the books. `/prd-toolkit:prd-change --review <dir>` reviews a change, edits nothing and writes one JSON verdict (see Machine interface) |
| `/prd-toolkit:prd-context [area] [IDs] [implement]` | `prd_context.py` | Print the focused context pack for one task: the decide pack, or with `implement` the implement pack |
| `/prd-toolkit:prd-build <area> <IDs>` | `prd-toolkit:building-from-prds` | Take approved requirements to verified code: `prd-builder` works on a round branch the build cuts and merges `--ff-only`, then `prd-tester` writes the tests in its `write` mode; the build reconciles by quote and moves statuses `approved`, `built`, `verified` with no version bump |
| `/prd-toolkit:prd-status` | `prd_status.py` | Show what the PRD needs next, where each requirement stands, and the version each environment runs |
| `/prd-toolkit:prd-deploy [--until <env>] [<run id>]` | `prd-toolkit:deploying-from-prds` | Deploy a verified PRD through its runbook with `prd_deploy.py`, stopping at every human step and failure, then record the run (see Deploying) |
| `/prd-toolkit:prd-error [<E-nnn> \| <run id> \| <text>]` | `prd-toolkit:handling-errors` | Record an error in `errors.md` with `prd_error.py`, diagnose it, propose its class and wait for the user's confirmation; the fix starts from a failing test and goes through `/prd-toolkit:prd-change` and `/prd-toolkit:prd-build --fixes E-nnn`, or, for code no adopted area covers, from a test committed alone, then a fix commit and `prd error resolve --red-run`; `prd error replay` shows that the fix turned its test green, and the close is checked with `prd_error.py check` |
| `/prd-toolkit:prd-publish [<out file>] [<request>]` | `prd-toolkit:publishing-prds` | Render the PRD with `prd_publish.py` as one self-contained HTML page (an Overview, a Business and a Technical tab), with per-area summaries by Claude that cite their IDs; the page goes outside the PRD folder, is never committed, and is offered as a private Artifact when the session has the Artifact tool |
| `/prd-toolkit:prd-change-set [<CS-nnn> \| <text>]` | `prd-toolkit:coordinating-prds` | Coordinate one change across linked PRDs in several repositories: one record, one approval for every member's PRD diff, then a build (and where a link needs it, a deploy) per repository in dependency order (see Change sets) |
| `/prd-toolkit:prd-practices [<PRD folder>] [<what to source>]` | `prd-toolkit:sourcing-practices` | Propose best-practice sources, the practices taken from them, standards rows and the skills the PRD needs, each read and quoted, as one PRD change the owner approves; install or write an approved skill only after it (see Practices) |
| `/prd-toolkit:prd-pack <PRD folder A> <PRD folder B> [<pack name>]` | `prd-toolkit:authoring-packs` | Propose a pack from what two adopted PRDs share, each item with the PRD lines it comes from and each difference with both sides; on the owner's decisions, write it into the plugin the owner names, check it with `prd pack check` and commit it on a new branch, pushing and installing nothing |

## The prd command

```
.prd-toolkit/prd lint docs/prd/<slug>   # the vendored copy
.prd-toolkit/prd --help                 # the commands, one line each
```

- One launcher runs every script: `prd <command> [arguments]`, where the command is the script's name
  without `prd_` and `.py`, with `_` written `-` (`prd_build_check.py` is `build-check`). The script
  prints its own usage line, messages and exit code. `prd --help` lists the commands; `prd --version`
  prints the toolkit's version.
- It runs the scripts in one uv environment per requirements list, shared by every clone and worktree,
  instead of one per script path. The scripts keep their uv headers and still run by their file.
- The vendored copy has it as `.prd-toolkit/prd`, the plugin as `scripts/prd` (which one to run: see
  Lint CLI). `publish` runs only from the plugin. Neither is on your shell's PATH: bare `prd` in this
  README is short for one of them (the root README's Install section has a shell function that picks).
- Since 0.8.13 it asks uv for a system Python first, with `uv python find --system ">=3.11"`, and runs on the path it prints; when uv
  finds none it runs on `>=3.11` as before. A `.venv` in the working directory whose interpreter cannot be read
  (a sandboxed session) no longer stops it.
- It is an `sh` script and must keep its executable bit; without it, `sh .prd-toolkit/prd …` works.

## Lint CLI

```
.prd-toolkit/prd lint docs/prd/<slug>   # a repo with hooks installed
uv run --script prd-toolkit/scripts/prd_lint.py --list-rules
uv run --script prd-toolkit/scripts/prd_lint.py --list-packs
uv run --script prd-toolkit/scripts/prd_lint.py docs/prd/<slug> --sample-tids 3
```

- **Which copy to run.** A person's shell does not set `${CLAUDE_PLUGIN_ROOT}`, so the commands here
  name a path. In a repo whose hooks are installed, run the vendored launcher,
  `.prd-toolkit/prd <command>`, where the command is the script's name without `prd_` and `.py`,
  with `_` written `-` (`prd_build_check.py` is `build-check`). Before the first install (no
  `.prd-toolkit/` yet) run the plugin's install path,
  `~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/<script>.py`, where `prdanvil` is
  this marketplace's name and `<version>` is the installed version (`claude plugin list` shows it,
  and so does `ls ~/.claude/plugins/cache/prdanvil/prd-toolkit/`). A checkout of this repo works
  too, as the other two lines do.
- Output is one line per violation: `<file>:<line>: <rule>: <message>`.
- Exit 0 when clean, 1 on violations, 2 on usage, dependency or internal error.
- Output is `<file>:<line>: warn: <rule>: <message>` for a warning (`platform-word`); the exit code counts errors only.
- `--list-packs` prints one line per pack, `<name> <version> (<source>) — <description>`: the built-ins first, then the installed plugins' packs. Run from a vendored copy, `--list-packs` lists the packs vendored in `.prd-toolkit/packs/` in place of the built-ins, each with the source `.prd-toolkit/pack-sources.json` records, and a line on stderr says so; the skills always list from the plugin's own copy.
- `--list-rules` prints the 41 rules and each one's severity. `--sample-tids N` prints up to N randomly chosen T-ids for the authoring
  dry run, one per line with the test-case file that holds it (`T-003.1 test-cases/nfr.yaml`), never a `level: unit` case; it exits 1 with `prd_lint: no non-unit T-ids to sample`
  when the PRD has none.

## Help

```
.prd-toolkit/prd help                    # the index: every entry key and every rule name
.prd-toolkit/prd help --key block.ac     # one field of the PRD grammar
.prd-toolkit/prd help --rule ac-ears     # one lint rule
.prd-toolkit/prd help --json             # the whole catalogue as one JSON document
```

- `prd help` answers what a field of a PRD or a lint finding means. The catalogue holds 48 entries,
  one per field of the PRD grammar (a section, a block line, a test-case key, a marker, a kind of
  ID), and the 41 lint rules each carry a description: what the rule checks and how to clear its
  finding. It takes no PRD folder and reads none.
- With no option it prints the index: one line per entry, its key and its name, then an empty line,
  then one line per rule, its name and its severity.
- `--key <key>` prints the entry: its name, `What:`, `Why:`, its formatting `Rules:`, the rules it
  is `Checked by:` with each one's description, and `See:`, a heading of `references/prd-format.md`.
  `--rule <name>` prints the rule's severity, its description and `Checks:`, the entries it checks.
- `--json` (or `--json=1`) prints one object on one line:
  `{"interface": 1, "kind": "help", "entries": [{"key", "name", "what", "why", "rules", "checked_by", "see"}, …], "rules": {"<name>": {"severity", "description"}, …}}`.
  An entry has `rules`, `checked_by` and `see` only when the catalogue gives them. With `--key` the
  document holds that entry and every rule; with `--rule`, that rule and the entries it checks. A
  client reads it once and looks each key and rule up itself. `--interface` prints `1`.
- An unknown key or rule, a usage error or a catalogue that cannot be read is exit 2, with a message
  on stderr (`prd_help: no entry '<key>'`; a usage error prints the usage line first) and, with `--json`, the document
  `{"interface": 1, "kind": "help", "error": "<message>"}`. Exit 1 is never used, with one known
  exception: a catalogue file that exists and cannot be read (see the changelog, E-020).
- The setting `PRD_HELP_FILE` names another catalogue file to read in place of the shipped one,
  `references/help.yaml` (`.prd-toolkit/help.yaml` in a vendored copy). Lint's own output does not
  change: it never prints a description.
- A copy vendored before 0.8.9 has no `help` command: its launcher answers
  `prd: unknown command 'help'` with exit 2. Run `install` from the 0.8.9 plugin to get it (see the
  changelog).

## Status

```
.prd-toolkit/prd status docs/prd/<slug>          # the report, starting with what the PRD needs next
.prd-toolkit/prd status docs/prd/<slug> --json   # the same as one JSON document
```

- The report starts with the part **Next**: an ordered list of what the PRD needs, each item one
  sentence and, when a command does it, that command on a second line. The parts that follow say
  where every requirement stands (Header, Requirements, Areas, Adoption map, Not built, Not
  verified, Open errors, Upstreams, Consumers, Change sets, CI, Deployed, Matrix).

  ```
  ## Next

  1. E-020 is open (confirmed): prd help prints a traceback and exits 1 when the catalogue file exists and cannot be read.
    run: /prd-toolkit:prd-error E-020
  2. FR-007 and FR-009 are approved and not built.
    run: /prd-toolkit:prd-build orders FR-007 FR-009
  ```

- The items come in three tiers, and inside a tier in this order of kinds:

  | Tier | Kind | When | Command |
  |---|---|---|---|
  | Broken | `lint` | lint reports an error, or trace a finding (one item each) | none |
  | Broken | `deploy-stopped` | a deploy run stopped unfinished or failed, or at a human step that was confirmed and not resumed | `/prd-toolkit:prd-deploy` |
  | Broken | `error-open` | an `errors.md` entry is open and its class does not wait at a gate | `/prd-toolkit:prd-error <E-id>` |
  | Waiting on you | `gate` | a gate of `prd gates list` waits for an answer | none |
  | Waiting on you | `question` | an assumption is `awaiting <who>`, or section 13 holds an open question | none |
  | Waiting on you | `draft` | the PRD's version is below 1.0.0 | `/prd-toolkit:prd-new` |
  | Work | `deploy` | requirements are `verified`, and `operations.md` names an environment | `/prd-toolkit:prd-deploy` |
  | Work | `verify` | an area has requirements `built` | `/prd-toolkit:prd-build <area> <IDs>` |
  | Work | `build` | an area has requirements `approved` | `/prd-toolkit:prd-build <area> <IDs>` |
  | Work | `adopt` | an area of the adoption map is not `adopted` and has no adoption gate waiting | `/prd-toolkit:prd-adopt <area>` |

  Work runs furthest along first, so what is closest to live is finished before anything new starts.
  Each thing is listed once: an entry whose class waits at a gate, a run stopped at a human step
  that waits for its confirmation, and an area whose adoption answers wait, are the gate's item. A lint warning makes no item. When nothing
  matches, the part holds one item of kind `idle`: `Nothing waits. Everything approved is live.`, or
  `… is verified.` for a PRD whose `operations.md` names no environment.
- With `--json`, the Next items come first in `items`, each
  `{"part": "Next", "id", "text", "kind", "ids", "area", "command", "waits_on"}`: `ids` the IDs it
  concerns, `area` its area or null, `command` the command or null, and `waits_on` `you` (the owner
  decides or answers), `agent` (an agent can do it) or null for `idle`. The other items keep their three keys,
  `part`, `id` and `text`. Since the Header is no longer the first item, a client selects the Header by `part`.
- To find the Next items, status runs lint and trace itself. Lint runs the validator commands of the PRD's
  section 7, as `prd lint` does, so the report takes as long as they do and does what they do; the toolkit
  itself fetches nothing and writes nothing.
- A copy vendored before 0.8.10 prints the report without the Next part. Run `install` from the 0.8.10
  plugin to get it (see the changelog).

## Practices

```
.prd-toolkit/prd practices docs/prd/<slug>                          # the sources and the practices
.prd-toolkit/prd practices docs/prd/<slug> --paths src/app.py       # the practices that apply to these files
```

- A PRD folder may hold `practices.md`: where a platform's or a language's good practice comes from, and what
  was taken from it. A PRD without the file works as before.
  - **Sources**, each `S-nn`: a title, a location (a URL or a path in the repository), what it covers, the date
    it was read, and a Decision: `approved`, `declined` or `proposed`. A `proposed` source blocks the PRD's
    approval; a `declined` one stays, so it is not proposed again.
  - **Practices**, each `P-nn`: the source it comes from, the files it applies to (a glob, or `-` for a practice
    about the PRD itself), `code` or `prd`, and one sentence a reader can answer yes or no. A practice is what no
    linter checks; a rule a linter checks is a section 5 row, which names its source's `S-nn` in "Rules live in".
- `/prd-toolkit:prd-practices` fills it. It works out what to source from the PRD (packs, output languages, the
  stack, linter configurations), reads each source before proposing it (a pack's own `sources`, ones the owner
  names, and a search when the session has a web tool), and shows one proposal: the sources, the practices each
  with the passage it came from, the standards rows, the skills, and any instruction it found inside a source
  and did not follow. The owner decides each row, and the whole is one PRD change with its own approval.
  Nothing is installed and no skill file is written before that approval; a plugin is installed only from a
  marketplace already added on the machine, at the scope the owner names; and a skill no plugin provides is
  written into the repository's `.claude/skills/`, from the approved sources, citing them.
- The lint rule `practices` checks the file: the IDs, the Decisions, the dates, that a `code` practice has a
  glob, and that a practice, and each `S-nn` a section 5 row names, cites a source of the table that is
  `approved` (or `proposed` while the PRD is not Approved; a `declined` or missing one is always a finding).
- `prd practices` lists the sources, then the practices, one line each. `--paths <path> …` prints only the
  `code` practices whose glob matches one of the paths, matched as a section 5 row's glob is. `--json` prints
  `{"interface": 1, "kind": "practices", "sources": [{"id", "title", "location", "covers", "read", "decision", "line"}], "practices": [{"id", "source", "glob", "applies_to", "practice", "line"}]}`;
  `--interface` prints `1`. Exit 0 printed, 2 usage or tool error (no PRD, an unsupported `--json=N`).
- The builder is given the practices: on a PRD that holds `practices.md`, the implement context pack has a part
  `## Practices` with the `code` practices whose glob matches the area's Boundary, and the builder's report
  says of each `P-nn: followed`, `P-nn: not applicable (<why>)` or `P-nn: not followed (<why>)`. The last is a
  question for the caller and stops the build, as a required skill that cannot be found does. The `prd`
  practices are answered with the quality checklist when a PRD is written, adopted or changed. No gate checks
  that code follows a practice: trace and the commit hook do not read them, and CI's lint checks only the form
  of the rows.
- `prd change ids next docs/prd/<slug> S` and `… P` give the next source and practice ID. A pack may list
  `sources` in its `pack.yaml` (`{title, location, covers}` items), which `/prd-toolkit:prd-practices` proposes first.
- A copy vendored before 0.8.11 has no `practices` command and no `practices` rule. Run `install` from the 0.8.11
  plugin to get them (see the changelog).

## Adopting an existing repo

`/prd-toolkit:prd-adopt [area]` runs the `adopting-prds` skill. It bootstraps `docs/prd/<slug>/` (first run
only), then takes one area at a time, an area being `features/<area>.md` plus
`test-cases/<area>.yaml`, bounded by the file globs in its Boundary cell. Progress is the adoption
map in `adoption.md`, and each area moves forward one state at a time:

`not started` → `extracted` → `confirmed` → `adopted`

- **extracted:** requirements are written as `as-built`, each with a `Source: <file>:<line> @<commit>`
  line. Apparent bugs become open `E-nnn` entries in `errors.md`, never requirements.
- **confirmed:** only on the user's word on each requirement and each `E-nnn`. Silence or "looks
  fine overall" confirms nothing, and with no answer the area stays `extracted`.
- **adopted:** only after a `prd-tester` suite where every T-id is `pass` or `known-failing E-nnn`,
  plus lint, the checklist, a dry run, `prd_trace.py` and the user's approval. Adoption changes no
  code. The first adopted area takes the PRD to `1.0.0`; each later area is a minor bump.

Adoption also reads the owner's Claude Code memory: the auto-memory directory the session's
system prompt names, starting from its `MEMORY.md` index, and keeps the notes that name the
repository or the area. Their digest goes to the extractor, which records code that contradicts a
note as an open `E-nnn` naming the note, and turns a note the code does not show into a question.
At bootstrap a note may propose the answer to a `[NEEDS CLARIFICATION]` marker or a human runbook
step, written only on the owner's yes, and at confirmation each requirement is shown with the notes
that touch it. A note never confirms a requirement and is never a `Source:`. Nothing from a note
is committed except what the owner confirmed, in plain words, and an `E-nnn` Diagnosis that
paraphrases it. With no memory, adoption says so and goes on.

### Confirming through the form

Step 3 of adoption confirms an area through a local form, not a list of questions in the chat:

```
.prd-toolkit/prd confirm serve docs/prd/<slug> --area <area> [--summaries F] [--port N] [--no-open] [--idle-minutes N]
.prd-toolkit/prd confirm status docs/prd/<slug> --area <area>
```

- `serve` builds the area's items: the as-built requirements, the open `E-nnn` entries that touch the
  area, the area's section 13 questions, and the contract `[NEEDS CLARIFICATION]` markers the area
  names. It serves them on `127.0.0.1` behind a random token and prints
  `url=http://127.0.0.1:<port>/?token=...` as its first line. `--summaries` takes a JSON object of
  item ID to a short text that cites its own ID; `--port` fixes the port (in use, or any other bind
  error: exit 2); `--no-open` does not open the browser; `--idle-minutes` (default 120) ends an idle
  server. Two items under one ID are refused (exit 2).
- The page, `templates/confirm/form.html`, is one self-contained file that loads nothing. It shows one
  item at a time with the list on the left. Keys: C confirms, R corrects, B marks a bug, S asks, and
  the arrows move between items.
- Each answer is saved as it is given to `.prd-confirm-<area>.json` at the repo root, with the item's
  `where` and `served` text. Before anything else, `serve` adds the line `/.prd-confirm-*.json` to
  `.git/info/exclude`, once. An item whose text changed since it was answered counts as open again.
- `serve` ends with exit 0 when Done: every item answered and none changed since. It ends with exit 2 for
  a usage error or a refusal, with `prd_confirm: <why>` on stderr, and with exit 3 when stopped without
  Done (Ctrl-C, SIGTERM or the idle time).
- `status` prints `<answered>/<total>` and one `open <ID>` line per open item, and exits 0 when it
  prints and 2 on error.
- Without a browser, the fallbacks are `AskUserQuestion` and then the checklist file. A headless run
  leaves the area `extracted`, as before.

## Testing from the PRD

The `testing-from-prds` skill and the `prd-tester` agent write and run tests from the PRD folder
alone: it has never seen the code and must not look for it. A dry run writes tests for sampled
T-ids to a dry-run directory without running them; a suite writes tests to the test roots that
`testing.md` names and runs the harness commands. Every test carries an `@prd <T-id>` citation,
and the report lists QUESTIONS, TESTS, HARNESS CHOICES, FILES READ and, for a suite, RESULTS.
Dispatch it as a subagent (the Agent tool), not with `claude --agent`.

**Guard hook.** `hooks/hooks.json` registers `scripts/prd_tester_guard.py` as a PreToolUse hook
on Read, Glob, Grep, Write, Edit, NotebookEdit and Bash. It acts only when the hook's
`agent_type` is `prd-tester` (or ends with `:prd-tester`); every other session passes through.
For the tester it allows reads only of the PRD folder, the scratchpad and the test roots, writes
only to the scratchpad and the test roots (the PRD is read-only), and Bash only for the
`testing.md` harness commands (one simple command each) plus `ls`, `mkdir`, `uv run python -m py_compile` and, since 0.8.4, a checked `grep` (readable paths named one by one, a fixed list of options, the options before the pattern), for a session whose Claude Code build has no Grep tool. It never fails open: with `testing.md`
missing or unparsable, only Read, Glob and Grep under the PRD folder are allowed.

Since 0.8.5 the guard checks every argument after a harness command, not only those that look like
paths. A bare positional or path value must lie under a test root or the scratch directory
(`prd_tester_guard: <arg> is not under a test root`). `--pyargs`, `--doctest-modules`,
`--doctest-glob`, `--rootdir`, `--confcutdir`, `-p <plugin>` (but not `-p no:<name>`) and `-o addopts`
are refused (`prd_tester_guard: <option> is refused after a harness command`), and so is an unquoted
glob character `*`, `?`, `[`, `^` or `#` (`prd_tester_guard: unquoted glob in <arg>`). A quoted
`-k 'T-015*'`, `-n auto`, `-p no:cacheprovider` and `--tb=short` pass.

**Limit.** The guard confines the tester's tool calls, not the processes the harness runs. A
`conftest.py` the tester writes can touch any file when pytest runs it. So callers run an
integrity check after each dispatch (a before and after snapshot of `git status`, the PRD folder's file list
and a tree of the working files), as in `skills/testing-from-prds/dispatching.md`. The hook runs
`python3`: under Python 3.7 or 3.8 it blocks the tester (and only the tester), but with no
`python3` on the PATH the hook exits 127, which Claude Code treats as non-blocking, so the guard
fails open.

**One test (0.8.14).** The Levels table of `testing.md` may hold one more optional column, `One test`,
found by its header name as `Timeout` is: the command that runs one test of the level. `prd error replay`
and `prd error resolve --red-run` run it (see Handling errors); nothing else reads it. The level's
`Harness command` still runs the level at a build and at a deploy, and the tester guard allows what it
allowed.

```
| Level | Harness command | Environment | Gate | One test |
|---|---|---|---|---|
| unit | `uv run pytest tests/unit` | local | build | `uv run pytest -q` |
| system | `uv run pytest tests/system` | staging | deploy | |
```

- The cell is empty or one simple command in backticks, under the rules a `Harness command` follows:
  its first word is none of `cd`, `env`, `sh`, `bash`, `zsh`, `eval` and `exec` and holds no `=`, and it
  holds none of `$`, `{`, `~`, `;`, `|` and `&&`. Quotes group words; nothing is expanded. A blank cell,
  or no column, means the level has no One test command.
- The replay appends exactly one word, a test file's path or a test id, and runs the result from the
  repository root (of a fresh clone) without a shell. So the command must take a path relative to the
  repository root: for a project in a subfolder, `uv run --project <folder> pytest -q`, not
  `uv run --directory <folder> pytest -q`.
- Lint reports a malformed cell through `runbook-tests`, so the rule count stays 41:
  `` docs/prd/greet/testing.md:7: runbook-tests: level 'unit': One test '`cd tests && uv run pytest -q`' is not one simple command in backticks ``.
  `prd help --rule runbook-tests` names the column, and `references/prd-format.md` describes it.
- The command is PRD text, so it changes only through a change the owner approves; that is why the
  replay may run it. A PRD adds the column as a patch, with the section 14 row
  `format: One test column (prd-toolkit 0.8.14)`. A PRD that never adds it needs no change; the replay
  skips its entries.

## Trace CLI

`prd_trace.py` checks the PRD against the repo's tests and commits. It reads the test roots from
`testing.md` (falling back to `tests/`) for `@prd T-nnn.n` citations.

```
.prd-toolkit/prd trace docs/prd/<slug>
uv run --script prd-toolkit/scripts/prd_trace.py docs/prd/<slug> --range BASE..HEAD
```

| Rule | Finding |
|---|---|
| `t-implemented` | a T-id is cited by no test: a unit or build-gate T-id of a `built`, `verified` or `as-built` requirement, or any T-id of a `live` one (in an adopted area, where the PRD has an adoption map). `approved` requirements are skipped; a level with no Gate row counts as build |
| `test-cites-live` | a test cites a T-id that does not exist in the PRD or belongs to a removed requirement |
| `commit-refs` | with `--range`, a commit touches a file inside an adopted Boundary and has no `Refs:` trailer (`Refs: none (no behaviour change)` counts) |
| `status-current` | a requirement's status claims a test that nothing cites: a `built` block's unit T-id, a `verified` block's unit or build-gate T-id, or any T-id of a `live` block |

Where the PRD has an adoption map, `t-implemented` and `status-current` cover `adopted` areas
only. Output and exit codes match lint: `<file>:<line>: <rule>: <message>`; exit 0 clean, 1 on
findings, 2 on a usage, dependency or internal error. A malformed `--range` exits 2.

## Hooks and CI

`prd_hooks.py` vendors the toolkit's scripts into `.prd-toolkit/` and installs two git hooks:
`commit-msg` (a commit touching the Boundary needs a `Refs:` trailer naming live PRD IDs) and
`pre-commit` (each `enforced` standards row runs its linter on the staged files its glob
matches). It never overwrites an existing hook and never sets `core.hooksPath`; in either case it
prints the line to add. Where `core.hooksPath` is set, since 0.8.13, it rewrites a hook in that folder that is
the toolkit's own (a file whose second line starts `# prd-toolkit hook`), so `check` does not call it stale;
any other file there is yours and is left as it is.

The first install runs from the plugin's install path (see Lint CLI for how to find it); then commit `.prd-toolkit/` so every
clone and CI run the same copy:

```
uv run --script ~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd_hooks.py install docs/prd/<slug>
```

Git does not clone hooks, so each other clone runs the vendored copy once (the managed CLAUDE.md
block says so):

```
.prd-toolkit/prd hooks install docs/prd/<slug>
```

Generate the merge-gate CI file, then commit it. `--github` writes
`.github/workflows/prd-toolkit.yml`; `--gitlab` writes `.gitlab/prd-toolkit.yml` and prints the
`include: '.gitlab/prd-toolkit.yml'` line to add to `.gitlab-ci.yml`. An existing file that
differs is rewritten only with `--force`.

The generated `prd-lint` job runs `prd_lint.py --ci` and then `prd_hooks.py check --ci`, which reports
`stale: <path>: re-run prd_hooks.py ci --<forge> --force` when the PRD has since gained a level, an
environment, a `tests` step or a Drift row. `check` and `/prd-toolkit:prd-status` print the same line.
Outside a git checkout `check --ci` exits 2 (`prd_hooks: <path> is not inside a git checkout`), and
`/prd-toolkit:prd-status`'s CI part says the same.

```
uv run --script ~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd_hooks.py ci --github docs/prd/<slug>
uv run --script ~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd_hooks.py ci --gitlab docs/prd/<slug>
```

After a plugin upgrade, `check` names every vendored file that differs from the plugin (exit 1);
run `install` from the plugin again to refresh the copy, and commit it. In the repository that holds the
plugin itself, `vendor` refreshes the copy instead (see below). `uninstall` removes only
the hooks it wrote and leaves `.prd-toolkit/`:

```
uv run --script ~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd_hooks.py check docs/prd/<slug>
.prd-toolkit/prd hooks uninstall docs/prd/<slug>
```

`prd_hooks.py vendor` writes `.prd-toolkit/` exactly as `install` does, packs included, and nothing
else: no git hook, no CLAUDE.md block, no CI file. This repository, which holds the plugin, refreshes
its own copy with it, run from the plugin's directory:

```
uv run --script prd-toolkit/scripts/prd_hooks.py vendor docs/prd/<slug>
```

It prints `vendored the toolkit into .prd-toolkit/ (version <X.Y.Z>)` and exits 0. Run from a vendored
copy it prints `prd_hooks: vendor runs from the plugin, not from .prd-toolkit/` and exits 2.

The hooks and every CI job need only `uv`: CI runs on a bare runner, so each standards linter
and each build-gate Levels harness command must run there too (for example `uv run ...`). A hook
blocks the commit when `uv` is missing, and skips with a message on a branch that has no
`.prd-toolkit/` or no PRD folder.

Since 0.8.5 the toolkit's own `unit` and `integration` Harness commands run with `-n auto`
(`pytest-xdist`, in the dev group of `prd-toolkit/pyproject.toml`), so the generated test jobs run in
parallel. An adopting repository's CI changes only where its own Levels change; no path filter is added.

Known limits:

- A case that is `known-failing` on an open `E-nnn` is a strict expected failure that tags its
  citation, so known-failing tests mark themselves and a `test-<level>` job stays green while the
  bug is open.
- A `commit --amend` that only rewrites the message stages no file, so the `commit-msg` hook lets
  it through; CI's `commit-refs` (trace with `--range`) catches it.

## Deploying

`/prd-toolkit:prd-deploy [--until <env>] [<run id>]` runs the `deploying-from-prds` skill. It takes `verified`
code to a running environment by running the `operations.md` runbook with `prd_deploy.py`: every
step from 1, in order, never from the middle. A script runs the commands, not the model. The skill
shows the plan, relays the user's reply to each human step, offers a failed step's rollback, and
at the end writes only what the run's log proves: the `## Deployed` rows, `verified` → `live (since
X.Y.Z)` after a production finish, and an open `E-nnn` for each failure. Then it commits that close
and runs `prd_deploy.py check`. A deploy changes no behaviour, so it bumps no version.

**The runbook.** Each step is a numbered line followed by labelled lines:

```
3. Approve production (actor: human) (env: production)
   Do: read the staging results and reply "deploy production"
   Check: the reply says "deploy production"
4. Deploy to production (actor: agent) (env: production)
   Run: `./deploy.sh production`
   Check: `curl -fsS https://orders.example.com/health` prints `ok`
   Rollback: `./deploy.sh production --previous`
```

- The step line is `N. <title> (actor: agent|human) (env: <environment>)`; steps are numbered from 1
  without gaps.
- An agent step has `Run:` (one backticked command, or `tests <level>[, <level>...]`), a `Check:`
  (one backticked command, optionally followed by ``prints `<text>` ``, which must equal one stdout
  line) and an optional `Rollback:`. A `tests` step has no `Check:`: the suite, run against that
  environment, is its check. `tests` levels are the Levels in `testing.md`, including the
  `smoke` level.
- A human step has `Do:` and `Check:`, both prose. It is where a person's approval is given: the run
  stops there until the user replies, and `confirm` records the reply verbatim. The request to
  deploy is never that reply.
- **The production gate.** The first production step must be a human step, or come after one. Lint
  fails a runbook without it (`production-gate`); there is no opt-out. Environments has a
  `Production` column (`yes` or `no`) that says which environment is production.

**`## Deployed`** is the PRD's record of what each environment runs: a table of environment, PRD
version, commit, date and run id, one row per environment, written at a run's close and replacing
that environment's earlier row. **`## Drift`** is an optional table of environment, check
(`version` or `config`) and an introspection command; `prd_drift.py <prd-dir> [--env <env>]` runs
each command and compares what it prints with the Deployed row (`version`) or with
`contracts/config.yaml` (`config`). It exits 0 for no drift, 1 for drift (each finding is
`operations.md:<line>: drift-<check>: <what>`) and 2 when a command failed, timed out or printed
something unparseable, which is never counted as drift.

```
.prd-toolkit/prd drift docs/prd/<slug> --env production
```

**CI.** `prd_hooks.py ci` adds a `drift-<env>` job only for an environment with rows in
`## Drift`, and a `test-deploy-<env>` job only for one that a `tests` step runs on: the
deploy-gate suites the runbook runs there, each line `export PRD_ENV=<env> TEST_ENV=<env>; <harness
command>`, so the harness command (one simple command, such as `bash tools/gate.sh system`, as the
Levels rule requires) sees both variables. Both start by
hand (`workflow_dispatch` on GitHub, `when: manual` on GitLab), stay out of the merge gate, and
never deploy; deploying is done from a session.

**Since 0.8.5.**

- *Several human steps in one reply.* `prd_deploy.py confirm <prd> --run ID --step N --reply TEXT`
  may repeat the `--step N --reply TEXT` pair. The first pair is the stopped step; each later pair is
  the next consecutive human step, with its own non-empty reply, one record per step. The call is
  all or nothing, and a bad pair refuses the whole call. The skill adds a later step only when the
  owner's reply names it. The decision inbox still confirms one step at a time.
- *An error entry recorded while a run is stopped.* `prd_error.py new` may write an entry that names
  the run and a step; leave it uncommitted and resume. The close commits it. Any other tracked change
  still refuses `resume`.
- *A `tests` step's own timeout.* A `Timeout` column in Levels (`testing.md`; whole seconds, at least
  1; a pack level's `timeout` is copied into it) bounds that level's run. `--timeout` overrides every
  level; the default is 600 s. A timeout reads `timed out after <N> s (the <level> level's Timeout)`,
  `(--timeout)` or `(the default)`.
- *A close on another branch.* An optional `Branch` column in `operations.md` Environments names the
  branch an environment deploys from. When a run finishes (done or failed) or on `check`, stderr gets
  `prd_deploy: the close is on <current>, not <branch>; push the close commit to <branch> too` (`a
  detached HEAD` for `<current>`). It is a note; the exit is unchanged, and the skill tells the owner
  to push, never pushes itself.
- *A Check that matches by pattern.* ``Check: `<cmd>` matches `<pattern>` `` passes when some stdout
  line fully matches the Python regular expression (`no stdout line matches '<pattern>'` otherwise).
  A pattern holds no backtick; lint refuses one that does not compile, and a Check with both `prints`
  and `matches`.

**What `prd_deploy.py` refuses.** Exit 1 (`refused`), with each reason printed:

- `run`: the tracked working tree is dirty; `prd_lint` or `prd_trace` finds anything; any
  requirement is still `built` (a deploy starts from `verified`); the run reaches a production
  environment while a `verified` requirement has a deploy-gate T-id that no test cites (it could
  never go `live`); or another `prd_deploy` command is running in this repository;
- `resume`: the run is another PRD's run (`run <id> is for <folder>, not <folder>`), or its log
  names no PRD folder (written before the header named it); HEAD or the PRD version moved since
  the run started, the tree changed, or the runbook changed (`operations.md` or `testing.md`); the
  run has no step records, is done, or did not stop at a human step, or the step it stopped at is
  not a human step of the runbook; the run's human step has no `confirm`, or its `confirm` was
  already used; a step started and did not finish (a killed or timed-out call); the run failed,
  since a failure ends the run and `resume` never goes past it; or another `prd_deploy` command
  is working on this run or running in this repository;
- `rollback`: the run is another PRD's run, or its log names no PRD folder; HEAD or the PRD
  version moved since the run started, the tracked tree is dirty, or the runbook changed; or
  another `prd_deploy` command is working on this run or running in this repository;
- `recover`: the run is another PRD's run, or its log names no PRD folder; the step has no
  unfinished `start` (`step <N> has no unfinished start in run <id>`) or already has a result
  (`step <N> already has a result in run <id>`); or another `prd_deploy` command is working on
  this run or running in this repository;
- `check`: the run is another PRD's run, or its log names no PRD folder, as its only line; every
  other exit 1 of `check` prints close-check findings.

Exit 2 (usage error, nothing run), with the reason printed:

- `plan` or `run`: an `--until <env>` whose cut would take a production step along (a step on
  `<env>` after a production one), unless `<env>` is production itself;
- `rollback`: a second rollback of the same step, or a rollback of a step that is not the run's
  failed step or has no `Rollback:`;
- `confirm`: another PRD's run, or its log names no PRD folder, or another `prd_deploy` command working on this run; a step that
  already has a `confirm` record, or that is not the human step the run stopped at; or an empty
  reply;
- `recover`: no log for the run, or an empty reply.

`recover --run <id> --step <N> --reply "<the user's words>"` ends a step killed between its `start`
and its result, once the user has checked the environment: it logs the reply and a failed step
(`recovered: no result after start`, never a pass) and ends `prd-deploy: failed step=<N> run=<id>`,
exit 4, so `rollback` and the close work as for any failed run.

`run`, `resume` and `rollback` hold a repository-wide lock while they run commands; a run stopped
at a human step holds none, and `plan`, `check` and `confirm` take none. `recover` runs no command
but takes the same repository lock and the run's lock while it writes.

A failed step exits 4 and prints its `Rollback:` command; the script never runs it unasked.

**Known limits.** The script reads the runbook's steps and hashes `operations.md` and `testing.md` a
moment apart; an edit to either in the window between reading the runbook steps and hashing them is
not caught. The script cannot prove that a person wrote a `confirm` reply. The skill requires
the user's own message, verbatim, the log keeps it, and the close report quotes it, but a `confirm`
reply is trusted to be the user's. Steps run in a shell on the session's machine with its
credentials; the toolkit adds no sandbox.

## Handling errors

`/prd-toolkit:prd-error` (skill `prd-toolkit:handling-errors`) takes any error, a bug, a failing test, an
incident or a failed deploy, from a record to a checked fix. `errors.md` holds one `### E-nnn`
entry for each; `prd_error.py` is the only writer.

1. **Record.** `new` appends the entry as `unclassified` with its `Detected:` line and a bounded
   `Evidence:` (20 lines at most, no secret or classified value). A build or deploy that stops on a
   failure records its entry itself.
2. **Reproduce.** A code reading is not a reproduction: this step ends in a run, the failing test, the
   command the report names, or a probe in a scratch clone, and the diagnosis quotes the command, the
   expected output and the printed one; an error that does not reproduce gets a diagnosis that
   starts `not reproduced:` and says what was tried, recorded with `propose --class unclassified`; it
   opens no gate.
3. **Propose.** `propose` writes the class (`code bug`, `spec gap`, `invalid requirement`,
   `environment` or `standard`), or since 0.8.15 `not a defect`, a diagnosis and, with `--explanation`,
   an `Explanation:` line that says in plain words what was run, what it printed, what the PRD line
   says and why this class. Nothing is final yet.
4. **Your confirmation.** `confirm` records your reply verbatim, in your words, and the class you
   settle on. A reply that doubts or asks is not a confirmation; `reopen` takes back one the inbox
   already wrote (**A class settled on a run** below). Only a confirmed entry can be cited by code (`Refs: E-nnn`); the commit-msg hook and
   `prd_error.py check` refuse a code commit that cites an unconfirmed one.
5. **Fix.** A change goes through `/prd-toolkit:prd-change` (citing the entry), and `/prd-toolkit:prd-build --fixes E-nnn`
   builds it from the entry's failing test. The skill never edits code or tests itself, except code no
   adopted area covers: a confirmed `code bug` whose faulty code lies outside every adopted Boundary
   takes the route of **Code no area covers** below, a test committed alone, then the fix.
6. **Resolve and check.** `resolve` writes the resolution (`<T-id> [<level>], PRD <X.Y.Z>, fixed in
   <commit>`; `<T-id or ->, PRD <X.Y.Z>, run <run id>`; `not a defect: <why>`; or, since 0.8.14, a red
   run, `fixed in <commit>, red run <test id> [<level>]`). The skill replays a fix that names a T-id
   before it commits the ledger (**Replay a fix** below), then `prd_error.py check <base>..<head>`
   validates every change to the ledger in the range.

```
.prd-toolkit/prd error new docs/prd/<slug> --title "<title>" --source "<where seen>" [--url <address>]
.prd-toolkit/prd error url docs/prd/<slug> E-nnn <address>
.prd-toolkit/prd error propose docs/prd/<slug> E-nnn --class "<class>" --diagnosis "<root cause>" [--explanation "<plain words>"] [--touches FR-001,FR-002] [--recurrence E-mmm]
.prd-toolkit/prd error reopen docs/prd/<slug> E-nnn --reason "<why>"
.prd-toolkit/prd error list docs/prd/<slug> --open
.prd-toolkit/prd error replay docs/prd/<slug> E-nnn [--timeout <seconds>] [--json]
.prd-toolkit/prd error resolve docs/prd/<slug> E-nnn --commit <sha> --red-run <test id> --level <level>
.prd-toolkit/prd error check docs/prd/<slug> <base>..<head>
```

**Where the trouble is (0.8.12).** An entry may hold one line `URL: <address>`, after `Touches:`: the
page, dashboard or failed run the error is about. `prd error new --url <address>` writes it, and
`prd error url` sets or replaces it later (`-` removes it). An area may give its own address as the
`url` part of its `Target:` line, the line's last part, after the pack and the output language:
`Target: output language en, url https://example.com/orders`, or `Target: url <address>` alone. Both
addresses start with `http://` or `https://` and hold no white space; lint reports a malformed one
(`error-entries` for the entry's, `pack-resolves` for the area's), and nothing fetches either. The
entry's card in the decision inbox names the entry's areas and links to its URL, else to the URL of
its first area that has one (see Decision inbox). The handling-errors skill passes an address the
report gives to `--url`. A copy vendored before 0.8.12 has neither option nor the `url` part: its
lint refuses the part, so run `install` from the 0.8.12 plugin first (see the changelog).

**Replay a fix (0.8.14).** A resolution names the commit that fixed the error, and `check` verifies
only that the commit is in history. `prd error replay` checks the claim itself: it runs the entry's
test, through its level's `One test` command (see Testing from the PRD), on `<sha>^`, the fix commit's
first parent, where it must fail, and on `<sha>`, where it must pass. Each run happens in a git clone
of its own under the system temporary folder (`git clone --shared --no-checkout`, then a detached checkout
of the commit), removed when the run ends. The command's own git commands never write the working tree, the index or
the git folder of the repository it starts in, so it also runs where that folder cannot take a new
worktree, as in a sandboxed session. A test it runs has the command's environment (see the limits below). It reads the entry from `errors.md` in the
working tree, so it replays a resolution that is written and not yet committed.

- **A fix with a T-id** (`<T-id> [<level>], PRD <X.Y.Z>, fixed in <sha>`): it runs, one by one, each file
  under a test root that cites the T-id (`@prd <T-id>`) in the resolving commit, the first commit whose
  `errors.md` holds the entry's Resolution line (`HEAD` while the line is not committed). Each tree's
  test roots are replaced, whole, by the resolving commit's, so a regression test committed after its
  fix still proves it, and the run on `<sha>^` runs the old code. At least one cited file must fail on
  `<sha>^`, and every one must pass on `<sha>`.
- **A red run** (`fixed in <sha>, red run <test id> [<level>]`, below): it runs the test id on each tree
  as committed.
- **A run** is the command with its one argument, started from the clone's root with the command's
  environment, in a process group of its own. Exit 0 passes; any other exit fails. The level's `Timeout`
  applies (600 s without one), and `--timeout` overrides it; a run that times out is killed, and is a
  finding, never a proof.
- **Exit 0** prints the proof, `<E-nnn>: <T-id or test id> fails on <sha>^ and passes on <sha>`, as in
  `E-001: tests/unit/test_count_names.py fails on 6c1f39f^ and passes on 6c1f39f`, or a skip and its
  reason: `skipped: <E-nnn>: resolved by an environment run`, `skipped: E-001: resolved as not a defect`,
  `skipped: <E-nnn>: <level> is a deploy-gate level` (the deploy run is its proof) or
  `skipped: E-001: unit has no One test command`. A skip proves nothing.
- **Exit 1** prints one finding per line: `<E-nnn> is not resolved`;
  `<E-nnn>: resolution is not one of the four forms`; `<E-nnn>: <level> is not a level of testing.md`;
  `<E-nnn>: <sha> names no commit`, `<E-nnn>: <sha> names more than one commit` or
  `<E-nnn>: <sha> has no parent`; `<E-nnn>: <T-id> is cited by no test in <resolving commit>`;
  `<E-nnn>: <T-id or test id> passes on <sha>^; <sha> did not turn it green`, as in
  `E-001: T-001.2 passes on 6c3a03e^; 6c3a03e did not turn it green` for a test that passed before its
  fix; `<E-nnn>: <T-id or test id> fails on <sha>: <file or test id>`;
  `<E-nnn>: timed out after <N> s on <commit>`; and `<E-nnn>: <program> cannot start on <commit>`. An
  ID that names no entry is `refused: <E-nnn> is not an entry` on stderr, exit 1. Exit 2 is a usage or
  tool error, such as `prd_error: --timeout must be a whole number of seconds of at least 1`.
- **The skill** runs it after every `resolve` that names a T-id, before `errors.md` is committed. On
  findings it puts the ledger back with `git restore --staged --worktree docs/prd/<slug>/errors.md`,
  leaves the entry `confirmed`, reports each finding and returns to the build; it names a skip and its
  reason in its report. Nothing runs it in CI: the generated CI file is unchanged.

`--json` prints one document on one line, with the exit code it has without it. `outcome` is `holds`,
`skipped` or `findings`; `subject` is the T-id or the test id; `reason` is the skip's reason, else null;
and `runs` holds one record per run, in the order made: the full SHA of the tree that ran, `before` or
`after`, the argument, the exit code (null for a run that timed out or could not start), the seconds it
took and `timed_out`. `prd error replay --interface` prints `1`. The finding above, as JSON:

```
{"interface": 1, "kind": "error-replay", "entry": "E-001", "outcome": "findings", "subject": "T-001.2", "reason": null, "findings": ["E-001: T-001.2 passes on 6c3a03e^; 6c3a03e did not turn it green"], "runs": [{"commit": "6069f6f49c700c3263677b068585aef75bd6471d", "when": "before", "argument": "tests/unit/test_greet.py", "exit": 0, "seconds": 0.676, "timed_out": false}, {"commit": "6c3a03e9620666fcad1af4d1ce697c68cbcc6f66", "when": "after", "argument": "tests/unit/test_greet.py", "exit": 0, "seconds": 0.534, "timed_out": false}]}
```

**Code no area covers: a red run (0.8.14).** A fix with a T-id needs a requirement, and code outside
every adopted Boundary of `adoption.md` has none, so an error there could not close. It now closes with
a fourth resolution form, a fix with no T-id and no PRD version, since no requirement changed:

```
Resolution: fixed in <sha>, red run <test id> [<level>]
```

`<test id>` is what the level's `One test` command takes, a path or a test id, and `<level>` is a
build-gate level. When the owner has confirmed the class `code bug` and the diagnosis puts the faulty
code outside every adopted Boundary, the skill takes this route in place of `/prd-toolkit:prd-change`
and `/prd-toolkit:prd-build`, and writes the test and the fix itself: the builder and the tester work
from requirement blocks, and this code has none. The rest of the loop stands: record first, no fix
before `Confirmed:`, no retry in place of a diagnosis.

1. **The failing test first,** committed alone (`Refs: E-nnn`) and run with the level's `One test`
   command to show it failing. Always commit the failing test alone, before the fix: a test committed
   with its fix fails on the parent for lack of its file, and the replay would call that fix proven.
2. **The fix,** in its own commit citing the entry.
3. **`resolve --red-run`,** which replays before it writes, and refuses a fix whose test did not fail
   on the commit before it and pass on it.
4. **The ledger committed, then `prd error check`,** as for every entry.

In a repository whose adopted area `greet` covers `src/greet/**` and `tests/**`, with the bug in
`tools/count_names.py`, the fix commit `6c1f39f` resolved as
`Resolution: fixed in 6c1f39f, red run tests/unit/test_count_names.py [unit]`, and `resolve` printed
`E-001 resolved code bug`. It refuses this form, and writes nothing (exit 1), when:

- a path the fix commit changes is covered by an adopted area, as with the test's own commit named in
  place of the fix:
  `refused: 3845582 changes tests/unit/test_count_names.py, which area greet covers; resolve with a regression T-id`.
  That code has requirements, so its fix takes a regression T-id and `/prd-toolkit:prd-build --fixes`.
  A PRD with no adoption map covers every path outside the PRD folder and `.prd-toolkit/`, so it never
  takes this form:
  `refused: the PRD has no adoption map, so every path is covered; resolve with a regression T-id`;
- the entry's class is not `code bug`: `refused: <E-nnn> is classed <class>; a red run resolves a code bug only`;
- the level is not in Levels, is a deploy-gate level or has no One test command:
  `refused: <level> is not a level of testing.md`, `refused: system is a deploy-gate level` or
  `refused: <level> has no One test command; add the One test column to testing.md Levels through /prd-toolkit:prd-change`;
- the test id holds white space or starts with `-`, since it becomes a command argument:
  `refused: the test id must hold no white space and must not start with -`;
- the replay does not hold: each finding as `refused: <finding>`, such as
  `refused: E-001: tests/unit/test_count_names.py fails on 86287b0: tests/unit/test_count_names.py`
  for a commit made before the test existed;
- or, as for every form, the entry is not `confirmed`.

`--red-run` with `--t`, `--version`, `--run` or `--not-a-defect`, or without `--commit` or without
`--level`, and `--level` without `--red-run`, is a usage error, exit 2 (a Ctrl-C during its replay exits
130):
`prd_error: --red-run takes --commit and --level, and no --t, --version, --run or --not-a-defect`.

`prd error check` accepts a red run added in its range and runs no test. It reports, each as
`errors.md: <E-nnn>: <finding>`, `commit <sha> is not an ancestor of HEAD`,
`the PRD has no adoption map, so every path is covered`,
`commit <sha> changes <path>, which area <area> covers` and `<level> is not a level of testing.md`; a
line of no form is now `resolution is not one of the four forms`. The three older forms are written,
read and checked as before, and `resolve` runs no replay for them. A copy vendored before 0.8.14
reports a red run as none of the three forms it knows: re-vendor before a ledger holds one (see the
changelog).

**Limits of the replay (0.8.14).**

- An exit code cannot tell a test that failed from one that could not run. The second run catches a
  harness that cannot run in a fresh checkout, because it fails there too and the proof does not hold.
  A test committed in the same commit as its fix fails on the parent for lack of its file, so the replay
  would call that fix proven: commit the failing test alone, before the fix.
- The proof is per file. Two entries fixed together whose tests share a file share one proof.
- For an entry with a T-id, a test added to the same file between the fix and the resolve can fail the
  second run.
- A One test program that cannot start in a fresh clone (a path into a virtual environment, for
  example) is a finding, `<E-nnn>: <program> cannot start on <commit>`: give the column a command that
  builds what it needs, such as `uv run --project <folder> pytest -q`.
- The replay removes its clones on SIGINT (exit 130). SIGTERM is not handled: a replay killed that way
  leaves its folder under the system temporary folder and its running test behind; remove the folder.
- A Ctrl-C that arrives while the replay removes one run's clone is lost; press it again in the next
  run.
- The test a replay runs has the environment the command was started with. Git's own commands in the
  replay ignore `GIT_INDEX_FILE`, `GIT_DIR` and `GIT_WORK_TREE`, but a test that calls git itself sees
  them: do not start a replay from inside a git hook.
- `resolve --red-run=` with an empty test id is refused as `resolution is not one of the four forms`, not
  with the test id's own refusal.
- A fix that lies inside a test root cannot be proven by a T-id replay: both trees get the resolving
  commit's test roots, so they are the same tree and the first run passes.
- A tree older than something the `One test` command needs (a test plugin, an option of the runner) fails
  both runs for that reason, and the proof does not hold.
- A clone has the repository's commits and none of its local configuration, its hooks or the checkouts of
  its other refs: a test that relied on its tree being a linked worktree of the repository does not find
  them.
- A red run typed into `errors.md` by hand is never replayed, and `check` accepts it: only
  `resolve --red-run` proves one.
- With `GIT_INDEX_FILE`, `GIT_DIR` or `GIT_WORK_TREE` set, a test that calls git can write the repository
  the replay was started in (E-036, open). A test that leaves a folder it took the write permission from
  makes the replay leave its folder under the system temporary folder, with no message (E-037, open).
- A session's Bash call that times out may end the replay the way SIGTERM does: give the call a timeout
  above the runs' total.
- When a T-id's test files number more than one, a timeout or cannot-start finding does not name the file
  it is about.
- A `One test` cell lint calls malformed reads as no `One test` command (a skip, or the refusal that says
  to add the column), and a `Test roots:` entry written `./` or with a leading `./` makes a T-id replay
  report `is cited by no test`: write the roots without it.

**Known-failing tests.** A case marked `known-failing` on an open entry is a strict expected failure
that tags its citation `@prd T-nnn.n known-failing E-nnn`; it fails the day the bug is fixed, so the
marker cannot outlive the defect. The trace's `known-failing-tags` rule reports a case with no tagged
citation and a tag whose entry is resolved or unknown.

**A class settled on a run (0.8.15).** A proposed class rests on a run, and a confirmation can be
taken back when a reply doubts it or a later run shows it wrong.

- `propose --explanation '<plain words>'` writes `Explanation: <the words>` directly before the
  Diagnosis, or in place of the one there; a `propose` without it leaves the line as it was. The
  decision inbox's card shows it first, with the Diagnosis behind a `Diagnosis` disclosure.
- `propose --class unclassified` records an entry that did not reproduce, with its `not reproduced:`
  diagnosis; it prints `E-nnn unclassified` and opens no `error-class` gate.
- `not a defect` is a class: a run that shows the system doing what the PRD says is proposed as
  `not a defect`, and a confirmed one resolves with `resolve --not-a-defect`. Lint's class list
  holds it: `E-001: Classification: 'typo' is not one of code bug, spec gap, invalid requirement,
  environment, standard, not a defect, unclassified`.
- `reopen <prd_dir> E-nnn --reason '<why>'` takes back a confirmation. On a confirmed, open entry it
  replaces the `Confirmed:` line with
  `Reopened: 2026-11-23, "the reply was unsure"; was Confirmed: 2026-11-22, "I guess, sure?"`, keeping
  the old line word for word, and prints `E-001 proposed code bug`. The entry is `proposed` again, so
  no code commit may cite it until a new `confirm`, which writes its line after the last `Reopened:`
  line; a second reopen adds a second line. It refuses an entry that is not confirmed
  (`refused: E-001 is not confirmed`), a resolved one (`refused: E-001 is resolved`), a reason that
  would open a code fence or holds `; was Confirmed:` (exit 1), and an empty reason
  (`prd_error: the reason is empty`, exit 2).
- `check` accepts a write that swaps a `Confirmed:` line for the `Reopened:` line that quotes it. It
  still reports `Confirmed: changed` for a removal no `Reopened:` line quotes, and reports
  `Reopened: changed` for an edited or deleted `Reopened:` line and
  `Reopened: added without its Confirmed:` for one that quotes nothing. Lint checks the line's form
  (`E-001: Reopened: must be '<YYYY-MM-DD>, "<reason>"; was Confirmed: <YYYY-MM-DD>, "<reply>"'`), and
  its prose rules skip it, as they skip `Confirmed:`.
- The skill reproduces again at the start of the fix: a confirmed entry that no longer reproduces on
  `HEAD`, or whose run now points to another class, is reopened, never resolved by a commit made
  without it.

**A killed deploy step.** `prd_deploy.py recover` ends a step killed between its `start` and its
result, once you have checked the environment (see Deploying); the run then fails as any failed run
does, and the failure close records the entry.

**What `prd_error.py` refuses.** Exit 1 (`refused`), with each reason printed:

- `new`: a `Touches:` ID the PRD does not define, or evidence over 20 lines;
- `propose`: an entry that is `confirmed` (its class is settled) or `resolved`, a
  `Recurrence of:` that is not an entry, or a `--touches` ID the PRD does not define;
- `confirm`: an `unclassified`, already `confirmed` or `resolved` entry;
- `reopen`: an entry that is not `confirmed`, or is resolved, or a reason that holds `; was Confirmed:`;
- `resolve`: an entry that is not `confirmed`, or is already resolved, or a `--t` with no test case or level;
  with `--red-run`, also each refusal of **Code no area covers** above;
- `new`, `propose`, `confirm` and `resolve`: a value that would open a code fence (an `Evidence:` line,
  or a title, diagnosis, reply or reason, whose first non-space characters are ```` ``` ```` or `~~~`),
  which would end the ledger's parse (`refused: Evidence: line <n> would open a code fence; drop it or
  put text before it`, or `refused: --reply would open a code fence; …`);
- `new`, `propose`, `confirm` and `resolve`: a write that would add a lint finding located in
  `errors.md` (`refused: the entry would fail lint: <file>:<line>: <rule>: <message>`, one per finding,
  then the hint `put quoted output in backticks`); `errors.md` is left byte-identical. Lint's prose
  rules skip `Evidence:` and `Confirmed:` lines, and `schema-refs` skips `errors.md`, so quoted output
  belongs in `Evidence:` bare and in backticks elsewhere; since 0.8.15 they skip `Reopened:` lines too;
- any command naming an `E-nnn` that is not an entry; and `check`, whose exit 1 prints findings, one
  per line, as `errors.md: E-nnn: <finding>`, and `replay`, whose exit 1 prints its findings on stdout
  (see **Replay a fix**).

Exit 2 (usage error, nothing written): an empty reply, class, diagnosis, title or source, or an empty
reason or explanation; `unclassified` as the class of `confirm`; a malformed version, T-id, run id or commit (7 to 40 lowercase hex digits); a fix without its
T-id, level or commit (`a fix needs a T-id, its level and a commit`); `--not-a-defect` combined with
another resolution; `--red-run` combined with another resolution's flags, or without `--commit`
or `--level`; an unreadable range or PRD folder.

## Publishing

`/prd-toolkit:prd-publish [<out file>] [<request>]` (skill `prd-toolkit:publishing-prds`) renders the PRD with
`prd_publish.py` as one self-contained HTML page with an Overview tab (opened by default), a Business tab and a Technical tab; the Overview is described under READMEs and the Overview tab. The page
loads nothing (no script, stylesheet, font or image from any URL), so it opens offline, by email or
on an intranet; PRD text is rendered from markdown with raw HTML escaped, and the error ledger
appears without its `Evidence:` lines.

**Diagrams (0.8.5).** A mermaid fence renders as an inline SVG in a `<figure class="diagram">`, drawn
by the pinned renderer `mermaidx==0.11.3` named in `prd_publish.py`'s dependency header, followed by a
closed `<details>` titled `Diagram source` that holds the source. The SVG is checked before it goes in
(no script, event attribute, outside link, `foreignObject` or outside `url(`), so the page still loads
nothing. A diagram that cannot render, or whose SVG fails the check, stays a `<pre class="mermaid">`
block and prints `prd_publish: diagram at <file>:<line> shown as source: <reason>` on stderr; the
render still exits 0. Publish the page as its own Artifact, never as a file inside another one: an
Artifact draws a `pre.mermaid` block only on its own main page.

**Summaries.** The skill writes a short plain-language summary of each area (600 characters at most,
in the language you ask for), and the page shows it in a box labelled `Summary by Claude of
FR-001–FR-004, PRD <version>` that cites its IDs. Summaries are written fresh for each publish and
never stored in the PRD folder.

**Where it goes.** The page is written outside the PRD folder, to the path you name (default
`./<project>-prd-<version>.html` in the repository root, untracked; the summaries file is written
beside it and deleted after the render), and is never committed; the skill reports its absolute
path. An untracked page stops the next `/prd-toolkit:prd-build` at its clean-tree check, so move it out of the
repository or delete it first. When the session has the Artifact tool,
the skill offers the same file as a private Artifact, or updates one you name; otherwise, or when you
decline, it gives you the file path.

`prd_publish.py` is not vendored into `.prd-toolkit/`; it runs from the plugin (see Lint CLI for the install path).

```
uv run --script ~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd_publish.py render docs/prd/<slug> --out <file> [--summaries <json>]
```

**What `prd_publish.py` refuses.** Exit 1 (`refused`): an `--out` inside the PRD folder; a summary
whose version is not the PRD's, whose area does not exist, whose ID is undefined or belongs to
another area, or whose text is over 600 characters; a summaries file that is not an object with version and areas (`summaries: must be an object …`), an area that is not an object with text and ids, or `ids` that are not a list of requirement IDs (`… ids must be a list of requirement IDs`). Exit 2 (usage error, nothing written): not a PRD
folder, an unmigrated `adoption.md`, an unreadable summaries file, or an output path that cannot be
written.

## Technical view

```
.prd-toolkit/prd trd docs/prd/<slug>                 # print the view
.prd-toolkit/prd trd docs/prd/<slug> --out trd.md    # write it to a file
```

- `prd trd` prints one Markdown document, the technical view: what the PRD says about how the system
  is built beside what the repository holds at HEAD. Its sections are Stack, Architecture, Standards
  and Skills (copied from `prd.md` sections 1, 4, 5 and 6, with assumption markers left out), Contracts
  (the section 7 types, which stay in the PRD), Components (each area's state, Boundary, file count at
  HEAD and requirements), Requirements to code (each `Source:` line's refs, joined by commas, and `yes`
  at HEAD only when every ref holds) and Uncovered code (the files at HEAD that no Boundary glob
  matches, leaving out the test roots and the CI files `prd hooks ci` generates). Each section's `From:`
  line says where it comes from.
- The view is an output, never part of the PRD: nobody edits it, no gate approves it, no hook or CI
  job runs it, and the black-box tester never reads it. The same commit and PRD folder always give
  the same bytes, and the view holds no date, so two views diff cleanly; you may commit one to diff it
  between releases.
- Its use is to learn which parts people want to keep by hand. Such a part becomes a managed document
  only through a later PRD change, and anything the black-box tester needs stays in the PRD.
- `--out` is refused (exit 1) inside the PRD folder or `.prd-toolkit/`, symbolic links followed. Exit
  2: no `prd.md`, no git work tree, a repository with no commit, or an `--out` file that cannot be
  written (its folder is never created).

## Links

A PRD may link to the PRDs of other repositories. `links.md` (optional, in the PRD folder) holds an
Upstreams table (the PRDs this one uses, each with a Location, a lock of Version and Commit, and a
`Needs` of `verified` or `live in <env>`) and a Consumers table (the PRDs that use this one). A PRD
without `links.md` is unchanged.

A downstream PRD cites an upstream item with a prefix, `<kind>:<prd>/<name>` in a test case target
or a `Traces:` line (`cli:greet/greet`, `table:transform/orders_daily`) and `<prd>/<table>.<column>`
in prose. The kinds that cross are `op`, `table`, `event`, `job` and a custom type whose files are
YAML mappings; `code:` never does. `prd_links.py sync` copies the cited items, and only those, into
`contracts/upstream/<prd>/` as a pinned snapshot, and lint, trace, the tester and context packs read
that snapshot offline. Never edit it by hand.

```
.prd-toolkit/prd links add docs/prd/<slug> <location> [--needs <value>]
.prd-toolkit/prd links sync docs/prd/<slug> <upstream> [--ref <ref>]
.prd-toolkit/prd links check docs/prd/<slug> [--ref <ref>] [--ci]
.prd-toolkit/prd links impact docs/prd/<slug> [--base <ref>]
```

`check` compares each snapshot item with its upstream (`same`, `changed`, `removed`), reads each
consumer's snapshot of this PRD the same way, and checks that both sides list the link. `impact` lists
the contract items the working tree changes and the consumers that cite them. A git URL location is
read with your own git credentials, cached under `${XDG_CACHE_HOME:-~/.cache}/prd-toolkit/links/`, and
bounded by a 60-second timeout (`PRD_LINKS_TIMEOUT`); the commands never prompt.

**What `prd_links.py` refuses.** Exit 1 (`refused: <why>` on stderr, or drift on stdout): a location
that holds another PRD than the row names, a PRD linking to itself, a cited item that is not in the
upstream (nothing is written), an item of `contracts/asyncapi.yaml` (not citable across repositories),
and drift in `check` or a consumer that cites a changed item in `impact`. Exit 2: a usage or tool error
with nothing on stdout (`prd_links: <why>` on stderr), git that cannot run in any command among them, and
a refusal or failure of `impact` itself, so its exit 1 always means a consumer cites a changed item. Exit 3 (`check` and `impact` only): nothing drifted but a side was unreachable.
`check --ci` exits 0 where `check` would exit 3, after printing the unreachable line; the generated
`prd-lint` job runs it, so CI catches a break only where the other side is reachable. The deploy
pre-flight refuses to start on exit 1 and reports exit 3. `/prd-toolkit:prd-status` shows the verdict counts for
path locations and `check: not run` for a git URL.

Four lint rules (36 in all) read `links.md`, the snapshot and the records without leaving the
repository: `links-format`, `upstream-refs`, `snapshot-cited` and `change-sets`.

## Change sets

A change to a contract item that another PRD cites cannot stop at one repository. `/prd-toolkit:prd-change-set
[<CS-nnn> | <text>]` (skill `prd-toolkit:coordinating-prds`) runs it as one change set:

1. `impact` finds the consumers; you confirm the members; `prd_links.py changeset new` writes
   `docs/prd/<slug>/changes/CS-nnn.md` in the starting repository, with each member's Order, Waits for
   and Target. An unreachable consumer is never skipped.
2. Each member's PRD is edited in Order on the branch `cs-<nnn>-<slug>` (the same in every member), and
   each downstream member syncs from the edited upstream branch.
3. One approval: every member's PRD diff is shown together, and one reply approves the set. The record
   quotes it; an amendment is approved alone.
4. Each member builds in Order once its Waits for holds, through `/prd-toolkit:prd-build`, with the
   `Change-set: <prd>/CS-nnn` trailer on its commits; an upstream is deployed through `/prd-toolkit:prd-deploy
   --until <env>` first when a downstream link needs it. Its pre-flight, and `check --ci` (the
   generated `prd-lint` job), let drift between two members of the open change set through, printing
   `drift allowed by <start-prd>/CS-nnn: <line>`; other drift still refuses or fails, and a plain
   `check` still reports it.
5. A failed build, a human step without a reply or an error stops the chain. The stop is on the
   record's Status and in its Log, and a new session resumes from the record alone. A blocker in step
   2 (a member's lint or dry run) is recorded the same way, with `changeset stop`, before any approval:
   once it is fixed, step 3's one reply (`changeset approve`, no `--amendment`) approves the set and
   clears the stop, and the Log says so. No State can be set while the record has no `Approval:` line.
6. `changeset close` writes the Merge order, upstream first. Nothing is pushed, merged or opened as a
   pull request; you land each member.

The record is written only by `prd_links.py changeset`. A dry run and a build dispatch agents bound to
the session's own repository, so they run in a session started in that member's root: expect one resume
per member, each a `/prd-toolkit:prd-change-set CS-nnn` from that root. Record writes, `impact`, `sync`, `check` and
deploys run for any member from any session.

A headless run registers only `prd-toolkit:<command>` (a bare `/prd-toolkit:prd-status` is not listed, as probed in
0.7 on Claude Code 2.1.316): invoke `prd-toolkit:prd-change-set` and the other commands in that form.

## Packs

A pack tells the toolkit what kind of output a PRD describes. It is a folder with a `pack.yaml`: contract
types and their validators, target kinds, test levels, harness defaults, a vocabulary of platform words,
and optional rubric and clarify text, a grader and language tables. Two ship with the toolkit:

- **`service`** is the PRD of 0.7: an API, a database or events. It is the default, so a PRD that names no
  pack needs no edit.
- **`document`** is a Markdown document written for people (a guide, a runbook, a policy): the `outline`
  contract type, `checks` and `judged` levels, and no builder unit tests. Its checks read each document as
  CommonMark 0.31.2 after NFC normalization, a section being a level-2 heading that equals a `sections`
  entry; a PRD that wants another standard writes it in the Harness Assertions slot.

A plugin adds a pack as `prd-packs/<name>/` in its install path. A PRD names its packs in §1 (`- Pack:
<name> <X.Y.Z> (<source>)`, with `- Output language: <code>` when it differs from `language:`) and, for one
area, in a `Target:` line of `features/<area>.md`. `prd_hooks.py install` vendors each named pack, and
`service`, into `.prd-toolkit/packs/<name>/` and records each one's source in `.prd-toolkit/pack-sources.json`;
the vendored copy is then the one lint reads, and its version must equal the named one. `prd_lint.py --list-packs` lists what is installed, one `<name> <version> (<source>) — <description>` line per pack. A `Target:` line may also set an area's output language alone (`Target: output language pt-BR`), and since 0.8.12 it may end with the area's URL (`url <address>`; see Decision inbox). A pack's commands may use
`${PACK}` for its own folder. The format is `references/prd-format.md` ("Target profiles") and the manifest
is `references/contract-types.md` ("pack"). Lint adds `pack-resolves` (a profile line or pack that does
not resolve) and the warning `platform-word` (a word from the area's pack vocabulary in a requirement).

**A pack release (0.8.5).** `prd_change.py pack <prd_dir> <name> <X.Y.Z>`, run from the plugin, moves
every `Pack:` and `Target:` line that names the pack, records `pack <name> <old> → <new>; pending` as
a patch with no IDs, and leaves the tree uncommitted. Then run `prd_hooks.py install docs/prd/<slug>`
from the plugin to re-vendor the pack, and give the owner's approval with the dry-run record `no dry
run (pack version only)`. It refuses a PRD with uncommitted changes, a pack no line names, lines that
already name the version or that disagree on it, and a pack that does not resolve. `install` on an
old version ends its refusal with the `prd_change.py pack` command to run.

## Writing a pack

```
<plugin>/scripts/prd pack compare <prd A> <prd B>                          # what two PRDs share, part by part
<plugin>/scripts/prd pack check <pack dir> <prd A> <prd B>                 # the written pack against both
<plugin>/scripts/prd change pack docs/prd/<slug> <name> <X.Y.Z> --lift     # move one PRD onto it
```

A repository of a kind no pack covers is adopted with custom contract types: section 7 rows whose
Validator is a command of the PRD's own. When a second repository of that kind is adopted the same
way, `/prd-toolkit:prd-pack <PRD folder A> <PRD folder B> [<pack name>]` (skill
`prd-toolkit:authoring-packs`) writes the pack the two can share, from what their PRDs already say.

- **Compare.** `prd pack compare` reads both PRD folders and prints seven parts, Contract types (the
  custom section 7 rows), Target kinds, Levels, Harness, Standards (the `enforced` rows), Skills and
  Vocabulary (words both PRDs' requirements use, a candidate list for a person to cut), each line
  marked `both`, `A` or `B`; an item that differs prints its `A` line, then its `B` line. "The same" is
  exact equality after a cell's white space is collapsed; nothing is matched by resemblance. It writes
  nothing. It exits 0 when printed, 1 when the two PRDs share no custom contract type (there is no pack
  to write), 2 on usage or a folder that is not a PRD.
- **Propose and decide.** Both PRDs must be Approved and lint clean. The skill shows one proposal: each
  manifest item with the PRD line it comes from, each difference with both sides and a recommended
  resolution (take A's, take B's, or leave it out so each PRD keeps its own), the vocabulary candidates,
  and the to-do list. The owner decides each item; a difference is never merged into a third text, and a
  contract type one PRD lacks never goes in. Nothing is written before the owner's reply.
- **What is written,** into the plugin checkout the owner names, as `prd-packs/<name>/` on a new branch
  `pack-<name>-0.1.0` (or into a new minimal plugin, a manifest and a README, only when the owner asks for
  one, at the path they give):
  - `pack.yaml`, at `version: 0.1.0`, with the built-in packs' `toolkit` range and the decided items;
  - each validator, the command as it stands, or the repository file it runs, copied unchanged and named
    in the command through `${PACK}`;
  - `samples/<type>/bad.*`: for each contract type, a copy of a real contract file broken in one named
    way, which the validator must refuse;
  - `README.md`: where each item came from, how each sample was broken, and the to-do list, the harness
    helpers, clarify questions and skill rules a person would write, each with the files to start from.

  Nothing else: no helper code, `clarify.md`, `rubrics.md` or skill is drafted, and neither PRD is
  edited. The skill commits the pack once the check is clean, and pushes, publishes or installs nothing.
- **Check.** `prd pack check` loads the manifest with the toolkit's own loader; runs each type's
  validator on each PRD's files of the type from the PRD's root, and again on the same files from the
  pack folder (`validator fails from the pack folder: <line>` when only the second fails); runs it on
  each sample from the pack folder, which must exit non-zero (a type with no sample is a finding); and
  checks that each `target-kinds` entry names a type of the pack and each Levels command's first word is
  on PATH. One finding per line, `<file>: <what>`; exit 0 clean, 1 findings, 2 usage.
- **JSON.** Both take `--json`: `compare` prints
  `{"interface": 1, "kind": "pack.compare", "a", "b", "parts"}`, with `parts` holding the keys
  `contract-types`, `target-kinds`, `levels`, `harness`, `standards`, `skills` and `vocabulary`, each a
  list of the part's lines with their `mark`; `check` prints
  `{"interface": 1, "kind": "pack.check", "findings": [{"file", "message"}]}`. `--interface` prints `1`.
- **The lift.** Once the owner has installed the plugin (`prd lint --list-packs` lists
  `<name> 0.1.0 (<source>)`), each PRD moves onto the pack by its own `/prd-toolkit:prd-change`. The
  lift, `prd change pack … --lift` run from the plugin (`--source <source>` when two installed plugins
  hold the pack), is allowed only when the PRD names no pack, the pack declares at least one contract type (since 0.8.13:
  `pack <name> <X.Y.Z> declares no contract type; a lift moves a PRD onto a pack that declares its custom types`)
  and every contract type of the pack is a
  custom section 7 row of the PRD with the same Files glob. It writes the section 1 `Pack:` line, sets
  those rows' Validator cell to `pack`, and records the patch `pack <name> <X.Y.Z> lifted; pending`,
  leaving the tree uncommitted. Then `prd hooks install` from the plugin vendors the pack, lint must exit
  0 with the pack's validators, and the owner approves with the dry-run record
  `no dry run (pack lifted)`; the approval commit holds `.prd-toolkit/packs/<name>/` and
  `.prd-toolkit/pack-sources.json`. What the PRD produces does not change: its Levels, Harness,
  standards and skills rows stay as they are. Lint prints what it printed before, and beside it a
  `platform-word` finding for each requirement that names a word the pack keeps in its `vocabulary`. Changing the pack of a built area in any other way is a
  conversion, which a later release brings.
- A copy vendored before 0.8.12 has no `pack` command and no `--lift`; the skill runs `compare` and
  `check` from the plugin, and a lift is run with the 0.8.12 plugin's own scripts, whose `hooks install` then vendors 0.8.12 (see the changelog).
  The format is `references/contract-types.md` ("A pack written from two PRDs").

## Languages

Frontmatter `language:` (default `en`) is the language of the PRD's prose. Lint reads a language's EARS
openers, ubiquitous form and vague words from a table, `references/languages/<code>.yaml` in the toolkit
or `languages/<code>.yaml` in a pack the PRD names. `en` and `es` ship (`es` accepts `Cuando`, `Mientras`,
`Si` and `Donde`, and `El/La/Los/Las <cosa> deberá`). `en` reproduces 0.7 exactly. A `language:` with no
table is a `language-table` violation. Field labels, IDs, YAML keys and headings stay English.

## Judged cases

A test case whose `expect` has `rubric:` and `threshold:` (and optionally `runs:`, default 3) is scored by a
model against its rubric. `prd_judge.py <prd dir> <T-id> <output file>` runs the grader `runs` times; each
rubric item passes only with a quote copied from the output (compared after collapsing whitespace), and the
case passes when the median score reaches the threshold. It exits 0 on a pass, 1 on a fail and 2 when the
case could not be judged (an unknown T-id, a missing output, `claude` missing or signed out, or two bad
answers), so exit 2 is a test error, never a pass. The default grader is a headless `claude -p` with no
tools in an empty temporary directory; a pack's `grader:` command replaces it. Each run is recorded in
`.prd-judge/<T-id>.json` (git-ignored by `prd_hooks.py install`). The tester writes the test that calls
`prd_judge.py`; it never grades. Lint adds `judged-case`.

## Machine interface

A client other than Claude Code (an editor, a desktop app, a CI dashboard, another agent harness)
calls the repository's vendored scripts in `.prd-toolkit/` and reads JSON. It never links toolkit
code.

**JSON output.** `prd_lint.py`, `prd_trace.py`, `prd_status.py`, `prd_context.py`, `prd_change.py`
and `prd_gates.py` take `--json` (or `--json=1`) and print one object on stdout, `interface` and
`kind` first: `{"interface": 1, "kind": "lint", "prd": …, "version": …, "dir": …, "findings":
[{"file", "line", "rule", "severity", "message"}], "errors": N, "warnings": N}`. Exit codes are the
text mode's: `0` ok, `1` violations or refused, `2` usage or internal error. On exit 2 the document
is `{"interface": 1, "kind": …, "error": "<first stderr line>"}`, an argparse error included; any
other `--json=N` exits 2 with `unsupported interface <N>; this toolkit speaks 1`. `--interface`
prints the number alone. Within one `interface` number a field may be added, never removed or renamed.

**The change bookkeeping.** `prd_change.py` works on the PRD folder it is given, in any checkout or
worktree; it never switches branches or pushes.

```
.prd-toolkit/prd change ids next docs/prd/<slug> <FR|NFR|UJ|AC-<nnn>|T-<nnn>>
.prd-toolkit/prd change bump docs/prd/<slug> --base HEAD
.prd-toolkit/prd change record docs/prd/<slug> --base HEAD --bump <patch|minor|major> --change "<text>"
.prd-toolkit/prd change digest docs/prd/<slug>
.prd-toolkit/prd change approve docs/prd/<slug> --reply "<verbatim>" --dry-run "<record>" [--refs "<IDs>, E-nnn"]
```

- `prd_change.py ids next` prints the next free ID by `prd-format.md` decision 6, removed IDs and
  §14-only T-ids counted; a UJ has two digits.
- `prd_change.py bump` compares the folder at `--base` with the working tree and prints each changed
  item with its level, `patch`, `minor`, `major` or `needs judgment`, by the table in
  `changing-prds`' Version rule. A model (review mode) or a person decides a `needs judgment` item.
- `prd_change.py record` writes the version, `updated`, the §14 row (`<change>; pending`, so its
  Change cell ends `; pending`) and the §11 rows. It refuses a level below what the diff needs,
  and `needs-judgment` as a level; run again, it replaces its own pending row. It never changes the
  digest.
- `prd_change.py digest` prints the SHA-256 of the folder, leaving out what `record` writes and
  `.prd-review.json`.
- `prd_change.py approve` refuses unless `.prd-review.json` is ready and its digest matches, lint
  passes, the dry-run record is given (`no dry run (unit only)` for a unit-only change) and the last
  §14 row is pending, and `CLAUDE.md` has no uncommitted changes (an ignored `CLAUDE.md` is skipped). It then writes the record, sets the status `Approved`, runs `prd_block.py` and
  commits `docs(prd): approve <slug> <version>` with `Reply: "…"` in the body, and deletes the verdict.

**Review mode.** `/prd-toolkit:prd-change --review <dir>` edits nothing (only the tester's dry-run directory and
the verdict): it restates the change, runs `prd_links.py impact` when `links.md` has Consumers,
decides each `needs judgment` item, dry-runs the new and revised non-unit T-ids through `prd-tester`,
and writes `.prd-review.json` in the PRD folder: `{"interface": 1, "kind": "review", "head",
"digest", "restate", "touches", "impact", "bump": {"level", "decided"}, "dry_run", "ready",
"blockers"}`, plus an optional `"refs"` (0.8.2) that `changing-prds` step 4 sets for a change made for an
`errors.md` entry, the approval commit's `Refs:` IDs. Run it headless as `claude -p "/prd-toolkit:prd-change --review <dir>" --output-format json` with
the plugin loaded and the tools `Read`, `Grep`, `Glob`, `Bash` and `Agent`. The order a client runs: `bump`, then the review, then `record` at the level the verdict gives, then lint and trace; `record` does not change the digest, so the verdict stays valid.

**Pending decisions.** `prd_gates.py list <prd dir> [--worktrees] --json` prints every decision a
person owes, in one shape (`id`, `kind`, `title`, `question`, `evidence`, `choices`, `source`, and
since 0.8.12 `areas` and `url`, as Decision inbox says): an
approval (`approval:<branch>`), an error class (`error-class:E-nnn`), a deploy step
(`deploy-step:<run id>:<step>`), an adoption area (`adoption:<area>`, with its open `items`) and a
sign-off (`signoff:<T-id>`). `prd_gates.py answer <prd dir> <gate id> --reply "<verbatim>"
--question "<the question shown>"` passes the answer to the script that owns it (`prd_change.py
approve`, `prd_error.py confirm`, `prd_deploy.py confirm`, `prd_confirm.py answer` or `done`, the
Sign-offs row) and prints `{"interface": 1, "kind": "gates.answer", "gate", "result": {"stdout",
"exit"}}`. Every client passes `--question`, the text it showed: a gate that is gone or whose
question changed is refused, `refused: the gate changed; list again`, exit 1. The approval gate's
choices are `approve` (the default) and `changes`: `--choice changes` writes the owner's reply into
the verdict, sets `ready` to false and commits nothing, so only a new review after an edit makes the
gate pending again. An adoption area stays pending until `--choice done`. An answer to an
error-class or sign-off gate commits the owner's write itself, by path only, so other staged work
stays staged: `errors.md` as `docs(prd): confirm E-nnn` (`Refs: E-nnn`), `testing.md` as
`docs(prd): sign off <T-id>` (`Refs:` the case's requirement). When that commit fails (a hook rejects
it), `answer` exits 1 with git's error in `result.stderr`, and the write stays in the tree. Such an answer
changes the PRD folder's digest, so a pending approval gate is withdrawn until a new review. To answer
a `--worktrees` approval gate, run `answer` on that worktree's PRD folder: the gate's `path` (the
worktree) joined with the PRD's path in the repository. Beside the form,
`prd_confirm.py answer` (one item), `prd_confirm.py open` (a new answers file) and
`prd_confirm.py done` (the area finished) write the 0.7.1 answers file, under its lock.

## Decision inbox

`prd_gates.py serve` is a local page that lists every decision a person owes (the gates of
`prd_gates.py list`, across the repository's worktrees) and answers each one: an approval with its
diff, an error class, a deploy step, an adoption area and a sign-off. The session starts `wait` on
a gate before it gives you the URL, so it learns of the answer whichever client gave it.

```
.prd-toolkit/prd gates serve docs/prd/<slug> [--gate <id>] [--port N] [--no-open] [--idle-minutes N]
.prd-toolkit/prd gates wait docs/prd/<slug> <gate id> [--worktree <path>] [--timeout S]
.prd-toolkit/prd build-check docs/prd/<slug> --stale --tids <T-ids>
.prd-toolkit/prd deploy record docs/prd/<slug> --env <env> --commit <sha> --reply "<owner's words>"
```

| Command | Does | Exit codes |
|---|---|---|
| `prd_gates.py serve` | Prints `url=http://127.0.0.1:<port>/?token=<token>` as its first stdout line, opens the browser unless `--no-open` (the page opens on `--gate` when given), and serves until Ctrl-C, SIGTERM or `--idle-minutes` (default 120) without a request. With `--gate`, when an inbox for the PRD is already live, it prints `prd_gates: an inbox is already serving at <url>` and stands by: if that inbox stops before the gate is answered, it takes over at the same URL (the same port and token; it prints `url=<url>#gate=<id>` and opens no browser) and serves from then on as any `serve` does. A standby lives at most `--idle-minutes`, counted from when it began standing by | `serve` exits 3 when stopped (Ctrl-C, SIGTERM or the idle time), 1 when refused (a `--gate` that is not pending, or `prd_gates: an inbox is already serving at <url>` without `--gate`) and when a standby's gate is answered or gone (`prd_gates: <gate id> is not pending`, 5 seconds after it left the list), 2 when it cannot start (usage, a port in use, `prd_gates: cannot start the inbox: …`) or cannot take over (`prd_gates: cannot take over the inbox at port <N>: …`); a standby stopped by Ctrl-C or SIGTERM, or at the end of its `--idle-minutes`, exits 3 too; it has no Done, so it never exits 0 |
| `prd_gates.py wait` | Blocks until the gate is answered by any client and prints `{"interface": 1, "kind": "gates.outcome", "gate", "worktree", "choice", "reply", "by", "at"}` | `wait` exits 0 when answered, 1 when the gate is not pending, 3 on timeout, 2 on usage (at exit 0 `choice` is the answer's, `confirm` for a deploy step; a gate that is not pending prints `choice` null: it was answered before `wait` began with nothing logged, or the PRD changed under it) |
| `prd_build_check.py --stale` | Prints `stale <T-id> <test path>: its test case changed after the test (last changed in <sha>)` for each dispatched T-id whose test case changed after its test's last commit; a suite prompt then carries one `Rewrite: <T-id>` line for each | `--stale` exits 0 when nothing is stale, 1 when any is, 2 on a usage or tool error (which stops the dispatch) |
| `prd_hooks.py vendor` | Writes `.prd-toolkit/` as `install` does and nothing else (no hook, block or CI file); the way the repository that holds the plugin refreshes its own copy, and the one change a build's `--diff` accepts under `.prd-toolkit/` | `vendor` exits 0 and prints `vendored the toolkit into .prd-toolkit/ (version <X.Y.Z>)`; 2 from a vendored copy (`prd_hooks: vendor runs from the plugin, not from .prd-toolkit/`) or when the PRD's pack cannot be resolved |
| `prd_deploy.py record` | Records a deploy the owner did by hand: a run log marked `by: hand` and the environment's Deployed row, left uncommitted; it runs nothing and moves no status | `record` exits 0, 1 when refused (an environment not in both Environments tables, a commit not in the repository, an empty reply), 2 on usage; it prints `run=<id>` on success |

**A question on an error card (0.8.15).** An `error-class` card shows the entry's `Explanation:` first
(its `explanation` key, null when the entry has none) and the Diagnosis behind a disclosure, and offers
three answers: Confirm, Correct it to another class, and Ask a question. A question needs your words,
writes nothing to `errors.md` and commits nothing; it logs one answer line with `choice` `question`,
so the session's `wait` returns it and answers you, and the card stays until you confirm or correct.
`prd gates answer <prd_dir> error-class:E-nnn --choice question --reply '<words>'` does the same and
prints `recorded a question for error-class:E-nnn`.

The inbox page is vendored at `.prd-toolkit/gates/inbox.html`. It passes the question it showed with
every answer, so an answer to a gate that changed is refused. The page asks for a new list every 5
seconds. A reply from a button ends with ` (form)` and the answer log's `by` is `form`; an answer by
`prd_gates.py answer` has `by` `cli`.

**Each card's area and URL (0.8.12).** In `prd gates list --json`, every gate holds two more keys, after
the ones it held: `areas`, a list of area names in the PRD's area order (the empty list when it has
none), and `url`, a string or null. The inbox's card carries both, and shows directly under its title
the line `Area: <names>` (the areas joined by `, `) or `Area: none`, and, when `url` is a string, the URL
as a link that opens in a new tab.

| Gate | `areas` | `url` |
|---|---|---|
| `error-class:E-nnn` | the areas of the blocks its entry's `Touches:` names, then of the blocks that own a test case `known-failing` on it, each once | the entry's `URL:`, else the URL of its first area that has one |
| `signoff:<T-id>` | the area of the test case's file | that area's |
| `approval:<branch>` | the areas of the blocks the change touches (the verdict's `touches`) | that area's when the change touches exactly one area, else null |
| `adoption:<area>` | the area | that area's |
| `deploy-step:<run id>:<step>` | none: a run deploys the whole PRD | null |

An area's URL is the `url <address>` part of the `Target:` line of `features/<area>.md`
(`Target: url https://example.com/orders`); an entry's is its `URL:` line (see Handling errors). A
malformed address is a lint finding and is passed over, so a card never links to it; nothing fetches a
URL. The adoption card keeps `area`, a string, beside `areas`; no key is removed, renamed or changes
type, so `interface` stays 1. The text listing (`prd gates list` without `--json`) and `prd status`'s
Next part print what they printed before. A copy vendored before 0.8.12 prints neither key; run
`install` from the 0.8.12 plugin to get them (see the changelog).

**One card for an error entry (0.8.13).** An entry that is `proposed` in a commit two branches share is
`proposed` in every worktree that holds it. The inbox shows its `error-class:E-nnn` card once, in the first
worktree of its list whose PRD folder holds an entry with that ID, the same title and the same `Detected:`
value, and the answer is committed on that worktree's branch alone; the other branches get it when they
merge. `prd gates list` and `prd status` list what they listed before.

These files live in the git common directory, so every worktree of the repository shares them:

- `prd-inbox-<slug>.json` (mode 0600): the lock file of the live inbox, with its port, token and pid. A second
  `serve` for the PRD finds it live and refuses, or with `--gate` stands by behind it; a dead one is deleted.
- `prd-gates-log.jsonl`: the answer log, one line per accepted answer (an adoption's per-item answers
  excepted; only its `done` is logged). `wait` reads it, never the page.
- `prd-gates-answering/`: one marker for each answer in progress. `wait` waits while a live marker
  exists. A marker older than 15 minutes, or whose process is gone (a dead pid), is ignored and removed.
- `prd-gates-waiting/`: one marker for each running `wait`, `<key>-<pid>`, keyed as the answering marker
  is. A card whose gate no live `wait` holds says `No session is waiting on this gate. Answering it still
  records the answer.` A marker whose process is gone is removed when read; a marker has no age limit.

The skills route each decision through the inbox and fall back to the chat when `serve` cannot start; the
page is never the only route.

## Known limits (0.8.5)

- A diagram draws as inline SVG where the renderer works, in a plain browser and in an Artifact
  published as its own page; a diagram with a render error, or an SVG the diagram check refuses, is shown as its source,
  with the stderr note `prd_publish: diagram at <file>:<line> shown as source: <reason>`. Mermaid's
  journey diagrams always fall back, since they use `foreignObject`. The `Diagram source` summary is
  English on every page.
- `mermaidx` pulls an unpinned `quickjs-ng`, so a render is the same per resolution, not across time.
- On the `uv run --script` path a renderer that cannot install stops the publish rather than falling
  back; wheels exist for macOS, manylinux, musllinux, Windows. The pip route needs `mermaidx` too
  (`pip install pyyaml sqlglot openapi-spec-validator markdown-it-py mermaidx`).
- The tester guard applies pytest's option table to every harness. A non-pytest runner's name filter
  (jest `-t foo`) is read as a bare positional and refused (`prd_tester_guard: <arg> is not under a
  test root`); an option the table does not know is read as a plain flag, so a value it takes is
  checked as a positional, which errs toward refusing. `-o addopts`, `--doctest-glob`, `--confcutdir`
  and the other refused options end with `is refused after a harness command`, and an unquoted glob
  with `prd_tester_guard: unquoted glob in <arg>`.
- A SOURCES finding from `prd_build_check.py --sources` does not fail the round the first time: the
  caller sends the report back to the builder with the finding. A second one on the same round fails
  it.
- A pack release needs the plugin's `prd_change.py`, not the vendored copy, which resolves the pack
  from `.prd-toolkit/packs`, still at the old version.

## Known limits (0.8.4)

- Two branches that each change a different PRD both rewrite the parent `docs/prd/README.md` table,
  so their merge can conflict there. Rerun `prd_block.py`; never edit the table by hand.
- The README shows no requirement statuses; `/prd-status` does. Only the PRD folder's root has a
  README: `features/`, `contracts/` and the other folders have none.
- Since 0.8.4 the page's labels follow the PRD's language, with English where a language table lacks a key. (A mermaid diagram is drawn from 0.8.5: see Known limits (0.8.5).)
- The description is §2's first paragraph as written. The toolkit never drafts one itself.

## Known limits (0.8.2)

- The form cannot prove a person clicked, as in 0.7.1. The page needs the token, which only the session that
  started the inbox and the inbox file (mode 0600) hold.
- "Signing as `<owner>`" names the owner; it does not check who is at the keyboard.
- A new gate takes up to 5 seconds to appear.
- The answer log grows without bound; it is a few hundred bytes per decision.
- A sandbox that forbids a local port makes `serve` exit with `cannot start the inbox: …`; the skills then
  ask in the chat.
- An owner whose commit hooks run longer than 15 minutes gets `wait` exit 1, because its answering marker
  has expired; the session then lists the gates again.

## Known limits (0.8.1)

- `bump`'s wording rule is conservative: an AC is "reworded" only when it is equal after lowercasing,
  removing punctuation and collapsing whitespace, so most rewordings come out `needs judgment` for a
  model or a person to decide.
- Review mode's "edit nothing" is held by instruction; a headless client also limits its tools.
- `prd_gates.py answer` without `--question` refuses only a gone gate, not a changed one.
- A refusal in JSON mode (exit 1) prints its text on stderr, and stdout is empty; only exit 2 prints
  an error document.
- Inside a change set the member approvals are committed by `coordinating-prds`, not by
  `prd_change.py approve`, whose commit carries no `Change-set:` trailer.
- An approval is trusted to be the owner's, as `prd_error.py confirm` is.
- A client that narrows `Bash` to prefix rules (such as `Bash(uv run:*)`) needs the `Write` tool, or plain
  `Bash`, for review mode to write `.prd-review.json`: under prefix rules Claude Code refuses the heredoc
  the review writes it with.
- The `document` pack's parsing default (CommonMark after NFC) does not settle what text the checks compare
  (plain or source text, word boundaries, how nested blocks and list items join, inline HTML). The 0.8.1
  acceptance run's Spanish guide failed its dry-run clause on that; the rule is a spec line for a later release.

## Known limits (0.8.0)

- Judged cases are not deterministic: the median of three runs damps a flip, but a case near its threshold
  can still flip between runs, and the record shows every run.
- Each judged case costs `runs` model calls per suite run, and the runner needs Claude Code signed in (or a
  pack grader). A suite-mode tester that runs a judged level needs network access in its sandbox.
- PRD languages are `en` and `es` unless a pack adds a table; field labels stay English.
- An `es` NFR states its bound with an English unit for now (`200 ms`, `5 minutes`, not `5 minutos`):
  units move to the language table in 0.8.1.
- A headless `claude -p` run of the skills needs Bash permission rules for `echo` (every gate echoes its exit
  code), `mktemp`, `GIT_INDEX_FILE=` and `sort` (the tester's state snapshot), and `--add-dir` for the user
  temp directory (`$TMPDIR`), which the tester's snapshot writes to.
- Documents are Markdown only; another format needs a pack.
- Pack discovery reads `~/.claude/plugins/installed_plugins.json`, or the file named by the
  `PRD_PLUGINS_FILE` environment variable. A plugin loaded only with `claude --plugin-dir` is not in that
  file, so its pack is not found; point `PRD_PLUGINS_FILE` at a list that names it.

## Known limits (0.7.1)

- The form has one owner at one machine: the server is local, and the answers are trusted to be that
  owner's.
- A plain-words correction is turned into acceptance-criteria text by the session after Done, not by
  the form.
- Only adoption step 3 uses the form; other confirmations keep their commands.

## Known limits (0.7)

- A git URL location is read with your own credentials; CI without them gets exit 3, so CI catches a
  break only where the other side is reachable.
- An upstream sees a consumer's citations only through that consumer's committed snapshot.
- Only the kinds named under Links cross repositories. A non-YAML custom type and an item of
  `contracts/asyncapi.yaml` cannot be cited across.
- Every member must be cloned on the machine running the change set, and a dry run or build of a member
  runs in a session started in that member's root.
- An approval is trusted to be yours, as `prd_error.py confirm` is.
- While a change set is open, a reachable member's plain `check` reports the other member as drift
  until both land; `check --ci` lets it through while the record is open (Status not `done` or
  `abandoned`, visible from the checkout).

## Known limits (0.6)

- The strict expected-failure marker is held by instruction; the trace reads the tag, not each
  runner's syntax.
- A confirmation is trusted to be the user's, as `prd_deploy.py confirm` is.
- `recover` never marks a step done.
- `Evidence:` holding no secret or classified value is held by instruction; nothing scans it.
- Mermaid diagrams on the published page are shown as source, and the page's own labels are English. (0.8.4 changes the labels: see Known limits (0.8.4); 0.8.5 draws the diagrams: see Known limits (0.8.5).)
- The window between reading the runbook steps and hashing them is not covered (see Deploying).

## Assumption status `awaiting <who>`

An assumption row in section 12 has status `open`, `confirmed`, `corrected` or `awaiting <who>`,
where `<who>` is a named person (`awaiting Sam Rivera`; a bare `awaiting` is a violation).
`awaiting <who>` is for intent only that person can confirm. Unlike `open`, it does not block
approval and may stay while the PRD is Approved. Adoption uses it for requirements whose intent
the user cannot state.

## Changelog

Commit SHAs in entries dated before 2026-11-10 resolve in `ihistand/claude-plugins`, where the toolkit lived before 0.8.6.

- **0.8.20:** adoption reads the owner's Claude Code memory. A session's auto-memory often holds what a repository cannot show (which login publishes, the order of a release, a rule a client relies on), and adoption never looked: on 0.8.19 the eval `adopting-memory-conflict` wrote "the notes service shall return the id 1" while the owner's memory note said ids start at 0. Now `adopting-prds` builds a digest of the notes that name the repository or the area, at step 0 and step 1, and says so when there are none. The extract prompt takes it in a `<MEMORY>` slot: code that contradicts a note is an open `E-nnn` whose Diagnosis names the note and paraphrases it, a note the code does not show is a question, and a note is never a `Source:`. Bootstrap proposes marker answers and human runbook steps from notes, written only on the owner's yes; confirmation shows each requirement's notes beside its source. A note never confirms a requirement, two notes that disagree go to the owner as one question, and a note's text, a secret or a note about another project never reaches a committed file. Only the skill text changes. The lint rule count stays 41.
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.20 plugin and commit `.prd-toolkit/`: only its `VERSION` changes, since the vendored copy holds no skill, but a stale one is reported as differing from the plugin version. A PRD needs no change.

- **0.8.19:** the technical view, refined from its first use on a real PRD. Three things made `prd trd` harder to read than it should be. Section 1 was copied with its inline `[ASSUMPTION …]` markers, which are PRD bookkeeping; now Stack, Architecture, Standards and Skills leave each marker out, with the space before it, and a marker whose `]` is not on its line is copied as it is (AC-265.2). A `Source:` line with several refs was printed with its continuation lines joined by a space, so the first two refs ran together, and only the first ref was checked; now the refs are joined by `, ` and the row is `yes` at HEAD only when every ref holds (AC-266.3). Uncovered code listed the tests and the generated CI file, which sit outside every area by design and buried the files that truly have no owner; now it leaves out files under the test roots that `testing.md` names (`tests/` when it names none) and `.github/workflows/prd-toolkit.yml` and `.gitlab/prd-toolkit.yml`, while any other workflow is still listed (AC-266.4). The toolkit's own PRD is 13.0.0: a major version, because the view of a PRD with markers, multi-ref `Source:` lines, tests or a generated CI file changes; FR-265 and FR-266 are verified. The lint rule count stays 41.
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.19 plugin and commit `.prd-toolkit/`, so `.prd-toolkit/prd trd` prints the refined view. A PRD needs no change. A view you committed under 0.8.18 differs from the next one in those three places only.
- **0.8.18:** a technical view. `prd trd <prd_dir> [--out FILE]` prints one Markdown document that sets what the PRD says about how the system is built (its stack, architecture, standards and skills registries and contract types) beside what the repository holds at HEAD: each area's state, Boundary, file count and requirements, each requirement's `Source:` line checked at HEAD, and the files no area covers (see Technical view). It is an output, never part of the PRD: no gate approves it, no hook or CI job runs it, and the black-box tester never reads it; the same commit always gives the same bytes, and `--out` is refused inside the PRD folder and `.prd-toolkit/`. The aim is to learn which of its parts want to be kept by hand before any of them becomes a managed document. The `prd` launcher runs it as `prd trd`, and `prd hooks install` vendors `prd_trd.py`, so `prd --help` lists 21 commands and an unknown command's message names them. The toolkit's own PRD is 12.0.0: 11.1.0 added the area `trd` (FR-265 to FR-267), written before its code, and 12.0.0 is major because the dispatcher's command list, its help listing and the vendored file set change (FR-098, FR-119, FR-120); all six are verified. The lint rule count stays 41.
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.18 plugin and commit `.prd-toolkit/`, which then holds `prd_trd.py`, so `.prd-toolkit/prd trd` runs. A PRD needs no change. A client that parses `prd --help` or the unknown-command message sees one more command, `trd`.
- **0.8.17:** `schema-refs` no longer reads a backticked file name as a table and column. Once a PRD had `contracts/schema.sql`, a span such as `actions.parquet` beside `CREATE TABLE actions` was reported as `table actions has no column parquet`, because the rule skipped only nine file extensions; a PRD had to write such a file as a full path to get past it. The rule now also skips `parquet`, `avro`, `orc`, `ndjson`, `jsonl`, `xml`, `xlsx`, `gz`, `zip`, `html`, `log`, `toml`, `ini`, `py`, `ts` and `js`, still compared case included, so `actions.Parquet` is checked as a column (E-084, AC-183.1). Also: the toolkit's own Python 3.11 syntax guard test passes on Python 3.11, where its self-check now asserts that the parser rejects a reused f-string quote instead of expecting the 3.12 tokenizer to flag it (E-085). The toolkit's own PRD is 11.0.0: a major version, because AC-183.1 now accepts spans it used to report. The lint rule count stays 41.
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.17 plugin and commit `.prd-toolkit/`: the lint your hooks and CI run comes from the vendored copy. A PRD needs no change; one that worked around the rule with full paths may keep them.
- **0.8.16:** a change set stopped before its first approval can be approved, and the fixes since 0.8.15. A session that met a blocker in a member's step 2 lint recorded it with `changeset stop`; once it was fixed, `changeset approve` refused the owner's reply (`…, not proposed; a later approval is an --amendment`), and `--amendment` refused too (`… has no approval to amend`), so the only way on was to abandon the record and start again with new branches and a second reply. Now `approve` takes the first approval of a stopped record whose rows are all still `proposed`, and writes the Log line `<prd> stop cleared by the first approval`; a stopped record with no approval whose row is past `proposed` is refused, naming the abandon route (E-081). `changeset set state=…` is refused whenever the record has no `Approval:` line, so a stop no longer lets a row reach `approved` or `built` unapproved (E-082). The `coordinating-prds` skill records a step 2 blocker with `changeset stop`, clears it with step 3's one approval, keeps `--amendment` for a record that has an approval, and enters a stopped record with no approval at step 2 or 3 (see Change sets). Since 0.8.15, also: a `- **Runner setup.**` slot in testing.md's Harness, whose commands every generated CI job runs first (E-073); a section 5 row's files mode, `files: appended`, `none` or `changed`, as the second backticked span of its Linter command cell (FR-264, E-074); `prd error resolve --ci-run <url> --version <X.Y.Z>` for an environment or standard fix proven by a green CI run (E-075); install outside a git checkout refused before it writes (E-043); uninstall removes the toolkit's hooks where `core.hooksPath` is set (E-044), and `check` reports a vendored file the plugin no longer ships (E-045); and four lint ID fixes (E-046 to E-048, E-050). The toolkit's own PRD is 10.4.0 (10.1.0 to 10.4.0: those fixes and the change area adopted); E-081 and E-082 are in the `links` area, not adopted yet, and closed by red runs. The lint rule count stays 41.
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.16 plugin and commit `.prd-toolkit/`: the change-set fixes, the files mode and `--ci-run` run from the vendored copy. A PRD needs no change.
  - **Evals:** a new case, `change-set-stopped-before-approval`, fails on 0.8.15 and passes on 0.8.16. It was run outside `claude plugin eval`, whose sandbox stops every scaffold of `link_repo.py`, and the existing change-set cases could not run (see evals/BASELINE.md).
- **0.8.15:** an error class settled on a run, explained for the owner, and taken back when wrong. An owner confirmed a `code bug` in the decision inbox without understanding the error: the class came from a reading of the code, the card showed a Diagnosis written for someone who had read it, and the Confirm button wrote `Confirmed:` with the words "I guess, sure?" beside it, which no command could take back. Now the `handling-errors` skill ends its reproduction step in a run whose command and output the diagnosis quotes, sends a proposed entry with no run behind it (an adoption extract's) back to that step, records one that does not reproduce with `prd error propose --class unclassified`, and proposes `not a defect`, a sixth class, when the run matches the PRD (see Handling errors). `prd error propose --explanation` writes an `Explanation:` line that the inbox's `error-class` card shows first, the Diagnosis behind a disclosure, and the card gains a third answer, Ask a question, which writes and commits nothing and reaches `prd gates wait` (see Decision inbox). A reply that doubts is answered, never taken as a confirmation, and `prd error reopen` swaps a `Confirmed:` line for a `Reopened:` line that keeps it word for word, so the entry is `proposed` again; `prd error check` accepts that write and reports an edited, deleted or unmatched `Reopened:` line, and lint checks its form. The fix now starts by reproducing the confirmed entry on `HEAD` and reopens it when it no longer reproduces. The `adopting-prds` skill and its extract prompt write an apparent bug as `unclassified`, its Diagnosis marked as read from the code, not reproduced. The toolkit's own PRD is 10.0.0: the new adopted area `error-reopen` (FR-251 to FR-253) and inbox-cards FR-254, written before their code, and AC-026.2, AC-145.1, AC-146.4 and AC-067.3; a major version because lint's class list, and with it the finding of an unknown class, and the error-class card's choices change. The lint rule count stays 41.
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.15 plugin and commit `.prd-toolkit/`: `reopen`, `--explanation`, `--class unclassified` and the class `not a defect` run from the vendored copy, and on a copy vendored before 0.8.15 the skill still runs its reproduction step, keeps the explanation in the chat, and stops where a reopen or an `unclassified` record is needed, and says so. The generated CI file is unchanged, and a PRD needs no change. What a client may notice: lint's `Classification:` finding lists `not a defect` before `unclassified`, and an `error-class` gate's `choices` are `confirm`, `correct` and `question`, its card holding `explanation` before `waiting`.
  - **Evals:** three new cases, `error-reproduce-before-propose`, `error-unsure-reply-not-confirmed` and `error-reverify-before-fix`, each failing on 0.8.14 with the plugin and passing on 0.8.15; the existing `error-*`, `handling-errors-*` and `inbox-*` cases were rerun on the new text (see evals/BASELINE.md).
- **0.8.14:** a replay that proves a fix, and a close for an error no area covers. An entry closed with a line such as `T-005.3 [integration], PRD 1.0.1, fixed in 0dd4037`, and `prd error check` verified that its T-id, version and commit exist, never that the commit turned the test green. And an error in code outside every adopted Boundary could not close at all: `resolve` needs a T-id, that code has no requirement, and E-017 had stayed `confirmed` since 0.8.7 though its fix was in. Now `prd error replay` (see Handling errors) runs the entry's test through the new optional `One test` column of `testing.md` Levels (see Testing from the PRD) on the commit before the fix, where it must fail, and on the fix, where it must pass, each run in a temporary git clone it removes, so it writes nothing in the repository's git folder and also runs where that folder cannot take a new worktree, as in a sandboxed session; it prints the proof, a skip and its reason, or each finding, and with `--json` one document (`kind` `error-replay`, `interface` 1). A fourth resolution form, `fixed in <commit>, red run <test id> [<level>]`, closes a `code bug` whose fix commit changes no path an adopted area covers: `prd error resolve --red-run <test id> --level <level>` writes it only when its replay holds, and `prd error check` reads it. The `handling-errors` skill and `/prd-toolkit:prd-error` take that route (the failing test committed alone, the fix, `resolve --red-run`, `check`), the one case where the session writes a test and a fix itself, and replay every `resolve` that names a T-id before the ledger is committed. The three older forms are written, read and checked as before. Lint reports a malformed `One test` cell through `runbook-tests`. The lint rule count stays 41. The toolkit's own ledger closes E-017 and E-032 by the fourth form (E-032 was the first use of the route: the tester guard now finds a headless session's tasks folder by its session id when the hook input names no scratchpad, so the tester may read its own background run's output), E-033 with T-079.6 (the replay wrote the caller's git index when `GIT_INDEX_FILE` was set; found by review before release) and E-035 with T-079.7 (the replay made each run's tree with `git worktree add`, which a sandboxed session refuses; found by the eval runs before release). The toolkit's own PRD is 9.0.0: 8.4.0 added the area `error-replay` (UJ-07, FR-075 to FR-081), written before its code, with `format: One test column (prd-toolkit 0.8.14)` and the column on its two levels; 8.5.0 holds the fix route of E-033, a finding of its own for a One test program that cannot start, and the help catalogue's red-run form; 9.0.0, a major version because a test that relied on its tree being a linked worktree can now fail, makes each run's tree a clone (E-035); the area is verified. Conversion, which once held this number, stays in the backlog with no release (owner, 2026-11-19).
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.14 plugin and commit `.prd-toolkit/` before a ledger holds a fourth-form line: `replay`, `resolve --red-run` and `check` run from the vendored copy, and a copy vendored before 0.8.14 reports a red run as none of the three forms it knows (on such a copy the 0.8.14 skill stops before the route and before it resolves a fix that names a T-id, and says so). The generated CI file is unchanged, and no repository regenerates it. A PRD needs no change: it takes the `One test` column as a patch, with the section 14 row `format: One test column (prd-toolkit 0.8.14)`, only if it wants the replay, which skips the entries of a level without the column. What a client may notice: `prd error check` calls a line of no form `resolution is not one of the four forms`, where it said `three`.
  - **Known limits:**
    - An exit code cannot tell a test that failed from one that could not run. The second run catches a harness that cannot run in a fresh checkout. A test committed in the same commit as its fix fails on the parent for lack of its file, so the replay would call that fix proven: commit the failing test alone, before the fix.
    - The proof is per file: two entries fixed together whose tests share a file share one proof. For an entry with a T-id, a test added to the same file between the fix and the resolve can fail the second run.
    - A One test program that cannot start in a fresh clone (a path into a virtual environment, for example) is a finding, `<E-nnn>: <program> cannot start on <commit>`; give the column a command that builds what it needs, such as `uv run --project <folder> pytest -q`.
    - The replay removes its clones on SIGINT (exit 130), but SIGTERM is not handled: a replay killed that way leaves its folder under the system temporary folder and its running test behind (remove the folder). A Ctrl-C that arrives while the replay removes one run's clone is lost; press it again in the next run.
    - The test a replay runs has the environment the command was started with: git's own commands in the replay ignore `GIT_INDEX_FILE`, `GIT_DIR` and `GIT_WORK_TREE`, but a test that calls git sees them. Do not start a replay from inside a git hook.
    - `resolve --red-run=` with an empty test id is refused as `resolution is not one of the four forms`, not with the test id's own refusal.
    - A fix that lies inside a test root cannot be proven by a T-id replay (both trees get the resolving commit's test roots), and a tree older than something the `One test` command needs fails both runs: of the toolkit's own 34 resolved entries, the replay proves 23, skips 2 that are not defects and cannot prove 9 old ones for those two reasons and the per-file proof.
    - A clone has the repository's commits and none of its local configuration, its hooks or the checkouts of its other refs: a test that relied on its tree being a linked worktree of the repository does not find them.
    - E-034 is open (a confirmed `code bug`, left open for this release by the owner): the unit test `test_done_right_after_the_last_answer_is_accepted` fails now and then in a whole parallel run and passes alone, because it acts on the panel a fixed 300 ms after opening it; run its file again alone. The red-run route cannot close it as written: the faulty test passes when run alone, so it has no red run to give.
    - No replay runs in CI, and an agent that skips the skill's replay step is not caught for an entry with a T-id; for the fourth form `resolve --red-run` itself replays, but a red run typed into `errors.md` by hand is never replayed and passes `check`.
    - E-036 (a confirmed `invalid requirement`) and E-037 (a confirmed `code bug`) are open, found by the final review and left open for this release by the owner: with `GIT_INDEX_FILE`, `GIT_DIR` or `GIT_WORK_TREE` set, a test that calls git can write the repository the replay was started in; and a test that leaves a folder it took the write permission from makes the replay leave its folder behind with no message.
    - A session's Bash call that times out may end the replay the way SIGTERM does. A malformed `One test` cell reads as no `One test` command, and a `Test roots:` entry with a leading `./` makes a T-id replay report `is cited by no test`.
  - **Evals:**
    - `claude plugin eval ./prd-toolkit --model sonnet --scaffold`, Claude Code 2.1.330, 2026-11-21, one run each (see `evals/BASELINE.md`), 8 cases: the two new cases, `error-uncovered-code-red-run` (an error in code no adopted area covers is fixed test first and resolved with `--red-run`, never through `/prd-toolkit:prd-build`) and `error-replay-finding-not-committed` (replay findings after `resolve` leave the ledger uncommitted and the entry `confirmed`), and every existing case of `handling-errors`, the one skill whose text changed. All 8 score 1.00 with the plugin; the two new cases score 0.33 and 0.50 without it. The first run of the two new cases found E-035: in the runner's sandbox the replay could not add its worktree, and both sessions kept the entry `confirmed`. They were rerun once on the fix, after three graders of the first case that read a commit hook's log, which the runner never wrote, were rewritten to read the trace.
- **0.8.13:** fixes for the open entries of the toolkit's own error ledger; no new command, skill or lint rule. Nine entries are fixed, each recorded in `errors.md`, classed by the owner and built from a test that failed first, and one is closed as not a defect. The `prd` launcher asks uv for a system Python first (`uv python find --system ">=3.11"`) and runs on the path it prints, so a `.venv` in the working directory whose interpreter cannot be read no longer stops every `prd` command, as it did in a sandboxed session (E-022); when uv finds none it runs on `>=3.11` as before. Where `core.hooksPath` is set, `prd hooks install` rewrites a hook that is the toolkit's own, so `prd hooks check` no longer calls it stale after install's own instruction was followed (E-024); a hook of your own is left as it is, with the line to add. The decision inbox shows an error entry's `error-class` card once, in the first worktree whose PRD folder holds the entry, so one answer is one commit and the other branches get it when they merge (E-023). `prd context --area` prints the text a features file gives before its first block as a part `Area notes`, directly before `Requirements`, in the text pack and in `--json`, so the builder is given the definitions its criteria use (E-028); a features file with no such text gives the pack it gave before, byte for byte. `prd change pack … --lift` refuses a pack that declares no contract type, and the PRD and the `changing-prds` skill now say what a lift adds to lint's output: a `platform-word` finding for each requirement that names a word of the pack's `vocabulary` (E-030). `prd help` refuses a catalogue file that is there and cannot be read with the line `prd_help: <path>: cannot read: <message>` and exit 2, where it printed a traceback (E-020). `prd status`'s Next part takes a section 13 question without the white space at its ends, so a line that ends in spaces no longer gets a second full stop (E-021). The build check (`prd build-check --diff`) calls a changed file a tester's test only when it lies under a test root of `testing.md` (`tests` when it names none), so a build can change a file outside the roots that holds `@prd T-` text for another PRD (E-031). The six deploy eval scaffolds and the scaffold of `review-edits-nothing` build their start states, so those seven cases run again (E-019). E-029 is closed as not a defect: `prd pack check` already reports a validator that cannot be found or run from the pack folder, on its sample's path. The toolkit's own PRD is 8.3.1: 8.0.0, a major version because the Next part's line for such a question changed, holds the fixes for E-020, E-021 and E-030; 8.1.0 added the areas `launcher`, `hook-shims`, `inbox-cards` and `context-notes` (FR-069 to FR-072), 8.2.0 `eval-scaffolds` (FR-073) and 8.3.0 `tester-paths` (FR-074), each a small area of one module whose requirement was written before its code, beside older code that is not adopted yet; all six are verified. The lint rule count stays 41. Conversion, planned for this number, moves to 0.8.14 (owner, 2026-11-17).
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.13 plugin and commit `.prd-toolkit/`: the launcher, `hooks check`, the context pack, the inbox, the build check, help and status run from the vendored copy, so a repository gets those fixes only then; the lift and `hooks install` run from the plugin. The generated CI file is unchanged, and a PRD needs no change. What a client or a person may notice: `prd context --area … --json` holds one more entry in `parts`, titled `Area notes`, before the first `Requirements` entry, for an area whose features file has text before its first block (`interface` stays 1); `prd status` prints an open question without the white space at its ends; and where `core.hooksPath` is set, `install` now writes the toolkit's own hooks in that folder (a file whose second line starts `# prd-toolkit hook`), where it printed a line to replace by hand.
  - **Known limits:**
    - E-017 stays open: its test was fixed in 0.8.7, and the entry waits for a close for an error outside every adopted Boundary, which a later release brings (resolved in 0.8.14, by a red run).
    - E-032 is open and not yet classed: in two builds the tester guard refused the tester's Read of its own background run's output file, which the tester's rule 7 allows. The tester ran the harness in the foreground instead, and the results stand. It is not reproduced outside those sessions (fixed in 0.8.14).
    - Only the inbox shows an entry's card once: `prd gates list --worktrees` still lists its `error-class` gate in every worktree that holds the entry, and `prd status` prints what it printed before.
    - The build check no longer guards a tester's test kept outside the test roots `testing.md` names; keep every tester's test under a root, where trace reads its citations.
    - Each new area adopts one module. The code around them (the areas `trace-and-hooks`, `gates`, `context`, `build-check` and `change`) is still not adopted.
  - **Evals:**
    - `claude plugin eval ./prd-toolkit --model sonnet --scaffold`, Claude Code 2.1.327, 2026-11-18, one run each (see `evals/BASELINE.md`), 14 cases: the six deploy cases and `review-edits-nothing`, which E-019 had stopped, `deploy-confirms-named-steps`, and the six cases of `changing-prds`, the one skill whose text changed. 13 score 1.00 with the plugin; `changing-hands-off-to-change-set` scores 0.75, as in 0.8.12, for one grader the baseline names. Two eval files still used the bare command names of before 0.8.7 and had never run since: a grader of `deploy-by-hand-records` and the prompt of `review-edits-nothing`. Both were corrected against the first run's trace, and each case then scored 1.00. No case grades the launcher, the inbox or the part `Area notes`; the PRD's own integration tests cover them, and the full suite passes (`scripts/ci-local.sh`).
- **0.8.12:** a pack written from two adopted PRDs, and cards that say where. A repository of a kind no pack covers could be adopted with custom contract types, but the second repository of that kind wrote them all again, and writing a pack was undocumented hand work. Now `/prd-toolkit:prd-pack`, the new skill `authoring-packs`, writes one from two adopted PRDs (see Writing a pack): `prd pack compare` (the new script `prd_pack.py`) prints what the two share, each line marked `both`, `A` or `B`; the skill proposes each item with the PRD line it comes from and each difference with both sides; the owner decides; and the skill writes `pack.yaml`, the validators the PRDs already run, one bad sample per type and a README with a to-do list into the plugin the owner names, checks it with `prd pack check` and commits it on a new branch, pushing and installing nothing. Each PRD then moves onto the pack with `prd change pack … --lift`, a patch the owner approves: the pack declares what the PRD already declared, so nothing it produces changes. And every card in the decision inbox now names its areas and links to where the trouble is (see Decision inbox): `prd gates list --json` gives every gate `areas` and `url`; an error entry may hold a `URL:` line, written by `prd error new --url` or set later by `prd error url`; an area's `Target:` line may end with a `url` part. The text listing of `prd gates list`, `prd status`'s Next part and `interface` 1 are unchanged. A standards row is no longer run on a file under `.prd-toolkit/`, in the pre-commit hook or in the generated CI job, so a commit that re-vendors the toolkit is no longer refused by a repository's own linter (E-025). Also fixed while building: the approval of a lift commits the vendored pack (E-026), and `prd pack check` runs each validator a second time from the pack folder, so a validator that only works from the PRD's root no longer passes (E-027). The toolkit's own PRD is 7.3.0: 7.1.0 added the areas `pack-authoring` (UJ-05, FR-057 to FR-061) and `card-context` (UJ-06, FR-062 to FR-067), each written before its code, and `standards-run` (FR-068) for E-025; 7.2.0 and 7.3.0 closed the gaps found while building them; all three are verified. The lint rule count stays 41. See the [design spec](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.12-pack-authoring-design.md).
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Then re-run `<plugin>/scripts/prd hooks install docs/prd/<slug>` from the 0.8.12 plugin and commit `.prd-toolkit/`; a repository with a generated CI file also re-runs `<plugin>/scripts/prd hooks ci --github --force docs/prd/<slug>` (or `--gitlab`) and commits it with them, since `prd hooks check --ci` reports a CI file an earlier release wrote as stale when it differs from what `ci` writes now (a `standards-<n>` job does). The vendored `.prd-toolkit/prd hooks install` installs the hooks only. A copy vendored before 0.8.12 lacks `prd_pack.py`, `prd error new --url`, `prd error url`, the `url` part of a `Target:` line (its lint refuses one) and `areas` and `url` on its gates; the 0.8.12 skills say so and work around it (an entry is recorded without its URL, which is named in the report; the areas are named from `Touches:`). Lint's `pack-resolves` message for a malformed `Target:` line changed with the `url` part (it now reads `Target: must be one or more of pack <name> <X.Y.Z> (<source>), output language <code> and url <address>, comma-separated, in that order`): a client or CI step that matches the earlier text needs the new one. A PRD needs no change.
  - **Known limits:**
    - A pack's samples prove little when its validator reads the repository: run from the pack folder, such a validator refuses every sample for missing files as well as for its named break, and `prd pack check` cannot tell the two apart. The second run from the pack folder (E-027) does catch a validator that cannot work there on the PRD's own files.
    - `prd change bump` answers `needs judgment` for a lift (the `Pack:` line and the `pack` Validator cells), though `prd change pack … --lift` records a patch.
    - A change that only adds an area's `Target:` line shows no area on its approval card (`"areas": []`, `"url": null`): a card's areas come from the blocks a change touches, and such a change touches none.
    - The vocabulary candidates of `prd pack compare` are mostly ordinary words; every one is a candidate for a person to cut.
    - No harness helper, clarify file or skill is drafted for a pack, by design: the README's to-do list names them and the files to start from.
    - After a lift each repository keeps its own validator scripts, now unused; nothing removes them.
    - A lift checks only the contract types a pack declares, so it accepts a pack that declares none, and a pack that holds vocabulary words adds a `platform-word` finding, after a lift, for each requirement that names one: for those two packs "nothing it produces changes" does not hold (E-030, open in 0.8.12; fixed in 0.8.13, which refuses the first pack and states the findings of the second). Lift only onto a pack written from the PRD's own custom types, and expect the new findings where its vocabulary is not empty.
    - The implement context pack leaves out the definitions a features file gives before its first block (E-028, open in 0.8.12; fixed in 0.8.13). `prd pack check` reports a validator that cannot be found or run from the pack folder on its sample's path, not on the PRD's (E-029, open: a confirmed spec gap whose diagnosis is "not a defect", left as it is). E-017 and E-019 to E-024 stay open (0.8.13 fixes E-019 to E-024).
  - **Evals and proof:**
    - `claude plugin eval ./prd-toolkit --model sonnet --scaffold`, Claude Code 2.1.325, 2026-11-16, one run each (see `evals/BASELINE.md`), 29 cases: the four new `pack-*` cases and `error-records-the-url`, the fourteen existing cases of the skills whose text changed, and the ten cases E-022 stopped in 0.8.11. 26 score 1.00 with the plugin; `pack-proposal-names-its-sources` scores 0.90 (after four of its graders were widened against the trace), `authoring-proposes-pack` 0.83 and `changing-hands-off-to-change-set` 0.75, each for one grader the baseline names. E-022 did not recur, and stays open. No case grades `prd pack check` on a written pack, the pack's commit or the lift.
    - Proof (see the [acceptance record](../docs/superpowers/plans/2026-11-15-prd-toolkit-0.8.12-acceptance.md)): two static web sites hosted on the same platform, neither with a PRD at the start. One area of each was adopted with two custom contract types; `/prd-toolkit:prd-pack` compared the two PRDs, the owner decided every item, and the pack was written into a new minimal plugin with `prd pack check` exit 0; both PRDs were lifted onto it with lint clean and the integration suites as before. An approval card showed its area and the area's `Target:` URL, and an error-class card the entry's own `URL:`.
- **0.8.11:** best-practice sources, `practices.md` and `/prd-toolkit:prd-practices`. The standards and skills registries were filled only from what was already on the machine: linter configurations in the repository and the skills a session happened to list. A platform's good practice that no installed linter enforces never reached the PRD, so the builder never saw it. Now a PRD folder may hold `practices.md` (see Practices): the sources, each read and approved by the owner, and the practices taken from them, each one checkable sentence. The new skill `sourcing-practices`, run as `/prd-toolkit:prd-practices`, proposes sources, practices, standards rows and skills, quotes the passage behind each practice, reports any instruction it finds inside a source and follows none, and lands everything as one PRD change the owner approves; it installs a plugin only after that approval and only from a marketplace already added, and writes a skill into the repository only from approved sources. `prd practices` lists them, as text or JSON; `prd change ids next` takes `S` and `P`; the builder's implement pack carries the practices that apply and the builder reports on each; a pack may list `sources`. Lint has a 41st rule, `practices`, and the help catalogue has 48 entries. A PRD without `practices.md` lints, builds and reports as before, except that `--list-rules` prints 41 rules. The toolkit's own PRD is 7.0.0, a major version: two of its test cases name every lint rule line by line, and the new rule changes what they expect; the new area `practices` (UJ-04, FR-048 to FR-056) is verified. See the [design spec](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.11-practices-design.md).
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). A repository gets the `practices` command and rule when `<plugin>/scripts/prd hooks install docs/prd/<slug>` is next run from the 0.8.11 plugin; commit `.prd-toolkit/`. The vendored `.prd-toolkit/prd hooks install` installs the hooks only and does not bring them. Until then the 0.8.11 skill stops on that repository and says so. A PRD needs no change: `practices.md` appears only when `/prd-toolkit:prd-practices` writes it. No hook, CI file or managed block changes.
  - **Known limits:**
    - `prd` exits 2 with uv's `Failed to inspect Python interpreter from virtual environment at .venv/bin/python` when the working directory holds a `.venv` whose interpreter cannot be read, as in a sandboxed session whose `.venv` links to a Python outside what the sandbox may read (E-022, open; not new in this release; fixed in 0.8.13).
    - Every `P-nn: not followed` line stops a build as a question for the caller.
    - A plugin in a marketplace that is not added gets no skills row: the command prints the commands for the owner, and the row comes in a later change.
    - An inbox answer given while several worktrees hold the PRD is committed in each (E-023), and with `core.hooksPath` set `hooks check` can report a hook stale after `hooks install`'s instruction is followed (E-024); both are open, from a repository on 0.8.10 (both fixed in 0.8.13).
  - **Evals and proof:**
    - `claude plugin eval ./prd-toolkit --model sonnet --scaffold`, Claude Code 2.1.325, 2026-11-15, one run each (see `evals/BASELINE.md`): the six new `practices-*` cases score 1.00 with the plugin against 0.50 to 0.88 without, after three of their graders were corrected against the traces; eleven existing cases of the skills whose text changed ran, all 1.00. Fourteen existing cases and the new `builder-reports-practices` could not run: in the eval sandbox the launcher fails on the scaffold's `.venv` (E-022), and the same case fails the same way on 0.8.10. No eval exercises a real marketplace listing or install.
    - Proof, in a scratch repository (see the [acceptance record](../docs/superpowers/plans/2026-11-15-prd-toolkit-0.8.11-acceptance.md)): the command proposed one source and three practices from a file in the repository and wrote nothing; after the owner's decision it wrote `practices.md` as a minor PRD change and stopped at the approval gate; and a build of one requirement then showed `P-01: followed`, `P-02: followed` and `P-03: followed` in the builder's report.
- **0.8.10:** a Next part in `prd status`. The report said where every requirement stands and left the reader to work out the next move; a person and a client could each derive a different one. Now the report starts with the part Next (see Status): an ordered list of what the PRD needs, each item one sentence with the command that does it. Broken things come first (lint and trace findings, a stopped deploy run, an open error), then what waits on the owner (a gate, a question, a draft), then the work, furthest along first (deploy, verify, build, adopt); when nothing matches, one item says nothing waits. With `--json` the Next items come first in `items`, each with `kind`, `ids`, `area`, `command` and `waits_on` beside `part`, `id` and `text`; `interface` stays 1, since fields are added and none is removed or renamed. One thing changes for a reader of today's output: the Header is no longer the first part of the text or the first item of the JSON document, so a client that took `items[0]` as the Header selects it by `part`. Every other part is byte for byte what it was. The toolkit's own PRD is 6.4.0, with the new area `status-next` (UJ-03, FR-040 to FR-047) verified. See the [design spec](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.10-next-part-design.md).
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). A repository gets the Next part when `<plugin>/scripts/prd hooks install docs/prd/<slug>` is next run from the 0.8.10 plugin; commit `.prd-toolkit/`. The vendored `.prd-toolkit/prd hooks install` installs the hooks only and does not bring it. Until then its report has no Next part and is otherwise as before. No hook, CI file or skill line changes.
  - **Known limits:** a section 13 question whose line ends in spaces is printed with those spaces and a second full stop (`An open question waits: Which month?   .`) (E-021, open; fixed in 0.8.13). `prd status` now runs the PRD's section 7 validator commands, through lint, so a slow validator slows the report.
  - **Evals:** the eval suite was not rerun. The only text that changed is the description and one step of the `/prd-toolkit:prd-status` command, which now name the Next part and the report's parts, and no eval case runs that command. The 0.8.8 baseline in `evals/BASELINE.md` stands.
- **0.8.9:** a help catalogue, `prd help`. The meaning of a PRD's fields and of a lint finding was only in `references/prd-format.md` and in the rules' code, so a person had to know where to look and a client had to keep its own copy. Now `prd help` prints it (see Help): the index with no option, one field with `--key`, one lint rule with `--rule`, and the whole catalogue as one JSON document with `--json`, which a client reads once. The catalogue, `references/help.yaml`, has 43 entries, one per field of the PRD grammar, each with what it is, why it is there, its formatting rules and the lint rules that check it; and each of the 40 lint rules now carries a description, what it checks and how to clear its finding. The setting `PRD_HELP_FILE` names another catalogue file. Nothing existing changes: lint prints no description, `--list-rules`, the finding lines and every `--json` document are byte for byte what they were, and `interface` stays 1. The toolkit's own PRD is 6.3.0, with the new area `help` (UJ-02, FR-033 to FR-039) verified. See the [design spec](../docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.9-help-catalogue-design.md).
  - **Upgrade:** update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). A repository gets the command when `<plugin>/scripts/prd hooks install docs/prd/<slug>` is next run from the 0.8.9 plugin, which vendors `prd_help.py` and `help.yaml`; commit `.prd-toolkit/`. The vendored `.prd-toolkit/prd hooks install` installs the hooks only and does not bring it. Until then its launcher answers `prd help` with `prd: unknown command 'help'` and exit 2, and everything else works as before. No hook, CI file or skill line changes.
  - **Known limits:** when `PRD_HELP_FILE` names a file that exists and cannot be read (no read permission), `prd help` prints a Python traceback and exits 1, with no `--json` error document, where it should refuse with exit 2 (E-020, open; fixed in 0.8.13). The shipped catalogue is not affected.
  - **Evals:** the eval suite was not rerun: no skill, command or agent text changed. The 0.8.8 baseline in `evals/BASELINE.md` stands, E-019 included.
- **0.8.8:** one `prd` command, and no uv environment per clone. `uv run --script` keeps one cached environment per script path, so every clone and worktree that vendors the toolkit added environments of its own on each hook run, CI job and skill command ([issue #2](https://github.com/PRDAnvil/prd-toolkit/issues/2)). Now one launcher, `<scripts>/prd <command>`, runs every script (see The prd command), and every hook shim, generated CI line, skill, command and agent line, and the README's vendored-copy examples, run it; uv keeps one environment per requirements list, shared by every clone and worktree. The scripts keep their uv headers and still run by their file. The toolkit's own PRD is 6.2.3. See the [design spec](../docs/superpowers/specs/2026-11-14-prd-toolkit-0.8.8-invocation-design.md).
  - **Upgrade:**
    - Update the plugin (`claude plugin marketplace update prdanvil`, `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`). Once per repository, run from the 0.8.8 plugin `<plugin>/scripts/prd hooks install docs/prd/<slug>` and then, when a generated CI file exists, `<plugin>/scripts/prd hooks ci --github --force docs/prd/<slug>` (or `--gitlab`), where `<plugin>` is the plugin's install path, `~/.claude/plugins/cache/prdanvil/prd-toolkit/0.8.8`; and commit `.prd-toolkit/`, the CI file, `CLAUDE.md` and the READMEs in one commit. Either step alone fails CI: `install` alone leaves the workflow stale, and `ci` is refused until the vendored copy is 0.8.8.
    - In every other clone, after pulling: `.prd-toolkit/prd hooks install docs/prd/<slug>`. Worktrees share their clone's hooks. Until then the old hooks keep working, and keep adding environments.
    - A hook under `core.hooksPath`, or a hook file of your own: replace its old `uv run --script … prd_git_hook.py` line with the line `install` prints; do not add the new line beside it.
    - Until a repository is upgraded, the 0.8.8 skills stop on it and tell the user to run `prd_hooks.py install docs/prd/<slug>` from the plugin (the skills' wording; type it as in the first Upgrade bullet).
    - A branch whose `.prd-toolkit/` predates 0.8.8 prints `prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped` and runs no hook checks until it merges the upgraded copy.
    - Permission rules that allow `Bash(uv run:*)` or name `.prd-toolkit/prd_<x>.py` no longer match the toolkit's commands: allow `.prd-toolkit/prd` and the plugin's `scripts/prd`.
    - The environments already in uv's cache (`uv cache dir`, folder `environments-v2`) can be deleted at any time; uv rebuilds what it needs.
  - **Known limits:**
    - A PRD that uses the `document` pack still adds one uv environment per clone on each lint: the pack's validator runs by its file. Fixed with the next pack version.
    - Judged tests written before 0.8.8 call `uv run --script .prd-toolkit/prd_judge.py` and keep one environment per clone until they are rewritten.
    - A git hook under `core.hooksPath` that carries the toolkit's marker (a shim copied there by hand) is reported stale by `check`, and `install` cannot rewrite it: replace its content with the shim from the plugin's `templates/hooks/<hook>`, with `{{hook}}` and `{{prd}}` filled in, or run `install` in a clone without `core.hooksPath` and copy the shim it writes in `.git/hooks/`.
    - In a repository with several PRDs, `install` and `check` run for a second PRD report the one CI file as stale; it belongs to the PRD it was generated for.
    - A launcher reached through a symbolic link does not find its files; call it by its real path.
  - **Evals and proof:**
    - `claude plugin eval ./prd-toolkit --model sonnet --scaffold`, Claude Code 2.1.325, 2026-11-14 (see `evals/BASELINE.md`): first run of all 59 cases, one run each: 46 passed, overall score 0.85, mean delta +0.37 over the no-plugin arm; seven did not run (E-019, below); two publish cases failed for a real reason, fixed before release (below); four scored below 1.00. Reruns at three runs each on the fixed tree: five of those six score 1.00 in every run, and `changing-hands-off-to-change-set` scores 0.75, as it does on 0.8.7. So 51 of the 59 cases pass, 7 cannot run (E-019) and 1 fails as it did on 0.8.7; no case that 0.8.8 changed for the worse remains. The seven that cannot run (E-019): their scaffolds fail their own clean-tree check, as they have since 0.8.4, so the six deploy cases and `review-edits-nothing` did not run, and no eval exercised the deploy skill's command lines in this release. The two publish cases: `prd publish`, run from the plugin in a repository whose `pyproject.toml` sets `[tool.uv] exclude-newer`, could not resolve its requirements; the launcher now reads uv's settings from its own directory, as `uv run --script` read them from the script's.
    - Proof, in a scratch repository with its own uv cache and a fresh uv-managed Python 3.13: three checkouts (the repository, a clone and a worktree of the clone), with hooked commits and `lint`, `status` and `trace` in each, left one environment in the cache for all of them (beside the one that `uv run --script prd_hooks.py install` made for the plugin's own script); the same three checkouts with `uv run --script .prd-toolkit/prd_lint.py` added three more, one per checkout.
- **0.8.7:** fixes and full command names; no feature. Current Claude Code lists a plugin's commands only under the plugin's name, so a bare `/prd-build` is "Unknown command": every template, skill, command, agent and script message now names the commands in full (`/prd-toolkit:prd-build`, `/prd-toolkit:prd-error`, …), including the managed `CLAUDE.md` block and the `docs/prd/README.md` and `docs/prd/<slug>/README.md` blocks that `prd_block.py` writes. The `lint-structure` fixes from its adoption: `sections` names an unnumbered heading as it is, not `## None.` (E-009); `vague-word` skips code spans in acceptance criteria (E-010); the placeholder, marker, assumption and glossary rules skip hidden files (E-011); a frontmatter key missing from `prd.md` is reported at the frontmatter, not a body line (E-012); an empty Test roots list is reported wherever a marker sits on the Layout line (E-013); a repeated section or Harness slot is reported as a duplicate, not as out of order (E-014); an empty section 13 fails `open-questions-empty` on an Approved PRD (E-015); the `adoption.md` header finding names the header's line (E-016). The toolkit's own test `test_validator_fails_defect` runs the document pack's validator with `--quiet`, as the pack does, so uv's `Installed 1 package` line no longer breaks it (E-017). The toolkit's own PRD is 6.2.2. Best-practice sources move to 0.8.8 and conversion to 0.8.9. See the [plan](../docs/superpowers/plans/2026-11-11-prd-toolkit-0.8.7.md).
  - **Upgrade:** run `claude plugin marketplace update prdanvil` and `claude plugin update prd-toolkit@prdanvil` at each scope it is installed at, then `/reload-plugins`. A repository that vendors the toolkit keeps the old, bare command names in its `CLAUDE.md` block and its PRD READMEs until it runs `uv run --script <plugin>/scripts/prd_hooks.py install docs/prd/<slug>` from 0.8.7 and commits `.prd-toolkit/` with the refreshed blocks; until then its own checks stay green, because they read the vendored templates.
- **0.8.6:** prd-toolkit moved, with its history, from `ihistand/claude-plugins` to its own public repository, [PRDAnvil/prd-toolkit](https://github.com/PRDAnvil/prd-toolkit), and its own marketplace, `prdanvil`. It is MIT-licensed: `LICENSE` ships in the plugin, and `prd_hooks.py install` and `vendor` copy it into `.prd-toolkit/LICENSE`. Nothing else changes in the scripts or skills. The toolkit's own PRD is 6.2.1. See the [plan](../docs/superpowers/plans/2026-11-10-prd-toolkit-move-to-prdanvil.md).
  - **Upgrade:** run `claude plugin uninstall prd-toolkit@ihistand` at each scope it is installed at, then `/plugin marketplace add PRDAnvil/prd-toolkit` and `/plugin install prd-toolkit@prdanvil`, then `/reload-plugins`. The plugin's install path becomes `~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/`. In each repository with a vendored copy, re-run `install` from that path at its next upgrade; it writes the new HOMEPAGE and the LICENSE.
- **0.8.5:** The deploy, pack and check fixes from the first private-pack loop, the published page's diagrams, and a stricter tester guard. See the [design spec](../docs/superpowers/specs/2026-11-08-prd-toolkit-0.8.5-design.md).
  - Item 1: `prd_deploy.py confirm` takes repeated `--step N --reply TEXT` pairs, one record per step, all or nothing; the skill adds a later step only when the owner's reply names it.
  - Item 2: `prd_error.py new` may record an entry while a run is stopped; it stays uncommitted through `resume` and the close commits it.
  - Item 3: a `Timeout` column in `testing.md` Levels bounds a `tests` step's level; `--timeout` still wins; a pack level's `timeout` is copied into it.
  - Item 4: a `Branch` column in `operations.md` Environments; a run's finish and `check` print `prd_deploy: the close is on <current>, not <branch>; push the close commit to <branch> too`.
  - Item 5: a Check may be ``matches `<pattern>` `` (a full-line Python regular expression).
  - Item 6: `prd_change.py pack <prd_dir> <name> <X.Y.Z>` moves a pack release without a hand-made patch, then `prd_hooks.py install` and the approval with the dry-run record `no dry run (pack version only)`.
  - Item 7: `prd_context.py --for implement` judges a `Source:` by the cited line: `MOVED: line <L> is now line <M>` is not stale (the close refreshes the line), `STALE: the cited line's text is gone` or `appears <N> times` is; the exit counts only the blocks asked for, and a block pulled in through `Traces:` prints `(pulled in; not counted)`. `--json` keeps `stale` as every stale block and adds `counted` (the stale blocks the exit counts) and `moved`.
  - Item 8: `prd_build_check.py --diff <base>..<head> --sources <file>` checks each builder SOURCES line against the round's hunks; the caller sends a finding back to the builder, and the round is not failed for it.
  - Item 9: the published page draws mermaid as inline SVG from the pinned `mermaidx==0.11.3`, each diagram falling back to its source with `prd_publish: diagram at <file>:<line> shown as source: <reason>`; publish the page as its own Artifact.
  - Item 10: the tester guard checks every harness argument: a bare positional or path under a test root, `--pyargs`, `--doctest-modules`, `--doctest-glob`, `--rootdir`, `--confcutdir`, `-p <plugin>` and `-o addopts` refused, and an unquoted glob refused.
  - Item 11: `pytest-xdist` and `-n auto` for the toolkit's own suite.
  - Item A: a moved `Status:` line is a `patch` bump item that §14's IDs cell names. Item B: a new or removed block's ACs and T-ids are named in §14's IDs cell.
  - The toolkit's own PRD is at 6.0.0 (approved b99cfac). 5.2.0 (approved f4468b0) added `lint-cli` FR-016 (lint reports a `testing.md` Levels `Timeout` cell that is not a whole number of seconds of at least 1: `runbook-tests`), FR-017 (an `operations.md` Environments `Branch` cell that `git check-ref-format --branch` refuses: `runbook-env`) and FR-018 (a runbook Check whose `matches` pattern does not compile or that holds both `prints` and `matches`: `runbook-steps`); 6.0.0 changes FR-010 (rebuilt and verified): `prd_publish.py`'s missing-package hint now ends `pip install pyyaml sqlglot openapi-spec-validator markdown-it-py mermaidx`.
  - Upgrading from 0.8.4: re-run `prd_hooks.py install docs/prd/<slug>` from the plugin, which vendors the new scripts. Every new column and form is optional, so no PRD changes. A pack release now ends with `prd_change.py pack`.
  - Proven on 2026-11-09:
    - CI passed all five jobs on PR #25 at `eed2d3f` (run 42708030265). `test-unit` took 9 min 59 s, against 21 min on PR #22 before item 11. `scripts/ci-local.sh origin/main` with an empty HOME passed all five at the same commit: 3484 unit tests passed, 1 skipped, and 58 integration tests passed. The new Python 3.11 compile check is among them; it caught a 3.11 `SyntaxError` in `deploy.py` before the release.
    - Items 1–5, in one `/prd-deploy` run of a scratch repository:
      - one `confirm` answered steps 2, 3 and 4, and the log records 3 and 4 with `"ahead": true`;
      - an uncommitted mid-run `errors.md` entry passed `resume`, and the close commit carried it;
      - a `matches` Check passed;
      - a 2 s level Timeout logged `timed out after 2 s (the smoke level's Timeout)`;
      - the branch note printed at the finish and from `check`, which exited 0.
    - Item 6: in a scratch repository with a private pack, `prd_change.py pack` moved it 0.1.0 → 0.1.1, then `install` and the approval ran. The approval commit holds the re-vendored `pack.yaml` and the §14 row `pack notes-pack 0.1.0 → 0.1.1; no dry run (pack version only)`, and lint is clean.
    - Items 7 and 8 ran in this release's own `/prd-build` rounds: `lint-cli` FR-016..FR-018, and FR-010 for PRD 6.0.0.
    - Item 9: `/prd-publish` of PRD 6.0.0 drew both diagrams as inline SVG, Overview and Technical, in plain Chrome and in the page's own private Artifact.
    - Item 10, proven live after the merge: a real `prd-tester` on the installed 0.8.5 ran the integration harness command with spec 11's examples added. The guard refused:
      - a bare `scripts`, `..` and `-c ../pyproject.toml`, each with `prd_tester_guard: <arg> is not under a test root`;
      - `--doctest-modules`, `--pyargs prdlint`, `-p pytest_randomly` and `--rootdir=..`, each with `prd_tester_guard: <option> is refused after a harness command`;
      - an unquoted `-k T-015*`, with `prd_tester_guard: unquoted glob in T-015*`.

      The guard let through a quoted `-k`, `-p no:cacheprovider` and `--tb=short`, and the tester's T-015.1 passed. A bare `scripts` argument ran under the 0.8.4 guard.
- **0.8.4:** A README for each PRD folder, an Overview tab on the published page, and ten fixes from the 0.8.3 proof. See the [design spec](../docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.4-prd-readmes-design.md).
  - `docs/prd/<slug>/README.md` and `docs/prd/README.md` are managed blocks between `<!-- prd-toolkit:start -->` and `<!-- prd-toolkit:end -->`, written by `prd_block.py` beside the `CLAUDE.md` block from two templates, from the PRD's own text (see READMEs and the Overview tab). Text outside the markers is yours. The toolkit's own PRD is at 5.1.0 with `lint-cli` FR-015: lint, the change digest, the bump and the tester skip the PRD folder's root `README.md`.
  - `prd.md` §2 gains two optional parts, `Principles:` and `Getting started:`; no section is added and no existing PRD breaks. Authoring and adoption offer to draft them.
  - `/prd-publish` renders an Overview tab, first and opened by default, from §2, §4, the areas, the open errors and the linked PRDs; a mermaid fence renders as `<pre class="mermaid">`. One module, `prdlint/overview.py`, holds the facts the README and the tab share.
  - `prd_block.py --check` and `prd_hooks.py check --ci` report a stale block (including `CLAUDE.md`, which nothing checked before) as `stale: <file>; run prd_block.py docs/prd/<slug>` and fail; `prd_hooks.py install` refreshes the three blocks. Watch item: a hand-edited `CLAUDE.md` block fails `check --ci` until `prd_block.py` reruns.
  - Known limit: two branches that each change a different PRD can conflict in the parent README's table; rerun `prd_block.py`.
  - Fix 1: a regression case's `known-failing: E-nnn` line comes off together with its `symptom:` line when it has one, at the deploy gate and at the build gate, and no other test-case line goes.
  - Fix 2: the tester's guard resolves a path argument after a harness command that holds uv's `--directory <d>` (or `--directory=<d>`) from `<d>`, so `uv run --directory prd-toolkit pytest -q tests/prd/test_x.py` is allowed; a glob and a path outside the test roots are still refused.
  - Fix 3: the guard allows a checked `grep` (readable paths named one by one, a fixed list of options, no `-R`) for a session with no Grep tool; the tester quotes `--include` and `--exclude` globs and puts every option before the pattern. `cat`, `head`, `sed` and `find` stay barred.
  - Fix 4: `prd_build_check.py --stale` reads a test's path literally (`git --literal-pathspecs log`), so a name with `[`, `*` or `?` is judged by its own last commit.
  - Fix 5: `prd_change.py record` lists a cited ID in the §14 IDs cell when it is a block in the base or the working tree, so an FR the same change removes is listed.
  - Fix 6: `prd_build_check.py --diff` rebuilds the expected `.prd-toolkit/` from a checkout of `<head>` through a temporary index, so `export-ignore` and `export-subst` no longer change it and nothing is held whole in memory; it compares the executable bit as well as the bytes; a subprocess that times out is the tool error `<command> timed out after <n> s`; a failing vendor reads `vendor at <sha>: <its first line>`.
  - Fix 7: a deploy run log that cannot be read is the gate `deploy-step:<run id>:unreadable`, titled `run log <run id> could not be read`, instead of vanishing from the list; answering it is refused with the reason, and the inbox shows the reason with no answer controls.
  - Fix 8: thirteen scripts that no area owned are mapped in four `not started` rows of the toolkit's `adoption.md`: `gates`, `change`, `judge` and `packs`; the new `overview.py` and the two README templates join the `status` row. A `not started` row changes no behaviour.
  - Fix 9: a pack validator that fails reads `validator failed: <first non-blank stderr line>`, else the first non-blank stdout line, else `exit <n>`.
  - Fix 10: the E-007 fix of the 0.8.3 entry (PR #18, `lint-cli` FR-006, PRD 5.0.0) changed lint after 0.8.3 shipped, with no version bump; it first ships to installs in 0.8.4.
  - Upgrading from 0.8.3: re-run `prd_hooks.py install docs/prd/<slug>` (the repository that holds the plugin runs `prd_hooks.py vendor` and then `prd_block.py`), which vendors the new scripts and writes both READMEs and a current `CLAUDE.md` block; commit them with `.prd-toolkit/`. No PRD needs an edit. Watch for a hand-edited `CLAUDE.md` block, which fails `check --ci` until `prd_block.py` reruns.
  - Proven on 2026-11-08, on the toolkit's own PRD:
    - CI passed all five jobs on PR #21 at `041675e` (run 42521656890), and `scripts/ci-local.sh origin/main` with an empty HOME passed all five at `a427384`.
    - A README edited inside its block failed the `prd-lint` job with `stale: docs/prd/prd-toolkit/README.md; run prd_block.py docs/prd/prd-toolkit`, and passed again after `prd_block.py`.
    - The owner approved PRD 5.1.0 in the decision inbox's form, then read both READMEs and approved the `es` labels.
    - Fix 6: `prd_build_check.py --diff 081a20c..bead8e1` passed the vendor-refresh round (exit 0).
    - Fix 2: a `prd-tester` suite round ran T-015.1 and T-015.2 under `uv run --directory prd-toolkit`, both passed, and the guard refused no call. That session had no Grep tool and read whole files instead, so fix 3's checked `grep` waits for a live tester after the merge.
    - `/prd-publish` put PRD 5.1.0 into the design artifact. The Overview tab drew. The mermaid diagram showed as source, because the Artifact viewer runs no mermaid on an HTML page; the cause was publishing the page as a file inside another Artifact, and 0.8.5 draws the diagram.
    - Proven live after the merge on 2026-11-08: a real `prd-tester` on the installed 0.8.4 ran `uv run --directory` and five checked greps with no refusal (fixes 2 and 3).
- **0.8.3:** The fixes from the 0.8.2 proof, and a way for the toolkit's own repository to refresh its vendored copy. See the [design spec](../docs/superpowers/specs/2026-11-06-prd-toolkit-0.8.3-backlog-design.md).
  - `prd_hooks.py vendor <prd>` writes `.prd-toolkit/` exactly as `install` does and nothing else, prints `vendored the toolkit into .prd-toolkit/ (version <X.Y.Z>)`, and refuses from a vendored copy (`prd_hooks: vendor runs from the plugin, not from .prd-toolkit/`, exit 2).
  - `prd_build_check.py --diff` accepts a change under `.prd-toolkit/` when the repository holds exactly one prd-toolkit plugin directory and `.prd-toolkit/` at `<head>` is, byte for byte, what `vendor` writes from that directory at `<head>` (read from `<head>`'s tree, never the working tree), with no path `vendor` would delete. Otherwise each differing path is `<path>: differs from the plugin; refresh it with prd_hooks.py vendor`, exit 1; in any other repository the old refusal stands unchanged.
  - The builder refreshes: in a repository that holds the plugin, a change to a file `vendor` copies is followed, before the commit, by `prd_hooks.py vendor` in its own Bash call, and `.prd-toolkit/` is committed with the change. Never a hand edit under `.prd-toolkit/`, never `install`.
  - `prd_change.py record` writes a block's Since in the §11 row (`live (since 5.1.0)` gives `5.1.0`; a status without one leaves it empty), so a `live` block no longer fails `index-consistent`. When a contract item changes, the §14 IDs cell also lists the UJ, FR and NFR IDs the item cites (an OpenAPI operation's `x-prd-ids`, or the IDs in any other item's text), not `-`.
  - Seven `prd_build_check.py` fixes: `--stale` outside a git working tree is `prd_build_check: <prd> is not in a git working tree`, exit 2; `--results` reads no result line after the first blank or non-result line that follows the first result line; `--stale` reads a repeated key in a test case as the PRD loader does (the first value wins); it reads only files directly in `test-cases/` named `*.yaml`, at a commit and in the working tree alike; it skips a directory or broken link named `<name>.yaml`; `--diff`, `--stale` and `prd_trace.py` read citations line by line with one shared scan, so `@prd` at a line's end and a T-id on the next line is no citation; and a test that cites the T-id and is untracked or changed in the working tree silences the T-id's stale line.
  - The approval card diffs against the base the review read: the verdict gains an optional `base` (a full SHA from `git rev-parse <base>`), and a verdict with no `base`, or one no longer in the repository, falls back to the branch's upstream, else `main`, else `HEAD`. A multi-line `refs` makes the verdict the wrong shape: no gate. A run log that does not parse is `prd_deploy: internal error: <type>: <message>` (exit 2), which the inbox answers 500, not 400. The page's `beforeDone` is optional: Done awaits it only when it is a function.
  - Standby: a PRD that vanishes during a takeover keeps the standby, and a first `serve` with an unreadable PRD says `prd_gates: cannot start the inbox: …`, exit 2; an unexpected error during a takeover is said once, as `prd_gates: standby: <type>: <message>`, and the standby goes on; a gate that left the list wins over the idle bound (exit 1, not 3).
  - The proof, E-007 through the toolkit's own PRD (5.0.0): a directory or broken link named `<name>.yaml` in `test-cases/`, or under `contracts/` outside `contracts/fixtures/`, is now the lint finding `<path>:0: sufficiency: a .yaml entry that is not a file` (exit 1), not an internal error (exit 2), as AC-006.3 says. The fix ran `/prd-error`, `/prd-change` and `/prd-build lint-cli FR-006 --fixes E-007`: regression tests T-006.4 and T-006.5 failed first as strict expected failures, the builder's round committed the `prdlint/model.py` fix with its `vendor` refresh of `.prd-toolkit/` in one commit, `prd_build_check.py --diff` passed it (exit 0), and FR-006 closed `verified`. With that fix, `prd_build_check.py --stale` no longer stops in the PRD loader on such an entry, and a CLI test proves E-013's skip end to end.
  - Upgrading from 0.8.2: re-run `prd_hooks.py install docs/prd/<slug>`, which vendors the fixed `prd_build_check.py`, `prd_change.py`, `prd_gates.py` and `prd_deploy.py` into `.prd-toolkit/` (commit it); the repository that holds the plugin runs `prd_hooks.py vendor` instead. No PRD needs an edit. A verdict written before the upgrade still makes a gate, and its card uses the fallback base.
- **0.8.2:** A local decision inbox, and the fixes from the first real adoption. The sections named below are those of the [design spec](../docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.2-decision-inbox-design.md).
  - `prd_gates.py serve` is the inbox (see Decision inbox): one page for every pending gate across the worktrees, with the approval's diff. `prd_gates.py wait` blocks until a gate is answered by any client and prints `gates.outcome`; both read and write `prd-gates-log.jsonl` in the git common directory. `gates.answer` gains `by` (`form` or `cli`), a reply from a button ends with ` (form)`, and the vendored page is `.prd-toolkit/gates/inbox.html`. The skills route each decision through the inbox and fall back to the chat.
  - The shared inbox outlives its starter (section 18): a `serve --gate` that finds a live inbox stands by and, when that inbox stops before its gate is answered, takes it over at the same URL; each card says when no session's `wait` holds its gate.
  - It builds on three changes to the 0.8.1 interface, made before 0.8.1 shipped (`interface` stays 1): the approval gate has two choices, `approve` and `changes`; the adoption gate stays pending until `done`; and `prd_confirm.py open` writes a new answers file.
  - The 0.8.0 retarget refusal names no release number now: `retargeting an area is a conversion, which a later prd-toolkit release brings`.
  - The confirm form (section 13): the page asks `/ping` every 60 seconds, so the idle time counts from the last page closing and not from the last answer; the question choices read `Keep it as it is`, `Change it…` (words required) and `Answer in my own words`; a confirmed bug counts as answered after the answers file is deleted.
  - `Touches: -` (section 13): `prd_error.py new` and `propose` take `--touches -` and write `Touches: -`; `-` with an ID is refused. `error-entries` reports a gap or an entry out of order, such as `E-012 follows E-010: E-011 is missing; entries are never deleted, restore it from git`.
  - The tester's reading (section 14): the guard lets it Read a background task's `<id>.output` file and read the vendored `.prd-toolkit/packs/`; the references say a helper a pack ships has its parameters and result stated in the pack's `harness`.
  - `prd_build_check.py --stale` (section 15) lists a T-id whose test case changed after its test; the caller adds a `Rewrite:` line for each to the suite prompt, and the tester rewrites that test from the case as it stands.
  - `symptom:` (section 16): a known-failing case names what the run shows while the bug is open, and the test accepts only that failure. `symptom:` without `known-failing:` is an error; a known-failing case that names no symptom gets the warning `known-failing E-nnn names no symptom; any failure would pass as it`. The checklist asks how each precondition is confirmed.
  - Section 17: a pack's shipped helper is imported, never copied, in a dry run; the Leaks slot says how a failure report avoids printing test values (`--tb=short` for pytest); a dry run that failed only on Harness conventions is a harness-only round that keeps the status `In review`; the CLAUDE.md block's change line covers only the adopted areas of a partly adopted PRD (`prd_block.change_line`); `prd_deploy.py record` records a deploy done by hand and moves no status; the build's close names a `verified` block with no build-gate test (`<ID>: verified with no build-gate test; its proof is the deploy gate at /prd-deploy`); and every builder round runs on a round branch, `prd-round/<area>-<n>`, cut in the build worktree, merged `--ff-only` after the check, with no Agent isolation.
  - Upgrading from 0.8.1: re-run `prd_hooks.py install`, which vendors `gates/inbox.html` and the new script versions into `.prd-toolkit/` (commit it). Re-run `prd_block.py` to pick up the new change line: until then `prd_block.py --check` reports a CLAUDE.md block stale. `prd_confirm.py serve` stays for a session that prefers the single-area form. A PRD with a gap in `errors.md` restores the entry from git; a known-failing case without `symptom:` still lints clean (a warning). No PRD needs an edit.
  - Proven on 2026-11-06, on the toolkit's own PRD, in two worktrees on proof branches that stay unpublished (their SHAs are local) and in a fixture:
    - The `deploy-step`, `signoff` and `adoption` cards, each answered in the inbox and checked in the owner's file: `inbox-deploy-step.gif`, `inbox-signoff.gif`, `inbox-adoption.gif`.
    - Two worktrees' gates in one inbox: an approval from each, answered in the inbox at 14:58:51Z and 15:05:48Z (`60d0b6d`, `cd1d4ec`).
    - A `/prd-change` approved in the inbox after a Request changes round: the gate log holds `changes` with the owner's words (21:57:23Z), then `approve` (21:58:10Z), in `215e297`.
    - A `/prd-error` class confirmed on the inbox card, not in the chat: E-008 at 17:30:58Z (`844037a`), and eight more entries the same way.
    - The proof found that a shared inbox died with the session that started it, and that the owner could answer a gate no session still waited on; section 18 fixes both (`3870060`, `560265b`).
- **0.8.1:** The machine interface: JSON output, the change bookkeeping as code, one list of pending decisions and a review mode.
  - `--json` and `--interface` on `prd_lint.py`, `prd_trace.py`, `prd_status.py`, `prd_context.py`, `prd_change.py` and `prd_gates.py`; every document starts `{"interface": 1, "kind": …}` (see Machine interface). The toolkit's own PRD is at 4.0.0, with `lint-cli` FR-014 (lint `--json` and `--interface`) verified and FR-001 and FR-004 revised for them.
  - A break: in 0.8.0 `prd_status.py --json` and `prd_context.py --json` printed a bare JSON list. In 0.8.1 they print a wrapped document, `{"interface": 1, "kind": …}` (the status items under `items`, the context pack's parts under `parts`, one entry per item), so anything that parses them must change.
  - `prd_change.py` (`ids next`, `bump`, `record`, `digest`, `approve`): `changing-prds` takes its IDs, version bump, §14 and §11 rows and approval commit from it instead of working them out by hand, and its Version rule carries the script's bump table.
  - `/prd-change --review <dir>`: review mode edits nothing and writes the verdict `.prd-review.json`, which `approve` checks.
  - `prd_gates.py list` and `answer`: every pending approval, error class, deploy step, adoption area and sign-off in one shape, each answer passed to the script that owns it. `prd_confirm.py` gains `answer`, `open` and `done`, and the adoption gate stays pending until `done`.
  - Upgrading from 0.8.0: re-run `prd_hooks.py install`, which vendors `prd_change.py` and `prd_gates.py` into `.prd-toolkit/` and adds `.prd-review.json` to `.gitignore` (commit `.gitignore` along with `.prd-toolkit/`); `changing-prds` stops on a vendored copy without `prd_change.py`. No PRD needs an edit.
- **0.8.0:** Packs, languages and judged test cases.
  - Packs: the `pack.yaml` manifest, discovery from `.prd-toolkit/packs/`, the toolkit and installed plugins' `prd-packs/<name>/`, a version lock, and two built-in packs, `service` (0.7's behaviour) and `document` (Markdown documents, with the `outline` contract type). `prd_hooks.py install` records each vendored pack's source in `.prd-toolkit/pack-sources.json`. `prd_lint.py --list-packs` lists them. A PRD names a pack in §1 (`Pack:`, `Output language:`) and per area in a `Target:` line.
  - Languages: frontmatter `language:` with EARS and vague-word tables for `en` and `es`.
  - Judged cases: `rubric:` and `threshold:` in a test case, scored by `prd_judge.py` (median of runs, quote-checked, recorded in `.prd-judge/`).
    `judged-case` also refuses a repeated rubric item and warns on a threshold below 1.0 that needs every item (2 of 3 items is 0.666…, so 0.67 needs all three).
  - Lint: severity `warn` (`<file>:<line>: warn: <rule>: <message>`; the exit code counts errors only) and four rules, `language-table`, `pack-resolves`, `judged-case` and the warning `platform-word` (40 in all). The authoring, building, testing and changing skills and the agents use packs, languages and judged cases.
  - The lint command's output changes. `--list-rules` now prints `<name> <severity>` on each line (0.7 printed names only), so anything that parses it must change. `prd_lint.py --list-packs` lists the packs, built-ins first. The usage line is one line whatever the terminal width. The toolkit's own PRD (`docs/prd/prd-toolkit`) is at 2.0.0, with `lint-cli` FR-001, FR-003, FR-004 and the new FR-013 verified.
  - `prd_trace.py --range` judges each commit by the adoption map in that commit's own tree, so a commit made before an area was adopted (or before `adoption.md` was committed) is not held to today's Boundary. An adoption map that was never committed still judges every commit, as before.
  - Upgrading from 0.7: re-run `prd_hooks.py install`, which vendors the 0.8.0 scripts and the `service` pack into `.prd-toolkit/` and adds `.prd-judge/` to `.gitignore`. A PRD that adds `language:`, a `Pack:`, `Output language:` or `Target:` line takes a patch bump with the §14 row `format: target profiles (prd-toolkit 0.8)`. No 0.7 PRD needs an edit.
- **0.7.3:** The toolkit's own PRD fixes six `lint-cli` bugs, E-001 to E-006, each closed by its regression test. A directory named `prd.md` is refused as "prd.md must be a file", with no lowercase-name hint. The missing-package message names the script that failed and only the packages of its own dependency header. A YAML mapping key that is a list or a mapping is a `YAML parse error: found unhashable key` finding, not an internal error. Nothing under `contracts/fixtures/` is read as a PRD document or contract YAML. A `.md` entry that is not a file is a `sufficiency` finding, not an internal error. `--sample-tids` no longer samples a test case with no level or a level that is not lowercase. The git hooks also work in a linked worktree: git exports `GIT_DIR` to a hook without `GIT_WORK_TREE`, and the pre-commit hook ran each enforced standards command from the PRD folder; it now pins both from the hook's own directory. Upgrading from 0.7.2: re-run `prd_hooks.py install`, which vendors the fixed scripts into `.prd-toolkit/`. No PRD needs an edit.
- **0.7.2:** Three fixes from the 0.7.1 acceptance run. The form now serves a clarification marker whose key a requirement's `Traces:` line names without backticks, when the word is an identifier with an underscore or in camelCase (`PRD_LINT_CI`, `maxSize`; a dotted or `kind:name` word names its last part). A prose word, an all-caps word, an ID such as `FR-001`, a version and a path part still name nothing, and backticks remain the sure way to name a key. A bare `settings.KEY` now names `KEY`, which 0.7.1 did not. The answers file's `prd` field holds the PRD's slug (it read the wrong frontmatter key and was empty). Every text box in the form now has a one-line hint: a bug's box asks for the behaviour you want, not the code fix, and a question's or a setting's box says what its answer needs. Upgrading from 0.7.1: re-run `prd_hooks.py install`, which vendors the fixed scripts and `confirm/form.html` into `.prd-toolkit/`. No PRD needs an edit.
- **0.7.1:** `prd_confirm.py` and `templates/confirm/form.html`: adoption step 3 confirms an area's as-built requirements, open errors, questions and clarification markers through a local form, with answers saved as they are given (see Adopting an existing repo). `AskUserQuestion` and the checklist file remain the fallbacks. Upgrading from 0.7.0: re-run `prd_hooks.py install`, which vendors `prd_confirm.py` and `confirm/form.html` into `.prd-toolkit/`. No PRD needs an edit.
- **0.7.0:**
  - `/prd-change-set` and the `coordinating-prds` skill: `links.md`, the pinned snapshot `contracts/upstream/<prd>/` and `prd_links.py` (`add`, `sync`, `check`, `impact`, `changeset`) link PRDs across repositories; one record, `changes/CS-nnn.md`, drives a change with one approval and a build per repository in dependency order (see Links and Change sets).
  - Four lint rules (`links-format`, `upstream-refs`, `snapshot-cited`, `change-sets`; 36 in all). `commit-refs` checks the `Change-set:` trailer. The generated `prd-lint` job runs `check --ci`, and the deploy pre-flight runs the link check. The interview asks about packaging.
  - Upgrading from 0.6: re-run `prd_hooks.py install` (it vendors `prd_links.py`) and `prd_hooks.py ci` (the `prd-lint` job gains `check --ci` when `links.md` exists). The managed block's wording changed, so re-run `prd_block.py` after upgrading: the vendored block templates are stale until then, and `prd_block.py --check` reports each CLAUDE.md block stale. A PRD without `links.md` needs no edit.
- **0.6.1:** `/prd-publish` writes again. 0.6.0 put the page and the summaries file under `.git/`, where Claude Code refuses writes, so nothing rendered. The page's default is `./<project>-prd-<version>.html` in the repository root again, untracked and never committed. The summaries file is written beside it and deleted after the render. Move the page out of the repository or delete it before the next `/prd-build`, whose clean-tree check stops on an untracked file.
- **0.6.0:**
  - `/prd-error` and the `handling-errors` skill: `errors.md` entries gain a canonical line order (`Detected:`, `Classification:`, `Confirmed:`, `Touches:`, `Evidence:`, `Diagnosis:`, `Resolution:`, `Recurrence of:`) and `prd_error.py` (`new`, `list`, `propose`, `confirm`, `resolve`, `check`) is their only writer. The linter gains `error-entries` (its 32nd rule) and the trace gains `known-failing-tags` (its fifth rule). A code commit may cite only a confirmed entry (see Handling errors).
  - Known-failing tests mark themselves as strict expected failures and tag their citation. A stopped build records an entry, and `/prd-build --fixes E-nnn` builds a fix from it. `prd_deploy.py recover` ends a killed step. The generated `prd-lint` job also runs `prd_hooks.py check --ci`, which reports stale CI.
  - `/prd-publish` and the `publishing-prds` skill: `prd_publish.py` renders the PRD as one self-contained HTML page (see Publishing).
  - Upgrading from 0.5: re-run `prd_hooks.py install` (it vendors `prd_error.py`) and `prd_hooks.py ci` (the `prd-lint` job gains `check --ci`). The managed block's text changed in 0.6, so every existing repo's `prd_block.py --check` reports its CLAUDE.md block stale until `prd_block.py` is re-run. An existing `known-failing` case needs a tagged citation: the trace's `known-failing-tags` reports it until `/prd-error E-nnn` takes its entry to the code-bug route, whose tester round marks the test a strict expected failure and tags its citation (the case and its `approved` block need no patch). An open 0.5 entry that carries a class now counts as `proposed`, so a code commit citing it is refused until `prd_error.py confirm` records your reply (`/prd-error E-nnn` asks for it). Existing entries need no edit: the new lines are optional, `error-entries` judges `Detected:` and `Recurrence of:` only on an entry that carries `Confirmed:`, and `check` judges only ranges. A `.prd-toolkit/` without `prd_error.py` predates 0.6, and the skills stop on it until `prd_hooks.py install` runs.
- **0.5.0:**
  - `/prd-deploy` and the `deploying-from-prds` skill: `prd_deploy.py` runs the `operations.md` runbook, every step from 1 in order, and stops at each human step and on each failure. The model never types a runbook command; it relays each reply verbatim, records a failure in `errors.md`, and closes with Deployed rows and `verified` → `live (since X.Y.Z)` (see Deploying).
  - The runbook is a step grammar: `(actor: …) (env: …)` and the labels `Run:`, `Check:`, `Rollback:`, `Do:`. Environments gains a `Production` column. `operations.md` gains `## Deployed` and `## Drift`.
  - `prd_drift.py` compares what an environment runs with what the PRD says (`version` and `config`).
  - A `smoke` level in `testing.md`. Five lint rules: `runbook-steps`, `runbook-env`, `production-gate`, `runbook-tests` and `drift-rows`.
  - Generated CI adds manual `drift-<env>` and `test-deploy-<env>` jobs, outside the merge gate; they never deploy. `/prd-status` shows each environment's deployed version.
  - The README's shell commands name a real path (`.prd-toolkit/<script>.py`, or the plugin's install path for the first install) instead of `${CLAUDE_PLUGIN_ROOT}`, which a shell does not set.
  - After upgrading the plugin, run `prd_hooks.py install` from it again, so `.prd-toolkit/` gains `prd_deploy.py`, `prd_drift.py`, `prd_block.py` and the block template (`templates/claude-block.md`), then `prd_hooks.py ci` again for the manual deploy jobs. Until then `prd_hooks.py check` reports the stale copy.
  - Upgrading a 0.4 PRD: lint fails `runbook-steps` until each runbook step carries `(env: …)` and its labels, and `runbook-env` until Environments has a Production column; a patch bump with the §14 row `format: runbook steps (prd-toolkit 0.5)`. `## Deployed` and `## Drift` are optional. The 0.4 runbook and its 0.5 form:

    ```
    ## Runbook

    1. Deploy the build with `./deploy.sh staging`, then run the system tests. (actor: agent)
    2. Deploy to production with `./deploy.sh production` after the owner approves. (actor: human)
    ```

    ```
    ## Runbook

    1. Deploy to staging (actor: agent) (env: staging)
       Run: `./deploy.sh staging`
       Check: `curl -fsS https://orders-staging.example.com/health` prints `ok`
       Rollback: `./deploy.sh staging --previous`
    2. System tests on staging (actor: agent) (env: staging)
       Run: tests system, e2e
    3. Approve production (actor: human) (env: production)
       Do: read the staging results and reply "deploy production"
       Check: the reply says "deploy production"
    4. Deploy to production (actor: agent) (env: production)
       Run: `./deploy.sh production`
       Check: `curl -fsS https://orders.example.com/health` prints `ok`
       Rollback: `./deploy.sh production --previous`
    5. Smoke on production (actor: agent) (env: production)
       Run: tests smoke
    ```

    The Environments table gains the column, `yes` on the production row and `no` on the others:
    `| Environment | URL | Production |`.
- **0.4.0:**
  - `/prd-build` and the `building-from-prds` skill: `prd-builder` works in its own worktree while `prd-tester` writes its tests in the new `write` mode; the build reconciles by quote. Statuses move `approved`, `built`, `verified` with no version bump; built blocks carry `Source:`.
  - `/prd-status` (`prd_status.py`) and `prd_build_check.py`.
  - `prd_hooks.py` vendors the scripts into `.prd-toolkit/` and installs `commit-msg` and `pre-commit` hooks. It never overwrites an existing hook and never sets `core.hooksPath`; with `core.hooksPath` set it writes no shim and prints the lines to add. A hook skips, with a message, on a branch with no `.prd-toolkit/` or no PRD folder (see Hooks and CI).
  - `prd_hooks.py ci --gitlab|--github` generates a merge-gate include file. `prd_lint.py --ci` skips the installed-skill and on-PATH checks of `registries` and keeps every Decision check.
  - The commit rule covers new projects and checks cited IDs (deletions and rename sources count).
  - `prd_trace.py` is gate-aware: `approved` blocks are skipped, `built`, `verified` and `as-built` blocks need citations for unit and build-gate T-ids, and `live` blocks for every T-id.
  - The Levels table in `testing.md` gains a `Gate` column (`build` or `deploy`). Upgrading a 0.3 PRD: lint fails `test-level` until the table has a Gate column (build or deploy), a patch bump.
  - Generated CI jobs install only `uv`, so each standards linter and Levels harness command must run on a bare runner (for example `uv run ...`). GitLab jobs run on merge-request pipelines.
- **0.3.0:** `/prd-context` and `prd_context.py` (decide and implement packs); `adoption.md`; `Touches:` in `errors.md`; `changing-prds` works from the pack. Upgrading a 0.2 PRD: it fails `sections` until §8's table moves to `adoption.md` and §8 reads `See adoption.md.`, a patch bump. The managed `CLAUDE.md` block's wording changed in 0.3: re-render it with `prd_block.py`; until then, `prd_block.py --check` reports it stale.
- **0.2.0:** `/prd-adopt` and `adopting-prds`; `testing-from-prds`, the `prd-tester` agent and its guard hook; `prd_trace.py`; the `awaiting <who>` assumption status. Upgrading a 0.1 PRD: it fails `sections` until its `testing.md` Harness has every slot, in order, and a `Test roots:` list.
- **0.1.0:** `/prd-new`, `/prd-change`, `prd_lint.py` (27 rules) and `prd_block.py`.

## CLAUDE.md block

`prd_block.py` writes the managed block that points agents at the PRD. It is deterministic, not
written by an agent.

```
uv run --script prd-toolkit/scripts/prd_block.py docs/prd/<slug> [--claude-md PATH] [--check]
```

`--check` reports whether the block is current without writing.

## READMEs and the Overview tab

Since 0.8.4 a person who opens `docs/prd/` or `docs/prd/<slug>/` on a forge finds a README that says
what the folder is, whether to edit it and how, and a person who opens a published page finds an
Overview tab. Both are assembled from the PRD's own text, never from anything outside the PRD folder.

**The two READMEs.** `prd_block.py docs/prd/<slug>` writes three managed blocks: the `CLAUDE.md`
block as before, `docs/prd/<slug>/README.md` (what the PRD covers, its areas, what is in the folder
and how to read and change it) and `docs/prd/README.md` (a table of every PRD under `docs/prd/`, how
the toolkit works and how to get started). Each block sits between `<!-- prd-toolkit:start -->` and
`<!-- prd-toolkit:end -->`; text outside the markers belongs to you and is never touched. A block is
never edited by hand: it is rewritten from the PRD, and a better description is a better PRD §2,
changed through `/prd-toolkit:prd-change`. The description is §2's first paragraph (its first sentence in the
parent's table). Two start markers, or unbalanced markers, make `prd_block.py` exit 2; a marker
inside a closed code fence is not a marker. The skills stage both READMEs with `CLAUDE.md` wherever
they run `prd_block.py`, and lint, the change digest, the version bump and the tester all skip the
PRD folder's root `README.md` (the toolkit's own PRD, `lint-cli` FR-015, PRD 5.1.0).

**Checking.** `prd_block.py --check` prints `stale: <file>` for each block that differs from what it
would write now and exits 1, else 0. `prd_hooks.py check --ci`, which the generated CI job already
runs, prints `stale: <file>; run prd_block.py docs/prd/<slug>` and exits 1 for the same condition,
and now covers `CLAUDE.md` too. There is no pre-commit check: in the middle of a change the version
moves before the blocks are refreshed.

**Upgrading.** `prd_hooks.py install` refreshes the three blocks after it vendors the copy, so an
upgrade writes both READMEs in the same commit as `.prd-toolkit/` and the next PR does not fail the
new check. The one thing to watch: a repository that hand-edited the text between the markers of its
`CLAUDE.md` block fails `check --ci` until `prd_block.py docs/prd/<slug>` runs again (the check
message names the command). Never merge a README conflict by hand; rerun `prd_block.py`.

**§2's two optional parts.** `prd.md` §2 may hold two more labelled parts beside `Goals:`,
`Personas:` and `Out of scope:`: `Principles:` (bold-named bullets, each one or two sentences) and
`Getting started:` (numbered steps a new user takes). A part runs from its label to the next
labelled line of §2 or its end; a PRD in another language uses its language table's labels
(`Principios:` and `Primeros pasos:` in Spanish). Both are optional and free Markdown, lint checks
nothing new, and no existing PRD breaks. Authoring phase 2 and the adoption bootstrap offer to draft
them from what you say; neither requires them.

**The Overview tab.** `prd_publish.py render` writes three tabs, the Overview first and checked by
default, then Business and Technical unchanged. The Overview holds, each part left out when its
source is empty: the version, status, owner and date line; what it is (§2's first paragraph); the
principles; the architecture (§4); a table of areas with adoption status and requirement counts
by status; the count of open errors; the linked PRDs; and the getting-started steps. It needs no
summary and gets none, and it loads nothing, like the rest of the page. The README and the tab take
their facts from one module, `prdlint/overview.py`, so they never disagree. A published page gains
its tab on the next `/prd-toolkit:prd-publish`; a PRD without `Principles:` or `Getting started:` gets the tab
without those two parts.

## Folder layout

```
docs/prd/<project>/
├── prd.md                  index: metadata, goals, glossary, registries, ID registry, changelog
├── features/<area>.md      FR blocks with EARS acceptance criteria and T-ids
├── test-cases/<area>.yaml  one entry per T-id
├── contracts/              openapi.yaml, schema.sql, events.md, errors.yaml, permissions.yaml,
│                           config.yaml, data-classification.yaml, dependencies/, fixtures/
├── nfr.md                  NFRs with numeric bounds
├── testing.md              levels, harness, environments, sign-offs
├── operations.md           environments, deploy and rollback runbook, Deployed and Drift tables
└── errors.md               the Error-Driven Development ledger

.prd-toolkit/               vendored scripts, version file and hook sources (written by prd_hooks.py install)
```

The exact syntax lint parses is `references/prd-format.md`. The starting files are in
`templates/prd/`.

## Tests and evals

```
uv run --directory prd-toolkit pytest -q
```

The commands answer only to their namespaced form, such as `/prd-toolkit:prd-change`, both when
the plugin is installed and under `claude --plugin-dir <path>`. The bare `/prd-change` that the
skills' text still prints gets "Unknown command" from current Claude Code: type the namespaced form.

The plugin eval: run the command recorded in `evals/BASELINE.md` (0.2 baseline; the 0.8.0 and 0.8.1 sections run one case at a time). The `--scaffold`
flag is required by the scaffolded cases, `Agent` lets the caller dispatch `prd-tester`, and the
pypi grants let `prd_lint.py` fetch its dependencies under the Bash sandbox:

```
claude plugin eval ./prd-toolkit --runs 3 --model sonnet --scaffold --trust-plugin --no-publish -j 4 --keep-temp \
  --json <out>.json --allow-tools Write Edit Bash Agent "WebFetch(domain:pypi.org)" "WebFetch(domain:files.pythonhosted.org)"
```

## License

MIT; see [LICENSE](./LICENSE). A vendored `.prd-toolkit/` carries a copy of it.

## Credits

Adapted from GitHub Spec Kit, cc-sdd, BMAD-METHOD, mattpocock/skills and Anthropic's
doc-coauthoring skill. See [NOTICE](./NOTICE).
