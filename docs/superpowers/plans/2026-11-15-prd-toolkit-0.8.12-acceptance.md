# prd-toolkit 0.8.12: the proof run — acceptance record

> **Date:** 2026-11-16 and 2026-11-17
> **Plan:** `2026-11-15-prd-toolkit-0.8.12.md`, Task 5. **Spec:** `../specs/2026-11-15-prd-toolkit-0.8.12-pack-authoring-design.md`.
> **Result:** passed, with the findings below. Nothing in either site's repository, or in the new plugin, is pushed.

## What was run

Two static web sites hosted on the same platform, each in its own repository, neither with a PRD at
the start. Called site A and site B here. Every session loaded the plugin from the release branch
(its manifest still reads 0.8.11; the bump is the release commit). The headless sessions ran as
`claude -p`, model `opus`; every owner decision was asked in the controlling session's chat or in the
decision inbox, and passed to the next headless session verbatim.

1. **Adoption of one area in each site** (`/prd-toolkit:prd-adopt`), the area `site`: the pages and the
   hosting configuration, with two custom contract types, `pages` and `hosting`, each with a
   validator script committed in the repository.
   - Site A: 23 requirements, 35 test cases. The owner answered the 31 confirmation items in the
     decision inbox, served by the controlling session. Approved at 1.0.0 with 30 T-ids passing and 5
     `known-failing` on five open entries; hooks and CI installed.
   - Site B: 22 requirements, 58 test cases, the same two type names, and the two validators copied
     byte for byte from site A. Approved at 1.0.0 with 51 T-ids passing and 7 `known-failing`.
   - Site B does things site A does not (two pages at the same path on two hosts, path redirects,
     host-based rewrites, a sitemap line), which the validators refused. The owner chose to extend
     the shared validators with four optional additions; site A's contracts still passed unchanged,
     and both repositories took the new files.
   - On site A, one entry was then fixed through the error loop (`/prd-toolkit:prd-error`, a
     `--fixes` build, resolve, `prd error check` exit 0), and two patch changes were approved.
2. **`/prd-toolkit:prd-pack`** on the two approved PRDs. `prd pack compare` exit 0: both contract
   types, both Levels rows, nine Harness slots and four skills rows marked `both`; seven Harness slots
   differ; 104 vocabulary candidates. The headless session wrote nothing and ended with the proposal.
   The owner decided every item (the name `static-site`, the proposed description, every `both` item
   in, all seven differences out, no vocabulary, a new minimal plugin). A second session re-ran the
   comparison (byte-identical to the one the owner read), wrote `pack.yaml`, the two validators
   copied unchanged, one `bad.yaml` sample per type and a README with the provenance of each item
   and the to-do list, ran `prd pack check` (exit 0) and committed on a new branch of a new local
   repository. No helper, clarify file or skill was drafted.
3. **The lift.** The owner added a local marketplace and installed the plugin;
   `prd lint --list-packs` then listed `static-site 0.1.0 (<plugin>@<marketplace>)`. In each site:
   `prd change pack … --lift`, `prd hooks install`, lint exit 0 with the pack's validators, the
   integration suite as before (site A 44 passed and 2 expected failures; site B 37 passed and 5),
   the verdict with `no dry run (pack lifted)`, the owner's approval of each patch, and
   `prd change approve`. Each approval commit holds `.prd-toolkit/packs/static-site/` whole and
   `.prd-toolkit/pack-sources.json`, with `prd.md`, CLAUDE.md and the READMEs: AC-060.9 (E-026) on
   two real repositories.
4. **The cards.**
   - Site A: a patch gave area `site` a `Target: url <address>` line, the address given by the
     owner. A later patch that touches a requirement of the area then gave the gate
     `approval:<branch>` with `"areas": ["site"]` and `"url"` the area's address in
     `prd gates list --json`; the owner opened the inbox page, confirmed the card showed the area and
     the link, and approved on the card.
   - Site B: a defect found by probing the live site was recorded with
     `prd error new … --url <address>` and proposed. Its gate `error-class:E-007` carried
     `"areas": ["site"]` and `"url"` the entry's own address; the owner confirmed the class on the
     card.

## What the pack holds

`pack.yaml` (`static-site` 0.1.0, `toolkit: '>=0.8.0,<0.9'`): contract types `pages`
(`contracts/pages.yaml`) and `hosting` (`contracts/hosting.yaml`), each validated by
`uv run --quiet --script ${PACK}/validate_<type>.py`; target kinds for both; Levels `integration`
(local, build) and `smoke` (production, deploy); nine Harness slots (Lifecycle, Environment switch,
Database access, Persistent environments, Layout, Fixtures, Browser identity, Leaks, Acceptance);
four skills rows; `vocabulary: []`; `builder-tests: none`.

Its to-do list names, with the files to start from: shared harness helpers (each site's test files
hold their own HTML reader and smoke client), clarify questions for this kind of site, and the rules
of a skill for it.

## Findings

Defects of this release were fixed and their step rerun; the rest is the owner's to decide and is
listed in the release report.

1. **The adoption's dry-run gate converges slowly on free-form test-case keys.** Site A needed more
   than a dozen rounds: each fresh sample of five T-ids found `expect` keys whose reading the Harness
   never stated. None of the questions was about what the site should do. Three standing answers
   from the owner (take a fact of the committed pages; take the reading the current suite passes
   with; bring the PRD in line with an answer already given) and one sweep of every key ended it.
   Site B, given those lessons in its first prompt, converged in four rounds.
2. **An answer on an error-class card commits `errors.md` alone** while the rest of a draft PRD is
   still untracked, and records only the class: the adoption then lacks the intended behaviour and
   has to ask again. Seen on both sites.
3. **A pack's samples prove little when the validator reads the repository.** Both validators find
   the repository root above the contract file; inside the plugin that root holds no site files, so
   each sample is refused for missing files as well as for its named break, and `prd pack check`
   cannot tell the two apart. AC-059.7's second run (E-027) did its job: the validators run from the
   pack folder on each PRD's files.
4. **`prd change bump` answers `needs judgment` for a lift** (the `Pack:` line and the `pack`
   Validator cells), though `prd change pack --lift` itself records a patch.
5. **A change that only adds an area's `Target:` line shows no area on its approval card**
   (`"areas": []`, `"url": null`): the areas come from the blocks a change touches (AC-062.3), and
   such a change touches none.
6. **The vocabulary candidates are mostly ordinary words** ("with", "that", "each") and the sites'
   own names; the owner kept none.
7. **A first adoption wrote a `unit` Levels row with no unit test case**, so the generated CI had a
   job that runs a folder that does not exist. Removed by a patch change; site B was told not to
   write one.
8. **The black-box tester's guard blocks it from reading its own background run's output**, so it
   reruns each level in the foreground. Seen in most suite runs.
9. **`prd build-check --stale` passes over test files that are not committed yet**, so it reports
   nothing stale during an adoption.
10. **The vendored copy refuses `hooks check`** ("run check from the plugin"); the adoption's last
    step has to run it from the plugin's scripts.
11. **The pack procedure's commit command adds no attribution line**, and its report told the owner
    to commit the vendored pack by hand after a lift, which AC-060.9 made unnecessary. The second is
    corrected in `skills/authoring-packs/running-a-pack.md`.
12. **After a lift, each repository keeps its own validator scripts**, now unused. Nothing removes
    them or says to.
13. **A desktop client opened with a checkout's path did not load it** and showed two empty windows;
    reported to that client's repository.

## Not covered

- A pack with a vocabulary, a standards row or a harness helper: the two PRDs gave none.
- A pack written into an existing plugin; a pack name already taken; two plugins holding the same
  pack (`--source`).
- A lift refused by lint, and a lift of a PRD whose section 7 differs from the pack's globs.
- The deploy of either site: every smoke-level requirement of the fixed entry stays `verified` until
  one runs.
- The decision inbox's card for a `signoff:` or `deploy-step:` gate.
