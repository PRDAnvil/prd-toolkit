---
type: regex
pattern: '(?=[^\n]*(?<![\w-])memor(?:y|ies)\b)[^\n]*\bno\b[^\n]{0,20}\bnotes?\b|(?<![\w-])memor(?:y|ies)\b[^\n]{0,30}\bnotes?\b[^\n]{0,80}\b(?:none|not|only|unrelated|another|other)\b'
flags: i
target: last_message
---

The session says, in its report, that no memory note bears on this repository (the skill's "say so in one
line"): a line that names memory and says no note applies, or names memory notes and says they are another
project's. A toolkit that never reads memory says nothing about it. "in-memory", the service's own wording, is
not memory, and "memory is unreadable ... `none`" names no note, so neither passes (BASELINE 0.8.21, run 3).
