<!-- Format: references/prd-format.md, "Requirement blocks". -->

# trace: the trace report, the commit rule and the git hooks

Trace asks whether the tests keep up with the PRD. `prd_trace.py <prd_dir>` reads the citations under the test
roots and reports a test that cites a T-id no live requirement owns (FR-082), a T-id that no test cites (FR-084),
a status that claims a test nothing cites (FR-085), and a known-failing case and its tag that disagree (FR-086);
with `--range` it also checks each commit of a range against the commit rule (FR-090). `prd_git_hook.py` applies
the commit rule to the commit being made, as git's commit-msg hook (FR-093), and runs the enforced section 5
linters as its pre-commit hook (FR-094); the two files under `prd-toolkit/templates/hooks/` are the shims git
runs (FR-096). The area is adopted as it was built. Its files are `prd-toolkit/scripts/prd_trace.py`,
`prd-toolkit/scripts/prdlint/trace.py`, `prd-toolkit/scripts/prd_git_hook.py`,
`prd-toolkit/scripts/prdlint/githook.py` and `prd-toolkit/templates/hooks/**`. Which staged files a linter is
given, and the line a failing linter prints, are FR-068's (area `standards-run`). What `prd hooks install` writes
from the two templates is area `hooks-install`, which is not adopted, and FR-070's (area `hook-shims`).

Words used below. A **citation** of a T-id is the text AC-083.4 defines, in a file under a test root (FR-083).
The **commit rule** is what FR-091 says of a commit message's `Refs:` lines and FR-092 of its `Change-set:`
lines. The **Boundary** is the set of repository paths whose commits the commit rule's `Refs:` part covers
(AC-090.2, AC-090.3).

### FR-082 Report a test that cites a T-id no live requirement owns
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:285 @a87f336
Acceptance (EARS):
- AC-082.1 When a file under a test root holds a citation of a T-id that no requirement block's `Tests:` line lists, the trace command shall report the finding `test-cites-live` at that file and line with the message `cites <T-id>, which does not exist in the PRD`, once per citing line.
- AC-082.2 When a file under a test root holds a citation of a T-id that the `Tests:` line of a `removed` block lists, the trace command shall report `test-cites-live` at that file and line with the message `cites <T-id>, which belongs to removed requirement <ID>`.
Errors: -
Edge cases: a T-id that a test case in `test-cases/` defines but no `Tests:` line lists counts as absent → AC-082.1; the finding's file is the test file, printed by FR-087 → AC-082.1
Tests: T-082.1 [integration], T-082.2 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace

### FR-083 Read citations under the test roots
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:37 @a87f336
Flow: 1. take the Test roots of testing.md's Layout slot, or `tests` when it names none → 2. resolve each against the repository root
      → 3. read every file under each root, line by line → 4. collect each `@prd T-nnn.n` match as a citation
Acceptance (EARS):
- AC-083.1 The trace command shall read citations from each path that the `Test roots:` list of testing.md names, resolved against the repository root (`git rev-parse --show-toplevel` from the PRD folder), and from no other path.
- AC-083.2 If testing.md's Layout slot holds no `Test roots:` text, or a `Test roots:` text that lists no backticked path, the trace command shall read citations from `tests` under the repository root.
- AC-083.3 If the PRD folder lies in no git checkout, the trace command shall resolve the test roots against the PRD folder.
- AC-083.4 The trace command shall count as a citation of a T-id only the text `@prd`, one or more white-space characters and the T-id, `T-` with three digits, a dot and one or more digits, ending at a word boundary, all on one line.
- AC-083.5 The trace command shall read no citation from a file whose path below its test root has a part, a folder's name or the file's own, that starts with `.prd-dry-run-`, from a file whose path has a part named `__pycache__` or `.git`, or from a file that cannot be read as UTF-8 text.
Errors: -
Edge cases: `@prd T-001.10` cites T-001.10 and not T-001.1 → AC-083.4; `@prd` on one line and the T-id on the next cites nothing → AC-083.4; two roots that overlap read each file once → AC-083.1
Tests: T-083.1 [integration], T-083.2 [integration], T-083.3 [integration], T-083.4 [integration], T-083.5 [integration], T-083.6 [integration], T-083.7 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace; testing.md Layout slot `Test roots:`

### FR-084 Report a T-id that no test cites
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:292 @a87f336
Acceptance (EARS):
- AC-084.1 When a block whose status is `built`, `verified` or `as-built` lists in its `Tests:` line a T-id of level `unit`, of a level whose Gate in testing.md Levels is `build`, or of a level with no Gate (no Levels row, no Gate column or a blank cell), and no test cites it, the trace command shall report `t-implemented` at the block's features file and the line of that `Tests:` entry with the message ``<T-id> (<ID>) is cited by no test; add `@prd <T-id>` to the test that proves it``.
- AC-084.2 When a `live` block lists a T-id of any level that no test cites, the trace command shall report AC-084.1's `t-implemented` finding.
- AC-084.3 The trace command shall report no `t-implemented` finding for a block whose status is `approved` or `removed`.
- AC-084.4 If a `built`, `verified` or `as-built` block's uncited T-id has a level whose Gate is `deploy`, the trace command shall report no `t-implemented` finding for it.
- AC-084.5 Where the PRD folder holds `adoption.md`, the trace command shall report `t-implemented` only for blocks of an area whose adoption row is `adopted`, the area being the features file's name without `.md`, or `nfr` for `nfr.md`.
Errors: -
Edge cases: without `adoption.md` every area, `nfr` included, is covered → AC-084.1; an `adoption.md` with no table covers no area → AC-084.5
Tests: T-084.1 [integration], T-084.2 [integration], T-084.3 [integration], T-084.4 [integration], T-084.5 [integration], T-084.6 [integration], T-084.7 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace; testing.md Levels Gate column

### FR-085 Report a status that claims a test nothing cites
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:303 @a87f336
Acceptance (EARS):
- AC-085.1 When the trace command reports a `t-implemented` finding for a T-id of a `verified` or `live` block, it shall also report `status-current` at the same file and line with the message `<ID> is <status> but <T-id> has no citing test`.
- AC-085.2 When the trace command reports a `t-implemented` finding for a `unit` T-id of a `built` block, it shall also report AC-085.1's `status-current` finding.
- AC-085.3 If the trace command reports a `t-implemented` finding for a T-id of a `built` block whose level is not `unit`, it shall report no `status-current` finding for that T-id.
- AC-085.4 The trace command shall report no `status-current` finding for an `as-built` block.
Errors: -
Edge cases: status-current is reported only beside a t-implemented finding, so it follows FR-084's scope and gate rules → AC-085.1
Tests: T-085.1 [integration], T-085.2 [integration], T-085.3 [integration], T-085.4 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace; FR-084

### FR-086 Report known-failing cases and tags that disagree
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:306 @a87f336
Acceptance (EARS):
- AC-086.1 When a test case holds `known-failing: <E-id>` and no file under a test root holds, on one line, `@prd`, white space, its T-id, white space, `known-failing`, an optional `:`, white space and that E-id, the trace command shall report `known-failing-tags` at the test-case file and the line of the case's key with the message ``<T-id> is known-failing on <E-id> but no citation is tagged `known-failing <E-id>` ``.
- AC-086.2 When a file under a test root tags a T-id `known-failing <E-id>` and that T-id's test case exists and is not `known-failing` on that E-id, the trace command shall report `known-failing-tags` at that file and line with the message `tags <T-id> known-failing <E-id>, but its test case is not known-failing on <E-id>`.
- AC-086.3 When a file under a test root tags a T-id `known-failing <E-id>` and errors.md holds that entry resolved, the trace command shall report `known-failing-tags` at that file and line with the message `tags <T-id> known-failing <E-id>, which is resolved`.
- AC-086.4 If a file under a test root tags a T-id `known-failing <E-id>` and errors.md holds no entry of that E-id, the trace command shall report no `known-failing-tags` finding for the missing entry; AC-086.2 still applies to that tag.
Errors: -
Edge cases: a tagged citation also counts as a plain citation for FR-084 → AC-086.1; the rule covers every test case, in an adopted area or not → AC-086.1; an unknown entry on a test case's own `known-failing:` line is the lint rule `test-refs`'s finding, not trace's → AC-086.4
Tests: T-086.1 [integration], T-086.2 [integration], T-086.3 [integration], T-086.4 [integration], T-086.5 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace

### FR-087 Print the trace findings and exit by them
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prd_trace.py:84 @a87f336
Acceptance (EARS):
- AC-087.1 When prd_trace.py is run without `--json` on a PRD folder and no rule reports a finding, the trace command shall print nothing and exit 0.
- AC-087.2 When prd_trace.py is run without `--json` and a rule reports a finding, the trace command shall print each finding on its own stdout line as `<path>:<line>: <rule>: <message>`, where `<path>` is the finding's file relative to the PRD folder joined to the folder's path relative to the working directory and normalised, sorted by the file relative to the PRD folder, then line, rule and message, and shall exit 1.
- AC-087.3 When the working directory is the PRD folder, the trace command shall print each finding's file as it is relative to the PRD folder.
- AC-087.4 If the PRD folder is not under the working directory, the trace command shall print `<path>` with the folder's resolved absolute path as the prefix.
Errors: -
Edge cases: a test file's path relative to the folder starts `../`, so it sorts before every file inside the folder → AC-087.2
Tests: T-087.1 [integration], T-087.2 [integration], T-087.3 [integration], T-087.4 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace

### FR-088 Print the trace result as a JSON document
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prd_trace.py:75 @a87f336
Acceptance (EARS):
- AC-088.1 When prd_trace.py is run with `--json` or `--json=1` on a PRD folder, the trace command shall print on stdout one JSON object on one line, ending in a newline, with the keys in the order `interface` (1), `kind` (`trace`), `prd` and `version` (the frontmatter values, `null` when absent), `dir` (AC-087.2's prefix), `errors` (the number of findings), `warnings` (0) and `findings` (a list of `{"file": <path relative to the PRD folder>, "line", "rule", "severity": "error", "message"}` in AC-087.2's order), and shall exit 1 when there is a finding, else 0.
- AC-088.2 If the trace command, run with `--json`, exits 2, it shall print on stdout one line `{"interface": 1, "kind": "trace", "error": <message>}`, `<message>` being its first stderr line without the `prd_trace: ` prefix, and shall print its stderr lines as without `--json`.
- AC-088.3 If the command line holds `--json=<N>` with `<N>` other than `1` and no `--interface`, the trace command shall print the stderr line `prd_trace: unsupported interface <N>; this toolkit speaks 1`, print AC-088.2's object with the message `unsupported interface <N>; this toolkit speaks 1`, and exit 2 without reading the folder.
- AC-088.4 When run with `--interface`, the trace command shall print `1` on one stdout line and exit 0 without reading the folder.
Errors: -
Edge cases: the key order differs from lint's document (FR-014: `findings` before `errors`) → AC-088.1
Tests: T-088.1 [integration], T-088.2 [integration], T-088.3 [integration], T-088.4 [integration], T-088.5 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace; `prdlint/interface.py`

### FR-089 Refuse a trace it cannot run
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prd_trace.py:51 @a87f336
Acceptance (EARS):
- AC-089.1 If prd_trace.py is run with no folder argument and neither `--interface` nor `-h`, the trace command shall print its usage line, starting `usage: prd_trace.py`, on stderr and exit 2.
- AC-089.2 If the folder holds no file named `prd.md`, the trace command shall print `prd_trace: <resolved folder>: no prd.md` on stderr and exit 2.
- AC-089.3 If `prd.md` section 8 holds a table and the folder holds no `adoption.md`, the trace command shall print `prd_trace: <resolved folder>/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."` on stderr and exit 2.
- AC-089.4 If `git log` refuses the `--range` value, the trace command shall print one stderr line `prd_trace: bad --range <value>: <git's first stderr line>` and exit 2.
Errors: -
Edge cases: an empty `--range ""` checks no commit and is not refused; an exception while loading or tracing prints `prd_trace: internal error: <type>: <message>` and exits 2 (no test: no black-box input triggers it)
Tests: T-089.1 [integration], T-089.2 [integration], T-089.3 [integration], T-089.4 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace

### FR-090 Check each commit of a range against the commit rule
Status: verified
Source: prd-toolkit/scripts/prdlint/trace.py:323 @a87f336
Flow: 1. `git log <range>` with each commit's message and changed paths → 2. per commit, the Boundary as that commit's own tree's adoption map stood
      → 3. a commit touching the Boundary: its `Refs:` problems (FR-091) → 4. every commit: its `Change-set:` problems (FR-092)
Acceptance (EARS):
- AC-090.1 When prd_trace.py is run with `--range <range>` and a commit of the range changes a path inside the Boundary and its message has a `Refs:` problem (FR-091), the trace command shall report `commit-refs` at `prd.md` line 1 with the message `commit <sha8> touches <path> inside the Boundary: <problem>`, `<sha8>` the commit's first eight hex digits and `<path>` the first such path in git's list, one finding per problem.
- AC-090.2 Where the PRD folder holds no `adoption.md`, the trace command shall take as the Boundary every repository path except the PRD folder, the path `.prd-toolkit` and every path under `.prd-toolkit/`.
- AC-090.3 Where `adoption.md` has been committed, the trace command shall judge a commit by the `adopted` rows' Boundary globs of the `adoption.md` in that commit's own tree, and shall judge no commit whose tree holds no `adoption.md` or no `adopted` row with a glob.
- AC-090.4 Where `adoption.md` exists in the working tree and no commit reachable from HEAD has touched it, the trace command shall judge every commit by the working tree's `adoption.md`.
- AC-090.5 If no `--range` is given, the trace command shall report no `commit-refs` finding.
- AC-090.6 When a commit of the range has a `Change-set:` problem (FR-092), the trace command shall report `commit-refs` at `prd.md` line 1 with the message `commit <sha8>: <problem>`, whether or not the commit touches the Boundary.
- AC-090.7 Where the repository's object format is SHA-256, the trace command shall check every commit of the range as AC-090.1 to AC-090.6 say, `<sha8>` being the first eight hex digits of the commit's 64-digit name.
Errors: -
Edge cases: a Boundary glob takes `**/` as zero or more folders, `**` as any characters, `*` as any characters but `/` and `?` as one character but `/`, matched against the whole path → AC-090.3; trace does not apply the hook's unconfirmed-entry rule (FR-093 AC-093.5) to range commits → AC-090.1; a commit's `Refs:` IDs are judged against the PRD folder as it stands on disk, whatever the PRD held when the commit was made → AC-090.1; git lists no path for a merge commit, so no merge commit's `Refs:` lines are judged, while its `Change-set:` lines are → AC-090.6
Tests: T-090.1 [integration], T-090.2 [integration], T-090.3 [integration], T-090.4 [integration], T-090.5 [integration], T-090.6 [integration], T-090.7 [integration], T-090.8 [integration], T-090.9 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_trace; FR-091; FR-092; adoption.md

### FR-091 Judge a commit message's Refs: trailers
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:150 @a87f336
Acceptance (EARS):
- AC-091.1 If a commit message holds no line that starts with `Refs:` and has a value after it, white space removed, the commit rule shall give the one problem ``no `Refs:` trailer (`Refs: FR-001`, or `Refs: none (no behaviour change)`)``.
- AC-091.2 When a `Refs:` line's value, white space trimmed, is exactly `none (no behaviour change)`, the commit rule shall give no problem for that line.
- AC-091.3 If an item of a `Refs:` value is `none`, the commit rule shall give the problem ``none` alone is not accepted; write `Refs: none (no behaviour change)` `` (the text `` `none` alone is not accepted; write `Refs: none (no behaviour change)` ``).
- AC-091.4 If an item is `UJ-`, `FR-` or `NFR-` followed by digits and no block defines it, the commit rule shall give `<ID> is not defined in the PRD`; if its block is `removed`, `<ID> is removed`.
- AC-091.5 If an item is `E-` followed by digits and errors.md holds no such entry, the commit rule shall give `<ID> is not defined in the PRD`.
- AC-091.6 If an item is none of AC-091.3 to AC-091.5's forms, the commit rule shall give ``` `<item>` is not a PRD ID; give other keys their own trailer ```.
- AC-091.7 The commit rule shall read every `Refs:` line of the message (case-sensitive, at the start of a line), split each value on commas, trim each item and skip an empty one, and give one problem per failing item, in message order.
Errors: -
Edge cases: `refs: FR-001` is not a trailer → AC-091.1; a `Refs:` line with nothing after it is skipped → AC-091.1
Tests: T-091.1 [integration], T-091.2 [integration], T-091.3 [integration], T-091.4 [integration], T-091.5 [integration], T-091.6 [integration], T-091.7 [integration], T-091.8 [integration], T-091.9 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_git_hook; cli:prd_trace

### FR-092 Judge a commit message's Change-set: trailers
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/trace.py:196 @a87f336
Acceptance (EARS):
- AC-092.1 If a line of the message starts with `Change-set:` and its value is not a slug (`[a-z][a-z0-9-]*`), `/CS-` and three digits, with only spaces or tabs around it, the commit rule shall give the problem ``` `Change-set: <value trimmed>` must be <prd>/CS-nnn ```, `<prd>` this PRD's `prd:` value.
- AC-092.2 If a well-formed value names this PRD and the PRD folder's `changes/` holds no file `CS-nnn.md` of that number, the commit rule shall give the problem `Change-set: <prd>/CS-nnn has no record in changes/`.
- AC-092.3 When a well-formed value names another PRD's slug, or names this PRD and `changes/CS-nnn.md` exists, the commit rule shall give no problem for that line.
Errors: -
Edge cases: every `Change-set:` line counts → AC-092.1
Tests: T-092.1 [integration], T-092.2 [integration], T-092.3 [integration], T-092.4 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_git_hook; cli:prd_trace

### FR-093 The commit-msg hook refuses a message the commit rule rejects
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/githook.py:11 @a87f336
Flow: 1. read the staged paths (`git diff --cached --name-status -z -M`) → 2. a merge in progress: allow
      → 3. drop `#` lines from the message → 4. a staged path inside the Boundary: FR-091 and FR-092 problems → 5. print each, exit 1
Acceptance (EARS):
- AC-093.1 When `prd_git_hook.py commit-msg <prd_dir> <message file>` runs, a staged path lies inside the Boundary and the message has FR-091 or FR-092 problems, the commit-msg hook shall print each problem as the stderr line `prd-toolkit: <problem>`, `Refs:` problems first, then the line `prd-toolkit: accepted forms: Refs: FR-001, E-002 | Refs: none (no behaviour change)`, and exit 1.
- AC-093.2 When a staged path lies inside the Boundary and the message has no problem, the commit-msg hook shall print nothing and exit 0.
- AC-093.3 The commit-msg hook shall not read a message line that starts with `#`.
- AC-093.4 While a merge is in progress (the file `git rev-parse --git-path MERGE_HEAD` names exists), the commit-msg hook shall print nothing and exit 0.
- AC-093.5 If a staged path lies inside the Boundary, a staged path lies outside the PRD folder and a `Refs:` item names an errors.md entry with no `Confirmed:` line, the commit-msg hook shall give the problem `<E-id> is not confirmed; a commit that changes code may cite it only after prd_error.py confirm`.
- AC-093.6 The commit-msg hook shall count as staged paths both paths of a staged rename and the path of a staged deletion.
- AC-093.7 The commit-msg hook shall take as the Boundary the `adopted` rows' globs of the working tree's `adoption.md`, or AC-090.2's Boundary when the folder holds no `adoption.md`.
- AC-093.8 If no staged path lies inside the Boundary, and the message names no errors.md entry and holds no `Change-set:` line, the commit-msg hook shall print nothing and exit 0.
- AC-093.9 If no staged path lies inside the Boundary, a staged path lies outside the PRD folder and a `Refs:` item names an errors.md entry with no `Confirmed:` line, the commit-msg hook shall print AC-093.5's problem for that entry as AC-093.1 prints a problem, once for each such entry, then AC-093.1's `accepted forms` line, and exit 1.
- AC-093.10 If no staged path lies inside the Boundary and the message has an FR-092 problem, the commit-msg hook shall print each such problem as AC-093.1 prints a problem, after any AC-093.9 line, then AC-093.1's `accepted forms` line, and exit 1.
Errors: -
Edge cases: a `--amend` that only rewrites the message stages no path and is allowed (README Known limits) → AC-093.8; the staged paths are read relative to the repository root → AC-093.7; outside the Boundary the hook asks for no `Refs:` line → AC-093.8; a commit that stages only paths inside the PRD folder may cite an unconfirmed entry → AC-093.9; a line that starts with `#` is dropped whatever git's `core.commentChar` or cleanup mode is → AC-093.3
Tests: T-093.1 [integration], T-093.2 [integration], T-093.3 [integration], T-093.4 [integration], T-093.5 [integration], T-093.6 [integration], T-093.7 [integration], T-093.8 [integration], T-093.9 [integration], T-093.10 [integration], T-093.11 [integration], T-093.12 [integration], T-093.13 [integration], T-093.14 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_git_hook; FR-091; FR-092

### FR-094 The pre-commit hook runs each enforced standards row
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prdlint/githook.py:26 @a87f336
Acceptance (EARS):
- AC-094.1 The pre-commit hook shall run no section 5 row whose Decision is not `enforced`, and no `enforced` row whose Linter command cell holds no backticked span.
- AC-094.2 If an enforced row's command cannot be split as shell words or cannot be started, the pre-commit hook shall print the stderr line ``prd-toolkit: `<command>` could not run: <error>`` and exit 1.
- AC-094.3 When two or more enforced rows' linters fail, the pre-commit hook shall print one FR-068 `failed` line per failing row, in section 5 row order, print no `accepted forms` line, and exit 1.
- AC-094.4 When every enforced row given a path exits 0, the pre-commit hook shall print nothing and exit 0.
Errors: -
Edge cases: which paths a row is given, and the `failed` line's text, are FR-068's; each linter runs from the repository root → AC-094.4
Tests: T-094.1 [integration], T-094.2 [integration], T-094.3 [integration], T-094.4 [integration], T-094.5 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_git_hook; FR-068

### FR-095 The git hook command refuses what it cannot run, and finds the work tree
Status: live (since 9.1.0)
Source: prd-toolkit/scripts/prd_git_hook.py:66 @a87f336
Acceptance (EARS):
- AC-095.1 If prd_git_hook.py is run with no hook name, it shall print its usage line, starting `usage: prd_git_hook.py`, on stderr and exit 2.
- AC-095.2 If the folder holds no file named `prd.md`, the git hook command shall print `prd-toolkit: <resolved folder>: no prd.md` on stderr and exit 2.
- AC-095.3 If `prd.md` section 8 holds a table and the folder holds no `adoption.md`, the git hook command shall print `prd-toolkit: <resolved folder>/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."` on stderr and exit 2.
- AC-095.4 While `GIT_DIR` is set and `GIT_WORK_TREE` is not, the git hook command shall set `GIT_DIR` to its absolute path and `GIT_WORK_TREE` to the top of the work tree as `git rev-parse --show-toplevel` gives it from the hook's working directory, before any other git call, so it reads the staged paths and runs each linter at that top.
Errors: -
Edge cases: a relative `GIT_DIR` (`.git`) in the main checkout and an absolute one in a linked worktree are the same rule → AC-095.4; a failure in that step or while reading the staged paths prints `prd-toolkit: internal error: <type>: <message>` and exits 2 (no test: no black-box input triggers it)
Tests: T-095.1 [integration], T-095.2 [integration], T-095.3 [integration], T-095.4 [integration], T-095.5 [integration]  (test-cases/trace.yaml)
Traces: cli:prd_git_hook

### FR-096 The hook shims skip a branch without the vendored copy
Status: live (since 9.1.0)
Source: prd-toolkit/templates/hooks/commit-msg:3 @a87f336
Flow: 1. find the work tree top → 2. copy without launcher: skip → 3. no copy or no PRD folder: skip → 4. no uv: block → 5. exec the launcher's `git-hook`
Acceptance (EARS):
- AC-096.1 If `git rev-parse --show-toplevel` fails, the hook shim shall exit 1.
- AC-096.2 If `<top>/.prd-toolkit/prd_git_hook.py` exists and `<top>/.prd-toolkit/prd` does not, the hook shim shall print `prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped` on stderr and exit 0.
- AC-096.3 If `<top>/.prd-toolkit/prd_git_hook.py`, `<top>/.prd-toolkit/prd` or the folder `<top>/<prd folder>` is absent, the hook shim shall print `prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped` on stderr and exit 0.
- AC-096.4 If the vendored copy and the PRD folder are present and `uv` is not on PATH, the hook shim shall print `prd-toolkit: uv is not on PATH; install uv to run this hook` on stderr and exit 1.
- AC-096.5 When the vendored copy, the PRD folder and `uv` are present, the hook shim shall run `sh <top>/.prd-toolkit/prd git-hook <hook> <top>/<prd folder>`, the commit-msg shim adding the arguments git gave it, and exit with that command's exit code.
- AC-096.6 The hook templates `templates/hooks/commit-msg` and `templates/hooks/pre-commit` shall hold, as line 2, `# prd-toolkit hook: written by prd_hooks.py install; removed by prd_hooks.py uninstall`.
Errors: -
Edge cases: `{{hook}}` and `{{prd}}` are filled by `prd_hooks.py install` (area hooks-install) → AC-096.5; the pre-commit shim passes no argument of its own → AC-096.5
Tests: T-096.1 [integration], T-096.2 [integration], T-096.3 [integration], T-096.4 [integration], T-096.5 [integration], T-096.6 [integration], T-096.7 [integration]  (test-cases/trace.yaml)
Traces: cli:git_hook_shims; FR-070
