<!-- Format: references/prd-format.md, "errors.md".
Entry lines in order: Detected, Classification, Confirmed, Touches, Evidence (at most 20 lines, continuation lines indented two spaces), Diagnosis, Resolution, Recurrence of. -->

# Error ledger

### E-001 A prd.md directory gets the lowercase-name hint
Detected: 2026-11-03, adoption extract of lint-cli (prd-toolkit/scripts/prdlint/model.py:713 @1cde4cc)
Classification: code bug
Confirmed: 2026-11-03, "Real bug — it should: When prd.md is a directory, lint says prd.md must be a file and exits 2. The lowercase-name hint appears only when a different name matches prd.md ignoring case."
Touches: FR-005
Diagnosis: When the folder holds a directory named exactly `prd.md`, `load` sets `names["prd.md"]` but `is_file()` is false, so it enters the refusal branch. Then `next(n for n in names if n.lower() == "prd.md")` finds that same entry, and the message reads `no prd.md; found prd.md; the file name is lowercase prd.md`, which tells the user to rename prd.md to prd.md. The comment at model.py:710 says the hint is for case-insensitive filesystems, where `PRD.md` "exists" as prd.md, and test_cli.py:28-33 tests only the `PRD.md` case. The search does not leave out the exact name.
Resolution: T-005.3 [integration], PRD 1.0.1, fixed in 0dd4037
Recurrence of: -

### E-002 The shared missing-package message always names prd_lint and its packages
Detected: 2026-11-03, adoption extract of lint-cli (prd-toolkit/scripts/prdlint/deps.py:13 @1cde4cc)
Classification: code bug
Confirmed: 2026-11-03, "Real bug — it should: The missing-package message names the script that failed and only the packages that script needs."
Touches: FR-010
Diagnosis: `deps.require` is documented as a general "Optional-import helper" (deps.py:1). Thirteen CLI scripts call it (prd_trace.py:17, prd_publish.py:19, prd_links.py:23 and others), and so do library modules (publish.py:16, context.py:14, snapshot.py:14). Its message always starts `prd_lint:` and always suggests `pip install pyyaml sqlglot openapi-spec-validator`. Under prd_publish.py, a missing `markdown-it-py` therefore prints `prd_lint: missing Python package 'markdown-it-py'. …, or: pip install pyyaml sqlglot openapi-spec-validator`. That names the wrong script and gives a pip command that does not install the missing package. The sibling scripts prefix their own messages with their own names (`prd_links: <why>`, commit a98746b; `prd_hooks: …`, commit f03ca0f). The text is right for prd_lint itself, so FR-010's case cannot show the bug.
Resolution: T-010.2 [integration], PRD 1.0.1, fixed in 0dd4037
Recurrence of: -

### E-003 An unhashable YAML mapping key crashes the load instead of being reported
Detected: 2026-11-03, adoption extract of lint-cli (prd-toolkit/scripts/prdlint/yamlload.py:35 @1cde4cc)
Classification: code bug
Confirmed: 2026-11-03, "Real bug — it should: A YAML key that is a list or a mapping is reported as a finding at its line, like any other malformed YAML, and lint keeps going"
Touches: FR-011, FR-012
Diagnosis: `_Loader.construct_line_map` runs `if key in data` on whatever the key node builds. A sequence or mapping key (`? [a, b]` or `{a: 1}: x`) builds a list or a LineDict, and that line raises `TypeError: unhashable type`. A TypeError is not a `yaml.YAMLError`, so it escapes `load_yaml`'s `except yaml.YAMLError` (yamlload.py:57) and `model.load`. prd_lint then exits 2 with `prd_lint: internal error: TypeError: …` and reports no finding. The docstring (yamlload.py:46-50) says a parse error becomes a `sufficiency` or `contracts-valid` finding and that the loader "Returns (None, findings) on error". PyYAML's own SafeConstructor, which this loader replaces for mappings, raises `ConstructorError("found unhashable key")`, a YAMLError, for the same input. FR-011's and FR-012's cases use only scalar keys.
Resolution: T-011.6 [integration], PRD 1.0.1, fixed in 0dd4037
Recurrence of: -

### E-004 The loader reads fixture data under contracts/fixtures/ as PRD documents and contract YAML
Detected: 2026-11-03, adoption extract of lint-cli (prd-toolkit/scripts/prdlint/model.py:717 @1cde4cc)
Classification: code bug
Confirmed: 2026-11-03, "Real bug — it should: Lint skips everything under contracts/fixtures/, as prd-format.md says."
Touches: FR-012
Diagnosis: `load` reads every `*.md` below the folder into its documents (model.py:717) and every `*.yaml` below `contracts/` into its contract YAML (model.py:758), reporting their parse errors, duplicate keys and non-mapping top levels under `contracts-valid`; neither glob leaves out `contracts/fixtures/`. prd-format.md (lines 168-169) says fixture data under `contracts/fixtures/` is not scanned, and the sibling `all_lines` skips raw YAML/SQL/JSON fixture files (rules/structure.py:62-64) but starts from `prose(prd)`, which walks fixture `.md` files too. So a fixture `.md` is read by placeholder, glossary-synonym, id-format, schema-refs, markers-open and assumption-indexed, and a fixture `.yaml` by the loader's contracts-valid findings, placeholder's YAML-value check, id-format and id-removed-reused.
Resolution: T-012.2 [integration], PRD 1.0.1, fixed in 0dd4037
Recurrence of: -

### E-005 A directory named `<name>.md` in the PRD folder is an internal error
Detected: 2026-11-03, lint-cli characterization suite, T-006.3 (prd-toolkit/scripts/prdlint/model.py:717 @0f89b47)
Classification: code bug
Confirmed: 2026-11-03, "Real bug (Recommended)"
Touches: FR-006
Diagnosis: `load` reads every path that `prd_dir.rglob("*.md")` yields with `read_text` (model.py:717) and does not check that it is a file, so a directory named `notes.md` raises `IsADirectoryError`. prd_lint reports it as `prd_lint: internal error: IsADirectoryError: [Errno 21] Is a directory: '…/notes.md'` and exits 2, where AC-006.3 (the owner's answer to Q-03) wants a `sufficiency` finding and the rules run.
Resolution: T-006.3 [integration], PRD 1.0.1, fixed in 0dd4037
Recurrence of: -

### E-006 --sample-tids samples a case with no level or a non-lowercase level
Detected: 2026-11-03, lint-cli characterization suite, T-007.5 (prd-toolkit/scripts/prd_lint.py:67 @0f89b47)
Classification: code bug
Confirmed: 2026-11-03, "Real bug (Recommended)"
Touches: FR-007
Diagnosis: The sample keeps every loaded case whose `str(level).strip()` is not `unit` (prd_lint.py:67). A case with no `level` gives `""` and one with `level: Unit` gives `Unit`, so both are sampled. T-007.5 printed `T-009.1 test-cases/odd.yaml` and `T-009.2 test-cases/odd.yaml` beside the nine expected lines, where AC-007.4 (the owner's answer to Q-02) samples neither.
Resolution: T-007.5 [integration], PRD 1.0.1, fixed in 0dd4037
Recurrence of: -

### E-007 lint crashes (internal error, exit 2) on a directory or broken symlink named `<name>.yaml` in test-cases/ or contracts/
Detected: 2026-11-07, user report (/prd-error)
Classification: invalid requirement
Confirmed: 2026-11-07, "Confirm the class (form)"
Touches: FR-006
Evidence: User report (/prd-error), verbatim:
    lint-cli: a directory or broken symlink named <name>.yaml in test-cases/ or contracts/ crashes lint
    (internal error, exit 2) instead of a sufficiency finding like AC-006.3.
    Repro: /private/tmp/claude-502/-Users-ihistand-projects/70d5ca74-4580-4373-ba48-6ff35310fa48/scratchpad/lintbug/ydir
Diagnosis: Reproduced once: `prd_lint.py <repro>/ydir`, where test-cases/sub.yaml is an empty directory, printed `prd_lint: internal error: IsADirectoryError: [Errno 21] Is a directory: .../test-cases/sub.yaml` and exited 2. Root cause: prdlint/model.py guards `.md` entries with `is_file()` (line 854, the E-005 fix), but the test-cases glob (line 887) and the contracts rglob (line 899) pass every `*.yaml` match, a directory or a broken symlink included, to load_yaml, whose open raises. The broken-symlink half is read from the code, not run: glob yields a dangling link and open raises FileNotFoundError. The code does what an AC says: AC-006.1 `If loading the folder raises an error other than a missing prd.md, the lint command shall print prd_lint: internal error: <exception type>: <message> to stderr ... and exit 2.` AC-006.3 gives the sufficiency finding only to `an entry of the folder whose name ends in .md`. The AC is wrong in scope: a non-file `.yaml` entry in test-cases/ or contracts/ is the same malformed-folder case E-005 fixed for `.md`, and should be a sufficiency finding at line 0, not an internal error.
Resolution: T-006.4 [integration], PRD 5.0.0, fixed in a0e9d4f
Recurrence of: E-005

### E-008 Cached uv script environments accumulate without bound in ~/.cache/uv/environments-v2
Detected: 2026-11-09, user report (GitHub issue #24)
Classification: spec gap
Confirmed: 2026-11-09, "Confirm the class (form)"
Evidence: Source: GitHub issue ihistand/claude-plugins#24, filed 2026-11-09 from a disk-space review.
  ~/.cache/uv/environments-v2 held 26,888 cached script environments; uv cache size reported 454.4GiB.
  Per script: prd-git-hook 8,632; prd-block 4,485; prd-deploy 3,466; prd-lint 2,535; prd-trace 1,747;
  prd-status 1,479; prd-links 1,336; prd-change 1,221; validate-outline 692; prd-gates 602; prd-error 470; prd-hooks 54.
  Each environment about 20 MB as listed (CPython 3.13, uv 0.13.7; pyyaml, jsonschema, openapi-spec-validator).
  New prd-git-hook environments per day: Nov 1 1,271; Nov 2 1,281; Nov 3 2,645; Nov 4 764; Nov 9 1,365.
  rm -rf of the folder freed about 89 GB of disk and about 27 million files (APFS clones made the listed size overstate it).
  During the rm, two new environments appeared from hook runs in another session:
  prd-git-hook-bda7e90cb225275c and prd-lint-d26ef0960b4cb95e (16:12), so the rm ended with Directory not empty.
Diagnosis: Root cause: uv keys a cached script environment on the script's path, not its contents or dependencies. Reproduced 2026-11-09 with uv 0.13.7: running `.prd-toolkit/prd_error.py` twice from one path reused one environment; a copy in a new folder built a second; the same path with the file edited reused it. Every distinct path a prd script runs from therefore leaves one environment in `~/.cache/uv/environments-v2` that nothing removes. Two sources make new paths: (1) the unit suite builds git repositories under pytest `tmp_path`, installs the hooks there and commits, so each shim runs `uv run --script "$prd_top/.prd-toolkit/prd_git_hook.py"` from a new path, and tests run vendored copies of scripts the same way; one run of `tests/test_hooks_install.py` (33 tests) added 4 `prd-git-hook` environments, and the full suite runs on every build, review fix and CI-parity run; (2) in real repositories each clone or worktree has its own `.prd-toolkit/`, so every new worktree adds environments for each script its hooks and skills run. Sections searched and found silent on cached environments, their count or their cleanup: prd.md technical context ("Each CLI script (`prd-toolkit/scripts/prd_*.py`) is a uv script with an inline dependency header, run as `uv run --script <script>`."), testing.md Harness (Lifecycle, Clean state: "Every test starts from its own pytest `tmp_path`"), nfr.md and operations.md; no AC in the lint-cli feature covers the hooks or test setup. No PRD line bounds what a test run or a hook run may leave in the user's uv cache.
Resolution: T-019.2 [integration], PRD 6.1.0, fixed in c7aa72aaed54ba4bcbe8af0ceb6d837bffbeea07
Recurrence of: -

### E-009 sections misquotes an unnumbered level-2 heading as `## None. <title>`
Detected: 2026-11-10, adoption extract of lint-structure (prd-toolkit/scripts/prdlint/rules/structure.py:150 @ae00c13)
Classification: code bug
Confirmed: 2026-11-10, "Real bug (form) — it should: When prd.md has a level-2 heading that is not one of the fourteen sections, numbered or not, lint reports sections at its line with unexpected section '<the heading as written>', e.g. unexpected section '## Notes'; it never prints None."
Touches: FR-022
Diagnosis: The section parser gives an unnumbered level-2 heading of prd.md (`## Notes`) the number None, and the finding is built as `unexpected section '## {a[0]}. {a[1]}'`, so it prints `unexpected section '## None. Notes'`, quoting a heading that is in no file. The sibling message on line 144 (`missing section '## <n>. <title>'`) and prd-format.md ("prd.md sections": level-2 headings, exactly these) quote a heading as it is written. The Python `None` reaching the message contradicts them.
Resolution: T-022.4 [integration], PRD 6.2.1, fixed in dbad7a3
Recurrence of: -

### E-010 vague-word reads code spans in an FR block's acceptance criteria
Detected: 2026-11-10, adoption extract of lint-structure (prd-toolkit/scripts/prdlint/rules/structure.py:290 @ae00c13)
Classification: code bug
Confirmed: 2026-11-10, "Real bug (form) — it should: In an FR block's ACs, vague-word ignores code spans the way it does for NFR lines: a listed word inside a code span is not reported, and a digit inside a code span does not count as a measurable number."
Touches: FR-028
Diagnosis: For an NFR block the rule blanks fenced code and inline code spans before matching (line 286). Commit 3b28e1a ("vague-word ignores code in NFR blocks") added this, and test_vague_word_ignores_inline_code_and_fences tests it. For an FR block it matches the raw AC text (`a.text`, line 290). An FR AC that names a flag such as `--secure` in a code span is therefore reported as `'secure' with no measurable number on the line`, and a digit inside a code span exempts a listed word outside it. prd-format.md ("lint ignores code spans", Requirement blocks) and the sibling NFR branch treat code as not prose.
Resolution: T-028.7 [integration], PRD 6.2.2, fixed in 76cf058
Recurrence of: -

### E-011 Markers in hidden Markdown files are scanned
Detected: 2026-11-10, adoption extract of lint-structure (prd-toolkit/scripts/prdlint/rules/structure.py:58 @ae00c13)
Classification: code bug
Confirmed: 2026-11-10, "Real bug (form) — it should: A file or folder under the PRD folder whose name starts with . is not part of the PRD: lint loads no Markdown from it, so no rule (markers, assumptions, placeholders, glossary, requirement blocks) reads it."
Touches: FR-027, FR-029, FR-030, FR-032
Diagnosis: `all_lines` yields every line of `prose(prd)`, which holds every Markdown file the loader read. The loader collects them with `rglob("*.md")` (model.py:869), which also matches hidden names such as `.notes.md` or `features/.draft.md`. markers-open and assumption-indexed therefore report markers in hidden Markdown files. The function's own docstring (structure.py:57: hidden or editor-backup files are skipped) and prd-format.md (Requirement blocks: hidden or editor-backup files are not scanned) say otherwise, and the raw-file branch (line 64) does skip any path part that starts with `.`.
Resolution: T-027.9 [integration], PRD 6.2.2, fixed in ca2cee4
Recurrence of: -

### E-012 A key missing from the frontmatter is reported at a body line of prd.md
Detected: 2026-11-10, adoption extract of lint-structure (prd-toolkit/scripts/prdlint/rules/structure.py:83 @ae00c13)
Classification: code bug
Confirmed: 2026-11-10, "Real bug (form) — it should: lint looks up a frontmatter key's line only inside the frontmatter block: a present key is reported at its own line, and a missing key always at prd.md:1, whatever lines below the frontmatter start with <key>:. The language-table and sql-dialect findings use the same lookup."
Touches: FR-020, FR-021
Diagnosis: `_fm_line` scans every line of prd.md for one that starts with `<key>:`, not only the frontmatter block, and falls back to the frontmatter's line only when none does. Suppose a key is absent from the frontmatter and a later line of prd.md starts with it, for example a configuration example in a fenced block of section 4 with a `language: python` or `owner: ops` line at column 0. Then the `missing key` finding, and a language-table finding for a PRD with no `language:` key, point at that body line. The helper's name (`_fm_line`) and its fallback to `prd.frontmatter_line` say the line is the frontmatter's.
Resolution: T-020.14 [integration], PRD 6.2.2, fixed in a184bc1
Recurrence of: -

### E-013 An empty Test roots list goes unreported when a marker sits elsewhere on the Layout line
Detected: 2026-11-10, adoption extract of lint-structure (prd-toolkit/scripts/prdlint/rules/structure.py:217 @ae00c13)
Classification: code bug
Confirmed: 2026-11-10, "Real bug (form) — it should: lint reports Test roots: lists no backticked directory whenever the list after Test roots: names no backticked directory and that list itself holds no [NEEDS CLARIFICATION marker; a marker elsewhere on the Layout line does not excuse it."
Touches: FR-025
Diagnosis: When `Test roots:` lists no backticked directory, the rule skips its finding if `[NEEDS CLARIFICATION` appears anywhere on the Layout bullet's line, including the convention text before `Test roots:`. Consider the template's Layout line with its first marker kept and its roots filled in without backticks (`Test roots: tests/`). It gives no `sections` finding, and in a Draft PRD no finding at all, although the guard will then block every write. prd-format.md (testing.md, Harness) reports a `Test roots:` that lists no backticked directory and holds no marker. The comment on line 217 names the case it skips as an unfilled marker, which markers-open reports. The loader already removes markers from the Test roots text alone (model.py:575).
Resolution: T-025.9 [integration], PRD 6.2.1, fixed in 876eda9
Recurrence of: -

### E-014 A repeated prd.md section or Harness slot is reported as out of order, not as a duplicate
Detected: 2026-11-10, confirmation of Q-01 (FR-022, FR-025)
Classification: code bug
Confirmed: 2026-11-10, "Confirm the class (form)"
Touches: FR-022, FR-025
Diagnosis: The order checks compare the present sections, and the present Harness slots, with the expected list (structure.py:146 and :210), so a section or slot that appears twice makes the lists differ and is reported as out of order. No finding names the duplicate, which sends the author looking for a misplaced section instead of the repeated one, often left by a merge.
Resolution: T-022.5 [integration], PRD 6.2.1, fixed in 1c7f45e
Recurrence of: -

### E-015 An empty section 13 passes open-questions-empty while the PRD is Approved
Detected: 2026-11-10, confirmation of Q-02 (FR-031)
Classification: code bug
Confirmed: 2026-11-10, "Confirm the class (form)"
Touches: FR-031
Diagnosis: open-questions-empty reports only the first body line of section 13 that is neither empty nor `None.` (structure.py:333), so a section 13 with no text at all gives no finding. prd-format.md says section 13 is the single line `None.` when there are no open questions, so an Approved PRD with an empty section 13 passes a rule meant to require that line.
Resolution: T-031.3 [integration], PRD 6.2.2, fixed in 0d5cc508ec826791c9da3348bc68d8b67a51deea
Recurrence of: -

### E-016 The adoption.md header finding is reported at line 1, not at the header's line
Detected: 2026-11-10, confirmation of Q-03 (FR-024)
Classification: code bug
Confirmed: 2026-11-10, "Confirm the class (form)"
Touches: FR-024
Diagnosis: The header-mismatch finding is built with line 1 (structure.py:193) although the table's own line is known (the parsed table's line). Every other adoption.md finding points at the line to fix, a row at its own line, so this one sends the author to the file's heading instead of the header row.
Resolution: T-024.7 [integration], PRD 6.2.2, fixed in 628895739af3e88bdf9c9d19fa6f3173638e0a54
Recurrence of: -

### E-017 test_validator_fails_defect fails when uv prints `Installed 1 package` on stderr
Detected: 2026-11-11, user report (/prd-error)
Classification: code bug
Confirmed: 2026-11-11, "Confirm the class (form)"
Evidence: User report (/prd-error), 2026-11-11: test_builtin_packs.py::test_validator_fails_defect is flaky.
  It sometimes fails when uv prints "Installed 1 package" on stderr.
  First seen during the move to PRDAnvil/prd-toolkit (0.8.6, 2026-11-10).
Diagnosis: Reproduced: the unit harness narrowed to `tests/test_builtin_packs.py` failed on both runs (run 1 `[no-purpose]`, run 2 `[not-md]`, 26 passed each), with `assert 'g: missing purpose' in 'Installed 1 package in 1ms'`. Root cause: the test's `_run` helper starts the document pack's validator as `uv run --script <validator>` without `--quiet`, and asserts on the first stderr line. The first validator run in each session builds the script's environment and uv prints `Installed 1 package` there; which parametrized case gets it depends on xdist scheduling, so a different case fails each time. Since NFR-019 (E-008) the session deletes `environments-v2` at the end of every run, so a narrowed run always rebuilds it; the full suite passes when another test builds the environment first. The test breaks testing.md Harness, Lifecycle: "A test runs a CLI script as a subprocess with the test's own interpreter, `python <repo>/prd-toolkit/scripts/<script>` (not `uv run --script`, whose own stderr lines would break the stderr assertions)". The validator itself is right, and the pack manifest the test checks already runs it as `uv run --quiet --script`. No AC covers the validator and the test cites no T-id: both sit outside every adopted area's Boundary.
Resolution: -
Recurrence of: -

### E-018 `prd_error.py check` reports `Detected: changed` on entries whose only change is the move's SHA remap (c8f48cf)
Detected: 2026-11-11, user report (/prd-error)
Classification: code bug
Confirmed: 2026-11-11, "Confirm the class (form)"
Evidence: User report (/prd-error), 2026-11-11: prd_error.py check over a range that includes c8f48cf
  reports `Detected: changed` on E-001..E-006 and E-009..E-013.
  c8f48cf is the move's filter-repo SHA remap (0.8.6): it rewrote old-repo SHAs in docs/prd to the new ones, provenance only.
  Seen on the E-009 close (check over the whole loop exited 1, every finding from an older commit) and on the E-010 close (95d26dd, check over ae00c13..HEAD failing on c8f48cf findings).
  A check started after c8f48cf (c8f48cf..HEAD) exits 0.
Diagnosis: not a defect: reproduced, `prd_error.py check docs/prd/prd-toolkit c8f48cf~1..HEAD` exits 1 with `Detected: changed` on E-001 to E-006 and E-009 to E-013, and the same check from c8f48cf exits 0. The findings are true: c8f48cf rewrote those entries' `Detected:` lines (for example `model.py:713 @d1a4146` became `@1cde4cc`), and `_structure` in `prdlint/errors.py` reports any `Detected:` that differs between two commits. The toolkit holds ledger lines fixed on purpose: changing-prds says of the errors.md ledger "existing entries stay as written", and running-an-error.md step 6 says "a changed `Detected:` line) cannot be fixed by an edit, and history is never rewritten, so report it with its commit". The move broke that rule once, deliberately, so every check over a range that spans c8f48cf reports it; a check from c8f48cf on is clean and stays clean. No PRD line covers `prd_error.py`: its `errors` area is not adopted. Accepting a provenance-only rewrite would be a new feature, not a fix.
Resolution: not a defect: the check is right: c8f48cf rewrote the `Detected:` lines of E-001 to E-006 and E-009 to E-013 once, during the move, and the toolkit keeps ledger lines as written ("existing entries stay as written"); a check from c8f48cf on exits 0
Recurrence of: -

### E-019 Seven eval scaffolds fail their own clean-tree check, so their cases never run
Detected: 2026-11-14, eval run for prd-toolkit 0.8.8 (claude plugin eval, 2026-11-14)
Classification: spec gap
Confirmed: 2026-11-14, "Confirm the class (form)"
Evidence: claude plugin eval ./prd-toolkit --runs 1 --model sonnet --scaffold, 2026-11-14, on a5223fc's parent 5af6330
  7 of 59 cases did not run, each with: scaffold failed (exit 1)
  deploy-by-hand-records
  deploy-close-live
  deploy-close-staging-only
  deploy-failure-no-improvise
  deploy-stops-at-human
  deploying-trigger
  review-edits-nothing
  Each scaffold ends with: test -z "$(git status --porcelain)"
  Run by hand in an empty directory, evals/deploy-close-live/scaffold.sh exits 1 and leaves:
  ?? CLAUDE.md
  ?? docs/prd/README.md
  ?? docs/prd/greet/README.md
  The same scaffold exits 1 the same way from main at fdcf473 (prd-toolkit 0.8.7).
Diagnosis: Reproduced twice by hand: `evals/deploy-close-live/scaffold.sh` exits 1 in an empty directory from this branch and from main at fdcf473 (0.8.7), so 0.8.8 did not cause it. Root cause: `evals/scaffolds/deploy_repo.py` (and the scaffold `review-edits-nothing` uses) runs the plugin `prd_hooks.py install`, then commits only `.gitignore` and `.prd-toolkit`; since prd-toolkit 0.8.4 `install` also writes the managed block in `CLAUDE.md` and the two README files under `docs/prd/`, which stay untracked, and seven scaffolds end with a clean-tree check (`git status --porcelain` must print nothing). The scaffolds were written before 0.8.4 (f818be0, 2026-11-01) and the later baselines ran single cases, so nothing noticed. Class against the PRD: no requirement, contract or test case covers the eval suite or its scaffolds (searched features/lint-cli.md, features/lint-structure.md, nfr.md and testing.md; adoption.md maps `prd-toolkit/skills/**` but not `prd-toolkit/evals/**`), so the PRD is silent. E-017, a defect in a test outside every adopted Boundary, was confirmed as a code bug; the same may be the owner's choice here. Any fix must keep the scaffold commits' fixed dates and check which graders pin a commit SHA, since committing three more files changes every later SHA.
Resolution: -
Recurrence of: -

### E-020 prd help prints a traceback and exits 1 when the catalogue file exists and cannot be read
Detected: 2026-11-15, final review of the 0.8.9 branch
Classification: spec gap
Confirmed: 2026-11-15, "I think the wording is good for E-020, it should remain as a spec gap. My thought is that this will rarely happen, as almost all of the PRDs will be authored by the prd_toolkit, so keeping it as a spec gap is the best way to handle it."
Touches: FR-036
Evidence: Final review of the 0.8.9 branch, 2026-11-15:
  chmod 000 unread.yaml
  PRD_HELP_FILE=<tmp>/unread.yaml prd-toolkit/scripts/prd help
  Traceback ... helpcat.py line 90 ... PermissionError: [Errno 13] Permission denied: '<tmp>/unread.yaml'
  exit=1
  The same with --json (stdout is empty: no error document) and with --key a.
Diagnosis: Reproduced once: with `PRD_HELP_FILE` naming a file of mode 000, `prd help --json` prints a Python traceback ending `PermissionError: [Errno 13] Permission denied`, nothing on stdout, exit 1. Root cause: `load()` in `prd-toolkit/scripts/prdlint/helpcat.py` checks `is_file()`, then calls `read_bytes()` and catches only the YAML error, so an OSError from the read escapes. Class against the PRD: AC-036.3 says "If the catalogue cannot be used, the help command shall print the one stderr line `prd_help: <path>: <reason>`, print nothing on stdout and exit 2", where the reason "is the first that applies of: `no such file`; `YAML parse error: <the parser's problem>`; `top level must be a list`" and the entry reasons; none of them applies to a file that exists and cannot be read, and no test case covers it, so the PRD does not say which line to print. The FR-036 edge cases "exit 1 is never used" and "no exit-2 path prints a traceback" show the intent. The fix adds a reason to AC-036.3 (for example `cannot read: <the system's reason>`), a test case, and the catch in `load()`.
Resolution: T-036.6 [integration], PRD 8.0.0, fixed in 619f073
Recurrence of: -

### E-021 A section 13 question that ends in spaces gets a second full stop in the Next part
Detected: 2026-11-15, final review of the 0.8.10 branch
Classification: invalid requirement
Confirmed: 2026-11-15, "I merged PR #17, the class is right"
Touches: FR-044, FR-047
Evidence: Final review of the 0.8.10 branch, 2026-11-15:
  Section 13 of prd.md holds the lines "- Trailing spaces?   " and "Plain line!  " (each ends in spaces).
  prd status prints:
  1. An open question waits: Trailing spaces?   .
  2. An open question waits: Plain line!  .
Diagnosis: Reproduced once on a scratch copy of fixture status-next/base whose section 13 line is `- Trailing spaces?` followed by three spaces: `prd status` prints `2. An open question waits: Trailing spaces?` then the three spaces and a full stop. Root cause: `_open_questions` in `prd-toolkit/scripts/prdlint/nextpart.py` keeps the trailing spaces of a section 13 line, and `_sentence` then finds no closing mark at the end and adds a full stop. Class against the PRD: the code does what the criteria say. AC-044.2 says "a line that starts with `- ` begins a question whose text is the line without its `- `", so the spaces are part of the text, and AC-047.1 adds no full stop only "Where the text a sentence of FR-043 to FR-046 inserts last already ends in `.`, `?` or `!`", which a text ending in spaces does not. The criteria are wrong for a line that ends in white space: the title of FR-047 is "A sentence ends with one full stop", and the sentence the reader sees ends with two marks. The fix revises AC-044.2 (the text of a question has no leading or trailing white space) with a test case, then the code.
Resolution: T-044.7 [integration], PRD 8.0.0, fixed in 0de147a
Recurrence of: -

### E-022 The prd launcher fails when the working directory holds a .venv whose interpreter cannot be read
Detected: 2026-11-15, eval run for prd-toolkit 0.8.11 (claude plugin eval, 2026-11-15)
Classification: spec gap
Confirmed: 2026-11-15, "spec gap is right, start task 5"
Evidence: Eval run for prd-toolkit 0.8.11 (claude plugin eval, 2026-11-15), in the eval sandbox, in a scaffold repository that holds a .venv:
  <plugin>/scripts/prd lint docs/prd/notes; echo "prd-lint-exit=$?"
  error: Failed to inspect Python interpreter from virtual environment at `.venv/bin/python`
    cause: Failed to query Python interpreter
    cause: failed to canonicalize path `<tmp>/home/cwd/.venv/bin/python`: Operation not permitted (os error 1)
  The same from prd context and prd status. Fifteen of 34 eval cases stopped at their first prd command.
  The same case (building-trigger) fails the same way against the released 0.8.10 plugin.
Diagnosis: Reproduced once outside the eval sandbox: in a folder whose `.venv/bin/python` is a link into a directory with no read permission (and a `pyvenv.cfg` beside it), `prd-toolkit/scripts/prd --version` prints uv's `error: Failed to inspect Python interpreter from virtual environment at .venv/bin/python` with the cause `failed to canonicalize path`, and exits 2 before any script runs. Root cause: the launcher runs `uv run --quiet --no-project --project "$here" --python ">=3.11" --with-requirements …`, and uv, looking for an interpreter, inspects a `.venv` in the working directory first and treats one it cannot read as a hard error instead of passing over it. In the eval sandbox the scaffold's `.venv` links to a uv-managed Python under the home directory, which the sandbox does not let the session read, so every `prd` command of 15 of the 34 cases run for 0.8.11 failed; one of them, run against the released 0.8.10 plugin, fails the same way, so 0.8.11 did not cause it. The same cases ran in the 0.8.8 baseline of 2026-11-14 with the same uv and Claude Code versions; what changed on the machine since is not found. Class against the PRD: no requirement, contract or test case covers the launcher (searched features/lint-cli.md, features/help.md, features/status-next.md, features/practices.md, nfr.md and testing.md for the launcher, uv and a repository `.venv`; adoption.md maps `prd-toolkit/scripts/prd` in `trace-and-hooks`, which is not started), so the PRD is silent on what the launcher does when the repository's own environment cannot be read. A fix would make the launcher ignore the working directory's environment (the uv option or variable to be confirmed against uv's documentation) and add a test with an unreadable `.venv`.
Resolution: T-069.3 [integration], PRD 8.1.0, fixed in 144d179
Recurrence of: -

### E-023 An error-class answer given in the inbox is committed in every worktree that holds the PRD
Detected: 2026-11-15, user report from a repository that vendors 0.8.10
Classification: spec gap
Confirmed: 2026-11-17, "both are right"
Evidence: Report from a repository that vendors prd-toolkit 0.8.10, 2026-11-15:
  The repository has its main checkout on one branch and a worktree on another; both hold the PRD folder.
  From the worktree: prd gates serve <prd> --gate approval:<branch>, and prd gates wait.
  In that inbox the owner also answered eleven error-class gates, E-001 to E-011 ("Confirm the class (form)").
  Each confirmation was committed twice: once on the worktree's branch and once on the main checkout's branch,
  eleven `docs(prd): confirm E-nnn` commits on each side with identical errors.md content.
Diagnosis: Reproduced once in a scratch repository on 0.8.12: a PRD with one entry `proposed`, committed, and a second worktree on another branch cut from that commit. The inbox listing then holds the gate `error-class:E-002` twice, once in the group of each worktree, because the entry is `proposed` in both checkouts. Root cause: `listing` in `prd-toolkit/scripts/prdlint/gates.py` lists the gates of the PRD folder in every worktree and shows only a `deploy-step:` gate once ("a run is repo-wide: once, in the first group"); an answer to a card runs `prd error confirm` in that card's own worktree and commits there. So the owner is asked the same question once per worktree, and each answer is a commit on that worktree's branch with the same `errors.md` text, as the report says; one answer is not copied to the other worktree by the code. Class against the PRD: the area `gates` is not adopted (adoption.md: `gates | not started`), and no AC says how the inbox shows an entry that is `proposed` in more than one worktree. What a change could add: one card for an entry whose `proposed` text is the same in several worktrees, and a stated rule for which branch its answer is committed on.
Resolution: T-071.1 [integration], PRD 8.1.0, fixed in ba1736f
Recurrence of: -

### E-024 hooks check reports a hook stale after hooks install's own instruction for core.hooksPath is followed
Detected: 2026-11-15, user report from a repository that vendors 0.8.10
Classification: spec gap
Confirmed: 2026-11-17, "both are right"
Evidence: Report from a repository that vendors prd-toolkit 0.8.10, 2026-11-15:
  core.hooksPath is set to the repository's own .git/hooks. Its commit-msg and pre-commit were toolkit shims from an
  earlier release (header "# prd-toolkit hook (prd_hooks.py install <prd>); ...", one uv run --script ... prd_git_hook.py line).
  prd hooks install said: "core.hooksPath is set to ...; no shim written; replace its uv run --script ... prd_git_hook.py
  line in .../commit-msg with this line: <line>".
  After that line was replaced exactly as told, prd hooks check still said: "stale: .../commit-msg; run prd_hooks.py install".
Diagnosis: Reproduced once in a scratch repository on 0.8.12: `core.hooksPath` set to the repository's own `.git/hooks`, whose `commit-msg` and `pre-commit` were toolkit shims of the earlier form (the header `# prd-toolkit hook (prd_hooks.py install <prd>); …` and one `uv run --script … prd_git_hook.py` line). `prd hooks install` printed `core.hooksPath is set to …; no shim written; replace its uv run --script … prd_git_hook.py line in …/commit-msg with this line: <line>`; with that line replaced as told, `prd hooks check` printed `stale: …/commit-msg; run prd_hooks.py install` for both hooks. Root cause, in `prd-toolkit/scripts/prdlint/hooks.py`: `install` writes no hook when `core.hooksPath` is set and gives the instruction for a hook of the user's own, while `_stale_shims` takes a file that holds the toolkit's header as the toolkit's own shim and compares it whole with the current template, which the edited file can never equal; its advice, `run prd_hooks.py install`, changes nothing, since install writes nothing there. The two commands disagree on whose hook it is, and no step ends the loop short of removing the header by hand. Class against the PRD: the hooks commands are in no adopted area (adoption.md), and no AC says what `install` and `check` do with a toolkit shim under a set `core.hooksPath`. What a change could add: `install` rewrites a hook that holds the toolkit's header where `core.hooksPath` is set, or `check` accepts the line `install` prints.
Resolution: T-070.2 [integration], PRD 8.1.0, fixed in 92d60fe
Recurrence of: -

### E-025 The pre-commit standards run lints the vendored .prd-toolkit/ copy, so a re-vendor commit can be refused
Detected: 2026-11-15, user report from a repository that vendors 0.8.11
Classification: spec gap
Confirmed: 2026-11-15, "spec gap is right, add it to the change"
Evidence: Report from a repository that vendors prd-toolkit, 2026-11-15, after hooks install from the 0.8.11 plugin (vendored copy 0.8.4 to 0.8.11):
  The PRD's section 5 has an enforced row whose glob is **/*.py and whose linter enforces a line length the toolkit's own scripts do not keep.
  git add .prd-toolkit && git commit (a vendor-only commit, Refs: none) was refused by the pre-commit hook:
  prd-toolkit: `<linter>` failed (exit 1) on .prd-toolkit/prd_block.py, ... .prd-toolkit/prdlint/status.py
  The vendored copy must stay byte for byte what the plugin ships, so it cannot be changed to pass.
Diagnosis: Reproduced once in a scratch repository: a PRD whose section 5 holds an enforced row with the glob `**/*.py` and a linter that refuses a line over 88 characters; after `prd hooks install` from the plugin, `git add .prd-toolkit` and `git commit` is refused by the pre-commit hook with `prd-toolkit: ... failed (exit 1) on .prd-toolkit/prd_block.py, .prd-toolkit/prd_build_check.py, ...`. Root cause: `pre_commit` in `prd-toolkit/scripts/prdlint/githook.py` gives a standards row every staged file its glob matches, and the generated CI job (`standards-<n>` in `prd-toolkit/scripts/prdlint/hooks.py`) lists every tracked file the glob matches; neither leaves out the vendored copy `.prd-toolkit/`, which must stay byte for byte what the plugin ships and so can never be changed to pass a repository's own linter. The same code is in every release since the hooks were written. Class against the PRD: no requirement, contract or test case covers the standards run of the commit hook or of the generated CI (searched every features file, nfr.md and testing.md for the standards run, pre-commit and the vendored copy; adoption.md maps `githook.py` and `hooks.py` in `trace-and-hooks`, which is not started), so the PRD does not say which files a standards row is run on. The fix adds a requirement that a standards row is never run on a file under `.prd-toolkit/`, in the hook and in the generated CI job, with test cases, then the code.
Resolution: T-068.3 [integration], PRD 7.1.0, fixed in 27aab93
Recurrence of: -

### E-026 Approving a lift leaves the vendored pack uncommitted
Detected: 2026-11-16, review of the 0.8.12 skill text
Classification: spec gap
Confirmed: 2026-11-16, "spec gap is right for all three"
Touches: FR-060
Evidence: Review of the 0.8.12 skill text, 2026-11-16, in a scratch repository whose vendored copy was committed before the lift:
  prd change pack docs/prd/south leaflet 0.1.0 --lift, then prd hooks install docs/prd/south, the verdict, then prd change approve.
  The approval commit holds CLAUDE.md, docs/prd/README.md, docs/prd/south/README.md and docs/prd/south/prd.md.
  git status --porcelain after it:
   M .prd-toolkit/pack-sources.json
  ?? .prd-toolkit/packs/leaflet/
  A clone of the approval commit, with no plugin installed, fails lint with exit 1:
  pack leaflet 0.1.0 ... not found, and two contracts-valid findings.
  After a version move (prd change pack without --lift) the approval commit holds the re-vendored pack and pack-sources.json.
Diagnosis: Reproduced by the reviewer in a scratch repository. `_vendored_packs` in `prdlint/change_approve.py` stages `.prd-toolkit/packs/<name>` and `pack-sources.json` only for the packs `change.pack_moves` returns, which are lines whose pack version moved with the name and source unchanged; a lift adds a `Pack:` line the committed PRD lacks, so it returns none and the approval commit leaves out the vendored pack. No AC of FR-060 says what the approval of a lift commits (the area `change` is not adopted); only its Edge cases line says: "then `prd hooks install` vendors the pack and the owner approves with the dry-run record `no dry run (pack lifted)`, as for a version move".
Resolution: T-060.13 [integration], PRD 7.3.0, fixed in 307ebad
Recurrence of: -

### E-027 A validator that crashes from the pack folder counts as refusing its sample
Detected: 2026-11-16, review of the 0.8.12 skill text
Classification: spec gap
Confirmed: 2026-11-16, "spec gap is right for all three"
Touches: FR-059
Evidence: Review of the 0.8.12 skill text, 2026-11-16, on the fixture pack-authoring/sites:
  A contract type's validator that reads a file by a path relative to the PRD folder is carried into the pack.
  samples/<type>/bad.yaml is an unbroken copy of the PRD's own file, which the validator accepts when run from the PRD folder.
  prd pack check <pack dir> <prd A> <prd B> runs the validator on the sample from the pack folder, where it stops with a traceback (the file it reads is not there) and exits 1.
  The check prints no finding for the sample and exits 0: the crash counts as the sample being refused.
Diagnosis: Reproduced by the reviewer on the fixture pack-authoring/sites. `_sample_findings` in `prdlint/packcheck.py` reports a sample only when the validator exits 0, as AC-059.3 says: "the finding `<pack dir>/samples/<type>/<name>: the validator accepts it; a sample must be refused` when the validator exits 0". The code does what the AC says. No AC covers a validator that exits non-zero from the pack folder for a reason other than the sample (it reads a file by a path relative to the PRD folder and stops there): the check cannot tell that from a refusal, so a pack whose validator cannot run from the pack folder passes.
Resolution: T-059.8 [integration], PRD 7.3.0, fixed in 2b8d036
Recurrence of: -

### E-028 The implement pack leaves out the definitions a features file gives before its first block
Detected: 2026-11-16, stopped-builder report, the card-context build
Classification: spec gap
Confirmed: 2026-11-16, "spec gap is right for all three"
Evidence: Build of the area card-context, 2026-11-16, the builder's report:
  "The PRD's area order" and "well-formed address" are used by the acceptance criteria of FR-062 to FR-066.
  Both are defined only in the paragraph "Words used below." at the top of features/card-context.md, before the first block.
  prd context docs/prd/prd-toolkit --area card-context --req UJ-06,FR-062,FR-063,FR-064,FR-065,FR-066,FR-067 --for implement prints the blocks and not that paragraph.
  The builder read lines 1 to 27 of features/card-context.md, outside the pack, to learn them.
Diagnosis: Reproduced: `prd context docs/prd/prd-toolkit --area card-context --req FR-062 --for implement` exits 0 and holds neither "Words used below" nor the definition of the area order, which `features/card-context.md` gives in its lines before the first block. The pack prints the requirement blocks of a features file and none of its text before the first block. The area `context` is not adopted (adoption.md: `context | not started`), so no AC says what the pack takes from a features file outside its blocks; the format reference names no place in a features file for definitions the blocks share.
Resolution: T-072.1 [integration], PRD 8.1.0, fixed in 3a021bf
Recurrence of: -

### E-029 pack check reports nothing when a validator cannot be found or run from the pack folder on its second run
Detected: 2026-11-16, builder report, build pack-authoring FR-059 --fixes E-027
Classification: spec gap
Confirmed: 2026-11-16, "spec gap is right, leave it unfixed"
Touches: FR-059
Evidence: Report of the builder that fixed E-027 (build pack-authoring FR-059, 2026-11-16):
  On the second run from the pack folder, a validator that is not found or cannot be run gives no finding.
  AC-059.7 names only "exits other than 0" and "runs past the time".
  This is plausible when the validator's program is a relative path that resolves from the PRD folder and not from the pack folder.
Diagnosis: not a defect: reproduced once on the PRD's pack-authoring fixture, with the pack's `pages` validator set to `./ok.sh`, a program that exists in each PRD folder and not in the pack folder. `prd pack check` printed one finding, `plug/prd-packs/leaflet/samples/pages/bad.yaml: validator not found: ./ok.sh`, and exited 1. The second run from the pack folder (AC-059.7) did print nothing, as the report says, and AC-059.7 asks for nothing there: it names a finding only "when that run exits other than 0" and "when it runs past the time AC-059.2 allows". The case is still reported, by AC-059.3: the sample run uses the same validator "with the pack folder as the working directory" and prints "the finding `<pack dir>/samples/<type>/<name>: <problem>` with AC-059.2's problem text when the validator does not split, is not found, cannot be run or times out"; and a type with no sample draws `no bad.* sample`. So a validator that cannot be found or run from the pack folder never passes the check; its finding sits on the sample's path, not on the PRD's. Root cause of the silence: `_from_pack_folder` in prdlint/packcheck.py drops the not-found and not-executable problems on purpose. What a change could add, if wanted: the same problem printed on the PRD's line too, which would say it twice.
Resolution: not a defect: AC-059.3 already reports the case on the sample path: it prints "the finding `<pack dir>/samples/<type>/<name>: <problem>` with AC-059.2's problem text when the validator does not split, is not found, cannot be run or times out", so a validator that cannot be found or run from the pack folder never passes the check
Recurrence of: -

### E-030 a lift accepts a pack that declares no contract type, and a pack vocabulary adds lint findings after a lift
Detected: 2026-11-17, final review of the 0.8.12 branch
Classification: spec gap
Confirmed: 2026-11-17, "spec gap is right"
Touches: FR-060
Evidence: Final review of the 0.8.12 branch, 2026-11-17, on the PRD's fixture pack-authoring/sites:
  a second plugin held pack bare 0.1.0 with vocabulary [visitor, redirect], builder-tests: none and no contract types.
  prd change pack docs/prd/north bare 0.1.0 --lift exited 0 and recorded: pack bare 0.1.0 lifted; pending
  Lint then printed six new `platform-word` findings, the first:
  features/site.md:6: warn: platform-word: AC-001.1 names 'visitor', a word of pack bare
  AC-060.4 refuses only a declared type that is not a matching custom row; a pack with no type passes it.
  AC-060.7 says lint prints, after a lift, the findings it printed before it.
  The same new findings follow a lift onto a pack written by authoring-packs when the owner keeps a vocabulary word.
Diagnosis: reproduced by the final review of the 0.8.12 branch on the fixture pack-authoring/sites (the evidence above), not run again here; the code was read. The lift does what AC-060.4 states: `lift` in prdlint/change.py checks only the types the pack declares ("If a contract type the pack declares has no section 7 row in `prd.md` that is a custom row"), and the manifest reader allows none (`contract_types` in prdlint/packs.py returns an empty list), so a pack with no contract type passes with nothing checked. No PRD line says what a lift does with such a pack, or with a pack that holds vocabulary words. AC-060.7 then states more than holds: "the lint command shall print the findings it printed for the PRD before the lift", while a pack vocabulary adds a `platform-word` finding for each requirement that names a word, as the pack procedure itself says of a kept word. What a change would add: a refusal of a pack that declares no contract type, under AC-060.4 and in the AC-060.5 order, and AC-060.7 and the sentences that repeat it (the README, references/contract-types.md, the changing-prds skill) qualified for a pack vocabulary.
Resolution: T-060.14 [integration], PRD 8.0.0, fixed in dbd0b07
Recurrence of: -

### E-031 The build check reads an eval scaffold that holds `@prd T-` text as a tester's test, so no build can edit it
Detected: 2026-11-18, stopped build (/prd-toolkit:prd-build eval-scaffolds FR-073 --fixes E-019, 2026-11-18)
Classification: spec gap
Confirmed: 2026-11-18, "yes, E-031 is a spec gap"
Evidence: /prd-toolkit:prd-build eval-scaffolds FR-073 --fixes E-019, 2026-11-18, on bcf4d0c (PRD 8.2.1)
  The round's diff check exited 1 on the builder's commit 3dd8036 (branch prd-round/eval-scaffolds-2):
    prd-toolkit/evals/scaffolds/deploy_repo.py cites T-001.1, T-001.2, T-002.1, T-002.2, a tester's test: the builder may not edit it
  deploy_repo.py is an eval scaffold, not a test: it holds, as text, the test files of the demo repository it builds.
  Their docstrings read @prd T-001.1, @prd T-001.2, @prd T-002.1 and @prd T-002.2 (lines 187, 192, 217, 232): the demo PRD's T-ids.
  This PRD has cases with the same four IDs at a non-unit level, so the check reads the file as a tester's test.
  features/eval-scaffolds.md (FR-073) names deploy_repo.py as a file the build edits, so every round fails the same way.
  The build stopped before any merge; FR-073 stays approved and E-019 stays open.
Diagnosis: Reproduced: `prd_build_check.py docs/prd/prd-toolkit --diff bcf4d0c..3dd8036` exits 1 with `prd-toolkit/evals/scaffolds/deploy_repo.py cites T-001.1, T-001.2, T-002.1, T-002.2, a tester's test: the builder may not edit it`. Root cause: `diff_findings` in `prd-toolkit/scripts/prdlint/buildcheck.py` reads every changed path outside the PRD folder and `.prd-toolkit/` for `@prd T-` citations, at the base and at the head, and reports the path when a cited T-id is not a `unit` case of the PRD; it never asks where the file is. `deploy_repo.py` is an eval scaffold that holds the demo repository's test files as text, with the demo PRD's T-001.1, T-001.2, T-002.1 and T-002.2 in their docstrings; this PRD has cases with those IDs at the integration level, so the scaffold reads as a tester's test and no builder round can change it. The same holds for any file outside the test roots that quotes such a citation. Class against the PRD: testing.md Harness, Layout says where a tester's test is, "the black-box characterization tests are `prd-toolkit/tests/prd/test_<area>_*.py`", but no requirement, contract or test case covers the build check: adoption.md lists `build-check` as `not started`, so the PRD is silent on which changed files the check may call a tester's test. It blocks the fix of E-019: FR-073 names `deploy_repo.py` as a file its build edits, and a commit made after the scaffold's deploy run is no way round it, since `prd_deploy.py resume` then answers `refused: HEAD moved since the run started`.
Resolution: -
Recurrence of: -
