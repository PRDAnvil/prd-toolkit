---
type: regex
target: trace
pattern: '"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=][\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit\s[\s\S]*?"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+check\s(?:[^"\\]|\\.)*?[0-9a-f]{7,40}\.\.(?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\1","type":"tool_result","content":"(?:[^"\\]|\\.)*?prd-error-exit=0'
---

The loop closes on `prd error check <start>..HEAD`, run after the resolve and after a `git commit` (the ledger's),
and it exits 0 (`prd-error-exit=0` in that call's result). A check run before the ledger is committed reads no
resolution, so it would pass whatever the line said: the order is part of the grade.
