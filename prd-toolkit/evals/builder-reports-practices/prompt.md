---
max_turns: 100
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write, Edit, Bash]
---

Dispatch the prd-builder agent with exactly this prompt and nothing else, then show me its report as it gave it.
Change nothing yourself. Do not ask me questions.

```
Mode: build
PRD: docs/prd/notes/
Area: notes
IDs: FR-003
Unit T-ids: T-003.1 (docs/prd/notes/test-cases/notes.yaml)
Base: 52b1bc2443f590cc5a6938bad06e3f092276b5b9
Branch: prd-round/notes-1
```
