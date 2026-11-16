---
type: regex
match: contains
target: last_message
pattern: 'tests/integration\b[\s\S]*\btests/site\b|\btests/site\b[\s\S]*tests/integration\b'
---

The first planted difference is shown with both sides: north's `integration` command (`tests/integration`) and
south's (`tests/site`).
