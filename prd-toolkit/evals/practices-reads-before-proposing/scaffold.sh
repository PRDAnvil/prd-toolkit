#!/usr/bin/env bash
# Start state: the wordcount PRD (a Lua plugin for the Quill editor, a platform no pack covers) Approved at
# 1.0.0, no practices.md (scaffolds/practices_repo.py `two-sources`). docs/sources/ holds lua-style.md and
# quill-plugin-guide.md, each with a phrase no other text holds, so a quoted passage shows it was read.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/practices_repo.py" "$PWD" two-sources
grep -q '^status: Approved$' docs/prd/wordcount/prd.md
test -f docs/sources/lua-style.md
test -f docs/sources/quill-plugin-guide.md
test ! -e docs/prd/wordcount/practices.md
test -z "$(git status --porcelain)"
