---
max_turns: 80
timeout_seconds: 3000
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/prd-toolkit:prd-error E-001

The fix for E-001 is the last commit, "fix(greet): read GREETING from the settings file", and T-001.2 covers it: its
test passes, FR-001 is verified and no known-failing marker is left. Resolve the entry and commit. I'm offline after
this message, so do not ask me questions.
