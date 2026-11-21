---
type: regex
pattern: '\t(?:commit|merge|reset|revert|cherry-pick|rebase|pull)'
match: not_contains
target: { source: file, path: .git/logs/HEAD }
---

The scaffold empties the reflog, so a commit (the resolution's, or any other), or a reset or revert that undoes
one, is a line here. A resolution whose replay printed findings is never committed.
