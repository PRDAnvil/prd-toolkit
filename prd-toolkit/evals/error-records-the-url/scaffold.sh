#!/usr/bin/env bash
# Start state: scaffolds/pack_repo.py `error`: the north leaflet site as the repository itself, its PRD Approved and
# lint clean with an empty error ledger, no `.prd-toolkit/` (the skill runs the plugin's scripts) and no `.venv`. The
# user's report gives an address; step 1 records the entry with `--url` and that address, exactly as given, so the
# ledger's `URL:` line holds it.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/pack_repo.py" "$PWD" error
grep -q '^status: Approved$' docs/prd/north/prd.md
grep -q '^No entries yet' docs/prd/north/errors.md
test -z "$(find . -name .venv -o -name .prd-toolkit -o -name CLAUDE.md)"
test -d .git
test -z "$(git status --porcelain)"
