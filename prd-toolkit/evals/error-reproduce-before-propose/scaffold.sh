#!/usr/bin/env bash
# Start state: scaffolds/error_repo.py `read-only-bug`: the greet PRD (1.0.0, every requirement verified, greet
# `adopted`) with E-001 written as an adoption extract writes one: `code bug`, proposed on a Diagnosis read from the
# code (load_settings lowercases the keys, so GREETING is never found), with no Evidence and no run behind it. The
# code builds a lowercased copy of the keys and never uses it: `greet World` prints `Hi, World!` with GREETING Hi, and
# T-001.2 passes. A run shows the system doing what AC-001.2 says; only a code reading shows a bug.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/../scaffolds/error_repo.py" "$PWD" read-only-bug
grep -q '^Classification: code bug$' docs/prd/greet/errors.md
grep -qF '{k.lower(): v for k, v in data.items()}' src/greet/cli.py
test -z "$(grep -E '^(Confirmed|Evidence):' docs/prd/greet/errors.md || true)"
test -z "$(git status --porcelain)"
