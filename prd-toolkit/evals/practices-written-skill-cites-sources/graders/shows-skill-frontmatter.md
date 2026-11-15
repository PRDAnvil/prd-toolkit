---
type: regex
match: contains
target: last_message
pattern: 'name:\s*[a-z0-9][a-z0-9-]*[ \t]*\n[\s>]*description:'
---

The reply shows the skill's full text, from its frontmatter (`name:` then `description:`).
