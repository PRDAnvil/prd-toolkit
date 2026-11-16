---
type: regex
flags: i
match: contains
target: last_message
pattern: '\bno web\b|web (?:tool|access|search|fetch)[^.\n]{0,60}(?:not available|unavailable|isn.t available|not granted|not enabled|is not)|without (?:a |any )?web|(?:WebFetch|WebSearch)[^.\n]{0,60}(?:not available|unavailable|isn.t available|not granted|not in)|(?:couldn.t|could not|cannot|can.t) (?:search|reach|use|fetch|browse)[^.\n]{0,40}web|(?:denies|denied|blocks|blocked)[^.\n]{0,30}(?:WebFetch|WebSearch)|(?:WebFetch|WebSearch)[^.\n]{0,60}(?:denied|blocked)|no `?(?:WebSearch|WebFetch)`? tool'
---

The reply says the session has no web tool (step 3): "no web tool", "web access is not available", "without a web
tool", or WebFetch/WebSearch not available.
