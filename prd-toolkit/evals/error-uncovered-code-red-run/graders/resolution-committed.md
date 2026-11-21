---
type: regex
target: trace
pattern: '(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=](?:(?:[^"\\]|\\.)*"[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?|(?:[^"\\]|\\.)*?)(?:\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*add(?![\w-])(?:\s+[^\s"\;&|]+)*?\s+(?:(?:\\")?(?:[^\s"\;&|]*/)?errors\.md|-A|-u|--all|--update|\.)(?![^\s"\;&|])(?:(?:[^"\\]|\\.)*"[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?|(?:[^"\\]|\\.)*?)\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])|\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])(?:\s+(?:\\"(?:[^"\\]|\\[^"])*\\"|\x27[^\x27]*\x27|[^\s"\;&|\x27]+))*?\s+(?:-[a-zA-Z]*a[a-zA-Z]*|--all|(?:\\")?(?:[^\s"\;&|]*/)?errors\.md)(?![^\s"\;&|]))'
---

The red run is committed, read from the trace: after the `prd error resolve ... --red-run` call, `errors.md` is
committed, by a `git add` naming `errors.md` (or `-A`, `-u`, `.`) and a `git commit`, in one Bash call or in
later ones, or by a `git commit` with `-a`/`-am` or one that names the file. A ledger left in the working tree
fails it.
