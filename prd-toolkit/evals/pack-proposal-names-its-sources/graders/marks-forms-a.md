---
type: regex
match: contains
target: last_message
pattern: '\bforms\b[^\n]{0,160}(?:\bA\b|\bnorth\b)|(?:\bA\b|\bnorth\b)[^\n]{0,160}\bforms\b'
---

`forms` is marked as A's alone: `A` or north, its PRD, on its line.
