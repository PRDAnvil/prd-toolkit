---
type: tool_used
tool: Edit
input_match: '"file_path"\s*:\s*"[^"]*errors\.md"'
min: 0
max: 0
---

Only `resolve --red-run` writes a red run, and `check` finds nothing to fix by hand here: no Edit of `errors.md`.
