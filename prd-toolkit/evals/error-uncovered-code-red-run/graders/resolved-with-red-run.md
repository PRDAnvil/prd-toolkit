---
type: regex
target: trace
pattern: '"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=](?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\1","type":"tool_result","content":"(?:[^"\\]|\\.)*?(?:prd-error-exit=0|E-001 resolved code bug)'
---

The entry is resolved by `prd error resolve … --red-run`, and that call exits 0: its result holds
`prd-error-exit=0` or the line `E-001 resolved code bug`, which the command prints only when the replay it makes
holds. Bound to one Bash call by its id, so the skill text in the trace never matches.
