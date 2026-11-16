# prd-toolkit: the open 0.8.x items and four ideas from an earlier prototype, in priority order — plan

> **Date:** 2026-11-14
> **Author:** Ivan Histand & Claude Code
> **Status:** Draft, for the owner's review. Not approved; nothing is built.
> **Extends:** `docs/superpowers/specs/2026-11-03-prd-toolkit-0.8-umbrella.md`. **Decided (owner,
> 2026-11-14):** the invocation release is inserted as 0.8.8; best practices move to 0.8.9 and
> conversion to 0.8.10, their content unchanged. The umbrella's Revisions note, its §4 rows and
> the backlog file's Revisions note are edited on the 0.8.8 spec branch, cut from `main` once
> 0.8.7 is merged: the current umbrella text exists only on `release/0.8.7`, which is built and
> waiting to be pushed.
> **Carries:** every open item of 0.8.7 (`plans/2026-11-11-prd-toolkit-0.8.7.md`), of the
> backlog (now 0.8.11's; `specs/2026-11-08-prd-toolkit-0.8.6-backlog.md`) and of the umbrella's 0.8.8 and 0.8.9
> rows, as they stand on `release/0.8.7` (d23cdfe).
> **Decided later (owner, 2026-11-14, after the 0.8.8 build):** a help catalogue (0.8.9) and a Next
> part in the status report (0.8.10) are inserted after 0.8.8, each its own release; best practices
> move to 0.8.11 and conversion to 0.8.12, their content unchanged. The priority order below and the
> umbrella's §4 rows say so.
> **Decided later (owner, 2026-11-15, in the 0.8.11 brainstorm):** 0.8.11 is best-practice sources and
> the skills a PRD needs; pack authoring from an example repository becomes its own release, 0.8.12;
> conversion moves to 0.8.13, its content unchanged.
> **Source:** the review of an earlier prototype of a PRD command-line tool against prd-toolkit 0.8.6.
> The prototype is retired (owner, 2026-11-15) and its repository is gone: prd-toolkit is the only
> line of development, and what this plan keeps from the prototype is the ideas below, restated here in full.

**Goal:** Bring four ideas from the prototype into prd-toolkit. Three are planned here: a replay that
proves a fix turned its regression test green, one `prd` command with an Antigravity wrapper, and
a check of the code's public surface against the contracts. The fourth, an approval the agent
cannot forge, is deferred to the 2.0.0 roadmap (owner, 2026-11-14); its design is kept at the end
of this document.

**Shape:** One priority list (next section) over the carried 0.8.x items and four phases for those ideas.
Each release has its own spec, plan, build and acceptance record, as every 0.8.x release has had. This document fixes the order, the design decisions and the
interfaces between phases. It is not the task-level plan of any phase: each phase's spec comes
first, then its plan (`superpowers:writing-plans`), then the build.

**Tech stack:** Python 3.11+, uv script headers, git, `ssh-keygen -Y` (OpenSSH 8.2+), pytest. No
new Python dependency in any phase.

## Global constraints

- Each phase lands by pull request from a worktree; `main` is what users install.
- A change inside an adopted area (`lint-cli`, `lint-structure`) starts with
  `/prd-toolkit:prd-change`. Phase 3 adds a lint rule, which changes `--list-rules` output and
  the README's "40-rule" count: a lint-cli change.
- Existing script names, usage lines and exit codes do not change. Tests in `tests/prd/` pin them.
- Every script added joins `VENDORED` in `prdlint/hooks.py`, and the vendored copy is refreshed in
  the same commit (`prd_hooks.py vendor docs/prd/prd-toolkit`).
- A new machine-readable output is one JSON document through `prdlint/interface.py`
  (`interface: 1`).
- Pack manifests keep `toolkit: ">=0.8.0,<0.9"`. Phase 3 adds an optional pack key, which is
  additive; if the owner wants these phases numbered 0.9.x instead, the pack range moves in the
  phase that opens 0.9.
- Skill edits follow `superpowers:writing-skills`, and the evals run before the version bump.

## Priority order

| # | Release | Contents | From | Size | Needs |
|---|---|---|---|---|---|
| 1 | **0.8.7** | Released: merged to `main` | 0.8.7 plan | done | — |
| 2 | **0.8.8** | **Invocation**, released: merged to `main`: uv environments no longer pile up per clone (PRDAnvil/prd-toolkit#2) and one `prd` command (phase 2), which share one upgrade note; the small leftovers (carried items C1 to C3); the umbrella and backlog renumbering. Delivered wider than first written: every skill, command and agent line runs the launcher (the 0.8.8 spec's Revisions) | backlog item 3; prototype | done | 0.8.7 |
| 3 | **0.8.9** | **Help catalogue**, delivered: a machine-readable catalogue of the PRD format's fields and of every lint rule, for the terminal and for any client: `prd help`, with `--json` | owner, 2026-11-14 | done | 0.8.8 |
| 4 | **0.8.10** | **Next part in the status report**, delivered: an ordered list of what a PRD needs next, first in `prd status` and in its `--json` | owner, 2026-11-14 | done | 0.8.8 |
| 5 | **0.8.11** | **Best-practice sources**, delivered, and finding, installing or writing a skill a PRD needs | umbrella row, backlog item 1 | done | 0.8.0 |
| 6 | **0.8.12** | **Pack authoring** from an example repository: a pack proposed and written from two repositories that declare the same custom contract types; and, added by the owner on 2026-11-15, cards in the decision inbox that show the area an issue is for and a URL when it has one | backlog item 1; owner | large | best practices |
| 7 | **0.8.13** | **Conversion:** retarget an area or a PRD to another pack | umbrella row | large | best practices |
| 8 | after 0.8.13 | **Errors:** red replay (phase 1) and a close for an error outside every adopted Boundary, which closes E-017 | prototype; backlog item 5 | small | none |
| 9 | after 0.8.13 | **Surface check** (phase 3) | prototype | medium | conversion, so the extractor key is designed once for retargeted packs |
| 10 | after | **Antigravity wrapper** (phase 4), if its spike passes | prototype | large, uncertain | the `prd` command |
| — | every release | **One area adopted** in the toolkit's own PRD: `lint-ids` next, then `lint-testcases` | backlog item 2's policy | medium each | the release that last reshaped the area |
| — | before 1.0.0 | **A production release path** (PRDAnvil/prd-toolkit#14): tagged releases from a commit that passed CI and the evals, each with its upgrade note; a marketplace entry on the latest release, with pinning and rollback; a standalone `prd` install for macOS and Linux; one version everywhere, checked by CI; a vendored copy that records the release it came from. A prerequisite for 1.0.0 (owner, 2026-11-14) | issue #14 | not sized | the `prd` command (0.8.8) |
| — | 2.0.0 roadmap | **Signed approvals** | prototype | medium | one of its three triggers |

Why this order:

- **0.8.7 first.** It is built and `ci-local` passed 5/5 on 2026-11-11. Every later branch should
  be cut from a `main` that holds it. Done: 0.8.8 was cut from it.
- **Invocation before the features.** Issue #2 is a defect in every install today: about 90 GB
  and 27 million files on the owner's machine before it was cleared, and the hooks keep adding.
  The fix rewrites how hooks, CI and skills start the scripts, and so does the `prd` command.
  Done together they cost each vendoring repository one reinstall; done apart, two.
- **Then the two features, with no further inserts.** Best practices has been moved back seven
  times since 2026-11-03, each time by a fixes release. The owner moved it once more on
  2026-11-14, for a defect that grows daily. After that, fixes ride with a feature release or
  wait. (The owner then inserted the help catalogue and the Next part on 2026-11-14, below.)
- **The help catalogue and the Next part before best practices** (owner, 2026-11-14). Both serve
  any client as much as the terminal, and each is its own release: 0.8.9 gives
  a client the format's fields and the lint rules as data, 0.8.10 tells it what a PRD needs next.
- **Errors after the features** because it is small and nothing waits on it; E-017 stays
  `confirmed` meanwhile, as the owner chose on 2026-11-11.
- **Surface after conversion** because both reshape what a pack declares.

**The item no release holds.** The PRD's goal is every area adopted before the plugin's 1.0.0.
`adoption.md` lists 21 areas; 2 are adopted. At one per release that is 19 more releases, and
`lint-structure` alone produced eight errors and a fixes release. This is the largest item on the
list. It needs its own decision: adopt faster, group small areas, or drop the 1.0.0 condition.

**What 1.0.0 waits on.** Two things: every area adopted (above), and the production release path
of issue #14 (owner, 2026-11-14). Today a merge to `main` is the release: there are no tags, the
marketplace entry follows the default branch, and the version is kept by hand in four places. The
issue's design points: a `prd` on the PATH never replaces a repository's own `.prd-toolkit/prd`;
the name is checked for clashes; downloads carry checksums; and the release runs from the
toolkit PRD's own `operations.md` runbook through `/prd-toolkit:prd-deploy`. It is not ordered
among the 0.8.x releases; it takes its place when 1.0.0 is planned.

**The prototype had drafts of best-practice sources and of conversion.** What 0.8.11 took from the
first is in its spec (`specs/2026-11-15-prd-toolkit-0.8.11-practices-design.md`): one record of
sources, standards and skills, approved by the owner. The conversion draft's one idea worth keeping
is a warning for platform words, which the toolkit already has as `platform-word`.

## Carried items

Everything still open from 0.8.7 and the backlog (now 0.8.11's). Items already done (backlog
items 2 and 4, the lint-structure fixes E-009 to E-016, E-018, the full command names) are not
listed.

| ID | Item | Where it goes |
|---|---|---|
| R1 | 0.8.7 is not pushed: 11 commits on `release/0.8.7`, upstream unset | done: merged to `main` |
| R2 | After 0.8.7 merges: install it, remove `.worktrees/release-0.8.7`, update the site's two pages | priority 1 |
| B1 | Best-practice sources (backlog item 1) | priority 5 |
| B3 | One uv environment per script path, per clone (backlog item 3, issue #2). Likely fix: `uv run --with … python <script>`; the vendored copies, hooks and generated CI must keep working or be rewritten by `install`, `vendor` and `ci` | addressed in 0.8.8: one `prd` launcher and one uv environment per requirements list; what remains is in its changelog entry's Known limits (the `document` pack's validator, judged tests written before 0.8.8) |
| B5 | An error in code no adopted area covers has no close; E-017 is open because of it (backlog item 5) | priority 7 |
| U9 | Conversion (umbrella row) | priority 6 |
| A1 | Adopt the next area: `lint-ids`, then `lint-testcases` | every release |
| C1 | `prd.md` line 60, "Out of scope: the repository's other plugins and the `web/` docs site", is stale since the move; a PRD patch | done in 0.8.8 |
| C2 | SHAs from `ihistand/claude-plugins` outside `docs/prd` (the plugin README's changelog, `evals/BASELINE.md`) resolve only there; add a note | done in 0.8.8 |
| C3 | `prd_error.py check` reports `Detected: changed` over a range that spans the move's SHA rewrite (c8f48cf); accept a provenance-only rewrite, or document "start the range after it" | done in 0.8.8 |
| E-019 | Seven eval scaffolds (the six deploy cases and `review-edits-nothing`) fail their own clean-tree check since 0.8.4, because `install` writes `CLAUDE.md` and the PRD READMEs, which the scaffolds never commit; their cases never run (the toolkit's `errors.md`, `proposed`) | open; the next release that touches the evals |

Parked, with no release (recorded so they are not lost): the 5-sample dry run does not converge on
a large adopted area (0.2 acceptance); the builder worktree and tester guard bind to the session's
repository, so a change set needs one session per member (0.7, R-11c); the candidates in PR #25's
body. **A `macos-app` pack**: contract types for an app's surface (screens, menus, keyboard
shortcuts, accessibility identifiers, file formats, settings), an XCTest and UI-test harness,
SwiftLint or swift-format standards rows, and a build, sign, notarize and release runbook shape; a
macOS app that uses the toolkit as a client would be its first adopter, and the pack would come out
of 0.8.12's pack-authoring flow. **adoption.md as data**: its Boundary cells are long lists in one
table cell, which makes diffs and merges poor; first a command that edits the map, and a move to one
path per line (YAML) only in a release that already changes the format.

## Follow-ups from the 0.8.8 review

One line each; none is in a release yet.

- The `document` pack's validator still runs by its file from the vendored copy: a pack version bump.
- The `core.hooksPath` marked-shim loop: `check` reports it stale and `install` cannot rewrite it
  (`ours = _ours(path) and not _hooks_path_config(repo_root)`).
- The stale-CI line that `install` and `check` print for a second PRD in the same repository.
- The unknown-command message of a vendored copy lists `publish`, which runs only from the plugin.
- `prd.md` section 1 says every script runs from `scripts/requirements.txt`; publish uses its own
  file (the next PRD patch).
- `header_deps` parses only a single-line dependency header.
- `test_launcher_without_uv` on a machine with uv under `/usr/bin`.
- An exact-match test for the generated `trace --range` line.
- The two judged-test graders that miss a launcher path built in pieces.
- The launcher alternative in graders is not tied to `.prd-toolkit` or `/scripts`.
- Stale "judged tests call `.prd-toolkit/prd_judge.py`" wording in two skills and the `document` pack.
- The first docstring lines of `prd_gates.py` and `prd_judge.py` are cut mid-sentence in `prd --help`.
- E-019: the seven eval scaffolds that fail their own clean-tree check.
- The `stops-in-review` grader of `changing-hands-off-to-change-set` fails at 0.8.7 and 0.8.8 alike.

---

## Phase 1: red replay

**What the toolkit already has.** More than the review credited. A regression test is committed as
a strict expected failure (`known-failing: <E-nnn>`), its RESULTS line is the red proof, and
`prd_error.py check <range>` verifies each Resolution line (`T-005.3 [integration], PRD 1.0.1,
fixed in 0dd4037`). The gap is narrower than "no receipt": nothing shows that the commit named in
`fixed in` is what turned the test green.

**Decision.** Replay from git, with no receipt file. Everything needed is already in the
Resolution line, so the proof is recomputable by anyone, including CI. A receipt file in
`.git/`, as the prototype kept, is local and cannot be checked by a second party.

**Files.**

- Modify `prdlint/errors.py`: add
  `replay(prd: Prd, repo_root: Path, eid: str, timeout: int | None = None) -> list[str]` — the
  findings, empty when the proof holds. It:
  1. reads the entry's `fixed in <sha>` and T-id (the `_FIX` pattern);
  2. adds a temporary git worktree at `<sha>^`;
  3. overlays the test roots (`testing.md` Layout, `Test roots:`) from `<sha>`;
  4. runs the T-id's level command from `testing.md` Levels, with its Timeout;
  5. reads the T-id's RESULTS line with `buildcheck.results_findings`' parser;
  6. removes the worktree, also on failure.
- Findings: `<E-nnn>: <T-id> passes on <sha>^; <sha> did not turn it green`, and
  `<E-nnn>: <T-id> has no RESULTS line on <sha>^` (the test could not run there).
- Modify `prd_error.py`: subcommand `replay <prd_dir> <E-nnn>`, with `--json`; exit 0 holds, 1
  findings, 2 usage.
- Modify the CI generator (`prd_hooks.py ci`): a job `prd-error-replay` that replays each entry
  the pull request's range resolves. Not in the pre-commit hook: it runs a test level.
- Skill `handling-errors/running-an-error.md` step 5: run `replay` before `resolve`.

**Decisions inside.** The whole level runs and one line is read; a per-T-id filter is a later
optimisation, since `testing.md` has no slot for one. Entries with an environment resolution
(`_ENV`) or `not a defect` are skipped: they have no fix commit.

**With backlog item 5 (carried item B5), in the same release.** `resolve` refuses a fix with no
T-id, so an error in code outside every adopted Boundary cannot close. The phase's spec decides
between a resolution form without a T-id (`fixed in <sha>, red run <test id>`, which `replay` can
check the same way, given a test id instead of a T-id) and adopting the area first. The first is
preferred here: it closes E-017 without waiting on an adoption.

**Tests that must exist.**

- `test_replay_holds` — a fixture repo with a bug commit, a test commit and a fix commit.
- `test_replay_refuses_test_that_always_passed` — the fix commit does not touch the behaviour.
- `test_replay_overlays_tests_only` — the code in the worktree is the parent's.
- `test_replay_removes_worktree_on_timeout`
- `test_replay_skips_env_and_not_a_defect`
- `test_replay_fix_is_root_commit` — `<sha>^` does not exist: a finding, not a traceback.

---

## Phase 2: `prd` dispatcher

**Done in 0.8.8** (built on `feat/prd-toolkit-0.8.8`). The design that was built is
`docs/superpowers/specs/2026-11-14-prd-toolkit-0.8.8-invocation-design.md` with its Revisions; the
text below is the plan as first written.

**Decision.** One entry point that **executes** the existing scripts; it does not import them.
`prd lint docs/prd/x` replaces its own process with `prd_lint.py docs/prd/x`, so usage lines,
stderr prefixes and exit codes stay what the adopted areas' tests pin.

**Files.**

- Create `prd-toolkit/scripts/prd` (uv script; dependency header is the union of the scripts'):
  - a table `COMMANDS: dict[str, str]` — `lint`, `trace`, `status`, `context`, `build-check`,
    `hooks`, `deploy`, `drift`, `block`, `error`, `links`, `confirm`, `judge`, `change`, `gates`,
    `publish`; phase 3 adds `surface`;
  - `prd --help` lists the commands with each script's docstring first line; `prd --version`
    prints the plugin version (`.prd-toolkit/VERSION` when vendored);
  - an unknown command exits 2 with `prd: unknown command '<x>'` and the list.
- Add `prd` to `VENDORED`; `test_vendored_copy.py` covers it.
- **With issue #2 (carried item B3), in the same release.** This phase is designed in
  `docs/superpowers/specs/2026-11-14-prd-toolkit-0.8.8-invocation-design.md`, which governs where
  it and this section differ: a `prd` launcher (an `sh` script holding the one uv line,
  `--with-requirements`, so uv keeps one environment per requirements list and none per script
  path) in front of the dispatcher, and only the callers that run a vendored copy are rewritten.
- The CLAUDE.md block and README gain one line naming `prd`.

**Tests that must exist.**

- `test_prd_table_covers_every_script` — every `prd_*.py` that has a `main` is in `COMMANDS`, so
  a new script cannot be forgotten.
- `test_prd_passes_argv_and_exit_code` — for 0, 1 and 2.
- `test_prd_output_is_the_scripts` — `prd lint --help` equals `prd_lint.py --help`, byte for byte.
- `test_prd_unknown_command`
- `test_shims_and_ci_use_no_script_mode` — no generated shim or workflow line holds `--script`.
- `test_install_rewrites_old_shims` — a repository installed by 0.8.7 is on the new form after
  `install`, and its `check` is clean.
- `test_two_clones_one_environment` — running the hook's command from two clone paths adds no
  directory to the test cache's `environments-v2` (the harness already isolates that cache,
  NFR-019).

---

## Phase 3: surface check

**Problem.** `prd_trace.py` checks that tests and commits cite the PRD, and `prd_drift.py` checks
configuration against an environment. Nothing checks that the code exposes exactly what the
contracts declare, so an agent can add a flag, a route or a table the PRD never approved.

**Decision.** The core compares two sets of item names per contract type; a pack supplies the
extractor that produces the code's set. The core already knows the contract's set
(`operation_ids`, `schema_tables`, `event_names`, `custom_items` in `prdlint/rules/contracts.py`).
Granularity in this phase is the contract's own item names; flags and fields come later.

**Pack key** (optional, additive):

```yaml
surface:
  - {type: cli, extractor: extract_cli.py}
```

**Extractor contract.** Run from the repo root, `PRD_DIR` set, timeout as the pack validators'.
Stdout is one document:

```json
{"interface": 1, "kind": "surface-items", "type": "cli", "items": ["prd_lint", "prd_trace"]}
```

**Files.**

- Create `prd-toolkit/scripts/prdlint/surface.py`:
  - `declared(prd: Prd) -> dict[str, set[str]]`
  - `extracted(prd: Prd, repo_root: Path) -> tuple[dict[str, set[str]], list[Finding]]`
  - `surface_findings(prd: Prd, repo_root: Path) -> list[Finding]`
- Create `prd-toolkit/scripts/prd_surface.py` — `<prd_dir> [--json] [--interface]
  [--write-baseline]`; exit 0, 1, 2 as the other scripts.
- `docs/prd/<slug>/contracts/surface-baseline.yaml` — per type, the undeclared items an adopting
  repo tolerates. `prd_hooks.py check` refuses a range in which a baseline list grows.
- Findings: `undeclared: <type> item '<name>' is in the code and not in <contract file>` (error
  unless baselined); `unimplemented: …` (warn in this phase).
- Add `surface` to the dispatcher's `COMMANDS` table (phase 2).
- New lint rule `surface-extractor`: a pack's `surface` entry names a type the pack declares and a
  file that exists.
- CI generator: a job `prd-surface`, emitted only when a pack of the PRD declares `surface`.
- First extractor, to dogfood: the toolkit's own `cli` custom type — the script names under
  `prd-toolkit/scripts/` against the top-level keys of `contracts/cli.yaml`. Second: `openapi`,
  comparing against a generated OpenAPI file the project's harness emits, so no code is parsed.

**Tests that must exist.**

- `test_surface_clean`, `test_surface_undeclared_is_error`, `test_surface_unimplemented_is_warn`
- `test_baseline_tolerates_and_cannot_grow`
- `test_extractor_bad_json_is_finding` and `test_extractor_timeout_is_finding` — never a traceback.
- `test_type_without_extractor_is_skipped` — and named on stderr, so a silent skip is visible.
- `test_no_surface_key_no_ci_job`

---

## Phase 4: Antigravity wrapper (spike first)

**Why a spike.** The toolkit's black-box guarantee rests on `prd_tester_guard.py` knowing that the
caller is `prd-tester`. What I know of Antigravity's plugin format comes only from the prototype's
wrapper (`plugin.json`, `hooks.json` with a `toolCall` payload, `rules/AGENTS.md`, subagents made
with `define_subagent` and `invoke_subagent`), not from its documentation.

**Spike, one day, written up as a spec section.** Answer from Antigravity's documentation and a
running hook:

1. Does a hook payload identify which subagent is calling?
2. Can a subagent be denied reading a path, by a hook or by its definition?
3. Do `SKILL.md` files load unchanged, sub-files included?
4. Is there an equivalent of slash commands?

**Gate.** If 1 and 2 are both no, the tester cannot be isolated there. Then the wrapper is not
built, and the spec records why; an advisory wrapper that cannot enforce the black-box rule would
carry the toolkit's name without its main guarantee.

**If it passes, the deliverables are:**

- `prd-toolkit/plugin.json`, `prd-toolkit/hooks.json` and `prd-toolkit/rules/AGENTS.md` beside
  the Claude Code manifest, as the prototype laid them out.
- `prd_tester_guard.py` reads both payload shapes; one function
  `invocation(event: dict) -> tuple[str, str, str]` (kind, command, path) in front of the existing
  logic, with the existing tests run against both shapes.
- `skills/testing-from-prds/dispatching.md` and the builder dispatch gain an Antigravity branch.
- The evals stay Claude Code only; the acceptance record says which behaviours were checked by
  hand in Antigravity.

---

## Review focus

Failure modes no single phase's tests own, most likely first:

1. **An agent adds its own key.** Verifying against the head's `allowed_signers` would accept it.
   Owned by the 2.0.0 item (`test_verify_uses_base_signers`).
2. **A PRD edit after approval.** A signature covers the tree at the approval commit only. The 2.0.0
   item's spec must name the existing check that refuses a later behaviour edit without a new §14 row, or
   add one.
3. **A key that needs no presence.** A passphrase-less key on disk signs for the agent as readily
   as for the owner. The toolkit can only warn (key type); the README must say so plainly.
4. **Replay on a repo whose old commit cannot run today's tests.** Missing fixtures or a changed
   harness yield "no RESULTS line", which must read as "could not prove", not as a pass.
5. **Shallow clones in CI.** Phase 1 and the 2.0.0 item read history; the generated jobs already use
   `fetch-depth: 0`, and each new job must too.

## What this plan does not port

- The prototype's second implementation in Go.
- Its environment-variable and command-regex owner check.
- Its hash lockfile as a separate file: `change.digest` plus a signature per version gives the
  same record without a second source of truth beside `prd.md` §14.

---

## 2.0.0 roadmap: signed approvals

**Deferred (owner, 2026-11-14).** Not part of the phases above. Today the owner is the control:
one owner, working interactively, with every approval commit read in a pull request. The item
becomes due when any one of these is true:

1. Agents run unattended (the machine interface, the decision inbox or a headless client writes
   the approval with nobody watching the session).
2. Someone other than the owner relies on an approval, and cannot tell whether the quoted reply
   is real.
3. "The owner's word decides" is promoted as a guarantee of a public product.

Until then, keep required review on `main` in every repo that uses the toolkit. The design below
is kept so the 2.0.0 spec starts from it.

**Problem.** `change_approve.approve` writes the `docs(prd): approve <slug> <version>` commit from
a reply string the agent supplies. The prototype tried to solve this with an environment-variable
check and a regex over Bash commands; both were bypassed in the review. A check on *who is
calling* cannot work, because the agent runs as the owner.

**Decision.** Bind the approval to a key the agent cannot use without the owner's physical act.
The toolkit signs the approval with `ssh-keygen -Y sign`; the protection is the key's own
user-presence requirement (a FIDO2 `ed25519-sk` key, a Secure Enclave key, or an agent that
prompts per use). CI verifies the signature. The toolkit never decides who is calling.

**What is signed.** One message per approval, namespace `prd-approval`:

```
prd-toolkit approval 1
<slug>
<version>
<digest>
```

`<digest>` is `change.digest(prd_root)`, which already normalizes `prd.md`, computed on the tree
the approval commit holds. `change.digest` must be changed to skip the `approvals/` folder
(`_skipped` in `prdlint/change.py`), or a signature would alter the digest it signs.

**Files.**

- `docs/prd/<slug>/approvals/allowed_signers` — OpenSSH allowed-signers file, one line per owner.
- `docs/prd/<slug>/approvals/<version>.sig` — the signature, committed in the approval commit.
- `prd.md` frontmatter gains `approval-signing: off | optional | required` (default `off`, so no
  existing PRD changes behaviour).
- Create `prd-toolkit/scripts/prdlint/signing.py`:
  - `message(slug: str, version: str, digest: str) -> bytes`
  - `sign(prd_root: Path, version: str, key: Path | None) -> Path` — runs `ssh-keygen -Y sign`;
    the key is `--key`, else git's `user.signingkey`; raises `SigningError` with ssh-keygen's text.
  - `verify(prd_root: Path, version: str, digest: str, signers: bytes) -> str | None` — the
    reason it fails, or `None`.
  - `signers_at(repo_root: Path, rev: str, prd_rel: str) -> bytes | None`
- Modify `prdlint/change_approve.py`: after `_approved_text` is written and before `_commit`,
  when the mode is not `off`, call `signing.sign`; a failure under `required` rolls back as any
  other failure does; under `optional` the approval proceeds unsigned and says so.
- Modify `prdlint/hooks.py` (`check`): for each approval commit in the range, under `required`,
  verify `<version>.sig` against the allowed-signers file **at the range's base**, never the
  head's.
- New lint rule `approval-signing` in `prdlint/rules/`: the frontmatter value is one of the
  three; under `required`, `approvals/allowed_signers` exists; **warn** when a signer's key type
  is not `sk-*` ("this key cannot prove the owner was present").
- The authoring skill's first approval takes the same path as a change's.
- Skills `changing-prds` and `authoring-prds`: one paragraph each — the signing prompt is the
  owner's; the agent waits and never passes a key path the owner did not name.

**Tests that must exist** (names for the phase plan):

- `test_signing_roundtrip` — sign with a throwaway key, verify passes.
- `test_verify_refuses_changed_digest` — edit any PRD file after signing; verify names the digest.
- `test_verify_uses_base_signers` — a PR that adds its own key to `allowed_signers` and signs with
  it fails `check`.
- `test_signers_change_needs_existing_signer` — a change to `allowed_signers` is accepted only in
  an approval signed by a key already in the base file.
- `test_required_without_key_rolls_back` — `prd.md`, CLAUDE.md and the READMEs are byte-identical
  after a refused signing.
- `test_off_is_unchanged` — with `approval-signing` absent, the approval commit is what 0.8.6
  writes, byte for byte.

**Out of scope.** Signing error-class confirmations and deploy human steps. They reuse
`signing.py` later if this item proves out.

**Open for the owner.** (a) The first `allowed_signers` has no earlier signer; the plan accepts an
unsigned bootstrap commit, visible in review. (b) Whether `required` should refuse non-`sk-*` keys
outright rather than warn.
