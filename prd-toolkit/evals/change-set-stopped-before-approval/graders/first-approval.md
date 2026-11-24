---
type: regex
pattern: '\nApproval: \d{4}-\d{2}-\d{2}, "approved, both diffs"\n'
match: contains
target: { source: file, path: upstream/greet/docs/prd/greet/changes/CS-001.md }
---

The record in greet holds the owner's reply verbatim on one Approval line with no ` (amendment)`: the stop was cleared
by the first approval. Fails when the record has no such line.
