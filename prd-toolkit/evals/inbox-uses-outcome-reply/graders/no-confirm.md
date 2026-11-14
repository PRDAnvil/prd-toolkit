---
type: tool_used
tool: Bash
input_match: '(?:prd_error\.py(?:\\")?|/prd(?:\\")?\s+error)\s+confirm\b'
min: 0
max: 0
---

The session never runs `prd_error.py confirm` (`…/prd error confirm`): the owner's answer in the inbox already confirmed the entry, and a
second confirm would be the session's own.
