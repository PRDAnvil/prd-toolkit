---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*(?:prd_links\.py|/prd(?:\\")?\s+links)\s+impact\b'
min: 1
---

After the restate, `prd_links.py impact` or `.prd-toolkit/prd links impact` (or the plugin's `…/scripts/prd links impact`) runs (links.md lists a Consumer). Fails if the session edits the contract and never runs it.
