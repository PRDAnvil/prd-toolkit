---
type: regex
pattern: '\b(?:no|none|nothing|not)\b[^\n]{0,80}\bmemor(?:y|ies)\b|\bmemor(?:y|ies)\b[^\n]{0,80}\b(?:no|none|nothing|not|only|unrelated|another|other)\b'
flags: i
target: last_message
---

The session says, in its report, that no memory note bears on this repository (the skill's "say so in one
line"). A toolkit that never reads memory says nothing about it.
