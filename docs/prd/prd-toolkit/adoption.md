# Adoption map

| Area | State | Boundary |
|---|---|---|
| lint-cli | adopted | `prd-toolkit/scripts/prd_lint.py`, `prd-toolkit/scripts/prdlint/__init__.py`, `prd-toolkit/scripts/prdlint/model.py`, `prd-toolkit/scripts/prdlint/markdown.py`, `prd-toolkit/scripts/prdlint/yamlload.py`, `prd-toolkit/scripts/prdlint/findings.py`, `prd-toolkit/scripts/prdlint/registry.py`, `prd-toolkit/scripts/prdlint/deps.py`, `prd-toolkit/scripts/prdlint/rules/__init__.py`, `prd-toolkit/scripts/prdlint/interface.py` |
| lint-structure | adopted | `prd-toolkit/scripts/prdlint/rules/structure.py` |
| lint-ids | adopted | `prd-toolkit/scripts/prdlint/rules/ids.py` |
| lint-testcases | adopted | `prd-toolkit/scripts/prdlint/rules/testcases.py` |
| lint-contracts | adopted | `prd-toolkit/scripts/prdlint/rules/contracts.py` |
| lint-registries | adopted | `prd-toolkit/scripts/prdlint/rules/registries.py`, `prd-toolkit/scripts/prdlint/rules/errors.py` |
| trace | adopted | `prd-toolkit/scripts/prd_trace.py`, `prd-toolkit/scripts/prdlint/trace.py`, `prd-toolkit/scripts/prd_git_hook.py`, `prd-toolkit/scripts/prdlint/githook.py`, `prd-toolkit/templates/hooks/**` |
| hooks-install | adopted | `prd-toolkit/scripts/prd_hooks.py`, `prd-toolkit/scripts/prdlint/hooks.py`, `prd-toolkit/scripts/prd_dispatch.py`, `prd-toolkit/scripts/requirements.txt` |
| context | adopted | `prd-toolkit/scripts/prd_context.py`, `prd-toolkit/scripts/prdlint/context.py` |
| status | adopted | `prd-toolkit/scripts/prd_status.py`, `prd-toolkit/scripts/prdlint/status.py`, `prd-toolkit/scripts/prd_block.py`, `prd-toolkit/templates/claude-block.md`, `prd-toolkit/scripts/prdlint/overview.py`, `prd-toolkit/templates/readme-prd.md`, `prd-toolkit/templates/readme-prds.md` |
| build-check | adopted | `prd-toolkit/scripts/prd_build_check.py`, `prd-toolkit/scripts/prdlint/buildcheck.py` |
| deploy | not started | `prd-toolkit/scripts/prd_deploy.py`, `prd-toolkit/scripts/prdlint/deploy.py`, `prd-toolkit/scripts/prd_drift.py`, `prd-toolkit/scripts/prdlint/drift.py` |
| errors | not started | `prd-toolkit/scripts/prd_error.py`, `prd-toolkit/scripts/prdlint/errors.py` |
| publish | not started | `prd-toolkit/scripts/prd_publish.py`, `prd-toolkit/scripts/requirements-publish.txt`, `prd-toolkit/scripts/prdlint/publish.py`, `prd-toolkit/scripts/prdlint/diagrams.py`, `prd-toolkit/templates/publish/**` |
| links | not started | `prd-toolkit/scripts/prd_links.py`, `prd-toolkit/scripts/prdlint/links.py`, `prd-toolkit/scripts/prdlint/changeset.py`, `prd-toolkit/scripts/prdlint/snapshot.py`, `prd-toolkit/scripts/prdlint/citations.py`, `prd-toolkit/scripts/prdlint/rules/links.py` |
| tester-guard | not started | `prd-toolkit/scripts/prd_tester_guard.py`, `prd-toolkit/hooks/**` |
| gates | not started | `prd-toolkit/scripts/prd_gates.py`, `prd-toolkit/scripts/prdlint/gates.py`, `prd-toolkit/scripts/prdlint/formserver.py`, `prd-toolkit/scripts/prd_confirm.py`, `prd-toolkit/scripts/prdlint/confirm.py` |
| change | adopted | `prd-toolkit/scripts/prd_change.py`, `prd-toolkit/scripts/prdlint/change.py`, `prd-toolkit/scripts/prdlint/change_approve.py` |
| judge | not started | `prd-toolkit/scripts/prd_judge.py`, `prd-toolkit/scripts/prdlint/judge.py` |
| packs | not started | `prd-toolkit/scripts/prdlint/packs.py`, `prd-toolkit/scripts/prdlint/languages.py`, `prd-toolkit/scripts/prdlint/rules/packs.py` |
| skills | not started | `prd-toolkit/skills/**`, `prd-toolkit/agents/**`, `prd-toolkit/commands/**`, `prd-toolkit/references/clarify-categories.md`, `prd-toolkit/references/contract-types.md`, `prd-toolkit/references/ears.md`, `prd-toolkit/references/quality-checklist.md`, `prd-toolkit/references/test-levels.md`, `prd-toolkit/references/prd-format.md`, `prd-toolkit/templates/prd/**` |
| release | adopted | `prd-toolkit/.claude-plugin/**`, `prd-toolkit/README.md`, `prd-toolkit/LICENSE`, `prd-toolkit/NOTICE`, `prd-toolkit/pyproject.toml`, `prd-toolkit/uv.lock`, `.claude-plugin/marketplace.json`, `README.md` |
| help | adopted | `prd-toolkit/scripts/prd_help.py`, `prd-toolkit/scripts/prdlint/helpcat.py`, `prd-toolkit/references/help.yaml` |
| status-next | adopted | `prd-toolkit/scripts/prdlint/nextpart.py` |
| practices | adopted | `prd-toolkit/scripts/prd_practices.py`, `prd-toolkit/scripts/prdlint/practices.py`, `prd-toolkit/scripts/prdlint/rules/practices.py` |
| pack-authoring | adopted | `prd-toolkit/scripts/prd_pack.py`, `prd-toolkit/scripts/prdlint/packcompare.py`, `prd-toolkit/scripts/prdlint/packcheck.py` |
| card-context | adopted | `prd-toolkit/scripts/prdlint/cardcontext.py` |
| standards-run | adopted | `prd-toolkit/scripts/prdlint/standardsrun.py` |
| launcher | adopted | `prd-toolkit/scripts/prd` |
| hook-shims | adopted | `prd-toolkit/scripts/prdlint/hookshims.py` |
| inbox-cards | adopted | `prd-toolkit/scripts/prdlint/inboxcards.py` |
| context-notes | adopted | `prd-toolkit/scripts/prdlint/contextnotes.py` |
| eval-scaffolds | adopted | `prd-toolkit/evals/scaffolds/install_files.py` |
| tester-paths | adopted | `prd-toolkit/scripts/prdlint/testerpaths.py` |
| error-replay | adopted | `prd-toolkit/scripts/prdlint/errorreplay.py` |
| error-reopen | adopted | `prd-toolkit/scripts/prdlint/errorreopen.py` |
| trd | adopted | `prd-toolkit/scripts/prd_trd.py`, `prd-toolkit/scripts/prdlint/trd.py` |
| edit-hook | adopted | `prd-toolkit/scripts/prd_edit_hook.py` |
