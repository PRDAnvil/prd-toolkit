---
type: tool_used
tool: Bash
input_match: '(?:prd_deploy\.py|/prd(?:\\")?\s+deploy)\s+record\b[\s\S]*--commit[\s=]+["'']?f4674c9'
min: 1
---

The deploy done by hand is recorded with `prd_deploy.py record` (`…/prd deploy record`), naming the commit the owner gave.
