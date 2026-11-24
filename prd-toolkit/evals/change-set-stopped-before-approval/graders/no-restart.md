---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*\bchangeset\s+(?:abandon|new)\b'
min: 0
max: 0
---

The stopped record is approved where it stands: no `changeset abandon` and no second `changeset new` for the same
members. Fails on any Bash call that runs either.
