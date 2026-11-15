---
type: regex
pattern: 'no module assigns to'
flags: i
match: contains
target: last_message
---

A passage of `lua-style.md` is quoted: "no module assigns to `_G`" is in that file and nowhere else, so it reaches
the reply only from a read of the file (step 4's quote).
