#!/usr/bin/env bash
# Start state: scaffolds/error_repo.py `confirmed-gone`: E-001 (greet ignores GREETING) recorded, proposed and
# confirmed as a `code bug` while the planted bug was in the code, then an ordinary commit that puts the GREETING key
# back without citing the entry. The entry is `confirmed` and HEAD no longer has the bug: T-001.2 passes and
# `greet World` prints `Hi, World!`. Only a run at the start of the fix shows there is nothing left to fix.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/error_repo.py" "$PWD" confirmed-gone
grep -q '^Confirmed: 2026-01-08, "Yes, it is a code bug."$' docs/prd/greet/errors.md
grep -q '^Resolution: -$' docs/prd/greet/errors.md
grep -qF 'load_settings().get("GREETING", "Hello")' src/greet/cli.py
test -z "$(git status --porcelain)"
