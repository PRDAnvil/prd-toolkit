---
type: regex
match: contains
target: last_message
pattern: '\b(?:pages|routes)\b[^\n]{0,160}\bboth\b(?!\s+(?:sites?|repos?\w*|PRDs?))|\bboth\b(?!\s+(?:sites?|repos?\w*|PRDs?))[^\n]{0,160}\b(?:pages|routes)\b|\b(?:pages|routes)\b[^\n]{0,200}\bnorth and south\b'
---

A shared type is marked `both`, on its own line of the proposal. "both sites", "both repositories" and "both PRDs"
are not the mark: the baseline's "`pages` and `routes` (both sites)" said that much with no comparison run.

Naming both PRDs on the type's line ("north and south `prd.md` section 7 row `pages`") counts as the mark: a session
of the 0.8.12 run wrote it so.
