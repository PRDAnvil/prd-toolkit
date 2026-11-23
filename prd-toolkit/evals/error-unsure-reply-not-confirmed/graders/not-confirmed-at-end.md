---
type: regex
pattern: '(?:^|\n)Confirmed:'
match: not_contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The inbox wrote the unsure reply as `Confirmed:`. A reply that shows the owner does not follow is not a
confirmation, so the session reopens the class and the entry ends with no `Confirmed:` line.
