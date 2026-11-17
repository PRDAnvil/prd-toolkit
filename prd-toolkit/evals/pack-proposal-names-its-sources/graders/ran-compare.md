---
type: tool_used
tool: Bash
min: 1
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*\bprd(?:\\")?(?:\s+pack|_pack\.py(?:\\")?)\s+compare\b'
---

Step 2 runs `prd pack compare` on the two PRDs (or `prd_pack.py compare`, the launcher path plain or in double
quotes): what the proposal holds comes from its output.
