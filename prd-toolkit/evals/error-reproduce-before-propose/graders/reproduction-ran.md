---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?!(?:uv run --script \S*prd_error\.py|(?:[\w./~+@,:${}-]*/prd|\\"[^"\\]*/prd\\")\s+error)\s)(?:[^"\\]|\\.)*?(?:\buv\s+run\b|\bpython[0-9.]*\b)(?:[^"\\]|\\.)*?(?:-m\s+greet\b|\bpytest\b|load_settings|\bgreet\.cli\b)'
min: 1
---

A run that could show the failure: the T-001.2 test (pytest through `uv run` or `python -m`), `greet` itself
(`python -m greet`), or a probe that imports `greet.cli` and drives `load_settings` or `main`, each through an interpreter. A `prd_error.py` call, or a
`…/prd error` call (its launcher path plain or in double quotes, at the command's start), is never counted: its
diagnosis may quote a command it does not run. A `cat` or `grep` of the code is a reading, not a run.

A code reading is a hypothesis: the entry's class is settled on a run.
