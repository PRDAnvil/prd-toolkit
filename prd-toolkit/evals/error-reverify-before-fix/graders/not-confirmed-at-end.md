---
type: regex
pattern: '(?:^|\n)Confirmed:'
match: not_contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The run on HEAD shows nothing to fix, so the session reopens the class instead of fixing it: the entry ends
with no `Confirmed:` line. The start state is confirmed, so it fails here.
