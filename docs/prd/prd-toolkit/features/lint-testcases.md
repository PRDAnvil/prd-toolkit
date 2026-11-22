<!-- Format: references/prd-format.md, "Requirement blocks". -->

# lint-testcases: the lint rules for test cases, levels and fixtures

### FR-149 Require a test case for every live acceptance criterion
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:128 @5483ca1
Acceptance (EARS):
- AC-149.1 If an acceptance criterion that is not marked `(removed in X.Y.Z)`, in a block whose status is not `removed`, is named by the `ac:` of no test case, the lint command shall report `ac-has-test` at the criterion's line in the block's file with `<AC-id> has no test case whose ac: is <AC-id>`.
- AC-149.2 When a test case in any file of `test-cases/` names an acceptance criterion in its `ac:`, the lint command shall count that criterion as having a test, whichever area's file holds the case.
- AC-149.3 When a block's status is `removed`, or an acceptance criterion is marked `(removed in X.Y.Z)`, the lint command shall report no `ac-has-test` finding for that criterion.
Errors: -
Edge cases: the blocks of `nfr.md` are checked like those of `features/*.md` → AC-149.1; a UJ block has no criteria; a case the loader reports as not a mapping names no criterion (AC-154.6) → AC-149.2; a case whose `ac:` names a removed criterion is reported by `id-removed-reused` (lint-ids) → AC-149.3
Tests: T-149.1 [integration], T-149.2 [integration], T-149.3 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-150 Tie each Tests line to its test-cases file
Status: verified
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:139 @5483ca1
Flow: 1. for each T-id on each block's Tests line: does the line name a file → does the file exist → does it hold the T-id → does its level agree
      → 2. for each test case: does some Tests line that names the case's file list its T-id
Acceptance (EARS):
- AC-150.1 If a block's `Tests:` line lists a T-id and names no `(test-cases/<file>)`, the lint command shall report `test-cases-consistent` at the Tests line with `the Tests line of <block-id> names no test-cases file; end it with (test-cases/<area>.yaml)`, once for the line whatever the number of T-ids on it, and shall count none of that line's T-ids as cited.
- AC-150.2 If the file a `Tests:` line names is not a file in the PRD folder, the lint command shall report `test-cases-consistent` at the Tests line with `<T-id>: the named file <file> does not exist`, once for each T-id the line lists.
- AC-150.3 If the named file exists and holds no entry for a T-id the line lists, the lint command shall report `test-cases-consistent` at the Tests line with `<T-id> has no entry in <file>`.
- AC-150.4 If the entry's `level:` is a string other than the level the Tests line gives that T-id in brackets, the lint command shall report `test-cases-consistent` at the Tests line with `<T-id> is [<line level>] on the Tests line but level: <case level> in <case file>:<level line>`.
- AC-150.5 If no `Tests:` line that names a test case's own file lists the case's T-id, the lint command shall report `test-cases-consistent` at the case's key line in its file with `<T-id> is cited by no Tests line naming <file>`.
- AC-150.6 When an entry's `level:` is absent or is not a string, the lint command shall report no AC-150.4 finding for it.
Errors: -
Edge cases: `<file>` is the path the line names, relative to the PRD folder (`test-cases/api.yaml`) → AC-150.2; the bracket level is read with its surrounding white space removed (lint-cli, the loader) → AC-150.4; a case the loader reports as not a mapping is still checked by AC-150.5 → AC-150.5; blocks whose status is `removed` are checked too → AC-150.1; a line with no file and several T-ids gets the finding once → AC-150.1
Tests: T-150.1 [integration], T-150.2 [integration], T-150.3 [integration], T-150.4 [integration], T-150.5 [integration], T-150.6 [integration], T-150.7 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-151 Check the Gate column of the Levels table
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:271 @5483ca1
Acceptance (EARS):
- AC-151.1 If testing.md has a table under its `## Levels` heading and that table has no Gate column, the lint command shall report `test-level` once, at the table's header line in `testing.md`, with `testing.md Levels: add a Gate column (build or deploy), new in prd-toolkit 0.4`.
- AC-151.2 If a Levels row's Gate cell, stripped and with its backticks removed, is neither `build` nor `deploy`, the lint command shall report `test-level` at the row's line in `testing.md` with `level '<level>': Gate '<gate>' is not one of build, deploy`.
- AC-151.3 While the Levels table has no Gate column, the lint command shall report neither an AC-151.2 finding nor an FR-152 finding.
- AC-151.4 While testing.md has no table under a `## Levels` heading, the lint command shall report no AC-151.1, AC-151.2 or FR-152 finding.
Errors: -
Edge cases: the loader looks for the Gate column by its header from the table's fourth column on (lint-cli) → AC-151.1; an empty Gate cell is reported as `Gate ''` → AC-151.2; FR-153 still checks each case's level when there is no Levels table, so every case is reported → AC-151.4
Tests: T-151.1 [integration], T-151.2 [integration], T-151.3 [integration], T-151.4 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-152 Report a build command that would collect deploy-gate tests
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:249 @5483ca1
  prd-toolkit/scripts/prdlint/rules/testcases.py:193 @5483ca1
Flow: 1. take each level's Harness command (the first backticked span of its cell) → 2. find its path, the paths it excludes and whether it selects tests by an expression
      → 3. for each build-gate level with a path and no selection, compare its path with each deploy-gate level's path
Acceptance (EARS):
- AC-152.1 When the Harness command of a level whose Gate is `build` has a path (AC-152.2) that is `.`, that equals the path of a level whose Gate is `deploy`, or that is a folder holding that path, and the command neither excludes that path (AC-152.3) nor selects its tests by an expression (AC-152.4), the lint command shall report `test-level` at the build level's row in `testing.md` with `level '<build level>' (Gate build) would collect level '<deploy level>' (Gate deploy) tests: <deploy path>`, once for each such deploy-gate level, in Levels table order.
- AC-152.2 The lint command shall read a command's path as the first word that, once a leading `./` and a trailing `/` are removed, is `.`, `..` or a Test roots entry (written the same way), or that holds a `/` and has no `.` in its last `/`-separated part. Words are split the way a POSIX shell splits them. The path is never the first word of a simple command (the command's start, and the word after each `&&`, `||`, `;`, `|` or `&`). It is also never a `NAME=value` word before that first word, the word after `-m` when the program's name starts with `python`, a word that starts with `-`, or the word after an option that takes a value. Those options are `--ignore`, `--ignore-glob`, `--deselect`, `--testPathIgnorePatterns`, `-m`, `-k`, `-t`, `--testNamePattern`, `-run`, `-p`, `-c`, `-o`, `-n`, `-W`, `--rootdir`, `--confcutdir`, `--basetemp`, `--junitxml`, `--junit-xml`, `--cov`, `--cov-report`, `--cov-config`, `--log-file`, `--maxfail`, `--tb`, `--durations`, `--import-mode`, `--override-ini`, `--config`, `--roots`, `--selectProjects`, `-tags` and `-timeout`.
- AC-152.3 When a build command gives `--ignore`, `--ignore-glob`, `--deselect` or `--testPathIgnorePatterns` a value, either as the next word or after `=`, and that value (written as in AC-152.2) equals a deploy-gate level's path, is a folder that holds it, or matches it as a case-sensitive shell glob, the lint command shall report no AC-152.1 finding for that pair of levels.
- AC-152.4 When a build command gives `-m`, `-k`, `-t`, `--testNamePattern` or `-run` a value, either as the next word or after `=`, the lint command shall report no AC-152.1 finding for that build level. A `-m` right after a program whose name starts with `python` does not count.
- AC-152.5 When a level has no Harness command (its cell holds no backticked span, or an empty one), or its command has no path, the lint command shall report no AC-152.1 finding that pairs it with another level.
Errors: -
Edge cases: a command whose quotes do not balance is split on white space instead → AC-152.2; a file with an extension (`tools/gate.sh`, `tests/unit/test_a.py`) is never the path, so a shared runner script is no overlap → AC-152.2, AC-152.5; excluding a file inside a deploy-gate path still overlaps → AC-152.3; `tests/systematic` does not hold `tests/system` → AC-152.1; the orders fixture's `acceptance` level (`python3 tools/acceptance_report.py`) has no path → AC-152.5; the check needs a Gate column (AC-151.3); Test roots come from the Layout slot (lint-cli, the loader)
Tests: T-152.1 [integration], T-152.2 [integration], T-152.3 [integration], T-152.4 [integration], T-152.5 [integration], T-152.6 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint; testing.md Levels

### FR-153 Name a Levels row in each test case
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:280 @5483ca1
Acceptance (EARS):
- AC-153.1 If a test case has no `level:`, or its `level:` is null or an empty string, list or mapping, the lint command shall report `test-level` at the case's key line with `<T-id> has no level`.
- AC-153.2 If a test case's `level:`, written as text, is not the first cell (backticks removed) of a row of testing.md's Levels table, the lint command shall report `test-level` at the `level:` line with `<T-id>: level '<level>' is not a row of the Levels table in testing.md`.
Errors: -
Edge cases: level names compare exactly, so `Unit` is not `unit` → AC-153.2; a level of white space only is reported by AC-153.2, and by `sufficiency` too (AC-154.2); `sufficiency` also reports a missing level (AC-154.1) → AC-153.1
Tests: T-153.1 [integration], T-153.2 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-154 Require a case's scalar elements and a known target kind
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:298 @5483ca1
Acceptance (EARS):
- AC-154.1 If a test case has no `ac:`, `level:`, `environment:` or `identity:` key, the lint command shall report `sufficiency` at the case's key line with `<T-id>: <key> is missing`, once for each missing key, in the order `ac`, `level`, `environment`, `identity`.
- AC-154.2 If a test case's `ac:`, `level:`, `environment:` or `identity:` is present but is not a string, or is a string of white space only, the lint command shall report `sufficiency` at the case's key line with `<T-id>: <key> is missing`.
- AC-154.3 If a test case has no `target:` key, the lint command shall report `sufficiency` at the case's key line with `<T-id>: target is missing`. If its `target:` is not a string, or is white space only, the lint command shall report `sufficiency` at the case's key line with the same message.
- AC-154.4 If a target holds no `:`, or holds only white space after its first `:`, the lint command shall report `sufficiency` at the `target:` line with `<T-id>: target '<target>' must be <kind>:<name>`.
- AC-154.5 If a target's kind (the text before its first `:`) is not a known kind, the lint command shall report `sufficiency` at the `target:` line with `<T-id>: target kind '<kind>' is unknown (known: <the known kinds, sorted, comma-separated>)`. The known kinds are `op`, `table`, `event`, `job`, `component`, `page` and `code`, the type of each section 7 row whose Validator cell (stripped, without backticks) is not `built-in`, and the target kinds of the packs the PRD resolves.
- AC-154.6 When the loader reports a test case's value as not a mapping (FR-011), the rules `ac-has-test`, `test-level`, `sufficiency`, `judged-case`, `test-refs`, `deny-tested` and `classified-fixtures` shall check nothing in that case.
Errors: -
Edge cases: the name of a built-in section 7 type (`openapi`) is not a kind → AC-154.5; a custom type is a kind whatever its files hold → AC-154.5; a prefixed target in a PRD with links.md is covered by AC-164.8 → AC-154.5; the kind is not stripped, so `op :x` is unknown → AC-154.5; a present but malformed `ac:`, `level:`, `environment:`, `identity:` or `target:` is called missing and reported at the case's key line, not its own; the finding still names the key → AC-154.2, AC-154.3
Tests: T-154.1 [integration], T-154.2 [integration], T-154.3 [integration], T-154.4 [integration], T-154.5 [integration], T-154.6 [integration], T-154.7 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-155 Require preconditions, input and expect in their forms
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:310 @5483ca1
Acceptance (EARS):
- AC-155.1 If a test case's `preconditions:` is absent or not a list, the lint command shall report `sufficiency` with `<T-id>: preconditions must be a list (use [] for none)`, at the `preconditions:` line, or at the case's key line when the key is absent.
- AC-155.2 If a test case's `input:` is absent, null, or an empty string, list or mapping, the lint command shall report `sufficiency` with `<T-id>: input is missing or empty`, at the `input:` line, or at the case's key line when the key is absent.
- AC-155.3 If a test case's `expect:` is absent or not a mapping, the lint command shall report `sufficiency` with `<T-id>: expect is missing`, at the `expect:` line, or at the case's key line when the key is absent. It shall then apply AC-155.4 to AC-155.6 as if `expect` were an empty mapping, and report each of their findings at that same line.
- AC-155.4 If a test case that is not judged (AC-157.1) has an `expect.output` that is absent, null, or an empty string, list or mapping, the lint command shall report `sufficiency` with `<T-id>: expect.output is missing`, at the `output:` line, or at the `expect:` line when the key is absent.
- AC-155.5 If `expect.effects` or `expect.errors` is absent or not a list, the lint command shall report `sufficiency` with `<T-id>: expect.<key> must be a list (use [] for none)`, at that key's line, or at the `expect:` line when the key is absent.
- AC-155.6 If `expect.leaks` is absent, null, or an empty string, list or mapping, the lint command shall report `sufficiency` with `<T-id>: expect.leaks is missing (use 'none')`, at the `leaks:` line, or at the `expect:` line when the key is absent.
Errors: -
Edge cases: `0` and `false` are not empty → AC-155.2, AC-155.6; any non-empty `leaks` value passes, not only `none` → AC-155.6; for one case at one line the findings come in the order expect, output, effects, errors, leaks → AC-155.3
Tests: T-155.1 [integration], T-155.2 [integration], T-155.3 [integration], T-155.4 [integration], T-155.5 [integration], T-155.6 [integration], T-155.7 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-156 Give an acceptance case its steps and sign-off
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:326 @5483ca1
Acceptance (EARS):
- AC-156.1 If a test case's `level:` is `acceptance` and its `steps:` is not a non-empty list whose every item is a string holding a character other than white space, the lint command shall report `sufficiency` with `<T-id>: an acceptance case needs steps: a non-empty list of strings`, at the `steps:` line, or at the case's key line when the key is absent.
- AC-156.2 If an acceptance case's `signoff:` is absent, not a string, or white space only, the lint command shall report `sufficiency` with `<T-id>: an acceptance case needs signoff: the business owner`, at the `signoff:` line, or at the case's key line when the key is absent.
- AC-156.3 When a test case's `level:` is not `acceptance`, the lint command shall not check its `steps:` or `signoff:`.
Errors: -
Edge cases: the level must be exactly `acceptance` → AC-156.3
Tests: T-156.1 [integration], T-156.2 [integration], T-156.3 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-157 Check a judged case's rubric, threshold, runs and output
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:347 @5483ca1
Acceptance (EARS):
- AC-157.1 When a test case's `expect:` is a mapping that holds the key `rubric`, the lint command shall treat the case as judged and shall report no AC-155.4 finding for it.
- AC-157.2 If a judged case's `rubric` is not a non-empty list whose every item is a string holding a character other than white space, the lint command shall report `judged-case` at the `rubric:` line with `<T-id>: rubric must be a non-empty list of non-empty strings`.
- AC-157.3 If an item of a well-formed rubric equals an earlier item once every run of white space in each is collapsed to one space and their ends are trimmed, the comparison `prd_judge.py` makes, the lint command shall report `judged-case` at the `rubric:` line with `<T-id>: rubric item <k> repeats item <j>`. `<k>` is the item's place and `<j>` the place of the first item it equals, both counted from 1.
- AC-157.4 If a judged case's `threshold` is absent, a boolean, not a number, or not both greater than 0 and at most 1, the lint command shall report `judged-case` with `<T-id>: threshold must be a number in (0, 1]`, at the `threshold:` line, or at the `rubric:` line when the key is absent.
- AC-157.5 If a judged case has `runs` and its value is a boolean, not an integer, or less than 1, the lint command shall report `judged-case` at the `runs:` line with `<T-id>: runs must be an integer of at least 1`.
- AC-157.6 If a judged case's `expect:` holds the key `output`, the lint command shall report `judged-case` at the `output:` line with `<T-id>: a judged case has no expect.output`.
Errors: -
Edge cases: two items that differ only in their inner white space are repeats → AC-157.3; `runs` is optional → AC-157.5; an `output:` of any value, null included, is reported → AC-157.6; `effects`, `errors` and `leaks` are still checked (FR-155) → AC-157.1
Tests: T-157.1 [integration], T-157.2 [integration], T-157.3 [integration], T-157.4 [integration], T-157.5 [integration], T-157.6 [integration], T-157.7 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-158 Warn when a judged threshold below 1.0 needs every rubric item
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:334 @5483ca1
Acceptance (EARS):
- AC-158.1 When a judged case has a well-formed rubric of `n` items, `n` at least 2, and a threshold `t` that is greater than `(n-1)/n` and less than 1.0 in floating point, the lint command shall report a `judged-case` finding of severity `warn` at the `threshold:` line. It is printed `<file>:<line>: warn: judged-case: <T-id>: threshold <t> needs all <n> items (<n-1> of <n> is <(n-1)/n>); write <d> to allow one miss, or 1.0`. `<d>` is `(n-1)/n` rounded down to two decimal places, and `<t>`, `<(n-1)/n>` and `<d>` are each written with at most four significant digits (Python's `.4g`).
- AC-158.2 When the threshold is at most `(n-1)/n` in floating point, or is 1.0, the lint command shall report no AC-158.1 `warn` finding.
Errors: -
Edge cases: a `warn` finding alone leaves the lint exit code at 0 (lint-cli FR-001) → AC-158.1; a one-item rubric, a malformed rubric and a malformed threshold get no `warn` finding → AC-158.2; `4/5` is `0.8` in floating point, so five items at 0.8 get no `warn` finding → AC-158.2
Tests: T-158.1 [integration], T-158.2 [integration], T-158.3 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-159 Point each case's ac at its own requirement
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:402 @5483ca1
Acceptance (EARS):
- AC-159.1 If a test case's `ac:` is a non-empty string that is not the ID of an acceptance criterion in any block, removed ones included, the lint command shall report `test-refs` at the `ac:` line with `<T-id>: <ac> is not an acceptance criterion in any requirement block`.
- AC-159.2 If a test case's `ac:` is `AC-<a>.<x>` and its T-id is `T-<b>.<y>`, and the digits `<a>` and `<b>` differ as written, the lint command shall report `test-refs` at the `ac:` line with `<T-id>: <ac> belongs to requirement <a>, but <T-id> is numbered for requirement <b>`.
Errors: -
Edge cases: both findings can come from one case → AC-159.1, AC-159.2; a removed criterion's ID passes here and `id-removed-reused` reports it (lint-ids) → AC-159.1
Tests: T-159.1 [integration], T-159.2 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-160 Resolve each case's preconditions and input file
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:410 @5483ca1
Acceptance (EARS):
- AC-160.1 If an item of a test case's `preconditions:` list is not a string, the lint command shall report `test-refs` at the `preconditions:` line with `<T-id>: precondition <item> must be a fixture name or mock:<service>`, writing `<item>` the way Python's `repr` writes it.
- AC-160.2 If a precondition `mock:<service>` has no file `contracts/dependencies/<service>.yaml` in the PRD folder, the lint command shall report `test-refs` at the `preconditions:` line with `<T-id>: mock:<service> has no contracts/dependencies/<service>.yaml`.
- AC-160.3 If any other precondition is not the first cell of a row of testing.md's Fixtures table, the lint command shall report `test-refs` at the `preconditions:` line with `<T-id>: fixture '<name>' is not in the Fixtures table of testing.md`.
- AC-160.4 If such a precondition `<name>` is not a folder `contracts/fixtures/<name>`, and the folder that would hold it has no file whose name, without its last extension, is the last part of `<name>`, the lint command shall report `test-refs` at the `preconditions:` line with `<T-id>: fixture '<name>' has no file or directory at contracts/fixtures/<name>`.
- AC-160.5 If a test case's `input:` is a mapping whose `file` is a string, and `contracts/fixtures/<file>` is not a file, the lint command shall report `test-refs` at the `input:` line with `<T-id>: input.file '<file>' does not exist under contracts/fixtures/`.
Errors: -
Edge cases: AC-160.3 and AC-160.4 are checked separately, so a name found in neither place gets both findings, in that order → AC-160.3, AC-160.4; `orders/one_existing` resolves to `orders/one_existing.csv` → AC-160.4
Tests: T-160.1 [integration], T-160.2 [integration], T-160.3 [integration], T-160.4 [integration], T-160.5 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-161 Resolve each case's error codes, environment and identity
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:427 @5483ca1
Acceptance (EARS):
- AC-161.1 While contracts/errors.yaml loads as a mapping and a test case's `expect.errors` is a list, the lint command shall report `test-refs` at the `expect:` line, once per item and in the list's order. A non-string item gets `<T-id>: expect.errors item <item> must be an error code string`, with `<item>` written the way Python's `repr` writes it. A string that is not a top-level key of errors.yaml gets `<T-id>: error code <code> is not in contracts/errors.yaml`.
- AC-161.2 If a test case's `environment:` is a non-empty string that is not the first cell of a row of testing.md's Environments table, the lint command shall report `test-refs` at the `environment:` line with `<T-id>: environment '<env>' is not in the Environments table of testing.md`.
- AC-161.3 If a test case's `identity:` is a non-empty string that is neither `none` nor the `identity` string of a role under `roles` in contracts/permissions.yaml, the lint command shall report `test-refs` at the `identity:` line with `<T-id>: identity '<identity>' is neither none nor a test identity in contracts/permissions.yaml`.
Errors: -
Edge cases: without an errors.yaml that loads, no code is checked → AC-161.1; without permissions.yaml only `none` resolves → AC-161.3
Tests: T-161.1 [integration], T-161.2 [integration], T-161.3 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-162 Resolve each case's refs entries
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:435 @5483ca1
  prd-toolkit/scripts/prdlint/rules/testcases.py:25 @5483ca1
Acceptance (EARS):
- AC-162.1 Where a test case has `refs:`, the lint command shall check each item when the value is a list, and the value itself when it is not.
- AC-162.2 If a refs entry is not a string, or is a string of white space only, the lint command shall report `test-refs` at the `refs:` line with `<T-id>: refs entry <entry> must be a path in the PRD folder, optionally with #heading`, writing `<entry>` the way Python's `repr` writes it.
- AC-162.3 If the part of a refs entry before its first `#` does not name a file inside the PRD folder once `..` and symbolic links are resolved, the lint command shall report `test-refs` at the `refs:` line with `<T-id>: refs entry '<entry>': no file <path> in the PRD folder`.
- AC-162.4 If the text after a refs entry's first `#` is not empty and equals no heading's text as written, code spans included and trailing white space removed, a heading line being one to six `#` and white space at a line's start outside fenced code blocks, the lint command shall report `test-refs` at the `refs:` line with `<T-id>: refs entry '<entry>': <path> has no heading '<heading>'`.
- AC-162.5 When the text after a refs entry's first `#` equals a heading's text as written at any heading level, or is empty, the lint command shall report no AC-162.4 finding.
Errors: -
Edge cases: a heading's code spans are part of its text, so an entry names such a heading with its backticks, and the heading's text without them names nothing → AC-162.4, AC-162.5; a `#` line inside a fenced code block is not a heading → AC-162.4; an entry ending in `#` is checked for its file only → AC-162.5
Tests: T-162.1 [integration], T-162.2 [integration], T-162.3 [integration], T-162.4 [integration], T-162.5 [integration], T-162.6 [integration], T-162.7 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-163 Tie a known-failing case to an open entry and its symptom
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:449 @5483ca1
Acceptance (EARS):
- AC-163.1 If a test case's `known-failing:` is present and not null, and is not a string that names a `### E-nnn` entry of errors.md, the lint command shall report `test-refs` at the `known-failing:` line with `<T-id>: known-failing <value> must be an E-nnn entry of errors.md`, writing `<value>` the way Python's `repr` writes it.
- AC-163.2 If a test case's `known-failing:` names an errors.md entry that is resolved, the lint command shall report `test-refs` at the `known-failing:` line with `<T-id>: known-failing <E-id> is resolved in errors.md; remove the line`.
- AC-163.3 If a test case has a `symptom:` key and its `known-failing:` is absent or null, the lint command shall report `test-refs` at the `symptom:` line with `<T-id>: symptom: needs known-failing: on the same case`, whatever the symptom's value.
- AC-163.4 If a test case's `known-failing:` is present and not null, and its `symptom:` is absent, not a string, or white space only, the lint command shall report a `test-refs` finding of severity `warn` at the `known-failing:` line, printed `<file>:<line>: warn: test-refs: <T-id>: known-failing <value> names no symptom; any failure would pass as it`.
- AC-163.5 When a test case's `known-failing:` names an open errors.md entry and its `symptom:` is a string holding a character other than white space, the lint command shall report no `test-refs` finding on either key.
Errors: -
Edge cases: errors.md's own rule decides whether an entry is open or resolved (prd-format.md, "errors.md") → AC-163.2; AC-163.4's `warn` finding comes alongside AC-163.1's or AC-163.2's error when both apply → AC-163.4; in AC-163.4 `<value>` is written as plain text (`E-001`), not as `repr` → AC-163.4
Tests: T-163.1 [integration], T-163.2 [integration], T-163.3 [integration], T-163.4 [integration], T-163.5 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-164 Resolve each case's target in the contracts
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:466 @5483ca1
Acceptance (EARS):
- AC-164.1 If a target `op:<name>` names no operationId of contracts/openapi.yaml, the lint command shall report `test-refs` at the `target:` line with `<T-id>: target op:<name>: no operationId '<name>' in contracts/openapi.yaml`.
- AC-164.2 If a target `table:<name>` names no table of contracts/schema.sql (compared without regard to case), the lint command shall report `test-refs` at the `target:` line with `<T-id>: target table:<name>: no table '<name>' in contracts/schema.sql`.
- AC-164.3 If a target `event:<name>` or `job:<name>` names neither a `### <name>` heading of contracts/events.md nor an asyncapi channel or operation, the lint command shall report `test-refs` at the `target:` line with `<T-id>: target <kind>:<name>: no '### <name>' heading in contracts/events.md and no such asyncapi channel or operation`.
- AC-164.4 Where a target's kind is a target kind of a pack the PRD resolves, if the contract type the pack maps it to is not the type of a section 7 row whose Validator is not `built-in`, the lint command shall report `test-refs` at the `target:` line with `<T-id>: target <target>: contract type <type> has no §7 row (Validator pack)`.
- AC-164.5 Where that contract type has such a row and one of its files under contracts/ loads as a YAML mapping, if the target's name is not a top-level key of those mappings, the lint command shall report `test-refs` at the `target:` line with `<T-id>: target <target>: no <type> entry '<name>'`.
- AC-164.6 Where a target's kind is the type of a section 7 row whose Validator is not `built-in`, and a file its glob matches loads as a YAML mapping, if the name is not a top-level key of those mappings, the lint command shall report `test-refs` at the `target:` line with `<T-id>: target <target>: '<name>' is not an item of the <kind> files (items: <the keys, sorted, comma-separated>)`.
- AC-164.7 When a target's kind is `component`, `page` or `code`, or is a section 7 type none of whose files loads as a YAML mapping, the lint command shall not check the target's name.
- AC-164.8 Where the PRD folder has links.md, neither `sufficiency` nor `test-refs` shall check a target `<kind>:<a>/<name>` whose kind is not `code` and whose `<a>` matches `[a-z][a-z0-9-]*`. Without links.md, the lint command shall check such a target like any other.
Errors: -
Edge cases: `upstream-refs` judges a prefixed target (links, not adopted) → AC-164.8; asyncapi channel names, their addresses and operation IDs also resolve `event:` and `job:` targets → AC-164.3; only `.yaml` files load as YAML (lint-cli FR-012) → AC-164.6
Tests: T-164.1 [integration], T-164.2 [integration], T-164.3 [integration], T-164.4 [integration], T-164.5 [integration], T-164.6 [integration], T-164.7 [integration], T-164.8 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-165 Prove every denial with a test case
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:484 @5483ca1
Acceptance (EARS):
- AC-165.1 If a role in an operation's `deny:` list in contracts/permissions.yaml has no entry under `roles` with a non-empty `identity`, the lint command shall report `deny-tested` in `contracts/permissions.yaml`, at the `deny:` key's line, with `deny cell (<operation>, <role>): role '<role>' has no test identity`.
- AC-165.2 If a role in a `deny:` list has an identity and no test case has the target `op:<operation>`, that identity and a non-empty `expect.errors`, the lint command shall report `deny-tested` at the `deny:` key's line with `deny cell (<operation>, <role>) has no test case with target op:<operation>, identity <identity> and expect.errors`.
- AC-165.3 When contracts/permissions.yaml is absent or not a mapping, an operation's entry is not a mapping, its `deny` is not a list, or a role in it is not a string, the lint command shall report no `deny-tested` finding for it.
Errors: -
Edge cases: the codes in `expect.errors` are not compared with the operation's codes → AC-165.2; `contracts-valid` reports the shapes AC-165.3 skips (lint-contracts) → AC-165.3
Tests: T-165.1 [integration], T-165.2 [integration], T-165.3 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-166 Keep real-looking personal data out of classified fixture columns
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:540 @5483ca1
Acceptance (EARS):
- AC-166.1 If a `.csv` file anywhere under contracts/fixtures/ has a column whose header names a column that contracts/data-classification.yaml classifies `pii` for that table, and a value in it holds a real-looking email, phone number or SSN (FR-168), the lint command shall report `classified-fixtures` in that file with `<table>.<column> is classified pii but holds the real-looking value '<value>'`. It reports once per value, at the line where the value's record ends. The file's table is the name of the folder that holds it, at any depth, or for a file directly in contracts/fixtures/, the file's name without its extension.
- AC-166.2 If, in a `.yaml`, `.yml` or `.json` file under contracts/fixtures/ that parses to a mapping of table names to lists of row mappings, a row's value under a column the classification marks `pii` for that table holds a real-looking value, in a scalar or in any string nested in a list or mapping, the lint command shall report `classified-fixtures` in that file with `<table>.<column> is classified pii but holds the real-looking value '<value>'`, at the line where the value first appears in the file's text.
- AC-166.3 The lint command shall report no `classified-fixtures` finding for a value in a column that is not classified `pii`, for a `.yaml`, `.yml` or `.json` fixture file that does not parse, or for a fixture file with any extension other than `.csv`, `.yaml`, `.yml` and `.json`.
Errors: -
Edge cases: header names are compared exactly → AC-166.1; a value's line is found by searching the file's text, so the same value earlier in the file gives that earlier line → AC-166.2; a CSV's table is always its folder's name, never taken from the file's name, so `contracts/fixtures/seed/customers.csv` is table `seed` → AC-166.1; only structured files map a value to a classified column, so a `.txt`, `.sql` or `.md` fixture is not read → AC-166.3
Tests: T-166.1 [integration], T-166.2 [integration], T-166.3 [integration], T-166.4 [integration], T-166.5 [integration], T-166.6 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-167 Keep real-looking personal data out of inline test input
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:574 @5483ca1
Acceptance (EARS):
- AC-167.1 If a string anywhere in a test case's `input:`, at any depth of lists and mappings, holds a real-looking email, phone number or SSN (FR-168), the lint command shall report `classified-fixtures` at the `input:` line with `<T-id>: inline input holds the real-looking PII value '<value>'; use a synthetic form`. It reports once per value, whatever contracts/data-classification.yaml classifies.
- AC-167.2 The lint command shall not look for personal data in a mapping key of `input:`, or in a value that is not a string.
Errors: -
Edge cases: `expect:` and the other keys of a case are not scanned → AC-167.1
Tests: T-167.1 [integration], T-167.2 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-168 Tell real-looking personal data from synthetic
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:52 @5483ca1
  prd-toolkit/scripts/prdlint/rules/testcases.py:62 @5483ca1
Acceptance (EARS):
- AC-168.1 The lint command shall search a text first for emails (`[\w.+-]+@[\w-]+(\.[\w-]+)+`), then for SSNs (`\d{3}-\d{2}-\d{4}`), then for phone numbers (`\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}`), and shall report the values in that order. An SSN or a phone number counts only when no digit stands directly before or after it. Each later pattern skips the text an earlier pattern matched.
- AC-168.2 The lint command shall count an email as synthetic, and report none, when its domain (the text after its last `@`), in lower case, is `example.com`, `example.org` or `example.net`, ends with `.example.com`, `.example.org` or `.example.net`, or ends with `.test`, `.example` or `.invalid`.
- AC-168.3 The lint command shall count an SSN as synthetic, and report none, when its first three digits are `000` or `666` or start with `9`.
- AC-168.4 The lint command shall count a phone number as synthetic, and report none, when its fourth to sixth digits are `555` and its seventh and eighth digits are `01`.
Errors: -
Edge cases: a UUID or a long order number holds no value → AC-168.1; the digits of a matched email are not read again as a phone number → AC-168.1; an address at a subdomain of a reserved domain is synthetic; `notexample.com` is no subdomain → AC-168.2
Tests: T-168.1 [integration], T-168.2 [integration], T-168.3 [integration], T-168.4 [integration], T-168.5 [integration], T-168.6 [integration], T-168.7 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_lint

### FR-169 Describe each rule of the area
Status: live (since 9.5.0)
Source: prd-toolkit/scripts/prdlint/rules/testcases.py:127 @5483ca1
Acceptance (EARS):
- AC-169.1 The help command, run as `prd_help.py --rule <name>`, shall print `<name> (error)` as its first stdout line for each of `ac-has-test`, `test-cases-consistent`, `test-level`, `sufficiency`, `judged-case`, `test-refs`, `deny-tested` and `classified-fixtures`.
- AC-169.2 The help command, run as `prd_help.py --rule ac-has-test`, shall print as its second stdout line `Checks that every live acceptance criterion of a requirement that is not removed has at least one test case whose ac: names it. Add a case to the area's test-cases file with ac: set to that AC.`
- AC-169.3 The help command, run as `prd_help.py --rule test-cases-consistent`, shall print as its second stdout line `Checks that each block's Tests line names its test-cases file, that the file exists and holds an entry for every T-id listed, at the level the line gives, and that every test case is cited by a Tests line naming its file. End the Tests line with (test-cases/<area>.yaml) for a file that exists, add the missing entry or Tests item, or make the level on the line and in the case agree.`
- AC-169.4 The help command, run as `prd_help.py --rule test-level`, shall print as its second stdout line `Checks that testing.md's Levels table has a Gate column whose values are build or deploy, that no build-gate Harness command would collect a deploy-gate level's tests, and that each test case's level: is a row of that table. Add the level or the Gate value, or exclude the deploy-gate path from the build command with --ignore.`
- AC-169.5 The help command, run as `prd_help.py --rule sufficiency`, shall print as its second stdout line `Checks that each test-cases file parses as YAML mapping each T-id to a mapping, and that each case has the eight sufficiency elements: ac, level, environment and identity as strings, target as <kind>:<name> of a known kind, preconditions as a list, a non-empty input, and expect with output (unless judged), effects and errors lists and leaks; an acceptance case also needs steps: and signoff:. Fix the YAML, or fill the element the message names in its form, with a target kind that is built in, a pack's, or a section 7 custom type. An entry named .md or .yaml in the PRD folder that is not a file is reported here too; rename or remove it.`
- AC-169.6 The help command, run as `prd_help.py --rule judged-case`, shall print as its second stdout line `Checks a judged case's expect: rubric a non-empty list of distinct non-empty strings, threshold a number in (0, 1], runs an integer of at least 1, and no output beside rubric; it warns when a threshold below 1.0 still needs every rubric item. Fix the key the message names, or lower the threshold to allow one miss.`
- AC-169.7 The help command, run as `prd_help.py --rule test-refs`, shall print as its second stdout line `Checks that each test case's references resolve: ac names an AC of the requirement its T-id is numbered for, preconditions name fixtures in testing.md and contracts/fixtures/ or mock services in contracts/dependencies/, input.file, error codes, refs entries, environment, identity and target exist, known-failing names an open errors.md entry and has a symptom: beside it (a warning when it has none), and a symptom: has a known-failing: beside it. Point the reference at something that exists or add what it names; delete a known-failing: line whose entry is resolved, and a symptom: with no known-failing: beside it.`
- AC-169.8 The help command, run as `prd_help.py --rule deny-tested`, shall print as its second stdout line `Checks that every deny cell of contracts/permissions.yaml has a role with a test identity and a test case with target op:<operation>, that identity and a non-empty expect.errors. Give the role an identity, or add the case that proves the denial.`
- AC-169.9 The help command, run as `prd_help.py --rule classified-fixtures`, shall print as its second stdout line `Checks that no fixture file under contracts/fixtures/ holds a real-looking email, phone number or SSN in a column contracts/data-classification.yaml classifies pii, and that no test case's inline input holds one in any value. Use a synthetic form: an example.com address, a 555-01xx phone number, or an SSN starting 000, 666 or 9.`
Errors: -
Edge cases: `judged-case` and `test-refs` are `error` rules, although they also report `warn` findings (AC-158.1, AC-163.4) → AC-169.1; how help prints a rule is FR-034's (help)
Tests: T-169.1 [integration], T-169.2 [integration], T-169.3 [integration], T-169.4 [integration], T-169.5 [integration], T-169.6 [integration], T-169.7 [integration], T-169.8 [integration], T-169.9 [integration]  (test-cases/lint-testcases.yaml)
Traces: UJ-01; cli:prd_help; cli:prd_lint
