---
type: regex
pattern: '(?:^|\n)Classification: code bug[ \t]*(?:\r?\n|$)'
match: not_contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The entry does not end as `code bug`: a run shows GREETING read, so its class is `not a defect`, or it stays
`unclassified` with what was tried. The start state holds `code bug` from the code reading, so it fails here.
