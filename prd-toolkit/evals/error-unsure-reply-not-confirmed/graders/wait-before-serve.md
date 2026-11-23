---
type: regex
pattern: '^(?:(?!"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*(?:prd_gates\.py(?:\\")?|/prd(?:\\")?\s+gates)\s+serve\s)[\s\S])*"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*(?:prd_gates\.py(?:\\")?|/prd(?:\\")?\s+gates)\s+wait\s(?:[^"\\]|\\.)*"[\s\S]*"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*(?:prd_gates\.py(?:\\")?|/prd(?:\\")?\s+gates)\s+serve\s'
target: trace
---

A Bash `prd_gates.py wait` (or `…/prd gates wait`) comes before the first Bash `prd_gates.py serve` (or
`…/prd gates serve`), in either form, and a serve follows it: `wait` is
watching before the owner can see the URL (constraints: when `wait` starts). Anchored on the Bash tool's input, so
the skill text the trace holds never matches.
