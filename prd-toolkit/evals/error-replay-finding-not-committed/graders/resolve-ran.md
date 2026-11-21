---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--t(?:\s+|=)T-001\.2(?![\w.])'
min: 1
---

The entry is resolved with its T-id, `prd error resolve … --t T-001.2 …`, as step 6 says for a fix whose build
closed: the replay comes after the resolve. A run that refuses to resolve at all (the 0.8.13 baseline's) fails it.
