---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?!(?:uv run --script (?:\\")?\S*prd_publish\.py|(?:[\w./~+@,:${}-]*/prd|\\"[^"\\]*/prd\\")\s+publish(?![\w.-])))(?:[^"\\]|\\.)*?(?:\bsed\s+-i\S*\s(?:[^"\\]|\\.)*?docs/prd/|>>?\s*(?:\\"|'')?(?:[^\s"''\\]*/)?docs/prd/|\btee\s+(?:-a\s+)?(?:\\"|'')?(?:[^\s"''\\]*/)?docs/prd/|docs/prd/[^\s"''\\]*(?:\\"|'')?\)\.(?:write_text|write_bytes)\(|\bopen\(\s*(?:\\"|'')?(?:[^\s"''\\]*/)?docs/prd/[^,)]*,\s*(?:\\"|'')?[wa])'
min: 0
max: 0
---

No write under `docs/prd/` through Bash either (`sed -i`, a `>` or `>>` redirect, `tee`, a Python one-off).
A `prd_publish.py` call, or a `…/prd publish` call (its launcher path plain or in double quotes, at the command's start), is never counted: it reads `docs/prd/<slug>` and refuses an `--out` inside it. A
Python write counts only on a `docs/prd/` path itself (`Path("docs/prd/x").write_text(`), so RED's U2 driver,
which loads `docs/prd/greet` and writes `dist/greet-prd.html`, is not counted; a path first held in a variable
is missed.
