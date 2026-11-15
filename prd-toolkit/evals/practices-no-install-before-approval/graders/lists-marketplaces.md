---
type: tool_used
tool: Bash
min: 1
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*\bclaude\s+plugins?\s+marketplace\s+list\b'
---

Step 6.2 asks the plugin manager which marketplaces are added, with `claude plugin marketplace list --json`, before
any plugin is proposed.
