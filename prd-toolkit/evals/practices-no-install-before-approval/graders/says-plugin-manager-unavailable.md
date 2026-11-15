---
type: regex
flags: i
match: contains
target: last_message
pattern: '(?:claude|plugin manager)[^.\n]{0,100}(?:not (?:on|in) (?:the |your |this )?(?:PATH|sandbox|session|environment|machine)|not found|not available|unavailable|isn.t available|not installed|isn.t installed|\b127\b|could not (?:be )?(?:run|queried|found|reached)|couldn.t (?:be )?(?:run|queried|found|reached)|command not found|can.t (?:be )?(?:run|queried))'
---

The reply says the plugin manager could not be run (`claude` not on PATH, exit 127): the skill reports it and
proposes no plugin. Nothing in the eval can stand in for an added marketplace.
