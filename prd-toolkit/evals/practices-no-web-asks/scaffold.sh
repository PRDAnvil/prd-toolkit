#!/usr/bin/env bash
# Start state: the wordcount PRD Approved at 1.0.0 (scaffolds/practices_repo.py `no-sources`): no
# docs/sources/, no source named in the prompt, and the case grants no web tool. The skill says so and asks
# for sources; it writes no row and names no source it has not read.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/practices_repo.py" "$PWD" no-sources
grep -q '^status: Approved$' docs/prd/wordcount/prd.md
test ! -e docs/sources
test -z "$(git status --porcelain)"
