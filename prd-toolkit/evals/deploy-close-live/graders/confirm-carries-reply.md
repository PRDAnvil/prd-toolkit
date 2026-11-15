---
type: tool_used
tool: Bash
input_match: '(?:prd_deploy\.py|/prd(?:\\")?\s+deploy) confirm.*deploy production'
min: 1
---

The user's reply is relayed through `prd_deploy.py confirm` (`…/prd deploy confirm`), carrying the reply.
