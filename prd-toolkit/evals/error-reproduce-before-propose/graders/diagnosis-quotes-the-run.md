---
type: regex
pattern: '(?:^|\n)Diagnosis: [^\n]*\b[A-Z][A-Za-z]*, World!'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The Diagnosis quotes what the run printed, `<greeting>, World!` with the greeting the run set (`Hi, World!` with
the repository's own settings): the actual output beside the expected one. The
adoption's Diagnosis, read from the code, holds no output.
