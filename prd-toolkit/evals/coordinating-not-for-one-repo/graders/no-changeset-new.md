---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*(?:prd_links\.py|/prd(?:\\")?\s+links)\s+changeset\s+new\b'
min: 0
max: 0
---

A change nobody cites opens no change set. Fails on `prd_links.py changeset new` or `.prd-toolkit/prd links changeset new` (or the plugin's `…/scripts/prd links changeset new`).
