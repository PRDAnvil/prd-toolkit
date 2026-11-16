<!-- Format: references/prd-format.md, "Requirement blocks". -->

# card-context: the area and the URL of a gate

Every gate of `prd gates list --json`, and every card of the decision inbox, carries `areas`, a list of
area names, and `url`, a string or null; the text listing of `prd gates list` is unchanged. One module derives both, `prd-toolkit/scripts/prdlint/cardcontext.py`. The
same build makes the edits this area needs in `prdlint/gates.py`, `prd_gates.py` and
`templates/gates/inbox.html` (area `gates`), `prdlint/errors.py` and `prd_error.py` (area `errors`),
`prdlint/rules/errors.py` (area `lint-registries`), `references/help.yaml` (area `help`) and
`prdlint/model.py`, which parses an `errors.md` entry and a `Target:` line (area `lint-cli`); what each
edit does is stated here. Nothing fetches a URL.

Words used below. The area of a requirement block is the name of its features file without `.md`
(`features/import.md` is `import`), and `nfr` for a block of `nfr.md`. The PRD's area order is the
order the loader reads the blocks in: the features files by name, then `nfr.md`. An area's URL is the
address of the url part of its features file's `Target:` line (FR-065); an area with no such part, and
`nfr`, has none. A well-formed address starts with `http://` or `https://`, has one or more characters
after it, and holds no white space.

### UJ-06 An owner reading a card sees which area it is for and can open the thing it is about
Status: approved
Flow: 1. record an error with `prd error new … --url <address>`, or set one later with `prd error url`
      → 2. give an area its URL on its `Target:` line: `Target: url https://example.com/orders`
      → 3. open the decision inbox: each card says `Area: <names>` or `Area: none`, and links to its URL
      → 4. a program runs `prd gates list --json` and reads each gate's `areas` and `url`
Traces: FR-062, FR-063, FR-064, FR-065, FR-066, FR-067

### FR-062 A gate's areas
Status: approved
Acceptance (EARS):
- AC-062.1 The gates command shall give an `error-class:<E-id>` gate as its areas, first, the areas of
  the blocks its entry's `Touches:` line names that the PRD defines, in the PRD's area order; then the
  areas of the blocks that own a test case whose `known-failing:` names the entry (the block that holds
  the case's `ac:`, else the FR or NFR whose number is the case's T-id's), each area not already listed,
  in the PRD's area order; and the empty list when there is none, as for `Touches: -` with no such case.
- AC-062.2 The gates command shall give a `signoff:<T-id>` gate the one area of its test case's file
  (`test-cases/<area>.yaml`, and `nfr` for `test-cases/nfr.yaml`), and an `adoption:<area>` gate the one
  area `<area>`.
- AC-062.3 The gates command shall give an `approval:<branch>` gate as its areas the areas of the blocks
  that the verdict's `touches` list names, each once, in the PRD's area order, where an entry that is
  the ID of a block the PRD defines names that block, an `AC-<nnn>.<n>` names the block that holds that
  AC, a `T-<nnn>.<n>` names the FR or NFR whose number is `<nnn>`, and any other entry names none.
- AC-062.4 The gates command shall give every `deploy-step:` gate, the gate of a run log that cannot be
  read included, the empty list, since a run deploys the whole PRD.
Errors: -
Edge cases: an ID on `Touches:` that no block defines gives no area (`index-consistent` reports it) → AC-062.1; the owners of known-failing cases are found as the context pack's `--req E-nnn` finds them → AC-062.1; an area is listed once however many blocks name it → AC-062.1
Tests: T-062.1 [integration], T-062.2 [integration], T-062.3 [integration], T-062.4 [integration], T-062.5 [integration]  (test-cases/card-context.yaml)
Traces: UJ-06; cli:prd_gates; `prdlint/context.py` _entry_reqs

### FR-063 The URL: line of an error entry
Status: approved
Acceptance (EARS):
- AC-063.1 Where an `errors.md` entry holds a line that starts at column 0 with `URL:`, the PRD loader
  shall take the text after `URL:`, its surrounding white space removed, as the entry's URL, the first
  such line of the entry counting, wherever it stands in the entry; and an entry with no such line shall
  have no URL.
- AC-063.2 If an entry's URL is not a well-formed address, the lint command shall report
  `error-entries` at the entry's first `URL:` line with
  `<E-id>: URL: must start with http:// or https:// and hold no white space`.
- AC-063.3 While no `errors.md` entry holds a `URL:` line, the lint command and `prd error list` shall
  print what they printed before this area, byte for byte.
Errors: -
Edge cases: the line's place is after `Touches:`, where FR-064 writes it, and the loader reads it anywhere in the entry → AC-063.1; a line indented two spaces after `Evidence:` is evidence, not a `URL:` line → AC-063.1; nothing fetches the address → AC-063.2
Tests: T-063.1 [integration], T-063.2 [integration], T-063.3 [integration]  (test-cases/card-context.yaml)
Traces: UJ-06; cli:prd_lint; `prdlint/model.py` _errors_ledger

### FR-064 Write an entry's URL with prd error
Status: approved
Acceptance (EARS):
- AC-064.1 When `prd_error.py new <prd_dir> --title <title> --source <source>` is run with
  `--url <address>` and a well-formed address, the error command shall write the new entry as it writes
  one without `--url`, with the line `URL: <address>` directly after its `Touches:` line, or directly
  after its `Classification:` line when it has no `Touches:` line, and shall print the new entry's ID
  on one stdout line and exit 0, as before.
- AC-064.2 When run as `prd_error.py url <prd_dir> <E-id> <address>` with a well-formed address, the
  error command shall write the line `URL: <address>` into the entry, in place of its first `URL:` line
  when it has one, else directly after the last of its `Detected:`, `Classification:`, `Confirmed:` and
  `Touches:` lines, leaving every other line of `errors.md` as it was; shall print on one stdout line
  the entry's ID, one space and its state, then one space and its class when the class is not the
  state (`E-001 proposed code bug`, `E-002 unclassified`), the line `prd error propose` prints; and
  shall exit 0.
- AC-064.3 When run as `prd_error.py url <prd_dir> <E-id> -`, the error command shall remove the
  entry's first `URL:` line, or leave `errors.md` byte for byte as it was when the entry has none, print
  the AC-064.2 line and exit 0.
- AC-064.4 If the address that `new --url` or `url` is given is not well formed, and for `url` is not
  `-`, the error command shall print the stderr line
  `refused: URL: must start with http:// or https:// and hold no white space`, leave `errors.md` byte
  for byte as it was and exit 1; and if `url` names no entry, it shall do the same with the stderr line
  `refused: <E-id> is not an entry`.
Errors: -
Edge cases: without `--url` the entry is written byte for byte as before → AC-064.1; `-` is not an address for `new`: an entry with no URL is written by leaving `--url` out → AC-064.4
Tests: T-064.1 [integration], T-064.2 [integration], T-064.3 [integration], T-064.4 [integration]  (test-cases/card-context.yaml)
Traces: UJ-06; cli:prd_error; `prdlint/errors.py` new

### FR-065 The url part of a Target: line
Status: approved
Acceptance (EARS):
- AC-065.1 Where a features file's `Target:` line holds one, two or three parts separated by commas, in
  the order `pack <name> <X.Y.Z> (<source>)`, `output language <code>` and `url <address>`, each at most
  once, the PRD loader shall read the pack part and the output-language part as it did before this
  area, and shall take the address after `url `, its surrounding white space removed, as the area's URL,
  the url part being the line's last part and its address running to the end of the line, so that it
  may hold a comma; and an area whose line has no url part, or whose file has no `Target:` line, shall
  have no URL.
- AC-065.2 If the address of a `Target:` line's url part is not a well-formed address, the lint command
  shall report `pack-resolves` at that line with
  `Target: url must start with http:// or https:// and hold no white space`, and the PRD loader shall
  read the line as it reads a malformed `Target:` line, so that the area takes section 1's pack and
  output language and has no URL.
- AC-065.3 If a `Target:` line names no part, names a part twice, names its parts out of the order of
  AC-065.1, or holds a part that is none of the three forms, the lint command shall report
  `pack-resolves` at that line with
  `Target: must be one or more of pack <name> <X.Y.Z> (<source>), output language <code> and url <address>, comma-separated, in that order`,
  the message that takes the place of the one it printed before this area.
Errors: -
Edge cases: `Target: url https://example.com/orders` gives the area a URL and inherits section 1's pack and output language → AC-065.1; `Target: pack document 1.0.0 (prd-toolkit), output language en, url https://example.com/guide` names all three → AC-065.1; the place rules of a `Target:` line (after the level-1 heading, before the first requirement, one per file) are unchanged → AC-065.3; section 1 holds no URL line: a PRD-wide URL is set aside
Tests: T-065.1 [integration], T-065.2 [integration], T-065.3 [integration]  (test-cases/card-context.yaml)
Traces: UJ-06; cli:prd_lint; `prdlint/model.py` _targets

### FR-066 A gate's URL
Status: approved
Acceptance (EARS):
- AC-066.1 The gates command shall give an `error-class:<E-id>` gate as its URL the entry's URL when
  the entry has one that is a well-formed address, else the URL of the first of the gate's areas
  (AC-062.1, in that order) that has one, else null.
- AC-066.2 The gates command shall give a `signoff:<T-id>` gate and an `adoption:<area>` gate as its URL
  the URL of its one area, or null when that area has none.
- AC-066.3 The gates command shall give an `approval:<branch>` gate as its URL the URL of its area when
  its areas (AC-062.3) are exactly one area, or null when that area has none; and null when its areas
  are none or two or more.
- AC-066.4 The gates command shall give every `deploy-step:` gate the URL null.
Errors: -
Edge cases: a URL is given as written, never checked to answer → AC-066.1; a malformed URL is a lint finding (AC-063.2, AC-065.2) and is passed over, so a card never links to it: an entry's goes to its areas' URL, and an area's malformed `Target:` line gives it none → AC-066.1, AC-065.2
Tests: T-066.1 [integration], T-066.2 [integration], T-066.3 [integration], T-066.4 [integration]  (test-cases/card-context.yaml)
Traces: UJ-06; cli:prd_gates

### FR-067 Where the area and the URL show
Status: approved
Acceptance (EARS):
- AC-067.1 When `prd_gates.py list <prd_dir>` is run without `--json`, the gates command shall print
  what it printed before this area, byte for byte: one line `<id> <title>` per gate, in the same order,
  with neither the gate's areas nor its URL, whatever areas and URLs the PRD holds.
- AC-067.2 When `prd_gates.py list <prd_dir>` is run with `--json`, the gates command shall print the
  document it printed before this area, `{"interface": 1, "kind": "gates", "prd": <slug>, "gates": […]}`,
  with each gate object holding the keys it held before this area and, after them, `areas`, the gate's
  areas as a list of strings, and `url`, the gate's URL as a string or null, both on every gate.
- AC-067.3 The inbox's card of a gate, the object `prdlint.gates.card(gate, prd, root, rel)` returns and
  `/gates` serves for it, shall hold the gate's `areas` list and `url`, and every key it held before this
  area with its value unchanged, so that an adoption gate's card keeps its `area`, the area's name as a
  string, beside `areas`.
- AC-067.4 The decision inbox page (`templates/gates/inbox.html`) shall show on each card, directly under
  its title, the line `Area: <areas>`, the card's `areas` joined by `, `, or `Area: none` when they are
  the empty list; and, when the card's `url` is a string, a link whose text and address are that URL and
  that opens in a new tab (`target="_blank"`, `rel="noopener"`), and no link when it is null; each
  inserted as text, never as HTML.
- AC-067.5 The status command's Next part shall list each gate as it did before this area: the text
  `<the gate's title> waits for your answer.`, the title without the gate's areas, with the `id`,
  `ids` and `area` AC-044.1 gives.
- AC-067.6 The help catalogue the toolkit ships shall name, in the `rules` of its entry `kind.E`, the
  optional line `URL: <address>` of an entry, after `Touches:`.
Errors: -
Edge cases: fields are added and none is removed, renamed or changes type, so `interface` stays 1 → AC-067.2, AC-067.3; the areas and the URL are for a program and the inbox: the text listing and `prd status`'s Next part read as before → AC-067.1, AC-067.5; a gate's areas and URL are worked out when the gates are listed, so a `Target:` or `URL:` line edited while the inbox is open shows at its next refresh
Tests: T-067.1 [integration], T-067.2 [integration], T-067.3 [integration], T-067.4 [unit], T-067.5 [integration], T-067.6 [integration]  (test-cases/card-context.yaml)
Traces: UJ-06; cli:prd_gates; `prdlint/gates.py` list_gates
