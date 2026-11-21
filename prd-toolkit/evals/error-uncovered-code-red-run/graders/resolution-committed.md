---
type: regex
pattern: '(?:^|\n)ledger: red run\n'
match: contains
target: { source: file, path: .git/eval-commits.log }
---

The red run is committed: a commit the session made holds an `errors.md` whose entry has the red-run Resolution line
(the recorder's `ledger: red run`). A line left in the working tree fails it.
