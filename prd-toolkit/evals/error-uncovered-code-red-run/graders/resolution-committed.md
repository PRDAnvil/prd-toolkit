---
type: regex
target: trace
pattern: '"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:/prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+resolve\s(?:[^"\\]|\\.)*?--red-run[\s=](?:(?:[^"\\]|\\.)*"[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?|(?:[^"\\]|\\.)*?)(?:(?:\b|(?<=\\n))git\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*add(?![\w-])(?:\s+[^\s"\;&|]+)*?\s+(?:\\"|\x27)?(?:(?:[^\s"\;&|\\]*/)?(?:errors\.md|docs(?:/prd(?:/greet)?)?/?)|-A|-u|--all|--update|\.)(?=\\[n"]|[\s"\;&|\x27]|$)(?:(?:[^"\\]|\\.)*"[\s\S]*?"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?|(?:[^"\\]|\\.)*?)(?:\b|(?<=\\n))git\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])|(?:\b|(?<=\\n))git\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*commit(?![\w-])(?:\s+(?:\\"(?:[^"\\]|\\[^"])*\\"|\x27[^\x27]*\x27|[^\s"\;&|\x27]+))*?\s+(?:-[a-zA-Z]*a[a-zA-Z]*|--all|(?:\\"|\x27)?(?:[^\s"\;&|\\]*/)?errors\.md)(?=\\[n"]|[\s"\;&|\x27]|$))'
---

The red run is committed, read from the trace: after the `prd error resolve ... --red-run` call, `errors.md` is
committed, by a `git add` naming `errors.md` (quoted or not), its folder (`docs/prd/greet`, `docs/prd`, `docs`) or `-A`, `-u`, `.`, and a `git commit`, in one Bash call or in
later ones, or by a `git commit` with `-a`/`-am` or one that names the file. A ledger left in the working tree
fails it.
