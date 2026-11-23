---
type: regex
pattern: '(?:^|\n)Resolution: -[ \t]*(?:\r?\n|$)'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The entry stays open: no fix was made for it, so nothing resolves it, and no `not a defect` closes it
without the owner's word.
