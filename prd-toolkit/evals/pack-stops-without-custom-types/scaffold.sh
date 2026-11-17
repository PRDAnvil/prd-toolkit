#!/usr/bin/env bash
# Start state: scaffolds/pack_repo.py `no-custom`: north/ and south/, each an Approved PRD that lints clean, and plug/,
# an empty plugin checkout. South's section 7 holds only the built-in `errors` row, so the two PRDs share no custom
# contract type and `prd pack compare` exits 1 with `share no custom contract type; there is no pack to write`.
# What is graded: the skill quotes that line, stops, and proposes and writes nothing.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/pack_repo.py" "$PWD" no-custom
grep -q '^status: Approved$' north/docs/prd/north/prd.md
grep -q '^status: Approved$' south/docs/prd/south/prd.md
test -f plug/.claude-plugin/plugin.json
test ! -e plug/prd-packs
test "$(grep -c '^| pages |' south/docs/prd/south/prd.md || true)" = 0
test "$(ls -A | tr '\n' ' ')" = "north plug south "
test -z "$(find . -name .venv -o -name .prd-toolkit -o -name CLAUDE.md)"
for repo in north south plug; do test -d "$repo/.git"; test -z "$(git -C "$repo" status --porcelain)"; done
