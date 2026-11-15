#!/usr/bin/env bash
# Start state: the wordcount PRD Approved at 1.0.0 (scaffolds/practices_repo.py `release`), with
# docs/sources/quill-release.md, the only text on releasing a Quill plugin. No skill covers the activity, so
# the proposal holds the full text of a repository-local skill, with its Sources line, and no file is written
# before the approval.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/practices_repo.py" "$PWD" release
grep -q 'quill pack' docs/sources/quill-release.md
test ! -e .claude
test -z "$(git status --porcelain)"
