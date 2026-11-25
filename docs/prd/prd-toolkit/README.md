<!-- prd-toolkit:start -->
# prd-toolkit — product requirements

This folder is the living PRD for **prd-toolkit**: the requirements that say what it does, kept in
step with the code. The code implements this PRD, and a change in behaviour starts here, not in
the code. It is maintained with prd-toolkit, a Claude Code plugin (see [../README.md](../README.md) to set it up).

Version 13.0.0 · Approved · Owner: Ivan Histand · Updated 2026-11-25

## What this PRD covers

> prd-toolkit keeps a living PRD folder in a repository and makes agents build, test and deploy
> from it: a linter and trace checks for the folder, a black-box test agent, and skills that
> author, adopt, change, build, deploy, handle errors in, publish and link PRDs.

## Areas

| Area | Adoption | File |
|---|---|---|
| build-check | adopted | [features/build-check.md](features/build-check.md) |
| card-context | adopted | [features/card-context.md](features/card-context.md) |
| change | adopted | [features/change.md](features/change.md) |
| context-notes | adopted | [features/context-notes.md](features/context-notes.md) |
| context | adopted | [features/context.md](features/context.md) |
| error-reopen | adopted | [features/error-reopen.md](features/error-reopen.md) |
| error-replay | adopted | [features/error-replay.md](features/error-replay.md) |
| eval-scaffolds | adopted | [features/eval-scaffolds.md](features/eval-scaffolds.md) |
| help | adopted | [features/help.md](features/help.md) |
| hook-shims | adopted | [features/hook-shims.md](features/hook-shims.md) |
| hooks-install | adopted | [features/hooks-install.md](features/hooks-install.md) |
| inbox-cards | adopted | [features/inbox-cards.md](features/inbox-cards.md) |
| launcher | adopted | [features/launcher.md](features/launcher.md) |
| lint-cli | adopted | [features/lint-cli.md](features/lint-cli.md) |
| lint-contracts | adopted | [features/lint-contracts.md](features/lint-contracts.md) |
| lint-ids | adopted | [features/lint-ids.md](features/lint-ids.md) |
| lint-registries | adopted | [features/lint-registries.md](features/lint-registries.md) |
| lint-structure | adopted | [features/lint-structure.md](features/lint-structure.md) |
| lint-testcases | adopted | [features/lint-testcases.md](features/lint-testcases.md) |
| pack-authoring | adopted | [features/pack-authoring.md](features/pack-authoring.md) |
| practices | adopted | [features/practices.md](features/practices.md) |
| standards-run | adopted | [features/standards-run.md](features/standards-run.md) |
| status-next | adopted | [features/status-next.md](features/status-next.md) |
| status | adopted | [features/status.md](features/status.md) |
| tester-paths | adopted | [features/tester-paths.md](features/tester-paths.md) |
| trace | adopted | [features/trace.md](features/trace.md) |
| trd | adopted | [features/trd.md](features/trd.md) |

## What is in this folder

| Path | Holds |
|---|---|
| `prd.md` | The overview: goals, glossary, architecture, the requirement index, open questions, changelog |
| `features/` | One file per area: requirements (`FR-nnn`) and their acceptance criteria (`AC-nnn.n`) |
| `test-cases/` | The test cases for each criterion (`T-nnn.n`), which the tests cite |
| `contracts/` | The interfaces the code must match: commands, configuration, schemas, APIs |
| `testing.md` | How the tests are run, at which level and gate |
| `errors.md` | The error ledger: every bug, its class and its fix (`E-nnn`) |
| `operations.md` | Environments and the deploy runbook |
| `nfr.md` | Non-functional requirements (`NFR-nnn`) |
| `adoption.md` | Which areas of the existing code are under this PRD, and their state |

## Reading and changing it

- Read `prd.md`, then the area you care about. With the plugin: `/prd-toolkit:prd-status` for
  where every requirement stands, `/prd-toolkit:prd-context <area>` for one area,
  `/prd-toolkit:prd-publish` for a readable page.
- Don't edit these files by hand. A change in behaviour starts with `/prd-toolkit:prd-change` and
  is built with `/prd-toolkit:prd-build`; a bug starts with `/prd-toolkit:prd-error`. Lint and the
  git hooks check every commit.
<!-- prd-toolkit:end -->
