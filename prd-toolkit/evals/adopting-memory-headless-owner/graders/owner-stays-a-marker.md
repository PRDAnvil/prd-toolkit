---
type: regex
pattern: '^(?![^\n]*[Mm]emory note)[^\n]*Quillon'
flags: m
match: not_contains
target: { source: file, path: docs/prd/notes/prd.md }
---

The owner's name comes only from a memory note, and nobody said yes, so the PRD never states it as fact: a
line of `prd.md` may hold the name only beside the note it came from, as the §13 question the skill's Memory
section allows (`memory note <file> (<date>)`). The `owner:` field, a §1 line or any other line naming her
fails.
