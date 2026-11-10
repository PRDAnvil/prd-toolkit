# prd-toolkit

A living PRD as the single authority agents build, test and deploy from: a PRD folder in the repo with contracts and black-box test cases, a 40-rule linter, standards and skills registries, and skills to author and change it, plus a builder that takes an approved change to verified code and a deploy script that takes it live.

**Features:**
- **authoring-prds skill** - Interviews to `docs/prd/<project>/`, lints it, dry-runs it with prd-tester, and approves it
- **changing-prds skill** - Changes the PRD first, with new IDs and a version bump, before any code
- **building-from-prds skill** - Takes approved requirements to verified code: a builder in its own worktree, tests written by prd-tester, statuses approved, built, verified
- **deploying-from-prds skill** - Deploys a verified PRD through its runbook with `prd_deploy.py`, stopping at every human step and failure, and records Deployed rows and `verified` → `live`
- **handling-errors skill** - Records any error in `errors.md` with `prd_error.py`, proposes its class for the user to confirm, and fixes it from a failing test through `/prd-change` and `/prd-build`
- **publishing-prds skill** - Renders the PRD with `prd_publish.py` as one self-contained HTML page with per-area summaries that cite their IDs, outside the PRD folder and never committed, offered as a private Artifact
- **coordinating-prds skill** - Links PRDs across repositories (`links.md`, a pinned snapshot of the cited upstream items, `prd_links.py`) and runs a change that crosses them as one change set: one record, one approval, a build per repository in dependency order
- **Slash commands**: `/prd-new`, `/prd-adopt`, `/prd-change`, `/prd-change-set`, `/prd-context`, `/prd-build`, `/prd-status`, `/prd-deploy`, `/prd-error` and `/prd-publish`
- **Lint CLI**: `prd_lint.py` checks 40 rules; `prd_block.py` writes the CLAUDE.md block

**For full documentation:** See [prd-toolkit/README.md](./prd-toolkit/README.md)


## Install

In Claude Code:

```
/plugin marketplace add PRDAnvil/prd-toolkit
/plugin install prd-toolkit@prdanvil
```

Restart Claude Code, then check that `claude plugin list` shows `prd-toolkit@prdanvil`. The scripts need [uv](https://docs.astral.sh/uv/).

## License

MIT; see [LICENSE](./LICENSE).
