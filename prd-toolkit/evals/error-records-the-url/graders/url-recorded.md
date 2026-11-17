---
type: regex
match: contains
target: { source: file, path: docs/prd/north/errors.md }
pattern: '(?:^|\n)URL: https://north\.example\.com/nothing[ \t]*(?:\r?\n|$)'
---

The ledger's entry holds the `URL:` line with the report's address.
