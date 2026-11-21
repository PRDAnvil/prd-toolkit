# error-replay

An `errors.md` entry closes with a Resolution line that names the commit that fixed it, and nothing
checked that claim. This area checks it: `prd error replay <prd_dir> <E-id>` runs the entry's test on the
commit before the fix, where it must fail, and on the fix, where it must pass, each run in a git worktree
of its own that it removes. It adds a fourth form of Resolution line, a fix with no T-id for code that no
adopted area covers, which `prd error resolve --red-run` writes only when that replay holds and
`prd error check` reads; and the optional `One test` column of the `testing.md` Levels table, the command
that runs one test, which the replay runs. Its one module is `prd-toolkit/scripts/prdlint/errorreplay.py`.
The same build makes the edits this area needs in `prd_error.py` and `prdlint/errors.py` (area `errors`:
they parse the new subcommand and flags and call the module), `prdlint/model.py` (area `lint-cli`: the
Levels loader reads the column), `prdlint/rules/registries.py` (area `lint-registries`: the rule
`runbook-tests` reports a malformed cell and its description names the column),
`references/prd-format.md` (area `skills`: the column and the fourth form) and `references/help.yaml`
(area `help`: its entry `kind.E` names the fourth form); what each edit does is stated here. The three
older forms of a Resolution line are written, read and checked as before.

Words used below.

- A **Resolution line** is the text after `Resolution:` in an entry, the white space around it removed. It
  has one of four forms: a **fix with a T-id**, `<T-id> [<level>], PRD <X.Y.Z>, fixed in <sha>`; an
  **environment run**, `<T-id or ->, PRD <X.Y.Z>, run <run id>`; **not a defect**, `not a defect: <why>`;
  and a **red run**, `fixed in <sha>, red run <test id> [<level>]`. In each, `<sha>` is 7 to 40 lowercase
  hex digits; in a red run, `<test id>` is one or more characters, none of them white space and the first
  not `-`, and `<level>` is one or more characters, none of them white space or `]`. An entry whose line is
  empty, `-` or starts with `open` is open, as the format reference says.
- An entry's **level** is the text between the brackets of its Resolution line, and its **subject** is the
  T-id of a fix with a T-id or the test id of a red run.
- `<sha>` in any output is the text the Resolution line holds (for `resolve --red-run`, the `--commit`
  value as given), and `<sha>^` is that text followed by `^`. `<sha>` **names one commit** when git
  resolves it to exactly one commit; `<sha>^` is that commit's first parent.
- A One test cell is **one simple command in backticks** when, with the white space around it removed, it
  starts and ends with a backtick and holds no other backtick; the text between the two, split into words
  as a POSIX shell splits them (quotes group words and are removed, a backslash escapes the next
  character, nothing is expanded), gives one or more words; its first word is none of `cd`, `env`, `sh`,
  `bash`, `zsh`, `eval` and `exec` and holds no `=`; and the text holds none of `$`, `{`, `~`, `;` and `|`,
  and not `&&`. A level's **One test command** is those words.
- A **test root** is a backticked path of the `Test roots:` list in the Layout line of `testing.md` in the
  working tree, less the white space around it and every `/` at its end; with no such list the one test
  root is `tests`. A path **lies under** a root when it equals the root or starts with the root and `/`. A
  text **cites** a T-id when one of its lines holds `@prd`, white space and the T-id, as trace reads a
  citation.
- The **resolving commit** of an entry is the first commit, in the order
  `git rev-list --topo-order --reverse HEAD` prints them, whose PRD folder's `errors.md` holds the entry
  with the same Resolution line as `errors.md` in the working tree; when no commit does, it is `HEAD`.
  `<resolving commit>` in an output is the first 7 hex digits of its SHA.
- A **run** starts the level's One test command with one more word appended, its argument, without a
  shell, from the root of a worktree, with the environment the command itself has, in a process group of
  its own. A run that exits 0 **passes**; one that exits with any other code **fails**. A run still going
  when the timeout ends is killed with its process group; it **times out**, and neither passes nor fails.
  A run whose program the operating system cannot start **cannot start**, and neither passes nor fails.
- The **timeout** of a run is the `--timeout` value when one is given, else the level's `Timeout` cell when
  it holds a number, else 600 seconds. `<N>` in an output is that timeout in whole seconds.
- A **worktree** is one that the command adds with `git worktree add --detach` under a new folder it makes
  in the system temporary folder (the folder the `TMPDIR` variable names, when it is set), at the commit
  under test. Every git command the replay runs has the environment the command itself has without the
  variables `git rev-parse --local-env-vars` lists, so none of them points it at the repository the
  command is started in. The command never writes the working tree or the index of the repository it is
  started in.
- A path is **covered** by an area when a Boundary glob of that area's `adopted` row in `adoption.md`
  matches it, as the commit rule matches the globs; the area named is the first such row in the table's
  order. A path in the PRD folder or in `.prd-toolkit/` is covered by no area. The **paths a commit
  changes** are those `git diff --no-renames --name-only <sha>^ <sha>` prints, from the repository root,
  in the order it prints them.

### UJ-07 Anyone with the repository sees whether the commit an entry names fixed it
Status: verified
Source: prd-toolkit/scripts/prd_error.py:182 @68d53f9
Flow: 1. an entry is resolved, with a T-id by `/prd-toolkit:prd-build --fixes`, or with a red run by
      `prd error resolve <prd_dir> <E-id> --commit <sha> --red-run <test id> --level <level>`
      → 2. `prd error replay <prd_dir> <E-id>` runs the entry's test on `<sha>^` and on `<sha>`
      → 3. it prints that the test fails on `<sha>^` and passes on `<sha>`, a skip and its reason, or each
      finding → 4. `prd error check <prd_dir> <base>..<head>` reads the red run, as it reads the other forms
Traces: FR-075, FR-076, FR-077, FR-078, FR-079, FR-080, FR-081

### FR-075 The One test column of the Levels table
Status: verified
Source: prd-toolkit/scripts/prdlint/model.py:982 @68d53f9
Flow: 1. load testing.md → 2. find the Levels table's optional `One test` column by its header name, as
      `Timeout` is found → 3. read each level's cell as its One test command → 4. lint reports a cell that
      is not one simple command in backticks
Acceptance (EARS):
- AC-075.1 Where the Levels table of `testing.md` has a column whose header, its white space and
  backticks removed, is `One test` in any letter case, the error command shall run, for a level whose cell
  in that column is one simple command in backticks, that level's One test command; and a level whose cell
  is empty or holds only white space, or any level of a Levels table with no such column, shall have no
  One test command.
- AC-075.2 If a level's One test cell, the white space around it removed, is not empty and is not one
  simple command in backticks, the lint command shall report `runbook-tests` at that level's row in
  `testing.md` with `level '<level>': One test '<cell>' is not one simple command in backticks`, where
  `<cell>` is the cell with the white space around it removed.
- AC-075.3 While every One test cell of the Levels table is empty or one simple command in backticks, the
  lint command shall print for the PRD folder what it prints for the same folder with the One test column
  taken out of the Levels table.
- AC-075.4 The help command, run as `prd_help.py --rule runbook-tests`, shall print as its second stdout
  line the description `Checks that each level a runbook tests step names is in testing.md Levels with Gate deploy and a Harness command, that each Timeout cell is a whole number of seconds of at least 1, and that each One test cell is one simple command in backticks. Add or fix the level's row, or name a deploy-gate level.`
Errors: -
Edge cases: `cd`, a first word that holds `=`, a cell without backticks, two backticked spans, an
unbalanced quote, `~`, `;` and `|` are each reported → AC-075.2; quotes that group words are allowed →
AC-075.1, AC-075.2; nothing else reads the column: the level's Harness command still runs the level at a
build and at a deploy, and the tester guard allows what it allowed → AC-075.3; the rule count stays 41 →
AC-075.2
Tests: T-075.1 [integration], T-075.2 [integration], T-075.3 [integration], T-075.4 [integration], T-075.5 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_lint; cli:prd_help; testing.md Levels

### FR-076 Replay an entry resolved with a T-id
Status: approved
Source: prd-toolkit/scripts/prdlint/errorreplay.py:156 @68d53f9
Flow: 1. read the entry from `errors.md` in the working tree → 2. find its resolving commit and the
      files under the test roots there that cite its T-id → 3. run each file on the tree of `<sha>^`, its
      test roots replaced by the resolving commit's → 4. run each file on the tree of `<sha>`, the roots
      replaced the same way → 5. print what the runs show
Acceptance (EARS):
- AC-076.1 When `prd_error.py replay <prd_dir> <E-id>` is run on an entry whose Resolution line is a fix
  with a T-id, whose level is a row of the Levels table with Gate `build` and a One test command, and whose
  `<sha>` names one commit that has a parent, the error command shall take as the cited files each file
  under a test root, in the resolving commit's tree, whose text cites the T-id, and shall make one run per
  cited file, in the sorted order of their paths, with the file's path from the repository root as its one
  argument, on the tree of `<sha>^` and then on the tree of `<sha>`, each tree in a worktree with every
  test root replaced, whole, by that root of the resolving commit's tree and every other path as the
  commit holds it.
- AC-076.2 When at least one cited file fails on `<sha>^` and every cited file passes on `<sha>`, the error
  command shall print the one stdout line `<E-id>: <T-id> fails on <sha>^ and passes on <sha>` and exit 0.
- AC-076.3 If every cited file passes on `<sha>^`, the error command shall print the finding
  `<E-id>: <T-id> passes on <sha>^; <sha> did not turn it green`; if a cited file fails on `<sha>`, it
  shall print the finding `<E-id>: <T-id> fails on <sha>: <file>` for that file, `<file>` its path from
  the repository root; and on either it shall exit 1.
- AC-076.4 If no file under a test root of the resolving commit's tree cites the T-id, the error command
  shall print the finding `<E-id>: <T-id> is cited by no test in <resolving commit>`, make no run and
  exit 1.
- AC-076.5 While the entry's Resolution line is in `errors.md` in the working tree and in no commit that
  `HEAD` reaches, the error command shall take the cited files and the test roots from `HEAD`'s tree,
  never from the working tree.
Errors: -
Edge cases: a regression test committed after its fix proves the fix, since the tests come from the
resolving commit → AC-076.1; only the test roots are replaced, so the run on `<sha>^` runs the old code →
AC-076.1; a cited path that holds a space is passed as one argument → AC-076.1; the fix commit is a merge:
`<sha>^` is its first parent → AC-076.1; a test file of the resolving commit that does not cite the T-id
is not run, though it fails on older code → AC-076.1; a harness that starts in a fresh worktree and fails
there for want of what only the repository's own checkout holds fails on `<sha>` too, so the proof never
holds → AC-076.3; a One test program that the operating system cannot start in a fresh worktree is no
fail: the run cannot start, a finding of its own → AC-078.14; two entries whose tests share a file share
one proof, since the proof is per file
Tests: T-076.1 [integration], T-076.2 [integration], T-076.3 [integration], T-076.4 [integration], T-076.5 [integration], T-076.6 [integration], T-076.7 [integration], T-076.8 [integration], T-076.9 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_error

### FR-077 Replay an entry resolved with a red run
Status: verified
Source: prd-toolkit/scripts/prdlint/errorreplay.py:342 @68d53f9
Flow: 1. read the entry from `errors.md` in the working tree → 2. run its test id on the tree of `<sha>^`
      as committed → 3. run it on the tree of `<sha>` as committed → 4. print what the runs show
Acceptance (EARS):
- AC-077.1 When `prd_error.py replay <prd_dir> <E-id>` is run on an entry whose Resolution line is a red
  run, whose level is a row of the Levels table with Gate `build` and a One test command, and whose `<sha>`
  names one commit that has a parent, the error command shall make two runs, each with the test id as its
  one argument, written as the line holds it: one in a worktree of `<sha>^` as committed, then one in a
  worktree of `<sha>` as committed.
- AC-077.2 When the run on `<sha>^` fails and the run on `<sha>` passes, the error command shall print the
  one stdout line `<E-id>: <test id> fails on <sha>^ and passes on <sha>` and exit 0.
- AC-077.3 If the run on `<sha>^` passes, the error command shall print the finding
  `<E-id>: <test id> passes on <sha>^; <sha> did not turn it green`; if the run on `<sha>` fails, it shall
  print the finding `<E-id>: <test id> fails on <sha>: <test id>`; and on either it shall exit 1.
Errors: -
Edge cases: a `$` or a `;` in the test id reaches the command as plain text → AC-077.1; a test committed
after its fix is not in `<sha>^` or in `<sha>`, so both runs fail and the proof does not hold → AC-077.1,
AC-077.3
Tests: T-077.1 [integration], T-077.2 [integration], T-077.3 [integration], T-077.4 [integration], T-077.5 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_error

### FR-078 What the replay prints and how it exits
Status: approved
Source: prd-toolkit/scripts/prdlint/errorreplay.py:370 @68d53f9
Flow: 1. read the entry → 2. make the checks in order, the first that matches deciding → 3. make the runs
      → 4. print one line per finding, or the one line that the proof holds or that the entry is skipped
Acceptance (EARS):
- AC-078.1 If `<E-id>` names no entry of `errors.md`, the error command shall print the stderr line
  `refused: <E-id> is not an entry`, print nothing on stdout, with or without `--json`, make no run and
  exit 1.
- AC-078.2 If the entry is open, the error command shall print the finding `<E-id> is not resolved`, and
  if its Resolution line is none of the four forms, the finding
  `<E-id>: resolution is not one of the four forms`; in either case it shall make no run and exit 1.
- AC-078.3 When the entry's Resolution line is an environment run, the error command shall print the one
  stdout line `skipped: <E-id>: resolved by an environment run`, and when it is not a defect, the line
  `skipped: <E-id>: resolved as not a defect`; in either case it shall make no run and exit 0.
- AC-078.4 If the entry's level is not a row of the Levels table, the error command shall print the
  finding `<E-id>: <level> is not a level of testing.md`, make no run and exit 1.
- AC-078.5 When the entry's level has Gate `deploy`, the error command shall print the one stdout line
  `skipped: <E-id>: <level> is a deploy-gate level`, and when the level has no One test command, the line
  `skipped: <E-id>: <level> has no One test command`; in either case it shall make no run and exit 0.
- AC-078.6 If `<sha>` names no commit, the error command shall print the finding
  `<E-id>: <sha> names no commit`; if it names more than one commit, the finding
  `<E-id>: <sha> names more than one commit`; if it names one commit that has no parent, the finding
  `<E-id>: <sha> has no parent`; in each case it shall make no run and exit 1.
- AC-078.7 The error command shall make its checks in this order and report only the first that matches:
  the entry exists (AC-078.1); it is resolved, and its line is one of the four forms (AC-078.2); it is not
  resolved by an environment run or as not a defect (AC-078.3); its level is a row of Levels (AC-078.4);
  that level's Gate is not `deploy`, then it has a One test command (AC-078.5); `<sha>` names one commit,
  then that commit has a parent (AC-078.6); and, for a fix with a T-id, a file cites it (AC-076.4).
- AC-078.8 When the checks pass, the error command shall make every run on `<sha>^` and then every run on
  `<sha>`, each group in its argument order, whatever the runs on `<sha>^` show, and shall print the
  findings of the runs on `<sha>^` and then those of the runs on `<sha>`, one stdout line each, each group
  in argument order.
- AC-078.9 If a run times out, the error command shall print the finding
  `<E-id>: timed out after <N> s on <commit>`, where `<commit>` is `<sha>^` for a run on `<sha>^` and
  `<sha>` for a run on `<sha>`, count that run as neither passing nor failing, make the runs that remain,
  and exit 1.
- AC-078.10 If `--timeout` is given a value that is not a whole number of at least 1 written in the digits
  0 to 9, the error command shall print the stderr line
  `prd_error: --timeout must be a whole number of seconds of at least 1`, make no run and exit 2.
- AC-078.11 When run with `--json`, the error command shall print on stdout, in place of its lines, one
  JSON object on one line, ending in a newline,
  `{"interface": 1, "kind": "error-replay", "entry": <E-id>, "outcome": <outcome>, "subject": <subject>, "reason": <reason>, "findings": [<finding>, …], "runs": [<run>, …]}`,
  with its keys in that order and the exit code it has without `--json`, where `<outcome>` is `holds`,
  `skipped` or `findings`; `<subject>` is the entry's subject, or null for any other line; `<reason>` is
  the text of the skip line after `skipped: <E-id>: `, or null; each `<finding>` is a finding line as the
  text form prints it, in its order; and each `<run>` is
  `{"commit": <the full SHA of the commit whose tree ran>, "when": "before" or "after", "argument": <the argument>, "exit": <its exit code, or null when it timed out or cannot start>, "seconds": <a number>, "timed_out": <true or false>}`,
  in the order the runs were made.
- AC-078.12 If the error command, run with `--json`, exits 2, it shall print on stdout one JSON object on
  one line, ending in a newline, `{"interface": 1, "kind": "error-replay", "error": <message>}`, where
  `<message>` is its stderr line without the `prd_error: ` prefix, or argparse's error message for a bad
  command line, and shall print its stderr lines as it does without `--json`; and if the command line holds
  `--json=<N>` with any `<N>` other than `1`, it shall print that object with the message
  `unsupported interface <N>; this toolkit speaks 1` and the stderr line
  `prd_error: unsupported interface <N>; this toolkit speaks 1`, read no folder and exit 2.
- AC-078.13 When run as `prd_error.py replay --interface`, the error command shall print `1` on one stdout
  line and exit 0, whatever other arguments are given, reading no folder.
- AC-078.14 If a run cannot start, the error command shall print the finding
  `<E-id>: <program> cannot start on <commit>`, where `<program>` is the first word of the level's One
  test command, its quotes removed, and `<commit>` is `<sha>^` for a run on `<sha>^` and `<sha>` for a run
  on `<sha>`, count that run as neither passing nor failing, make the runs that remain, and exit 1; with
  `--json`, that run's record shall have `exit` null and `timed_out` false.
Errors: -
Edge cases: `--json=1` is the same as `--json` → AC-078.11; `seconds` is the run's time and is never
compared to a value → AC-078.11; a line of no form, such as free text written before prd-toolkit 0.6, is a
finding, so older entries need not hold → AC-078.2; a missing argument is argparse's usage error, exit 2;
the stderr is empty whenever the exit is 0 or 1, but for AC-078.1's line; a program that only `<sha>`
holds cannot start on `<sha>^`, which is no fail, so the proof does not hold → AC-078.14
Tests: T-078.1 [integration], T-078.2 [integration], T-078.3 [integration], T-078.4 [integration], T-078.5 [integration], T-078.6 [integration], T-078.7 [integration], T-078.8 [integration], T-078.9 [integration], T-078.10 [integration], T-078.11 [integration], T-078.12 [integration], T-078.13 [integration], T-078.14 [integration], T-078.15 [integration], T-078.16 [integration], T-078.17 [integration], T-078.18 [integration], T-078.19 [integration], T-078.20 [integration], T-078.21 [integration], T-078.22 [integration], T-078.23 [integration], T-078.24 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_error

### FR-079 The replay leaves nothing behind and writes nothing
Status: approved
Source: prd-toolkit/scripts/prdlint/errorreplay.py:207 @68d53f9
Flow: 1. add a worktree for each run → 2. remove it when the run ends → 3. remove the folder the
      worktrees were made in when the command ends, however it ends
Acceptance (EARS):
- AC-079.1 When the replay ends with the proof holding, `git worktree list --porcelain` in the repository
  shall print what it printed before the command started, the folder the command made in the system
  temporary folder shall no longer exist, and `git status --porcelain` shall print what it printed before.
- AC-079.2 When the replay ends with findings, `git worktree list --porcelain` in the repository shall
  print what it printed before the command started, the folder the command made in the system temporary
  folder shall no longer exist, and `git status --porcelain` shall print what it printed before.
- AC-079.3 When a run of the replay times out, `git worktree list --porcelain` in the repository shall
  print what it printed before the command started once the command ends, the folder the command made in
  the system temporary folder shall no longer exist, and `git status --porcelain` shall print what it
  printed before.
- AC-079.4 If the command receives SIGINT while a run is going, the error command shall kill the run's
  process group, remove the run's worktree and its folder, and exit 130, after which
  `git worktree list --porcelain` in the repository shall print what it printed before the command
  started and `git status --porcelain` what it printed before.
- AC-079.5 Where the command is started inside a linked worktree of the repository, the error command
  shall read `errors.md` and `testing.md` from that worktree's checkout, and when it ends
  `git worktree list --porcelain` shall print what it printed before it started, the linked worktree
  included.
Errors: -
Edge cases: a test points `TMPDIR` at an empty folder and finds it empty again when the command ends →
AC-079.1 to AC-079.5; `prd error resolve --red-run`, which replays, leaves nothing behind the same way →
AC-079.2, FR-080; an internal error ends the command the same way, with exit 2; a command started with
`GIT_INDEX_FILE`, `GIT_DIR` or `GIT_WORK_TREE` set, as git sets `GIT_INDEX_FILE` for its pre-commit and
commit-msg hooks, leaves its repository's index and working tree as they were, since no git command the
replay runs has those variables → AC-079.1 to AC-079.3
Tests: T-079.1 [integration], T-079.2 [integration], T-079.3 [integration], T-079.4 [integration], T-079.5 [integration], T-079.6 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_error

### FR-080 Resolve a fix outside every adopted Boundary with a red run
Status: approved
Source: prd-toolkit/scripts/prd_error.py:170 @68d53f9
Flow: 1. read the flags → 2. read the entry, its class and the level → 3. check the test id and the paths
      the fix commit changes → 4. replay the line it would write → 5. write the line, or refuse and leave
      `errors.md` as it was
Acceptance (EARS):
- AC-080.1 When `prd_error.py resolve <prd_dir> <E-id> --commit <sha> --red-run <test id> --level <level>`
  is run on a `confirmed` entry of class `code bug`, with a level that is a row of the Levels table with
  Gate `build` and a One test command, a test id that holds no white space and does not start with `-`, a
  commit no path of which is covered by an area, and a replay (FR-077) of the line
  `fixed in <sha>, red run <test id> [<level>]` that holds, the error command shall write
  `Resolution: fixed in <sha>, red run <test id> [<level>]` into the entry, in place of its `Resolution:`
  line when it has one, leaving every other line of `errors.md` as it was; shall print the one stdout line
  `<E-id> resolved code bug`; and shall exit 0.
- AC-080.2 If `--red-run` is given with `--t`, `--version`, `--run` or `--not-a-defect`, or without
  `--commit` or without `--level`, or if `--level` is given without `--red-run`, the error command shall
  print the stderr line
  `prd_error: --red-run takes --commit and --level, and no --t, --version, --run or --not-a-defect`, leave
  `errors.md` byte for byte as it was and exit 2.
- AC-080.3 If `--red-run` is given with a `--commit` value that is not 7 to 40 lowercase hex digits, the
  error command shall print the stderr line
  `prd_error: commit must be 7 to 40 lowercase hex digits; got '<value>'`, leave `errors.md` byte for
  byte as it was and exit 2.
- AC-080.4 If the entry is not an entry, is already resolved or is not `confirmed`, the error command
  shall print the stderr line `refused: <E-id> is not an entry`, `refused: <E-id> is already resolved` or
  `refused: <E-id> is not confirmed`, as `resolve` refuses the other forms, leave `errors.md` byte for
  byte as it was and exit 1.
- AC-080.5 If the entry's class is not `code bug`, the error command shall print the stderr line
  `refused: <E-id> is classed <class>; a red run resolves a code bug only`, leave `errors.md` byte for
  byte as it was and exit 1.
- AC-080.6 If the level is not a row of the Levels table, has Gate `deploy`, or has no One test command,
  the error command shall print the stderr line `refused: <level> is not a level of testing.md`,
  `refused: <level> is a deploy-gate level`, or
  `refused: <level> has no One test command; add the One test column to testing.md Levels through /prd-toolkit:prd-change`,
  leave `errors.md` byte for byte as it was and exit 1.
- AC-080.7 If the test id holds white space or starts with `-`, the error command shall print the stderr
  line `refused: the test id must hold no white space and must not start with -`, leave `errors.md` byte
  for byte as it was and exit 1.
- AC-080.8 If the PRD has no adoption map, the error command shall print the stderr line
  `refused: the PRD has no adoption map, so every path is covered; resolve with a regression T-id`; and if
  `<sha>` names one commit that has a parent and a path it changes is covered by an area, the stderr line
  `refused: <sha> changes <path>, which area <area> covers; resolve with a regression T-id` for the first
  such path; in either case it shall leave `errors.md` byte for byte as it was and exit 1.
- AC-080.9 If the replay of the line it would write does not hold, the error command shall print each of
  the replay's findings as its own stderr line `refused: <finding>`, in the replay's order, leave
  `errors.md` byte for byte as it was and exit 1.
- AC-080.10 The error command shall make the refusals of `resolve --red-run` in this order and print only
  the first that matches: the flags (AC-080.2, AC-080.3); the entry (AC-080.4); its class (AC-080.5); the
  level, as not a level, then a deploy-gate level, then no One test command (AC-080.6); the test id
  (AC-080.7); the adoption map, then the paths the commit changes (AC-080.8); and last the replay
  (AC-080.9), with the level's timeout.
Errors: -
Edge cases: `--red-run=-x` gives a test id that starts with `-`, since `--red-run -x` reads as an option →
AC-080.7; a One test program that cannot start gives the replay's finding, so the refusal → AC-080.9,
AC-078.14; a `<sha>` that names no commit, or one with no parent, has no paths to check, so the replay's
finding is the refusal → AC-080.8, AC-080.9; a path in the PRD folder or in `.prd-toolkit/` is covered by
no area → AC-080.8; a refused write never leaves a half-written line → AC-080.2 to AC-080.9; the write
goes through the lint guard every `resolve` passes, as before → AC-080.1
Tests: T-080.1 [integration], T-080.2 [integration], T-080.3 [integration], T-080.4 [integration], T-080.5 [integration], T-080.6 [integration], T-080.7 [integration], T-080.8 [integration], T-080.9 [integration], T-080.10 [integration], T-080.11 [integration], T-080.12 [integration], T-080.13 [integration], T-080.14 [integration], T-080.15 [integration], T-080.16 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_error

### FR-081 Check a red run, and the older forms as before
Status: approved
Source: prd-toolkit/scripts/prdlint/errors.py:299 @68d53f9
Flow: 1. `prd error check` finds the Resolution lines added in its range → 2. a red run is checked
      against the PRD at the range's head, with no run → 3. the three older forms are checked as before
Acceptance (EARS):
- AC-081.1 When `prd_error.py check <prd_dir> <base>..<head>` reads a red run added in its range, it shall
  make no run, and shall print `errors.md: <E-id>: commit <sha> is not an ancestor of HEAD` when `<sha>`
  is not an ancestor of `<head>`; `errors.md: <E-id>: the PRD has no adoption map, so every path is covered`
  when the PRD at `<head>` has no adoption map; `errors.md: <E-id>: commit <sha> changes <path>, which area <area> covers`
  for the first path the commit changes that an area of the PRD at `<head>` covers; and
  `errors.md: <E-id>: <level> is not a level of testing.md` when the level is not a row of the Levels
  table of the PRD at `<head>`; each a line of stdout, in that order, and it shall exit 1 when it prints
  any line.
- AC-081.2 If a Resolution line added in the range is none of the four forms, the check command shall
  print `errors.md: <E-id>: resolution is not one of the four forms`, the line that takes the place of
  `errors.md: <E-id>: resolution is not one of the three forms`, and exit 1.
- AC-081.3 When `prd_error.py check <prd_dir> <base>..<head>` reads a Resolution line added in its range,
  of an entry that holds a `Confirmed:` line, the check command shall make no run and shall print: for a
  fix with a T-id whose T-id has no test case in the PRD at `<head>`, the stdout line
  `errors.md: <E-id>: <T-id> has no test case`; for an environment run `-, PRD <X.Y.Z>, run <run id>`
  whose run id has no deploy run log, the stdout line
  `errors.md: <E-id>: run <run id> has no log in <folder>`, where `<folder>` is the absolute path, with
  symbolic links resolved, of the folder `prd-toolkit/deploys` in the repository's git common folder;
  nothing for not a defect; and nothing for a fix with a T-id whose T-id has a test case in the PRD at
  `<head>`, is cited by a file under a test root and is not marked `known-failing` on the entry, whose
  `<X.Y.Z>` has a section 14 row and is not above the PRD's version at `<head>`, and whose commit is an
  ancestor of `<head>`; and it shall exit 1 when it prints a line, else 0.
- AC-081.4 When `prd_error.py resolve <prd_dir> <E-id>` is run on a `confirmed` entry with
  `--t <T-id> --version <X.Y.Z> --commit <sha>`, the error command shall write the line
  `Resolution: <T-id> [<level>], PRD <X.Y.Z>, fixed in <sha>`, `<level>` being the `level:` of the T-id's
  test case; with `--t <T-id> --version <X.Y.Z> --run <run id>`, the line
  `Resolution: <T-id>, PRD <X.Y.Z>, run <run id>`; and with `--not-a-defect <why>` alone, where `<why>`
  holds no line break and no two white-space characters in a row, the line
  `Resolution: not a defect: <why>`; each in place of the entry's `Resolution:` line when it has one,
  leaving every other line of `errors.md` as it was; and in each case it shall print the one stdout line
  `<E-id> resolved <class>`, `<class>` being the entry's Classification, make no run and exit 0.
- AC-081.5 The help catalogue the toolkit ships shall name, in the `rules` of its entry `kind.E`, the red
  run `fixed in <commit>, red run <test id> [<level>]` (code bug) as a form of resolution, beside the other
  three.
Errors: -
Edge cases: a red run whose `<sha>` names no commit gets the ancestor line alone, since it has no paths →
AC-081.1; a deploy-gate level or a level with no One test command is not a check finding: `resolve`
refuses it → AC-081.1; an older vendored copy reports a red run as none of the three forms it knows, so a
repository re-vendors before its ledger holds one
Tests: T-081.1 [integration], T-081.2 [integration], T-081.3 [integration], T-081.4 [integration], T-081.5 [integration], T-081.6 [integration], T-081.7 [integration], T-081.8 [integration], T-081.9 [integration], T-081.10 [integration], T-081.11 [integration], T-081.12 [integration], T-081.13 [integration], T-081.14 [integration]  (test-cases/error-replay.yaml)
Traces: UJ-07; cli:prd_error
