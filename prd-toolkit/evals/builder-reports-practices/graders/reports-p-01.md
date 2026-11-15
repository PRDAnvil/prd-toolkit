---
type: regex
match: contains
target: last_message
pattern: '\bP-01`?\s*:\s*`?(?:followed\b|not applicable \(|not followed \()'
---

The report holds a line for P-01 in one of the three forms: `P-01: followed`, `P-01: not applicable (<why>)` or
`P-01: not followed (<why>)`.
