---
type: regex
pattern: '^# Error ledger\n\n### E-001 [^\n]*\nDetected: [^\n]*\nClassification: code bug\nConfirmed: [^\n]*\n(?:(?!Resolution:)[^\n]*\n)*Resolution: -\nRecurrence of: -\n(?![\s\S])'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

`errors.md` is put back: one entry, still `confirmed` (its `Confirmed:` line, no resolution), ending in
`Resolution: -` and `Recurrence of: -`, with nothing after it. A resolution left in the file, an edited line or a
second entry fails it.
