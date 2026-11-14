---
type: tool_used
tool: Bash
input_match: '(?:prd_deploy\.py|/prd(?:\\")?\s+deploy) run'
min: 1
---

The deploy goes through `prd_deploy.py run` (`…/prd deploy run`), never the runbook's commands by hand.
