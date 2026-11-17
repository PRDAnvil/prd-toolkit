#!/usr/bin/env bash
# Start state: scaffolds/pack_repo.py `pair`: north/ and south/, each an Approved PRD that lints clean, and plug/, an
# empty plugin checkout. The prompt is the owner's reply to a proposal shown earlier in the same conversation (quoted
# in it), every item decided and plug/ named, going on from step 4. What is graded: the pack folder holds
# `pack.yaml` without the items left out, the copied validator `check_pages.py`,
# one bad sample per type and a README, and nothing else is written: no helper code, no `clarify.md` or `rubrics.md`,
# no skill, and the PRDs untouched. A hand-written pack of exactly those files passes `prd pack check`
# (tests/test_pack_evals.py).
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
