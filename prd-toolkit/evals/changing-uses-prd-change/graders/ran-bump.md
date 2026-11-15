---
type: tool_used
tool: Bash
input_match: '(?:prd_change\.py\S*|/prd(?:\\")?\s+change) bump'
min: 1
---

The version level comes from `prd_change.py bump` (`…/prd change bump`), not from reading the table by hand.
