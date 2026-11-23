<!-- Format: references/prd-format.md, "Requirement blocks". -->

# Status: the report, the managed blocks and the PRD facts

`prd status` prints the Next part (area `status-next`), then thirteen parts that say where every requirement stands. `prd_block.py` writes three managed blocks from the PRD: one in `CLAUDE.md`, one in the PRD folder's `README.md` and one in the parent folder's `README.md`. `prdlint/overview.py` gathers the facts that both the READMEs and the published Overview tab show.

### FR-222 The status command's arguments and refusals
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_status.py:33 @3a70ba0
  prd-toolkit/scripts/prd_status.py:52 @3a70ba0
Acceptance (EARS):
- AC-222.1 When run with `--interface`, the status command shall print the one line `1`, read no folder and
  exit 0, even when `--json=<N>` names another interface.
- AC-222.2 If no PRD folder is given and `--interface` is not, the status command shall print the one stderr line
  `usage: prd_status.py [-h] [--json] [--interface] [prd_dir]`, print nothing on stdout and exit 2. With `--json`,
  its stdout shall be the one line
  `{"interface": 1, "kind": "status", "error": "usage: prd_status.py [-h] [--json] [--interface] [prd_dir]"}`.
- AC-222.3 If `--json=<N>` names an interface other than 1 and `--interface` is not given, the status command
  shall print `prd_status: unsupported interface <N>; this toolkit speaks 1` on stderr and the one stdout line
  `{"interface": 1, "kind": "status", "error": "unsupported interface <N>; this toolkit speaks 1"}`, and exit 2.
- AC-222.4 If the folder holds no file `prd.md`, the status command shall print
  `prd_status: <folder>: no prd.md` on stderr, `<folder>` being the folder's resolved absolute path, and exit 2.
  Without `--json` it shall print nothing on stdout. With `--json` its stdout shall be the error document whose
  `error` is `<folder>: no prd.md`.
- AC-222.5 If section 8 of `prd.md` holds a table and the folder has no `adoption.md`, the status command shall
  print `prd_status: <folder>/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."`
  on stderr, print nothing on stdout and exit 2.
Errors: -
Edge cases: the internal-error line and its JSON document belong to AC-040.3; `-h` prints the help and exits 0
Tests: T-222.1 [integration], T-222.2 [integration], T-222.3 [integration], T-222.4 [integration], T-222.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status; FR-040; `prdlint/interface.py`

### FR-223 The thirteen parts and their layout
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:169 @3a70ba0
  prd-toolkit/scripts/prdlint/status.py:177 @3a70ba0
  prd-toolkit/scripts/prd_status.py:66 @3a70ba0
Acceptance (EARS):
- AC-223.1 When run on a PRD folder without `--json`, the status command shall print, after the Next part, the
  parts `Header`, `Requirements`, `Areas`, `Adoption map`, `Not built`, `Not verified`, `Open errors`,
  `Upstreams`, `Consumers`, `Change sets`, `CI`, `Deployed` and `Matrix`, each once and in that order. Each part
  is the line `## <part>`, one empty line and the part's lines, with one empty line between a part's last line and
  the next part's heading. The last part's last line ends stdout. The command shall exit 0.
- AC-223.2 The status command shall print every part with at least one line. A part with nothing to list holds
  the one line `None.`, except where this area gives that part another line.
- AC-223.3 When run with `--json`, the status command shall give each item after the Next items an `id`:
  - the area for an Areas line and an Adoption map row;
  - the block ID for a Not built, Not verified or Matrix line;
  - the entry ID for an Open errors line;
  - the link's name for an Upstreams or Consumers line;
  - the change-set ID for a Change sets line;
  - the environment for a Deployed line;
  - null for the Header, a Requirements line, a CI line, the Adoption map's `Not applicable` line and every
    `None.` line.

  The Header is one item whose `text` joins its three lines with a newline.
Errors: -
Edge cases: the item keys and the document's keys are AC-041.2's; `None.` lines carry no ID → AC-223.3
Tests: T-223.1 [integration], T-223.2 [integration], T-223.3 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status; FR-040; FR-041

### FR-224 The Header part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:170 @3a70ba0
  prd-toolkit/scripts/prd_status.py:21 @3a70ba0
Acceptance (EARS):
- AC-224.1 When run, the status command shall print as the Header's lines `PRD: <folder>`, `version <version>`
  and `status <status>`.
  - `<version>` and `<status>` are the frontmatter values of `prd.md`, each `-` when its key is missing.
  - `<folder>` is the PRD folder's resolved path relative to the working directory when the folder is the working
    directory or lies inside it (`.` for the working directory itself), and its resolved absolute path otherwise.
Errors: -
Tests: T-224.1 [integration], T-224.2 [integration], T-224.3 [integration], T-224.4 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-225 The Requirements part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:26 @3a70ba0
Acceptance (EARS):
- AC-225.1 When the PRD holds requirement blocks (UJ, FR or NFR), the status command shall print one
  Requirements line per area that holds one, `<area>: <status> <n>, <status> <n>`:
  - an area is a features file's name without `.md`, and `nfr` for `nfr.md`;
  - a status is a block's `Status:` text before any `(since …)`, or `-` for a block with no `Status:` line;
  - each status appears once with its count, the statuses sorted as text;
  - the areas follow the order of their files in the PRD (features files by path, then `nfr.md`), with `nfr`
    last.
- AC-225.2 If the PRD holds no requirement block, the Requirements part shall hold the one line `None.`.
Errors: -
Edge cases: `live (since 1.0.0)` counts as `live` → AC-225.1; a features file with no block has no line → AC-225.1
Tests: T-225.1 [integration], T-225.2 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-226 The Areas part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:37 @3a70ba0
Acceptance (EARS):
- AC-226.1 When the folder holds files `features/<area>.md` directly in `features/`, the status command shall print
  one Areas line per file, in path order: `<area>: pack <name> <version>, output language <code>`.
  - The pack and output language are the area's profile: its `Target:` line, else section 1's `Pack:` and
    `Output language:` lines, else the built-in `service` pack and the PRD's `language:` (`en` when unset).
  - `<version>` is written `(default)` when no line names a version.
- AC-226.2 If the folder holds no such file, the Areas part shall hold the one line `None.`.
Errors: -
Edge cases: how a profile resolves is the packs area's; status names the pack and never resolves it → AC-226.1
Tests: T-226.1 [integration], T-226.2 [integration], T-226.3 [integration], T-226.4 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-227 The Adoption map part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:49 @3a70ba0
Acceptance (EARS):
- AC-227.1 While the PRD folder has no `adoption.md`, the status command shall print the one Adoption map line
  `Not applicable: new project`.
- AC-227.2 When `adoption.md` holds rows, the status command shall print one line per row, in the map's order:
  `<area> | <state> | <globs>`, where `<globs>` is the row's Boundary globs without their backticks, joined by `, `,
  or `-` when the row names none.
- AC-227.3 If `adoption.md` exists and its table holds no row, the Adoption map part shall hold the one line
  `None.`.
Errors: -
Tests: T-227.1 [integration], T-227.2 [integration], T-227.3 [integration], T-227.4 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-228 The Not built and Not verified parts
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:56 @3a70ba0
Acceptance (EARS):
- AC-228.1 The status command shall list each block whose status is `approved` in the Not built part, in the PRD's
  order (features files by path, then `nfr.md`, each from top to bottom), as `<ID> <title> (<file>)`, where
  `<file>` is the block's path inside the PRD folder. With no such block, the part holds `None.`.
- AC-228.2 The status command shall list each block whose status is `built` in the Not verified part, in the same
  order and form. With no such block, the part holds `None.`.
Errors: -
Tests: T-228.1 [integration], T-228.2 [integration], T-228.3 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-229 The Open errors part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:61 @3a70ba0
Acceptance (EARS):
- AC-229.1 When `errors.md` holds open entries, the status command shall list each one in the ledger's order as
  `<E-id> <state> <class> — <title>`. `<state>` is the entry's state (`unclassified`, `proposed` or
  `confirmed`), and ` <class>` is left out when the class is empty or equals the state. When no entry is open,
  the part holds `None.`.
Errors: -
Edge cases: a resolved entry is not listed → AC-229.1; what makes an entry open, and its state, is the errors area's
Tests: T-229.1 [integration], T-229.2 [integration], T-229.3 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-230 The Upstreams and Consumers parts
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:74 @3a70ba0
  prd-toolkit/scripts/prdlint/status.py:100 @3a70ba0
Acceptance (EARS):
- AC-230.1 While the PRD has no `links.md`, or its Upstreams table has no row, the Upstreams part shall hold the
  one line `None.`. The Consumers part shall do the same for the Consumers table.
- AC-230.2 When an Upstreams row's Location is a git URL, the status command shall print for that row
  `<name> <version> at <commit>, needs <needs>, check: not run (git URL; run prd_links.py check)`.
  `<version>` and `<commit>` are the row's lock, each `-` when empty, and `<needs>` is the Needs cell, or
  `default` when empty. The command shall fetch nothing for that row.
- AC-230.3 When an Upstreams row's Location is a path, the status command shall print the same text, followed by
  `, check: error (<message>)` when the links check of the path rows refuses or cannot run. It shall add nothing
  when the check reports that upstream `unreachable`.
- AC-230.4 When the Consumers table holds rows, the status command shall print one line per row,
  `<name> <location>`, where `<location>` is the Location cell without its backticks.
Errors: -
Edge cases: for a reachable path upstream the line ends `, check: <verdict> <n>, …`, the verdicts sorted and counted, or `, check: no items`; the verdicts are prd_links check's, and the links area's adoption adds their case (the owner's answer to Q-49); a git URL is never fetched, so the report stays offline → AC-230.2
Tests: T-230.1 [integration], T-230.2 [integration], T-230.3 [integration], T-230.4 [integration], T-230.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status; `prd_links.py check`

### FR-231 The Change sets part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:105 @3a70ba0
Acceptance (EARS):
- AC-231.1 When the folder `changes/` holds change-set records whose Status is neither `done` nor `abandoned`,
  the status command shall print one line per record, in file-name order:
  `<CS-id> <status>: <prd> <state>; <prd> <state>`, one `<prd> <state>` pair per member row in the table's
  order. With no such record, the part holds `None.`.
Errors: -
Tests: T-231.1 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status

### FR-232 The CI part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:111 @3a70ba0
Acceptance (EARS):
- AC-232.1 When the PRD folder is inside a git checkout, the status command shall print in the CI part the lines
  that `prd_hooks.py check --ci` prints for stale managed blocks and CI files (AC-111.1, AC-111.2 and AC-068.5,
  with AC-111.3's exception for an ignored `CLAUDE.md`), in that order. With none, the part holds `None.`.
- AC-232.2 If the PRD folder is in no git checkout, the CI part shall hold the one line
  `<folder> is not inside a git checkout`, where `<folder>` is the folder's resolved absolute path.
Errors: -
Tests: T-232.1 [integration], T-232.2 [integration], T-232.3 [integration], T-232.4 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status; FR-111; FR-068

### FR-233 The Deployed part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:145 @3a70ba0
  prd-toolkit/scripts/prdlint/status.py:118 @3a70ba0
Acceptance (EARS):
- AC-233.1 When `operations.md` has a `## Deployed` row for an environment, the status command shall print
  `<env>: <version> at <commit>, <date>` for it. The environments follow the order of `operations.md`
  Environments, then the environments that only Deployed rows name, in row order.
- AC-233.2 When the PRD folder is in a git checkout, the status command shall read this PRD's deploy run logs
  whose run ID sorts after the Run of the environment's Deployed row (all of them when there is no row), newest
  first, and take the first with a `start` or `step` record on that environment. When that log did not finish the
  environment, it shall print `<env>: run <run id> stopped (<state>) at step <N>` after the environment's row line.
  - `<N>` is the step of the log's last `start` or `step` record on the environment.
  - `<state>` is `unfinished` when that record is a `start`, `human` when it is a step whose result is `human`,
    `failed` when the result is `fail`, and `unfinished` otherwise.
  - When that log finished the environment, no line is printed, whatever older logs hold.
- AC-233.3 The status command shall pass over a log that cannot be read, a log whose first record is not a header,
  and a log whose header names another PRD folder, and read the next older log.
- AC-233.4 When no environment has a line, the Deployed part shall hold the one line `None.`.
Errors: -
Edge cases: whether a run finished an environment is the deploy area's rule (`deploy.finished_envs`); a log no newer than the row's run is never read → AC-233.2; in no git checkout no log is read → AC-233.4
Tests: T-233.1 [integration], T-233.2 [integration], T-233.3 [integration], T-233.4 [integration], T-233.5 [integration], T-233.6 [integration], T-233.7 [integration], T-233.8 [integration], T-233.9 [integration], T-233.10 [integration], T-233.11 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status; FR-043

### FR-234 The Matrix part
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/status.py:160 @3a70ba0
Acceptance (EARS):
- AC-234.1 When the PRD holds requirement blocks, the status command shall print one Matrix line per block, in the
  PRD's order: `<ID>: <cell>; <cell>`, one cell per T-id of its `Tests:` line, in that line's order.
  - A cell is `<T-id> <level> <gate> <mark>`.
  - `<gate>` is the level's Gate in `testing.md` Levels, or `-` when the level has no row or no Gate.
  - `<mark>` is `cited` when a file under the test roots holds `@prd <T-id>`, and `missing` otherwise.
  - A block with no T-id prints `<ID>: no tests`.
- AC-234.2 If the PRD holds no requirement block, the Matrix part shall hold the one line `None.`.
Errors: -
Tests: T-234.1 [integration], T-234.2 [integration], T-234.3 [integration], T-234.4 [integration], T-234.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_status; FR-090

### FR-235 The CLAUDE.md block
Status: approved
Source: prd-toolkit/scripts/prd_block.py:110 @3a70ba0
  prd-toolkit/templates/claude-block.md:1 @3a70ba0
  prd-toolkit/scripts/prd_block.py:74 @3a70ba0
  prd-toolkit/scripts/prd_block.py:84 @3a70ba0
Acceptance (EARS):
- AC-235.1 When run on a PRD folder, the block command shall write in `CLAUDE.md` the block of 26 lines that test
  case T-235.1 gives, from the start marker to the end marker, filled in as follows:
  - line 4 names the PRD folder's path from the repository root and the frontmatter `version` (`unknown` when the
    key is missing);
  - line 10 is `- ` and the change line of FR-236;
  - line 18 names the PRD folder's path again;
  - the lines after `Required skills:` are AC-235.2's;
  - the line `Adopted areas: <areas>` holds AC-235.3's areas.

  Every other line is fixed text.
- AC-235.2 The block command shall write under `Required skills:` one line per row of section 6 of `prd.md` whose
  Decision, without backticks, is `required`, in the table's order: `- <skill> for <object>`, where `<skill>` is
  the Skill cell without its backticks, put in a code span, and `<object>` is the Object or activity cell as
  written. With no such row it writes the one line `- none`.
- AC-235.3 Where `adoption.md` exists, the block command shall write as `<areas>` the areas of its rows in state
  `adopted`, in the map's order, joined by `, `, or `none yet` when no row is adopted. Where it does not exist,
  `<areas>` is `all (new project)` when section 8 holds `Not applicable: new project`, and `none yet` otherwise.
- AC-235.4 The block command shall fill each placeholder of the template once, from the template's own text, and
  write each value as it is: a `{{…}}` text inside a value, such as a section 6 Object cell, is never replaced.
Errors: -
Edge cases: the block budget, under 1,792 bytes, is a unit-test check of the template, not a requirement (the owner's answer to Q-48)
Tests: T-235.1 [integration], T-235.2 [integration], T-235.3 [integration], T-235.4 [integration], T-235.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block; FR-104

### FR-236 The block's change line
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_block.py:99 @3a70ba0
Acceptance (EARS):
- AC-236.1 Where the PRD folder has neither `adoption.md` nor `links.md`, the block command shall write as the
  change line the sentence T-236.1 gives, which names `/prd-toolkit:prd-change` and the skill
  `prd-toolkit:changing-prds`.
- AC-236.2 Where the folder has `links.md` and no `adoption.md`, the block command shall write the two lines
  T-236.2 gives. The first ends `before code;` and names no skill. The second, indented two spaces, names
  `/prd-toolkit:prd-change-set`.
- AC-236.3 Where the folder has `adoption.md`, the block command shall write the sentence that starts
  `Every behaviour change in an adopted area starts with` and names `/prd-toolkit:prd-change`. With `links.md`,
  that sentence ends `before code;` and goes on with `one to a cited item, with` and the change-set command. The
  sentence is wrapped at 100 columns, the bullet `- ` counted, with continuation lines indented two spaces and no
  word broken.
Errors: -
Tests: T-236.1 [integration], T-236.2 [integration], T-236.3 [integration], T-236.4 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-237 Where each block goes in its file
Status: approved
Source: prd-toolkit/scripts/prd_block.py:154 @3a70ba0
  prd-toolkit/scripts/prd_block.py:268 @3a70ba0
  prd-toolkit/scripts/prd_block.py:300 @3a70ba0
Acceptance (EARS):
- AC-237.1 When a target file does not exist or is empty, the block command shall write it as the block followed
  by one newline. A run that writes, or finds nothing to write, prints nothing on stdout and exits 0.
- AC-237.2 When `CLAUDE.md` exists and holds no block, the block command shall keep its text byte for byte and add,
  at its end, a newline when the text does not end in one, one empty line, the block and one newline.
- AC-237.3 When the PRD folder's README or the parent README exists and holds no block, the block command shall
  write the block, one empty line and then the file's text, byte for byte.
- AC-237.4 When a target file holds a block, the block command shall replace only the lines from its start marker
  to its end marker. Every byte before and after stays, and so does the end marker line's own line ending (none
  when the file ends at the marker).
- AC-237.5 When every target file already holds what it would write, the block command shall leave each file as
  it is.
Errors: -
Edge cases: a file the command creates takes the mode AC-239.3 gives → AC-237.1
Tests: T-237.1 [integration], T-237.2 [integration], T-237.3 [integration], T-237.4 [integration], T-237.5 [integration], T-237.6 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-238 What counts as a marker
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_block.py:124 @3a70ba0
  prd-toolkit/scripts/prd_block.py:141 @3a70ba0
Acceptance (EARS):
- AC-238.1 The block command shall take as markers only the lines that, without the white space at their ends, are
  `<!-- prd-toolkit:start -->` or `<!-- prd-toolkit:end -->` and that lie outside every closed code fence.
  - A fence opens at a line that starts, after white space, with three or more backticks or tildes.
  - It closes at the next line that holds only that character, at least as many times.
  - A fence that never closes protects nothing.
- AC-238.2 If a target file holds two or more start markers, or two or more end markers, the block command shall
  print `prd_block: <file>: more than one prd-toolkit block` on stderr, write no file and exit 2. `<file>` is the
  file's resolved absolute path.
- AC-238.3 If a target file holds one marker without the other, or its end marker before its start marker, the
  block command shall print `prd_block: <file>: prd-toolkit start and end markers are unbalanced` on stderr, write
  no file and exit 2.
Errors: -
Edge cases: every merge is computed before anything is written, so a bad marker in one file stops the other two → AC-238.2, AC-238.3
Tests: T-238.1 [integration], T-238.2 [integration], T-238.3 [integration], T-238.4 [integration], T-238.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-239 Writing through a link, and keeping the mode
Status: approved
Source: prd-toolkit/scripts/prd_block.py:304 @3a70ba0
  prd-toolkit/scripts/prd_block.py:313 @3a70ba0
Acceptance (EARS):
- AC-239.1 When a target file is a symbolic link, the block command shall write the file the link points to and
  keep the link.
- AC-239.2 When the block command rewrites an existing file, it shall keep that file's permission bits.
- AC-239.3 When the block command creates a target file, it shall give it the mode a new file gets from the
  umask, `0o666 & ~umask`.
Errors: -
Edge cases: an existing file keeps its mode → AC-239.2; a created file takes the umask's → AC-239.3
Tests: T-239.1 [integration], T-239.2 [integration], T-239.3 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-240 The --check option
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_block.py:354 @3a70ba0
  prd-toolkit/scripts/prd_block.py:291 @3a70ba0
Acceptance (EARS):
- AC-240.1 When run with `--check`, the block command shall write nothing, print `stale: <file>` for each target
  file whose text differs from what it would write (a missing file included), and exit 1 when it printed a line,
  0 otherwise.
  - The files come in the order `CLAUDE.md`, the PRD folder's README, the parent README.
  - `<file>` is relative to the repository root, or to the folder of `CLAUDE.md` when the PRD folder is in no git
    checkout, and is written as given when it lies outside that folder.
- AC-240.2 If a target file's markers are broken, the block command run with `--check` shall print the line of
  AC-238.2 or AC-238.3 on stderr, print nothing on stdout and exit 2.
Errors: -
Tests: T-240.1 [integration], T-240.2 [integration], T-240.3 [integration], T-240.4 [integration], T-240.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block; FR-111

### FR-241 The PRD folder's README block
Status: approved
Source: prd-toolkit/scripts/prd_block.py:217 @3a70ba0
  prd-toolkit/templates/readme-prd.md:1 @3a70ba0
Acceptance (EARS):
- AC-241.1 When run, the block command shall write in the PRD folder's `README.md` the block that test case
  T-241.1 gives, filled in as follows:
  - `<slug>`, `<version>`, `<status>`, `<owner>` and `<updated>` come from the frontmatter of `prd.md`, each
    `unknown` when its key is missing;
  - the parent link before the full stop of line 6 is ` (see [../README.md](../README.md) to set it up)` when the
    PRD folder's parent is named `prd`, and empty otherwise;
  - the summary, the areas table, the files table and the links part are AC-241.2 to AC-241.5's.
- AC-241.2 The block command shall write as the summary each line of the summary paragraph (FR-247) after `> `.
  When §2 has no summary paragraph, it writes the one line `_No summary yet: prd.md §2 is empty._`.
- AC-241.3 The block command shall write the areas table as `| Area | Adoption | File |`, `|---|---|---|` and one
  row per file `features/<area>.md`, in path order: `| <area> | <state> | [features/<area>.md](<target>) |`.
  `<state>` is the area's state in `adoption.md`, or `-` when there is none, and `<target>` is the path
  percent-encoded except for `/`, `.`, `-`, `_` and `~`.
- AC-241.4 The block command shall write the files table as `| Path | Holds |`, `|---|---|` and one row for each of
  `prd.md`, `features/`, `test-cases/`, `contracts/`, `testing.md`, `errors.md`, `operations.md`, `nfr.md`,
  `adoption.md` and `links.md` that exists, in that order, with the fixed text T-241.5 gives.
  - `features/` exists when a Markdown file lies under it.
  - `test-cases/` and `contracts/` exist when the folder exists.
- AC-241.5 Where the PRD folder has `links.md`, the block command shall write, between the files table and
  `## Reading and changing it`, these lines: one empty line, `## Linked PRDs`, an empty line, `**Upstreams**`, an
  empty line, one `- <location>` line per Upstreams row (or `- none`), an empty line, `**Consumers**`, an empty
  line, the same for the Consumers rows, and an empty line.
  - A location that holds `://` or `#`, or starts with `git@`, is written in a code span.
  - An empty location is written `-`.
  - Any other location is written as a link `[<path>](<path percent-encoded>)`.

  Where the folder has no `links.md`, one empty line stands there.
- AC-241.6 The block command shall fill each placeholder of the README template once, from the template's own
  text, and write each value as it is: a summary that holds `{{areas}}`, `{{files}}` or `{{links}}` is written
  with that text, word for word.
Errors: -
Edge cases: the README shows no requirement status; lint, the digest and the tester skip it (FR-015) → AC-241.1
Tests: T-241.1 [integration], T-241.2 [integration], T-241.3 [integration], T-241.4 [integration], T-241.5 [integration], T-241.6 [integration], T-241.7 [integration], T-241.8 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block; FR-015; FR-247

### FR-242 The parent README block
Status: approved
Source: prd-toolkit/scripts/prd_block.py:242 @3a70ba0
  prd-toolkit/scripts/prd_block.py:274 @3a70ba0
  prd-toolkit/templates/readme-prds.md:1 @3a70ba0
Acceptance (EARS):
- AC-242.1 Where the PRD folder's parent is named `prd`, the block command shall write in the parent's `README.md`
  the block that test case T-242.1 gives, with its table `| PRD | Version | Status | Covers |`, `|---|---|---|---|`
  and one row per folder of the parent, the PRD's own included, whose name does not start with `.` and that holds
  a file `prd.md`.
  - The rows are sorted by folder name: `| [<name>](<name percent-encoded>/) | <version> | <status> | <covers> |`.
  - `<covers>` is the first sentence (AC-247.2) of that PRD's summary, or `-`.
  - In each cell, runs of white space become one space and `|` is written `\|`.
- AC-242.2 Where the PRD folder's parent is not named `prd`, the block command shall write no parent README.
- AC-242.3 If a sibling folder's PRD cannot be loaded, the block command shall give it the row
  `| <name> | - | could not be read | - |`, print `prd_block: <name>: could not be read (<exception type>: <message>)`
  on stderr, and still exit 0.
- AC-242.4 The block command shall fill each placeholder of the parent template once, from the template's own
  text, and write each value as it is: a Covers cell that holds `{{homepage}}` is written with that text.
Errors: -
Tests: T-242.1 [integration], T-242.2 [integration], T-242.3 [integration], T-242.4 [integration], T-242.5 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-243 The parent README's install line
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_block.py:171 @3a70ba0
  prd-toolkit/scripts/prd_block.py:258 @3a70ba0
Acceptance (EARS):
- AC-243.1 When run from the vendored copy (`.prd-toolkit/prd_block.py`), the block command shall write the
  parent's install line as `- Install the prd-toolkit plugin for Claude Code: <H>`, where `<H>` is the first line
  of `.prd-toolkit/HOMEPAGE` without the white space at its ends. When that file is missing or empty, the line is
  `- Install the prd-toolkit plugin for Claude Code.`, whatever any `plugin.json` holds.
- AC-243.2 When run from the plugin, the block command shall take `<H>` from the plugin's own
  `.claude-plugin/plugin.json`: its `homepage`, without the white space at its ends, when the manifest's `name` is
  `prd-toolkit` and the homepage is a non-empty string. Otherwise the line ends `Claude Code.`.
Errors: -
Tests: T-243.1 [integration], T-243.2 [integration], T-243.3 [integration], T-243.4 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block; FR-107

### FR-244 A marker in §2
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_block.py:219 @3a70ba0
Acceptance (EARS):
- AC-244.1 If section 2 of `prd.md` holds the text `<!-- prd-toolkit:start -->` or `<!-- prd-toolkit:end -->`
  anywhere, inside an HTML comment included, the block command shall print
  `prd_block: prd.md §2 holds a prd-toolkit marker` on stderr, write no file and exit 2.
Errors: -
Tests: T-244.1 [integration], T-244.2 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-245 The block command's refusals
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prd_block.py:337 @3a70ba0
Acceptance (EARS):
- AC-245.1 If the folder holds no file `prd.md`, the block command shall print `prd_block: <folder>: no prd.md` on
  stderr, `<folder>` being the folder's resolved absolute path, write no file and exit 2.
- AC-245.2 If section 8 of `prd.md` holds a table and the folder has no `adoption.md`, the block command, with
  `--check` or without it, shall print
  `prd_block: <folder>/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."`
  on stderr, write no file and exit 2.
- AC-245.3 If no PRD folder is given, the block command shall print the stderr lines
  `usage: prd_block.py [-h] [--claude-md CLAUDE_MD] [--check] prd_dir` and
  `prd_block.py: error: the following arguments are required: prd_dir`, and exit 2.
Errors: -
Tests: T-245.1 [integration], T-245.2 [integration], T-245.3 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-246 Which CLAUDE.md it writes
Status: approved
Source: prd-toolkit/scripts/prd_block.py:351 @3a70ba0
  prd-toolkit/scripts/prd_block.py:268 @3a70ba0
Acceptance (EARS):
- AC-246.1 When run without `--claude-md` on a PRD folder inside a git checkout, the block command shall write the
  block in `CLAUDE.md` at the checkout's root, whatever the working directory, the block naming the PRD folder's
  path from that root.
- AC-246.2 When `--claude-md <file>` is given, the block command shall write the block in that file, creating its
  folder, and leave the root's `CLAUDE.md` as it is. The block still names the PRD folder's path from the root,
  and the two READMEs are written as without the option.
- AC-246.3 If the PRD folder is in no git checkout and `--claude-md` is not given, the block command shall print
  `prd_block: <folder>: not inside a git checkout; name the CLAUDE.md with --claude-md` on stderr, `<folder>`
  being the folder's resolved absolute path, write no file and exit 2.
Errors: -
Edge cases: in no git checkout, `--claude-md` names the file to write → AC-246.2, AC-246.3
Tests: T-246.1 [integration], T-246.2 [integration], T-246.3 [integration]  (test-cases/status.yaml)
Traces: cli:prd_block

### FR-247 §2's summary paragraph and first sentence
Status: approved
Source: prd-toolkit/scripts/prdlint/overview.py:77 @3a70ba0
  prd-toolkit/scripts/prdlint/overview.py:44 @3a70ba0
Acceptance (EARS):
- AC-247.1 The PRD facts shall take as §2's summary the first run of non-blank lines in §2. A line that holds
  nothing but an HTML comment counts as blank. The run ends at a blank line or at a heading line outside code (one
  to six `#` and a space). Each line is kept without its trailing white space. There is no summary when §2 has no
  non-blank line, or when the run's first line starts with `Goals:`, `Personas:`, `Out of scope:`, `Principles:`,
  `Getting started:` or the PRD language's label for one of the last two.
- AC-247.2 The PRD facts shall take as the first sentence the summary with every run of white space written as
  one space, up to and including the first `.`, `?` or `!` followed by white space, or the whole summary when
  there is no such mark. Without a summary, the first sentence is empty.
- AC-247.3 The PRD facts shall remove an HTML comment that stands inside a summary line from that line and keep
  the text on either side of it as written: `Intro <!-- note --> text` gives `Intro  text`.
Errors: -
Edge cases: `v1.2 is out.` keeps `v1.2` whole, since no white space follows its dot → AC-247.2; an HTML comment inside a line is removed → AC-247.3
Tests: T-247.1 [integration], T-247.2 [integration], T-247.3 [integration], T-247.4 [integration], T-247.5 [integration], T-247.6 [integration]  (test-cases/status.yaml)
Traces: code:prdlint.overview.facts; FR-241; FR-242

### FR-248 §2's Principles and Getting started parts
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/overview.py:95 @3a70ba0
Acceptance (EARS):
- AC-248.1 The PRD facts shall take as §2's Principles part the text that starts at the line beginning
  `Principles:` and runs to the line before the next §2 line that begins with a label of AC-247.1, or to §2's end.
  - It is the label line's text after the label, then each following line without its trailing white space.
  - Empty lines at its start and end, and the white space at its ends, are removed.
  - A line inside code or an HTML comment is never a label.
  - The Getting started part is taken the same way from `Getting started:`, and the PRD language's labels for the
    two parts count too.
  - A part whose label is absent, or whose text is empty, is none.
Errors: -
Tests: T-248.1 [integration], T-248.2 [integration]  (test-cases/status.yaml)
Traces: code:prdlint.overview.facts; `prdlint/publish.py`

### FR-249 The areas the PRD facts list
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/overview.py:119 @3a70ba0
  prd-toolkit/scripts/prdlint/overview.py:131 @3a70ba0
Acceptance (EARS):
- AC-249.1 The PRD facts shall list one area per file `features/<area>.md`, in path order, with its file, its state
  in `adoption.md` (`-` when there is none), and the counts of its FR and NFR blocks by the first word of their
  `Status:`, in lower case.
  - Only `live`, `verified`, `built`, `approved` and `as-built` are counted, in that order.
  - A status no block has is left out.
  - UJ blocks and `removed` blocks are not counted.
Errors: -
Tests: T-249.1 [integration], T-249.2 [integration]  (test-cases/status.yaml)
Traces: code:prdlint.overview.facts; `prdlint/publish.py`

### FR-250 The other PRD facts
Status: live (since 9.9.0)
Source: prd-toolkit/scripts/prdlint/overview.py:129 @3a70ba0
Acceptance (EARS):
- AC-250.1 The PRD facts shall give:
  - `prd`, `version`, `status`, `owner` and `updated` from the frontmatter of `prd.md`, each `unknown` when its key
    is missing;
  - the number of open `errors.md` entries;
  - the Location cells of the Upstreams and Consumers rows of `links.md`, as written, backticks included, or two
    empty lists without `links.md`;
  - the paths of AC-241.4 that exist, in that order.
Errors: -
Tests: T-250.1 [integration], T-250.2 [integration]  (test-cases/status.yaml)
Traces: code:prdlint.overview.facts
