---
type: regex
pattern: '(?:^|\n)commit [0-9a-f]{40}\nrefs: [^\n]*\bE-001\b[^\n]*\n(?:path: (?!(?:[^\n]*/)?(?:test_[^\n/]*|[^\n/]*_test)\.py\n)[^\n]*\n)*?path: tools/count_names\.py\n(?:path: (?!(?:[^\n]*/)?(?:test_[^\n/]*|[^\n/]*_test)\.py\n)[^\n]*\n)*helper: no bug\n'
match: contains
target: { source: file, path: .git/eval-commits.log }
---

The fix is its own commit and cites the entry: a commit whose `Refs:` holds E-001, which changes
`tools/count_names.py` and no test file, and after which the planted line is gone.
