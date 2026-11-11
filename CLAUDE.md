# CLAUDE.md

Guidance for Claude Code in this repository.

## Project

This repository is **prd-toolkit**, a Claude Code plugin that keeps a living PRD as the single
authority agents build, test and deploy from. It is also its own marketplace, `prdanvil`
(`.claude-plugin/marketplace.json`). It moved here from `ihistand/claude-plugins` on 2026-11-10, with
its history.

```
.claude-plugin/marketplace.json   the prdanvil marketplace (one plugin, source ./prd-toolkit)
prd-toolkit/                      the plugin: skills, agents, commands, scripts, templates, packs, tests
docs/prd/prd-toolkit/             the toolkit's own PRD
.prd-toolkit/                     the vendored copy the git hooks and CI run
docs/superpowers/                 design specs and plans, one per release
scripts/ci-local.sh               runs the PR workflow's jobs locally, the way CI does
```

The toolkit is authored in place. Its skills share scripts, templates and references and are
useless apart.

Claude Code loads plugin skills only as `skills/<name>/SKILL.md`; a flat `skills/<name>.md` is
ignored.

## Tests

```bash
uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd   # unit
uv run --directory prd-toolkit pytest -q -n auto tests/prd                  # integration (prd-tester's)
scripts/ci-local.sh                                                         # every CI job, as CI runs it
```

Never edit a test that cites a non-unit T-id (`@prd T-…`): those are prd-tester's.

## The vendored copy

`.prd-toolkit/` must match the plugin byte for byte (`test_vendored_copy.py`). After a change to a
file vendoring copies, refresh it with:

`uv run --script prd-toolkit/scripts/prd_hooks.py vendor docs/prd/prd-toolkit`

Commit the refresh in the same commit. Never edit it by hand, and never run `prd_hooks.py install`
on this repository.

## Versions

A release bumps three places together: `prd-toolkit/.claude-plugin/plugin.json`, the
`marketplace.json` entry, and `.prd-toolkit/VERSION` (written by `vendor`). The newest
`prd-toolkit/tests/test_release_*.py` pins the current version. The toolkit stays below 0.9 while
packs declare `toolkit: ">=0.8.0,<0.9"`.

## Skills design

Skills enforce discipline, not just inform:

- They hold up against rationalization, especially under time pressure.
- They carry Red Flags and Common Rationalizations sections.
- They use non-negotiable language, and name the related skills they chain to.

## Git workflow

- **Author:** Ivan Histand <ivan@badgeretl.com>, set in this clone's `git config`.
- **Branch:** `main` is production, and users install from it. Work goes on a branch and lands by
  pull request.
- **Commits** cite the PRD IDs they touch (`Refs: FR-012`), or `Refs: none (no behaviour change)`.
- **Hooks:** never `--no-verify`, and never bare `git stash`.

## Writing

Omit needless words, use the active voice, and be specific.

<!-- prd-toolkit:start -->
## Product requirements (by prd_block.py; do not edit)

The PRD at `docs/prd/prd-toolkit` (version 6.2.1) is the authority.

- To learn what an area does, run `/prd-context <area>` and work from its pack; read whole PRD
  files only to edit them. Build an approved change with `/prd-build <area> <IDs>`. Code
  implements the PRD; it never defines behaviour the PRD lacks.
- Every behaviour change in an adopted area starts with `/prd-change`, before code.
- Gap rule: if the PRD is silent on what you need, stop and raise it with `/prd-change`.
  Do not guess or read the code to fill the gap.
- Deploy with `/prd-deploy`; never run a runbook command yourself.
- A bug, a failing test, an error or a failed deploy goes to `/prd-error` (skill
  `prd-toolkit:handling-errors`) before any code changes.
- Commits cite IDs: `Refs: FR-012`.
- Run `.prd-toolkit/prd_hooks.py install` once per clone:
  `uv run --script .prd-toolkit/prd_hooks.py install docs/prd/prd-toolkit`.
- Lint runs inside the prd-toolkit skills; after any PRD edit, finish through `/prd-change`.

Required skills:
- `superpowers:writing-skills` for a change to `prd-toolkit/skills/**`
- `superpowers-developing-for-claude-code:developing-claude-code-plugins` for a change to the plugin's layout or manifests
- `superpowers:test-driven-development` for any code change
- `superpowers:systematic-debugging` for a bug or a failing test
- `superpowers:verification-before-completion` for a claim that work is done
- `superpowers:writing-plans` for planning a change

Adopted areas: lint-cli, lint-structure
<!-- prd-toolkit:end -->
