---
type: regex
pattern: '/(prd-toolkit:)?prd-deploy[^\n]*\blive\b|\blive\b[^\n]*/(prd-toolkit:)?prd-deploy'
flags: i
target: last_message
---

The last message says that `live` waits for a later `/prd-deploy` run (both on one line), not the trace: the skill
text the trace holds carries the same words. The command is matched under its full name too,
`/prd-toolkit:prd-deploy`, the name the skills have printed since 0.8.7.
