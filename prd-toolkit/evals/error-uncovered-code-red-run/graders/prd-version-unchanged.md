---
type: regex
pattern: '(?:^|\n)version: 1\.0\.0\n'
match: contains
target: { source: file, path: docs/prd/greet/prd.md }
---

The PRD is still at 1.0.0: no change was made through any route to give the helper a requirement or an area.
