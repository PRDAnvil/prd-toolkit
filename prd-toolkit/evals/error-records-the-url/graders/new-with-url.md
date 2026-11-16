---
type: tool_used
tool: Bash
min: 1
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*?\b(?:prd(?:\\")?\s+error|prd_error\.py(?:\\")?)\s+new\s(?:[^"\\]|\\.)*?\s--url(?:\s+|=)(?:''|\\")?https://north\.example\.com/nothing(?:''|\\")?(?=\s|;|"|$)'
---

Step 1 records the entry with `prd error new … --url <address>`, the address exactly as the report gives it
(single-quoted, double-quoted or bare): never a longer, shorter or rebuilt one.
