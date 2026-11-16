---
type: regex
match: contains
target: last_message
pattern: 'CHANGES[\s\S]*UNIT[\s\S]*SOURCES[\s\S]*QUESTIONS[\s\S]*COMMIT'
---

The report keeps its five fields, in order: the practice lines go inside CHANGES and QUESTIONS, never in a field of
their own.
