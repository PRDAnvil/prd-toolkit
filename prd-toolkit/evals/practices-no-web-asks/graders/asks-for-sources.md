---
type: regex
flags: i
match: contains
target: last_message
pattern: '(?:send|give|name|share|point me|provide|tell me|paste|which|what)[^.\n?]{0,100}(?:sources?|URLs?|links?|guides?|documents?|docs|style guides?)'
---

The reply asks the owner for sources: a send, give, name, share, point, provide, tell, paste, which or what, then
sources, URLs, links, guides or documents, in one sentence.
