---
type: regex
target: trace
pattern: '"id":"(toolu_[A-Za-z0-9]+)","name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])(?:[^"\\]|\\.)*"[\s\S]*?"tool_use_id":"\1","type":"tool_result","content":"(?:[^"\\]|\\.)*?\b1 file changed(?:[^"\\]|\\.)*?\bcreate mode \d+ (?:[^"\\\s]*/)?(?:test_[^"\\\s/]*|[^"\\\s/]*_test)\.py(?![\w.])[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])(?:[^"\\]|\\.)*"[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=]'
---

The failing test is committed alone before the fix, read from the trace: a `git commit` call whose own result reports
`1 file changed` and `create mode <mode> <path>` for a test file (`test_*.py` or `*_test.py`); after it another
`git commit` call; and only after that, the `prd error resolve ... --red-run` call. A test and its fix in one commit
fail it (that result says `2 files changed`), and so does a test committed after the fix (no commit follows it
before the resolve).
