# error-reopen

An owner can confirm an entry's class and be wrong, or unsure: the inbox's Confirm button writes the
`Confirmed:` line at once, words of doubt included, and a later run can show that the error no longer
happens. Nothing took a confirmation back: no command removed the line, and `prd error check` reports any
change to it. This area takes it back. `prd error reopen <prd_dir> <E-id> --reason <why>` swaps the entry's
`Confirmed:` line for a `Reopened:` line that keeps the old one's date and reply word for word, so the entry
is `proposed` again by the state rule that already exists, and `prd error check` accepts that write. The
same area lets `prd error propose` write an `Explanation:` line, the proposal in plain words for an owner who
has not read the code, and record an entry that did not reproduce as `unclassified`; and the class list gains
`not a defect`. Its one module is `prd-toolkit/scripts/prdlint/errorreopen.py`. The same build makes the edits
this area needs in `prd_error.py` and `prdlint/errors.py` (area `errors`: they parse the new subcommand and
flags, call the module, and give `Reopened` and `Explanation` their place in the order of an entry's lines),
`prdlint/model.py` (area `lint-cli`: the class list, and the entry's explanation for the inbox),
`prdlint/rules/errors.py` (area `lint-registries`, whose requirements say what it reports),
`references/prd-format.md` (area `skills`: the two lines and the class) and `references/help.yaml` (area
`help`: its entry `kind.E`); what each edit does is stated here or in the area that owns it.

Words used below.

- An entry's **lines** are those from its heading to its last line that is not empty before the next
  heading, or before the end of the file; a line **starts with** `<Name>:` when its first characters are
  that name and a colon. An entry's **Confirmed: line** is the
  last of its lines that starts with `Confirmed:`, as the loader reads it, and its **Confirmed value** the text
  after `Confirmed:` on that line with the white space around it removed. Its **Reopened: lines** are its lines
  that start with `Reopened:`, in file order.
- A text **collapsed** is the text with each run of white space, line breaks included, made one space, and
  the white space around it removed. A collapsed text **opens a code fence** when it starts with three
  backticks or three tildes.
- **Today** is the date the command runs, as `YYYY-MM-DD` in the local time zone.
- An entry's **state** is the loader's: `resolved`, `unclassified`, `proposed` or `confirmed`.

## Requirements

### FR-251 Reopen a confirmed entry
Status: approved
Flow: 1. read the entry → 2. check that it is open and `confirmed` and that the reason can be written → 3.
      write the `Reopened:` line in place of the `Confirmed:` line → 4. print the entry's new state
Acceptance (EARS):
- AC-251.1 When `prd_error.py reopen <prd_dir> <E-id> --reason <why>` is run on an open entry whose state is
  `confirmed`, the error command shall replace the entry's Confirmed: line with the line
  `Reopened: <today>, "<why>"; was Confirmed: <value>`, `<why>` being the reason collapsed and `<value>` the
  entry's Confirmed value; shall leave every other line of `errors.md` as it was; shall print the one stdout
  line `<E-id> proposed <class>`, `<class>` being the entry's Classification; and shall exit 0.
- AC-251.2 If `<E-id>` names no entry, the error command shall print the stderr line
  `refused: <E-id> is not an entry`; if the entry is resolved, the stderr line `refused: <E-id> is resolved`;
  and if its state is `unclassified` or `proposed`, the stderr line `refused: <E-id> is not confirmed`; in each
  case it shall leave `errors.md` byte for byte as it was and exit 1.
- AC-251.3 If the reason, collapsed, is empty, the error command shall print the stderr line
  `prd_error: the reason is empty`, leave `errors.md` byte for byte as it was and exit 2.
- AC-251.4 If the reason, collapsed, opens a code fence, the error command shall print the stderr line
  `refused: --reason would open a code fence; drop it or put text before it`; and if it holds the text
  `; was Confirmed:`, the stderr line `refused: --reason must not hold "; was Confirmed:"`; in either case it
  shall leave `errors.md` byte for byte as it was and exit 1.
- AC-251.5 When the entry it reopens already holds Reopened: lines, the error command shall write its line in
  place of the Confirmed: line and leave each earlier Reopened: line as it was, so that the entry holds one
  Reopened: line more, the new one last.
- AC-251.6 When `prd_error.py confirm` is run on an entry that holds Reopened: lines and no line that starts
  with `Confirmed:`, the error command shall write its `Confirmed:` line directly after the entry's last
  Reopened: line; and `prd_error.py propose` on such an entry shall leave each Reopened: line as it was.
- AC-251.7 The help catalogue the toolkit ships shall name, in the `rules` of its entry `kind.E`, the line
  `Reopened: <YYYY-MM-DD>, "<reason>"; was Confirmed: <YYYY-MM-DD>, "<reply>"`, written only by
  `prd_error.py reopen`, which returns a confirmed entry to `proposed`.
Errors: -
Edge cases: a reason that holds a double quote is written as it is, since the reason never holds
`; was Confirmed:` and the line's one such text starts the old confirmation → AC-251.1, AC-251.4; a Confirm the inbox wrote with the
owner's words of doubt is reopened like any other → AC-251.1; the entry's Classification is kept, so a
`code bug` reopened stays `code bug` until it is proposed again → AC-251.1, AC-251.6; the write goes through
the lint guard every write of `prd error` passes, and the prose rules blank a `Reopened:` line as they blank
a `Confirmed:` line (lint-structure AC-026.2), so the owner's words never trip a prose rule → AC-251.1; a
reopened entry cites no confirmation, so a code commit that cites it is reported by `check` and refused by
the commit rule, as for any entry with no `Confirmed:` line → AC-252.4
Tests: T-251.1 [integration], T-251.2 [integration], T-251.3 [integration], T-251.4 [integration], T-251.5 [integration], T-251.6 [integration], T-251.7 [integration], T-251.8 [integration], T-251.9 [integration]  (test-cases/error-reopen.yaml)
Traces: cli:prd_error; cli:prd_help

### FR-252 Check a reopen
Status: approved
Flow: 1. `prd error check` compares each version of `errors.md` in its range with the one before it, as it
      does → 2. a `Confirmed:` line taken out by a reopen, with the `Reopened:` line that quotes it, is no
      finding → 3. an edited, deleted or unmatched `Reopened:` line is
Acceptance (EARS):
- AC-252.1 When `prd_error.py check <prd_dir> <base>..<head>` compares a version of `errors.md` in its range
  with the version before it, and an entry whose earlier version has a Confirmed: line has, in the later
  version, every earlier Reopened: line unchanged and in its order as its first Reopened: lines, followed by
  one Reopened: line more that ends with `; was Confirmed: <value>`, `<value>` being the earlier version's
  Confirmed value, the check command shall print no `Confirmed: changed` finding for that entry, whatever the
  later version's Confirmed: line holds.
- AC-252.2 If an entry's earlier version has a Confirmed: line and its later version has another Confirmed
  value or none, and the later version does not hold the Reopened: lines AC-252.1 names, the check command
  shall print `errors.md: <E-id>: Confirmed: changed`, as it does for an entry with no Reopened: line, and
  exit 1.
- AC-252.3 If an entry's later version does not hold every Reopened: line of its earlier version, unchanged
  and in its order, as its first Reopened: lines, the check command shall print
  `errors.md: <E-id>: Reopened: changed`; and if it holds them and one Reopened: line more or several that
  AC-252.1 does not account for, it shall print `errors.md: <E-id>: Reopened: added without its Confirmed:`;
  in either case it shall exit 1.
- AC-252.4 If a commit in the range changes a file outside the PRD folder and cites in its `Refs:` an entry
  that holds no `Confirmed:` line at that commit because it was reopened, the check command shall print
  `errors.md: <E-id>: commit <sha8> changes code and cites <E-id>, which was not confirmed at that commit`,
  `<sha8>` being the first 8 hex digits of the commit's SHA, as it does for an entry that was never confirmed,
  and exit 1.
Errors: -
Edge cases: a reopen and the confirmation that follows it are two versions, each compared with the one before
it, so neither is a finding → AC-252.1; a reopen and a fresh `Confirmed:` in one write are no finding either →
AC-252.1; a Classification changed in the same write as the reopen still gets the finding
`Classification: changed after Confirmed:` → AC-252.1; a merge commit is compared with each parent, as before;
the findings of resolutions added in the range are unchanged (FR-081)
Tests: T-252.1 [integration], T-252.2 [integration], T-252.3 [integration], T-252.4 [integration], T-252.5 [integration], T-252.6 [integration]  (test-cases/error-reopen.yaml)
Traces: cli:prd_error

### FR-253 Propose with an explanation, as unclassified, or as not a defect
Status: approved
Flow: 1. `prd error propose` reads its flags → 2. writes the Classification, the Touches and the Diagnosis as
      before → 3. writes the `Explanation:` line when `--explanation` is given → 4. prints the entry's state
Acceptance (EARS):
- AC-253.1 When `prd_error.py propose <prd_dir> <E-id> --class <class> --diagnosis <d> --explanation <x>` is
  run on an entry whose state is `unclassified` or `proposed`, the error command shall write the line
  `Explanation: <x>`, `<x>` being the explanation collapsed, in place of the entry's line that starts with
  `Explanation:` when it has one, else directly before its `Diagnosis:` line; shall write every other line as
  `propose` writes it without `--explanation`; and shall print the one stdout line `<E-id> proposed <class>`
  for a class other than `unclassified`.
- AC-253.2 When `prd_error.py propose` is run without `--explanation` on an entry that holds a line that starts
  with `Explanation:`, the error command shall leave that line as it was.
- AC-253.3 If the explanation, collapsed, is empty, the error command shall print the stderr line
  `prd_error: the explanation is empty`, and if it opens a code fence, the stderr line
  `refused: --explanation would open a code fence; drop it or put text before it`; and it shall leave
  `errors.md` byte for byte as it was and exit 2 for the first and 1 for the second.
- AC-253.4 When `prd_error.py propose <prd_dir> <E-id> --class unclassified --diagnosis <d>` is run on an
  entry whose state is `unclassified` or `proposed`, the error command shall write `Classification:
  unclassified`, the Diagnosis and the Touches as `propose` writes them for another class, write no
  `Confirmed:` line, print the one stdout line `<E-id> unclassified`, and exit 0, so that the entry is
  `unclassified` and has no `error-class:<E-id>` gate.
- AC-253.5 The error command shall take `not a defect` as a class wherever it takes `code bug`: as the
  `--class` of `propose` and of `confirm`, which write it and print it as they do any other class.
- AC-253.6 The help catalogue the toolkit ships shall name, in the `rules` of its entry `kind.E`, the optional
  line `Explanation:` (the proposed class in plain words for the owner, written by
  `prd_error.py propose --explanation`), and `not a defect` among the values of `Classification:`.
Errors: -
Edge cases: `--class unclassified` on a `proposed` entry returns it to `unclassified` → AC-253.4; `confirm
--class unclassified` is still refused, since a confirmed class is a class → AC-253.5; an explanation is
read by the prose rules, as the Diagnosis is, so a write that adds a prose finding is refused by the lint
guard → AC-253.1; an explanation on an `unclassified` entry is written and shown nowhere, since it has no
gate → AC-253.1, AC-253.4; the state rule is unchanged: `not a defect` is a class, so an entry of that class
with no `Confirmed:` line is `proposed` → AC-253.5
Tests: T-253.1 [integration], T-253.2 [integration], T-253.3 [integration], T-253.4 [integration], T-253.5 [integration], T-253.6 [integration], T-253.7 [integration], T-253.8 [integration], T-253.9 [integration]  (test-cases/error-reopen.yaml)
Traces: cli:prd_error; cli:prd_help
