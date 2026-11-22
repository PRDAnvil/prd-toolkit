<!-- Format: references/prd-format.md, "Requirement blocks". -->

# lint-ids: the lint rules for IDs, the index and acceptance criteria

### FR-121 Check the form of every ID
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/ids.py:66 @4465291
Flow: 1. read every Markdown line of the PRD, code spans and fenced blocks blanked → 2. find each token of a kind (`UJ`, `FR`, `NFR`, `AC`, `T`, `E`, `A`), a dash and a digit
      → 3. fully match it against its kind's pattern → 4. do the same for every key and string value of the contract YAML files and of each test case's body
Acceptance (EARS):
- AC-121.1 When a Markdown line of the PRD folder holds, outside a code span or fenced block, a token that starts at a word boundary with `UJ-`, `FR-`, `NFR-`, `AC-`, `T-`, `E-` or `A-` followed by a digit, and the token (the kind, the dash, then digits and dots up to the last digit) does not fully match its kind's pattern (`UJ-\d{2}`, `FR-\d{3}`, `NFR-\d{3}`, `AC-\d{3}\.\d+`, `T-\d{3}\.\d+`, `E-\d{3}`, `A-\d{2}`), the lint command shall report `id-format` at that line with `'<token>' does not match the <kind> id format <pattern>`, once per token.
- AC-121.2 When such a token stands inside a Markdown code span, the lint command shall report no `id-format` finding for it.
- AC-121.3 When a string key or string value of a YAML file under `contracts/` (fixtures excluded), or of the body of a test case, holds a token that AC-121.1 calls malformed, the lint command shall report `id-format` with AC-121.1's message, at the line of the key that holds the value (for a list item, the line of the list's key). A malformed test-case key is reported at the line of that key.
- AC-121.4 When a token fully matches its kind's pattern, the lint command shall report no `id-format` finding for it.
- AC-121.5 The lint command shall read, for `id-format`, no Markdown or YAML file whose name, or a folder of whose path below the PRD folder, starts with `.`, and shall report no `id-format` finding for a token in such a file.
Errors: -
Edge cases: a trailing `.` is not part of the token, so `FR-001.` is FR-001 → AC-121.4; `FR-001.1` is a malformed FR → AC-121.1; a letter right after the digits (`FR-012a`) makes no token, and `CS-001` holds none, since no word boundary precedes its `S`; errors.md's `Evidence:` and `Confirmed:` lines are blanked by the shared prose reader (lint-structure); YAML comments are not read, only loaded values; a malformed test-case key is reported at its own line, never at line 1 → AC-121.3; a hidden file gives no finding → AC-121.5; an ID with more digits than its pattern allows, such as `FR-1000` or `UJ-100`, is malformed: the patterns fix three digits for FR, NFR and E and two for UJ and A → AC-121.1
Tests: T-121.1 [integration], T-121.2 [integration], T-121.3 [integration], T-121.4 [integration], T-121.5 [integration], T-121.6 [integration], T-121.7 [integration], T-121.8 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-122 Define each ID once
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/ids.py:81 @4465291
Flow: 1. collect every definition: block headings and their ACs, test-case keys, `### E-nnn` headings, section 12 rows → 2. report each one after the first
      → 3. group FR and NFR blocks by number and report a number both kinds use
Acceptance (EARS):
- AC-122.1 When an ID has more than one definition, the lint command shall report `id-unique` at each definition after the first with `<ID> is already defined at <file>:<line>`, naming the first definition. The definitions are a requirement block heading, an AC line, a test-case key in any `test-cases/*.yaml` file, a `### E-nnn` heading of errors.md outside a code fence, and the first cell of a section 12 row (backticks removed). They are taken in this order: the blocks of `features/*.md` in sorted file order and then those of `nfr.md`, each followed by its ACs; then the test-case files in sorted order; then errors.md; then section 12.
- AC-122.2 When an FR block and an NFR block carry the same number, the lint command shall report `id-unique` once at the first NFR block of that number with `FR-<number> and NFR-<number> share a number; FR and NFR use one sequence`.
Errors: -
Edge cases: a third definition is also reported against the first → AC-122.1; the same AC ID in two blocks is a repeat → AC-122.1; a key repeated within one test-cases file is reported under this rule by the YAML loader (lint-cli); a fenced `### E-nnn` example in errors.md is no definition → AC-122.1
Tests: T-122.1 [integration], T-122.2 [integration], T-122.3 [integration], T-122.4 [integration], T-122.5 [integration], T-122.6 [integration], T-122.7 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-123 Mark a removal in both the index and the block
Status: live (since 9.3.0)
Source: prd-toolkit/scripts/prdlint/rules/ids.py:97 @4465291
Acceptance (EARS):
- AC-123.1 When a section 11 row's Status is `removed` and its block's is not, or the block's is `removed` and the row's is not, the lint command shall report `id-removed-reused` at the row's line with `<ID> is '<row status>' in the index but '<block status>' in <block file>:<block line>; both must say removed or neither`.
- AC-123.2 When exactly one of a row and its block says `removed`, the lint command shall report no `index-consistent` finding that the two statuses differ.
Errors: -
Edge cases: a row with no block is index-consistent's (FR-125); both saying removed gives no finding → AC-123.1
Tests: T-123.1 [integration], T-123.2 [integration], T-123.3 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-124 Never cite a removed requirement or AC
Status: live (since 9.3.0)
Source: prd-toolkit/scripts/prdlint/rules/ids.py:141 @4465291
Flow: 1. a requirement is removed when its row and its block both say removed; an AC is removed when its line carries `(removed in X.Y.Z)`
      → 2. check each test case's `ac:`, each `x-prd-ids` item, and each Traces line of a block that is not removed
Acceptance (EARS):
- AC-124.1 When a test case's `ac:` value names a removed AC, a removed requirement, or an AC whose FR or NFR of the same number is removed, the lint command shall report `id-removed-reused` at the `ac:` line with `test case <T-id> cites removed <ID>`, or `test case <T-id> cites <AC-id> of removed <requirement ID>` for an AC of a removed requirement.
- AC-124.2 When an item of an `x-prd-ids` list in a contract YAML file names an ID that AC-124.1 treats as removed, the lint command shall report `id-removed-reused` at the line of the `x-prd-ids` key with `x-prd-ids cites removed <ID>` or `x-prd-ids cites <AC-id> of removed <requirement ID>`, once per item.
- AC-124.3 When the `Traces:` line of a block that is not removed, or one of its continuation lines (indented two spaces, not blank), holds a `UJ-`, `FR-`, `NFR-` or `AC-` ID that AC-124.1 treats as removed, the lint command shall report `id-removed-reused` at that line with `<block ID> Traces cites removed <ID>` or `<block ID> Traces cites <AC-id> of removed <requirement ID>`.
- AC-124.4 When only one of a requirement's row and block says `removed`, the lint command shall not treat the requirement as removed, and shall report no finding that cites it.
Errors: -
Edge cases: a removed block's own Traces line is not checked → AC-124.3; the ID on a Traces line is checked even inside backticks → AC-124.3
Tests: T-124.1 [integration], T-124.2 [integration], T-124.3 [integration], T-124.4 [integration], T-124.5 [integration], T-124.6 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-125 Keep the section 11 index and the blocks in step
Status: verified
Source: prd-toolkit/scripts/prdlint/rules/ids.py:175 @1ad8dbe
Acceptance (EARS):
- AC-125.1 When an ID appears in more than one section 11 row, the lint command shall report `index-consistent` at each later row with `<ID> appears twice in the section 11 index (first at prd.md:<line>)`.
- AC-125.2 If a requirement block has no section 11 row, the lint command shall report `index-consistent` at the block's heading with `<ID> has no row in the section 11 index`.
- AC-125.3 If a section 11 row names an ID that no block defines, the lint command shall report `index-consistent` at the row with `<ID> is in the index but has no block`.
- AC-125.4 When a row's Title or File cell differs from its block's heading title or file, the lint command shall report `index-consistent` at the row with `<ID>: index title '<row title>' differs from block title '<block title>'` or `<ID>: index file '<row file>' differs from block file '<block file>'`. The two titles are compared as written, a code span at either end included, so a row and a block whose titles are the same text never differ.
- AC-125.5 When a row whose ID has a block carries a status outside `as-built`, `approved`, `built`, `verified`, `live` and `removed`, the lint command shall report `index-consistent` at the row with `<ID>: unknown index status '<status>'`. When that block's status is outside them, the lint command shall report `index-consistent` at the block with `<ID>: unknown status '<status>'`.
- AC-125.6 When a row with a block says `live` and its Since cell is empty, the lint command shall report `index-consistent` at the row with `<ID> is live but the index has no Since`. When a block says `live` with no `(since X.Y.Z)` and has a row, the lint command shall report `index-consistent` at the block with `<ID> is live but its Status line has no '(since X.Y.Z)'`.
- AC-125.7 When a row's status and its block's both come from AC-125.5's list, differ, and neither is `removed`, the lint command shall report `index-consistent` at the row with `<ID>: index status '<row status>' differs from block status '<block status>'`, and when either status is unknown it shall report no such finding.
Errors: -
Edge cases: the Since cell and the block's since are not compared with each other; a removed/other mismatch is FR-123's → AC-125.7; a title that starts or ends with a code span matches the same title in the other place → AC-125.4; a block with no row is reported for the missing row only, and its status is checked once the row exists → AC-125.2
Tests: T-125.1 [integration], T-125.2 [integration], T-125.3 [integration], T-125.4 [integration], T-125.5 [integration], T-125.6 [integration], T-125.7 [integration], T-125.8 [integration], T-125.9 [integration], T-125.10 [integration], T-125.11 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-126 Require a Source line on an as-built block
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/ids.py:191 @4465291
Acceptance (EARS):
- AC-126.1 If a block's status is `as-built` and it has no `Source:` field line with text, the lint command shall report `index-consistent` at the block's heading with `<ID> is as-built but has no 'Source: <file>:<line> @<commit>' line`.
- AC-126.2 When an `as-built` block has a `Source: <file>:<line> @<commit>` line, the lint command shall report no such finding.
- AC-126.3 If an `as-built` block's `Source:` line, or a continuation line of it, is not `<file>:<line> @<commit>` (a path, a colon, a line number, a space, `@` and a commit of 7 to 40 hex digits), the lint command shall report `index-consistent` at the block's heading with `<ID> is as-built but its Source line is not '<file>:<line> @<commit>'`.
Errors: -
Edge cases: the check runs whether or not the block has a row → AC-126.1; a continuation line of `Source:` is a line indented two spaces that follows it → AC-126.3
Tests: T-126.1 [integration], T-126.2 [integration], T-126.3 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-127 Check errors.md entries against the blocks
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/ids.py:184 @4465291
Acceptance (EARS):
- AC-127.1 If an errors.md entry is resolved and its `Classification:` value is `unclassified`, or it has no `Classification:` line, the lint command shall report `index-consistent` at the entry's heading with `<E-id>: unclassified is allowed only on an open entry`.
- AC-127.2 When an entry whose `Classification:` value is `unclassified` is open, the lint command shall report no such finding.
- AC-127.3 If a `Touches:` line names a `UJ-`, `FR-` or `NFR-` ID that no requirement block defines, the lint command shall report `index-consistent` at that line with `<E-id> Touches <ID>, which no block defines`, once per such ID, and nothing for an ID that a block defines.
Errors: -
Edge cases: a removed block still defines its ID → AC-127.3; the loader decides whether an entry is open, and which IDs `Touches:` names (lint-cli); a resolved entry with no `Classification:` line counts as `unclassified` → AC-127.1
Tests: T-127.1 [integration], T-127.2 [integration], T-127.3 [integration], T-127.4 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint; errors.md

### FR-128 Require a feature file for an area past not started
Status: live (since 9.3.0)
Source: prd-toolkit/scripts/prdlint/rules/ids.py:181 @4465291
Acceptance (EARS):
- AC-128.1 If an adoption.md row's State is `extracted`, `confirmed` or `adopted` and the PRD folder has no `features/<area>.md`, the lint command shall report `index-consistent` at the row with `adoption area '<area>' is <state> but features/<area>.md does not exist`.
- AC-128.2 When the row's State is `not started`, or `features/<area>.md` exists, the lint command shall report no such finding for that row.
Errors: -
Edge cases: a state outside the four is the sections rule's (lint-structure FR-024), and this rule skips it; with no adoption.md nothing is checked
Tests: T-128.1 [integration], T-128.2 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint; adoption.md

### FR-129 Give every FR and NFR a live acceptance criterion
Status: live (since 9.3.0)
Source: prd-toolkit/scripts/prdlint/rules/ids.py:221 @4465291
Acceptance (EARS):
- AC-129.1 If an FR or NFR block whose status is not `removed` holds no AC line, the lint command shall report `fr-has-ac` at its heading with `<ID> has no acceptance criteria`.
- AC-129.2 If every AC line of such a block is marked `(removed in X.Y.Z)`, the lint command shall report `fr-has-ac` at its heading with `<ID> has no live acceptance criteria; remove the requirement instead`.
- AC-129.3 When a block is a UJ, or its status is `removed`, the lint command shall report no `fr-has-ac` finding for it.
Errors: -
Edge cases: an AC is any `- AC-nnn.n` line of the block, as the loader reads it (lint-cli)
Tests: T-129.1 [integration], T-129.2 [integration], T-129.3 [integration], T-129.4 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint

### FR-130 Write each live AC in an EARS pattern
Status: live (since 9.3.0)
Source: prd-toolkit/scripts/prdlint/rules/ids.py:232 @4465291
Acceptance (EARS):
- AC-130.1 If a live AC's text (continuation lines joined) neither starts with one of the language table's `openers` as a whole word, case-sensitive, nor matches its `ubiquitous` pattern, the lint command shall report `ac-ears` at the AC's line with `<AC-id> must start with <the openers, comma-separated> or <ubiquitous_hint>`, which reads `must start with When, While, If, Where or 'The <thing> shall'` for `en`.
- AC-130.2 If a live AC passes AC-130.1 but does not hold the table's `modal` pattern, the lint command shall report `ac-ears` at its line with `<AC-id> must contain '<modal_word>'`.
- AC-130.3 When an AC is marked `(removed in X.Y.Z)`, the lint command shall report no `ac-ears` finding for it.
- AC-130.4 While the PRD's `language:` is `es`, the lint command shall apply the `es` table: the openers `Cuando`, `Mientras`, `Si`, `Donde`, the ubiquitous form `El/La/Los/Las <cosa> deberá` and the modal `deberá`.
Errors: -
Edge cases: `when` in lower case is not an opener → AC-130.1; "The API shall answer …" is the ubiquitous form → AC-130.1; which table applies, and the fall-back when none loads, are the language loader's (packs area, not adopted)
Tests: T-130.1 [integration], T-130.2 [integration], T-130.3 [integration], T-130.4 [integration], T-130.5 [integration], T-130.6 [integration], T-130.7 [integration], T-130.8 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint; references/languages/en.yaml; references/languages/es.yaml

### FR-131 Give every NFR a measurable bound
Status: live (since 9.3.0)
Source: prd-toolkit/scripts/prdlint/rules/ids.py:246 @4465291
Acceptance (EARS):
- AC-131.1 If an NFR block whose status is not `removed` holds, in its body lines (heading excluded, its `UJ-`, `FR-`, `NFR-` and `AC-` IDs removed), no number followed by a unit (`ms`, `s`, `sec`, `second(s)`, `minute(s)`, `min`, `h`, `hr(s)`, `hour(s)`, `day(s)`, `KB`, `MB`, `GB`, `TB`, `request(s)/s`, `req/s`, `request(s)/min`, `req/min`, `rps`, `rows`, `user(s)`, `error(s)`, or `%`), the lint command shall report `nfr-bound` at its heading with `<ID> states no measurable bound (a number with a unit such as ms, %, requests/s)`.
- AC-131.2 When the bound stands on any body line of the block, the AC's or another, the lint command shall report no `nfr-bound` finding.
- AC-131.3 When an NFR block's status is `removed`, the lint command shall report no `nfr-bound` finding for it.
Errors: -
Edge cases: a number inside an ID (`NFR-300 ms`) is no bound → AC-131.1; `99.9%` and `600 req/min` are bounds → AC-131.2; space between the number and the unit is optional; a unit matches in the case the list writes it, so `300 MS` and `4 kb` are no bound → AC-131.1
Tests: T-131.1 [integration], T-131.2 [integration], T-131.3 [integration], T-131.4 [integration], T-131.5 [integration], T-131.6 [integration]  (test-cases/lint-ids.yaml)
Traces: UJ-01; cli:prd_lint
