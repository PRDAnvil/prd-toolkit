<!-- Format: references/prd-format.md, "Requirement blocks". -->

# change: the next IDs, the digest, the bump, the record, the pack move and the approval

The change bookkeeping of a PRD, `prd_change.py` (`prd change` through the launcher): the next free IDs, the
folder digest a review verdict carries, the proposed version bump, the record of a change in §14 and §11, a
pack version move, and the approval commit. `ids next S|P` and the unknown-kind refusal are FR-054
(practices), and `pack --lift` is FR-060 (pack-authoring).

### FR-255 The change command's exit codes and usage errors
Status: live (since 10.2.0)
Source: prd-toolkit/scripts/prd_change.py:134 @169036a
Acceptance (EARS):
- AC-255.1 If `prd_change.py` is run with no subcommand, or as `prd_change.py ids` with no `next`, the
  change command shall print its usage on stderr, print nothing on stdout and exit 2.
- AC-255.2 When run with `--interface`, the change command shall print the one stdout line `1` and
  exit 0.
- AC-255.3 If `--json=<N>` names an N other than `1` and `--interface` is not given, the change command
  shall print the stderr line `prd_change: unsupported interface <N>; this toolkit speaks 1` and exit 2.
- AC-255.4 If the folder a subcommand names holds no `prd.md`, the change command shall print one
  stderr line that starts `prd_change: ` and exit 2.
- AC-255.5 If a subcommand refuses, the change command shall print the one stderr line
  `refused: <reason>`, print nothing on stdout and exit 1.
- AC-255.6 When a subcommand run with `--json` exits 2 having printed nothing on stdout, the change
  command shall print on stdout the one line `{"interface": 1, "kind": <kind>, "error": <message>}`,
  where `<kind>` is `change.ids`, `change.digest`, `change.bump`, `change.record`, `change.pack` or
  `change.approve` for the subcommand the command line names (`change` when it names none), and
  `<message>` is the stderr line.
Errors: -
Edge cases: an internal error prints `prd_change: internal error: <type>: <message>` and exits 2 → AC-255.4; argparse's own errors exit 2 → AC-255.1
Tests: T-255.1 [integration], T-255.2 [integration], T-255.3 [integration], T-255.4 [integration], T-255.5 [integration], T-255.6 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-256 The next free requirement, AC and T-id
Status: live (since 10.2.0)
Source: prd-toolkit/scripts/prdlint/change.py:48 @169036a
Acceptance (EARS):
- AC-256.1 When `prd change ids next <prd_dir> FR` or `… NFR` is run, the change command shall print
  one stdout line, the kind asked, `-`, and one more than the highest number of any FR or NFR found in
  the requirement blocks (removed ones included), the §11 index rows and the `FR-` and `NFR-` IDs of
  the §14 changelog's IDs cells, written with at least three digits, and exit 0.
- AC-256.2 When `prd change ids next <prd_dir> UJ` is run, the change command shall print `UJ-` and one
  more than the highest UJ number found in the blocks, the §11 rows and the changelog's IDs cells,
  written with at least two digits, `UJ-01` when none is found, and exit 0.
- AC-256.3 When `prd change ids next <prd_dir> AC-<nnn>` is run, the change command shall print `AC-`,
  `<nnn>` written with three digits, `.` and one more than the highest AC number of the FR or NFR block
  numbered `<nnn>`, its removed ACs included, and exit 0.
- AC-256.4 When `prd change ids next <prd_dir> T-<nnn>` is run, the change command shall print `T-`,
  `<nnn>` written with three digits, `.` and one more than the highest second number among the T-ids of
  requirement `<nnn>` that its block's `Tests:` line, the keys of every test-cases file and the
  changelog's IDs cells name, and exit 0.
- AC-256.5 If no FR or NFR block has the number of an `AC-<nnn>` or `T-<nnn>` kind, the change command
  shall print the one stderr line `refused: no block FR-<nnn> or NFR-<nnn>`, `<nnn>` as typed, and
  exit 1.
- AC-256.6 When `ids next` is run with `--json`, the change command shall print instead the one line
  `{"interface": 1, "kind": "change.ids", "next": <the ID>}`.
Errors: -
Edge cases: FR and NFR share one sequence → AC-256.1; an ID that survives only in §14 counts → AC-256.1, AC-256.2, AC-256.4; it reads and never writes → AC-256.1
Tests: T-256.1 [integration], T-256.2 [integration], T-256.3 [integration], T-256.4 [integration], T-256.5 [integration], T-256.6 [integration], T-256.7 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-257 The digest of a PRD folder
Status: live (since 10.2.0)
Source: prd-toolkit/scripts/prdlint/change.py:117 @169036a
Acceptance (EARS):
- AC-257.1 When `prd change digest <prd_dir>` is run, the change command shall print one stdout line of
  64 lowercase hexadecimal digits, the SHA-256 over the folder's files in sorted order of their paths
  relative to the folder, each fed as its path, a NUL byte, its content and a NUL byte, and exit 0; with
  `--json` the one line `{"interface": 1, "kind": "change.digest", "digest": <the digest>}`.
- AC-257.2 The change command shall leave out of the digest the frontmatter `version:` and `updated:`
  lines of `prd.md`, the body rows of its §11 and §14 tables, the folder's root `README.md`, and every
  file whose path relative to the folder holds a part that is `__pycache__` or starts with `.` (other
  than `.gitkeep`), `.prd-review.json` included, so that a change to any of them leaves the digest as
  it was.
- AC-257.3 When an AC's text or the frontmatter `status:` line of `prd.md` changes, the change command
  shall print a digest that differs from the one before.
- AC-257.4 The change command shall read the folder's files from disk, so that a file git ignores
  changes the digest and a folder in no git repository has a digest.
Errors: -
Edge cases: a review verdict carries the digest, and `record` writes only what the digest leaves out, so a verdict written before `record` still matches → AC-257.2
Tests: T-257.1 [integration], T-257.2 [integration], T-257.3 [integration], T-257.4 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-258 The proposed version bump and its output
Status: live (since 10.2.0)
Source: prd-toolkit/scripts/prdlint/change.py:550 @169036a
Acceptance (EARS):
- AC-258.1 When `prd change bump <prd_dir> --base <ref>` is run, the change command shall compare the
  PRD folder at the commit `<ref>` names with the working tree, print one stdout line per changed item,
  `<level> <ID> <file>:<line> <reason>` with `<file>` relative to the PRD folder, then the line
  `level <level>`, write nothing and exit 0; with `--json` the one line
  `{"interface": 1, "kind": "change.bump", "level": <level>, "items": [{"id", "file", "line", "change", "level", "reason"}]}`,
  each item's `change` being `added`, `removed` or `changed`.
- AC-258.2 The change command shall give the level `needs judgment` when any item is `needs judgment`,
  else the highest item level in the order `patch`, `minor`, `major`, and `patch` when there is no
  item.
- AC-258.3 If `<ref>` names no commit, or its tree holds no PRD folder at the PRD folder's path, the
  change command shall print the one stderr line `bump: <ref> has no <the PRD folder's path from the repository root>`,
  print nothing on stdout and exit 2.
- AC-258.4 If the PRD folder lies in no git repository, the change command shall print one stderr line
  that ends `is not in a git repository` and exit 2.
Errors: -
Edge cases: `<ref>` may be a branch → AC-258.1; `record`, `pack` and `approve` print this same `bump:` line for a missing base, as intended (the owner's answer to Q-53) → AC-258.3
Tests: T-258.1 [integration], T-258.2 [integration], T-258.3 [integration], T-258.4 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-259 How the bump classifies each changed item
Status: live (since 10.2.0)
Source: prd-toolkit/scripts/prdlint/change.py:136 @169036a
Acceptance (EARS):
- AC-259.1 When a block is new, the change command shall report the block, at its heading line, and
  each of its ACs, at the AC's line, `minor` with the reason `a new block or AC`; when an AC is new in a
  block that was there, the AC the same; and each new test case of a new block or a new AC `minor` with
  the reason `a new test case under a new AC`.
- AC-259.2 When a block is removed (gone, or its `Status:` becomes `removed`), the change command shall
  report the block and each AC of it that was not already removed, at their lines in the base, and
  each test case under it, `major` with the reason `a removed block or AC`; and a removed AC of a block
  that stays (marked `(removed in …)` or deleted) `major` with the same reason.
- AC-259.3 When an AC's text differs from the base's after both are lowercased, stripped of punctuation
  and underscores and have their runs of white space collapsed, the change command shall report it
  `needs judgment` with the reason
  `an AC whose text changed (not equal after lowercasing, removing punctuation and collapsing whitespace)`;
  when the text differs but is equal after that normalization, or a block's title, `Flow:` or
  `Edge cases:` changes, `patch` with the reason
  `an AC whose text is equal after that normalization, a changed title, Flow, Edge cases or glossary meaning`.
- AC-259.4 When a test case's mapping changes, the change command shall report it `major` with the
  reason `a changed test case under a changed AC` when its AC changed or was removed, and otherwise
  `needs judgment` with the reason `a changed test case or contract item under an unchanged AC`; and a
  contract item whose text changes (an `errors.yaml` code, a `config.yaml` setting, an OpenAPI
  operation, an event, an SQL table, a top-level key of a custom or pack type's YAML file, or any other
  contracts file outside `contracts/fixtures/` as one item named by its path) the same
  `needs judgment`, and one that is removed `major` with the reason `a removed contract item`.
- AC-259.5 When a test case is new under an AC that did not change, the change command shall report it
  `patch` with the reason `a new test case under an unchanged AC that cites an open errors.md entry`
  when its `known-failing:` names an open `errors.md` entry or an open entry's `Touches:` names the
  AC's requirement, and otherwise `needs judgment` with the reason
  `any other new test case under an unchanged AC`.
- AC-259.6 When a block's `Status:` line changes and the block is not removed, the change command shall
  report the block at its `Status:` line, `patch`, with the reason `status <old value> → <new value>`.
- AC-259.7 When a `Pack:` or `Target: pack` line names the same pack and source as in the base at
  another version, the change command shall report one `patch` item, the ID the pack's name, with the
  reason `` a changed version on a `Pack:` or `Target: pack` line, the pack's name and source unchanged ``,
  and no other item for that line.
- AC-259.8 The change command shall report no item for the frontmatter `version:`, `updated:` and
  `status:` lines, the body rows of the §11 and §14 tables, a block's `Source:` lines, the folder's root
  `README.md`, `.prd-review.json`, and a `Tests:` line whose only change is the T-ids of test cases
  added or removed for that block, each with its case's level tag and test-cases file.
- AC-259.9 When anything else changes, the change command shall report it `needs judgment` with the
  reason `unclassified change in <file>`: a file other than `prd.md`, `test-cases/` and `contracts/`
  (fixtures excepted) whose bytes differ (ID its path, line 1); the text of a features file or `nfr.md`
  outside its blocks (ID its path, line 1); another field of a block such as `Errors:` or `Traces:`
  (ID the block); the part of `prd.md` before its first section (ID `prd.md`) or a section other than
  §3 (ID `section <n>`); a new contract item (ID its name); and a removed test case whose requirement
  stays (ID its T-id).
- AC-259.10 When the body of §3 changes, the change command shall report one `patch` item with the ID
  `glossary`, at `prd.md`, with the reason of a wording-only AC (AC-259.3).
Errors: -
Edge cases: an open entry whose `Touches:` names the requirement makes a new case `patch` even without `known-failing:`, as intended (the owner's answer to Q-54) → AC-259.5; a test case with no `ac:` is read as testing `AC-<nnn>.0` of its T-id's requirement → AC-259.4, AC-259.5; a test case of a new or removed block gets its own item with AC-259.1's or AC-259.2's level and reason, never AC-259.4's or AC-259.5's → AC-259.1, AC-259.2
Tests: T-259.1 [integration], T-259.2 [integration], T-259.3 [integration], T-259.4 [integration], T-259.5 [integration], T-259.6 [integration], T-259.7 [integration], T-259.8 [integration], T-259.9 [integration], T-259.10 [integration], T-259.11 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change; `prdlint/change.py` BUMP_RULES

### FR-260 Record a change in the version, §14 and §11
Status: approved
Source: prd-toolkit/scripts/prdlint/change.py:728 @169036a
Acceptance (EARS):
- AC-260.1 When `prd change record <prd_dir> --base <ref> --bump <level> --change <text>` is run and no
  check of AC-260.5 refuses it, the change command shall write into `prd.md` the frontmatter
  `version:` as the base's version bumped (`major` X+1.0.0, `minor` X.Y+1.0, `patch` X.Y.Z+1),
  `updated:` as today's local date, and the §14 row
  `| <version> | <YYYY-MM-DD> | <text, stripped>; pending | <IDs> |` after the table's last row; stage
  nothing; print `<version>` and that row on two stdout lines and exit 0; with `--json`, the one line
  `{"interface": 1, "kind": "change.record", "version": <version>, "row": <row>}`.
- AC-260.2 The change command shall fill the IDs cell with every FR, NFR, AC and T-id that a bump item
  of FR-259 names, the FR or NFR each such AC and T-id belongs to, and the FR or NFR blocks an added,
  changed or removed contract item cites (an OpenAPI operation's `x-prd-ids`; for any other item the
  `FR-nnn` and `NFR-nnn` tokens of its text and the block of each `AC-nnn.n` token, read at the working
  tree, or at the base for a removed item, and kept to blocks of either PRD), each once, ordered UJ, FR,
  NFR, AC, T and by number, joined by `, `, or `-` when there is none.
- AC-260.3 The change command shall rewrite the §11 rows from the base's: a block a bump item names as
  removed gets the status `removed`; a block an item names that is in the working tree gets its title
  and file from there; a new block is appended as `| <ID> | <title> | <status, approved when none> | <file> | <since> |`;
  then every row whose block is in the working tree takes that block's status, and the Since of its
  `(since X.Y.Z)` (empty when there is none) when an item names the block, the block is `live` or the
  status moved; every other row keeps its Since.
- AC-260.4 When the last §14 row's version is the computed version and its Change cell ends
  `; pending`, the change command shall replace that row instead of adding one, so that a second run
  with the same arguments leaves `prd.md` byte for byte as the first left it.
- AC-260.5 If `--bump` is `needs-judgment`, the change command shall refuse with
  `a needs-judgment bump must be decided first`; else if the change text is empty or holds a newline or
  `|`, with `the change text must be one non-empty line without |`; else if `--bump` is below the
  bump's level (for a `needs judgment` bump, the highest level of its other items, `patch` when there is
  none), with `the diff needs <level>, not <given>`; each writing nothing and exiting 1.
- AC-260.6 If `--bump` is none of `patch`, `minor`, `major` and `needs-judgment`, the change command
  shall print a usage error on stderr and exit 2.
- AC-260.7 When `prd.md` ends its lines in CRLF, the change command shall write it with CRLF line
  endings.
- AC-260.8 If the working `prd.md`'s §14 holds no table, the change command shall refuse with
  `§14 has no changelog table` and write nothing.
- AC-260.9 The change command shall also put in the IDs cell each `UJ-nn` that the text of an added,
  changed or removed contract item names and that a block of either PRD defines, read as AC-260.2 reads
  the item's `FR-nnn` and `NFR-nnn` tokens.
- AC-260.10 When the last §14 row's Change cell ends `; pending`, the change command shall replace that
  row whatever its version, so that a second `record` at another level leaves one row ending `; pending`.
Errors: -
Edge cases: a missing base is FR-258's usage error, prefixed `bump:` (the owner's answer to Q-53) → AC-258.3; a rerun at the same version is AC-260.4's, at another version AC-260.10's → AC-260.4, AC-260.10; a base `prd.md` with no frontmatter version prints `record: the base prd.md has no frontmatter version` and exits 2 → AC-260.1; a working frontmatter with no `version:` or `updated:` line is refused `prd.md frontmatter has no <key>:` → AC-260.8
Tests: T-260.1 [integration], T-260.2 [integration], T-260.3 [integration], T-260.4 [integration], T-260.5 [integration], T-260.6 [integration], T-260.7 [integration], T-260.8 [integration], T-260.9 [integration], T-260.10 [integration], T-260.11 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-261 Move a PRD to a new version of its pack
Status: live (since 10.2.0)
Source: prd-toolkit/scripts/prdlint/change.py:780 @169036a
Acceptance (EARS):
- AC-261.1 When `prd change pack <prd_dir> <name> <X.Y.Z>` is run without `--lift` and no check of
  AC-261.2 refuses it, the change command shall replace, in each §1 `Pack:` line and features
  `Target:` line that names `<name>`, the text `<name> <old> (<source>)` with `<name> <X.Y.Z> (<source>)`;
  record the change against `HEAD` as `record --bump patch` would, with the change text
  `pack <name> <old> → <X.Y.Z>`; print what `record` prints; and stage and commit nothing.
- AC-261.2 The change command shall refuse, in this order: a `<X.Y.Z>` that is not three runs of digits
  joined by `.` (`pack: <X.Y.Z> is not a version X.Y.Z` on stderr, exit 2); no line naming `<name>`
  (`no Pack: or Target: pack line names <name>`); lines naming `<name>` at different versions or
  sources (`the lines naming <name> disagree on its version or source`); a `<X.Y.Z>` the lines already
  name (`every line naming <name> already names <X.Y.Z>`); a path of the PRD folder that
  `git status --porcelain --untracked-files=all` lists
  (`<the PRD folder from the repository root> has uncommitted changes; commit or set them aside first`);
  and a pack the resolver does not find at `<X.Y.Z>`, refused with the resolver's message; each
  writing nothing, and each exiting 1 apart from the first, which exits 2.
- AC-261.3 If the record refuses after the lines moved, the change command shall put back every file it
  edited byte for byte and exit 1.
Errors: -
Edge cases: a features file's `Target: pack` line moves with §1's → AC-261.1; `--source` without `--lift` is FR-060's → AC-060.8
Tests: T-261.1 [integration], T-261.2 [integration], T-261.3 [integration], T-261.4 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-262 The checks before an approval
Status: approved
Source: prd-toolkit/scripts/prdlint/change_approve.py:71 @169036a
Acceptance (EARS):
- AC-262.1 If `--reply` is empty or white space, the change command shall refuse
  `prd change approve` with `the owner's reply is empty`; if `--dry-run`, stripped, is empty or
  `pending`, with `the dry-run record is pending; give the record or "no dry run (<why>)"`; and if it
  holds a newline or `|`, with `the dry-run record must be one non-empty line without |`.
- AC-262.2 If the PRD folder holds no `.prd-review.json`, the change command shall refuse with
  `there is no .prd-review.json; run the review first`; if the file is not JSON, with
  `.prd-review.json is not valid JSON`; if it is not an object whose `ready` is `true`, with
  `the review is not ready`, followed by `: ` and its `blockers` joined by `; ` when that list is not
  empty; and if its `digest` differs from the folder's digest (FR-257), with
  `the PRD changed after its review; review it again`.
- AC-262.3 If `prd_lint.py` exits other than 0 on the PRD folder, the change command shall refuse with
  `lint exits <code>; fix it first`.
- AC-262.4 If the dry-run record starts `no dry run` and the last §14 row's IDs cell names a T-id whose
  test case has a level other than `unit`, the change command shall refuse with
  `the change adds or revises a non-unit test (<T-ids>) and has no dry-run record`, the T-ids joined by
  `, `; a T-id with no test case does not count.
- AC-262.5 If no §14 row's version has a major number of 1 or more, the change command shall refuse with
  `a first approval is authoring's, not a change's`.
- AC-262.6 If the last §14 row's Change cell does not end `; pending`, the change command shall refuse
  with `the last §14 row is not recorded and pending; run record first`.
- AC-262.7 If git lists `CLAUDE.md` at the repository root as changed, does not ignore it, and the file
  is anything other than `HEAD`'s `CLAUDE.md` with the managed block `prd_block.py` renders for the
  working PRD, the change command shall refuse with
  `CLAUDE.md has uncommitted changes; commit or set them aside first`.
- AC-262.8 The change command shall run the checks of AC-262.1 to AC-262.7 and AC-262.11 in that order before it
  writes anything, so that a refusal (exit 1) leaves every file, the verdict included, as it was.
- AC-262.9 The change command shall read a dry-run record that starts `no dry run` in any letter case
  (`No dry run (unit only)`) as AC-262.4's record with no dry run.
- AC-262.10 If the verdict's `blockers` is a string, the change command shall refuse with
  `the review is not ready: <blockers>`, the string written whole.
- AC-262.11 If git lists a generated CI file (`.github/workflows/prd-toolkit.yml` or
  `.gitlab/prd-toolkit.yml` at the repository root) as changed, staged or not, and does not ignore it,
  the change command shall refuse with `<file> has uncommitted changes; commit or set them aside first`,
  `<file>` that path, the GitHub file first.
Errors: -
Edge cases: a CLAUDE.md that git ignores is neither checked nor staged → AC-262.7, AC-263.3; a deleted CLAUDE.md counts as an uncommitted change → AC-262.7; a CI file that does not exist is not changed → AC-262.11
Tests: T-262.1 [integration], T-262.2 [integration], T-262.3 [integration], T-262.4 [integration], T-262.5 [integration], T-262.6 [integration], T-262.7 [integration], T-262.8 [integration], T-262.9 [integration], T-262.10 [integration], T-262.11 [integration], T-262.12 [integration], T-262.13 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change

### FR-263 The approval commit
Status: approved
Source: prd-toolkit/scripts/prdlint/change_approve.py:206 @169036a
Acceptance (EARS):
- AC-263.1 When `prd change approve <prd_dir> --reply <reply> --dry-run <record>` passes every check of
  FR-262, the change command shall replace the last §14 row's trailing `; pending` with
  `; <record, stripped>`, set the frontmatter `status:` line to `status: Approved`, run `prd_block.py`
  on the folder, commit, delete `.prd-review.json`, print the one stdout line
  `approved <the PRD folder's name> <version> <the commit's short SHA>` and exit 0; with `--json`, the
  one line `{"interface": 1, "kind": "change.approve", "commit": <the full SHA>}`.
- AC-263.2 The change command shall commit with the message
  `docs(prd): approve <the PRD folder's name> <the row's version>`, an empty line,
  `Reply: "<reply>"`, `Dry run: <record, stripped>`, an empty line and the trailer
  `Refs: none (no behaviour change)`, or `Refs: <refs>` when `--refs` is given and not empty, with a
  space put before each reply line that starts `Refs:`.
- AC-263.3 The change command shall commit the PRD folder without `.prd-review.json`; the
  `README.md` beside the folder when the folder's parent is named `prd`, the file exists and git does
  not ignore it; `CLAUDE.md` when `prd_block.py` changed its bytes or it held only that block's change,
  and git does not ignore it; and, for a change that moved a pack's version, every file under
  `.prd-toolkit/packs/<name>/` and `.prd-toolkit/pack-sources.json` that exists and git does not
  ignore; each CI file AC-263.6 rewrote; and leave no other path staged.
- AC-263.4 If `--refs` holds a newline or a carriage return, the change command shall print the one
  stderr line `approve: --refs must be one line` and exit 2.
- AC-263.5 If `git add` or `git commit` fails, the change command shall unstage the paths it named, put
  back `prd.md`, `CLAUDE.md`, the READMEs and the CI files it wrote as they were, removing each of them that the run
  created, keep `.prd-review.json`, and refuse
  with `git add failed: <git's message>` or `git commit failed: <git's message>`, git's message being its
  stderr stripped, or for `git commit` its stdout stripped when its stderr is empty.
- AC-263.6 When `prd change approve` passes every check of FR-262 and, after it writes `prd.md`, a
  generated CI file that exists and git does not ignore (`.github/workflows/prd-toolkit.yml` for
  `--github`, `.gitlab/prd-toolkit.yml` for `--gitlab`, the GitHub file first) differs from the text
  `prd_hooks.py ci --<forge> <prd_dir>` would write now (FR-113), the change command shall rewrite that
  file with that text, as `ci --<forge> --force` does (AC-113.2), before it commits; a CI file that does
  not exist, or already holds that text, it shall leave as it is. It prints no line for a rewrite.
Errors: -
Edge cases: the commit runs the repository's hooks; it never passes `--no-verify` → AC-263.5; the gate inbox's approve runs this same command → AC-263.1; approve never creates a CI file the repository does not have → AC-263.6; a rewritten CI file is what the merge gate's `hooks check --ci` compares (AC-068.5), so the approval commit leaves it current → AC-263.6
Tests: T-263.1 [integration], T-263.2 [integration], T-263.3 [integration], T-263.4 [integration], T-263.5 [integration], T-263.6 [integration], T-263.7 [integration], T-263.8 [integration], T-263.9 [integration], T-263.10 [integration], T-263.11 [integration]  (test-cases/change.yaml)
Traces: cli:prd_change
