<!-- Format: references/prd-format.md, "Requirement blocks". -->

# pack-authoring: a pack written from two adopted PRDs

The pack command is `prd-toolkit/scripts/prd_pack.py`, run through the launcher as `prd pack`. It has
two subcommands. `prd pack compare <prd A> <prd B>` reads two PRD folders and prints what they share,
part by part, each line marked `both`, `A` or `B`: `A` is the first folder the command line names and
`B` the second. `prd pack check <pack dir> <prd A> <prd B>` checks a pack folder written from them. The
library is `prd-toolkit/scripts/prdlint/packcompare.py` (the comparison) and
`prd-toolkit/scripts/prdlint/packcheck.py` (the check). The `--lift` form of
`prd change pack` moves a PRD that names no pack onto a pack declaring its own custom contract types;
the same build makes that edit in `prdlint/change.py`, in the area `change`, which is not adopted, and
what the edit does is stated here. Both read PRD folders and pack manifests and write nothing, except
the lift, which writes the PRD folder it names. How the skill `/prd-toolkit:prd-pack` proposes a pack,
takes the owner's decisions and writes the pack is not specified in this PRD.

### UJ-05 An owner with two adopted PRDs of one kind gets a pack from what they share
Status: verified
Source: prd-toolkit/scripts/prd_pack.py:1 @4fd2e89
Flow: 1. run `prd pack compare <prd A> <prd B>` and read what the two PRDs share and where they differ
      → 2. decide each item, then write the pack folder (`pack.yaml`, the validators, `samples/<type>/bad.*`, a README) into a plugin
      → 3. run `prd pack check <pack dir> <prd A> <prd B>` and fix each finding
      → 4. install the plugin, then in each repository run `prd change pack docs/prd/<slug> <name> <X.Y.Z> --lift`, `prd hooks install` and lint
      → 5. a program runs `prd pack compare --json` or `prd pack check --json` and reads the document
Traces: FR-057, FR-058, FR-059, FR-060, FR-061

### FR-057 Compare two PRDs, as text
Status: verified
Source: prd-toolkit/scripts/prdlint/packcompare.py:1 @4fd2e89
Acceptance (EARS):
- AC-057.1 When run as `prd_pack.py compare <prd A> <prd B>` on two PRD folders that share one or more
  custom contract types (AC-058.2), the pack command shall print seven parts, `Contract types`,
  `Target kinds`, `Levels`, `Harness`, `Standards`, `Skills` and `Vocabulary`, in that order, each as the
  line `## <part>`, then the part's lines as AC-057.2 to AC-057.8 give them or, when the part has none,
  the one line `None.`, then one empty line; and shall exit 0 with nothing on stderr.
- AC-057.2 The pack command shall take as a PRD's custom contract types the rows of the pipe tables of
  section 7 of its `prd.md` that have three or more cells and whose third cell, the Validator, read as
  AC-057.7 reads a cell, is neither empty nor `built-in` nor `pack`; and shall print in the
  Contract types part one line per such row, `<mark> <type>: <files>; <validator>`, where `<type>`,
  `<files>` and `<validator>` are the row's first, second and third cells, read as AC-057.7 reads a cell,
  the type being the item's key.
- AC-057.3 The pack command shall print in the Target kinds part, for each type the Contract types part
  names, in the order it first names it, that a test case of one or both PRDs uses, the line
  `<mark> <type>: <a> in A, <b> in B`, where `<a>` and `<b>` count the test cases of A and of B whose
  `target` value starts with `<type>:`, and `<mark>` is `both` when both counts are above 0, else `A` or
  `B`, the PRD whose count is above 0.
- AC-057.4 The pack command shall print in the Levels part one line per row of the table under the
  level-2 heading `## Levels` of the PRD's `testing.md`,
  `<mark> <level>: <command>; environment <environment>; gate <gate>; timeout <timeout>`, where
  `<level>` is the first cell, the item's key; `<command>` is the text of the second cell's first
  backticked span, its white space collapsed, or the second cell when it holds no backticked span; and
  `<environment>`, `<gate>` and `<timeout>` are the cells of the columns whose header is `Environment`,
  `Gate` and `Timeout`; each cell read as AC-057.7 reads a cell, and each value that is empty, or whose
  column the table lacks, written `-`.
- AC-057.5 The pack command shall print in the Harness part one line per bullet of the section under the
  level-2 heading `## Harness` of the PRD's `testing.md` that starts with `- **<slot>.**`,
  `<mark> <slot>: <text>`, where `<slot>` is the item's key and `<text>` is the rest of the bullet's
  line, followed by each next line that is indented by one or more spaces and not blank, joined with one
  space, its white space collapsed as AC-057.7 gives and its backticks kept.
- AC-057.6 The pack command shall print in the Standards part one line per section 5 row whose fifth
  cell, the Decision, is `enforced`, `<mark> <glob>: <linter>`, where `<glob>`, the item's key, is the
  first cell and `<linter>` the text of the second cell's first backticked span, its white space
  collapsed, or the second cell when it holds no backticked span; and in the Skills part one line per section 6 row whose third cell, the Decision, is
  `required` or `recommended`, `<mark> <activity>: <skill>`, where `<activity>`, the item's key, and
  `<skill>` are the first and second cells; each cell read as AC-057.7 reads a cell.
- AC-057.7 The pack command shall read a cell by removing every backtick from it and collapsing each run
  of white space to one space, with none at either end; shall pair the items of the Contract types,
  Levels, Harness, Standards and Skills parts by their key, the n-th item of a key in A with the n-th
  item of that key in B; shall call two paired items the same when every value their lines print is
  equal; and shall print, for each item of A in A's order, its line marked `both` when its pair in B is
  the same, its line marked `A` followed directly by its pair's line marked `B` when the pair differs,
  and its line marked `A` when it has no pair; and then, in B's order, the line marked `B` of each item
  of B that has no pair in A.
- AC-057.8 The pack command shall print in the Vocabulary part one line `both <word>: <a> in A, <b> in B`
  for each word that occurs in A and in B, where a PRD's words are read from the title of each UJ, FR
  and NFR block whose status is not `removed` and from the text of each of their ACs not marked
  removed, after every code span (a run between two backticks) is removed; a word is a longest run of
  letters (no digit, no underscore), taken in lower case; a word of fewer than four letters, a word of
  the EARS `openers` or the `modal_word` of either PRD's language table (`when`, `while`, `if`, `where`
  and `shall` for `en`), and a word of the `vocabulary` of either built-in pack, `service` or `document`,
  compared in lower case, is left out; `<a>` and `<b>` count the word's occurrences in each PRD; and the
  lines are ordered by `<a>` plus `<b>`, highest first, then by the word, in code-point order.
Errors: -
Edge cases: the comparison reads both folders as the lint command loads them and does not lint them, so a PRD lint reports is still compared → AC-057.1; nothing is matched by resemblance: two values are the same only when they are equal as AC-057.7 reads them → AC-057.7; a difference is never merged: both sides are printed, A's line first → AC-057.7; the built-in packs' vocabularies are empty today, so only the length and the language-table words leave a word out → AC-057.8
Tests: T-057.1 [integration], T-057.2 [integration], T-057.3 [integration], T-057.4 [integration], T-057.5 [integration], T-057.6 [integration], T-057.7 [integration], T-057.8 [integration], T-057.9 [integration]  (test-cases/pack-authoring.yaml)
Traces: UJ-05; cli:prd_pack

### FR-058 The comparison as JSON, and its refusals
Status: verified
Source: prd-toolkit/scripts/prd_pack.py:63 @4fd2e89
Acceptance (EARS):
- AC-058.1 When `prd_pack.py compare` is run with `--json`, the pack command shall print on stdout one
  JSON object on one line, ending in a newline, and nothing else,
  `{"interface": 1, "kind": "pack.compare", "a": <folder A>, "b": <folder B>, "parts": {…}}`, its keys
  in that order, where `<folder A>` and `<folder B>` are the folder arguments as given and `parts` holds
  the keys `contract-types`, `target-kinds`, `levels`, `harness`, `standards`, `skills` and
  `vocabulary`, in that order, each a list of the part's lines in the text's order as objects:
  `{"mark", "type", "files", "validator"}`, `{"mark", "type", "a", "b"}`,
  `{"mark", "level", "command", "environment", "gate", "timeout"}`, `{"mark", "slot", "text"}`,
  `{"mark", "glob", "linter"}`, `{"mark", "activity", "skill"}` and `{"mark", "word", "a", "b"}`, keys in
  those orders, each value the text the line prints, a count as a number and a value the line prints as
  `-` as null; text outside ASCII is written as itself in UTF-8, never as a `\u` escape; and shall exit 0
  with nothing on stderr, a part with no line being the empty list.
- AC-058.2 If no contract type name is a custom contract type (AC-057.2) of both PRDs, the pack command
  shall print nothing on stdout, print the one stderr line
  `prd_pack: <folder A> and <folder B> share no custom contract type; there is no pack to write`, and
  exit 1; with `--json`, it shall print on stdout instead the one line
  `{"interface": 1, "kind": "pack.compare", "error": "<folder A> and <folder B> share no custom contract type; there is no pack to write"}`,
  ending in a newline, and the same stderr line.
- AC-058.3 If a PRD folder argument of `compare` or of `check` names no directory, or a directory with no
  regular file named exactly `prd.md`, the pack command shall print the one stderr line `prd_pack: `
  followed by the text the lint command prints after `prd_lint: ` in that case (AC-005.1 to AC-005.3);
  if the command line names no subcommand or another one, gives a subcommand fewer or more folders than
  it takes, or holds an option it does not have, it shall print on stderr argparse's usage text, whose
  first line starts with `usage: prd_pack.py`, then a line ending in `error: <argparse's message>`; if
  loading a folder raises any other error, it shall print the one stderr line
  `prd_pack: internal error: <exception type>: <message>`; and in each case it shall print nothing on
  stdout and no traceback and exit 2, except that with `--json` stdout shall be the one line
  `{"interface": 1, "kind": <kind>, "error": <message>}`, `<kind>` being `pack.compare` or `pack.check`
  for the subcommand the command line names and `pack` when it names none, and `<message>` argparse's
  message or the stderr line without its `prd_pack: ` prefix.
- AC-058.4 When run with `--interface`, the pack command shall print `1` on one stdout line and exit 0,
  whatever other arguments are given, no subcommand included, without reading a folder; and if the
  command line holds `--json=<N>` with any `<N>` other than `1` and no `--interface`, it shall print the
  AC-058.3 object with the message `unsupported interface <N>; this toolkit speaks 1`, print the one
  stderr line `prd_pack: unsupported interface <N>; this toolkit speaks 1`, and exit 2 without reading
  a folder; `--json=1` shall behave as `--json`.
Errors: -
Edge cases: the part keys are the `pack.yaml` keys a pack writes them into → AC-058.1; the interface number is 1, as for every interface script, and the document is new, so no existing document changes
Tests: T-058.1 [integration], T-058.2 [integration], T-058.3 [integration], T-058.4 [integration], T-058.5 [integration]  (test-cases/pack-authoring.yaml)
Traces: UJ-05; cli:prd_pack; `prdlint/interface.py`

### FR-059 Check a written pack against both PRDs
Status: approved
Source: prd-toolkit/scripts/prdlint/packcheck.py:1 @4fd2e89
Acceptance (EARS):
- AC-059.1 If the pack manifest loader, the one `prd lint --list-packs` uses, refuses
  `<pack dir>/pack.yaml`, the check command (`prd_pack.py check <pack dir> <prd A> <prd B>`) shall print
  the one finding `<pack dir>/pack.yaml: <the loader's message>`, run no other check, and exit 1.
- AC-059.2 When the manifest loads, the check command shall, for each contract type of the manifest in
  its order, and for A and then B, run the type's validator as the lint command runs a section 7 custom
  validator: split as a shell splits it, `${PACK}` in each argument replaced by the pack folder's
  absolute path, with the PRD folder as the working directory and with the PRD's files that the type's
  `files` glob or globs match appended, each a path relative to the PRD folder, in sorted order, `**`
  matching any number of folders; and shall print the finding
  `<prd dir>/prd.md: contract type <type>: <problem>` when no file matches (`glob matches no file`),
  when the command does not split (`validator does not parse: <the error>`), when its program is not
  found (`validator not found: <program>`) or cannot be run (`validator not executable: <program>`), when
  it runs past the time the lint command allows a validator (`validator timed out after <N>s`), and when
  it exits other than 0 (`validator failed: <line>`, `<line>` its first stderr line that is not blank,
  else its first such stdout line, else `exit <code>`).
- AC-059.3 The check command shall, for each contract type of the manifest in its order, run the type's
  validator, split and expanded as AC-059.2 gives, with the pack folder as the working directory, once
  for each regular file of `<pack dir>/samples/<type>/` whose name starts with `bad.`, in name order,
  with that file's path relative to the pack folder (`samples/<type>/<name>`) as its one argument; and
  shall print the finding `<pack dir>/samples/<type>: no bad.* sample; add a file the validator must refuse`
  when there is no such file, the finding
  `<pack dir>/samples/<type>/<name>: the validator accepts it; a sample must be refused` when a run exits
  0, and the finding `<pack dir>/samples/<type>/<name>: <problem>` with AC-059.2's problem text when the
  validator does not split, is not found, cannot be run or times out.
- AC-059.4 The check command shall print, for each item of the manifest's `levels` in its order whose
  command's first word, split as a shell splits it, is not found on PATH, the finding
  `<pack dir>/pack.yaml: levels[<i>] (<level>): <word> is not on PATH`, `<i>` the item's index counted
  from 0.
- AC-059.5 The check command shall print its findings one per stdout line, those of AC-059.2, then of
  AC-059.3, then of AC-059.4, and nothing else; shall exit 1 when it prints one or more and, with none,
  print nothing and exit 0; and shall print nothing on stderr in either case.
- AC-059.6 When `prd_pack.py check` is run with `--json`, the check command shall print on stdout one
  JSON object on one line, ending in a newline, and nothing else,
  `{"interface": 1, "kind": "pack.check", "findings": [{"file": <path>, "message": <what>}, …]}`, keys
  in those orders, one object per finding in AC-059.5's order, `<path>` being the path before the
  finding's first `: ` as AC-059.1 to AC-059.4 write it and `<what>` the rest, and exit as AC-059.5
  gives; `findings` is the empty list when there is none.
- AC-059.7 The check command shall, for each contract type of the manifest and for A and then B, when
  AC-059.2's run of that type on that PRD exits 0, run the type's validator once more, split and
  expanded as AC-059.2 gives, with the pack folder as the working directory and the same files
  appended in the same order, each as an absolute path; and shall print, in the place AC-059.2's
  finding for that type and PRD would take, the finding
  `<prd dir>/prd.md: contract type <type>: validator fails from the pack folder: <line>`, `<line>` as
  AC-059.2 gives it, when that run exits other than 0, and the finding
  `<prd dir>/prd.md: contract type <type>: validator timed out after <N>s` when it runs past the time
  AC-059.2 allows.
Errors: -
Edge cases: `<pack dir>` is the folder as the command line names it, so a finding's path is that folder joined to the file with `/` → AC-059.1 to AC-059.4; the loader also refuses a `target-kinds` entry that names no contract type of the pack, a `toolkit:` range that excludes this toolkit and a folder with no `pack.yaml` (`pack <name>: pack.yaml: is missing`), so each is AC-059.1's one finding → AC-059.1, AC-059.4; the check writes nothing, in the pack or in either PRD
Tests: T-059.1 [integration], T-059.2 [integration], T-059.3 [integration], T-059.4 [integration], T-059.5 [integration], T-059.6 [integration], T-059.7 [integration], T-059.8 [integration]  (test-cases/pack-authoring.yaml)
Traces: UJ-05; cli:prd_pack; `prdlint/packs.py` load_manifest

### FR-060 Lift a PRD onto the pack written from its own custom types
Status: verified
Source: prd-toolkit/scripts/prdlint/change.py:821 @dcc43b5
Acceptance (EARS):
- AC-060.1 When run as `prd_change.py pack <prd_dir> <name> <X.Y.Z> --lift` and no check of AC-060.2 to
  AC-060.5 refuses it, the change command shall insert the line `- Pack: <name> <X.Y.Z> (<source>)`
  into section 1 of `prd.md`, directly after the last line of section 1 that starts with `- `, or, when
  section 1 holds no such line, directly after section 1's heading line; replace
  the Validator cell, the third cell, of each section 7 row that is a custom row (AC-057.2) of a contract
  type the pack declares, so that the text between that cell's two `|` becomes ` pack `, the rest of the
  row as it was; record the change as a patch as `prd change record --bump patch` records one, the
  version one patch above the committed one, `updated` today (the local date, as `record` takes it) and
  the section 14 row `| <version> | <YYYY-MM-DD> | pack <name> <X.Y.Z> lifted; pending | - |`; stage
  nothing and commit nothing, as a version move does, so that `git status --porcelain` lists the PRD's
  `prd.md` as modified and unstaged, ` M <its path from the repository root>`, and no other path of
  the PRD folder; and print on stdout the two lines `<version>` and that row, exit 0 and print nothing on
  stderr, or, with `--json`, print the one line
  `{"interface": 1, "kind": "change.pack", "version": <version>, "row": <row>}`.
- AC-060.2 If section 1 of `prd.md` holds a `Pack:` line, or a features file holds a `Target:` line with
  a pack part, the change command shall print the one stderr line
  `refused: the PRD already names pack <name> at <file>:<line>; a lift moves a PRD that names none`,
  where `<name>`, `<file>` and `<line>` are those of the first such line (section 1's, then the features
  files' in name order), write nothing and exit 1.
- AC-060.3 The change command shall take, as the pack to lift onto, the pack named `<name>` at version
  `<X.Y.Z>` among the packs that `prd lint --list-packs`, run from the same scripts, lists (the
  toolkit's own, then each installed plugin's, in the installed-plugins file's order), when exactly one
  listed pack has that name and version, and its source as `<source>`; with `--source <source>`, only
  the listed packs of that source count; and if no listed pack that counts has that name and version,
  it shall print the one stderr line
  `refused: no pack <name> <X.Y.Z> is on this machine; prd lint --list-packs lists the packs it finds`,
  or, with `--source`,
  `refused: no pack <name> <X.Y.Z> (<source>) is on this machine; prd lint --list-packs lists the packs it finds`,
  write nothing and exit 1.
- AC-060.4 If a contract type the pack declares has no section 7 row in `prd.md` that is a custom row
  (AC-057.2) of that name, the change command shall print the one stderr line
  `refused: contract type <type> of pack <name> is not a custom row of section 7`; and if the Files cell
  of the first such row, read as AC-057.7 reads a cell, differs from the type's `files` in the pack (a
  list of globs joined by `, `), the one stderr line
  `refused: contract type <type>: section 7 has <cell>, pack <name> has <files>`; in either case for the
  first such type in the pack's order, writing nothing and exiting 1.
- AC-060.5 If `git status --porcelain --untracked-files=all` lists a path of the PRD folder, the change
  command shall print the one stderr line
  `refused: <the PRD folder, relative to the repository root> has uncommitted changes; commit or set them aside first`,
  write nothing and exit 1; the command shall check `<X.Y.Z>` first, as a version move does
  (`pack: <X.Y.Z> is not a version X.Y.Z` on stderr, exit 2), then AC-060.2, then this criterion, then
  AC-060.3 and AC-060.8, then AC-060.4.
- AC-060.6 When run without `--lift`, the change command shall move a pack's version as it did before
  this area, with the same output, record and refusals, among them
  `refused: no Pack: or Target: pack line names <name>` for a PRD that names no such pack.
- AC-060.7 When a PRD that AC-060.1 lifted is linted while its pack resolves, the lint command shall
  print the findings it printed for the PRD before the lift, each finding at a line of `prd.md` below
  the inserted `Pack:` line with its line number one higher, and exit with the same code; the PRD
  folder shall differ from its committed state only in the frontmatter lines `version:` and `updated:`,
  the `Pack:` line, the Validator cells AC-060.1 replaces and the section 14 row it adds, so that its
  `testing.md` (Levels and Harness), its section 5 and 6 rows and its test cases are unchanged; and the
  implement context pack of an area of the PRD (`prd context <prd_dir> --area <area> --for implement`)
  shall differ from the one before the lift only in the Header part's version line
  (`PRD: … version <version> mode implement`), its profile line
  (`Target: pack <name> <X.Y.Z> (<source>), output language <code>`) and its size line (the one that
  starts with `pack `), in the Stack part's added `- Pack:` line, and, when the pack has a `harness`,
  in the added Harness defaults part.
- AC-060.8 If more than one pack that AC-060.3 counts has the name `<name>` and the version `<X.Y.Z>`,
  the change command shall print the one stderr line
  `refused: pack <name> <X.Y.Z> comes from more than one source: <sources>; name one with --source <source>`,
  where `<sources>` is each such pack's source, in the order `prd lint --list-packs` lists them, joined
  by `, `, and the line's last word is the text `<source>` as written here, naming no source, write
  nothing and exit 1; and if `--source` is given without `--lift`, it shall print the
  stderr line `pack: --source belongs to --lift` and exit 2.
- AC-060.9 When `prd_change.py approve` approves a PRD whose `prd.md` holds a `Pack:` line in section 1
  while its committed `prd.md` holds none and no features file of the commit holds a `Target:` line
  with a pack part (a lift, AC-060.1), the change command shall add to the approval commit, beside
  what an approval commits, every file under `.prd-toolkit/packs/<name>/`, `<name>` that line's pack,
  and the file `.prd-toolkit/pack-sources.json`, each where it exists and git does not ignore it, as
  the approval of a version move does; so that after it `git status --porcelain --untracked-files=all`
  lists none of them.
Errors: -
Edge cases: a lift is a patch, not a conversion: the pack declares what the PRD already declared, so no output changes → AC-060.7; the PRD's own Levels, Harness, standards and skills stay as they are → AC-060.1, AC-060.7; then `prd hooks install` vendors the pack and the owner approves with the dry-run record `no dry run (pack lifted)`, as for a version move; a lift is run from the plugin's scripts, as a version move is → AC-060.3; that the context pack names the pack and prints its harness defaults is a property of naming a pack, as for any area that names one, and what a build or a test produces does not change → AC-060.7; with exactly one pack of that name and version on the machine, no `--source` is needed → AC-060.3; a PRD that names the pack after its lift moves to a new version of it by the version move → AC-060.6
Tests: T-060.1 [integration], T-060.2 [integration], T-060.3 [integration], T-060.4 [integration], T-060.5 [integration], T-060.6 [integration], T-060.7 [integration], T-060.8 [integration], T-060.9 [integration], T-060.10 [integration], T-060.11 [integration], T-060.12 [integration], T-060.13 [integration]  (test-cases/pack-authoring.yaml)
Traces: UJ-05; cli:prd_change_pack_lift; cli:prd_change; `prdlint/change.py` pack

### FR-061 The launcher and a vendored copy answer the same
Status: verified
Source: prd-toolkit/scripts/prd_dispatch.py:15 @4fd2e89
Acceptance (EARS):
- AC-061.1 When run through the launcher's dispatcher as `prd_dispatch.py pack <arguments>` (what
  `prd pack <arguments>` runs), the pack command shall print what
  `prd-toolkit/scripts/prd_pack.py <arguments>` prints, on stdout and on stderr, and exit with the same
  code.
- AC-061.2 When `prd_pack.py` of a vendored copy (`.prd-toolkit/prd_pack.py`) is run with the same
  arguments, the pack command shall print, byte for byte, what the plugin's
  `prd-toolkit/scripts/prd_pack.py` prints, as text and with `--json`.
Errors: -
Edge cases: a copy vendored before this area existed has no `prd_pack.py`, and its launcher answers `prd pack` with the dispatcher's unknown-command line and exit 2
Tests: T-061.1 [integration], T-061.2 [integration]  (test-cases/pack-authoring.yaml)
Traces: UJ-05; cli:prd_pack; fixture repo/vendored
