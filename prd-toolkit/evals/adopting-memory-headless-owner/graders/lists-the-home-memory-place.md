---
type: regex
pattern: 'home/\.claude/projects/-[A-Za-z0-9-]*-home-cwd/memory'
target: trace
---

The runner denies the session its config dir, the first memory place, so the notes are read from the second:
`$HOME/.claude/projects/<encoded repo root>/memory/`. A session that stops at the denied first place and
calls memory unreadable never lists it. The skill's own text names the place only as a pattern, so it does
not match.

What it can see: a mention of the expanded path anywhere in the trace, in a tool call, its result or the
session's prose. A mention is not proof of a listing. A listing written with `$HOME` or `~` and no expanded
path in its output does not match. The pattern depends on the runner's sandbox home being named `home`,
with the scaffold's working directory `home/cwd`.
