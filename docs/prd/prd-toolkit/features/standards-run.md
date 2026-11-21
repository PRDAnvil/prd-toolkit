<!-- Format: references/prd-format.md, "Requirement blocks". -->

# standards-run: the files a standards row is run on

An enforced section 5 row is run twice: by the pre-commit hook on the staged files its glob matches
(`prd-toolkit/scripts/prd_git_hook.py pre-commit`), and by the generated CI's job `standards-<n>` on
the tracked files its glob matches (`prd_hooks.py ci --github` or `--gitlab`). Neither runs it on the
vendored copy `.prd-toolkit/`, which must stay byte for byte what the plugin ships and so can never be
changed to pass a repository's own linter. One module says which files a row is run on,
`prd-toolkit/scripts/prdlint/standardsrun.py`; the same build makes `prdlint/githook.py` (area `trace`) and
`prdlint/hooks.py` (area `hooks-install`), neither adopted, call it, and what they do is stated
here. The vendored copy is the folder `.prd-toolkit` at the repository root: a folder of that name
anywhere else, and a file whose name only starts with it, is an ordinary path.

### FR-068 A standards row is never run on the vendored copy
Status: verified
Source: prd-toolkit/scripts/prdlint/standardsrun.py:4 @27aab93
Acceptance (EARS):
- AC-068.1 When the pre-commit hook (`prd_git_hook.py pre-commit <prd_dir>`) runs an enforced section 5
  row, it shall give the row's linter every staged path that exists after the commit and that the row's
  glob matches, as it did before this area, except each path that is `.prd-toolkit` or starts with
  `.prd-toolkit/`, paths taken relative to the repository root.
- AC-068.2 If no staged path is left for an enforced row once AC-068.1 leaves out the vendored copy,
  the pre-commit hook shall not run that row's linter, and with no other problem shall exit 0 and print
  nothing on stderr.
- AC-068.3 When a linter the pre-commit hook gives one or more paths exits other than 0, the hook shall
  print, as it did before this area, the stderr line
  ``prd-toolkit: `<command>` failed (exit <code>) on <paths>``, `<paths>` the paths it gave joined by
  `, `, followed by `:` and, on the next lines, the linter's stdout and then its stderr with surrounding
  white space removed, when there is any such output, and shall exit 1.
- AC-068.4 When `prd_hooks.py ci --github <prd_dir>` or `prd_hooks.py ci --gitlab <prd_dir>` writes its
  CI include, the hooks command shall give the job `standards-<n>` of each enforced row the one command
  `git ls-files -z --format='./%(path)' -- <pathspec> ':(exclude).prd-toolkit' | xargs -0 -r <command>`,
  where `<pathspec>` is `:(glob)<glob>` quoted as a shell word, as before this area, and `<command>` the
  row's linter command; the command being, read as YAML, the value at `jobs.standards-<n>.steps.2.run`
  of `.github/workflows/prd-toolkit.yml` and at `standards-<n>.script.0` of `.gitlab/prd-toolkit.yml`.
- AC-068.5 When a CI include present in the repository differs from what `prd_hooks.py ci` would write
  now, a file an earlier release wrote included, `prd_hooks.py check --ci <prd_dir>` shall print the
  line `stale: <file>: re-run prd_hooks.py ci --<forge> --force` and exit 1.
Errors: -
Edge cases: a repository with no `.prd-toolkit/` folder is run exactly as before → AC-068.1, AC-068.4; `src/.prd-toolkit/x.py` and `.prd-toolkit-notes.py` are not the vendored copy and are run → AC-068.1, AC-068.4; a path the hook passes as `./<path>` because it starts with `-` is never under `.prd-toolkit/` → AC-068.1; the commit-msg hook and its `Refs:` rule are unchanged; the CI's job runs from the repository root, as before → AC-068.4; the hook runs a row's linter from the repository root, as it did before this requirement, with the paths it passes relative to that root → AC-068.1
Tests: T-068.1 [integration], T-068.2 [integration], T-068.3 [integration], T-068.4 [integration], T-068.5 [integration], T-068.6 [integration], T-068.7 [integration]  (test-cases/standards-run.yaml)
Traces: cli:prd_git_hook; cli:prd_hooks; E-025
