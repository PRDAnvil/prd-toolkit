---
type: regex
pattern: '(?:^|\n)Resolution: fixed in [0-9a-f]{7,40}, red run \S+ \[unit\][ \t]*(?:\r?\n|(?![\s\S]))'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The final ledger holds the fourth form of Resolution line, `fixed in <sha>, red run <test id> [unit]`, at the unit
level, the one build-gate level with a One test command.
