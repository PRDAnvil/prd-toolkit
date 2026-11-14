---
type: tool_used
tool: Bash
input_match: '(?:prd_build_check\.py|/prd(?:\\")?\s+build-check(?![\w.-]))[^"]*\s--diff\s+[0-9a-f]{7,40}\.\.prd-round/'
min: 1
---

The builder check runs on the round branch: `prd_build_check.py` (or `…/prd build-check`) `<prd dir> --diff <Base sha>..prd-round/<area>-<n>`,
not on `<base>..HEAD`.
