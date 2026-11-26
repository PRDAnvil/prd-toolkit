---
type: regex
pattern: 'memory note'
flags: i
match: contains
target: { source: file, path: docs/prd/notes/errors.md }
---

The code starts note ids at 1 and the owner's memory note says they start at 0. Only memory shows the
conflict, so an `errors.md` entry must record it, naming the memory note it came from.
