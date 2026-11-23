---
type: regex
pattern: '(?:^|\n)Diagnosis: [^\n]*Hi, World!'
match: contains
target: { source: file, path: docs/prd/greet/errors.md }
---

The Diagnosis quotes what the run printed, `Hi, World!`: the actual output beside the expected one. The
adoption's Diagnosis, read from the code, holds no output.
