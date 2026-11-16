---
type: regex
pattern: '## 5\. Standards registry\n\n\| Object \(glob\) \| Linter command \| Rules live in \| Applies to \| Decision \|\n\|-{3}\|-{3}\|-{3}\|-{3}\|-{3}\|\n\n## 6\. Skills registry\n\nNot applicable: no skill is registered yet\.\n'
match: contains
target: { source: file, path: docs/prd/wordcount/prd.md }
---

Sections 5 and 6 are as the scaffold wrote them, by any tool: no standards or skills row is written before the
owner decides, so none can claim a Decision, an installed skill or a plugin.
