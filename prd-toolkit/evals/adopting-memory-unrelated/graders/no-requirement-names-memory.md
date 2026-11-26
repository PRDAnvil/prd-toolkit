---
type: regex
pattern: 'memory note|auto-memory|MEMORY\.md'
flags: i
match: not_contains
target: { source: file, path: docs/prd/notes/features/notes.md }
---

The only note is another project's, so nothing in the notes area's requirements comes from memory: no
requirement names a memory note, auto-memory or `MEMORY.md`. The service keeps its notes in memory, and an
as-built requirement may say so.
