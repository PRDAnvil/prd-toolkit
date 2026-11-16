---
type: regex
match: contains
target: last_message
pattern: '\bfeeds\b[^\n]{0,160}(?:\bB\b|\bsouth\b)|(?:\bB\b|\bsouth\b)[^\n]{0,160}\bfeeds\b'
---

`feeds` is marked as B's alone: `B` or south, its PRD, on its line.
