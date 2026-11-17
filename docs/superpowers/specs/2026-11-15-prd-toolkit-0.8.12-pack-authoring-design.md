# prd-toolkit 0.8.12: a pack written from two adopted PRDs, and cards that say where — design

> **Date:** 2026-11-15
> **Author:** Ivan Histand & Claude Code
> **Status:** Approved by the owner 2026-11-15. Plan: `../plans/2026-11-15-prd-toolkit-0.8.12.md`.
> **Extends:** `2026-11-03-prd-toolkit-0.8-umbrella.md` (its 0.8.12 row), the backlog
> `2026-11-08-prd-toolkit-0.8.6-backlog.md` (item 1, pack authoring) and the priority plan
> `../plans/2026-11-14-prd-toolkit-engine-ports.md`.
> **Needs:** 0.8.11 (released).

## 1. Why

**Packs.** A repository of a kind no pack covers can be adopted today: its contract types are
declared as custom types in section 7 of its PRD, each with a validator command, and its Levels,
harness slots, standards and skills are written out in the PRD. The second repository of that kind
has to write all of it again, and the two drift. A pack is how that knowledge is shared, but writing
one is undocumented hand work: the two packs that exist were each written by reading a PRD and
copying its tables into a manifest.

**Cards.** A card in the decision inbox names its gate and quotes its evidence, but an owner with
several areas cannot tell at a glance which one an error belongs to, or open the thing it is about.

**Success:** from two adopted PRDs of one kind, one command proposes a pack, the owner decides what
goes in, and the pack is written into a plugin, checked, and adopted by both PRDs with no change to
what either produces. And every card says its area and links to where the trouble is.

## 2. Scope

In scope:

1. `prd pack compare`: what two PRDs share (§3).
2. The skill and command `/prd-toolkit:prd-pack`: a proposal, the owner's decisions, the pack
   written into a plugin (§4, §5).
3. `prd pack check`: the written pack against both PRDs (§6).
4. Moving a PRD onto a pack lifted from its own custom types, as a patch (§7).
5. Cards: an area on every card that has one, and a URL from the error entry or its area (§8).
6. The toolkit's own PRD, the evals, the proof and the release (§9, §10).

Out of scope: a pack from repositories that have no PRD; a pack from one PRD alone; drafting harness
helper code, clarify questions or a skill for the pack; a pack that lives in the repository that
uses it; widening an existing pack from a third repository; publishing a plugin; conversion to
another pack (0.8.13).

## 3. The comparison: `prd pack compare <prd A> <prd B>`

Read-only and deterministic. It loads both PRD folders and prints, part by part, what they share and
where they differ. Each line says which PRD it comes from: `both`, `A` or `B`.

| Part | What is compared |
|---|---|
| Contract types | the section 7 rows whose Validator is neither `built-in` nor `pack`: the type's name, its Files glob and its validator command |
| Target kinds | for each such type, the `<type>:` prefix its test cases' `target:` values use, and how many cases use it in each PRD |
| Levels | the rows of `testing.md` Levels: level, command, environment, gate, timeout |
| Harness | each slot of `testing.md` Harness, by slot name; the text when it is the same in both, and both texts when it differs |
| Standards | the section 5 rows that are `enforced`: object glob and linter command |
| Skills | the section 6 rows that are `required` or `recommended`: activity and skill |
| Vocabulary | words that occur in the requirement titles and acceptance criteria of both PRDs and of neither built-in pack's vocabulary, outside code spans, with the count in each; a candidate list for a person to cut, never a decision |

"The same" is exact equality after the whitespace of a cell is collapsed; nothing is matched by
resemblance. `--json` prints `{"interface": 1, "kind": "pack.compare", "a": …, "b": …, "parts": {…}}`;
exit 0 printed, 1 when the two PRDs share no custom contract type (there is no pack to write), 2
usage or a folder that is not a PRD.

## 4. The skill: `authoring-packs`, `/prd-toolkit:prd-pack`

1. **Preconditions.** Both PRDs are Approved and lint clean, and each holds one or more custom
   contract types. Otherwise the skill says what is missing and stops: a repository with no PRD is
   adopted first (`/prd-toolkit:prd-adopt`).
2. **Compare** (§3), and read both PRDs' contract files of the shared types.
3. **The proposal.** One message: the pack's name (the owner's, or a proposed one); each manifest
   item with where it comes from; for each difference between the PRDs, both sides and a recommended
   resolution with its reason (take A's, take B's, leave it out of the pack so each PRD keeps its
   own); the vocabulary candidates; and the to-do list (§5). Nothing is written.
4. **The owner decides** each item: in, out, or which side. One reply may decide them all, after the
   proposal is shown.
5. **Where it goes.** The owner names a plugin checkout; the pack is `prd-packs/<name>/` there, on a
   new branch of that repository. With none named, the skill scaffolds a minimal plugin folder at a
   path the owner gives (a manifest, a README and the pack) and says that publishing it is the
   owner's. It never pushes, publishes or installs.
6. **Write** (§5), **check** (§6), and commit on that branch.
7. **Report:** what was written, the check's result, the to-do list, and the next steps: install the
   plugin, then move each PRD onto the pack (§7).

The rules: every manifest item comes from a line of one or both PRDs and the report says which;
nothing a PRD does not hold is added (no helper, no rule, no level); a difference is the owner's to
settle, never averaged; the PRDs themselves are not edited by this skill.

## 5. What is written

- **`pack.yaml`:** `pack`, `version: 0.1.0`, `toolkit` (the range the built-in packs declare),
  `description`, and the decided `contract-types`, `target-kinds`, `levels`, `harness`, `standards`,
  `skills` and `vocabulary`. `builder-tests` is written only when both PRDs' Levels agree on having
  no unit level.
- **Validators.** A custom type's validator is a command in the PRD. When the command runs a file
  of the repository, that file is copied into the pack and the manifest's command names it through
  `${PACK}`; when it is a self-contained command, it is copied as it stands. When the two PRDs'
  validators differ, the owner picks one (step 4); the skill merges none.
- **`README.md`:** what the pack is for, where each part came from, and the to-do list: the harness
  helpers each PRD's tests use that the pack does not ship, the clarify questions an interview for
  this kind would ask, and the rules a skill for it would need. Each item names the files in the
  example repositories a person would start from.
- Nothing else. No helper code, `clarify.md`, `rubrics.md` or skill is drafted.

## 6. The check: `prd pack check <pack dir> <prd A> <prd B>`

1. The manifest loads with the toolkit's own loader (the keys, shapes and `toolkit` range).
2. For each contract type of the pack and each PRD, the pack's validator runs on that PRD's files of
   the type, from the PRD's root, as lint runs it: exit 0.
3. **Each validator can fail.** `<pack dir>/samples/<type>/bad.*` holds one or more files the
   validator must refuse; the check runs it on each and requires a non-zero exit. A type with no
   sample fails the check. The skill writes the samples in step 6 by breaking a copy of a real
   contract file in one named way, and the README says how.
4. Each `target-kinds` entry names a type of the pack, and each Levels command's first word is found
   on PATH.

One line per finding, `<pack file or PRD file>: <what>`; exit 0 clean, 1 findings, 2 usage. `--json`
prints `{"interface": 1, "kind": "pack.check", "findings": […]}`.

## 7. Moving a PRD onto the pack lifted from it

Changing the pack of an area that holds built, verified or live blocks is a conversion, and stays
refused until 0.8.13. A lift is narrower: the pack declares the contract types the PRD already
declares as custom types, so what the PRD produces does not change.

`prd change pack <prd dir> <name> <X.Y.Z> --lift`:

- **Allowed when** the PRD names no pack (it runs on the default), the pack resolves, and every
  contract type the pack declares is a custom row of the PRD's section 7 with the same Files glob.
- **It writes** the section 1 `Pack:` line, turns each of those section 7 rows' Validator cell into
  `pack`, and records the change as a patch, `pack <name> <X.Y.Z> lifted; pending`, leaving the tree
  uncommitted, as `prd change pack` does for a version move.
- **Then**, as for a version move: `hooks install` from the plugin vendors the pack, lint must exit
  0 (the pack's validators now run where the PRD's own did), and the owner approves with the dry-run
  record `no dry run (pack lifted)`.
- **Refused**, each with its reason: the PRD already names a pack; a type of the pack is not a
  custom row of the PRD, or its glob differs; the pack does not resolve; uncommitted changes in the
  PRD folder.
- The PRD's own Levels, harness, standards and skills stay as they are: they already say what the
  pack's defaults say, or the owner chose to keep a difference.

## 8. Cards that say where

**The area.** Every gate gains `area`, a list of area names (empty when it has none):

| Gate | Its areas |
|---|---|
| error-class | the areas of the blocks its entry's `Touches:` names, then of the blocks that own a test case `known-failing` on it, each once, in the PRD's order |
| signoff | the area of the test case |
| approval | the areas of the blocks the change touches |
| adoption | the area being adopted |
| deploy-step | none: a run deploys the PRD |

**The URL.** A gate gains `url`, a string or null.

- **On an error entry:** one optional line, `URL: <address>`, after `Touches:`. `prd error new`
  takes `--url <address>`, and `prd error url <prd dir> <E-id> <address>` sets or replaces it later
  (`-` removes it). The address is where the trouble is: a page, a dashboard, a failed run.
- **On an area:** the `Target:` line gains an optional third part, `url <address>`, after the pack
  and the output language: `Target: output language en, url https://example.com/orders`. A file may
  hold a `Target:` line with the URL part alone.
- **Which one a card shows:** an error-class gate takes its entry's URL, else the URL of its first
  area that has one. A signoff or adoption gate takes its area's. An approval gate takes its area's
  only when the change touches one area. Otherwise null.
- Lint checks the form of both: `http://` or `https://`, no white space. Nothing fetches a URL.

**Where they show.** `prd gates list` prints the area after the gate's title, in brackets, when
there is one; `prd gates list --json` and the inbox's card carry `area` and `url`. The inbox page
shows a line under the title, `Area: <names>` or `Area: none`, and the URL as a link that opens in a
new tab. `prd status`'s Next part is unchanged: its gate items carry the gate's title as before.
Fields are added and none is removed or renamed, so `interface` stays 1.

## 9. The toolkit's own PRD

Two new adopted areas, each written before its code, as `help`, `status-next` and `practices` were:

- **`pack-authoring`:** `prd pack compare`, `prd pack check` and the `--lift` form of
  `prd change pack`. Boundary: the new files (`prd_pack.py`, `prdlint/packcompare.py`,
  `prdlint/packcheck.py`); the edit to `change.py`, in an area not yet adopted, is made by the same
  build.
- **`card-context`:** the `area` and `url` of a gate, the entry's `URL:` line with `prd error new
  --url` and `prd error url`, and the `Target:` line's `url` part. Boundary: one new file
  (`prdlint/cardcontext.py`) that derives both; the edits to `gates.py`, `errors.py`,
  `prd_error.py`, the inbox page and the lint rules that read an entry and a `Target:` line are made
  by the same build. `prdlint/model.py`, which parses both, is in the adopted `lint-cli` Boundary,
  so the requirement for each parse is written where the commit hook will find it: the change's
  first step settles whether that is a new `lint-cli` requirement or the new area's.
- The lint rule count does not change. Expected level: minor (7.0.0 to 7.1.0), unless an existing
  test case pins something these touch, which the change's `bump` step decides.
- The skill's behaviour is not specified in the PRD: the `skills` area is adopted last. It is
  covered by evals and the proof.

## 10. Evals, proof and release

- **New eval cases** for `authoring-packs`: it stops when a PRD has no custom contract type; every
  manifest item in its proposal names the PRD it came from; a difference between the PRDs is shown
  with both sides and not merged; nothing is written before the owner decides; no helper, clarify
  file or skill is drafted; it pushes and installs nothing. And for the cards: the handling-errors
  skill passes a URL the report gives to `prd error new --url`.
- **Rerun** the cases of the skills whose text changes. A case that cannot run for E-022 is recorded
  as such.
- **The proof**, recorded in an acceptance record: two static web sites hosted on the same platform,
  neither with a PRD today. One area of each is adopted with custom contract types (the owner
  confirms each in the adoption form); then compare, the owner's decisions, the pack written into a
  plugin the owner names, the check, and both PRDs lifted onto it with lint clean. The proof also
  sets a `Target:` URL on one area and a `URL:` on one error entry and shows both cards.
- Version 0.8.12; eleven skills and twelve commands; README sections for pack authoring and for the
  cards; the changelog entry with its upgrade note.
- The priority plan marks 0.8.12 delivered.

## 11. Decisions and what was set aside

- **Two adopted PRDs are the input** (owner): everything in a pack comes from text the owner
  confirmed during adoption. A pack from bare repositories, or from one PRD, is set aside.
- **The pack goes into a plugin** the owner names, or a new minimal one (owner). A pack inside the
  repository that uses it is set aside.
- **Manifest and validators, with a to-do list** (owner). Helper code and skills for a pack are
  written by a person.
- **The proof pair is two static web sites** (owner); a pair of plugin marketplaces and a pair of
  desktop apps follow as later runs of the same command.
- **A lift is a patch, not a conversion.** It is allowed only where the pack declares what the PRD
  already declared, so no output changes; everything wider waits for 0.8.13.
- **Both URLs** (owner): the entry's own, else its area's. **Every card that has an area shows it**
  (owner).
- **The area's URL is a part of the `Target:` line,** which already says what the area produces. An
  adoption-map column was the alternative; a new project has no adoption map.
- **Set aside:** an area on `prd status`'s Next items beyond what they carry; a URL per environment
  on a card (the Environments tables already hold those); checking that a URL answers.

## Revisions

- **2026-11-15, while the requirements were written** (each is carried by an acceptance criterion):
  - **A third area, `standards-run`, for a confirmed error** (owner): a standards row is never run on a
    file under the vendored copy `.prd-toolkit/`, in the pre-commit hook and in the generated CI job
    (E-025). The fix rides with this release as part of the same PRD change.
  - **`prd gates list` as text is unchanged** (§8). The area in brackets after a title would have
    changed an existing test case's expectation and made the PRD's version major. The area and the URL
    are carried by `--json` and by the inbox's card, which is where the owner asked for them.
  - **The list is a new field, `areas`** (§8). The adoption card already carries `area` as a string,
    which a client reads; it stays, beside `areas`. No field changes type.
  - **After a lift a context pack names the pack** on its profile line and prints the pack's harness
    defaults (§7). That follows from naming a pack and is accepted; lint's findings, the PRD's own
    tables and its test cases do not change.
  - **Two installed packs of one name and version:** the lift is refused and names each source;
    `--source <source>` picks one (§7).
  - **The two parse requirements live in `card-context`** (§9): the commit hook asks only for a valid
    `Refs:` trailer on a Boundary file, and the build check has no area check.
  - **Twelve requirements in three areas**, with their own split (§9).
