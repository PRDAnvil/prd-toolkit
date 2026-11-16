<!-- Format: references/prd-format.md, "Requirement blocks". -->

# practices: best-practice sources and practices

A PRD may hold `practices.md`, beside `prd.md`: where a platform's good practice comes from, and the
practices taken from it. It holds two tables. `## Sources` has the columns ID (`S-nn`: `S-` and two
digits, never reused), Title (the source's name), Location (a URL, or a path inside the repository, in
backticks), Covers (what it is a source for: a platform, a language, a tool or an activity), Read (the
date its content was read, `YYYY-MM-DD`) and Decision (`approved`, `declined` or `proposed`).
`## Practices` has the columns ID (`P-nn`: `P-` and two digits, never reused), Source (the `S-nn` it was
taken from), Object (glob) (the files it applies to, in backticks, a glob as a section 5 row's; `-` for
a practice about the PRD itself), Applies to (`code` or `prd`) and Practice (one sentence a reader can
answer yes or no to). A rule a linter can check is a section 5 row instead, which names its source by
writing the `S-nn` in its Rules live in cell. The loader is `prd-toolkit/scripts/prdlint/practices.py`,
the lint rule `prdlint/rules/practices.py`, and the command `prd-toolkit/scripts/prd_practices.py`, run
through the launcher as `prd practices`. The same build makes the edits this area needs in
`prd change ids next` (`prdlint/change.py`), the implement context pack (`prdlint/context.py`) and the
pack manifest (`prdlint/packs.py`), which sit in areas that are not adopted; what those edits do is
stated here. How the skill `/prd-toolkit:prd-practices` proposes sources, practices and skills is not
specified in this PRD.

### UJ-04 An owner records where good practice comes from, and a builder is given the practices that apply
Status: verified
Source: prd-toolkit/scripts/prd_practices.py:1 @5d03191
Flow: 1. take each new ID from `prd change ids next docs/prd/<slug> S` or `… P` and write the row in `practices.md`
      → 2. run `prd lint` and fix what the rule `practices` reports
      → 3. run `prd practices docs/prd/<slug>` to read the record, or add `--paths` and the files a change touches
      → 4. a build's implement context pack holds the Practices part: the `code` practices whose glob matches a file of the area
      → 5. a program runs `prd practices --json` and reads the two lists
Traces: FR-048, FR-049, FR-050, FR-051, FR-052, FR-053, FR-054, FR-055, FR-056

### FR-048 Read the sources and practices of practices.md
Status: verified
Source: prd-toolkit/scripts/prdlint/practices.py:1 @5d03191
Acceptance (EARS):
- AC-048.1 If the PRD folder holds no regular file named exactly `practices.md` directly in it, the
  practices loader shall return no source and no practice, and shall not read a `practices.md` in a
  subfolder of the PRD folder as the record.
- AC-048.2 When the PRD folder holds `practices.md`, the practices loader shall read as the sources the
  rows of the first pipe table in the section under the level-2 heading `## Sources`, and as the
  practices the rows of the first pipe table in the section under the level-2 heading `## Practices`,
  each row after the table's separator line, in file order and with its line number in the file;
  where a heading or its table is missing it shall read no row of that kind, and it shall not check a
  table's header row.
- AC-048.3 The practices loader shall read a row's cells by position, a source's as ID, Title, Location,
  Covers, Read and Decision and a practice's as ID, Source, Object (glob), Applies to and Practice,
  splitting the row as section 5's rows are split (a `|` inside backticks does not end a cell); it
  shall remove each cell's surrounding whitespace, read a missing cell as the empty string, ignore every
  cell after the last of its kind, and remove every backtick from a source's ID, Location, Read and
  Decision cells and from a practice's ID, Source, Object (glob) and Applies to cells, keeping the
  Title, Covers and Practice cells as written.
Errors: -
Edge cases: what each value must be (the ID forms, the Decision values, the date, `code` or `prd`, a glob for a `code` practice) is the lint rule's to report, never the loader's: the loader reads a malformed cell as written → FR-049; a `practices.md` that is not a regular file is reported by the loader as any `.md` entry is (AC-006.3) and holds no row → AC-048.1; a `practices.md` that is not valid UTF-8 is an internal error, as any `.md` file of the folder is (AC-006.1) → AC-052.3; the rules that read every Markdown file of the folder (`placeholder`, `vague-word`, `markers-open`, `assumption-indexed`) read `practices.md` as they read it before this area
Tests: T-048.1 [integration], T-048.2 [integration], T-048.3 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_practices; `prdlint/practices.py`

### FR-049 The lint rule practices
Status: verified
Source: prd-toolkit/scripts/prdlint/rules/practices.py:1 @5d03191
Flow: 1. load the folder → 2. read `practices.md` with the practices loader (FR-048)
      → 3. check each source row, each practice row and each section 5 row → 4. report each fault at its row's line
Acceptance (EARS):
- AC-049.1 When a source's ID is not `S-` followed by exactly two digits, the lint command shall report
  `practices` at the source's row in `practices.md` with `source ID '<id>' is not S- and two digits`;
  and when a practice's ID is not `P-` followed by exactly two digits, it shall report `practices` at
  the practice's row with `practice ID '<id>' is not P- and two digits`.
- AC-049.2 When a source's ID, or a practice's ID, equals the ID of an earlier row of the same table, the
  lint command shall report `practices` at the later row with
  `<id> is already defined at practices.md:<line>`, where `<line>` is the line of the first row with
  that ID.
- AC-049.3 When a source's Decision is not `approved`, `declined` or `proposed`, the lint command shall
  report `practices` at its row with
  `source <id>: Decision '<decision>' is not one of approved, declined, proposed`.
- AC-049.4 While the `status` in the frontmatter of `prd.md` is `Approved`, the lint command shall report
  `practices` at the row of each source whose Decision is `proposed`, with
  `source <id> is still 'proposed' but the PRD is Approved`.
- AC-049.5 When a practice's Source names no source of the Sources table, the lint command shall report
  `practices` at the practice's row with `practice <id>: source '<source>' is not in the Sources table`;
  and when it names a source whose Decision is not `approved`, except a `proposed` source while the
  PRD's `status` is not `Approved`, it shall report `practices` at the practice's row with
  `practice <id>: source <source> is '<decision>', not approved`, the source being the first row of the
  Sources table with that ID.
- AC-049.6 When a practice's Applies to is not `code` or `prd`, the lint command shall report `practices`
  at its row with `practice <id>: Applies to '<value>' is not code or prd`.
- AC-049.7 When a practice's Applies to is `code` and its Object (glob) is empty or `-`, the lint command
  shall report `practices` at its row with `practice <id>: a code practice needs a glob in Object (glob)`.
- AC-049.8 When a source's Read is not a date written `YYYY-MM-DD` in the digits 0 to 9 that names a day
  of the calendar, the lint command shall report `practices` at its row with
  `source <id>: Read '<read>' is not a date YYYY-MM-DD`.
- AC-049.9 When the PRD folder holds `practices.md` and the Rules live in cell (the third cell) of a
  section 5 row names an ID `S-` followed by two digits that is not part of a longer word (`CS-01`
  names none), the lint command shall report `practices` at that row of `prd.md`, once for each such ID
  in the order the cell first names them, with `standards row names <S-id>, which is not in practices.md`
  when the ID is no source of the Sources table, and with
  `standards row names <S-id>, which is '<decision>' in practices.md, not approved` when the source's
  Decision is not `approved`, except a `proposed` source while the PRD's `status` is not `Approved`.
- AC-049.10 The lint command shall register the rule `practices` with the severity `error`, and shall
  report no `practices` finding for a PRD folder that holds no `practices.md`, whatever its section 5
  rows name, nor for a row that passes the checks of AC-049.1 to AC-049.9, whether or not a `code`
  practice's glob matches any file.
Errors: -
Edge cases: the checks of one row are reported in the order of the criteria, which lint's sort by file, line and rule keeps → AC-001.3; a malformed ID is still checked by the other criteria under the ID as written → AC-049.1; a practice whose source is `proposed` passes while the PRD is Draft or In review, so one change can propose a source and its practices together, and on an Approved PRD the source fails AC-049.4 and each practice that cites it AC-049.5; a glob that matches no file is not a fault, since a spec-first area's files do not exist yet and section 5 does not check its globs either → AC-049.10; a `prd` practice's Object (glob) is not checked (it is `-` by convention), nor is an empty Practice cell, nor is a Location read or fetched; no check prints a traceback: a malformed row is a finding → AC-049.1 to AC-049.9; the rule's description is the help catalogue's to print (FR-038)
Tests: T-049.1 [integration], T-049.2 [integration], T-049.3 [integration], T-049.4 [integration], T-049.5 [integration], T-049.6 [integration], T-049.7 [integration], T-049.8 [integration], T-049.9 [integration], T-049.10 [integration], T-049.11 [integration], T-049.12 [integration], T-049.13 [integration], T-049.14 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_lint; `prdlint/rules/practices.py`

### FR-050 List the sources and practices
Status: verified
Source: prd-toolkit/scripts/prd_practices.py:47 @5d03191
Acceptance (EARS):
- AC-050.1 When run on a PRD folder with no option, the practices command shall print one line per
  source, in the Sources table's order, `<id> (<decision>, read <read>): <title>, <location>; covers <covers>`,
  then one line per practice, in the Practices table's order,
  `<id> (<source>, <applies to>, <glob>): <practice>`, each value as the practices loader reads it
  (FR-048), and shall exit 0 with nothing on stderr; with no source and no practice it shall print
  nothing.
- AC-050.2 When run with `--paths` and one or more paths, the practices command shall print, in the form
  and order of AC-050.1 and with no source line, only the practices whose Applies to is `code` and whose
  Object (glob) matches one or more of the paths, each once, and shall exit 0 with nothing on stderr;
  a path matches a glob as the pre-commit hook matches a staged file against a section 5 row's glob:
  the whole path, as written, against the glob read as a pattern in which `**/` stands for zero or more
  folders, `**` for any characters, `*` for any characters but `/`, `?` for one character but `/`, and
  every other character for itself, case included.
Errors: -
Edge cases: every row is listed, a declined source and a row lint reports included, since listing is not checking → AC-050.1; a path is compared as written, relative to the repository root as a section 5 glob is, so `./src/a.py` and `src/a.py` are different paths → AC-050.2; a `prd` practice is never printed with `--paths`, whatever its glob → AC-050.2; `--paths` takes every argument after it, so the folder comes first (`prd practices docs/prd/<slug> --paths src/a.py`)
Tests: T-050.1 [integration], T-050.2 [integration], T-050.3 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_practices; `prdlint/trace.py` glob_re (the section 5 glob matching)

### FR-051 Print the record as one JSON document
Status: verified
Source: prd-toolkit/scripts/prd_practices.py:34 @5d03191
Acceptance (EARS):
- AC-051.1 When run with `--json`, the practices command shall print on stdout one JSON object on one
  line, ending in a newline, and nothing else,
  `{"interface": 1, "kind": "practices", "sources": [<source>, …], "practices": [<practice>, …]}`,
  its keys in that order, where each `<source>` is
  `{"id": <ID>, "title": <Title>, "location": <Location>, "covers": <Covers>, "read": <Read>, "decision": <Decision>, "line": <line>}`
  and each `<practice>` is
  `{"id": <ID>, "source": <Source>, "glob": <Object (glob)>, "applies_to": <Applies to>, "practice": <Practice>, "line": <line>}`,
  keys in those orders, each cell value the string the practices loader reads (FR-048) and `<line>` the
  row's line number in `practices.md`, the rows in the tables' order; text outside ASCII is written as
  itself in UTF-8, never as a `\u` escape; and shall exit 0 with nothing on stderr; with no source and
  no practice the two lists are empty.
- AC-051.2 When `--json` is given with `--paths`, the practices command shall print the AC-051.1 document
  with `practices` holding only the practices AC-050.2 prints, in its order, and `sources` whole.
- AC-051.3 When the command line holds `--json=1`, the practices command shall behave as with `--json`.
- AC-051.4 When run with `--interface`, the practices command shall print `1` on one stdout line and exit
  0, whatever other arguments are given, no folder included, without reading the folder and without
  checking a `--json=<N>`.
Errors: -
Edge cases: a value is a string even when it reads as a date (`"read": "2026-11-01"`), and a `prd` practice's glob is the string `-` → AC-051.1; the interface number is 1, as for every interface script, and the document is new, so no existing document changes
Tests: T-051.1 [integration], T-051.2 [integration], T-051.3 [integration], T-051.4 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_practices; `prdlint/interface.py`

### FR-052 Refuse what it cannot read
Status: verified
Source: prd-toolkit/scripts/prd_practices.py:39 @5d03191
Acceptance (EARS):
- AC-052.1 If the folder argument names no directory, or a directory with no regular file named exactly
  `prd.md`, the practices command shall print one stderr line, `prd_practices: ` followed by the text
  the lint command prints after `prd_lint: ` in that case (AC-005.1 to AC-005.3), print nothing on
  stdout and exit 2.
- AC-052.2 If the command line names no folder and holds no `--interface`, or holds an option the
  practices command does not have, a second positional argument, or `--paths` with no path, the
  practices command shall print on stderr the usage line
  `usage: prd_practices.py [-h] [--paths PATH [PATH ...]] [--json] [--interface] prd_dir`, on one line
  whatever the terminal width, then `prd_practices.py: error: <argparse's message>`, print nothing on
  stdout and exit 2.
- AC-052.3 If loading the folder raises an error other than a missing `prd.md`, the practices command
  shall print the one stderr line `prd_practices: internal error: <exception type>: <message>`, print
  no traceback and nothing on stdout, and exit 2.
- AC-052.4 If the practices command, run with `--json`, exits 2 by AC-052.1, AC-052.2 or AC-052.3, it shall
  print on stdout one JSON object on one line, ending in a newline,
  `{"interface": 1, "kind": "practices", "error": <message>}`, where `<message>` is argparse's message
  (the text after `prd_practices.py: error: `) for AC-052.2 and otherwise the stderr line without its
  `prd_practices: ` prefix, and shall print its stderr lines as it does without `--json`.
- AC-052.5 If the command line holds `--json=<N>` with any `<N>` other than `1` and does not hold
  `--interface`, the practices command shall print the AC-052.4 object with the message
  `unsupported interface <N>; this toolkit speaks 1`, print the one stderr line
  `prd_practices: unsupported interface <N>; this toolkit speaks 1`, and exit 2 without reading the
  folder.
Errors: -
Edge cases: exit 1 is never used: the command reports no findings, and a row lint reports is still listed → AC-050.1; a `practices.md` that is not valid UTF-8 is AC-052.3's case; no exit-2 path prints a traceback
Tests: T-052.1 [integration], T-052.2 [integration], T-052.3 [integration], T-052.4 [integration], T-052.5 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_practices; `prdlint/interface.py`

### FR-053 The launcher and a vendored copy answer the same
Status: verified
Source: prd-toolkit/scripts/prd_dispatch.py:15 @5d03191
Acceptance (EARS):
- AC-053.1 When run through the launcher's dispatcher as `prd_dispatch.py practices <arguments>` (what
  `prd practices <arguments>` runs), the practices command shall print what
  `prd-toolkit/scripts/prd_practices.py <arguments>` prints, on stdout and on stderr, and exit with the
  same code.
- AC-053.2 When `prd_practices.py` of a vendored copy (`.prd-toolkit/prd_practices.py`) is run on a PRD
  folder, the practices command shall print, byte for byte, what the plugin's
  `prd-toolkit/scripts/prd_practices.py` prints with the same arguments, as text and with `--json`.
Errors: -
Edge cases: a copy vendored before this area existed has no `prd_practices.py`, and its launcher answers `prd practices` with the dispatcher's unknown-command line and exit 2; the vendored lint carries the rule `practices` as the plugin's does
Tests: T-053.1 [integration], T-053.2 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_practices; fixture repo/vendored

### FR-054 The next source and practice ID
Status: verified
Source: prd-toolkit/scripts/prdlint/change.py:54 @5d03191
Acceptance (EARS):
- AC-054.1 When `prd change ids next <prd_dir> S` is run, the change command shall print the next free
  source ID on one stdout line and exit 0: `S-` and the highest number found plus 1, written with at
  least two digits, or `S-01` when none is found, where the numbers found are those of each source's ID
  cell, as the practices loader reads it, that is `S-` and digits, and of each `S-` and digits, not part
  of a longer word, in the IDs cells of the `## 14. Changelog` table of `prd.md`; with `--json` it shall
  print instead the one line `{"interface": 1, "kind": "change.ids", "next": <the ID>}`.
- AC-054.2 When `prd change ids next <prd_dir> P` is run, the change command shall print the next free
  practice ID as AC-054.1 gives the source ID, from the practices' ID cells and the `P-` IDs of the
  changelog's IDs cells, `P-01` when none is found.
- AC-054.3 If the kind is none of `FR`, `NFR`, `UJ`, `S`, `P`, `AC-<nnn>` and `T-<nnn>`, the change
  command shall print the one stderr line
  `refused: unknown kind <kind>; use FR, NFR, UJ, S, P, AC-<nnn> or T-<nnn>`, print nothing on stdout
  and exit 1.
Errors: -
Edge cases: a declined source is in the table, so its number counts, and a removed source or practice survives only in the changelog, so its number counts too → AC-054.1, AC-054.2; `CS-009` in a changelog cell is a change set, not a source → AC-054.1; with no `practices.md` the next IDs are `S-01` and `P-01` unless the changelog names some → AC-048.1; it reads and never writes, so each ID is written into its table before the next of its kind is asked for, as for every kind; the number after 99 is written with three digits, a form lint reports → AC-049.1; the other kinds answer as before
Tests: T-054.1 [integration], T-054.2 [integration], T-054.3 [integration], T-054.4 [integration], T-054.5 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_change; `prdlint/change.py` next_id

### FR-055 The Practices part of the implement context pack
Status: verified
Source: prd-toolkit/scripts/prdlint/context.py:16 @5d03191
Acceptance (EARS):
- AC-055.1 When run with `--for implement` and an area on a PRD folder that holds `practices.md`, the
  context command shall print a part `Practices`
  directly after the `Code` part and before the `Levels` part, holding one item per practice whose
  Applies to is `code` and whose Object (glob) matches one or more paths of the area (AC-055.2), in the
  Practices table's order, each item the one line `<id> (<source>): <practice>` with the values the
  practices loader reads (FR-048); in the text pack the items are separated by one empty line, as every
  part's items are.
- AC-055.2 The context command shall take as the paths of an area each path that
  `git ls-files --cached --others --exclude-standard`, run at the repository root, prints and that a
  glob of the area's Boundary cell in `adoption.md` matches, and each glob of that cell that holds no
  `*` and no `?`, taken as a path; and, when the PRD folder holds no `adoption.md`, each path that
  command prints outside the PRD folder and outside `.prd-toolkit/`; a glob matching a path as AC-050.2
  gives.
- AC-055.3 When run with `--for implement` on a PRD folder that holds `practices.md` and no practice
  meets AC-055.1, the context command shall print the Practices part with the one item `None.`.
- AC-055.4 When run without `--for implement`, or on a PRD folder that holds no `practices.md`, the
  context command shall print no Practices part and print the pack as it does without this area, byte
  for byte; and with `--for implement` on a PRD folder that holds `practices.md` it shall print every
  other part as it does without this area, except the Header part's size line, the one that starts
  with `pack ` (`pack <n> bytes …`), whose count includes the Practices part.
- AC-055.5 When run with `--for implement` and `--json`, the context command shall put each Practices item
  in the document's `parts`, in the part's place, as
  `{"title": "Practices", "id": <id>, "file": "practices.md", "line": <the row's line>, "text": <the item's line>, "stale": false, "counted": true, "moved": null}`,
  and the `None.` item as
  `{"title": "Practices", "id": null, "file": "practices.md", "line": null, "text": "None.", "stale": false, "counted": true, "moved": null}`.
Errors: -
Edge cases: a `prd` practice never enters the pack: it is for the PRD's review → AC-055.1; the part matches files as section 5 does, so a practice and a standards row with the same glob apply to the same files → AC-055.2; a file the build will create under a wildcard Boundary glob is not a path until it exists, so a Boundary that names the file itself brings it in → AC-055.2; an area with no row in an existing `adoption.md` has no paths → AC-055.3; the pack takes no list of a round's files: the area's Boundary stands for the files a round may change → AC-055.2; only the asked area's paths count, not those of a block pulled in through Traces; a PRD with no `practices.md` gets no Practices part, so its pack is what it was before this area → AC-055.4; the part reads no lint result, so a practice lint reports still appears until the row is fixed; the decide pack, the repo pack and the status report are unchanged → AC-055.4
Tests: T-055.1 [integration], T-055.2 [integration], T-055.3 [integration], T-055.4 [integration], T-055.5 [integration], T-055.6 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_context; `prdlint/context.py` PARTS

### FR-056 A pack's sources
Status: verified
Source: prd-toolkit/scripts/prdlint/packs.py:22 @5d03191
Acceptance (EARS):
- AC-056.1 When a pack's `pack.yaml` holds the key `sources`, a list each of whose items is a mapping whose
  `title`, `location` and `covers` are strings, the manifest loader shall accept the manifest, so that
  the plugin's `prd lint --list-packs` lists the pack.
- AC-056.2 If a pack's `sources` is not a list, the manifest loader shall refuse the manifest with
  `pack <name>: pack.yaml: sources must be a list`; and if an item of it is not a mapping, or lacks
  `title`, `location` or `covers`, or holds one that is not a string, with
  `pack <name>: pack.yaml: sources[<i>] must be a mapping with title, location and covers`, `<i>` the
  first such item's index counted from 0; each refusal reported where the loader's other refusals are,
  so that the plugin's `--list-packs` prints `prd_lint: skipped <folder>: <the refusal>` on stderr and
  lists no line for the pack.
- AC-056.3 When a pack's `pack.yaml` has no `sources` key, the manifest loader shall load it as it does
  without this area, and shall still refuse a key the manifest format does not name with
  `pack <name>: pack.yaml: unknown key <key>`.
Errors: -
Edge cases: an item may hold other keys beside the three, as a `standards` item may → AC-056.1; `pack-resolves` reports a refusal at the line that names the pack, as it reports every manifest refusal; the built-in packs `service` and `document` gain no `sources`, and the `toolkit:` range a pack declares is unchanged; nothing mechanical reads `sources`: the skill proposes them as `proposed` sources, which this PRD does not specify
Tests: T-056.1 [integration], T-056.2 [integration], T-056.3 [integration]  (test-cases/practices.yaml)
Traces: UJ-04; cli:prd_lint; `prdlint/packs.py` load_manifest
