<!-- Format: references/prd-format.md, "Requirement blocks". -->

# lint-contracts: the lint rules for contract files

### FR-170 Check each OpenAPI operation's PRD fields
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:131 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:523 @9961c9e
Flow: 1. validate the whole document with openapi-spec-validator → 2. for each item of `paths` and `webhooks`
      → 3. for each operation key: operationId, x-prd-ids, the three x- lists
Acceptance (EARS):
- AC-170.1 If `contracts/openapi.yaml` loads as a mapping and openapi-spec-validator rejects it, the lint command shall report `contracts-valid` at line 1 of the file with `openapi validation failed: <the first line of the validator's message>`, and shall still apply AC-170.2 to AC-171.4 to the file.
- AC-170.2 If the file's `paths` or `webhooks` key holds a value that is neither null nor a mapping, the lint command shall report `contracts-valid` at that key's line with `<key> must be a mapping`.
- AC-170.3 If a value under `paths` or `webhooks` is not a mapping, the lint command shall report `contracts-valid` at its key's line with `<path>: must be a mapping`, `<path>` being that key (a path, or a webhook's name).
- AC-170.4 Where a path item holds one of the keys `get`, `put`, `post`, `delete`, `options`, `head`, `patch` and `trace` with a value that is not null, the lint command shall check that value as the operation `<METHOD> <path>`, `<METHOD>` being the key upper-cased; if the value is not a mapping, it shall report `contracts-valid` at the key's line with `<METHOD> <path>: operation must be a mapping`.
- AC-170.5 If an operation's `operationId` is absent, not a string or empty, the lint command shall report `contracts-valid` at the line of the operation's key (`get:`, `post:` and so on) with `<METHOD> <path>: missing operationId`.
- AC-170.6 If an operation's `x-prd-ids` is absent or not a non-empty list, the lint command shall report `contracts-valid` with `<METHOD> <path>: x-prd-ids must be a non-empty list`, at the `x-prd-ids` line, or, when the key is absent, at the line of the operation mapping's first key.
- AC-170.7 If an item of a non-empty `x-prd-ids` list is not a string of the form `UJ-<n>`, `FR-<n>`, `NFR-<n>` or `AC-<n>.<n>` that the PRD defines, the lint command shall report `contracts-valid` at the `x-prd-ids` line with `<METHOD> <path>: x-prd-ids item <item> is not a defined requirement or AC id`, `<item>` written as Python's `repr` writes it (`'AC-003.9'` for a string), once for each such item, in list order.
- AC-170.8 If an operation's `x-error-codes`, `x-preconditions` or `x-effects` is absent or not a list, the lint command shall report `contracts-valid` with `<METHOD> <path>: <key> must be a list (use [] for none)`, at that key's line, or, when the key is absent, at the line of the operation mapping's first key.
Errors: -
Edge cases: the file is checked only when it loads as a mapping; its parse errors, repeated keys and a top level that is not a mapping are the loader's (lint-cli FR-012) → AC-170.1; an operation key whose value is null is skipped → AC-170.4; a webhook is checked like a path and named by its key → AC-170.3; a removed requirement's or AC's ID still counts as defined here, and `id-removed-reused` reports it (lint-ids) → AC-170.7; a test-case T-id or an E-id is defined but not of an accepted form → AC-170.7; the items of `x-preconditions` and `x-effects` are not checked → AC-170.8
Tests: T-170.1 [integration], T-170.2 [integration], T-170.3 [integration], T-170.4 [integration], T-170.5 [integration], T-170.6 [integration], T-170.7 [integration], T-170.8 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-171 Require a content example on each OpenAPI response
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:173 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:189 @9961c9e
Acceptance (EARS):
- AC-171.1 If an operation's `responses` is absent or not a mapping, the lint command shall report `contracts-valid` with `<METHOD> <path>: responses must be a mapping`, at the `responses` line, or, when the key is absent, at the line of the operation mapping's first key, and shall check none of that operation's responses.
- AC-171.2 If a response whose status key is not `204` is not a mapping, the lint command shall report `contracts-valid` at the status key's line with `<METHOD> <path>: response <status> must be a mapping`.
- AC-171.3 If a response mapping whose status key is not `204` holds no `$ref` key, and its `content` is not a mapping in which some media type is a mapping holding `example` or `examples`, the lint command shall report `contracts-valid` at the status key's line with `<METHOD> <path>: response <status> has no content example`.
- AC-171.4 When a response's status key is `204`, written as a string or as a number, the lint command shall report no AC-171.2 or AC-171.3 finding for it, whatever its value.
Errors: -
Edge cases: a `$ref` response is not looked into → AC-171.3; `examples` counts as `example` → AC-171.3
Tests: T-171.1 [integration], T-171.2 [integration], T-171.3 [integration], T-171.4 [integration], T-171.5 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-172 Require the asyncapi key of asyncapi.yaml
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:525 @9961c9e
Acceptance (EARS):
- AC-172.1 If `contracts/asyncapi.yaml` loads as a mapping with no top-level key `asyncapi`, the lint command shall report `contracts-valid` at line 1 of the file with `missing top-level key asyncapi`.
- AC-172.2 When `contracts/asyncapi.yaml` holds the top-level key `asyncapi`, `contracts-valid` shall report no finding about the file's shape.
Errors: -
Edge cases: `channels` and `operations` are not checked, whatever their type → AC-172.2
Tests: T-172.1 [integration], T-172.2 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-173 Require the five field lines of each event in events.md
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:195 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:538 @9961c9e
Acceptance (EARS):
- AC-173.1 If a section of `contracts/events.md` that starts at a `### ` heading has no line that starts, at column 0, with `Trigger:`, `Payload:`, `Delivery:`, `Retries:` or `Failure:`, the lint command shall report `contracts-valid` at the heading's line with `event '<name>' has no <field>: line`, once for each missing field, in that order. `<name>` is the heading's text after `### `, with its surrounding white space and backticks removed.
- AC-173.2 The lint command shall end a section at the next heading of level 1, 2 or 3, or at the end of the file; a heading of level 1 or 2 starts no section.
- AC-173.3 When a `### ` line or a field line lies inside a fenced code block, the lint command shall not treat it as a heading, and shall count the field line for no event.
Errors: -
Edge cases: a `####` heading neither ends nor starts a section → AC-173.2; lines before the first `### ` heading count for no event → AC-173.1; an indented field line does not count → AC-173.1; a fenced `Trigger:` line leaves its event without one → AC-173.3
Tests: T-173.1 [integration], T-173.2 [integration], T-173.3 [integration], T-173.4 [integration], T-173.5 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-174 Check that schema.sql parses and describes every table and column
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:223 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:256 @9961c9e
Acceptance (EARS):
- AC-174.1 If `contracts/schema.sql` is a file that sqlglot cannot parse in the dialect the front matter's `sql-dialect` names, or in sqlglot's default dialect when that key is absent or empty, the lint command shall report `contracts-valid` at line 1 of the file with `schema.sql does not parse (<dialect>): <the first line of the parser's message>`, `<dialect>` being the `sql-dialect` value or `default dialect`, and shall check nothing else in the file.
- AC-174.2 If the table of a `CREATE TABLE` statement has neither a `COMMENT ON TABLE` statement that names it nor a `description` property among the statement's properties, the lint command shall report `contracts-valid` with `table <table> has no COMMENT ON TABLE or OPTIONS(description=...)`, `<table>` being the table's name without its schema, at the first line of the file that holds `<table>` as a whole word.
- AC-174.3 If a column that a `CREATE TABLE` statement defines has neither a `COMMENT ON COLUMN <table>.<column>` statement nor a `description` property of its own, the lint command shall report `contracts-valid` with `column <table>.<column> has no COMMENT ON COLUMN or OPTIONS(description=...)`, at the first line, at or after the line AC-174.2 gives for its table, that holds `<column>` as a whole word.
- AC-174.4 When a table or a column carries a `description` property (BigQuery's `OPTIONS(description="…")`), the lint command shall report no AC-174.2 or AC-174.3 finding for it.
Errors: -
Edge cases: the line is the first occurrence of the word, so a table named in an earlier line (a comment, another table's REFERENCES) moves its finding there → AC-174.2; `structure` reports a missing or unknown `sql-dialect` (lint-structure FR-020) → AC-174.1
Tests: T-174.1 [integration], T-174.2 [integration], T-174.3 [integration], T-174.4 [integration], T-174.5 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-175 Check each code of the error catalogue
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:264 @9961c9e
Acceptance (EARS):
- AC-175.1 If a top-level key of `contracts/errors.yaml` is not a string matching `^[A-Z][A-Z0-9_]*$`, the lint command shall report `contracts-valid` at the key's line with `error code <key> must match ^[A-Z][A-Z0-9_]*$`, `<key>` written as Python's `repr` writes it.
- AC-175.2 If a code's value is not a mapping, the lint command shall report `contracts-valid` at the code's line with `<code>: must be a mapping with meaning, when, status, message, log_level, retryable, metric`, and shall check that value no further.
- AC-175.3 If a code's mapping lacks one of the keys `meaning`, `when`, `status`, `message`, `log_level`, `retryable` and `metric`, the lint command shall report `contracts-valid` at the code's line with `<code>: missing <key>`, once for each missing key, in that order.
- AC-175.4 If a code's `status` is present and is not an integer, or is a boolean, the lint command shall report `contracts-valid` at the `status` line with `<code>: status must be an integer`.
- AC-175.5 If a code's `retryable` is present and is not a boolean, the lint command shall report `contracts-valid` at the `retryable` line with `<code>: retryable must be true or false`.
Errors: -
Edge cases: YAML reads an unquoted `no` or `yes` as a boolean → AC-175.5; a null `status` is reported → AC-175.4; the values of `meaning`, `when`, `message`, `log_level` and `metric` are not checked → AC-175.3; an empty catalogue `{}` gets no finding → AC-175.3
Tests: T-175.1 [integration], T-175.2 [integration], T-175.3 [integration], T-175.4 [integration], T-175.5 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-176 Check the roles and operations of permissions.yaml
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:282 @9961c9e
Acceptance (EARS):
- AC-176.1 If the `roles` of `contracts/permissions.yaml` is absent or not a mapping, the lint command shall report `contracts-valid` with `roles must be a mapping of role to {identity}`, at the `roles` line, or at the file's first key line when the key is absent, and shall check the operations as if no role were defined.
- AC-176.2 If a role's value is not a mapping, or its `identity` is absent or empty, the lint command shall report `contracts-valid` at the role's line with `role <role>: missing identity`.
- AC-176.3 If `operations` is absent or not a mapping, the lint command shall report `contracts-valid` with `operations must be a mapping of operation to {allow, deny}`, at the `operations` line, or at the file's first key line when the key is absent.
- AC-176.4 If an operation's value is not a mapping, the lint command shall report `contracts-valid` at the operation's line with `operation <operation>: must be a mapping with allow and deny lists`.
- AC-176.5 If an operation's `allow` or `deny` is absent or not a list, the lint command shall report `contracts-valid` with `operation <operation>: <key> must be a list`, at that key's line, or at the line where the operation's mapping starts when the key is absent, and shall apply neither AC-176.6 nor AC-176.7 to that operation.
- AC-176.6 When an operation's `allow` and `deny` are both lists, if a role of `roles` is in neither list or in both, the lint command shall report `contracts-valid` at the operation's line with `operation <operation>: role <role> must appear in exactly one of allow and deny (found <n>)`, `<n>` being how many of the two lists hold it, for each such role in `roles` order.
- AC-176.7 When an operation's `allow` and `deny` are both lists, if a string in either is not a role of `roles`, the lint command shall report `contracts-valid` at the operation's line with `operation <operation>: unknown role <role>`, once for each such item, the `allow` items first.
- AC-176.8 If a role's value is a mapping whose `secret` is absent, null or an empty string, the lint command shall report `contracts-valid` at the role's line with `role <role>: missing secret`, after any AC-176.2 finding for that role.
Errors: -
Edge cases: a role that is not a mapping gets only the identity finding → AC-176.2, AC-176.8; a role listed twice in one list counts once → AC-176.6; an item that is not a string is neither a role nor an unknown role → AC-176.7; the operations are not compared with the operationIds of openapi.yaml → AC-176.4
Tests: T-176.1 [integration], T-176.2 [integration], T-176.3 [integration], T-176.4 [integration], T-176.5 [integration], T-176.6 [integration], T-176.7 [integration], T-176.8 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-177 Check the row rules of permissions.yaml
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:316 @9961c9e
Acceptance (EARS):
- AC-177.1 When `row_rules` is absent or null, the lint command shall report no AC-177.2, AC-177.3 or AC-177.4 finding.
- AC-177.2 If `row_rules` is present and not a list, the lint command shall report `contracts-valid` at its line with `row_rules must be a list`, and shall check no item.
- AC-177.3 If a mapping item of `row_rules` has no `role`, `operation`, `predicate` or `attribute`, or an empty one, the lint command shall report `contracts-valid` at the item's first line with `row_rules item <i>: missing <key>`, `<i>` being the item's place counted from 1, once for each such key, in that order.
- AC-177.4 If an item of `row_rules` is not a mapping, the lint command shall report `contracts-valid` at the `row_rules` line with `row_rules item <i> must be a mapping`.
Errors: -
Edge cases: the role and operation a rule names are not compared with `roles` and `operations` → AC-177.3
Tests: T-177.1 [integration], T-177.2 [integration], T-177.3 [integration], T-177.4 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-178 Check the settings of config.yaml
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:332 @9961c9e
Acceptance (EARS):
- AC-178.1 If the `settings` of `contracts/config.yaml` is absent or not a mapping, the lint command shall report `contracts-valid` with `settings must be a mapping of name to {type, default, environments, owner}`, at the `settings` line, or at the file's first key line when the key is absent, and shall check nothing else in the file.
- AC-178.2 If a setting's value is not a mapping, the lint command shall report `contracts-valid` at the setting's line with `setting <name>: must be a mapping`.
- AC-178.3 If a setting's mapping lacks `type`, `default`, `environments` or `owner`, the lint command shall report `contracts-valid` at the setting's line with `setting <name>: missing <key>`, once for each missing key, in that order.
- AC-178.4 If a setting's `environments` is present and not a mapping, the lint command shall report `contracts-valid` at the `environments` line with `setting <name>: environments must be a mapping`.
Errors: -
Edge cases: a key present with a null value is not missing → AC-178.3; the environment names are not compared with testing.md → AC-178.4
Tests: T-178.1 [integration], T-178.2 [integration], T-178.3 [integration], T-178.4 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-179 Check the tables and masking of data-classification.yaml
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:349 @9961c9e
Acceptance (EARS):
- AC-179.1 If the `tables` of `contracts/data-classification.yaml` is absent or not a mapping, the lint command shall report `contracts-valid` with `tables must be a mapping`, at the `tables` line, or at the file's first key line when the key is absent, and shall still check `masking`.
- AC-179.2 If a table's value is not a mapping, the lint command shall report `contracts-valid` at the table's line with `table <table>: must be a mapping`.
- AC-179.3 If a table's mapping lacks `retention`, `deletion` or `columns`, the lint command shall report `contracts-valid` at the table's line with `table <table>: missing <key>`, once for each missing key, in that order.
- AC-179.4 If a table's `columns` is present and not a mapping, the lint command shall report `contracts-valid` at the `columns` line with `table <table>: columns must be a mapping of column to class`.
- AC-179.5 If a column's class is anything other than one of the strings `public`, `internal`, `confidential` and `pii`, a list or a mapping included, the lint command shall report `contracts-valid` at the column's line with `<table>.<column>: class <class> must be public, internal, confidential or pii`, `<class>` written as Python's `repr` writes it.
- AC-179.6 If `masking` is absent or not a mapping, the lint command shall report `contracts-valid` with `masking must be a mapping with logs, errors and fixtures`, at the `masking` line, or at the file's first key line when the key is absent.
- AC-179.7 If the `masking` mapping lacks `logs`, `errors` or `fixtures`, the lint command shall report `contracts-valid` with `masking: missing <key>`, once for each missing key, in that order, at the line of the mapping's first key (the `masking:` line when the mapping is written inline).
Errors: -
Edge cases: classes compare exactly, so `PII` is not `pii` → AC-179.5; a class that is a list or a mapping is reported like any other, never as an internal error → AC-179.5; tables and columns are not compared with schema.sql → AC-179.2
Tests: T-179.1 [integration], T-179.2 [integration], T-179.3 [integration], T-179.4 [integration], T-179.5 [integration], T-179.6 [integration], T-179.7 [integration], T-179.8 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-180 Check the shape of each dependency file
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:378 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:536 @9961c9e
Acceptance (EARS):
- AC-180.1 If a `.yaml` file directly in `contracts/dependencies/` loads as a mapping that lacks one of `sends`, `expects`, `auth`, `limits`, `mock` and `failures`, the lint command shall report `contracts-valid` at the file's first key line with `missing <key>`, once for each missing key, in that order.
- AC-180.2 If `auth` is present and is not a mapping with a non-empty `secret`, the lint command shall report `contracts-valid` at the `auth` line with `auth must be a mapping with secret`.
- AC-180.3 If `failures` is present and not a mapping, the lint command shall report `contracts-valid` at the `failures` line with `failures must be a mapping with timeout, 4xx, 5xx and outage`.
- AC-180.4 If the `failures` mapping lacks `timeout`, `4xx`, `5xx` or `outage`, the lint command shall report `contracts-valid` with `failures: missing <key>`, once for each missing key, in that order, at the line of the mapping's first key (the `failures:` line when the mapping is written inline).
- AC-180.5 When a `.yaml` file lies in a subfolder of `contracts/dependencies/`, `contracts-valid` shall not check its shape.
Errors: -
Edge cases: the failure values are checked by `error-codes` (FR-184) → AC-180.4; the values of `sends`, `expects`, `limits` and `mock` are not checked → AC-180.1
Tests: T-180.1 [integration], T-180.2 [integration], T-180.3 [integration], T-180.4 [integration], T-180.5 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-181 Resolve each section 7 custom type to its files and validator
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:435 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:414 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:485 @9961c9e
Acceptance (EARS):
- AC-181.1 Where a row of a table in section 7 of prd.md has at least three cells, and its Validator cell, with white space and backticks removed from its ends, is neither empty nor `built-in`, the lint command shall treat the row as a custom type. Its type is the first cell with backticks and white space removed from its ends. Its files are the files in the PRD folder that a glob of its Files cell matches, the cell's backticks removed and its globs split on commas and white space, `**` matching any depth, each file once, sorted.
- AC-181.2 When a custom type's Validator cell is `pack`, the lint command shall take as its command the validator of the first resolved pack that declares the row's type with a validator other than `built-in`, the packs taken in the order the PRD names them and then the built-in service pack, with its `${PACK}` expanded; if no such pack does, it shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: no named pack declares contract type <type>`.
- AC-181.3 If a custom type's globs match no file in the PRD folder, the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: glob matches no file`, and shall not run its validator.
- AC-181.4 If a glob of a custom type matches a file that, its path made absolute and `..` resolved, lies outside the PRD folder, the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: file <path> is outside the PRD folder`, `<path>` written as the glob gives it, once for each such file, before any other finding for the type, and shall not pass that file to the validator.
Errors: -
Edge cases: a row with fewer than three cells is no custom type → AC-181.1; an absolute glob and one that climbs out with `..` are both checked → AC-181.4; a type whose only matches lie outside gets both the AC-181.4 and the AC-181.3 finding → AC-181.3; with links.md, a file under `contracts/upstream/` is not a file of the type (links, not adopted) → AC-181.1; a named pack that does not resolve is skipped (packs, not adopted) → AC-181.2; the service pack declares only built-in types, so a `pack` row with no Pack line is always reported → AC-181.2
Tests: T-181.1 [integration], T-181.2 [integration], T-181.3 [integration], T-181.4 [integration], T-181.5 [integration], T-181.6 [integration], T-181.7 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-182 Run each custom type's validator and report its failure
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:479 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:472 @9961c9e
Acceptance (EARS):
- AC-182.1 When a custom type has a command and at least one file, the lint command shall run the command, split into words as a POSIX shell splits them, with the type's files appended as arguments (paths relative to the PRD folder), with no shell and with the PRD folder as working directory, and shall report no finding for the type when the command exits 0.
- AC-182.2 If the Validator cell does not split into words (an unclosed quote), the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: validator does not parse: <reason>`, `<reason>` being the splitter's message (`No closing quotation`).
- AC-182.3 If the command's first word names no program that can be found, the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: validator not found: <first word>`.
- AC-182.4 If the system refuses to execute the program the first word names for lack of permission, the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: validator not executable: <first word>`.
- AC-182.5 If the validator runs longer than the timeout, the lint command shall stop it and report `contracts-valid` at the row's line in prd.md with `custom type <type>: validator timed out after <t>s`, `<t>` being the timeout in seconds.
- AC-182.6 The lint command shall read the timeout from the environment variable `PRD_VALIDATOR_TIMEOUT` as an integer number of seconds, and shall use 120 when the variable is unset or is not an integer.
- AC-182.7 If the validator exits other than 0, the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: validator failed: <line>`, `<line>` being the first line of its standard error that holds a character other than white space, else the first such line of its standard output, else `exit <code>`.
- AC-182.8 If the system refuses to run the command for a reason other than those of AC-182.3 and AC-182.4 (a file with its execute bit but no `#!` line that is not a program, an argument list too long), the lint command shall report `contracts-valid` at the row's line in prd.md with `custom type <type>: validator cannot run: <first word>: <reason>`, `<reason>` being the system's message for the error, and shall not exit 2.
Errors: -
Edge cases: the output is decoded as UTF-8 with undecodable bytes replaced → AC-182.7; the line is reported as written, leading white space kept → AC-182.7; a program the system cannot execute for another reason is a finding, never an internal error → AC-182.8
Tests: T-182.1 [integration], T-182.2 [integration], T-182.3 [integration], T-182.4 [integration], T-182.5 [integration], T-182.6 [integration], T-182.7 [integration], T-182.8 [integration], T-182.9 [integration], T-182.10 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-183 Check each backticked table.column against schema.sql
Status: live (since 9.6.0)
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:555 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:44 @9961c9e
Acceptance (EARS):
- AC-183.1 Where `contracts/schema.sql` parses and holds at least one `CREATE TABLE`, if a code span on a line outside fenced code blocks of a Markdown file of the PRD folder other than errors.md holds exactly `<a>.<b>` once white space is removed from its ends (each name a letter or underscore followed by letters, digits or underscores), `<a>` is a table of schema.sql, and `<b>` is neither one of its columns, both compared as schema.sql writes them, case included, nor one of `csv`, `tsv`, `sql`, `yaml`, `yml`, `json`, `md`, `txt` and `lkml`, the lint command shall report `schema-refs` at that line with `` `<a>.<b>`: table <a> has no column <b> ``, once for each such span.
- AC-183.2 When a span's first name is not a table of schema.sql, its second name is one of the AC-183.1 file extensions, its line is in errors.md, or its line is inside a fenced code block or is a fence line, the lint command shall report no `schema-refs` finding for it.
- AC-183.3 While `contracts/schema.sql` is absent, does not parse, or holds no `CREATE TABLE`, the lint command shall report no `schema-refs` finding.
Errors: -
Edge cases: a line that starts, after white space, with three backticks or three tildes opens or closes a fence, whichever kind it is → AC-183.2; the columns of several `CREATE TABLE` statements for one table are pooled → AC-183.1; prose names a table and column as schema.sql writes them, so a span in another case names no table and is not checked → AC-183.2
Tests: T-183.1 [integration], T-183.2 [integration], T-183.3 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-184 Report a cited error code the catalogue lacks
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:617 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:589 @9961c9e
Acceptance (EARS):
- AC-184.1 Where `contracts/errors.yaml` loads as a mapping, if a code the loader reads from a block's `Errors:` line is not a key of it, the lint command shall report `error-codes` at the Errors line with `error code <code> is not in contracts/errors.yaml`.
- AC-184.2 Where the catalogue loads as a mapping, if a string in the `x-error-codes` of an operation under `paths` or `webhooks` of `contracts/openapi.yaml` is not a key of it, the lint command shall report `error-codes` at the `x-error-codes` line with `error code <code> is not in contracts/errors.yaml`; an `x-error-codes` that is a single string counts as a list of that one code.
- AC-184.3 Where the catalogue loads as a mapping, if a value of the `failures` mapping of a dependency file (a `.yaml` file directly in `contracts/dependencies/`), or a string in a value that is a list, is not a key of it, the lint command shall report `error-codes` at that failure key's line with `error code <code> is not in contracts/errors.yaml`.
- AC-184.4 The lint command shall report no `error-codes` finding for a code that only a test case's `expect.errors` names.
- AC-184.5 While `contracts/errors.yaml` is absent or does not load as a mapping, the lint command shall report no `error-codes` finding.
Errors: -
Edge cases: a removed block's Errors line is read too → AC-184.1; `test-refs` reports a test case's uncatalogued code (lint-testcases FR-161) → AC-184.4; the loader reports a catalogue that is not a mapping (lint-cli FR-012) → AC-184.5; the items of a list that are not strings are skipped → AC-184.2; a file in a subfolder of `contracts/dependencies/` is no dependency file, so its failures cite nothing → AC-184.3
Tests: T-184.1 [integration], T-184.2 [integration], T-184.3 [integration], T-184.4 [integration], T-184.5 [integration], T-184.6 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint

### FR-185 Report a catalogued error code cited nowhere
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/contracts.py:626 @9961c9e
  prd-toolkit/scripts/prdlint/rules/contracts.py:607 @9961c9e
Acceptance (EARS):
- AC-185.1 If a key of `contracts/errors.yaml` is cited by no source of AC-184.1 to AC-184.3, and no test case's `expect.errors` (a string, or a list of strings) names it, the lint command shall report `error-codes` at the key's line with `error code <code> is catalogued but cited nowhere`.
- AC-185.2 When a code is named only in a test case's `expect.errors`, the lint command shall report no AC-185.1 finding for it.
Errors: -
Edge cases: a code a test case names is used even if no block or contract cites it → AC-185.2; a code that only a file in a subfolder of `contracts/dependencies/` names is cited nowhere → AC-185.1
Tests: T-185.1 [integration], T-185.2 [integration], T-185.3 [integration]  (test-cases/lint-contracts.yaml)
Traces: UJ-01; cli:prd_lint
