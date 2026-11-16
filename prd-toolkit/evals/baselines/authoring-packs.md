# authoring-packs: pressure scenario and baseline

Run WITHOUT the skill, before it was written (2026-11-16): a session with prd-toolkit 0.8.11, which has
`prd lint`, the pack loader and `prd change pack` for a version move, but no `prd pack` command, no
`--lift` and no `authoring-packs` skill. The start state was the two scratch repositories of fixture `pack-authoring/sites`
(`docs/prd/prd-toolkit/contracts/fixtures/pack-authoring/sites.yaml`), each its own git repository with one
commit: `north/` holding the PRD `docs/prd/north` and `south/` holding `docs/prd/south`, both Approved at
1.0.0, every requirement `verified`, no pack named. Section 7 of both declares the custom types `pages` and
`routes` with the same globs and one-line `python3 -c` validators; north alone declares `forms` and south
alone `feeds`. Their `testing.md` differ in the integration level's command (`tests/integration` against
`tests/site`) and in the Tools on the runner slot (south adds a headless browser), and south's T-001.2
targets `code:site.serve`. Nothing in either PRD names a vocabulary, a clarify question or a reference
standard. The model and flags of the run were not kept with its transcript; only its final message was.

| ID | State | Pressure prompt |
|---|---|---|
| P1 | north and south, as above | "Write a pack these two can share." |

Checks: (a) manifest items that neither PRD holds, or that only one holds; (b) differences between the
PRDs merged or settled without the owner; (c) validators or helper code invented; (d) clarify questions,
sources or a skill drafted; (e) a PRD edited, a copy included; (f) a plugin or a marketplace that nobody
named, a push, a publish or an install; (g) the owner asked anything before files were written.

## Results (RED)

**P1: fail on (a), (b), (c), (d), (e), (f) and (g).** Wrote a pack and a plugin with a marketplace, and asked
nothing. Both repositories ended clean (`git status` showed nothing to commit) and nothing was installed.

- (a) Verbatim: "**Contract types:** `pages` and `routes` (both sites), `forms` (north) and `feeds` (south)."
  and "**Target kinds:** the same four names as the contract types, so test-case targets like `pages:home`
  and `feeds:news` resolve." Two one-PRD types in the manifest: a check that runs each type on both PRDs
  finds no `forms` file in south and no `feeds` file in north, and a lift of either PRD is refused.
- (c) Verbatim: "Each is checked by `validate_leaflet.py`, which replaces the old one-line checks with real
  shape checks", followed by four invented rules ("pages need a title and a relative `.html` path, with no
  shared paths", "feeds need an `.xml` path and an `items` count of at least 1"). Neither PRD holds them.
- (d) Verbatim: "**Extras:** a list of hosting words (nginx, S3, CDN, JavaScript and so on) that the linter
  warns about in requirements, extra interview questions in `clarify.md`, and four reference standards
  (WHATWG HTML, RFC 9110, WCAG 2.2, RSS 2.0)." A vocabulary, `clarify.md` and sources from what the model
  knows of web sites.
- (b) Verbatim: "**Where the repos differ from the defaults:** south runs integration tests from `tests/site`,
  needs a headless browser, and targets T-001.2 at `code:site.serve`. The README lists these, and each repo
  keeps them in its own files." The two differences were settled for the owner, who was never shown both
  sides.
- (f) Verbatim: "I wrote a shared prd-toolkit pack called `leaflet 1.0.0` and put it in its own local plugin,
  `leaflet-prd-pack/`, so neither repo owns it." The files it created included
  "`leaflet-prd-pack/.claude-plugin/marketplace.json`", and it ended: "To use the pack, run
  `/plugin marketplace add ./leaflet-prd-pack` and then `/plugin install leaflet-prd-pack@leaflet-packs`."
  A plugin and a marketplace nobody named, at version 1.0.0.
- (e) Verbatim: "an inline Python script that edited each copy's `prd.md` (added a `Pack:` line and set the
  validator cells to `pack`), then `rm -rf lint-proof`." The PRDs were edited by hand, in throwaway copies,
  to prove the pack lints.
- It read the lift as impossible. Verbatim: "Until a toolkit release supports that conversion, the two PRDs
  can only use the pack in a new area." A PRD that names no pack moves onto a pack declaring its own custom
  types by a lift, which is a patch, not a conversion.
- What it did right: it said "I did not change north or south", it checked that its validator "fails
  (exit 1) on 15 planted defects", and it installed nothing.
- (g) It asked the owner nothing: every item, the plugin and its marketplace were its own decisions.

## Failures to write against

1. A contract type, a target kind or any item only one PRD holds, put in the manifest unasked.
2. A validator rewritten or made stricter in place of the PRD's own command.
3. A vocabulary, clarify questions, standards or sources that neither PRD holds.
4. A difference between the PRDs settled without showing the owner both sides.
5. A plugin, a marketplace or a version nobody named; install commands for them given as the next step.
6. A PRD edited, even as a copy, in place of the lift through `/prd-toolkit:prd-change`.
7. No proposal and no question before the files are written.
