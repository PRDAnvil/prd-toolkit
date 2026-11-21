#!/usr/bin/env bash
# Start state: scaffolds/error_repo.py `green-before-fix`: a confirmed `code bug` E-001 that names T-001.2, a fix
# commit that does fix the bug, FR-001 `verified` and no `known-failing` marker, and a One test command on the unit
# level. The T-001.2 test was rewritten before the entry to pass whichever settings key the code reads, so it passes
# on the fix and on its parent: nothing on HEAD looks wrong, and only `prd error replay` shows the proof does not
# hold. The reflog is emptied, so any commit, reset or revert the run makes is a line in .git/logs/HEAD.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/error_repo.py" "$PWD" green-before-fix
test "$(git log -1 --format=%s)" = "fix(greet): read GREETING from the settings file"
grep -q '^Confirmed: 2026-01-08, ' docs/prd/greet/errors.md
grep -q '^Resolution: -$' docs/prd/greet/errors.md
grep -qF 'load_settings().get("GREETING", "Hello")' src/greet/cli.py
grep -qF '"greeting": "Hi"' tests/unit/test_greet.py
grep -qF '| unit | `uv run pytest tests/unit` | local | build | `uv run pytest -q` |' docs/prd/greet/testing.md
test -z "$(grep -rl 'known-failing' docs/prd/greet/test-cases tests || true)"
git reflog expire --expire=now --all
test ! -s .git/logs/HEAD
test -z "$(git status --porcelain)"
