<!-- Format: references/prd-format.md, "Requirement blocks". -->

# eval-scaffolds: the start states the deploy and review evals build

An eval case under `prd-toolkit/evals/<case>/` builds its start state with `scaffold.sh`, run in an empty
folder; a case whose `scaffold.sh` exits other than 0 never runs. Six deploy cases build theirs with
`python3 -B prd-toolkit/evals/scaffolds/deploy_repo.py <dst> <state>`, `<state>` one of `ready`, `staging-done`,
`failing-check`, `at-gate` and `at-ui-steps`, and then require `git status --porcelain` to print nothing.
`deploy_repo.py` runs the plugin's `prd_hooks.py install` and committed only `.gitignore` and `.prd-toolkit`
after it, while install also writes `CLAUDE.md`, `docs/prd/README.md` and `docs/prd/greet/README.md`; those
stayed untracked, so the six cases never ran. A seventh case, `review-edits-nothing`, stopped because its
`scaffold.sh` expected the index row of a requirement that moved back to `approved` to keep its Since value,
and `prd_change.py record` writes that row with an empty Since (E-019). This area's one module is
`prd-toolkit/evals/scaffolds/install_files.py`, which commits what install left untracked. The same build edits
two files outside it: `prd-toolkit/evals/scaffolds/deploy_repo.py`, to call the module, and
`prd-toolkit/evals/review-edits-nothing/scaffold.sh`, to expect the row `record` writes. No other file changes.

### FR-073 The deploy and review eval scaffolds build their start states
Status: approved
Acceptance (EARS):
- AC-073.1 When `deploy_repo.py` builds any of its five states, it shall commit every file that
  `prd_hooks.py install` wrote and that `git status --porcelain` lists as untracked after the commit
  `Vendor the PRD toolkit` (today `CLAUDE.md`, `docs/prd/README.md` and `docs/prd/greet/README.md`), so that
  `git status --porcelain` in the built repository prints nothing when the build ends.
- AC-073.2 The commit of AC-073.1 shall be one commit that holds those files and no other, with the message
  `Add the files install wrote`, an empty line, then `Refs: none (no behaviour change)`, and the author and
  committer date `2026-01-05T13:00:00+0000`, made directly after the commit `Vendor the PRD toolkit` and before
  any commit or deploy run a state adds; every commit before it keeps its subject, its date and its files.
- AC-073.3 When `prd-toolkit/evals/review-edits-nothing/scaffold.sh` runs in an empty folder, it shall exit 0,
  and its check of FR-001's index row shall expect the row `prd_change.py record` writes for a requirement that
  moved from `live (since 1.0.0)` to `approved`: `| FR-001 | Import an orders file | approved | features/import.md |  |`.
Errors: -
Edge cases: with nothing untracked after `Vendor the PRD toolkit`, `deploy_repo.py` makes no commit for AC-073.1 → AC-073.1; an ignored file (`.deploy/`, `.venv/`, a cache folder) is not committed → AC-073.1; a commit made before install keeps its SHA, since the new commit comes after all of them, so the case `deploy-by-hand-records` still finds the PRD commit by the SHA its prompt names → AC-073.2; `doc_repo.py` and `link_repo.py` also run install and no case of theirs requires a clean tree, so they are unchanged; the case `deploy-confirms-named-steps` requires only a clean tracked tree and passes before and after
Tests: T-073.1 [integration], T-073.2 [integration], T-073.3 [integration], T-073.4 [integration]  (test-cases/eval-scaffolds.yaml)
Traces: cli:eval_scaffolds; E-019
