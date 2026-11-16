---
type: regex
match: contains
target: last_message
pattern: 'Sources:[^\n]*(?:\bS-\d{2}\b|\b[Ss]ource \d+\b)'
---

The skill's text holds its `Sources:` line naming the proposal's sources: their `S-nn` IDs or, before step 8 gives
the IDs, their labels (`source 1`).
