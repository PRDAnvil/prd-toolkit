---
type: regex
pattern: '(?:^|\n)commit [0-9a-f]{40}\nrefs: [^\n]*\n(?:path: (?:[^\n]*/)?(?:__init__|conftest)\.py\n)*path: (?:[^\n]*/)?(?:test_[^\n/]*|[^\n/]*_test)\.py\n(?:path: (?:(?:[^\n]*/)?(?:test_[^\n/]*|[^\n/]*_test)\.py|(?:[^\n]*/)?(?:__init__|conftest)\.py)\n)*helper: bug\n(?:[^\n]*\n)*?commit [0-9a-f]{40}\nrefs: [^\n]*\n(?:path: (?!(?:[^\n]*/)?(?:test_[^\n/]*|[^\n/]*_test)\.py\n)[^\n]*\n)*?path: tools/count_names\.py\n(?:path: (?!(?:[^\n]*/)?(?:test_[^\n/]*|[^\n/]*_test)\.py\n)[^\n]*\n)*helper: no bug\n'
match: contains
target: { source: file, path: .git/eval-commits.log }
---

The failing test is committed alone before the fix, in the end-state history. The scaffold's post-commit hook writes
one record per commit (its paths, and whether its tree still holds the planted line of `tools/count_names.py`): a
commit that changes only test files (`test_*.py` or `*_test.py`) while the bug is still in its tree, then a later
commit that changes `tools/count_names.py`, no test file, and leaves no bug. A test and its fix in one commit fail it,
and so does a test committed after the fix.
