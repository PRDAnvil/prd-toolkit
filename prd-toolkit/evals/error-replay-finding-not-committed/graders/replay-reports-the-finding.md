---
type: regex
target: trace
pattern: '"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+replay\s(?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\1","type":"tool_result","content":"(?:[^"\\]|\\.)*?E-001: T-001\.2 passes on [0-9a-f]{7,40}\^; [0-9a-f]{7,40} did not turn it green'
---

`prd error replay` runs and reports its finding: the result of that Bash call holds
`E-001: T-001.2 passes on <sha>^; <sha> did not turn it green`, which it prints only once the entry is resolved and
the T-001.2 test passes on the fix's parent. Bound to the call by its id, so the skill text never matches. This is
the grader that tells the 0.8.14 route from a run that never resolves.
