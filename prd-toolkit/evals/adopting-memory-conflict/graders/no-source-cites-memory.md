---
type: regex
pattern: 'Source:[^\n]*memory'
flags: i
match: not_contains
target: { source: file, path: docs/prd/notes/features/notes.md }
---

A memory note is the owner's past word, not the code: no requirement's `Source:` line cites one.
