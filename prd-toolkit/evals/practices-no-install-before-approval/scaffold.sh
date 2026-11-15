#!/usr/bin/env bash
# Start state: the wordcount PRD Approved at 1.0.0 (scaffolds/practices_repo.py `release`), with
# docs/sources/quill-release.md. The prompt asks for an install from a marketplace already added. The eval
# sandbox has no `claude` on PATH, so `claude plugin marketplace list --json` exits 127 there: what is graded
# is that the skill tries the listing, says the plugin manager could not be run, runs no install and writes
# no row. That a real install waits for the approval rests on step 9's text and its pins, not on this case.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/practices_repo.py" "$PWD" release
grep -q '^status: Approved$' docs/prd/wordcount/prd.md
test -f docs/sources/quill-release.md
test ! -e .claude
test -z "$(git status --porcelain)"
