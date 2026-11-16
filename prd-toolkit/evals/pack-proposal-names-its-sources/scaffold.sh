#!/usr/bin/env bash
# Start state: scaffolds/pack_repo.py `pair`: north/ and south/, each an Approved PRD that lints clean, and plug/, an
# empty plugin checkout. `prd pack compare` marks `pages` and `routes` `both`, `forms` `A` (north) and `feeds` `B`
# (south), and prints two planted differences as an `A` line and a `B` line: the `integration` level's command
# (`tests/integration` against `tests/site`) and the Harness slot `Tools on the runner` (`python3 on PATH` against
# `python3 and a headless browser on PATH`). With nobody to answer, the proposal is the report and nothing is written.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/pack_repo.py" "$PWD" pair
grep -q '^status: Approved$' north/docs/prd/north/prd.md
grep -q '^status: Approved$' south/docs/prd/south/prd.md
test -f plug/.claude-plugin/plugin.json
test ! -e plug/prd-packs
test "$(ls -A | tr '\n' ' ')" = "north plug south "
test -z "$(find . -name .venv -o -name .prd-toolkit -o -name CLAUDE.md)"
for repo in north south plug; do test -d "$repo/.git"; test -z "$(git -C "$repo" status --porcelain)"; done
