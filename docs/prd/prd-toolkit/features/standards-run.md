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

A row also says how its command takes files, its files mode (FR-264): `appended`, the default, gives
the command the matching files, as FR-068 says; `none` runs it once with no files, for a command that
checks a whole tree or one target; `changed` gives it only the matching files the branch changed.

### FR-068 A standards row is never run on the vendored copy
Status: verified
Source: prd-toolkit/scripts/prdlint/standardsrun.py:5 @ae307f1
Acceptance (EARS):
- AC-068.1 When the pre-commit hook (`prd_git_hook.py pre-commit <prd_dir>`) runs an enforced section 5
  row whose files mode (FR-264) is `appended`, it shall give the row's linter every staged path that
  exists after the commit and that the row's glob matches, as it did before this area, except each path
  that is `.prd-toolkit` or starts with `.prd-toolkit/`, paths taken relative to the repository root.
- AC-068.2 If no staged path is left for an enforced row once AC-068.1 leaves out the vendored copy,
  the pre-commit hook shall not run that row's linter, and with no other problem shall exit 0 and print
  nothing on stderr.
- AC-068.3 When a linter the pre-commit hook gives one or more paths exits other than 0, the hook shall
  print, as it did before this area, the stderr line
  ``prd-toolkit: `<command>` failed (exit <code>) on <paths>``, `<paths>` the paths it gave joined by
  `, `, followed by `:` and, on the next lines, the linter's stdout and then its stderr with surrounding
  white space removed, when there is any such output, and shall exit 1.
- AC-068.4 When `prd_hooks.py ci --github <prd_dir>` or `prd_hooks.py ci --gitlab <prd_dir>` writes its
  CI include, the hooks command shall give the job `standards-<n>` of each enforced row whose files mode
  (FR-264) is `appended` the one command
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

### FR-264 A standards row says how its command takes files
Status: verified
Source: prd-toolkit/scripts/prdlint/standardsrun.py:6 @ef5b43e
Flow: 1. read the row's files mode from the second backticked span of its Linter command cell
      → 2a. `appended` (the default): the matching files are given, as FR-068 says
        2b. `none`: the command runs once with no file, when a file matches
        2c. `changed`: CI gives only the matching files changed since the merge request's base; the pre-commit hook gives the staged ones
Acceptance (EARS):
- AC-264.1 The pre-commit hook and the hooks command (`prd_hooks.py ci`) shall take a section 5 row's
  files mode from the second backticked span of its Linter command cell: when that span's text,
  stripped, starts with `files:`, the mode is the rest of the text, stripped; when the cell holds no
  second backticked span, or its second span does not start with `files:`, the mode is `appended`. They
  shall run a row whose files mode is not one of `appended`, `none` and `changed` as an `appended` row.
- AC-264.2 When `prd_hooks.py ci --github <prd_dir>` or `prd_hooks.py ci --gitlab <prd_dir>` writes its
  CI include, the hooks command shall give the job `standards-<n>` of each enforced row whose files mode
  is `none` the one command
  `if [ -n "$(git ls-files -- <pathspec> ':(exclude).prd-toolkit')" ]; then <command>; fi`, `<pathspec>`
  and `<command>` as AC-068.4 gives them and the command read where AC-068.4 reads it: the job runs the
  row's command once, with no path, when a tracked file outside the vendored copy matches the glob, and
  exits 0 without running it when none does.
- AC-264.3 When `prd_hooks.py ci --github <prd_dir>` or `prd_hooks.py ci --gitlab <prd_dir>` writes its
  CI include, the hooks command shall give the job `standards-<n>` of each enforced row whose files mode
  is `changed` the one command
  `git diff -z --name-only --diff-filter=d --line-prefix=./ <base>...HEAD -- <pathspec> ':(exclude).prd-toolkit' | xargs -0 -r <command>`,
  `<base>` being `$CI_MERGE_REQUEST_DIFF_BASE_SHA` in `.gitlab/prd-toolkit.yml` and
  `${{ github.event.pull_request.base.sha }}` in `.github/workflows/prd-toolkit.yml`, the base the range
  of the job `prd-trace` starts from (FR-114), and `<pathspec>` and `<command>` as AC-068.4 gives them,
  the command read where AC-068.4 reads it; in `.gitlab/prd-toolkit.yml` that job shall also set the
  variable `GIT_DEPTH` to `"0"`, read as YAML at `standards-<n>.variables.GIT_DEPTH`.
- AC-264.4 When the pre-commit hook runs an enforced row whose files mode is `none` and one or more
  staged paths that the row's glob matches are left once AC-068.1 leaves out the vendored copy, it shall
  run the row's linter once, from the repository root, with no path argument; when no such path is left,
  it shall not run the linter, as AC-068.2 says.
- AC-264.5 When a linter the pre-commit hook runs with no path argument (AC-264.4) exits other than 0,
  the hook shall print on stderr what AC-068.3 prints for a linter given paths, with the text
  ` on <paths>` left out, and shall exit 1.
- AC-264.6 When the pre-commit hook runs an enforced row whose files mode is `changed`, it shall give the
  row's linter the paths AC-068.1 gives an `appended` row, and AC-068.2 and AC-068.3 shall hold for it as
  for an `appended` row: a commit's changes are its staged paths.
Errors: -
Edge cases: `files: appended` written out is the default → AC-264.1; a second span that does not start with `files:` (`` `--fix` ``) sets no mode → AC-264.1; a mistyped mode is reported by lint (AC-133.5) and run as `appended` → AC-264.1; a PRD whose rows name no mode gets the hook and the CI it got before → AC-264.1, AC-068.1, AC-068.4; a `none` row whose glob matches only the vendored copy runs nothing → AC-264.2, AC-264.4; a file deleted on the branch is not given in `changed` mode → AC-264.3; the generated CI runs only on a merge request or a pull request, so `<base>` is set → AC-264.3; on GitHub every job already fetches the whole history → AC-264.3
Tests: T-264.1 [integration], T-264.2 [integration], T-264.3 [integration], T-264.4 [integration], T-264.5 [integration], T-264.6 [integration], T-264.7 [integration], T-264.8 [integration], T-264.9 [integration]  (test-cases/standards-run.yaml)
Traces: cli:prd_git_hook; cli:prd_hooks; FR-068; FR-114; FR-133; E-074
