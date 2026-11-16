---
type: regex
flags: i
match: contains
target: last_message
pattern: '(?:claude|plugin manager)[^.\n]{0,100}(?:not (?:on|in) (?:the |your |this )?(?:PATH|sandbox|session|environment|machine)|not found|not available|unavailable|isn.t available|not installed|isn.t installed|\b127\b|could not (?:be )?(?:run|queried|found|reached)|couldn.t (?:be )?(?:run|queried|found|reached)|command not found|can.t (?:be )?(?:run|queried))|no marketplace (?:has been |is |was )?added|marketplace list[^.\n]{0,80}(?:\[\]|empty|none|nothing)|nothing to install (?:a plugin )?from'
---

The reply says there is nothing to install from: either the plugin manager could not be run (`claude` not on
PATH, exit 127) or, as in the eval sandbox, it lists no added marketplace (`[]`). The skill reports it and
proposes no plugin. Nothing in the eval can stand in for an added marketplace.
