<!-- Format: references/prd-format.md, "Requirement blocks". -->

# context: the context pack an agent reads before it decides or implements

### FR-199 The context command refuses a bad command line
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prd_context.py:53 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:44 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:56 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:64 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:67 @f5d2b4c
Acceptance (EARS):
- AC-199.1 If no PRD folder is given and neither `--interface` nor `--help` is given, the context command
  shall print argparse's usage on stderr, its first line starting `usage: prd_context.py`, print nothing on
  stdout and exit 2.
- AC-199.2 If `--context` is given a number below 0, the context command shall print the one stderr line
  `prd_context: --context must be 0 or more`, print nothing on stdout and exit 2, before it reads the folder.
- AC-199.3 If the folder holds no file named `prd.md`, the context command shall print the one stderr line
  `prd_context: <the folder, resolved>: no prd.md`, print nothing on stdout and exit 2.
- AC-199.4 If argparse refuses an argument (an option it does not know, or a `--for` value other than
  `decide` and `implement`), the context command shall print argparse's usage and a last stderr line that
  starts `prd_context.py: error: `, print nothing on stdout and exit 2.
- AC-199.5 If reading the PRD folder or building the pack raises an error the command does not expect, the
  context command shall print the one stderr line `prd_context: internal error: <exception type>: <message>`,
  print nothing on stdout and exit 2.
- AC-199.6 When `--help` is given, the context command shall print argparse's help on stdout, its first line
  starting `usage: prd_context.py`, and exit 0.
Errors: -
Edge cases: `--context` is checked in both modes, though only the implement pack reads it → AC-199.2; a file that is not UTF-8 in the PRD folder ends as an internal error → AC-199.5
Tests: T-199.1 [integration], T-199.2 [integration], T-199.3 [integration], T-199.4 [integration], T-199.5 [integration], T-199.6 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-200 The context command's interface number
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prd_context.py:46 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:49 @f5d2b4c
Acceptance (EARS):
- AC-200.1 When `--interface` is given, the context command shall print the one stdout line `1` and exit 0,
  reading no folder and checking no `--json=N`, with or without a folder argument.
- AC-200.2 If `--json=N` is given with N other than `1` and `--interface` is not given, the context command
  shall print the one stderr line `prd_context: unsupported interface <N>; this toolkit speaks 1`, print on
  stdout the one line `{"interface": 1, "kind": "context", "error": "unsupported interface <N>; this toolkit speaks 1"}`
  and exit 2; and `--json=1` shall print what `--json` prints.
Errors: -
Edge cases: `--interface` wins over a `--json=N` → AC-200.1
Tests: T-200.1 [integration], T-200.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-201 Requests the context command refuses
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:486 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:122 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:100 @f5d2b4c
Acceptance (EARS):
- AC-201.1 If `--req` is given without `--area`, the context command shall print the one stderr line
  `prd_context: --req needs --area`, print nothing on stdout and exit 2.
- AC-201.2 If `--for implement` is given without `--area` and without `--req`, the context command shall
  print the one stderr line `prd_context: --for implement needs --area`, print nothing on stdout and exit 2.
- AC-201.3 If the value of `--req`, split on commas with each piece stripped and empty pieces dropped, holds
  no ID, the context command shall print the one stderr line `prd_context: --req names no ID`, print nothing
  on stdout and exit 2, before it checks `--area`.
- AC-201.4 If `--area` names neither an area of an `adoption.md` row nor a file `features/<area>.md`, the
  context command shall print the one stderr line `prd_context: unknown area '<area>'; areas: <areas>`, where
  `<areas>` is the `adoption.md` rows' areas in table order and then each `features/<slug>.md` slug no row
  names, in sorted path order, joined by `, `, or `none` when there are none; print nothing on stdout and
  exit 2.
- AC-201.5 If `--for implement` is given with `--area` and the PRD folder is not inside a git work tree, the
  context command shall print the one stderr line
  `prd_context: --for implement needs the PRD inside a git work tree`, print nothing on stdout and exit 2.
- AC-201.6 If `--req` names IDs that no requirement block defines, or `E-nnn` IDs that `errors.md` does not
  record, the context command shall print one stderr line: `prd_context: no requirement block defines <IDs>`,
  the IDs in `--req` order joined by `, `, followed for each of them that is an AC or T ID (`AC-<n>.<n>`,
  `T-<n>.<n>`) by `; pass the requirement ID (<owners>), not <ID>`, `<owners>` being the blocks whose
  acceptance criteria or `Tests:` line name it, joined by `, `, or `UJ-, FR- or NFR-nnn` when none does; then
  `; errors.md has no entry <E-IDs>` (without the leading `; ` when no block ID is unknown); print nothing on
  stdout and exit 2.
- AC-201.7 If section 8 of `prd.md` holds a table and the folder holds no `adoption.md`, the context command
  shall print the one stderr line
  `prd_context: <the folder, resolved>/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; move the table there and leave "See adoption.md."`,
  print nothing on stdout and exit 2, before any other check of the request.
Errors: -
Edge cases: the checks run in the order AC-201.7, AC-201.3, AC-201.1, AC-201.2, AC-201.4, AC-201.5, AC-201.6; an area with an `adoption.md` row and no features file is known → AC-201.4; IDs are compared in upper case, so `fr-001` names FR-001 → AC-201.6
Tests: T-201.1 [integration], T-201.2 [integration], T-201.3 [integration], T-201.4 [integration], T-201.5 [integration], T-201.6 [integration], T-201.7 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-202 The JSON error document of the context command
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prd_context.py:30 @f5d2b4c
Acceptance (EARS):
- AC-202.1 When `--json` is given and the context command exits 2, it shall print on stdout the one line
  `{"interface": 1, "kind": "context", "error": <message>}`, `<message>` being its stderr line less the
  prefix `prd_context: `, or for an argparse refusal its `prd_context.py: error: ` line less that prefix,
  and keep its stderr text.
Errors: -
Edge cases: every exit-2 path of FR-199, FR-200 and FR-201 behaves the same way with `--json` → AC-202.1
Tests: T-202.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-203 The repository pack
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:495 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:273 @f5d2b4c
Acceptance (EARS):
- AC-203.1 When run without `--area`, `--req` and `--for implement`, the context command shall print the
  parts Header, Stack and Areas, in that order and no other, the Header part holding the two lines
  `PRD: <folder> version <version> mode decide` and
  `pack <n> bytes (~<k>k tokens, bytes / 4); prd.md <size>`, and exit 0.
- AC-203.2 Where the PRD folder holds `adoption.md`, the context command shall print in the repository
  pack's Areas part one line per row of its table, in table order, `- <area> (<state>; Boundary: <globs>)`,
  `<globs>` being the row's backticked Boundary globs without backticks, joined by `, `, or
  `- <area> (<state>)` for a row whose Boundary cell holds no backticked glob, with no empty line between the
  lines, and the one line `None.` when the table has no row.
- AC-203.3 Where the PRD folder holds no `adoption.md`, the context command shall print in the repository
  pack's Areas part one line `- <slug>` per file `features/<slug>.md`, in sorted path order.
Errors: -
Edge cases: a features file that no row names is not listed when `adoption.md` exists → AC-203.2
Tests: T-203.1 [integration], T-203.2 [integration], T-203.3 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-204 The Header part of an area pack
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:283 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:298 @f5d2b4c
Acceptance (EARS):
- AC-204.1 When run with `--area`, the context command shall print the Header part as the four lines
  `PRD: <folder> version <version> mode <mode>`, `Area: <area> (<row>)`, the profile line
  `Target: pack <name> <X.Y.Z> (<source>), output language <code>` (or
  `Target: pack service (default), output language <code>` for an area that names no pack and a PRD whose
  section 1 names none), and the size line; `<row>` being `<state>; Boundary: <globs>` for an `adoption.md`
  row with a Boundary glob, `<state>` for a row with none, and `-` when no row names the area; `<folder>`
  being the PRD folder resolved, written relative to the working directory when it lies under it and as an
  absolute path otherwise.
- AC-204.2 The context command shall write the size line as
  `pack <n> bytes (~<k>k tokens, bytes / 4); prd.md <p>`, followed by `; features/<area>.md <f>` when that
  file exists, where `<n>` is the number of UTF-8 bytes of the text pack from its line `## Stack` to its end
  (the Header part, which holds the size line, is not counted),
  `<k>` is n / 4 / 1000 written with one decimal, `<p>` and `<f>` are the sizes of those files in bytes, and
  `<n>`, `<p>` and `<f>` are written with a comma between thousands.
Errors: -
Edge cases: the size line counts every part but Header, so it does not count itself → AC-204.2; with `--json` the Header text is the same → AC-204.2
Tests: T-204.1 [integration], T-204.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-205 The Stack part
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:147 @f5d2b4c
Acceptance (EARS):
- AC-205.1 The context command shall print in the Stack part of every pack section 1 and then section 4 of
  `prd.md`, each as one item: its heading line with one more `#` (`### 1. Metadata & stack`), then its body
  lines as written up to the next level-2 heading, trailing empty lines removed; and the one item `None.`
  when `prd.md` holds neither section.
Errors: -
Edge cases: a section that is missing is left out and the other one printed → AC-205.1
Tests: T-205.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-206 Which blocks an area pack selects
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:122 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:59 @f5d2b4c
Acceptance (EARS):
- AC-206.1 When run with `--area` and without `--req`, the context command shall select every UJ and FR
  block of `features/<area>.md`, in file order.
- AC-206.2 When run with `--area` and `--req`, the context command shall select each block that `--req`
  names, from any features file or `nfr.md`, and each UJ that a `Traces:` line of a named block names and a
  block defines, each block once, in the order the PRD's files are read (the features files in sorted path
  order, then `nfr.md`) and in file order within a file; `--req` IDs being upper-cased and stripped of the
  white space around each comma.
Errors: -
Edge cases: a UJ that `Traces:` names and no block defines is skipped → AC-206.2; an ID that two blocks define selects the first one → AC-206.2
Tests: T-206.1 [integration], T-206.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-207 An errors.md entry in --req
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:106 @f5d2b4c
Acceptance (EARS):
- AC-207.1 When `--req` names an `E-nnn` that `errors.md` records, the context command shall select each
  block that the entry's `Touches:` line names and a block defines, and the block owning each test case
  whose `known-failing:` is that entry (the block holding the case's `ac:`, else the FR or NFR block whose
  number is the T-id's number), plus the UJs they trace (AC-206.2), and shall print the whole entry in Known
  defects whether it is open or resolved.
Errors: -
Edge cases: an entry that reaches no block selects none, so Requirements holds `None.` → AC-208.1
Tests: T-207.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context; FR-062

### FR-208 The Requirements part
Status: approved
Source: prd-toolkit/scripts/prdlint/context.py:87 @f5d2b4c
Acceptance (EARS):
- AC-208.1 The context command shall print each selected block as one item of the Requirements part: its
  heading line as written, with ` (area: <other>)` added for a block of `features/<other>.md` whose `<other>`
  is not the asked area, then every line of the block up to the next heading, trailing empty lines removed;
  and the one item `None.` when no block is selected.
Errors: -
Edge cases: a block of `nfr.md` takes no area label → AC-208.1
Tests: T-208.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-209 The Glossary part
Status: approved
Source: prd-toolkit/scripts/prdlint/context.py:157 @f5d2b4c
Acceptance (EARS):
- AC-209.1 The context command shall print in the Glossary part one item: the header and separator lines of
  the first table of section 3 of `prd.md` and each of its rows whose Term (the first cell, backticks removed)
  occurs in the selected blocks' own text, each block's heading line as written and its lines, never in the
  ` (area: <other>)` label AC-208.1 adds to a block of another area, case-insensitive, with no letter, digit,
  `_` or `-` directly before or after it, in table order; and the one item `None.` when no row matches or the
  table has no row.
Errors: -
Edge cases: a Term that only the ` (area: <other>)` label holds is not printed (E-067) → AC-209.1
Tests: T-209.1 [integration], T-209.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context; E-067

### FR-210 The Cited part
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:168 @f5d2b4c
Acceptance (EARS):
- AC-210.1 The context command shall print in the Cited part, first, the text of each NFR block (as
  AC-208.1 writes a block) whose ID the selected blocks' text names, with no letter, digit, `_` or `-`
  directly before or after it, and that is not itself selected, in file order; then the items of AC-210.2,
  AC-210.3, AC-210.5 and AC-210.4, in that order.
- AC-210.2 The context command shall print, for each code on a selected block's `Errors:` line that
  `contracts/errors.yaml` holds, in that file's order, the item `<CODE>:` followed by its fields, written as
  YAML in block style in file order and indented two spaces; then, sorted, the item
  `<CODE>: not in contracts/errors.yaml` for each such code the file does not hold.
- AC-210.3 The context command shall print, for each `<type>:<name>` the selected blocks' text holds (`<name>`
  with a trailing `.` or `:` removed), whose `<type>` is a section 7 row with a Validator other than
  `built-in` and whose `<name>` is a top-level key of a YAML file that row's Files glob matches, the item
  `<name>:` followed by its value, written as YAML in block style, each item once.
- AC-210.4 The context command shall print, for each `[ASSUMPTION A-nn:` marker in the selected blocks' text,
  the header and separator lines of the section 12 table and the row whose ID is `A-nn`, as one item per ID.
- AC-210.5 When a test case listed on a selected block's `Tests:` line has a `target:` whose kind is a target
  kind of a resolved pack, the context command shall treat that target as `<contract type>:<name>` for
  AC-210.3, the contract type being the one the pack maps that kind to.
- AC-210.6 If nothing meets AC-210.1 to AC-210.5, the context command shall print the Cited part with the one
  item `None.`.
Errors: -
Edge cases: `Errors: -` cites no code → AC-210.6
Tests: T-210.1 [integration], T-210.2 [integration], T-210.3 [integration], T-210.4 [integration], T-210.5 [integration], T-210.6 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-211 The Upstream contracts part
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:216 @f5d2b4c
Acceptance (EARS):
- AC-211.1 Where the PRD folder holds no `links.md`, the context command shall print no Upstream contracts
  part.
- AC-211.2 Where the PRD folder holds `links.md`, the context command shall print, directly after the Cited
  part, the part Upstream contracts: one item per upstream reference `<kind>:<prd>/<name>` that a selected
  block, one of its AC IDs or one of its T-ids cites, or whose text as written the selected blocks' text
  holds, each label once, holding the item's snapshot text or, when the snapshot holds none,
  `<kind>:<prd>/<name>: not in the snapshot`; and the one item `None.` when there is none.
Errors: -
Edge cases: which references count as citations is the links area's (`prdlint/citations.py`) → AC-211.2
Tests: T-211.1 [integration], T-211.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-212 The Known defects part
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:235 @f5d2b4c
Acceptance (EARS):
- AC-212.1 The context command shall print in the Known defects part, in `errors.md` order, each entry that
  `--req` names and each open entry whose `Touches:` line names a selected block's ID, each whole (its
  heading line to the line before the next heading, trailing empty lines removed), then the item
  `<n> open errors.md entries name no requirement`, `<n>` being the number of open entries that name no ID on
  a `Touches:` line and that the part does not print, the line written the same way for every `<n>`, 1
  included.
Errors: -
Edge cases: `Touches: -` names no ID, so its open entry is counted → AC-212.1; an open entry that names only unselected IDs is neither printed nor counted → AC-212.1; a resolved entry is printed only when `--req` names it → AC-212.1, AC-207.1
Tests: T-212.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-213 The Open questions part
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:247 @f5d2b4c
Acceptance (EARS):
- AC-213.1 The context command shall take as a question of section 13 of `prd.md` each line that starts with
  `- `, together with the non-empty lines directly after it that start with a space or a tab, and shall
  print in the Open questions part, in order, each question that holds a selected block's ID, an AC ID of a
  selected block or the area's slug, each with no letter, digit, `_` or `-` directly before or after it
  (case-sensitive), then the item `<n> other open questions in prd.md §13`, `<n>` being the number of
  questions not printed, the line written the same way for every `<n>`, 1 included.
Errors: -
Edge cases: `None.` in section 13 is no question, so the count is 0 → AC-213.1; a line that starts with neither `- ` nor white space belongs to no question → AC-213.1
Tests: T-213.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-214 The History part
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:261 @f5d2b4c
Acceptance (EARS):
- AC-214.1 The context command shall print in the History part one item: the header and separator lines of
  the first table of section 14 of `prd.md` and the last three of its rows whose line holds the area's slug
  with no letter, digit, `_` or `-` directly before or after it (case-sensitive), in table order; and the
  one item `None.` when no row holds it.
Errors: -
Edge cases: a row for `import-tools` is not a row for `import` → AC-214.1
Tests: T-214.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-215 The Code part of the implement pack
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:417 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:394 @f5d2b4c
Acceptance (EARS):
- AC-215.1 When run with `--for implement`, the context command shall print in the Code part, for each
  `<path>:<line> @<sha>` (`<sha>` 4 to 40 hexadecimal digits) on a selected block's `Source:` line or its
  continuation lines, one item: the line `### <path>:<line> @<sha>`, the state line FR-216 gives when there
  is one, and the lines `c − N` to `c + N` of the file as it is now at the repository root, limited to the
  file's lines, each written as its number right-aligned in five columns, two spaces and the line's text,
  `c` being the line it moved to (AC-216.2) or else `<line>`, and `N` the value of `--context` (20 when
  none is given); with no file lines when the file is missing.
- AC-215.2 If a selected block's `Source:` value holds no `<path>:<line> @<sha>`, the context command shall
  print in the Code part the item `### <ID> Source: <value>` followed by the line
  `STALE: Source not in <path>:<line> @<sha> form`, and count it as stale.
- AC-215.3 The context command shall print one item per distinct `<path>:<line> @<sha>` of the selected
  blocks, at the place of the first block counted for the exit (FR-217) that cites it, else of the first block
  that cites it; and the one item `None.` when no selected block has a `Source:` line.
Errors: -
Edge cases: the decide pack has no Code part → AC-220.1; a path outside the repository reads as a missing file → AC-215.1
Tests: T-215.1 [integration], T-215.2 [integration], T-215.3 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-216 How a cited source line stands
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:359 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:341 @f5d2b4c
Acceptance (EARS):
- AC-216.1 When the text of `<path>` line `<line>` in commit `<sha>`, white space stripped, is not empty and
  equals the stripped text of that line of the file now, the context command shall print the item with no
  state line and not count it as stale.
- AC-216.2 When that text is not at line `<line>` now and equals the stripped text of exactly one other line
  `<M>` of the file now, the context command shall print the state line `MOVED: line <line> is now line <M>`
  and not count the item as stale.
- AC-216.3 If `<sha>` names no commit, the file is missing, the file is not in `<sha>`, `<line>` is 0 or past
  the end of the file in `<sha>`, or the line's text is at no line or at more than one line of the file now, the
  context command shall print the state line `STALE: <reason>`, `<reason>` being in turn
  `unknown commit <sha>`, `file missing`, `<path> is not in <sha>`,
  `line <line> is past the end (<count> lines)`, `the cited line's text is gone` or
  `the cited line's text appears <count> times`, and count the item as stale.
- AC-216.4 When the cited line in `<sha>` is empty once white space is stripped, the context command shall
  print `STALE: changed since <sha>; the cited line may have moved` when a commit after `<sha>` up to HEAD
  changed the file, else `STALE: uncommitted changes; the cited line may have moved` when the file differs
  from HEAD, and `STALE: cannot compare with <sha>; the cited line may have moved` when git cannot list the
  file's commits after `<sha>` or compare the file with HEAD, counting each of the three as stale, and no
  state line otherwise.
Errors: -
Edge cases: git that cannot run or compare gives `cannot compare with <sha>` → AC-216.4; a `Source:` line number of 0 is past the end → AC-216.3; an uncommitted edit elsewhere in the file leaves a non-empty cited line current → AC-216.1
Tests: T-216.1 [integration], T-216.2 [integration], T-216.3 [integration], T-216.4 [integration], T-216.5 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-217 The exit code counts the blocks asked for
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prd_context.py:71 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:408 @f5d2b4c
Acceptance (EARS):
- AC-217.1 When the pack is printed, the context command shall exit 1 if the Code part holds a stale item of
  a block counted for the exit, and exit 0 otherwise, printing the whole pack in both cases; so the decide
  pack always exits 0.
- AC-217.2 The context command shall count for the exit every selected block when `--req` is not given, and
  with `--req` the blocks it names and the blocks an `E-nnn` it names reaches (AC-207.1); for a stale item of
  a block not counted, the context command shall add ` (pulled in; not counted)` to the end of its `STALE:`
  line.
Errors: -
Edge cases: a UJ selected only through `Traces:` is not counted → AC-217.2
Tests: T-217.1 [integration], T-217.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-218 The Levels part of the implement pack
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:468 @f5d2b4c
Acceptance (EARS):
- AC-218.1 When run with `--for implement`, the context command shall print in the Levels part one item: the
  header line, the separator line and every row of the first table under the `## Levels` heading of
  `testing.md` (the title compared case-insensitively), as written; and the one item `None.` when
  `testing.md`, that heading or a row of that table is missing.
Errors: -
Edge cases: -
Tests: T-218.1 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-219 The Harness defaults and Rubric conventions parts
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:306 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:317 @f5d2b4c
Acceptance (EARS):
- AC-219.1 When run with `--for implement` on an area whose pack resolves and declares `harness` slots, the
  context command shall print, after the Levels part, the part Harness defaults with one item: one line
  `- **<slot>.** <text>` per slot, in the pack's order.
- AC-219.2 When run with `--for implement` on an area whose pack resolves and names a `rubrics` file it can
  read, and `test-cases/<area>.yaml` holds a judged case, the context command shall print, after the Levels
  and Harness defaults parts and before the Cited part, the part Rubric conventions with one item: that
  file's text with its trailing newlines removed.
- AC-219.3 If the area's pack declares no harness, or it names no rubrics file or the area has no judged case,
  the context command shall print no Harness defaults part, or no Rubric conventions part.
Errors: -
Edge cases: the built-in service pack, the default, declares neither → AC-219.3; a pack that does not resolve gives neither part
Tests: T-219.1 [integration], T-219.2 [integration], T-219.3 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context; AC-060.7

### FR-220 The parts' order and the text pack
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:517 @f5d2b4c
  prd-toolkit/scripts/prdlint/context.py:522 @f5d2b4c
Acceptance (EARS):
- AC-220.1 When run with `--area`, the context command shall print the parts in the order Header, Stack,
  Glossary, Area notes, Requirements, then with `--for implement` only Code, Practices, Levels, Harness
  defaults and Rubric conventions, then Cited, Upstream contracts, Known defects, Open questions and History,
  leaving out a part that FR-072, FR-055, FR-211 or FR-219 leaves out; and `--for decide` and no `--for` shall
  print the same pack.
- AC-220.2 The context command shall print each part as the line `## <part>`, one empty line and its items,
  separated by one empty line (in the Areas part by none), with one empty line before the next part's heading
  and one newline at the end of stdout.
Errors: -
Edge cases: -
Tests: T-220.1 [integration], T-220.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context

### FR-221 The JSON context document
Status: live (since 9.8.0)
Source: prd-toolkit/scripts/prdlint/context.py:532 @f5d2b4c
  prd-toolkit/scripts/prd_context.py:70 @f5d2b4c
Acceptance (EARS):
- AC-221.1 When `--json` is given and the pack is built, the context command shall print one stdout line, a
  JSON object whose keys are, in order, `interface` (1), `kind` (`context`), `prd` (the frontmatter `prd:`),
  `mode`, `area` (null without `--area`), `ids` (the `--req` IDs as normalised, in their order, or an empty
  list) and `parts`, a list of one entry per item of the text pack in its order, each with the keys `title`,
  `id`, `file`, `line`, `text`, `stale`, `counted` and `moved`, in that order; and exit as the text pack does.
- AC-221.2 The context command shall give a Requirements entry the block's ID, its file and its heading line;
  a Stack entry the file `prd.md` and the section's heading line; a Glossary, Levels or History table entry
  the line of the table's header; a Cited error-code entry the code, `contracts/errors.yaml` and the code's
  line; a Code entry the block's ID, the cited path and line, `stale`, `counted` and, for a moved line, `moved`
  the line it moved to; a `None.` item or a count line the id null and the line null; every other entry
  `stale` false, `counted` true and `moved` null.
Errors: -
Edge cases: the Header entry's text is the text pack's Header item → AC-221.1
Tests: T-221.1 [integration], T-221.2 [integration]  (test-cases/context.yaml)
Traces: cli:prd_context
