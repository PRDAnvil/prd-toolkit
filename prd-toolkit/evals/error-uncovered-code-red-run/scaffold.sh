#!/usr/bin/env bash
# Start state: scaffolds/error_repo.py `uncovered-bug`: the greet PRD with an adoption map whose one adopted area,
# greet, does not cover `tools/count_names.py`, a confirmed `code bug` E-001 for that helper (two names print 3),
# and a One test command on the unit level, so step 5's **Code no area covers** can run its red run. The helper
# has no test. The history graders read the session's commits from its trace.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/error_repo.py" "$PWD" uncovered-bug
grep -q '^Confirmed: 2026-01-09, ' docs/prd/greet/errors.md
grep -q '^Resolution: -$' docs/prd/greet/errors.md
grep -qF 'return len(text.split("\n"))' tools/count_names.py
grep -qF '| unit | `uv run pytest tests/unit` | local | build | `uv run pytest -q` |' docs/prd/greet/testing.md
grep -qF '| greet | adopted | `src/greet/**`, `tests/**`, `scripts/**` |' docs/prd/greet/adoption.md
test -z "$(git status --porcelain)"
