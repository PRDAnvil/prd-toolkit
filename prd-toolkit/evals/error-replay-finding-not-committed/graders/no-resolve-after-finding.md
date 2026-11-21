---
type: regex
target: trace
pattern: '"type":"tool_result","content":"(?:[^"\\]|\\.)*?E-001: T-001\.2 passes on [0-9a-f]{7,40}\^; [0-9a-f]{7,40} did not turn it green[\s\S]*"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s'
match: not_contains
---

After the replay's finding, no second `prd error resolve` (with another T-id, version or commit) to make it hold.
