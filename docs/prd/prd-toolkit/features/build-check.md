<!-- Format: references/prd-format.md, "Requirement blocks". -->

# build-check: the build's mechanical checks of a round's range, a tester's RESULTS and stale tests

### FR-186 Refuse a call that does not name exactly one check
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prd_build_check.py:33 @2caf953
Acceptance (EARS):
- AC-186.1 If `prd_build_check.py` gets no `<prd_dir>`, or none or more than one of `--diff`, `--results` and
  `--stale`, or `--results` or `--stale` with no `--tids` or an empty one, or `--sources` with no `--diff`, the
  check shall print its usage line on stderr and then the line
  `prd_build_check: give exactly one of --diff, --results (with --tids) or --stale (with --tids); --sources goes with --diff`,
  print nothing on stdout, and exit 2, before it reads the PRD folder.
- AC-186.2 If an argument is one the parser does not know, or an option lacks its value, the check shall print
  the parser's `prd_build_check.py: error: …` message on stderr and exit 2.
- AC-186.3 When the check runs with `-h` or `--help`, it shall print its help, which starts
  `usage: prd_build_check.py`, on stdout and exit 0.
Errors: -
Edge cases: an empty value (`--diff ""`) counts as the option being absent → AC-186.1; `--tids` given with `--diff` is accepted and not read → AC-186.1
Tests: T-186.1 [integration], T-186.2 [integration], T-186.3 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-187 Check the three packages before anything else
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prd_build_check.py:15 @2caf953
Acceptance (EARS):
- AC-187.1 If `pyyaml`, `sqlglot` or `openapi-spec-validator` cannot be imported, the check shall print the
  missing-package line of FR-010 (AC-010.2) for the first one missing in that order, and exit 2, before
  it reads its arguments, `--help` included.
Errors: -
Edge cases: the line lists the packages of the script's header, `pyyaml sqlglot openapi-spec-validator` → AC-187.1
Tests: T-187.1 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check; FR-010

### FR-188 Stop on a PRD folder that cannot be loaded
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prd_build_check.py:38 @2caf953
Acceptance (EARS):
- AC-188.1 If `<prd_dir>` holds no `prd.md`, the check shall print `prd_build_check: ` and then the loader's
  message (`<folder>: no prd.md`, `<folder>` the folder's resolved absolute path) on stderr, print nothing
  on stdout, and exit 2.
- AC-188.2 If section 8 of `prd.md` still holds a table and the folder has no `adoption.md`, the check shall
  print
  `prd_build_check: <folder>/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."`
  on stderr, print nothing on stdout, and exit 2, in every mode and before it reads a `--results` or
  `--sources` file.
Errors: -
Edge cases: the load happens after the usage check of FR-186, so a usage error wins → AC-186.1
Tests: T-188.1 [integration], T-188.2 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-189 Refuse a range that is not two commits
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prdlint/buildcheck.py:127 @2caf953
Acceptance (EARS):
- AC-189.1 If the `--diff` value is not `<base>..<head>`, with each end non-empty, starting with a character
  other than `.` and holding no white space, or it holds `...`, the check shall print
  `prd_build_check: bad range <value>: expected <base>..<head>` on stderr, print nothing on stdout, and exit 2;
  `<base>..<head>` is printed as those literal words.
- AC-189.2 If an end of the range does not name a commit, the check shall print
  `prd_build_check: bad range <value>: <end> is not a commit` on stderr for the first such end, `<base>`
  read before `<head>`, print nothing on stdout, and exit 2.
Errors: -
Edge cases: `--sources` takes the same range and the same refusals; the `--diff` check refuses first → AC-189.1
Tests: T-189.1 [integration], T-189.2 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-190 Fail a round that edits the PRD folder
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prdlint/buildcheck.py:148 @2caf953
Acceptance (EARS):
- AC-190.1 When `--diff <base>..<head>` reads a changed path (a path `git diff --name-status -M` names for the
  range, from the repository root; a renamed file gives its old and its new path) that equals the PRD folder
  or lies inside it, the check shall print `<path>: the builder may not edit the PRD folder` on stdout,
  once per path, and exit 1. Where the PRD folder is the repository root, every changed path lies inside it,
  `.prd-toolkit/` paths included, and gets this line.
- AC-190.2 When the range changes no path in the PRD folder, none under `.prd-toolkit/` and no tester's test
  (FR-074), the check shall print nothing and exit 0.
Errors: -
Edge cases: the PRD folder at the repository root: every change is the builder editing it → AC-190.1; a file moved out of the PRD folder is reported by its old path → AC-190.1; a file moved into it by its new path → AC-190.1; the lines come in the order git lists the paths, and before every `.prd-toolkit/` line → AC-190.1, AC-191.1
Tests: T-190.1 [integration], T-190.2 [integration], T-190.3 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check; FR-074

### FR-191 Fail an edit of the vendored copy where the repository holds no one plugin
Status: approved
Source: prd-toolkit/scripts/prdlint/buildcheck.py:163 @2caf953
Acceptance (EARS):
- AC-191.1 When the range changes a path that is `.prd-toolkit` or lies under `.prd-toolkit/`, and `<head>`'s
  tree holds no plugin directory or more than one, the check shall print
  `<path>: the builder may not edit the vendored .prd-toolkit/ copy` on stdout for each such changed path, in
  the order git lists them, after every other line of the `--diff` check, and exit 1. A plugin directory is a
  folder `<d>` of `<head>`'s tree (the root included) that holds `<d>/.claude-plugin/plugin.json`, a JSON
  object whose `name` is `prd-toolkit`, and `<d>/scripts/prd_hooks.py`.
- AC-191.2 The check shall read the paths of `<head>`'s tree unquoted (as `git ls-tree -z` gives them), so a
  plugin directory whose path holds a character outside ASCII counts as AC-191.1 defines it, and an exact refresh
  of `.prd-toolkit/` there is compared as AC-192.1 says.
Errors: -
Edge cases: a `plugin.json` that is not JSON, or whose `name` is another, makes no plugin directory → AC-191.1; a second plugin directory added in the same range counts → AC-191.1
Tests: T-191.1 [integration], T-191.2 [integration], T-191.3 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-192 Accept only an exact refresh of the vendored copy where the repository holds the plugin
Status: approved
Source: prd-toolkit/scripts/prdlint/buildcheck.py:159 @2caf953
Acceptance (EARS):
- AC-192.1 When the range changes a path under `.prd-toolkit/` and `<head>`'s tree holds exactly one plugin
  directory (AC-191.1), the check shall compare `.prd-toolkit/` at `<head>` with what
  `prd_hooks.py vendor <PRD folder>` of that directory writes when run on a copy of `<head>`'s files whose
  `.prd-toolkit/` is removed first; for each path that differs (its bytes, its owner execute bit, or present on
  one side only, `__pycache__` folders of the written copy left out) it shall print
  `<path>: differs from the plugin; refresh it with prd_hooks.py vendor` on stdout, the paths sorted, and exit 1.
- AC-192.2 The comparison of AC-192.1 shall cover every path of `.prd-toolkit/`, a path the range did not
  change included.
- AC-192.3 When `.prd-toolkit/` at `<head>` equals what that vendor run writes, the check shall print no line
  for a `.prd-toolkit/` path; with no other finding it prints nothing and exits 0.
- AC-192.4 If that vendor run exits other than 0, the check shall print
  `prd_build_check: vendor at <first 12 characters of <head>'s full SHA>: <first line of its stderr, else of its stdout, else failed>`
  on stderr, print nothing on stdout, and exit 2.
Errors: -
Edge cases: the vendor run reads `<head>`'s files, never the working tree → AC-192.1; a hand-added file under `.prd-toolkit/` differs → AC-192.1; a deleted vendored file differs → AC-192.1
Tests: T-192.1 [integration], T-192.2 [integration], T-192.3 [integration], T-192.4 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-193 Hold SOURCES lines to the round's hunks
Status: approved
Source: prd-toolkit/scripts/prdlint/buildcheck.py:172 @2caf953
Acceptance (EARS):
- AC-193.1 When `--diff <base>..<head> --sources <file>` runs, the check shall read each non-blank line of the
  file as `<ID>: <path>:<line>`, with optional leading white space, an optional `SOURCES` or `SOURCES:` and an
  optional `- ` or `* ` bullet before it and optional white space after it, where `<ID>` is a letter, word
  characters, `-`, digits and an optional `.` and digits, and `<line>` is the digits at the line's end; for a
  line that is not of that form it shall print `sources: line <n> is not '<ID>: <path>:<line>'` on stdout,
  `<n>` the line's number in the file from 1, blank lines counted.
- AC-193.2 If a line's `<path>` is not a path `git diff --name-only --no-renames` names for the range, the check
  shall print `sources: <ID>: <path> is not changed in <range>` on stdout, `<range>` the `--diff` value as given.
- AC-193.3 If a line's `<line>` lies in no hunk of the path's diff between `<base>` and `<head>`, the check shall
  print `sources: <ID>: <path>:<line> is outside the round's changes (hunks <a>-<b>, …)` on stdout; a hunk
  covers the lines it adds or changes on the `<head>` side, and a hunk that only deletes covers its
  `<head>`-side start line and the line after it; the hunks are listed in diff order, joined by `, `.
- AC-193.4 When `--sources` gives a line, the check shall print the `sources:` lines in the file's line order,
  after every line of the `--diff` check, and exit 1; a file whose every line passes adds no line.
- AC-193.5 The check shall read each line's `<path>` literally, as the `--diff` and `--stale` checks read theirs:
  a line passes AC-193.3 only on a hunk of that exact file, a path that holds `*`, `?` or `[` included.
Errors: -
Edge cases: `SOURCES: FR-003: src/app.py:1` is read as `FR-003` → AC-193.1; prose after the line number makes no line number → AC-193.1; a renamed file's old and new paths both count as changed → AC-193.2
Tests: T-193.1 [integration], T-193.2 [integration], T-193.3 [integration], T-193.4 [integration], T-193.5 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-194 Check a tester report's RESULTS block
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prdlint/buildcheck.py:222 @2caf953
Acceptance (EARS):
- AC-194.1 When `--results <report> --tids <T-ids>` runs, the check shall read the report's lines, each stripped
  of the white space around it, take as the heading the first line that is optional `#` signs, optional white
  space, an optional `<digits>.` and white space, an optional `**`, and then the word `RESULTS`, and take as
  result lines the lines after it that start, after an optional `- ` or `* ` bullet, with a T-id
  (`T-<3 digits>.<digits>`), skipping blank lines before the first one; the first line after that is blank or
  does not start so ends the block, and nothing after it, or before the heading, is read.
- AC-194.2 When a result line's T-id is not one of `--tids`, the check shall print `<T-id> was not dispatched` on
  stdout, once for each such line; when it is, and the line, less its bullet, is not `<T-id>: pass`,
  `<T-id>: fail: <reason>` (a reason of one or more characters) or `<T-id>: known-failing E-<digits>`, it shall
  print `<T-id>: not one of pass, fail: <reason>, known-failing E-nnn`; these lines come in the report's order.
- AC-194.3 When a T-id of `--tids` has more than one result line, the check shall print
  `<T-id>: more than one RESULTS line` once, after every line of AC-194.2, these lines in the order of each
  T-id's first result line.
- AC-194.4 When a T-id of `--tids` has no result line, a report with no heading included, the check shall print
  `<T-id> has no RESULTS line`, after every other line, in the order of `--tids`.
- AC-194.5 When every T-id of `--tids` has exactly one result line in one of the three forms and the block holds
  no other T-id, the check shall print nothing and exit 0; with any line printed it exits 1.
Errors: -
Edge cases: `--tids` is split at commas and each part stripped, empty parts dropped → AC-194.4; notes after a blank line that follows the result lines are not read, T-ids in them included → AC-194.1, AC-194.5; the check never reads the PRD's test cases, so a `known-failing` line is accepted whatever the case says → AC-194.2
Tests: T-194.1 [integration], T-194.2 [integration], T-194.3 [integration], T-194.4 [integration], T-194.5 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-195 List the dispatched T-ids whose test case changed after their test
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prdlint/buildcheck.py:284 @2caf953
Acceptance (EARS):
- AC-195.1 When `--stale --tids <T-ids>` runs and a T-id is cited by a file under the test roots in the working
  tree (trace's citation rule), and its test case in the working tree differs, as parsed YAML, from its case at
  the last commit that changed the judged citing file, the check shall print
  `stale <T-id> <path>: its test case changed after the test (last changed in <sha>)` on stdout, `<path>` the
  judged file from the repository root and `<sha>` that commit's abbreviated SHA (`git log --format=%h`), one
  line per T-id in the order of `--tids`, and exit 1. A T-id's test case is the value of its key in the first
  `*.yaml` file directly in the PRD folder's `test-cases/`, in name order, whose top-level mapping holds the
  key, read so that a repeated key keeps its first value; at a commit, the same set of files at that commit.
- AC-195.2 Where a T-id is cited by several committed files, the check shall judge the one whose last commit has
  the latest committer time; of files
  whose last commits have the same committer time, it shall judge the first in the order of the test roots,
  then of the file path.
- AC-195.3 If any file that cites the T-id has a `git status --porcelain` entry (untracked, changed or staged),
  the check shall print no line for that T-id, whatever its committed citing files show.
- AC-195.4 If a T-id is cited by no file, by no committed file, or has no test case in the working tree, or its
  case is the same at the judged file's last commit, the check shall print no line for it; with no line at all
  it prints nothing and exits 0.
- AC-195.5 When a T-id's case is absent at the judged file's last commit and present in the working tree, the
  check shall count it as changed (AC-195.1).
Errors: -
Edge cases: a case changed and committed after the test is stale, as is one changed and not committed → AC-195.1; a T-id that is no T-id gets no line → AC-195.4; a citing file that git ignores has no commit and no status entry, so it is skipped and the other citing files are judged → AC-195.4
Tests: T-195.1 [integration], T-195.2 [integration], T-195.3 [integration], T-195.4 [integration], T-195.5 [integration], T-195.6 [integration], T-195.7 [integration], T-195.8 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check; trace citations

### FR-196 Refuse --stale outside a git working tree
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prd_build_check.py:56 @2caf953
Acceptance (EARS):
- AC-196.1 If `--stale` runs on a PRD folder that lies in no git working tree, the check shall print
  `prd_build_check: <folder> is not in a git working tree` on stderr, `<folder>` the folder's resolved absolute
  path, print nothing on stdout, and exit 2, before it reads a T-id.
Errors: -
Edge cases: -
Tests: T-196.1 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-197 Stop a command that runs past 120 seconds
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prdlint/buildcheck.py:30 @2caf953
Acceptance (EARS):
- AC-197.1 If a git command or the vendor run of the check runs longer than 120 seconds, the check shall stop it,
  print `prd_build_check: <name> timed out after 120 s` on stderr, `<name>` being `git` and the command's first
  word after `git` that does not start with `-` (`git diff`), or `vendor` for the vendor run, print nothing on
  stdout, and exit 2.
Errors: -
Edge cases: the git command that finds the repository root is not the check's and has its own limit (lint-cli) → AC-197.1
Tests: T-197.1 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check

### FR-198 Stop when the report or SOURCES file cannot be read
Status: live (since 9.7.0)
Source: prd-toolkit/scripts/prd_build_check.py:69 @2caf953
Acceptance (EARS):
- AC-198.1 If the `--results` report or the `--sources` file does not exist or is not UTF-8 text, the check shall
  print one line on stderr, `prd_build_check: internal error: <exception type>: <message>`, print nothing on stdout, the `--diff` lines
  included, and exit 2.
Errors: -
Edge cases: -
Tests: T-198.1 [integration]  (test-cases/build-check.yaml)
Traces: cli:prd_build_check
