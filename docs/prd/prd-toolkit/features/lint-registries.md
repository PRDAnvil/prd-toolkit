<!-- Format: references/prd-format.md, "Requirement blocks". -->

# lint-registries: the lint rules for the registries, the runbook and the error ledger

Behaviour already written in other areas, from this area's files: FR-016 (Levels Timeout), FR-017
(Environments Branch) and FR-018 (Check `matches`) in lint-cli; AC-063.2 (an entry's `URL:` line) in
card-context; AC-075.2 and AC-075.4 (the One test cell, the `runbook-tests` description) in error-replay.

### FR-132 Check the Decision of each registry row
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:82 @6162689
Flow: 1. read every row of every table in section 5, then in section 6 → 2. take the Decision cell (the fifth cell in section 5, the third in section 6), stripped and with its surrounding backticks removed
      → 3. report a value outside the table's set, and a `proposed` row while the PRD is Approved
Acceptance (EARS):
- AC-132.1 If a section 5 row's Decision cell, stripped and with surrounding backticks removed, is none of `enforced`, `declined` and `proposed`, the lint command shall report `registries` at the row's line in `prd.md` with `standards Decision '<decision>' is not one of enforced, declined, proposed`, and shall check nothing else on that row.
- AC-132.2 If a section 6 row's Decision cell, read the same way, is none of `required`, `recommended`, `declined` and `proposed`, the lint command shall report `registries` at the row's line with `skills Decision '<decision>' is not one of required, recommended, declined, proposed`, and shall check nothing else on that row.
- AC-132.3 When the frontmatter `status`, stripped, is `Approved` and a section 5 or section 6 row's Decision is `proposed`, the lint command shall report `registries` at the row's line with `standards row is still 'proposed' but the PRD is Approved` or `skills row is still 'proposed' but the PRD is Approved`.
- AC-132.4 While the frontmatter `status` is not `Approved`, the lint command shall report no `registries` finding for a `proposed` row.
- AC-132.5 When a Decision cell holds an allowed value in backticks, such as `` `declined` ``, the lint command shall read it as that value.
Errors: -
Edge cases: a section with no table, or a missing section, has no rows → AC-132.1; a short row reads its missing cells as empty, so a row with no Decision cell is reported with `''` → AC-132.1, AC-132.2; every table in the section is read, not only the first → AC-132.1; the header row's columns are the sections rule's (lint-structure)
Tests: T-132.1 [integration], T-132.2 [integration], T-132.3 [integration], T-132.4 [integration], T-132.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint

### FR-133 Check an enforced standard's linter command
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:87 @6162689
Flow: 1. for a section 5 row whose Decision is `enforced`, take the first backticked span of its Linter command cell → 2. split it into words as a POSIX shell does; the first word is the command
      → 3. report a row with no command, and, outside a CI run, a command that is not on PATH
Acceptance (EARS):
- AC-133.1 If an `enforced` section 5 row's Linter command cell holds no backticked span, or its first backticked span holds no word, the lint command shall report `registries` at the row's line with `enforced standards row has no linter command ('<cell>'); put it in backticks`, `<cell>` being the cell stripped, in a CI run as well as outside one.
- AC-133.2 If the first word of an `enforced` row's first backticked span (split with `shlex.split`, or on white space when the span's quotes do not balance) is not found on PATH, and the run is not a CI run, the lint command shall report `registries` at the row's line with `enforced linter command '<word>' is not on PATH`.
- AC-133.3 While `PRD_LINT_CI` is `1` (a CI run, FR-008), the lint command shall report no `is not on PATH` finding.
- AC-133.4 When a section 5 row's Decision is `declined` or `proposed`, the lint command shall not check its Linter command cell.
Errors: -
Edge cases: quotes group words, so `` `'no such linter' -x` `` names the command `no such linter` → AC-133.2; only the first word is looked up, so `` `uv run ruff` `` needs only `uv` → AC-133.2; a cell without backticks is reported even when its text names a command on PATH → AC-133.1; FR-008 owns how `--ci` sets `PRD_LINT_CI` (lint-cli)
Tests: T-133.1 [integration], T-133.2 [integration], T-133.3 [integration], T-133.4 [integration], T-133.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; setting PRD_LINT_CI (contracts/config.yaml)

### FR-134 Require a required skill to be installed
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:102 @6162689
Flow: 1. for a section 6 row whose Decision is `required`, outside a CI run, take the Skill cell, stripped and with its surrounding backticks removed
      → 2. `plugin:skill`: look the plugin up in the installed-plugins file; a bare name: look for its SKILL.md under the home folder and the repository root → 3. report a skill not found
Acceptance (EARS):
- AC-134.1 If a `required` row's skill is not installed and the run is not a CI run, the lint command shall report `registries` at the row's line with `required skill '<skill>' is not installed; if it is built into Claude Code, mark the row 'recommended'`.
- AC-134.2 Where the skill holds a `:`, the lint command shall treat the text before the first `:` as the plugin and the rest as the skill name. It shall count the skill installed when the installed-plugins file has a key that starts with `<plugin>@`, and either no install under such a key records a string `installPath`, or `<installPath>/skills/<name>/SKILL.md` is a file for at least one install that does.
- AC-134.3 Where the skill holds no `:`, the lint command shall count it installed when `.claude/skills/<skill>/SKILL.md` is a file under the home folder (`HOME`), or under the repository root: the `git rev-parse --show-toplevel` of the PRD folder, or the PRD folder itself when git finds no checkout there.
- AC-134.4 While `PRD_LINT_CI` is `1`, the lint command shall not check whether a `required` skill is installed.
- AC-134.5 When a section 6 row's Decision is `recommended`, `declined` or `proposed`, the lint command shall not check whether its skill is installed.
Errors: -
Edge cases: the installed-plugins file is `PRD_PLUGINS_FILE` when set, else `~/.claude/plugins/installed_plugins.json`, and a missing or unreadable file lists no plugin (packs area, not adopted) → AC-134.2; the plugin key must start with `<plugin>@`, so `foobar@m` does not install `foo:bar` → AC-134.2; the repository root is looked up once per lint run → AC-134.3; a skill built into Claude Code that a row marks `required` gets no finding of its own: it is reported as not installed, with the hint to mark it `recommended` → AC-134.1
Tests: T-134.1 [integration], T-134.2 [integration], T-134.3 [integration], T-134.4 [integration], T-134.5 [integration], T-134.6 [integration], T-134.7 [integration], T-134.8 [integration], T-134.9 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; setting PRD_PLUGINS_FILE (contracts/config.yaml); setting PRD_LINT_CI (contracts/config.yaml)

### FR-135 Number the runbook's steps and give each its actor and environment
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:130 @6162689
Flow: 1. read the runbook steps of operations.md in order → 2. compare each step's number with the one expected → 3. report each repeated label → 4. report a step line without `(actor: …) (env: …)`, and check nothing more on it
Acceptance (EARS):
- AC-135.1 If a runbook step's number is not the expected number, the lint command shall report `runbook-steps` at the step's line with `step <n>: expected step <expected>`. The expected number is 1 for the first step, and one more than the previous step's own number for every later step.
- AC-135.2 If a step's indented lines hold a label (`Run:`, `Check:`, `Rollback:` or `Do:`) a second time, the lint command shall report `runbook-steps` at the later line with `step <n>: label <label> appears twice`, `<label>` written without its colon, once for each repeat.
- AC-135.3 If a step line does not end with `(actor: agent)` or `(actor: human)` followed by `(env: <environment>)`, the lint command shall report `runbook-steps` at the step's line with `step <n>: the step line needs (actor: agent|human) (env: <environment>)`, and shall check no label of that step.
- AC-135.4 When the runbook has steps, no step line carries an `(env: …)` part in that form, and the text of operations.md holds no `(env:` anywhere, the lint command shall add ` (prd-toolkit 0.5 runbook format)` to the end of the first `runbook-steps` message the rule produces, and to no other.
- AC-135.5 If operations.md does not exist, the lint command shall report no `runbook-steps` finding.
Errors: -
Edge cases: the first of two same labels is the one used (lint-cli, the loader) → AC-135.2; a gap is reported once, at the step after it, and numbering goes on from that step → AC-135.1; a step line with `(actor: …)` alone, the 0.4 form, gets AC-135.3's message → AC-135.3; a step line inside a code fence is no step (lint-cli, the loader)
Tests: T-135.1 [integration], T-135.2 [integration], T-135.3 [integration], T-135.4 [integration], T-135.5 [integration], T-135.6 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook

### FR-136 Give a human step Do and Check only
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:142 @6162689
Acceptance (EARS):
- AC-136.1 If a step whose actor is `human` has a `Run:` or a `Rollback:` line, the lint command shall report `runbook-steps` at the `Run:` line, or at the `Rollback:` line when the step has no `Run:`, with `step <n>: a human step takes Do: and Check:, not <labels>`, `<labels>` being `Run:`, `Rollback:` or `Run: or Rollback:`.
- AC-136.2 If a human step has neither a `Run:` nor a `Rollback:` line and lacks a `Do:` or a `Check:` line, the lint command shall report `runbook-steps` at the step's line with `step <n>: a human step needs Do: and Check:`.
Errors: -
Edge cases: a human step with `Run:` and no `Do:` gets only AC-136.1's finding → AC-136.1; the text of a human step's `Do:` and `Check:` is prose and is not checked → AC-136.2
Tests: T-136.1 [integration], T-136.2 [integration], T-136.3 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook

### FR-137 Check an agent step's Run, Check and Rollback
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:149 @6162689
Flow: 1. an agent step: report a `Do:` line → 2. require `Run:`, and its form → 3. a step that is not a tests step: require `Check:`, and its form → 4. check `Rollback:`'s form when present
Acceptance (EARS):
- AC-137.1 If a step whose actor is `agent` has a `Do:` line, the lint command shall report `runbook-steps` at the `Do:` line with `step <n>: an agent step takes Run:, Check: and Rollback:, not Do:`.
- AC-137.2 If an agent step has no `Run:` line, the lint command shall report `runbook-steps` at the step's line with `step <n>: an agent step needs Run:`.
- AC-137.3 If an agent step's `Run:` value is neither one backticked command nor `tests` followed by white space and text, and holds no `[NEEDS CLARIFICATION:`, the lint command shall report `runbook-steps` at the `Run:` line with `step <n>: Run: must be one backticked command or tests <level>[, <level>]; got '<value>'`.
- AC-137.4 If an agent step that is not a tests step has no `Check:` line, the lint command shall report `runbook-steps` at the step's line with `step <n>: an agent step needs Check:`.
- AC-137.5 If such a step's `Check:` value is not one backticked command, optionally followed by `prints` and a backticked text or `matches` and a backticked pattern, holds each form at most once, holds no `[NEEDS CLARIFICATION:`, and does not hold both `prints` and `matches`, the lint command shall report `runbook-steps` at the `Check:` line with ``step <n>: Check: must be one backticked command, optionally followed by prints `<text>`; got '<value>'``.
- AC-137.6 If an agent step's `Rollback:` value is not one backticked command and holds no `[NEEDS CLARIFICATION:`, the lint command shall report `runbook-steps` at the `Rollback:` line with `step <n>: Rollback: must be one backticked command; got '<value>'`.
- AC-137.7 When a `Run:`, `Check:` or `Rollback:` value holds `[NEEDS CLARIFICATION:`, the lint command shall report no `runbook-steps` finding on its form.
Errors: -
Edge cases: `<value>` is the label's text after the colon, stripped → AC-137.3, AC-137.5, AC-137.6; a Check with both `prints` and `matches`, and a `matches` pattern that does not compile, are FR-018's (lint-cli) → AC-137.5; an open marker is the markers rule's (lint-structure FR-029) → AC-137.7; `Run: tests` with nothing after it is not a tests step and gets AC-137.3 → AC-137.3
Tests: T-137.1 [integration], T-137.2 [integration], T-137.3 [integration], T-137.4 [integration], T-137.5 [integration], T-137.6 [integration], T-137.7 [integration], T-137.8 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook

### FR-138 Check the form of a runbook tests step
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:155 @6162689
Acceptance (EARS):
- AC-138.1 If an agent step's `Run:` is `tests` followed by white space and a comma-separated list that names no level once each item is stripped, the lint command shall report `runbook-steps` at the `Run:` line with `step <n>: a tests step names no levels`.
- AC-138.2 If a tests step has a `Check:` line, the lint command shall report `runbook-steps` at the `Check:` line with `step <n>: a tests step has no Check:`.
- AC-138.3 If a tests step's `Rollback:` value is not one backticked command and holds no `[NEEDS CLARIFICATION:`, the lint command shall report `runbook-steps` at the `Rollback:` line with `step <n>: Rollback: must be one backticked command; got '<value>'`.
- AC-138.4 When a tests step has no `Check:` line, the lint command shall report no `an agent step needs Check:` finding for it.
Errors: -
Edge cases: `Run: tests ,` names no level → AC-138.1; whether each named level exists and is deploy-gate is FR-142's → AC-138.1
Tests: T-138.1 [integration], T-138.2 [integration], T-138.3 [integration], T-138.4 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook

### FR-139 Keep the Environments tables in step and mark production
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:202 @6162689
Flow: 1. for each operations.md Environments row: check it is a testing.md Environments row and, with a Production column, that its cell is yes or no
      → 2. with at least one row: report a missing Production column, or no row whose Production is yes
Acceptance (EARS):
- AC-139.1 If an environment of operations.md's Environments table is not a row of testing.md's Environments table, the lint command shall report `runbook-env` at its row in `operations.md` with `environment '<env>' is in operations.md but not in testing.md Environments`.
- AC-139.2 If the Environments table has a column whose header, stripped, without backticks and in lower case, is `production`, and a row's cell in it, stripped and with backticks removed, is neither `yes` nor `no`, the lint command shall report `runbook-env` at the row with `environment '<env>': Production '<cell>' is not yes or no`.
- AC-139.3 If the Environments table has rows and no such column, the lint command shall report `runbook-env` at its first row with `operations.md Environments has no Production column`.
- AC-139.4 If the table has the column and no row's cell is `yes`, the lint command shall report `runbook-env` at its first row with `operations.md Environments: no environment has Production yes`.
- AC-139.5 If operations.md does not exist, the lint command shall report no `runbook-env` finding.
Errors: -
Edge cases: `Yes` is not `yes` → AC-139.2; an Environments table with no rows gives neither AC-139.3 nor AC-139.4 → AC-139.3; the Branch cell is FR-017's (lint-cli)
Tests: T-139.1 [integration], T-139.2 [integration], T-139.3 [integration], T-139.4 [integration], T-139.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Environments; testing.md Environments

### FR-140 Name a known environment on each step, Deployed row and Drift row
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:216 @6162689
Acceptance (EARS):
- AC-140.1 If a runbook step's `(env: …)`, a `## Deployed` row's Environment or a `## Drift` row's Environment names an environment that operations.md's Environments table does not hold, the lint command shall report `runbook-env` at that step or row with `<prefix>environment '<env>' is not in operations.md Environments`, followed by ` (did you mean '<name>'?)` when an environment of that table differs from `<env>` only in letter case. `<prefix>` is `step <n>: `, `Deployed row: ` or `Drift row: `.
- AC-140.2 If that environment is in operations.md's Environments table but not in testing.md's, the lint command shall report `runbook-env` at the step or row with `<prefix>environment '<env>' is not in testing.md Environments`.
Errors: -
Edge cases: a step line that has no `(env: …)` part in the grammar's form is not checked here → AC-140.1; the environment in `(env: …)` may be in backticks (lint-cli, the loader) → AC-140.1; an environment missing from both tables gets AC-140.1's finding only → AC-140.2
Tests: T-140.1 [integration], T-140.2 [integration], T-140.3 [integration], T-140.4 [integration], T-140.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook, Deployed and Drift

### FR-141 Put a human step at or just before each production environment's first step
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:225 @6162689
Acceptance (EARS):
- AC-141.1 If, for an environment whose Production cell is `yes`, the first runbook step that names it is not a `human` step and the step directly before it is not a `human` step (or there is none), the lint command shall report `production-gate` at that step's line with `step <n> deploys <env> with no human step at or just before it`.
- AC-141.2 When that first step is a `human` step, or directly follows one, the lint command shall report no `production-gate` finding for the environment.
Errors: -
Edge cases: a production environment that no step names gives no finding → AC-141.1; the step directly before is checked whatever its environment, so a human step on staging gates a following production step → AC-141.2; production environments are checked in sorted order → AC-141.1
Tests: T-141.1 [integration], T-141.2 [integration], T-141.3 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook

### FR-142 Run only deploy-gate levels that have a Harness command
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:247 @6162689
Acceptance (EARS):
- AC-142.1 If a level that a runbook tests step names is not a row of testing.md's Levels table, the lint command shall report `runbook-tests` at the step's `Run:` line with `step <n>: level '<level>' is not in testing.md Levels`.
- AC-142.2 If the level's Gate is not `deploy`, the lint command shall report `runbook-tests` at the `Run:` line with `step <n>: level '<level>' has Gate <gate>; a tests step runs deploy-gate levels`, `<gate>` being `none` when the Gate is blank or the table has no Gate column.
- AC-142.3 If the level's Gate is `deploy`, its Harness command cell has no backticked command, and the cell holds no `[NEEDS CLARIFICATION:`, the lint command shall report `runbook-tests` at the `Run:` line with `step <n>: level '<level>' has no Harness command`.
- AC-142.4 When the Harness command cell holds `[NEEDS CLARIFICATION:`, the lint command shall report no `has no Harness command` finding.
Errors: -
Edge cases: each named level is checked on its own, in the order the step names them → AC-142.1; the Timeout and One test cells are FR-016's (lint-cli) and FR-075's (error-replay)
Tests: T-142.1 [integration], T-142.2 [integration], T-142.3 [integration], T-142.4 [integration], T-142.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Runbook; testing.md Levels

### FR-143 Check each Drift row's Check
Status: approved
Source: prd-toolkit/scripts/prdlint/rules/registries.py:260 @6162689
Acceptance (EARS):
- AC-143.1 If a `## Drift` row's Check cell, stripped and with surrounding backticks removed, is `schema`, the lint command shall report `drift-rows` at the row with `check 'schema' is not version or config`, as AC-143.2 does for any other unknown check; the message names no release.
- AC-143.2 If the cell is neither `version` nor `config`, the lint command shall report `drift-rows` at the row with `check '<check>' is not version or config`.
- AC-143.3 If the cell is `config` and the PRD folder has no file `contracts/config.yaml`, the lint command shall report `drift-rows` at the row with `a config drift row needs contracts/config.yaml`.
Errors: -
Edge cases: the comparison is case-sensitive, so `Version` is reported → AC-143.2; only the first table under `## Drift` is read (lint-cli, the loader); with no Drift table nothing is checked
Tests: T-143.1 [integration], T-143.2 [integration], T-143.3 [integration], T-143.4 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; operations.md Drift; contracts/config.yaml

### FR-144 Number errors.md entries from E-001 upward
Status: verified
Source: prd-toolkit/scripts/prdlint/rules/errors.py:24 @6162689
Flow: 1. read the entries in file order, keeping the highest number so far → 2. first entry: report the numbers below it → 3. a later entry: report one at or below the highest so far, or the numbers skipped above it
Acceptance (EARS):
- AC-144.1 If the first entry's number is above 1 and no later entry carries a number below it, the lint command shall report `error-entries` at the entry's heading with `<E-id> is the first entry: <missing> <tail>`.
- AC-144.2 If a later entry's number is more than one above the highest number so far, and no entry after it carries a skipped number, the lint command shall report `error-entries` at its heading with `<E-id> follows <previous E-id>: <missing> <tail>`, the previous entry being the one directly above it in the file.
- AC-144.3 If a later entry's number is at or below the highest number so far, the lint command shall report `error-entries` at its heading with `<E-id> follows <previous E-id>: entries run from E-001 upward, newest last`.
- AC-144.4 When the lint command reports AC-144.1's or AC-144.2's finding, it shall write `<missing>` and `<tail>` as follows: for one number, the ID and `is missing; entries are never deleted, restore it from git`; for two, the two IDs joined by `, ` and `are missing; entries are never deleted, restore them from git`; for three or more, ``<first> to <last>`` and that same plural tail. IDs are written `E-` and three digits.
- AC-144.5 When the entries run E-001, E-002 and on with no gap, in that order, the lint command shall report no sequence finding.
- AC-144.6 If a later entry carries a number that an earlier entry skipped, the lint command shall report no AC-144.1 or AC-144.2 finding for that number, and shall report the later entry as AC-144.3 says.
Errors: -
Edge cases: a second heading with an ID already seen is no entry here; the loader keeps the first (lint-cli), and `id-unique` reports it (lint-ids FR-122); a heading in a code fence is no entry (lint-cli); a short ID such as `E-1` counts as number 1, and T-144.5 uses one for the out-of-order entry → AC-144.3; a skipped number that turns up later is no gap → AC-144.6
Tests: T-144.1 [integration], T-144.2 [integration], T-144.3 [integration], T-144.4 [integration], T-144.5 [integration], T-144.6 [integration], T-144.7 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; errors.md

### FR-145 Check an entry's Classification and Evidence
Status: verified
Source: prd-toolkit/scripts/prdlint/rules/errors.py:57 @3049c0d
Acceptance (EARS):
- AC-145.1 If an entry's `Classification:` value, stripped, is not empty and is none of `code bug`, `spec gap`, `invalid requirement`, `environment`, `standard`, `not a defect` and `unclassified`, the lint command shall report `error-entries` at that line with `<E-id>: Classification: '<value>' is not one of code bug, spec gap, invalid requirement, environment, standard, not a defect, unclassified`.
- AC-145.2 If an entry's Evidence holds more than 20 lines, the lint command shall report `error-entries` at its `Evidence:` line with `<E-id>: Evidence: is <n> lines; at most 20`. The lines are the text on the `Evidence:` line when it is not empty, plus each following line that starts with two spaces, up to the first line that does not.
- AC-145.3 When an entry's Evidence holds 20 lines or fewer, the lint command shall report no Evidence finding.
Errors: -
Edge cases: a missing or empty `Classification:` is not reported here; on a resolved entry it is `index-consistent`'s (lint-ids FR-127) → AC-145.1; a blank line ends the Evidence → AC-145.2; the comparison is case-sensitive, so `Code bug` is reported → AC-145.1; `not a defect` is a class since prd-toolkit 0.8.15 (error-reopen FR-253), so `Classification: not a defect` is no finding → AC-145.1
Tests: T-145.1 [integration], T-145.2 [integration], T-145.3 [integration], T-145.4 [integration], T-145.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; errors.md

### FR-146 Check an entry's Confirmed and Reopened lines
Status: verified
Source: prd-toolkit/scripts/prdlint/rules/errors.py:59 @3049c0d
Acceptance (EARS):
- AC-146.1 If an entry has a `Confirmed:` line whose value, stripped, is not a `YYYY-MM-DD` date, a comma, optional white space and a reply in double quotes that end the value, the lint command shall report `error-entries` at that line with `<E-id>: Confirmed: must be '<YYYY-MM-DD>, "<reply>"'`.
- AC-146.2 If an entry has a `Confirmed:` line and its `Classification:` value is `unclassified`, empty or absent, the lint command shall report `error-entries` at the `Confirmed:` line with `<E-id>: Confirmed: on an unclassified entry`.
- AC-146.3 When an entry with a class from AC-145.1's list other than `unclassified` has a well-formed `Confirmed:` line, the lint command shall report no `Confirmed:` finding.
- AC-146.4 If an entry has a line that starts with `Reopened:` whose value, stripped, is not a `YYYY-MM-DD` date, a comma, one space, a reason in double quotes, the text `; was Confirmed: `, a `YYYY-MM-DD` date, a comma, optional white space and a reply in double quotes that end the value, the lint command shall report `error-entries` at that line with `<E-id>: Reopened: must be '<YYYY-MM-DD>, "<reason>"; was Confirmed: <YYYY-MM-DD>, "<reply>"'`.
Errors: -
Edge cases: the date's digits are not checked against the calendar → AC-146.1; with two `Confirmed:` lines the last one counts (lint-cli, the loader); a malformed line on an unclassified entry gets both findings → AC-146.1, AC-146.2; each malformed `Reopened:` line gets its own finding, whatever the entry's state, and a well-formed one none (error-reopen FR-251 writes them) → AC-146.4
Tests: T-146.1 [integration], T-146.2 [integration], T-146.3 [integration], T-146.4 [integration], T-146.5 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; errors.md

### FR-147 Check Detected and Recurrence of on an entry with Confirmed
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/errors.py:52 @6162689
Acceptance (EARS):
- AC-147.1 If an entry that has a `Confirmed:` line has a `Detected:` line whose value does not start with a `YYYY-MM-DD` date, a comma, white space and a character that is not white space, the lint command shall report `error-entries` at the `Detected:` line with `<E-id>: Detected: must be "<YYYY-MM-DD>, <source>"`.
- AC-147.2 If an entry that has a `Confirmed:` line has a `Recurrence of:` value that is not empty and not `-`, the lint command shall split it on commas, strip each item, and report `error-entries` at the `Recurrence of:` line with `<E-id>: Recurrence of: <item> is not an entry` for each item that is not an entry's ID.
Errors: -
Edge cases: `2026-10-29,report` has no white space after the comma and is reported → AC-147.1; an entry with a `Confirmed:` line and no `Detected:` line gets no Detected finding → AC-147.1; on an entry with no `Confirmed:` line neither `Detected:` nor `Recurrence of:` is checked, which leaves entries written before prd-toolkit 0.6 as they are → AC-147.1
Tests: T-147.1 [integration], T-147.2 [integration], T-147.3 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_lint; errors.md

### FR-148 Describe each rule of the area
Status: live (since 9.4.0)
Source: prd-toolkit/scripts/prdlint/rules/registries.py:75 @6162689
Acceptance (EARS):
- AC-148.1 The help command, run as `prd_help.py --rule <name>`, shall print `<name> (error)` as its first stdout line for each of `registries`, `runbook-steps`, `runbook-env`, `production-gate`, `drift-rows` and `error-entries`.
- AC-148.2 The help command, run as `prd_help.py --rule registries`, shall print as its second stdout line `Checks the section 5 and 6 registries: each Decision is one of its table's values, no row is proposed while the PRD is Approved, an enforced standard has a backticked linter command on PATH, and a required skill is installed. Fix the Decision or the command, install the skill, or mark a skill built into Claude Code recommended.`
- AC-148.3 The help command, run as `prd_help.py --rule runbook-steps`, shall print as its second stdout line `Checks the operations.md runbook: steps numbered from 1 with no gap, each with (actor: agent|human) (env: <environment>), an agent step's Run:, Check: and Rollback: in their forms, a human step's Do: and Check:, and no label twice. Rewrite the step to the form the message gives.`
- AC-148.4 The help command, run as `prd_help.py --rule runbook-env`, shall print as its second stdout line `Checks that operations.md Environments has a Production column with yes or no on every row and at least one yes, and a valid branch name or blank in each Branch cell, that every environment there is also in testing.md Environments, and that each runbook step and Deployed or Drift row names an environment of both tables. Add the environment to both tables or correct the name the message gives, add the Production column or set a row's Production to yes or no, and write a valid branch name or leave the Branch blank.`
- AC-148.5 The help command, run as `prd_help.py --rule production-gate`, shall print as its second stdout line `Checks that the first runbook step on each production environment is a human step or directly follows one. Add a human approval step just before it.`
- AC-148.6 The help command, run as `prd_help.py --rule drift-rows`, shall print as its second stdout line `Checks that each Drift row's Check is version or config, and that a config row has contracts/config.yaml. Use one of the two checks, or add the config contract.`
- AC-148.7 The help command, run as `prd_help.py --rule error-entries`, shall print as its second stdout line `Checks errors.md entries: they run from E-001 upward with no gap, newest last; each has a known Classification, Evidence of at most 20 lines, and a Confirmed: in its form only on a classified entry; and an entry with Confirmed: also has Detected in its form and a Recurrence of that names an entry. Fix the line the message names, put an out-of-order entry back in sequence, and restore a deleted entry from git.`
Errors: -
Edge cases: `runbook-tests`'s description is AC-075.4's (error-replay); how help prints a rule is the help area's (FR-034)
Tests: T-148.1 [integration], T-148.2 [integration], T-148.3 [integration], T-148.4 [integration], T-148.5 [integration], T-148.6 [integration], T-148.7 [integration]  (test-cases/lint-registries.yaml)
Traces: UJ-01; cli:prd_help; cli:prd_lint
