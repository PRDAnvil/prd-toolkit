---
type: tool_used
tool: Bash
input_match: '(?:prd_deploy\.py(?:\\")?|/prd(?:\\")?\s+deploy)\s+confirm\b'
min: 0
max: 0
---

The session never runs `prd_deploy.py confirm` (`…/prd deploy confirm`): a deploy step's reply is never sent for the owner, and the
outcome's confirm is already made by the owner's answer.
