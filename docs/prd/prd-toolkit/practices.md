<!-- Format: references/prd-format.md, "practices.md". -->

# Practices

## Sources

| ID | Title | Location | Covers | Read | Decision |
|---|---|---|---|---|---|
| S-01 | Claude Code plugin manifest reference | https://code.claude.com/docs/en/plugins/manifest-reference | the plugin manifest, `plugin.json` | 2026-11-26 | approved |
| S-02 | Claude Code marketplace reference | https://code.claude.com/docs/en/plugins/marketplace-reference | the marketplace file, `marketplace.json` | 2026-11-26 | approved |
| S-03 | Semantic Versioning 2.0.0 | https://semver.org/ | release version numbers | 2026-11-26 | approved |

## Practices

| ID | Source | Object (glob) | Applies to | Practice |
|---|---|---|---|---|
| P-01 | S-01 | `prd-toolkit/.claude-plugin/**` | code | `prd-toolkit/.claude-plugin/` holds no file other than `plugin.json`. |
| P-02 | S-01 | `prd-toolkit/.claude-plugin/plugin.json` | code | The plugin manifest's `license` value is an SPDX license identifier. |
| P-03 | S-02 | `.claude-plugin/marketplace.json` | code | The marketplace's `prd-toolkit` entry has a relative-path `source` that starts with `./`. |
| P-04 | S-03 | `prd-toolkit/.claude-plugin/plugin.json` | code | The plugin manifest's `version` has no leading zero in any of its three numbers. |
| P-05 | S-03 | `prd-toolkit/.claude-plugin/plugin.json` | code | A pull request that changes a file under `prd-toolkit/skills/`, `prd-toolkit/commands/`, `prd-toolkit/agents/`, `prd-toolkit/hooks/`, `prd-toolkit/scripts/` or `prd-toolkit/templates/` also changes `version` in `prd-toolkit/.claude-plugin/plugin.json`. |
