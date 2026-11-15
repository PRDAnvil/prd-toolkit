<!-- Format: references/prd-format.md, "Requirement blocks". -->

# help: the help catalogue

The help command is `prd-toolkit/scripts/prd_help.py`, run through the launcher as `prd help`. The
catalogue is a YAML list of entries, one per field of the PRD grammar; an entry has a `key`, a
`name`, a `what`, a `why` and, optionally, `rules` (a list), `checked_by` (a list of lint rule
names) and `see`. A rule's description is the text its registration in the lint registry carries.
The help command takes no PRD folder and reads none.

### UJ-02 A person or a program asks what a field or a lint finding means
Status: verified
Source: prd-toolkit/scripts/prd_help.py:34 @858bb3b
Flow: 1. run `prd help` and read the index of entry keys and rule names
      → 2. run `prd help --key block.ac` or `prd help --rule ac-ears`
      → 3. read what it is, why it is there and its formatting rules
      → 4. a program runs `prd help --json` once and looks each key and rule up itself
Traces: FR-033, FR-034, FR-035, FR-036

### FR-033 Print the index
Status: verified
Source: prd-toolkit/scripts/prd_help.py:57 @858bb3b
Acceptance (EARS):
- AC-033.1 When run with no option, the help command shall print one line per catalogue entry,
  the entry's `key`, two spaces and its `name`, in the catalogue's order; then one empty line;
  then one line per registered rule, its name, two spaces and its severity (`error` or `warn`),
  sorted by name; and shall exit 0 with nothing on stderr.
Errors: -
Edge cases: a catalogue that is an empty list prints the empty line and the rule lines → AC-033.1
Tests: T-033.1 [integration]  (test-cases/help.yaml)
Traces: UJ-02; cli:prd_help

### FR-034 Print one entry or one rule as text
Status: verified
Source: prd-toolkit/scripts/prd_help.py:61 @858bb3b
Acceptance (EARS):
- AC-034.1 When run with `--key` and the key of a catalogue entry, the help command shall print,
  in this order and with nothing else, the line `<name> (<key>)`; the line `What: <what>`; the
  line `Why: <why>`; when the entry has `rules`, the line `Rules:` and then one line `- <rule>`
  per item, in the entry's order; when the entry has `checked_by`, the line `Checked by:` and
  then one line `- <rule name>: <that rule's description>` per item, in the entry's order; when
  the entry has `see`, the line `See: <see>`; and shall exit 0 with nothing on stderr.
- AC-034.2 When run with `--rule` and the name of a registered rule, the help command shall
  print the line `<name> (<severity>)`; the rule's description on the next line; when one or more
  catalogue entries name the rule in `checked_by`, the line `Checks: ` followed by those entries'
  keys in the catalogue's order, joined by `, `; and shall exit 0 with nothing on stderr.
Errors: -
Edge cases: an entry with no `rules`, `checked_by` or `see` prints its first three lines only → AC-034.1; an empty `rules` or `checked_by` list counts as absent → AC-034.1; a rule no entry names prints two lines → AC-034.2; text is printed as the catalogue holds it, Markdown code spans included
Tests: T-034.1 [integration], T-034.2 [integration], T-034.3 [integration]  (test-cases/help.yaml)
Traces: UJ-02; cli:prd_help

### FR-035 Print the catalogue as one JSON document
Status: verified
Source: prd-toolkit/scripts/prd_help.py:35 @858bb3b
Acceptance (EARS):
- AC-035.1 When run with `--json`, the help command shall print on stdout one JSON object on one
  line, ending in a newline, and nothing else,
  `{"interface": 1, "kind": "help", "entries": [<entry>, …], "rules": {<name>: {"severity": <severity>, "description": <description>}, …}}`,
  its keys in that order, where `entries` holds every catalogue entry in the catalogue's order,
  each `<entry>` is an object with the keys `key`, `name`, `what` and `why`, then `rules`,
  `checked_by` and `see`, each of those three present only when the catalogue entry has it, in
  that order; `rules` (the object) holds every registered rule, sorted by name, its severity
  `error` or `warn`; text outside ASCII is written as itself in UTF-8, never as a `\u` escape;
  and shall exit 0 with nothing on stderr.
- AC-035.2 When `--json` is given with `--key`, the help command shall print the AC-035.1
  document with `entries` holding that entry only and `rules` whole; when `--json` is given with
  `--rule`, it shall print the document with `rules` holding that rule only and `entries` holding
  only the entries that name the rule in `checked_by`, in the catalogue's order.
- AC-035.3 When the command line holds `--json=1`, the help command shall behave as with `--json`.
- AC-035.4 When run with `--interface`, the help command shall print `1` on one stdout line and
  exit 0, whatever other options are given, without reading the catalogue and without checking a
  `--json=<N>`.
Errors: -
Edge cases: an empty `rules` or `checked_by` list in the catalogue is left out of the entry, as an absent one → AC-035.1; a field of an entry that the catalogue format does not name is not printed → AC-035.1; `--json --rule` for a rule no entry names prints `"entries": []` → AC-035.2; the interface number stays 1, since the document is new and no existing document changes
Tests: T-035.1 [integration], T-035.2 [integration], T-035.3 [integration], T-035.4 [integration]  (test-cases/help.yaml)
Traces: UJ-02; cli:prd_help; `prdlint/interface.py`

### FR-036 Refuse what it cannot answer
Status: verified
Source: prd-toolkit/scripts/prdlint/helpcat.py:48 @858bb3b
Acceptance (EARS):
- AC-036.1 If `--key` names no catalogue entry, the help command shall print the one stderr line
  `prd_help: no entry '<key>'`, print nothing on stdout and exit 2; if `--rule` names no
  registered rule, it shall do the same with the line `prd_help: no rule '<rule>'`.
- AC-036.2 If the command line holds `--key` together with `--rule`, an option the help command
  does not have, or a positional argument, the help command shall print on stderr the usage line
  `usage: prd_help.py [-h] [--key KEY | --rule RULE] [--json] [--interface]`, on one line whatever
  the terminal width, then `prd_help.py: error: <argparse's message>`, print nothing on stdout
  and exit 2.
- AC-036.3 If the catalogue cannot be used, the help command shall print the one stderr line
  `prd_help: <path>: <reason>`, print nothing on stdout and exit 2, whichever options are given
  other than `--interface` and `-h`, where `<path>` is the catalogue's path as FR-037 gives it and
  `<reason>` is the first that applies of: `no such file`; `YAML parse error: <the parser's problem>`;
  `top level must be a list`; and then, entry by entry in file order, `<n>` counting from 1,
  `entry <n>: must be a mapping`, `entry <n>: missing '<field>'` (the first of `key`, `name`,
  `what`, `why` that is absent, empty or not a string), `entry <n>: '<field>' must be a list of strings`
  (`rules`, then `checked_by`), `entry <n>: 'see' must be a string`,
  `entry <n>: duplicate key '<key>'`, and `entry <n>: checked_by names no rule '<name>'` (the
  first such name).
- AC-036.4 If the help command, run with `--json`, exits 2 by AC-036.1, AC-036.2 or AC-036.3, it
  shall print on stdout one JSON object on one line, ending in a newline,
  `{"interface": 1, "kind": "help", "error": <message>}`, where `<message>` is argparse's message
  (the text after `prd_help.py: error: `) for AC-036.2 and otherwise the stderr line without its
  `prd_help: ` prefix, and shall print its stderr lines as it does without `--json`.
- AC-036.5 If the command line holds `--json=<N>` with any `<N>` other than `1` and does not hold
  `--interface`, the help command shall print the AC-036.4 object with the message
  `unsupported interface <N>; this toolkit speaks 1`, print the one stderr line
  `prd_help: unsupported interface <N>; this toolkit speaks 1`, and exit 2 without reading the
  catalogue.
Errors: -
Edge cases: exit 1 is never used: 1 means findings, and help has none; an unknown key is checked after the catalogue is read, so a catalogue that cannot be used wins → AC-036.3; a usage error is found before the catalogue is read → AC-036.2; no exit-2 path prints a traceback
Tests: T-036.1 [integration], T-036.2 [integration], T-036.3 [integration], T-036.4 [integration], T-036.5 [integration]  (test-cases/help.yaml)
Traces: UJ-02; cli:prd_help; `prdlint/interface.py`

### FR-037 The catalogue it reads, and what the shipped one covers
Status: verified
Source: prd-toolkit/scripts/prdlint/helpcat.py:25 @858bb3b
Acceptance (EARS):
- AC-037.1 While the setting `PRD_HELP_FILE` is set and not empty, the help command shall read
  the catalogue from the file that value names, and `<path>` in AC-036.3 is that value as given.
- AC-037.2 While `PRD_HELP_FILE` is unset or empty, the help command shall read the catalogue the
  toolkit ships, `prd-toolkit/references/help.yaml` when it runs from the plugin and `help.yaml`
  beside the script when it runs from a vendored copy, and `<path>` in AC-036.3 is that file's
  absolute path.
- AC-037.3 The shipped catalogue shall hold an entry for every key that `contracts/cli.yaml`
  lists under `prd_help.keys`; every key in it shall be unique; and the `name` of `kind.UJ`,
  `kind.FR`, `kind.NFR`, `kind.T`, `kind.E` and `kind.CS` shall be `User journey`, `Requirement`,
  `Quality requirement`, `Test case`, `Error` and `Change set`.
- AC-037.4 The shipped catalogue shall hold the entries `kind.S`, named `Source`, and `kind.P`, named
  `Practice`, and the entries `file.practices`, `table.sources` and `table.practices`, and each of the
  five shall name the lint rule `practices` in its `checked_by`.
Errors: -
Edge cases: the shipped catalogue may hold more entries than the listed keys → AC-037.3; a key writes `_` where the PRD's own YAML key has `-` (`case.known_failing` for `known-failing:`), and the entry's `rules` name the real spelling; `see` is the text of a heading of `references/prd-format.md`, a name for a reader, since that file is not vendored
Tests: T-037.1 [integration], T-037.2 [integration], T-037.3 [integration], T-037.4 [integration]  (test-cases/help.yaml)
Traces: cli:prd_help; setting `PRD_HELP_FILE` (contracts/config.yaml)

### FR-038 Every lint rule carries a description
Status: verified
Source: prd-toolkit/scripts/prdlint/registry.py:9 @858bb3b
Acceptance (EARS):
- AC-038.1 The `rules` object of the AC-035.1 document shall hold exactly the rule names that
  `prd_lint.py --list-rules` prints, each with the severity that command prints, and each
  `description` shall be a string that is not empty and holds no line break.
- AC-038.2 The lint command shall print no rule's description: each `--list-rules` line stays
  the rule's name, one space and its severity (AC-003.1), and a finding, as a line or in the
  `--json` document, holds the fields AC-014.1 names and no other.
- AC-038.3 Where a rule is registered with no description, the registry shall hold the empty
  string as its description, and the AC-035.1 document shall print that rule with
  `"description": ""`.
Errors: -
Edge cases: the description says what the rule checks and how to clear a finding, in one to three sentences; the toolkit's own rules each carry one, so AC-038.3 is met only by a rule added later without one, which the unit tests then report
Tests: T-038.1 [integration], T-038.2 [integration], T-038.3 [unit]  (test-cases/help.yaml)
Traces: cli:prd_help; cli:prd_lint; `prdlint/registry.py` DESCRIPTION

### FR-039 A vendored copy answers the same
Status: verified
Source: prd-toolkit/scripts/prdlint/hooks.py:15 @541a963
Acceptance (EARS):
- AC-039.1 When `prd_help.py` of a vendored copy (`.prd-toolkit/prd_help.py`) is run with
  `--json` and `PRD_HELP_FILE` unset, the help command shall print, byte for byte, the document
  the plugin's `prd-toolkit/scripts/prd_help.py --json` prints, reading `.prd-toolkit/help.yaml`.
Errors: -
Edge cases: a copy vendored before the help command existed has no `prd_help.py`, and its launcher answers `prd help` with the dispatcher's unknown-command line and exit 2
Tests: T-039.1 [integration]  (test-cases/help.yaml)
Traces: cli:prd_help; fixture repo/vendored
