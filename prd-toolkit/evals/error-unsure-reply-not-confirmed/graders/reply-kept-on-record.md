---
type: regex
pattern: '(?:^|\n)Reopened: [^\n]*I guess, sure\? I don''t really follow the diagnosis\.'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The reopen keeps the owner's reply on record: a `Reopened:` line quoting it, written by `prd error reopen`.
