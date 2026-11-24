---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*--amendment'
min: 0
max: 0
---

No `changeset approve … --amendment`: the record has no Approval line, so the owner's reply is the change set's first
approval, never an amendment of one. Fails on any Bash call that passes `--amendment`.
