#!/usr/bin/env bash
# Start state: the linked pair of scaffolds/link_repo.py, state `cs-stopped` (greet-client, which prints a banner around
# the greeting of greet's staging install, and greet, the repo of the `cli` contract; links.md on both sides): CS-001
# with both PRD edits committed In review and a stop at greet-client's step 2 lint before any approval. The session's
# repository is the client; greet sits at upstream/greet inside it (git-ignored there), so a grader can read the
# record, reached by the relative Location in links.md.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/link_repo.py" "$PWD" cs-stopped
test -f upstream/greet/docs/prd/greet/changes/CS-001.md
test -z "$(git status --porcelain)"
