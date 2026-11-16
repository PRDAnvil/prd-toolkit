---
type: regex
match: contains
target: last_message
pattern: '\b(?:pages|routes)\b[^\n]{0,160}\bboth\b(?!\s+(?:sites?|repos?\w*|PRDs?))|\bboth\b(?!\s+(?:sites?|repos?\w*|PRDs?))[^\n]{0,160}\b(?:pages|routes)\b'
---

A shared type is marked `both`, on its own line of the proposal. "both sites", "both repositories" and "both PRDs"
are not the mark: the baseline's "`pages` and `routes` (both sites)" said that much with no comparison run.
