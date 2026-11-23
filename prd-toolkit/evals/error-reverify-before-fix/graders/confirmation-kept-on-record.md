---
type: regex
pattern: '(?:^|\n)Reopened: [^\n]*Yes, it is a code bug\.'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The reopen keeps the earlier confirmation on record: a `Reopened:` line quoting its reply.
