# prd-toolkit 0.8.9: a help catalogue — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One command, `prd help`, prints what every field of the PRD grammar and every lint rule is, why it is there and how it is written, as text and as JSON.

**Architecture:** A YAML catalogue (`references/help.yaml`), a description on each `@rule` registration, and a small interface script (`prd_help.py`) that joins the two. The area is written in the toolkit's own PRD first and built from it: `/prd-toolkit:prd-change` writes the requirements, `/prd-toolkit:prd-build` has the builder write the code and the black-box tester write the tests. This plan fixes what the PRD change must say, so the build has nothing left to decide.

**Tech stack:** Python 3.11+, pyyaml, the toolkit's own `prdlint` package and `interface.py`, pytest. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.9-help-catalogue-design.md`. Where this plan and the spec differ, the spec wins and the difference goes in its Revisions note.

## Global constraints

- **Branch:** `feat/prd-toolkit-0.8.9`, worktree `.worktrees/prd-toolkit-0.8.9`, cut from `main` after the spec branch (`docs/prd-toolkit-0.8.9-spec`) is merged. Never work in the main checkout.
- **Author:** the clone's git config (ivan@badgeretl.com). Commits cite the PRD IDs they touch (`Refs: FR-0nn`) or `Refs: none (no behaviour change)`. Never `--no-verify`, never a bare `git stash`.
- **Generic:** no file, test, commit or PRD line names a client application, an organization or a person. The public repository is the audience.
- **Unchanged:** `prd lint`'s finding lines, `--list-rules` and `--json` output, byte for byte. Every other script's usage and exit codes.
- **Commands are typed in the 0.8.8 form:** `.prd-toolkit/prd <command> …` for the vendored copy, `<plugin>/scripts/prd <command> …` for the plugin's.
- **The vendored copy** matches the plugin byte for byte: after a change to a vendored file, `prd-toolkit/scripts/prd hooks vendor docs/prd/prd-toolkit`, committed with the change. Never `install` in this repository.
- **Tests:** unit `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`; integration `uv run --directory prd-toolkit pytest -q -n auto tests/prd`. Nobody but `prd-tester` writes or edits a test under `tests/prd/`. Baseline on 9b9553c: unit 3575 passed, 1 skipped; integration 158 passed.
- **The stops:** the owner approves the PRD change (Task 1), reads the catalogue (Task 4) and gives the word to push (Task 5). Nothing else waits on a person.

## One addition to the spec

**A setting, `PRD_HELP_FILE`.** When it is set and not empty, `prd_help.py` reads the catalogue from that path instead of the file beside it. It goes in `contracts/config.yaml`, as `PRD_PLUGINS_FILE` does. Reason: a black-box test of the text and JSON forms needs to know every character of the output, and the shipped catalogue's wording is not in the PRD. The test cases that assert exact output run on a three-entry fixture catalogue; the cases about the shipped catalogue assert its structure and its keys. Task 1 adds a Revisions line to the spec.

## Review focus

What the spec implies and a build could miss. Each is pinned by an acceptance criterion in Task 1.

1. **A catalogue that is not valid** (a missing file, a top level that is not a list, an entry without a required field, a duplicate key, a `checked_by` naming no registered rule): exit 2 with one line naming the file and the reason, never a traceback. → FR-d.
2. **Non-ASCII text** in an entry (a dash, a quote): the JSON document is UTF-8 and not escaped to `\u…`, as every interface document. → FR-c.
3. **A rule with no description** registered later: the content test fails, and `prd help --json` still prints the document with an empty description rather than crashing. → FR-f.
4. **A vendored copy** must answer exactly as the plugin does, and `prd help` must reach it through the launcher. → FR-g.
5. **Lint must not change.** A description added to `@rule` must not reach any lint output. → FR-f, and the existing lint-cli cases, which must all still pass.

---

### Task 0: Branch and baseline

- [ ] **Step 1:** Confirm `origin/main` holds the merge of `docs/prd-toolkit-0.8.9-spec`. If not, stop and report.
- [ ] **Step 2:** `git worktree add -b feat/prd-toolkit-0.8.9 .worktrees/prd-toolkit-0.8.9 origin/main`; check `git config user.email`.
- [ ] **Step 3:** Run both test commands; record the counts in the ledger. A failure here is reported, not fixed.

---

### Task 1: The PRD change (controller-run; stops for the owner)

The controller runs `/prd-toolkit:prd-change` itself, in the worktree, and follows the skill: the IDs come from `prd change ids next`, the version from `bump` and `record`, the dry run from `prd-tester`. The working names below (UJ-x, FR-a to FR-g) are placeholders for the IDs the script prints.

**Files (all under `docs/prd/prd-toolkit/`):** create `features/help.md`, `test-cases/help.yaml`, `contracts/fixtures/help/catalogue.yaml`; modify `contracts/cli.yaml`, `contracts/config.yaml`, `adoption.md`, `testing.md` (the fixture's row and any output key the cases need), `features/lint-cli.md` (one Edge-cases clause), and what `record` writes in `prd.md`.

- [ ] **Step 1: `adoption.md`.** A row `| help | adopted | … |` with the Boundary `prd-toolkit/scripts/prd_help.py`, `prd-toolkit/references/help.yaml`. `adopted` is the state whose Boundary the commit-msg hook enforces, which is what a spec-first area wants from its first commit. If lint or the change script refuses that state for an area with no extraction history, stop and report the message; do not pick another state without a ruling.

- [ ] **Step 2: `features/help.md`**, with these blocks. Every AC is EARS, with the exact output text in it.

  **UJ-x A person or a program asks what a field or a lint finding means.** Flow: run `prd help` for the index → run `prd help --key <key>` or `prd help --rule <rule>` → read what it is, why and its rules; a program runs `prd help --json` once and looks items up itself. Traces: FR-a to FR-d.

  **FR-a Print the index.** When `prd_help.py` runs with no option, it prints one line per catalogue entry, `<key>  <name>` (two spaces), in the catalogue's order; then one empty line; then one line per registered rule, `<name>  <severity>`, sorted by name; and exits 0. It takes no folder argument and reads no PRD.

  **FR-b Print one entry or one rule as text.**
  - `--key <K>` prints, in this order, and exits 0: `<name> (<key>)`; `What: <what>`; `Why: <why>`; when the entry has `rules`, the line `Rules:` and one line `- <rule>` each; when it has `checked_by`, the line `Checked by:` and one line `- <rule name>: <description>` each; when it has `see`, `See: <see>`. A part the entry lacks prints no line.
  - `--rule <R>` prints `<name> (<severity>)`, then the description on its own line, then, when one or more entries name the rule in `checked_by`, `Checks: <key>, <key>` in the catalogue's order; exits 0.

  **FR-c Print the catalogue as one JSON document.**
  - `--json` prints on stdout one JSON object on one line, ending in a newline, and nothing else: `{"interface": 1, "kind": "help", "entries": [<entry>, …], "rules": {"<name>": {"severity": "error" or "warn", "description": <text>}, …}}`, its first two keys `interface` and `kind`; entries in the catalogue's order; `rules` holding every registered rule, sorted by name; exit 0.
  - An `<entry>` is `{"key", "name", "what", "why"}` plus `rules`, `checked_by` and `see`, each only when the catalogue gives it, in that key order.
  - `--json --key <K>` limits `entries` to that entry and leaves `rules` whole; `--json --rule <R>` limits `rules` to that rule and `entries` to those that name it in `checked_by`.
  - `--json=1` is `--json`; text outside ASCII is written as itself, in UTF-8.
  - `--interface` prints `1` on one line and exits 0, whatever else is given.

  **FR-d Refuse what it cannot answer.**
  - An unknown key: stderr `prd_help: no entry '<K>'`, exit 2. An unknown rule: stderr `prd_help: no rule '<R>'`, exit 2.
  - `--key` together with `--rule`, an unknown option, or a positional argument: argparse's usage and error lines on stderr, exit 2. The usage line is `usage: prd_help.py [-h] [--key KEY | --rule RULE] [--json] [--interface]`, on one line whatever the terminal width.
  - A catalogue that cannot be used: stderr `prd_help: <path>: <reason>`, exit 2, where `<reason>` is `no such file`, `YAML parse error: <problem>`, `top level must be a list`, `entry <n>: missing '<field>'` (the first of `key`, `name`, `what`, `why` that is absent or empty; `<n>` counts from 1), `entry <n>: duplicate key '<key>'`, or `entry <n>: checked_by names no rule '<name>'`; the first problem found, in file order.
  - With `--json`, each exit-2 case also prints on stdout `{"interface": 1, "kind": "help", "error": <message>}`, the message being the stderr line without its `prd_help: ` prefix (for a usage error, argparse's message).
  - `--json=<N>` with N other than 1, without `--interface`: the error document and stderr line of lint-cli's FR-014 (`unsupported interface <N>; this toolkit speaks 1`), exit 2.

  **FR-e The shipped catalogue covers the grammar.** When no `PRD_HELP_FILE` is set, the document's `entries` hold every key the contract lists (the 43 keys of spec section 3); every entry has non-empty `key`, `name`, `what` and `why`; keys are unique; the `name` of `kind.UJ`, `kind.FR`, `kind.NFR`, `kind.T`, `kind.E` and `kind.CS` is `User journey`, `Requirement`, `Quality requirement`, `Test case`, `Error` and `Change set`; every `checked_by` value is a key of the document's `rules`.

  **FR-f Every lint rule carries a description.** The document's `rules` hold exactly the names `prd_lint.py --list-rules` prints, each with the severity that command prints and a description that is not empty and holds no line break. A rule registered without a description has the description `""` in the document. The lint command's finding lines, its `--list-rules` output and its `--json` document hold no description.

  **FR-g A vendored copy answers the same.** When `.prd-toolkit/prd_help.py --json` runs in a repository that vendors the toolkit, it prints the document the plugin's `prd_help.py --json` prints; `.prd-toolkit/help.yaml` is the catalogue it reads.

  Each block carries `Status: approved`, its `Tests:` line and `Traces: cli:prd_help` (and `setting PRD_HELP_FILE` where it applies).

- [ ] **Step 3: contracts.** `contracts/cli.yaml` gains a `prd_help` key in the shape of `prd_lint`: `invocation`, `arguments` (`--key KEY`, `--rule RULE`, `--json`, `--interface`, `-h`), `output` (index line, rule line, each text part, `json_document`, `json_error`, each stderr line), `keys` (the 43 keys), `exit_codes` (0 and 2). `contracts/config.yaml` gains `PRD_HELP_FILE`.

- [ ] **Step 4: the fixture and the cases.** `contracts/fixtures/help/catalogue.yaml`: three entries, one with every optional field (its `checked_by` naming `ac-ears` and `platform-word`), one with none, one whose text holds a non-ASCII dash. `test-cases/help.yaml`: at least one case per AC, level `integration`, target `cli:prd_help`, run as `python <repo>/prd-toolkit/scripts/prd_help.py …` (the harness's subprocess form). Exact-output cases set `PRD_HELP_FILE` to the fixture; FR-e and FR-f run on the shipped catalogue and assert structure; FR-f compares with `prd_lint.py --list-rules` run in the same case; FR-g uses the `repo/vendored` fixture. Broken-catalogue cases write their own small file under `<tmp>`. If a case needs an assertion key `testing.md` does not define, define it there in the same change.

- [ ] **Step 5: `lint-cli`.** FR-003's Edge cases gain one clause: a rule's description is `prd_help.py`'s to print (FR-f); `--list-rules` prints the name and severity only. No lint-cli AC changes; if `bump` reports otherwise, decide it by the version rule and record the reason.

- [ ] **Step 6: the spec's Revisions** gain the `PRD_HELP_FILE` line (same commit as the PRD is not possible: the approval commit holds the PRD folder alone; commit the spec line before it, `Refs: none (no behaviour change)`).

- [ ] **Step 7:** `bump`, `record` (expected: minor, 6.3.0), lint, the dry run over the new T-ids, the verdict, and the approval gate. Show the owner the requirement list, the version and the dry-run record. **Stop for the owner's approval.**

---

### Task 2: The build (controller-run)

- [ ] **Step 1:** `/prd-toolkit:prd-build help <the UJ and FR IDs of Task 1>`, following the skill: the round branch, `prd-builder` for the unit tests and the code, `prd-tester` for the tests under `tests/prd/`, the reconciliation of each failure by quoting the PRD.

  What the builder must produce, so the controller can check the round against it:
  - `prd-toolkit/references/help.yaml`: every key of the contract, written from `references/prd-format.md`, `references/ears.md` and `references/test-levels.md`; each `see` the exact text of a heading of `prd-format.md` outside a code fence.
  - `prd-toolkit/scripts/prdlint/registry.py`: `rule(name, severity="error", description="")` and `DESCRIPTION: dict[str, str]`; a description on all 40 registrations under `prdlint/rules/`, each written from the rule's code and its finding messages.
  - `prd-toolkit/scripts/prdlint/helpcat.py` (the catalogue: load, validate, look up) and `prd-toolkit/scripts/prd_help.py` (the command, on `interface.py`).
  - `prd_dispatch.COMMANDS` gains `help`; `hooks.VENDORED` gains `prd_help.py`; `hooks._source_files` vendors `references/help.yaml` as `.prd-toolkit/help.yaml`; `adoption.md` already maps the two Boundary files, and `helpcat.py` joins the row in a follow-up PRD patch only if `tests/test_adoption_map.py` requires library modules (it requires scripts today; check).
  - Unit tests (the builder's, under `prd-toolkit/tests/`): every registered rule has a non-empty one-line description; every `checked_by` names a registered rule; every `see` is a heading of `prd-format.md` outside a fence; keys are unique and match `[a-z]+(\.[A-Za-z_]+)+`; the contract's key list equals the spec's; no entry and no description holds an organization's or an application's name (the test holds no such list itself: it asserts the text names no product by checking against the words in the toolkit's own `NOTICE` and plugin manifest only); `prd lint --list-rules` and a lint run on the valid fixture are byte-identical to files recorded from 9b9553c.
  - The vendored copy refreshed; `tests/test_vendored_copy.py`, `tests/test_dispatch.py` and `tests/test_release_0_8_8.py` updated where they count commands or vendored files (18 commands; the launcher-command test's table).
- [ ] **Step 2:** The close: every requirement `verified`, lint and `check --ci` clean, both suites green. If the round stops (the builder reports a gap in the PRD, or a tester's test contradicts an AC), follow the skill: a gap is a `/prd-toolkit:prd-change`, not a guess.

---

### Task 3: The text against its sources

Two reviewers and one fixer, as subagents; no reviewer edits.

- [ ] **Step 1: review the catalogue.** One reviewer reads `references/help.yaml` beside `references/prd-format.md`, `ears.md` and `test-levels.md`. For each entry: is `what` true; is every line of `rules` stated by the reference passage its `see` names (quote the passage); does `checked_by` name the rules that really check it (read the rule); is anything a person needs to fill the field missing. Output: a table, entry by entry, `ok` or the correction with its source quoted.
- [ ] **Step 2: review the descriptions.** A second reviewer reads each `@rule` description beside the rule's function and its finding messages: does the description say what the rule checks, and does following its fix advice clear every message the rule can print. Output: the same table, rule by rule.
- [ ] **Step 3: one fixer** applies every correction, re-runs the content tests and both suites, and commits (`Refs:` the catalogue's or the rule's requirement). A correction that shows the *reference* is wrong is not applied to the reference here: it is listed for the owner.
- [ ] **Step 4:** a scoped re-review of the fixer's diff.

---

### Task 4: The owner reads the catalogue (stops for the owner)

- [ ] **Step 1:** Print the whole catalogue as text to a file outside the repository: the index, then every `--key` and every `--rule`, in order. Give the owner the path, the count of entries and rules, and the list of corrections Task 3 made.
- [ ] **Step 2:** **Stop.** A change the owner asks for is a fixer round as in Task 3.

---

### Task 5: Release

**Files:** `prd-toolkit/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.prd-toolkit/VERSION`, `prd-toolkit/README.md`, `prd-toolkit/tests/test_release_0_8_9.py`, `docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md`.

- [ ] **Step 1:** `tests/test_release_0_8_9.py`: the three versions; the README's new section exists and sits after `## The prd command`; the changelog entry names `prd help`, `--json`, `--key`, `--rule` and the PRD version. See it fail.
- [ ] **Step 2:** Version 0.8.9 in the two manifests; `vendor` writes `VERSION`. The manifest description gains the help catalogue in a few words.
- [ ] **Step 3:** README: a section `## Help` (what `prd help` prints, the four forms, the JSON envelope, `PRD_HELP_FILE`, that a copy vendored before 0.8.9 has no `help` command), and the changelog entry: what it adds, that nothing existing changes, that a repository gets it with its next `install`, the PRD version, and that the eval suite was not rerun because no skill's text changed.
- [ ] **Step 4:** The priority plan: mark 0.8.9 delivered.
- [ ] **Step 5:** Both suites; `scripts/ci-local.sh`, all five jobs. Commit `release 0.8.9: a help catalogue, prd help`. **Stop: push and the pull request wait for the owner's word.**
- [ ] **Step 6, after the merge, on the owner's word:** install 0.8.9; remove the worktree and branch; update the site's two pages; tell the client session that asked for the catalogue the version.

---

## Self-review

- **Spec coverage:** §3 → Task 1 FR-e, Task 2; §4 → FR-f, Task 2; §5 → FR-a to FR-d; §6 → FR-g, Task 2; §7 → Task 1; §8 → Task 2's unit tests, Tasks 3 and 4; §9 → Task 5.
- **Added to the spec:** `PRD_HELP_FILE`, with its reason, recorded in the spec's Revisions in Task 1.
- **Left to the tools on purpose:** the IDs, the version level and the adoption state's acceptance (Task 1 says what to do if a tool refuses).
- **Names:** `DESCRIPTION`, `helpcat.py`, `PRD_HELP_FILE`, `prd_help.py`, `help.yaml` are spelled one way throughout.
