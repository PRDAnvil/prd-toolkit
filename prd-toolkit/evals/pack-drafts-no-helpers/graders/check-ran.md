---
type: tool_used
tool: Bash
min: 1
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*\bprd(?:\\")?(?:\s+pack|_pack\.py(?:\\")?)\s+check\b'
---

`prd pack check` runs on the written pack before anything is committed (rule 7).
