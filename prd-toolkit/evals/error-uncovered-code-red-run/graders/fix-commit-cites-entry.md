---
type: regex
target: trace
pattern: '"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])(?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\1","type":"tool_result","content":"(?:[^"\\]|\\.)*?\b1 file changed(?:[^"\\]|\\.)*?\bcreate mode \d+ (?:[^"\\\s]*/)?(?:test_[^"\\\s/]*|[^"\\\s/]*_test)\.py(?![\w.])[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])(?:[^"\\]|\\.)*?(?:\\n|\\\"|[\s\x27])[Rr]efs:(?:[^"\\]|\\[^n])*?\bE-001(?!\w)(?:[^"\\]|\\.)*"[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=]'
---

The fix is its own commit and cites the entry, read from the trace: after the test's commit (as above) and before
the `prd error resolve ... --red-run` call, a `git commit` call whose command holds a `Refs:` line with E-001.
