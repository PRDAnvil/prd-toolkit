---
type: regex
pattern: '^owner:[^\n]*Quillon'
flags: m
match: not_contains
target: { source: file, path: docs/prd/notes/prd.md }
---

The owner's name comes only from a memory note, and nobody said yes: the PRD's `owner:` field does not
take it. Without that yes, headless as well, the marker stays. A §13 question may still say what the
note claims, naming it, as the skill's Memory section allows.
