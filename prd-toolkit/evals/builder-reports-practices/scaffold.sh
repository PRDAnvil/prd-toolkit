#!/usr/bin/env bash
# Start state: build_repo.py's notes repo (FR-003 "Count notes" approved, count_notes not implemented) with
# a practices.md whose two code practices, P-01 and P-02, match the notes area's Boundary, so the implement pack
# holds both (scaffolds/practices_repo.py `build`); branch prd-round/notes-1 is checked out at the prompt's Base,
# 52b1bc2 (fixed by the scaffold's dates).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/practices_repo.py" "$PWD" build
test "$(git branch --show-current)" = prd-round/notes-1
test "$(git rev-parse HEAD)" = 52b1bc2443f590cc5a6938bad06e3f092276b5b9
grep -q '^| P-02 | S-01 |' docs/prd/notes/practices.md
test -z "$(git status --porcelain)"
