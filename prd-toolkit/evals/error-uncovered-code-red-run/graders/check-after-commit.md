---
type: regex
target: trace
pattern: '"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=][\s\S]*?(?:"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit\s[\s\S]*?"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+check\s(?:[^"\\]|\\.)*?[^\s"\\]+\.\.HEAD(?![\w.~^@{])(?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\1","type":"tool_result","content":"(?:[^"\\]|\\.)*?prd-error-exit=0|"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit\s(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+check\s(?:[^"\\]|\\.)*?[^\s"\\]+\.\.HEAD(?![\w.~^@{])(?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\2","type":"tool_result","content":"(?:[^"\\]|\\.)*?prd-error-exit=0)'
---

The loop closes on `prd error check <start>..HEAD` (any start: a SHA, `HEAD~4`, a branch), run after the resolve and
after a `git commit` (the ledger's), in a later Bash call or chained after the commit in the same call, and it exits
0 (`prd-error-exit=0` in that call's result). A check run before the ledger is committed reads no resolution, so it
would pass whatever the line said: the order is part of the grade.
