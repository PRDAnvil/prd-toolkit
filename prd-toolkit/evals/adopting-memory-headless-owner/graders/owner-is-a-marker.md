---
type: regex
pattern: '^owner:\s*\[NEEDS CLARIFICATION'
flags: m
target: { source: file, path: docs/prd/notes/prd.md }
---

Only the owner can name the owner. Without that yes, headless as well, the marker stays: `owner:` holds a
`[NEEDS CLARIFICATION]` marker, not the name from memory nor one taken from the git author.
