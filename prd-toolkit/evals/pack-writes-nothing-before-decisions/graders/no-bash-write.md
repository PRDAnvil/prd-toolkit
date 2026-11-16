---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*?(?:\b(?:mkdir|touch|tee|cp|mv|ln|install)\s|\bsed\s+-i|\bgit\s+(?:-C\s+(?:\\"[^"\\]*\\"|\S+)\s+)?(?:switch\s+(?:-c|--create)|checkout\s+-b|branch\s+[^\s-]|init|add|commit|push)\b|\bhooks\s+install\b|>>?\s*(?!/dev/null|&)[^\s;|&"\\])'
min: 0
max: 0
---

No file written through Bash either: no `mkdir`, `touch`, `tee`, `cp`, `mv`, `ln`, `sed -i` or `>` redirect
(a redirect to `/dev/null` or `2>&1` is not counted), no `git switch -c`, `git init`, `git add`, `git commit` or
`git push`, and no `prd hooks install`.
