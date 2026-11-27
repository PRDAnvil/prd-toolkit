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
    Repro: <repro>/ydir (a scratch folder on the reporter's machine; its path is removed from this entry)
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
Resolution: fixed in 6d6711b, red run prd-toolkit/tests/test_builtin_packs.py [unit]
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
Resolution: T-073.1 [integration], PRD 8.3.1, fixed in 3649ab8
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
Resolution: T-074.1 [integration], PRD 8.3.0, fixed in e4903d9
Recurrence of: -

### E-032 The tester guard refuses the tester's Read of its own background run's output file
Detected: 2026-11-18, tester report, the FR-073 builds for E-019
Classification: code bug
Confirmed: 2026-11-20, "yes, as you recommend"
Evidence: Seen twice on 2026-11-18, in two headless build sessions started in a worktree of this repository
  (claude -p, the prd-tester agent in suite mode, the FR-073 builds for E-019).
  The tester started the harness in the background, as its rule 7 says for a run longer than the Bash timeout,
  and then called Read on that run's own output file:
    <system temp>/<project folder>/<session id>/tasks/<task id>.output
  The guard refused the Read. Its message named only the PRD folder, prd-toolkit/tests and .prd-toolkit/packs
  as the places the tester may read. An ls of that tasks folder was refused too.
  The tester's rule 7 (skills/testing-from-prds/SKILL.md) says: "read its `<id>.output` file, and never another
  task's output. The `tasks` folder also holds the caller's background tasks; the guard lets you read only an
  `<id>.output` file there."
  The tester did not retry by another path; it ran the same harness command in the foreground, which finished
  within the timeout, so the RESULTS of both builds stand.
  Not reproduced outside those sessions, and the cause is not diagnosed yet.
Diagnosis: Reproduced once against the guard alone: a hook input for the agent `prd-toolkit:prd-tester` with a Read of `<tmp>/<project>/<session>/tasks/<id>.output` and no `scratchpad_dir` exits 2 with `prd-tester may only read under:` followed by the PRD folder, `prd-toolkit/tests` and `.prd-toolkit/packs`, the message in the evidence; the same input with `scratchpad_dir` set to the sibling scratchpad folder exits 0. Root cause: `Context.__init__` in prd-toolkit/scripts/prd_tester_guard.py finds the `tasks` folder only as the sibling of the hook input's `scratchpad_dir` (`tasks = self.scratch.parent / "tasks" if self.scratch else None`), and `can_read_task_output` returns False when there is none. The refusals in the evidence list no scratch folder among the read roots, so the hook input of those headless sessions carried no `scratchpad_dir`, and the Read of the run's own output could not be allowed. The guard lies in the area tester-guard, which adoption.md lists as not started: no PRD block describes it, and its code is outside every adopted Boundary. The rule it breaks is the tester's rule 7 in skills/testing-from-prds/SKILL.md: "the guard lets you read only an `<id>.output` file there." The refused `ls` of the tasks folder is the guard working as that rule says.
Resolution: fixed in 4514ecb, red run prd-toolkit/tests/test_guard_session_tasks.py [unit]
Recurrence of: -

### E-033 prd error replay writes the index of the repository it is started in when GIT_INDEX_FILE is set
Detected: 2026-11-20, code review of the error-replay build
Classification: code bug
Confirmed: 2026-11-20, "yes, as you recommend"
Touches: FR-079
Evidence: Code review of the error-replay build (9b17b5a..22218e9), verified by a probe in a scratch repository.
  Setup: testing.md steps R0, RT, RF, RE; E-001 resolved `T-006.1 [integration], PRD 1.0.0, fixed in <fix>`.
  Command: GIT_INDEX_FILE=<repo>/.git/index python prd_error.py replay docs/prd/orders E-001
  Result: prints the proof line and exits 0.
  Before the command: git status --porcelain prints nothing.
  After the command: git status --porcelain prints
  MM docs/prd/orders/errors.md
  and the bytes of <repo>/.git/index differ from before.
  prdlint/errorreplay.py _git passes the caller's environment to every git call:
  env={**os.environ, "GIT_LITERAL_PATHSPECS": "1"}
  git sets GIT_INDEX_FILE for the hooks it runs (pre-commit, commit-msg).
Diagnosis: Reproduced once in a scratch repository: with `GIT_INDEX_FILE` set to the repository's own index, `prd error replay` printed the proof and exited 0, and `git status --porcelain` went from empty to `MM docs/prd/orders/errors.md`. Root cause: `_git` in prdlint/errorreplay.py runs every git command with the caller's environment (`{**os.environ, "GIT_LITERAL_PATHSPECS": "1"}`), so the checkout of `git worktree add` and the `git rm` and `git checkout` that replace the test roots write the index `GIT_INDEX_FILE` names instead of the temporary worktree's own; `GIT_DIR` and `GIT_WORK_TREE` are inherited the same way, and `resolve --red-run` replays through the same code. AC-079.1: "When the replay ends with the proof holding, `git worktree list --porcelain` in the repository shall print what it printed before the command started, the folder the command made in the system temporary folder shall no longer exist, and `git status --porcelain` shall print what it printed before." The area's definition of a worktree: "The command never writes the working tree or the index of the repository it is started in." No test case sets these variables.
Resolution: T-079.6 [integration], PRD 8.5.0, fixed in 005cbd8
Recurrence of: -

### E-034 test_done_right_after_the_last_answer_is_accepted fails once in a whole unit run and passes alone
Detected: 2026-11-20, failing test, the whole unit suite
Classification: code bug
Confirmed: 2026-11-21, "option 1, yes to both classes"
Evidence: Whole unit suite, uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd, on 006b698 with an uncommitted PRD change in the tree:
  FAILED tests/test_inbox_page.py::test_done_right_after_the_last_answer_is_accepted
  2 failed, 3925 passed, 1 skipped in 518.60s
  (the other failure, test_the_vendored_copy_matches_the_plugin, is the In review PRD's stale block, expected until approval)
  The driver's error, from run_page:
  AssertionError: TypeError: Cannot read properties of undefined (reading 'id')
      at save (evalmachine.<anonymous>:174:22)
      at evalmachine.<anonymous>:8:7
  The driver line before it: const entry = [...I.seen.values()].find((e) => e.g.kind === 'adoption' && e.wt.path === <the test's worktree path>)
  Second run, the file alone, same tree, a few minutes later:
  uv run --directory prd-toolkit pytest -q -p no:cacheprovider tests/test_inbox_page.py
  22 passed in 25.26s
  The same test passed in three whole-suite runs earlier the same day (on e491e37, 22218e9 and 6e9cae9).
Diagnosis: Not reproduced on demand: the test failed once in a whole parallel unit run and passed in the second run, the file alone (22 passed); two runs made, as the rule allows. Root cause by reading: the test's driver calls `openAdoption(entry)`, waits a fixed 300 ms (`await new Promise((r) => setTimeout(r, 300))`) and then calls `save(S.order.find((it) => it.id === 'E-003'), …)`. `S.order` is filled only when the panel's `load()` gets its `GET /items` answer from the test's inbox server (templates/confirm/panel.html). When that answer takes longer than 300 ms, as on a machine busy with the parallel run, `find` returns undefined and `save` fails with `TypeError: Cannot read properties of undefined (reading 'id')`, the error in the evidence. The faulty code is the test itself, prd-toolkit/tests/test_inbox_page.py, which no adopted area covers: it acts on the panel before the load it started has finished. The page and the server are not shown wrong. The rule the test breaks is the Harness line of testing.md: "**Waits.** Not applicable: every command runs to completion before the test asserts."
Resolution: fixed in af56defaa0a8f5df80f4988e5c2a8fbd06bde72e, red run prd-toolkit/tests/test_inbox_page_slow_items.py [unit]
Recurrence of: -

### E-035 prd error replay cannot add its worktree inside the Bash sandbox of a Claude Code session
Detected: 2026-11-20, eval runs of the two new handling-errors cases
Classification: environment
Confirmed: 2026-11-21, "option 1, yes to both classes"
Touches: FR-079
Evidence: Eval runs of the two new handling-errors cases (claude plugin eval, one run each, the runner's sandbox on).
  error-uncovered-code-red-run, with the plugin: the session committed the failing test alone, then the fix, then ran
  .prd-toolkit/prd error resolve docs/prd/greet E-001 --commit <sha> --red-run tests/unit/test_count_names.py --level unit
  prd_error: internal error: RuntimeError: git worktree add --detach <tmp>/prd-error-replay-<x>/run-1 <sha> failed: Preparing worktree (detached HEAD bcd2623)
  prd-error-exit=2
  error-replay-finding-not-committed, with the plugin: resolve exited 0, then
  .prd-toolkit/prd error replay docs/prd/greet E-001
  prd_error: internal error: RuntimeError: git worktree add --detach <tmp>/prd-error-replay-<x>/run-1 <sha> failed: Preparing worktree (detached HEAD 6069f6f)
  prd-error-exit=2
  Both sessions then left the entry confirmed and reported the failure; the second put errors.md back with git restore.
  The same command in a headless session with the Bash sandbox enabled, in a scratch repository:
  git worktree add --detach <tmp>/wt HEAD
  Preparing worktree (detached HEAD dd29d3d)
  fatal: could not create directory of '.git/worktrees/wt': Operation not permitted
  exit=128
  In that session git archive HEAD | tar -x -C <tmp>/plain exited 0, and a file appended under .git/ was written.
  Outside the sandbox the same replays hold or print their findings (the cases' by-hand walk, and the toolkit's own ledger).
Diagnosis: Reproduced once: in a headless session with the Bash sandbox enabled, `git worktree add --detach <tmp>/wt HEAD` in a scratch repository printed `fatal: could not create directory of '.git/worktrees/wt': Operation not permitted` and exited 128; `git archive HEAD` piped into `tar -x` wrote the same tree there, exit 0. Root cause: the Bash sandbox of a Claude Code session keeps `.git/worktrees` of the repository read-only, and the replay makes each run's tree with `git worktree add --detach`, as the area's definition of a worktree says: "A **worktree** is one that the command adds with `git worktree add --detach` under a new folder it makes in the system temporary folder". The code does what the PRD says, and it ends as FR-079 says of an internal error ("an internal error ends the command the same way, with exit 2"): nothing was written or left behind, and both sessions kept the entry `confirmed`. So the replay and `resolve --red-run` cannot run in a sandboxed session, which is every `claude plugin eval` run: the two new eval cases cannot pass there. Outside the sandbox the same commands hold or print their findings. One thing the code adds to the trouble: the internal error quotes only the first line git printed (`Preparing worktree (detached HEAD …)`) and drops the `fatal:` line that names the cause.
Resolution: T-079.7 [integration], PRD 9.0.0, fixed in efcbe2e
Recurrence of: -

### E-036 A test the replay runs can write the index of the repository the command is started in
Detected: 2026-11-21, final review of the 0.8.14 branch, a probe in a scratch repository
Classification: invalid requirement
Confirmed: 2026-11-21, "yes to both classes, leave both open, push and open the PR"
Touches: FR-079
Evidence: Final whole-branch review of the 0.8.14 branch, then the same probe by the recording session, in a scratch repository
  whose entry E-001 is resolved `T-001.2 [unit], PRD 1.0.0, fixed in <fix>`.
  Setup: the unit level's One test cell names a program kept outside the repository, `python3 <elsewhere>/t1.py`, which
  writes a file `junk` in its working directory and then runs `git add -A`.
  `git status --porcelain` before:
   M docs/prd/greet/testing.md
  The command, started in the repository with GIT_INDEX_FILE set to the absolute path of the repository's own .git/index:
  prd error replay docs/prd/greet E-001
  E-001: T-001.2 passes on <fix>^; <fix> did not turn it green
  exit=1
  `git status --porcelain` after:
  MM docs/prd/greet/errors.md
   M docs/prd/greet/testing.md
  AD junk
  The bytes of .git/index differ from before; the temporary folder is gone.
  The reviewer's note on where the variable comes from: in the pre-commit hook of a partial commit (`git commit <paths>`)
  git sets GIT_INDEX_FILE to the absolute path of <repo>/.git/next-index-<pid>.lock; in a plain `git commit` it is the
  relative `.git/index`, which in a clone names the clone's own index.
Diagnosis: Reproduced once, as the evidence shows. Two sentences of the area contradict each other, and the code follows the first. The definition of a run says it starts "with the environment the command itself has", and `_execute` in prdlint/errorreplay.py starts the test with no `env`, so the test has the variables that point git at a repository. The definitions also say "The command never writes the working tree or the index of the repository it is started in", and FR-079's edge case says a command started with `GIT_INDEX_FILE`, `GIT_DIR` or `GIT_WORK_TREE` set "leaves its repository's index and working tree as they were, since no git command the replay runs has those variables". That holds for the git commands the replay itself runs (E-033) and not for a test that calls git: with `GIT_INDEX_FILE` naming the repository's index, the test's `git add -A` in its clone staged the clone's files into that index, so `git status --porcelain` no longer printed what it printed before, against AC-079.1 and AC-079.2. The edge case "a One test program that calls git finds a git checkout in its clone" fails the same way when `GIT_DIR` is set. One of the two sentences has to change: a run's environment drops the variables `git rev-parse --local-env-vars` lists, or the area says a test can reach the repository through them. The README's limits already tell the user not to start a replay from inside a git hook.
Resolution: T-079.9 [integration], PRD 9.7.1, fixed in 15058011d931657380b57e0cf7c905f5001ab71b
Recurrence of: -

### E-037 The replay leaves its folder behind when a test leaves a folder it cannot remove
Detected: 2026-11-21, final review of the 0.8.14 branch, a probe in a scratch repository
Classification: code bug
Confirmed: 2026-11-21, "yes to both classes, leave both open, push and open the PR"
Touches: FR-079
Evidence: Final whole-branch review of the 0.8.14 branch, then the same probe by the recording session, in a scratch repository
  whose entry E-001 is resolved `T-001.2 [unit], PRD 1.0.0, fixed in <fix>`.
  Setup: the unit level's One test cell names a program kept outside the repository, `python3 <elsewhere>/t2.py`, which
  makes the folders `ro/x` in its working directory, writes a file `ro/x/f` and sets the mode of `ro/x` to 0500.
  The command, with TMPDIR naming an empty folder <tmp>:
  prd error replay docs/prd/greet E-001
  E-001: T-001.2 passes on <fix>^; <fix> did not turn it green
  exit=1
  Nothing on stderr. After the command, <tmp> still holds:
  <tmp>/prd-error-replay-<x>/run-1/ro/x
  <tmp>/prd-error-replay-<x>/run-2/ro/x
Diagnosis: Reproduced once, as the evidence shows. AC-079.2 says that when the replay ends with findings "the folder the command made in the system temporary folder shall no longer exist", and AC-079.1 says the same of a proof that holds. prdlint/errorreplay.py removes each run's clone and then its own folder with `shutil.rmtree(..., ignore_errors=True)`, so a folder a test left without write permission stops the removal, nothing is printed, and the command exits as if it had cleaned up. The fault is in the code: it neither makes such a folder removable before it removes it nor reports a folder it could not remove.
Resolution: T-079.8 [integration], PRD 9.6.1, fixed in d38de99c
Recurrence of: -

### E-038 known-failing-tags reports no tag that names an unknown errors.md entry
Detected: 2026-11-21, adoption extract of trace (prd-toolkit/scripts/prdlint/trace.py:313 @a87f336)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-086
Evidence: prd-toolkit/README.md, "Known-failing tests": "The trace's `known-failing-tags` rule reports a case with no tagged citation and a tag whose entry is resolved or unknown."
  prd-toolkit/scripts/prdlint/trace.py:318-321 reports a tag only when its T-id's case is not known-failing on that E-id, or when the entry exists and is resolved (`entry is not None and not entry.open`).
Diagnosis: The README (prd-toolkit/README.md, "Known-failing tests") says the rule reports "a tag whose entry is resolved or unknown". For each tag the code reports only when the T-id's case is not known-failing on that E-id (trace.py:318) or when the entry exists and is resolved (trace.py:320, `entry is not None and not entry.open`). A tag `@prd T-001.1 known-failing E-009` on a case `known-failing: E-009`, with no E-009 in errors.md, gives no trace finding; a tag on a T-id with no case and an unknown E-id gives none either (only test-cites-live, for the T-id). The lint rule `test-refs` reports the case's unknown entry, but not the tag. Not reproduced by a run: read from the code during the adoption extract of the area trace.
Resolution: not a defect: the code is as intended, and AC-086.4 now says so: the trace command reports no `known-failing-tags` finding for an entry errors.md does not hold. Another rule already reports every tag that names such an entry: the lint rule `test-refs` when the test case names it, AC-086.2 when it does not, and `test-cites-live` when the T-id has no test case. The README sentence is the loose one. The owner, 2026-11-21, after confirming the class in the form: "I answered the form, but answered wrong on both E-038 and E-039, Those are intended"
Recurrence of: -

### E-039 commit_msg's docstring says it allows any commit with nothing staged under the commit rule; the code refuses some
Detected: 2026-11-21, adoption extract of trace (prd-toolkit/scripts/prdlint/githook.py:12 @a87f336)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-093, FR-092
Evidence: prd-toolkit/scripts/prdlint/githook.py:12, the docstring of `commit_msg`: "Problems with the commit message; [] for a merge commit or when nothing staged is under the commit rule."
  prd-toolkit/scripts/prdlint/githook.py:18-22: with no staged path inside the Boundary the function still returns `trace.unconfirmed_refs(...)` for a commit that stages a path outside the PRD folder, and `trace.changeset_problems(...)` for every commit.
Diagnosis: The docstring of `githook.commit_msg` says the function returns no problem "when nothing staged is under the commit rule". When no staged path is inside the Boundary, the code still returns `trace.unconfirmed_refs(...)` for a commit that stages a path outside the PRD folder, and `trace.changeset_problems(...)` for every commit (githook.py:18-22), so the hook exits 1 on such a commit when it cites an unconfirmed entry or holds a malformed or unrecorded `Change-set:` value. The code's side has more behind it: the comments at githook.py:18 and :20-21, commit e3b6f63 (the commit-msg gate refuses a code commit citing an unconfirmed entry whenever a staged path is outside the PRD folder, not only inside the Boundary), commit 78c667c, and the README ("the commit-msg hook and `prd_error.py check` refuse a code commit that cites an unconfirmed one"). Either the docstring or the code is wrong, and the owner says which. Not reproduced by a run: read from the code during the adoption extract of the area trace.
Resolution: not a defect: the code is as intended, and AC-093.9 and AC-093.10 now say so: with no staged path inside the Boundary the commit-msg hook still refuses a code commit that cites an unconfirmed entry, and a `Change-set:` problem. The docstring of `githook.commit_msg` is the stale one. The owner, 2026-11-21, after confirming the class in the form: "I answered the form, but answered wrong on both E-038 and E-039, Those are intended"
Recurrence of: -

### E-040 trace --range checks only the newest commit of a range in a SHA-256 repository
Detected: 2026-11-21, confirmation of FR-090 (the owner's answer to Q-09)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-090
Evidence: prd-toolkit/scripts/prdlint/trace.py:21 holds `_SHA = re.compile(r"[0-9a-f]{40}")`, and `_commits` (trace.py:229) takes the last line of a commit's path list for the next commit's name only when that pattern matches the whole line.
  In a repository whose object format is SHA-256 a commit's name has 64 hex digits, so the pattern never matches: the first commit of the log keeps the next commit's name as one of its paths, and the loop ends.
Diagnosis: With `--range`, `_commits` reads `git log` and finds where one commit ends and the next begins by a line of exactly 40 hex digits (trace.py:21, :229). In a repository whose object format is SHA-256 that line has 64 digits, so only the newest commit of the range is judged: the older commits get no `commit-refs` finding whatever their messages say, and the next commit's name is taken for a path of the newest one. The command says nothing of the commits it skipped and exits as if the range held one commit. The owner answered Q-09 on 2026-11-21 that trace is to support such a repository, and AC-090.7 now says so; the code does not. Not reproduced by a run: read from the code during the adoption of the area trace.
Resolution: T-090.9 [integration], PRD 9.6.0, fixed in eb9f9ff7602b0178325ef691207639af3a1250cc
Recurrence of: -

### E-041 The 0.8.13 upgrade note says hooks check runs from the vendored copy; it refuses
Detected: 2026-11-21, adoption extract of hooks-install (prd-toolkit/scripts/prd_hooks.py:56 @07f77b1)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-108, FR-109
Evidence: `prd_hooks.py check <prd_dir>` without `--ci`, run from `.prd-toolkit/`, prints `prd_hooks: run check from the plugin, not the vendored copy` and exits 2 (prd_hooks.py:56-58). The 0.8.13 changelog in `prd-toolkit/README.md:1336` says "the launcher, `hooks check`, the context pack, … run from the vendored copy, so a repository gets those fixes only then".
Diagnosis: `prd_hooks.py check <prd_dir>` without `--ci`, run from `.prd-toolkit/`, prints `prd_hooks: run check from the plugin, not the vendored copy` and exits 2 (prd_hooks.py:56-58). The 0.8.13 changelog in `prd-toolkit/README.md:1336` says "the launcher, `hooks check`, the context pack, … run from the vendored copy, so a repository gets those fixes only then". The code contradicts that doc. The unit tests `test_vendored_check_exits_2` and `test_check_without_ci_from_vendored_copy_still_refused` agree with the code, so the defect may be in the README rather than the code. The owner decides which one is wrong. Not reproduced by a run: read from the code during the adoption extract of the area hooks-install.
Resolution: not a defect: the code is as intended, and AC-108.5 now says so: `check` without `--ci`, run from the vendored copy, prints `prd_hooks: run check from the plugin, not the vendored copy` and exits 2, since the copy compared with itself would show nothing. Only `check --ci` runs from the vendored copy. The sentence of the 0.8.13 changelog is the loose one. The owner, 2026-11-21, asked which he meant after the class was confirmed in the form: "Intended (Recommended)"
Recurrence of: -

### E-042 vendor's pack refusal says "install refused"
Detected: 2026-11-21, adoption extract of hooks-install (prd-toolkit/scripts/prd_hooks.py:95 @07f77b1)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-107, FR-099
Evidence: When a pack the PRD names cannot be resolved, `prd_hooks.py vendor <prd_dir>` prints `prd_hooks: install refused: <reason>` and exits 2. The one `InstallRefused` handler (prd_hooks.py:95-97) serves both actions, so the message names the wrong action.
Diagnosis: When a pack the PRD names cannot be resolved, `prd_hooks.py vendor <prd_dir>` prints `prd_hooks: install refused: <reason>` and exits 2. The one `InstallRefused` handler (prd_hooks.py:95-97) serves both actions, so the message names the wrong action. `vendor` is documented as a separate action that "writes `.prd-toolkit/` … and nothing else" (README.md:418, hooks.py:311 docstring), and the hooks command names every other refusal after its own action (`prd_hooks: vendor runs from the plugin, …`, `--ci belongs to check`). Not reproduced by a run: read from the code during the adoption extract of the area hooks-install.
Resolution: T-107.4 [integration], PRD 9.6.0, fixed in 012db11a519eaa009e82d4c0e64d74980eb7cd80
Recurrence of: -

### E-043 Outside a git checkout, install vendors into the PRD folder and then fails with an internal error
Detected: 2026-11-21, adoption extract of hooks-install (prd-toolkit/scripts/prd_hooks.py:55 @07f77b1)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-098, FR-101, FR-107, FR-113
Evidence: `model.repo_root` returns the PRD folder itself when git finds no checkout (model.py:1022). Install then takes the PRD folder as the top.
Diagnosis: `model.repo_root` returns the PRD folder itself when git finds no checkout (model.py:1022). Install then takes the PRD folder as the top. It writes `<prd>/.prd-toolkit/` and `<prd>/.gitignore`, and only then fails at `git rev-parse --git-path hooks` (hooks.py:164, `check=True`). It prints `prd_hooks: internal error: CalledProcessError: …` and exits 2, leaving those files behind. `vendor` and `ci` take the same root, so they write `.prd-toolkit/` or `.github/…` inside the PRD folder and exit 0. The sibling code says this case should be refused cleanly. `check --ci` refuses outside a checkout with `prd_hooks: <path> is not inside a git checkout` and exit 2, a fix made deliberately (commit f03ca0f: "instead of passing with no CI file found"). The `InstallRefused` docstring says a refused install "vendors nothing". Commit 7fd23dc made check's hook loop tolerate a missing checkout "instead of raising". An internal error after partial writes matches none of these. Not reproduced by a run: read from the code during the adoption extract of the area hooks-install.
Resolution: T-098.6 [integration], PRD 10.3.1, fixed in 98638f4146af4196dedbe07dba8729b06d95b020
Recurrence of: -

### E-044 uninstall removes nothing where core.hooksPath is set, though install writes the hooks of the toolkit there
Detected: 2026-11-21, confirmation of FR-112 (the answer of the owner to Q-15)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-112
Evidence: prd-toolkit/scripts/prdlint/hooks.py:492-495: `uninstall` returns the one line `core.hooksPath is set to <value>; removed nothing` whenever `core.hooksPath` is set, before it looks at any hook file.
  Since FR-070 install writes the toolkit's own hooks into that folder, and line 2 of each shim reads `# prd-toolkit hook: written by prd_hooks.py install; removed by prd_hooks.py uninstall`.
Diagnosis: Where `core.hooksPath` is set, `uninstall` prints `core.hooksPath is set to <value>; removed nothing` and deletes no file (hooks.py:492-495). Since FR-070 (prd-toolkit 0.8.13) install replaces the hooks of the toolkit in that folder, and each shim says on its line 2 that `prd_hooks.py uninstall` removes it, so a repository that sets `core.hooksPath` cannot remove them with the command. The owner answered Q-15 on 2026-11-21 that uninstall is to remove the toolkit's own hooks there too, and AC-112.2 now says so; the code does not. Not reproduced by a run: read from the code during the adoption of the area hooks-install.
Resolution: T-112.2 [integration], PRD 10.3.1, fixed in b0396f1e207ef73ae4f6a4fd08f525ec969ccb90
Recurrence of: -

### E-045 check does not report a file of .prd-toolkit/ that the plugin no longer ships
Detected: 2026-11-21, confirmation of FR-108 (the answer of the owner to Q-16)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-108
Evidence: prd-toolkit/scripts/prdlint/hooks.py:454-458: `check` looks for a file the plugin does not ship only under the folders `prdlint`, `hooks`, `confirm`, `gates`, `judge` and `languages` of `.prd-toolkit/`.
  A file at the top of `.prd-toolkit/` (a script the plugin has retired) or under `.prd-toolkit/templates/` is never reported, and install and vendor do not delete it.
Diagnosis: `check` reports a file the plugin does not ship only under six folders of `.prd-toolkit/` (hooks.py:454-458). A file at the top of `.prd-toolkit/`, such as a script the plugin has retired, or a file under `.prd-toolkit/templates/`, gets no line, and install and vendor leave it in place; the dispatcher can still run such a script by its command name. The owner answered Q-16 on 2026-11-21 that check is to report such a file, and AC-108.2 now says so; the code does not. Not reproduced by a run: read from the code during the adoption of the area hooks-install.
Resolution: T-108.6 [integration], PRD 10.3.1, fixed in b0396f1e207ef73ae4f6a4fd08f525ec969ccb90
Recurrence of: -

### E-046 id-unique counts `### E-nnn` headings inside code fences of errors.md
Detected: 2026-11-21, adoption extract of lint-ids (prd-toolkit/scripts/prdlint/rules/ids.py:41 @4465291)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-122
Evidence: `defined_ids` matches `^### (E-\d+)\b` against the raw lines of errors.md (ids.py:40-43), so a fenced example such as `### E-001 <title>` counts as a definition. If the ledger's real E-001 comes after it, id-unique reports it as `E-001 is already defined at errors.md:<fence line>`. prd-format.md ("errors.md") says "Headings inside code fences are not entries", and the loader's own ledger parser (model.py `_errors_ledger`) matches against `strip_code(text)` and skips fenced headings.
Diagnosis: `defined_ids` matches `^### (E-\d+)\b` against the raw lines of errors.md (ids.py:40-43), so a fenced example such as `### E-001 <title>` counts as a definition. If the ledger's real E-001 comes after it, id-unique reports it as `E-001 is already defined at errors.md:<fence line>`. prd-format.md ("errors.md") says "Headings inside code fences are not entries", and the loader's own ledger parser (model.py `_errors_ledger`) matches against `strip_code(text)` and skips fenced headings. Not reproduced by a run: read from the code during the adoption extract of the area lint-ids.
Resolution: T-122.7 [integration], PRD 10.3.1, fixed in d98b4d711d3e15770d167ff1adc4e5bd6b6716b3
Recurrence of: -

### E-047 id-format reports a malformed test-case key at line 1
Detected: 2026-11-21, adoption extract of lint-ids (prd-toolkit/scripts/prdlint/rules/ids.py:74 @4465291)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-121
Evidence: For each test case, `id_format` builds a plain dict `{tc.id: tc.data}` (ids.py:74). A plain dict has no `key_lines`, so `_yaml_strings` gives the key the default line 1 (ids.py:54).
Diagnosis: For each test case, `id_format` builds a plain dict `{tc.id: tc.data}` (ids.py:74). A plain dict has no `key_lines`, so `_yaml_strings` gives the key the default line 1 (ids.py:54). A key such as `T-12.1:` on line 40 is therefore reported at `test-cases/<area>.yaml:1`. Every other place in this file reports a test-case key at its real line (`tc.line`, ids.py:38, 157), and every other key and value in this rule is reported at its own line. Not reproduced by a run: read from the code during the adoption extract of the area lint-ids.
Resolution: T-121.7 [integration], PRD 10.3.1, fixed in d98b4d711d3e15770d167ff1adc4e5bd6b6716b3
Recurrence of: -

### E-048 id-format reads hidden Markdown and YAML files
Detected: 2026-11-21, adoption extract of lint-ids (prd-toolkit/scripts/prdlint/rules/ids.py:72 @4465291)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-121
Evidence: `id_format` reads `prose(prd)`, which yields every Markdown file the loader read, hidden ones included (`.notes.md`, `features/.draft.md`). It also reads `prd.yaml`, which holds hidden YAML under `contracts/`.
Diagnosis: `id_format` reads `prose(prd)`, which yields every Markdown file the loader read, hidden ones included (`.notes.md`, `features/.draft.md`). It also reads `prd.yaml`, which holds hidden YAML under `contracts/`. The owner's confirmed rule in E-011 says that a file or folder whose name starts with `.` is not part of the PRD and that no rule reads it. The sibling rules in structure.py read `_visible_prose` and skip hidden YAML sources (structure.py:54-58, 283). Not reproduced by a run: read from the code during the adoption extract of the area lint-ids.
Resolution: T-121.8 [integration], PRD 10.3.1, fixed in d98b4d711d3e15770d167ff1adc4e5bd6b6716b3
Recurrence of: -

### E-049 index-consistent reports matching titles as different when a title starts or ends with a code span
Detected: 2026-11-21, adoption extract of lint-ids (prd-toolkit/scripts/prdlint/rules/ids.py:200 @4465291)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-125
Evidence: The loader strips backticks from both ends of every section 11 cell (model.py: `c = [x.strip("`") for x in r.cells]`), but it keeps the block heading's title as written. Take a heading `### FR-005 `prd help` prints the catalogue` and a row whose Title cell holds exactly the same text.
Diagnosis: The loader strips backticks from both ends of every section 11 cell (model.py: `c = [x.strip("`") for x in r.cells]`), but it keeps the block heading's title as written. Take a heading `### FR-005 `prd help` prints the catalogue` and a row whose Title cell holds exactly the same text. `r.title != b.title` compares `prd help` prints the catalogue` (leading backtick gone) with the heading's text, so the rule reports `index title ... differs from block title ...`. The rule's own description says it checks that the index and the block have "the same title", and here the two titles are the same. Not reproduced by a run: read from the code during the adoption extract of the area lint-ids.
Resolution: T-125.11 [integration], PRD 9.7.0, fixed in bec6d30
Recurrence of: -

### E-050 A resolved errors.md entry with no Classification line is not reported as unclassified
Detected: 2026-11-21, adoption extract of lint-ids (prd-toolkit/scripts/prdlint/rules/ids.py:185 @4465291)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-127
Evidence: `index_consistent` reports only the literal `Classification: unclassified` on a resolved entry (`e.classification == "unclassified"`). A resolved entry with no `Classification:` line passes. prd-format.md's state table counts "no `Classification:`" as `unclassified`, and it says `unclassified` is allowed only on an open entry.
Diagnosis: `index_consistent` reports only the literal `Classification: unclassified` on a resolved entry (`e.classification == "unclassified"`). A resolved entry with no `Classification:` line passes. prd-format.md's state table counts "no `Classification:`" as `unclassified`, and it says `unclassified` is allowed only on an open entry. The sibling code treats the two forms alike: `ErrorEntry.state` (model.py) and error-entries (errors.py:60, `e.classification in ("", "unclassified")`). Not reproduced by a run: read from the code during the adoption extract of the area lint-ids.
Resolution: T-127.4 [integration], PRD 10.3.1, fixed in d98b4d711d3e15770d167ff1adc4e5bd6b6716b3
Recurrence of: -

### E-051 index-consistent accepts any text as the Source line of an as-built block
Detected: 2026-11-21, confirmation of FR-126 (the answer of the owner to Q-20)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-126
Evidence: prd-toolkit/scripts/prdlint/rules/ids.py:191: `if b.status == "as-built" and not b.source:` is the whole check, so any text after `Source:` satisfies it.
  The finding's own message names the form the line is to have: `<ID> is as-built but has no 'Source: <file>:<line> @<commit>' line`.
Diagnosis: For an `as-built` block, `index_consistent` only asks whether the block has a `Source:` line with text (ids.py:191). A line such as `Source: somewhere in the code` passes, though the message of the rule names the form `<file>:<line> @<commit>`, and the context pack and the adoption checks read a path, a line and a commit from that line. The owner answered Q-20 on 2026-11-21 that lint is to check the form, and AC-126.3 now says so; the code does not. Not reproduced by a run: read from the code during the adoption of the area lint-ids.
Resolution: T-126.3 [integration], PRD 10.4.0, fixed in edffa43
Recurrence of: -

### E-052 A gap finding calls an entry missing when it stands later in errors.md
Detected: 2026-11-21, adoption extract of lint-registries (prd-toolkit/scripts/prdlint/rules/errors.py:37 @6162689)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-144
Evidence: `_sequence` reports a gap as soon as an entry's number is more than one above the highest number so far (`n > top + 1`). It does not look ahead. With the entries in the order E-001, E-003, E-002, the rule reports at E-003 `E-003 follows E-001: E-002 is missing; entries are never deleted, restore it from git`, even though E-002 is in the file.
Diagnosis: `_sequence` reports a gap as soon as an entry's number is more than one above the highest number so far (`n > top + 1`). It does not look ahead. With the entries in the order E-001, E-003, E-002, the rule reports at E-003 `E-003 follows E-001: E-002 is missing; entries are never deleted, restore it from git`, even though E-002 is in the file. It then reports E-002 as out of order. The message says the entry was deleted and must be restored from git, which is false for that file. The rule's own description says "put an out-of-order entry back in sequence" and treats a gap ("restore a deleted entry from git") as a separate case. prd-format.md also names the two separately ("lint reports a gap or an entry out of order"). The unit test `test_out_of_order` (prd-toolkit/tests/test_errors_model.py:160) asserts only `_ledger_findings(prd)[1:]` and skips this first finding. The same happens when the first entry is above 1 and a lower one follows (E-002, E-001 gives `E-001 is missing`). Not reproduced by a run: read from the code during the adoption extract of the area lint-registries.
Resolution: T-144.7 [integration], PRD 9.7.0, fixed in bc52b9f2a76dc9c5eee3f6f6217f735a65d6482a
Recurrence of: -

### E-053 drift-rows tells a schema Drift row that schema drift arrives in prd-toolkit 0.6
Detected: 2026-11-21, confirmation of FR-143 (the answer of the owner to Q-24)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-143
Evidence: prd-toolkit/scripts/prdlint/rules/registries.py:264 reports a `## Drift` row whose Check is `schema` with `check 'schema': schema drift arrives in prd-toolkit 0.6`.
  prd-toolkit/.claude-plugin/plugin.json holds version 0.8.14, and the toolkit has no schema drift check.
Diagnosis: A `## Drift` row whose Check cell is `schema` gets its own message, `check 'schema': schema drift arrives in prd-toolkit 0.6`. The toolkit is at 0.8.14 and no release brought a schema drift check, so the message promises what did not happen; the format reference repeats the wording. The owner answered Q-24 on 2026-11-22 that such a row is to be reported as `check 'schema' is not version or config`, like any other unknown check, with no release named, and AC-143.1 now says so; the code does not. Not reproduced by a run: read from the code during the adoption of the area lint-registries.
Resolution: -
Recurrence of: -

### E-054 A refs entry cannot name a heading that holds a code span
Detected: 2026-11-21, adoption extract of lint-testcases (prd-toolkit/scripts/prdlint/rules/testcases.py:35 @5483ca1)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-162
Evidence: `_ref_problem` collects a file's headings with `_HEADING.findall(strip_code(text))`. `strip_code` (markdown.py:9-21) blanks fenced blocks, and it also turns every inline code span into spaces.
Diagnosis: `_ref_problem` collects a file's headings with `_HEADING.findall(strip_code(text))`. `strip_code` (markdown.py:9-21) blanks fenced blocks, and it also turns every inline code span into spaces. So the heading ``## The `orders` table`` is read as `The table`. The entry ``prd.md#The `orders` table`` then gets `has no heading 'The `orders` table'`, and no entry can name that heading. The reverse also happens: the heading ``## Totals `beta` `` is read as `Totals`, so an entry `#Totals` resolves to it. The docstring (testcases.py:26-27) says an entry is a PRD-folder path "optionally followed by '#' and the exact text of a heading in that file". prd-format.md ("Test cases", `refs:`) says the same. Blanking fences is needed, because a `#` line in a code block is not a heading. Blanking inline spans is not needed. Not reproduced by a run: read from the code during the adoption extract of the area lint-testcases.
Resolution: T-162.6 [integration], PRD 9.7.0, fixed in 9038960641642100e5385ad435abbd9918434f7b
Recurrence of: -

### E-055 judged-case passes rubric items that prd_judge.py refuses as repeats
Detected: 2026-11-21, adoption extract of lint-testcases (prd-toolkit/scripts/prdlint/rules/testcases.py:365 @5483ca1)
Classification: code bug
Confirmed: 2026-11-21, "Confirm the class (form)"
Touches: FR-157
Evidence: judged-case reports a repeated rubric item when two items are equal after `str.strip()` (testcases.py:363-368). Its comment says it reports them because "prd_judge.py refuses it with exit 2: an answer cannot name each item", and commit 9e58d2e says the same. prd_judge.py refuses a rubric when two items are equal after `_collapse(r).strip()` (judge.py:245), and `_collapse` also turns every run of white space inside an item into one space (judge.py:39, 99-100).
Diagnosis: judged-case reports a repeated rubric item when two items are equal after `str.strip()` (testcases.py:363-368). Its comment says it reports them because "prd_judge.py refuses it with exit 2: an answer cannot name each item", and commit 9e58d2e says the same. prd_judge.py refuses a rubric when two items are equal after `_collapse(r).strip()` (judge.py:245), and `_collapse` also turns every run of white space inside an item into one space (judge.py:39, 99-100). So two items that differ only in inner white space, such as `The importer inserts no rows` and `The importer inserts no rows`, pass lint. prd_judge.py then exits 2 on them with `rubric repeats an item, so an answer cannot name each one`. Not reproduced by a run: read from the code during the adoption extract of the area lint-testcases.
Resolution: -
Recurrence of: -

### E-056 test-cases-consistent repeats the no-file finding for each T-id of a Tests line
Detected: 2026-11-21, confirmation of FR-150 (the answer of the owner to Q-27)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-150
Evidence: prd-toolkit/scripts/prdlint/rules/testcases.py:143-147 yields the finding inside the loop over the T-ids of the Tests line.
  In a copy of the fixture lint-cli/orders, line 8 of nfr.md replaced with `Tests: T-004.1 [system], T-004.2 [system], T-004.3 [system]`: `prd lint` exits 1 and prints `docs/prd/orders/nfr.md:8: test-cases-consistent: the Tests line of NFR-004 names no test-cases file; end it with (test-cases/<area>.yaml)` three times.
Diagnosis: For a block whose Tests line names no test-cases file, `test_cases_consistent` yields the finding inside its loop over the T-ids of that line (testcases.py:143-147). A line that lists three T-ids gets the same message at the same line three times. The owner answered Q-27 on 2026-11-21 that such a line gets the finding once, whatever the number of T-ids on it, and AC-150.1 now says so; the code does not. Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-150.7 [integration], PRD 9.7.0, fixed in 854efb18ec9dd7c36ba994607e4cf79e170198e2
Recurrence of: -

### E-057 classified-fixtures calls an address at a subdomain of a reserved example domain real-looking
Detected: 2026-11-21, confirmation of FR-168 (the answer of the owner to Q-31)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-168
Evidence: prd-toolkit/scripts/prdlint/rules/testcases.py:66: `return domain in _SYNTHETIC_DOMAINS or domain.endswith(_SYNTHETIC_SUFFIXES)`. The set (testcases.py:43) holds only `example.com`, `example.org` and `example.net`.
  `is_synthetic` returns False for an address at `mail.example.com` and at `sub.example.org`, and True for one at `example.com`.
Diagnosis: `is_synthetic` counts an email as synthetic only when its domain is exactly `example.com`, `example.org` or `example.net`, or ends with `.test`, `.example` or `.invalid` (testcases.py:43-44, 66). An address at `mail.example.com` therefore counts as real-looking, and `classified-fixtures` and `sufficiency` report it, though the three domains are reserved with every name under them. The owner answered Q-31 on 2026-11-21 that an address at a subdomain of the three domains counts as synthetic, and AC-168.2 now says so; the code does not. Reproduced by calling `is_synthetic`.
Resolution: T-168.7 [integration], PRD 10.4.0, fixed in 2515dc5
Recurrence of: -

### E-058 A list or mapping column class crashes contracts-valid
Detected: 2026-11-22, adoption extract of lint-contracts (prd-toolkit/scripts/prdlint/rules/contracts.py:367 @9961c9e)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-179
Evidence: prd-toolkit/scripts/prdlint/rules/contracts.py:367: `if kind not in _KINDS:`, and `_KINDS` (contracts.py:105) is a set.
  In a copy of the fixture lint-cli/orders, line 5 of contracts/data-classification.yaml replaced with `    columns: {id: internal, email: [pii], name: pii}`: `prd lint` exits 2 with stderr `prd_lint: internal error in rule contracts-valid: TypeError: cannot use 'list' as a set element (unhashable type: 'list')`.
Diagnosis: `_check_classification` tests `kind not in _KINDS`, and `_KINDS` is a set. A column class that is a YAML list or mapping (`columns: {email: [pii]}` or `{email: {a: b}}`) is unhashable, so the test raises `TypeError: unhashable type`. Nothing in the rule catches it, so `prd_lint` prints `prd_lint: internal error in rule contracts-valid: TypeError: …` and exits 2, instead of reporting `<t>.<c>: class [...] must be public, internal, confidential or pii`. Three things say this should be a finding. First, `prd-toolkit/tests/test_rules_contracts.py:146`, `test_malformed_shapes_never_crash`, asserts that malformed contract shapes give a `contracts-valid` finding and no `internal error`; its two classification inputs never put a list or mapping in the class position. Second, every sibling check in the file guards a value's type before it uses the value. Third, E-003 settled the same kind of TypeError escape as a bug. Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-179.8 [integration], PRD 10.4.0, fixed in cb01a35
Recurrence of: -

### E-059 A validator the system cannot execute crashes contracts-valid
Detected: 2026-11-22, adoption extract of lint-contracts (prd-toolkit/scripts/prdlint/rules/contracts.py:500 @9961c9e)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-182
Evidence: prd-toolkit/scripts/prdlint/rules/contracts.py:500-508: `subprocess.run` is wrapped by handlers for `FileNotFoundError`, `PermissionError` and `subprocess.TimeoutExpired` only.
  In a copy of the fixture lint-cli/orders, with an executable `tools/check.sh` holding `exit 0` and no shebang, and the lookml row of prd.md section 7 given the Validator `tools/check.sh`: `prd lint` exits 2 with stderr `prd_lint: internal error in rule contracts-valid: OSError: [Errno 8] Exec format error: 'tools/check.sh'`.
Diagnosis: `_check_custom` wraps `subprocess.run` but catches only `FileNotFoundError`, `PermissionError` and `TimeoutExpired`. Any other `OSError` escapes the rule, and `prd_lint` exits 2 with `prd_lint: internal error in rule contracts-valid: OSError: …`. Two examples are a validator file that has its execute bit but no shebang and is not a binary (`[Errno 8] Exec format error`), and an argument list too long for the system (E2BIG). The evidence that this should be a finding: the rule's own description says the custom type's validator "must run and pass" and tells the user to correct the Validator command. The sibling branches turn "not found" and "not executable" into findings. Commit 5a66652 decoded validator output as UTF-8 "so non-ASCII validator output under a C locale is a finding, not exit 2". Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-182.10 [integration], PRD 10.4.0, fixed in cb01a35
Recurrence of: -

### E-060 contracts-valid counts a field line inside a fenced code block for its event
Detected: 2026-11-22, confirmation of FR-173 (the answer of the owner to Q-32)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-173
Evidence: prd-toolkit/scripts/prdlint/rules/contracts.py:207-215: `_check_events` matches headings in the code-stripped text (`st`) but field lines in the original text (`orig.startswith(f + ":")`).
    In a copy of the fixture lint-cli/orders, line 4 of contracts/events.md replaced with three lines, a fence, `Trigger: a file arrives in the staging bucket.` and a fence: `prd lint` exits 0 and prints nothing.
Diagnosis: `_check_events` finds headings in the code-stripped text but tests field lines against the original text (contracts.py:207-215). A `Trigger:`, `Payload:`, `Delivery:`, `Retries:` or `Failure:` line inside a fenced code block therefore counts for the event around it, though a fenced `### ` line starts no event (AC-173.3). The owner answered Q-32 on 2026-11-22 that a fenced field line counts for no event, and AC-173.3 now says so; the code does not. Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-173.5 [integration], PRD 10.4.0, fixed in cb01a35
Recurrence of: -

### E-061 contracts-valid accepts a permissions role with no secret
Detected: 2026-11-22, confirmation of FR-176 (the answer of the owner to Q-33)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-176
Evidence: prd-toolkit/scripts/prdlint/rules/contracts.py:290-292: a role is checked for `identity` only; `secret` is never read.
    In a copy of the fixture lint-cli/orders, line 2 of contracts/permissions.yaml replaced with `  admin: {identity: test-admin}` and line 3 with `  rep: {identity: test-rep, secret: ''}`: `prd lint` exits 0 and prints nothing.
Diagnosis: `_check_permissions` checks each role for `identity` only (contracts.py:290-292). prd-format.md gives a role the shape `{identity, secret}`, and a test's credentials come from its role's `secret`. The owner answered Q-33 on 2026-11-22 that a role with no secret, or an empty one, is a finding, and AC-176.8 now says so; the code reports nothing. Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-176.8 [integration], PRD 10.4.0, fixed in cb01a35
Recurrence of: -

### E-062 error-codes reads the failures of dependency files in subfolders of contracts/dependencies/
Detected: 2026-11-22, confirmation of FR-184 (the answer of the owner to Q-35)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-184, FR-185
Evidence: prd-toolkit/scripts/prdlint/rules/contracts.py:600-603: `error_citations` reads `failures` from every loaded YAML file whose path starts with `contracts/dependencies/`, at any depth; `contracts-valid` checks only the `.yaml` files directly in that folder (AC-180.5).
    In a copy of the fixture lint-cli/orders, with contracts/dependencies/old/legacy.yaml holding `failures:` and `  timeout: NOT_CATALOGUED`: `prd lint` exits 1 and prints `docs/prd/orders/contracts/dependencies/old/legacy.yaml:2: error-codes: error code NOT_CATALOGUED is not in contracts/errors.yaml`.
Diagnosis: `error_citations` reads `failures` from every loaded YAML file under `contracts/dependencies/`, at any depth (contracts.py:600-603), while `contracts-valid` checks only the `.yaml` files directly in that folder (AC-180.5). A file in a subfolder therefore cites codes for `error-codes` (FR-184) and counts as a citation for FR-185, though it is no dependency file. The owner answered Q-35 on 2026-11-22 that the dependency files are the `.yaml` files directly in `contracts/dependencies/` and that `error-codes` reads failures only from those, and AC-184.3 now says so; the code does not. Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-184.6 [integration], PRD 10.4.0, fixed in cb01a35
Recurrence of: -

### E-063 A custom type's Files glob passes files outside the PRD folder to the validator
Detected: 2026-11-22, confirmation of FR-181 (the answer of the owner to Q-36)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-181
Evidence: prd-toolkit/scripts/prdlint/rules/contracts.py:450: `glob.glob(g, root_dir=prd.root, recursive=True)` keeps every match that is a file, with no check that it lies in the PRD folder.
    In a copy of the fixture lint-cli/orders, with docs/prd/outside.lkml written and the lookml row of prd.md section 7 given the Files `contracts/custom/*.lkml ../outside.lkml` and a validator that prints its arguments and exits 1: `prd lint` prints `docs/prd/orders/prd.md:80: contracts-valid: custom type lookml: validator failed: ['../outside.lkml', 'contracts/custom/sample.lkml']`. With the Files cell set to the file's absolute path, the validator receives that absolute path.
Diagnosis: `custom_types` keeps every file a Files glob matches (contracts.py:450), so an absolute glob or one that climbs out with `..` passes files outside the PRD folder to the validator, and AC-181.1 already says a type's files are files in the PRD folder. The owner answered Q-36 on 2026-11-22 that such a match is a finding and is not passed to the validator, and AC-181.4 now says so; the code does neither. Reproduced in a copy of the fixture lint-cli/orders.
Resolution: T-181.6 [integration], PRD 10.4.0, fixed in cb01a35
Recurrence of: -

### E-064 The prd-tester guard finds the PRD from the session's working directory, so a dispatch for a PRD in another repository may read nothing
Detected: 2026-11-22, user report (/prd-toolkit:prd-error), a dry-run dispatch
Classification: code bug
Confirmed: 2026-11-22, "not a defect, close it"
Evidence: A Claude Code session started in <session dir>, a folder that holds no docs/prd/ folder, dispatched the
  prd-toolkit:prd-tester agent for a dry run (changing-prds step 4) of a PRD in another repository:
    Mode: dry run
    PRD: <other repo>/docs/prd/<slug>/
    Dry-run directory: <other repo>/<test root>/.prd-dry-run-<timestamp>/
  The guard refused every call of the tester, its Bash ls of the PRD folder and its Read of the test-case file:
    prd-tester may only read under: (none) (testing.md is missing or has no Test roots: no docs/prd/*/ folder)
  The tester wrote no test and reported TESTS: none. The repository's git status was the same before and after.
Diagnosis: not a defect: reproduced once. Given the hook input of a prd-tester whose session started in a folder that holds no docs/prd/ (its cwd) and a Read of a testing.md in another repository, prd_tester_guard.py exits 2 with `prd-tester may only read under: (none) (testing.md is missing or has no Test roots: no docs/prd/*/ folder)`. The guard takes the repository from `git rev-parse --show-toplevel` run in the hook input's cwd (`Context.__init__` and `_toplevel`), and `_load_prds` reads docs/prd/*/ under it; with no PRD there its read roots are empty, so it refuses every call. No adopted area covers prd-toolkit/scripts/prd_tester_guard.py (tester-guard is not started), so its account is its own, and the README states this binding: "A dry run and a build dispatch agents bound to the session's own repository, so they run in a session started in that member's root", and in its limits, "a dry run or build of a member runs in a session started in that member's root". It also failed closed, as its docstring says: "For the tester it never fails open: any error blocks." The caller is what went wrong: changing-prds step 4 and testing-from-prds/dispatching.md dispatched the tester from a session started outside the PRD's repository, and neither says to check that first. That is a change to those skills, not a defect of the guard.
Resolution: not a defect: the guard binds the tester to the session's own repository, as the README says: "A dry run and a build dispatch agents bound to the session's own repository, so they run in a session started in that member's root"; a dispatch for a PRD in another repository runs from a session started in that repository's root
Recurrence of: -

### E-065 --sources reads a changed path's hunks through a glob pathspec, so another file's hunks can admit a SOURCES line
Detected: 2026-11-22, adoption extract of build-check (prd-toolkit/scripts/prdlint/buildcheck.py:186 @2caf953)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-193
Diagnosis: hunks_of runs `git diff -U0 --no-color --no-renames <base> <head> -- <path>` with no `--literal-pathspecs` (buildcheck.py:186), so git reads the path as a glob pathspec. If a changed file's name holds `*`, `?` or `[`, its hunk list also takes the hunks of every other changed file the pattern matches: a round that changes `src/x*.py` at line 1 and `src/xy.py` at line 50 lets the line `FR-001: src/x*.py:50` pass, though `src/x*.py` has no change at line 50. The path test just above (`path not in changed`) reads the path literally, as do the module's other git reads: `--stale` runs `git --literal-pathspecs log` and `status` (lines 254 and 296), and `--diff` reads blobs as `<rev>:<path>`. Commit 259c29b made the check read paths literally; `--sources` came later (d14b0ea), with no literal flag.
Resolution: -
Recurrence of: -

### E-066 The plugin-directory search reads git ls-tree without -z, so a plugin under a non-ASCII folder name is never found
Detected: 2026-11-22, adoption extract of build-check (prd-toolkit/scripts/prdlint/buildcheck.py:71 @2caf953)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class (form)"
Touches: FR-191, FR-192
Diagnosis: plugin_dir lists the head tree with `git ls-tree -r --name-only <rev>` and splits the output at newlines (buildcheck.py:71-75). With git's default `core.quotePath`, a path that holds a byte above 0x7F (or a quote, backslash or control character) is printed C-quoted, such as `"pl\303\274gin/.claude-plugin/plugin.json"`; that name does not end in `/.claude-plugin/plugin.json`, so the plugin directory is never found, and an exact vendor refresh in such a repository gets the AC-191.1 refusal instead of the comparison of AC-192.1. The sibling reads in the same module use `-z` for this reason: `refresh_differences` (line 113) and `_case_entries` (line 267); commit 78c95a6 says `--stale` uses `ls-tree -z` so a non-ASCII name is not C-quoted away.
Resolution: -
Recurrence of: -

### E-067 The Glossary part matches a term against the "(area: …)" label the pack adds to a block's heading
Detected: 2026-11-22, adoption extract of context (prd-toolkit/scripts/prdlint/context.py:91 @f5d2b4c)
Classification: code bug
Confirmed: 2026-11-22, "Confirm the class: The Glossary part prints the glossary rows whose term appears in the selected blocks' own text, the heading as written and the block's lines, never in the (area: <name>) label the pack adds to another area's heading. (form)"
Touches: FR-208, FR-209
Diagnosis: `_block_text` (context.py:87-92) adds ` (area: <other>)` to the heading of a block from another area. `build_pack` (context.py:508-509) joins those labelled texts into `text`, and `_glossary` (context.py:162-163) searches `text` for each section 3 Term. A Term the label holds, such as `area` (a term in this PRD's own glossary, prd.md line 67), is therefore printed for any `--req` block of another area, whether or not the block says it. The 0.3 design (docs/superpowers/specs/2026-10-30-prd-toolkit-0.3-design.md, line 96) says the Glossary holds "the §3 rows whose Term occurs (case-insensitive, whole word) in a selected block". The label is the pack's annotation, not text of the block.
Resolution: -
Recurrence of: -

### E-068 The decision inbox stops answering in a repository with many worktrees: each listing loads every worktree's PRD, and the page asks again every 5 seconds before the last listing ends
Detected: 2026-11-22, adoption confirmation of context (prd-toolkit/scripts/prdlint/gates.py:1004 @ad9c628)
Classification: code bug
Confirmed: 2026-11-22, "confirm E-068 as a code bug"
Touches: -
Diagnosis: `_Inbox.listing` (gates.py:1002-1022) loads the PRD of every worktree of the repository with `model.load` and lists its gates on every `GET /gates`. With seven worktrees holding the PRD, one listing took about 60 seconds when run alone (8 to 12 seconds per worktree, most of it in the pure-Python YAML loader). The inbox page (templates/gates/inbox.html:517) calls `refresh` every 5 seconds with `setInterval`, whether or not the last `GET /gates` has returned, and the server (formserver.py:149, a ThreadingHTTPServer) starts a thread for each one, so the listings run at once and share one interpreter: none returned within 120 seconds, and an item answer sent from the form never completed. The `wait` process, polling the same gate, also kept a CPU busy. Seen on 2026-11-22 with worktrees main, adopt-context and five fix worktrees: the inbox recorded an error-class confirmation at 15:02, then a confirmation-form answer for FR-199 hung, and `/gates` timed out at 120 seconds.
Resolution: fixed in de6cb39219be4b00005b8bcd9f2375b96fe6519d, red run prd-toolkit/tests/test_inbox_listing_load.py [unit]
Recurrence of: -

### E-069 A slot value that holds a later slot's placeholder is rewritten
Detected: 2026-11-22, adoption extract of status (prd-toolkit/scripts/prd_block.py:202 @3a70ba0)
Classification: code bug
Confirmed: 2026-11-22, "code bug (Recommended)"
Touches: FR-241, FR-242, FR-235
Diagnosis: `_fill` (prd_block.py:202) and `render_block` (prd_block.py:119) put the slot values into a template one slot after another, each with `str.replace` over the whole text. Text already put in is therefore searched again for every later slot. A §2 summary that holds `{{areas}}`, `{{files}}` or `{{links}}` has that text replaced in the README by the areas table, the files table or the links part. A parent row whose Covers text holds `{{homepage}}` gets the homepage URL. A section 6 Object cell holding `{{adopted_areas}}` gets the adopted areas in the CLAUDE.md block. The 0.8.4 design (docs/superpowers/specs/2026-11-04-prd-toolkit-0.8.4-prd-readmes-design.md §3 and §4) says the summary slot is "§2's first paragraph, word for word" and Covers is "§2's first sentence". FR-241 and FR-242 are written only for values that hold no `{{…}}` text.
Resolution: -
Recurrence of: -

### E-070 A file the block command creates is readable only by its owner
Detected: 2026-11-22, adoption extract of status (prd-toolkit/scripts/prd_block.py:315 @3a70ba0)
Classification: code bug
Confirmed: 2026-11-22, "code bug (Recommended)"
Touches: FR-237, FR-239
Diagnosis: `_replace` writes through `tempfile.mkstemp`, which creates its file with mode 0600, and copies a mode onto it only when the target already exists (prd_block.py:319). A `CLAUDE.md`, PRD README or parent README that the command creates is therefore 0600, whatever the umask: the group and others cannot read it. The sibling writer of a committed file, `prdlint/changeset.py:_write`, gives a new file `0o666 & ~umask` for exactly this reason (commit 42df229, "keep change-set records readable and write them whole"). FR-239 covers only a file that already exists.
Resolution: -
Recurrence of: -

### E-071 An HTML comment inside a summary line leaves its width as spaces
Detected: 2026-11-22, adoption extract of status (prd-toolkit/scripts/prdlint/overview.py:57 @3a70ba0)
Classification: code bug
Confirmed: 2026-11-22, "code bug (Recommended)"
Touches: FR-247, FR-241
Diagnosis: `_section2` replaces each HTML comment with spaces, to keep line numbers (overview.py:57). `summary_paragraph` then takes its lines from that text and strips only their ends. A §2 line `Intro <!-- note --> text` is summarised as `Intro`, fifteen spaces and `text`, and the README writes it that way after `> `. The docstring of `summary_paragraph` and references/prd-format.md (§2's summary is "its first run of non-blank lines once HTML comments are removed") say the comments are removed, not blanked. `first_sentence` collapses white space, so the parent's Covers cell is unaffected. FR-247's cases use comments that fill a whole line.
Resolution: -
Recurrence of: -

### E-072 Outside a git checkout and without --claude-md, the block command writes CLAUDE.md inside the PRD folder
Detected: 2026-11-22, confirmation of FR-246, the owner's answer to Q-47 (prd-toolkit/scripts/prd_block.py:351 @3a70ba0)
Classification: code bug
Confirmed: 2026-11-22, "code bug (Recommended)"
Touches: FR-246
Diagnosis: When the PRD folder is in no git checkout and `--claude-md` is not given, `main` takes the repository root from `model.repo_root(prd.root)` (prd_block.py:351), which falls back to the PRD folder itself, and writes `CLAUDE.md` there; the block names the PRD at `.` (prd_block.py:268-272). Lint then reads that `CLAUDE.md` as one of the PRD folder's files. The owner answered Q-47 that this is a defect: the command should refuse, printing `prd_block: <folder>: not inside a git checkout; name the CLAUDE.md with --claude-md`, writing nothing and exiting 2.
Resolution: -
Recurrence of: -

### E-073 The generated CI workflow has no way to add a runner setup step before a job's command
Detected: 2026-11-23, user report (adoption of SQLAnvil/sqlanvil, generated CI)
Classification: spec gap
Confirmed: 2026-11-23, "Confirm the class (form)"
Touches: FR-114, FR-116, FR-117
Evidence: Reported from the adoption of SQLAnvil/sqlanvil (PR #65, 2026-11-23), on prd-toolkit 0.8.14.
  Every Bazel job of the first generated CI run (45205148047) failed while Bazel loaded:
  java.io.FileNotFoundException: /home/runner/.npmrc
  The repository's MODULE.bazel sets rules_js use_home_npmrc = True, which fails when the file is missing.
  testing.md's Harness already named the file as a runner tool, but nothing in the generated workflow could create it.
  prdlint/hooks.py render_github (line 608) gives every job exactly actions/checkout@v4, astral-sh/setup-uv@v5, then the command.
  A Levels command must be one simple command, so no "touch ~/.npmrc && ...".
  A hand edit of the workflow fails prd hooks check --ci, which compares the file byte for byte.
  Workaround used there: a scripts/bazel-ci wrapper as the first word of every Bazel command (it creates the file, then exec bazel "$@").
  Ask: a way for the PRD to state per-runner setup that the generator renders as steps before the command, for GitHub and GitLab alike.
Explanation: What was run: in a throwaway copy of this repository, the PRD testing.md Harness was made to say the runner needs the file ~/.npmrc, and both CI files were generated from it. What it printed: every job in both files still runs only the standard steps (get the code, install uv, run the command); the word npmrc appears nowhere in either file. What the PRD says should happen: the CI rules list those standard steps exactly and say nothing more, and the Harness line that names what the runner needs is only checked for being present and in order; no rule says CI does anything with it. So the generator does exactly what the PRD says, and the PRD is silent on how a runner gets what the Harness says it needs. Why this class: it is not a code bug, because the code matches the PRD word for word; it is a spec gap if you want the PRD to give a way to set the runner up, and not a defect if you want runner setup to stay the project own business (a wrapper script, as SQLAnvil used, or a CI image). Do you want a PRD line that lets a project state runner setup, rendered as steps before each job command on GitHub and GitLab, or no change, with runner setup left to the project? The first makes it a spec gap, fixed by new acceptance criteria in the existing CI rules; the second makes it not a defect, closed with nothing changed.
Diagnosis: The CI renderers follow AC-117.1 and AC-116.1 exactly, and no AC, contract or test case covers setting up the runner a Harness describes. AC-117.1 (FR-117): per job, ` <id>:`, ` runs-on: ubuntu-latest`, ` steps:`, ` - uses: actions/checkout@v4`, ` with:`, ` fetch-depth: 0` and ` - uses: astral-sh/setup-uv@v5`; one ` - run: <command>` line per command. AC-116.1 (FR-116): ` before_script:`, ` - "pip install uv"` and ` script:`; one ` - <command>` line per command. AC-114.1 (FR-114): a `test-<level>` job whose one command is that backticked text. Searched and found silent on runner setup: hooks-install FR-113 to FR-118, lint-structure FR-025 (AC-025.2 checks only that the Tools on the runner slot is present and in order), testing.md. Run: a probe in a scratch clone added `The runner needs the file ~/.npmrc` to the Tools on the runner slot of docs/prd/prd-toolkit/testing.md, then `sh .prd-toolkit/prd hooks ci --github --force docs/prd/prd-toolkit` and `sh .prd-toolkit/prd hooks ci --gitlab --force docs/prd/prd-toolkit`; expected per the report: a setup step before the command; printed: `ci-github-exit=0`, `ci-gitlab-exit=0`, `npmrc in github: 0`, `npmrc in gitlab: 0`, and job test-unit holds only `actions/checkout@v4`, `astral-sh/setup-uv@v5`, `- run: "uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd"` (GitLab: `pip install uv`, then the command). Root cause: prdlint/hooks.py render_github and the GitLab renderer emit a fixed step list because the PRD gives no per-runner setup to render; a Levels command must be one simple command, and hooks check --ci refuses a hand edit, so a project cannot add one either.
Resolution: T-114.3 [integration], PRD 10.1.0, fixed in 906fbf3
Recurrence of: -

### E-074 A standards row's CI command always gets the matching file paths appended, even a command that takes none
Detected: 2026-11-23, user report (adoption of SQLAnvil/sqlanvil, generated CI)
Classification: spec gap
Confirmed: 2026-11-23, "Confirm the class (form)"
Touches: FR-068, FR-114
Evidence: Reported from the adoption of SQLAnvil/sqlanvil (PR #65, 2026-11-23), on prd-toolkit 0.8.14.
  The standards row cli/README.md -> bazel test //cli:readme_generated_test was rendered as:
  git ls-files -z ... -- ':(glob)cli/README.md' ... | xargs -0 -r bazel test //cli:readme_generated_test
  bazel test received ./cli/README.md and refused it (run 45207610173, job standards-3):
  invalid target name './cli/README.md': target names may not contain '.' as a path segment
  prdlint/standardsrun.py ci_command (line 18) always pipes the glob's files into the command through xargs.
  Related, same run: a row that lints a whole tree (bazel run //:eslint -- '**/*.ts') gets every file appended too.
  A row whose text says it checks "files changed on the branch" has no way to say so; the job checks every tracked file.
  Workaround used there: the owner declined the README row (the unit level already runs that target).
  Ask: let a row say how its command takes files: appended (today), none (run once), or changed-since-base.
Explanation: What was run: in a throwaway copy of the repository, two checks were added to the PRD standards table, each a command that takes no files (one checks a single generated file, one lints a whole tree). The CI workflow was then generated and each check job was run, and the pre-commit hook was run with that single file staged. What it printed: the single-file check was handed that file path by its CI job, the tree lint was handed all 77 matching files, and the pre-commit hook handed the single-file check the staged path. A command such as bazel test //cli:readme_generated_test refuses a path it did not ask for, which is how the sqlanvil job failed. What the PRD says: each row CI job lists the tracked files the glob matches and appends them to the command, and the pre-commit hook gives the command the staged files the glob matches. It says nothing of a command that takes no files, or only the files changed on the branch, and gives a row no way to say so. Why this class: the code does exactly what the PRD says, so it is not a code bug; whether it is a defect at all turns on what you want. Do you want a row to be able to say how its command takes files (the matching files appended, as today; no files, run once; or only the files changed on the branch)? Or should a row command be written to ignore the files it is given (a whole-tree check wrapped as sh -c "..." --)? The first makes it a spec gap, fixed by adding that to the PRD; the second makes it not a defect, and nothing changes.
Diagnosis: Root cause: prdlint/standardsrun.py ci_command (line 18), called by prdlint/hooks.py ci_jobs (line 555) for each enforced row, always pipes the glob tracked files into the row command through `xargs -0 -r`, as AC-068.4 says: "the hooks command shall give the job `standards-<n>` of each enforced row the one command `git ls-files -z --format='./%(path)' -- <pathspec> ':(exclude).prd-toolkit' | xargs -0 -r <command>`". AC-068.1 likewise gives the pre-commit linter "every staged path that exists after the commit and that the row's glob matches". No AC, section 5 column or test case lets a row say its command takes no files, or only the files changed since the base; FR-114 (the merge-gate jobs) and FR-132/FR-133 (the row cells) are silent too. Probe in a scratch clone: two enforced rows added to section 5, `prd-toolkit/README.md` with a command that logs its arguments (readme-check) and `prd-toolkit/scripts/**/*.py` with a whole-tree lint stand-in (tree-lint); `sh .prd-toolkit/prd hooks ci --github --force docs/prd/prd-toolkit` printed `wrote .github/workflows/prd-toolkit.yml`, and each job run, executed from the root, logged `[CI standards-2] readme-check got 1 args: ./prd-toolkit/README.md` and `[CI standards-3] tree-lint got 77 args`, where a command that takes no files expects `0 args`. `sh .prd-toolkit/prd git-hook pre-commit docs/prd/prd-toolkit` with the README staged logged `readme-check got 1 args: prd-toolkit/README.md`. The toolkit own row (`npx -y @anthropic-ai/claude-code plugin validate ./prd-toolkit`) is rendered the same way as standards-1, every prd-toolkit/** file appended. The code does what the PRD says; the PRD has no way to say otherwise.
Resolution: T-264.1 [integration], PRD 10.4.0, fixed in ef5b43e
Recurrence of: -

### E-075 An environment or standard fix proven by a CI run has no resolution form that prd error check accepts
Detected: 2026-11-23, user report (adoption of SQLAnvil/sqlanvil, generated CI)
Classification: spec gap
Confirmed: 2026-11-23, "spec gap, add the CI run form"
Touches: FR-081, FR-080
Evidence: Reported from the adoption of SQLAnvil/sqlanvil (PR #65, 2026-11-23), on prd-toolkit 0.8.14.
  Four entries of class environment (sqlanvil E-008, E-009, E-011, E-012) were fixed by PRD changes plus a new green CI run, 45211614726.
  prd error resolve ... --run 45211614726 --version 1.0.2 accepted each one.
  prd error check then reports, for every one of them:
  run 45211614726 has no log in <git common dir>/prd-toolkit/deploys
  because --run means a /prd-toolkit:prd-deploy run, not a forge CI run.
  Same gap for class standard: sqlanvil E-010 was fixed by a .prettierignore change and a formatting-only edit, with no --fixes build and no T-id.
  No resolution form fits it: the code-fix form needs --t, and --red-run is for code bugs.
  Where: prdlint/errors.py line 355.
  Workaround used there: none; the lines stand as resolve wrote them, and prd lint --ci still passes.
  Ask: a resolution form for a fix proven by a CI run (for example --ci-run <forge run id>, with the forge named), for environment and standard entries whose fix builds no T-id.
Explanation: What was run: in a scratch copy of this repository, two test entries were set up the way SQLAnvil had them. An environment entry was closed with the id of a GitHub Actions run, and the ledger was then checked. For a standard entry, closing it with only a commit (no test id) was tried, then closing it as a red run. What it printed: closing the environment entry with the CI run id was accepted, but the check then said that run has no log in the deploys folder. Closing the standard entry without a test id was refused (a fix needs a T-id, its level and a commit), and the red run was refused because a red run closes code bugs only. What the PRD says should happen: exactly that. The PRD gives four ways to close an entry: a fix proven by a test id, a deploy run made by /prd-toolkit:prd-deploy, not a defect, and a red run for code bugs outside every adopted area. Its check must report a run id that has no deploy log. A forge CI run is none of the four, so the toolkit did what the PRD says. Why this class: the code and the PRD agree, so it is not a code bug. Whether it is a spec gap depends on what you want. Do you want a fifth way to close an entry, a fix proven by a green forge CI run (for environment and standard entries whose fix has nothing for a test id to test, like a formatting change)? Or do you want the rule to stay: environment entries close on a /prd-toolkit:prd-deploy run, and every other fix closes on a test id? The first makes it a spec gap, fixed by a PRD change and a build. The second makes it not a defect, and SQLAnvil re-closes its entries by one of the four ways.
Diagnosis: not a defect: the run does what AC-081.3 and AC-081.4 state. Probe in a scratch clone of 932a764 (PRD 10.0.0): an environment entry (E-076 there) confirmed, then `prd error resolve docs/prd/prd-toolkit E-076 --run 45211614726 --version 10.0.0` printed `E-076 resolved environment` and wrote `Resolution: -, PRD 10.0.0, run 45211614726`; `prd error check docs/prd/prd-toolkit <base>..HEAD` printed `errors.md: E-076: run 45211614726 has no log in <clone>/.git/prd-toolkit/deploys` and exited 1. AC-081.3 expects exactly that: for an environment run `-, PRD <X.Y.Z>, run <run id>` whose run id has no deploy run log, the stdout line `errors.md: <E-id>: run <run id> has no log in <folder>`. A standard entry (E-077 there) confirmed, then `prd error resolve ... E-077 --version 10.0.0 --commit <sha>` printed `prd_error: a fix needs a T-id, its level and a commit` (exit 2), and `--commit <sha> --red-run tests/test_x.py --level unit` printed `refused: E-077 is classed standard; a red run resolves a code bug only` (exit 1), as AC-081.4 (the three older forms, a fix needing --t) and the red-run refusals of FR-080 state. error-replay definitions: the four forms are a fix with a T-id, an environment run `<T-id or ->, PRD <X.Y.Z>, run <run id>`, not a defect, and a red run; none names a forge CI run. Root cause: the PRD has no resolution form for a fix proven by a forge CI run (errors.py _ENV and _run_finished read only deploy logs, line 355). A side effect the PRD leaves open: resolve accepts any `--run` id and makes no run (AC-081.4), so it writes a line that check is bound to refuse when the id is not a deploy run.
Resolution: T-081.23 [integration], PRD 10.3.0, fixed in 86b7dd5
Recurrence of: -

### E-076 record never lists a UJ that a changed contract item cites
Detected: 2026-11-23, adoption extract of change (prd-toolkit/scripts/prdlint/change.py:602 @169036a)
Classification: code bug
Reopened: 2026-11-23, "the class was proposed and confirmed on a code reading, before any run; it is proposed again with the probe's run quoted"; was Confirmed: 2026-11-23, "Confirm the class (form)"
Confirmed: 2026-11-23, "Code bug (Recommended)"
Touches: FR-260
Explanation: Run on a change that edits a contract item naming a user journey, record left that journey out of the changelog row while it listed the requirement named beside it. The code's own description and its design say the journey belongs there, so the code is wrong, not the PRD: a code bug.
Diagnosis: A probe (scratchpad probe.py, in a scratch git repository built from fixture status-next/base, running prd_change.py at 169036a) added a block `### UJ-01 Import a file` to features/import.md and committed it, changed the errors.yaml message to `The import file has no header line (FR-001, UJ-01).`, and ran `prd_change.py record docs/prd/orders --base HEAD --bump patch --change 'cite a journey'`: exit 0, row `| 1.0.1 | 2026-11-23 | cite a journey; pending | FR-001 |`. FR-001 is listed and UJ-01 is not. The cause: `_CITED_BLOCK` (prdlint/change.py:602) matches `(?:UJ|FR|NFR)-\d{3}`, three digits, but a UJ ID has two (`UJ-03`: prd-format.md decision 6; `next_id` writes `UJ-{:02d}`), and `UJ-003` names no block, so the `id_ in have` filter drops it. The function's docstring says "The UJ, FR and NFR IDs a contract item cites", and the 0.8.3 design (§4 (j)) says every other item "cites each `UJ-nnn`, `FR-nnn` and `NFR-nnn` token in its text". The owner answered at confirmation that it is a bug (FR-260 corrected with AC-260.9).
Resolution: -
Recurrence of: -

### E-077 record adds a second pending row when it runs again at another level
Detected: 2026-11-23, adoption confirmation of change, the owner's answer to Q-52 (prd-toolkit/scripts/prdlint/change.py:728 @169036a)
Classification: code bug
Confirmed: 2026-11-23, "Code bug (Recommended)"
Touches: FR-260
Explanation: Recording the same change twice at two levels left two pending changelog rows, and nothing can remove the first, though the toolkit's own instructions say a rerun replaces its pending row and forbid editing it by hand. The owner said the rerun should replace it, so the code is wrong: a code bug.
Diagnosis: A probe (scratchpad probe.py, in a scratch git repository built from fixture status-next/base, running prd_change.py at 169036a) changed one AC's wording in features/import.md, then ran `prd_change.py record docs/prd/orders --base HEAD --bump minor --change first` (exit 0, row `| 1.1.0 | 2026-11-23 | first; pending | FR-001, AC-001.1 |`) and `prd_change.py record docs/prd/orders --base HEAD --bump major --change second` (exit 0, row `| 2.0.0 | 2026-11-23 | second; pending | FR-001, AC-001.1 |`). §14 then holds both rows ending `; pending`, and no command removes the first. The cause: `_write_prd_md` (prdlint/change.py:710) replaces the last row only when its version equals the computed one. The changing-prds skill says to "run `record` again, which replaces its own `pending` row" and forbids hand edits of §14. The owner answered Q-52 that a rerun should replace a last row ending `; pending` whatever its version.
Resolution: -
Recurrence of: -

### E-078 approve takes a capitalised No dry run record for a non-unit test
Detected: 2026-11-23, adoption confirmation of change, the owner's answer to Q-55 (prd-toolkit/scripts/prdlint/change_approve.py:71 @169036a)
Classification: code bug
Confirmed: 2026-11-23, "Code bug (Recommended)"
Touches: FR-262
Explanation: The approval refused a change with an integration test and no dry run when the record said `no dry run`, but approved the same change when it said `No dry run`. The check is there to stop exactly that, and the owner said the letter case must not matter, so the code is wrong: a code bug.
Diagnosis: A probe (scratchpad probe.py, in a scratch git repository built from fixture status-next/base, running prd_change.py at 169036a) recorded a change adding FR-008 with the integration case T-008.1 (row `| 1.1.0 | 2026-11-23 | Refuse an empty file; pending | FR-008, AC-008.1, T-008.1 |`), wrote a ready verdict with the folder's digest, and ran approve twice. `--dry-run 'no dry run (unit only)'`: exit 1, `refused: the change adds or revises a non-unit test (T-008.1) and has no dry-run record`. `--dry-run 'No dry run (unit only)'`: exit 0, `approved orders 1.1.0 ec7cd5f`. The cause: change_approve.py:88 tests `dry_run.strip().startswith("no dry run")`, lowercase only. AC-262.4's check exists so that a change with a non-unit test is never approved without a dry run; the owner answered Q-55 that the prefix should match in any letter case.
Resolution: -
Recurrence of: -

### E-079 approve prints a string blockers one character at a time
Detected: 2026-11-23, adoption confirmation of change, the owner's answer to Q-56 (prd-toolkit/scripts/prdlint/change_approve.py:71 @169036a)
Classification: code bug
Confirmed: 2026-11-23, "Code bug (Recommended)"
Touches: FR-262
Explanation: A review verdict that lists its one blocker as a word rather than a list made the refusal print the word letter by letter (`l; i; n; t`) instead of `lint`. The owner said it should print the word whole, so the refusal message is wrong: a code bug.
Diagnosis: A probe (scratchpad probe.py, in a scratch git repository built from fixture status-next/base, running prd_change.py at 169036a) recorded the same change as E-078's probe, wrote `.prd-review.json` as `{"digest": <the folder's digest>, "ready": false, "blockers": "lint"}` and ran `prd_change.py approve docs/prd/orders --reply approved --dry-run 'dry run T-008.1, 0 open questions'`: exit 1, `refused: the review is not ready: l; i; n; t`. With `"blockers": ["lint"]` the same run printed `refused: the review is not ready: lint`. The cause: change_approve.py:44 joins `blockers` with `"; ".join(str(b) for b in blockers)`, which walks a string one character at a time. The owner answered Q-56 that a string `blockers` should be printed whole.
Resolution: -
Recurrence of: -

### E-080 prd error check accepts a Resolution line whose PRD version was recorded by another change
Detected: 2026-11-23, closing E-075 (PR #54)
Classification: not a defect
Confirmed: 2026-11-24, "Confirm the class (form)"
Touches: FR-081
Evidence: Seen while closing E-075 (PR #54, 2026-11-23).
  E-075 was resolved at e211a6f as: Resolution: T-081.23 [integration], PRD 10.2.0, fixed in 86b7dd5
  Its change was then re-recorded on top of main and approved as PRD 10.3.0 (71247f9), after the change-area adoption merged as 10.2.0 (PR #53).
  The fixing session reported: prd error check had not flagged 10.2.0, since that version has #53's row in section 14.
  So the Resolution line named a version recorded by another change (the change-area adoption), not the version that carried E-075's regression test.
  The line was edited to PRD 10.3.0 by hand (2a70b7b) on the owner's choice.
Explanation: I re-ran the reported case: the check of E-075 at the point where its resolution still named PRD 10.2.0, while the PRD was at 10.3.0 and its regression test T-081.23 had been recorded by the 10.3.0 change. The check printed nothing and passed. The PRD says it should: the check accepts a fix whose version has a changelog row and is not above the PRD version, and 10.2.0 met both, because 10.2.0 is the change-area adoption that merged first. So the code and the PRD agree, which makes this not a defect as the PRD stands. The question is what you want. Do you want the check to accept any recorded version that is not above the PRD (what it does now, and what let E-044 and E-045 keep 10.3.1 today), or to require the version of the change that recorded the entry regression test whenever such a change exists (which would have refused E-075 at 10.2.0 and asked for 10.3.0)? The first keeps it not a defect, and nothing changes. The second makes it an invalid requirement: the rule in the PRD is revised first, then the check is built to match.
Diagnosis: not a defect: run in a scratch clone at `2a70b7b^` (PRD `version: 10.3.0`; E-075 line `Resolution: T-081.23 [integration], PRD 10.2.0, fixed in 86b7dd5`): `.prd-toolkit/prd error check docs/prd/prd-toolkit e211a6f^..HEAD` printed nothing and `prd-error-exit=0`. AC-081.3 says the check shall print nothing for a fix with a T-id `whose <X.Y.Z> has a section 14 row and is not above the PRD's version at <head>`; 10.2.0 has the section 14 row of the change-area adoption (PR #53) and is below 10.3.0, so the output is the one AC-081.3 gives. The row that lists T-081.23 is 10.3.0 (E-075 change, 71247f9), but no AC asks the check to match the version to that row. The code (`_version_findings` in prdlint/errors.py) checks exactly the two conditions AC-081.3 names. If the owner wants the version tied to the change that recorded the regression T-id, AC-081.3 is too permissive and the class is invalid requirement on FR-081.
Resolution: not a defect: AC-081.3 says check prints nothing for a fix with a T-id whose version has a section 14 row and is not above the PRD version at head; E-075 at 10.2.0 met both, and the owner confirmed that rule stands
Recurrence of: -

### E-081 changeset approve refuses a record stopped before its first approval, with and without --amendment
Detected: 2026-11-24, user report (/prd-toolkit:prd-error)
Classification: code bug
Confirmed: 2026-11-24, "Confirm the class (form)"
Evidence: User report: a change set's step 2 lint was blocked in one member, and the session recorded it with `changeset stop`.
  After the blocker was fixed, the owner replied to every member's PRD diff. Then:
  changeset approve <record> --reply '<reply>'
    refused: CS-001 is stopped: <prd>: <reason>, not proposed; a later approval is an --amendment
  changeset approve <record> --reply '<reply>' --amendment
    refused: CS-001 has no approval to amend
  The only way on was to abandon the record and start a new change set with the same members (new branches, a new record, a second approval reply for the same diffs). It happened in two change sets in two repositories.
Explanation: What was run: a probe made a three-member change set, stopped it before anyone approved it (as a session does when a member's lint is blocked), then gave the owner's approval reply both ways the command offers. What it printed: the plain approval was refused with "not proposed; a later approval is an --amendment", and the --amendment was refused with "has no approval to amend". Every row was still proposed. What should happen: the change-set procedure says one explicit reply approves the set, and that a stopped chain resumes from the record alone; the first refusal itself points to --amendment as the way on. Neither holds, so the only way on is to abandon the record and start again. Why a code bug: this code sits in no adopted area, so its own account (the procedure and the refusal's own hint) stands in for an AC, and the code breaks it. It is not a spec gap: for code no area covers, a gap is never a reason to write a requirement.
Diagnosis: Reproduced by a probe in a scratch clone at 54e28a1 (`uv run --directory prd-toolkit python <TMP>/probe.py <TMP>/repo/prd-toolkit/tests`): `changeset new` with three members, `changeset stop <record> reports 'lint blocked by a pack gap'` (exit 0), then `changeset approve <record> --reply approved` printed `refused: CS-001 is stopped: reports: lint blocked by a pack gap, not proposed; a later approval is an --amendment` (exit 1) and `changeset approve <record> --reply approved --amendment` printed `refused: CS-001 has no approval to amend` (exit 1); the record kept `Status: stopped: …`, no Approval line, every row `proposed`. Expected: the first approval accepted, Status and every row `approved`. Root cause: `approve()` (prd-toolkit/scripts/prdlint/changeset.py:401-404) takes a first approval only when `cs.status == "proposed"` and an amendment only when `cs.approvals` is not empty, and `stop()` (changeset.py:413-421) sets Status to `stopped: …` whatever the record's approvals, so a record stopped before its first approval matches neither branch. Its account: running-a-change-set.md step 3 (`One explicit reply approves the set.`), step 5 (`A new session resumes from the record alone`), and the refusal's own hint, which names an `--amendment` that the next branch refuses. The faulty code is outside every adopted Boundary (area links, not started).
Resolution: fixed in 31dbcd2c279b24d5a9c1fc1b126c29ada5ee84d3, red run prd-toolkit/tests/test_changeset.py::test_stop_then_first_approval [unit]
Recurrence of: -

### E-082 changeset set takes a State with no Approval line once Status is stopped
Detected: 2026-11-24, user report (/prd-toolkit:prd-error)
Classification: code bug
Confirmed: 2026-11-24, "Confirm the class (form)"
Evidence: User report (code reading, found with the approve refusal): set_fields() refuses a State only while Status is the text `proposed`.
  So on a record stopped before its first approval, `changeset set <record> <prd> state=approved`, or `state=built` for a row with no Waits for, is said to be accepted with no Approval line.
Explanation: What was run: a probe made a three-member change set, stopped it before anyone approved it, then set the first member's State to approved and then to built. What it printed: both were accepted. The record ended with that member built, Status running, and no Approval line at all. What should happen: the change-set procedure says one explicit reply approves the set and that with no one to ask nothing is approved; only the approval command moves a row out of proposed, and the same set is refused with "not approved yet" before the stop. Why a code bug: this code sits in no adopted area, so its own account stands in for an AC, and the code breaks it: a stop is not an approval. It is not a spec gap, for the same reason as E-081.
Diagnosis: Reproduced by a probe in a scratch clone at 54e28a1 (`uv run --directory prd-toolkit python <TMP>/probe.py <TMP>/repo/prd-toolkit/tests`): `changeset new` with three members, `changeset stop <record> reports 'lint blocked by a pack gap'` (exit 0), then `changeset set <record> transform state=approved` (exit 0) and `changeset set <record> transform state=built` (exit 0); the record read `Status: running`, row transform `built`, no Approval line. Expected: both refused with `refused: CS-001 is not approved yet`, the record unchanged. Root cause: `set_fields()` (prd-toolkit/scripts/prdlint/changeset.py:375) refuses a State only when `cs.status == "proposed"`; after `stop()` Status reads `stopped: …`, so the check passes with `cs.approvals` empty, and the row's own transform has no Waits for. Its account: running-a-change-set.md step 3 (`One explicit reply approves the set.` and `with no one to ask, nothing is approved and every member stays In review`), the docstring of `approve()` (`every proposed row and Status become approved`), and the refusal `is not approved yet` the same command gives before the stop. The faulty code is outside every adopted Boundary (area links, not started).
Resolution: fixed in 2082434ca9a2c2f633d4843bbc0d2a29f53a2927, red run prd-toolkit/tests/test_changeset.py::test_stop_then_set_state_without_approval_is_refused [unit]
Recurrence of: -

### E-083 Every eval case on the link_repo scaffold fails in claude plugin eval with scaffold failed (exit null)
Detected: 2026-11-24, eval runs (claude plugin eval)
Classification: code bug
Confirmed: 2026-11-24, "Confirm the class (form)"
Evidence: claude plugin eval (Claude Code 2.1.331), --scaffold --runs 1, cases on evals/scaffolds/link_repo.py:
    change-set-stopped-before-approval run 1/1 [with]: score 0.00  $0.00  error: scaffold failed (exit null):
    change-set-stopped-before-approval run 1/1 [without]: score 0.00  $0.00  error: scaffold failed (exit null):
    coordinating-resume-trigger  0.00  0%  1  $0.00  scaffold failed (exit null):
  The same runner ran error-confirm-before-fix (scaffold error_repo.py) at 1.00.
  Outside the runner the same scaffold.sh exits 0; it took 153 to 170 s while other test suites loaded the machine.
Explanation: What was run: four tiny eval cases whose scaffold only sleeps (60, 150, 240 and 330 s), one that logs a tick every 5 s, and the link_repo scaffold with each of its commands timed, all in claude plugin eval. What it printed: the 60 s case passed; the 150, 240 and 330 s cases failed with scaffold failed (exit null); the ticker's last tick was 115 s; the timed link_repo build took 34 s on a quiet machine and passed, and the same build took 150 to 250 s while other test suites ran, where every link_repo case had failed. So the runner stops any scaffold at about 120 s, and the link_repo build is near that limit under load. About 22 of its commits each run the installed prd hooks, which only check and write nothing. What should happen: the scaffold's own account is to build the start repos for these evals, so it has to build inside the runner the evals use. Why a code bug: the scaffold spends time it does not need (hook checks on its own commits, which its tests repeat with lint and trace), so the fix is in the scaffold. The nearest other class is environment, since the 120 s limit is the runner's; but that limit is not ours to change, and the build still fails under load. Do you want this fixed in the scaffold (a code bug), or treated as the runner's limit only (environment, with a report to Claude Code)? I propose both: the scaffold fix as this entry, and the report as a separate step.
Diagnosis: Runs in claude plugin eval (Claude Code 2.1.331, `--scaffold --runs 1 --ablation none`): sleep probes printed `probe-sleep-60 … 1.00`, `probe-sleep-150 … scaffold failed (exit null)`, the same for 240 and 330; a ticker scaffold logged its last line `tick 115` (one line every 5 s, so the kill came between 115 and 120 s). Expected: a scaffold runs to its end. A timed copy of the cs-stopped scaffold (subprocess.run wrapped, each call logged as it ends) printed `end 34.3s` inside the sandbox with load average about 3 and passed; outside the runner the same scaffold.sh took 153 to 170 s while other suites loaded the machine, and in a kept sandbox of a failed run the client's last commit (`Update the CLAUDE.md block`) was HEAD when it was killed. Root cause: evals/scaffolds/link_repo.py (with deploy_repo.py) builds two repositories with about 22 `legacy.commit` calls made after `prd_hooks.py install`, so each runs the pre-commit and commit-msg hooks (`.prd-toolkit/prd git-hook`, a `uv run` and a lint or trace, 1.3 to 2 s quiet, more under load), plus `uv run --script` per tool call; the hooks write nothing (prdlint/githook.py only checks), and tests/test_link_repo.py already runs lint and trace on every state. Its account: link_repo.py's docstring (`Build the start repos for the coordinating-prds (0.7) baselines, evals and proof`) and the eight cases whose scaffold.sh calls it. The faulty code is outside every adopted Boundary (eval-scaffolds covers only evals/scaffolds/install_files.py).
Resolution: fixed in abc4f811604bde1c6f721e17f1cdac82d3bcf983, red run prd-toolkit/tests/test_link_repo.py::test_the_scaffold_commits_run_no_hook_and_leave_the_hooks_installed [unit]
Recurrence of: -

### E-084 schema-refs reads a backticked file name like `actions.parquet` as table.column
Detected: 2026-11-25, user report (/prd-toolkit:prd-error), GitHub issue #65
Classification: invalid requirement
Confirmed: 2026-11-25, "Confirm the class (form)"
Touches: FR-183
URL: https://github.com/PRDAnvil/prd-toolkit/issues/65
Evidence: GitHub issue PRDAnvil/prd-toolkit#65, found with prd-toolkit 0.8.16 on the SQLAnvil engine PRD (docs/prd/sqlanvil 2.1.0):
  Once a PRD has contracts/schema.sql, schema-refs reads any backticked <word>.<word> span as table.column.
  It skips a span whose second part is a file extension, but _FILE_EXTENSIONS in scripts/prdlint/rules/contracts.py
  is a fixed set (csv, tsv, sql, yaml, yml, json, md, txt, lkml) that leaves out common data-file formats.
  features/artifacts.md:18: schema-refs: `actions.parquet`: table actions has no column parquet
  features/artifacts.md:139: schema-refs: `dependencies.parquet`: table dependencies has no column parquet
  prd.md:66: schema-refs: `columns.parquet`: table columns has no column parquet
  Repro: schema.sql has CREATE TABLE actions (...); a prose line holds `actions.parquet`; prd lint exits 1.
  Suggested: add parquet, avro, orc, ndjson, jsonl, xml, xlsx, gz, zip, html, log, toml, ini, py, ts, js, or let a PRD extend the list.
Explanation: I built a small PRD whose schema declares a table named orders, wrote a line citing `orders.parquet`, `orders.jsonl` and `orders.csv`, and ran the lint. It flagged the first two as missing columns (exit 1) and let `orders.csv` through. That is exactly what the requirement says: it names nine file extensions to skip (csv, tsv, sql, yaml, yml, json, md, txt, lkml) and checks everything else as a column. So the code is right by the PRD; the list in the PRD is too short, and any PRD that names data files like parquet or jsonl trips over it. That makes it an invalid requirement (the PRD is wrong) rather than a code bug (the code disobeying a correct PRD) or not a defect (both right). Do you want the fixed list made longer (the issue suggests parquet, avro, orc, ndjson, jsonl, xml, xlsx, gz, zip, html, log, toml, ini, py, ts, js), or do you want a PRD to be able to add its own extensions? The first is a small change to the list; the second adds a new setting.
Diagnosis: Probe in a scratch clone at e66be0d: the lint-cli/orders fixture with line 17 of features/import.md replaced by a Traces line citing `orders.parquet`, `orders.jsonl` and `orders.csv`, run as `.prd-toolkit/prd lint docs/prd/orders`. Expected (issue #65): no schema-refs finding for a file name. Printed: `exit 1`, `docs/prd/orders/features/import.md:17: schema-refs: `orders.parquet`: table orders has no column parquet` and the same line for `orders.jsonl`; `orders.csv` passed. Root cause: `_FILE_EXTENSIONS` in prd-toolkit/scripts/prdlint/rules/contracts.py:571 holds exactly the nine names AC-183.1 lists. AC-183.1: “nor one of `csv`, `tsv`, `sql`, `yaml`, `yml`, `json`, `md`, `txt` and `lkml`, the lint command shall report `schema-refs`”. The code matches the AC; the AC's list is too short.
Resolution: T-183.4 [integration], PRD 11.0.0, fixed in 17e502e
Recurrence of: -

### E-085 test_the_checker_flags_reused_quotes fails: reused_quotes finds no reused quote in a nested f-string on Python 3.11.15
Detected: 2026-11-25, build lint-contracts FR-183 --fixes E-084
Classification: code bug
Confirmed: 2026-11-25, "Confirm the class (form)"
Evidence: Step 7 full run of the unit level, `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd`, on fix/e084-schema-refs-file-extensions at b6f4463:
  FAILED tests/test_py311_syntax.py::test_the_checker_flags_reused_quotes - ass...
  >       assert reused_quotes('x = f"a {d["k"]} b"\n') == [1]
  E       assert [] == [1]
  tests/test_py311_syntax.py:42: AssertionError
  [gw0] darwin -- Python 3.11.15 /Users/ivan/projects-ivan/prdanvil/prd-toolkit/prd-toolkit/.venv/bin/python
  1 failed, 4049 passed, 1 skipped in 291.00s (0:04:51)
  The test cites no T-id. The builder of round 1 reported the same failure on the unit harness before its change (base 1271c17).
Explanation: I ran the failing test file on its own, and checked which Python the test environment uses. It is Python 3.11.15, and the run failed the same way: the self-check of the quote checker expects it to flag a nested f-string that reuses its own quote, and the checker returned nothing. The checker is written to do nothing on 3.11 (it needs a tokenizer feature that only exists from 3.12), so its self-check can only pass on 3.12 or later. The PRD says the toolkit runs on "Python 3.11 or later", so 3.11 is a supported environment and every test should pass on it. The test is what is wrong, not the scripts it checks, and not the environment: on 3.11 such a line is already a syntax error, which the other test in the file catches. That makes it a code bug in code no PRD area covers, fixed by correcting the test so it checks the right guard on each Python version. It has nothing to do with E-084.
Diagnosis: Run 1 (the build's step 7): `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd` printed `FAILED tests/test_py311_syntax.py::test_the_checker_flags_reused_quotes` (`assert [] == [1]`, line 42), `1 failed, 4049 passed`. Run 2: `uv run --directory prd-toolkit pytest -q -n auto tests/test_py311_syntax.py` printed the same failure, `1 failed, 77 passed`. Probe: `uv run --directory prd-toolkit python -c "import sys, tokenize; print(sys.version.split()[0], hasattr(tokenize, 'FSTRING_START'))"` printed `3.11.15 False`. Root cause: `reused_quotes` in prd-toolkit/tests/test_py311_syntax.py returns `[]` when `tokenize.FSTRING_START` is absent (Python 3.11), so `test_the_checker_flags_reused_quotes` asserting `== [1]` holds only on 3.12+; on 3.11 the same source fails `ast.parse(..., feature_version=(3, 11))`, which `test_parses_as_python_311` checks. The faulty code is the test, outside every adopted Boundary of adoption.md. Account: the file's docstring, “The scripts declare requires-python >= 3.11: none may use syntax that only parses on 3.12 or later.”, and prd.md §1: “Language: Python 3.11 or later.”
Resolution: fixed in 1b678329f699b70f111690fb6bbec1b2aac4e2cc, red run prd-toolkit/tests/test_py311_syntax.py::test_the_checker_flags_reused_quotes [unit]
Recurrence of: -

### E-086 lint-contracts and lint-ids tests capture the lint output in text mode, against the testing.md Assertions slot
Detected: 2026-11-25, user report (/prd-toolkit:prd-error), PRDAnvil/prd-toolkit#68
Classification: code bug
Confirmed: 2026-11-25, "Confirm the class (form)"
URL: https://github.com/PRDAnvil/prd-toolkit/issues/68
Evidence: Reported in PRDAnvil/prd-toolkit#68 (user report via /prd-toolkit:prd-error):
  run_lint in prd-toolkit/tests/prd/lint_contracts_support.py calls subprocess.run with
  capture_output=True, text=True, encoding="utf-8", errors="replace".
  run_lint in prd-toolkit/tests/prd/lint_ids_support.py calls subprocess.run with
  capture_output=True, encoding="utf-8", errors="replace" (encoding alone selects text mode).
  The lint-contracts tests (12 files, 85 calls) and the lint-ids tests (2 files, 62 calls) use them.
  testing.md Harness, Assertions: "a test captures a command's stdout and stderr as bytes, never in
  text mode (whose newline translation turns a \r into \n), and compares them with the expected text
  encoded as UTF-8".
  Only the T-183 tests (test_lint_contracts_schema_refs.py) use the bytes-mode run_lint_bytes.
Explanation: I ran a probe in a scratch copy of the repository. It swapped the lint for a stand-in that writes a line ending in a carriage return and newline, a byte that is not valid UTF-8, and a lone carriage return on stderr, and handed that output to the two helpers that the lint-contracts and lint-ids tests use to run the lint. Both helpers gave the tests a changed copy: each carriage return became a newline, and the invalid byte became a replacement character. The bytes helper that the four schema-refs tests use gave back the output unchanged. The testing rules of this PRD say a test captures a command's output as bytes, never in text mode, and compares it with the expected text encoded as UTF-8, so a test sees exactly what the command wrote. This is a code bug, not an invalid requirement: the testing rule is right and the two helpers break it. The helpers are test code that no adopted area covers, so the fix goes through the route for such code: a failing unit test first, then the fix in the two helpers alone. Every test file that cites a T-id stays as it is, so no black-box test is edited.
Diagnosis: Root cause: `run_lint` in prd-toolkit/tests/prd/lint_contracts_support.py:143 passes `text=True, encoding="utf-8", errors="replace"` to subprocess.run, and `run_lint` in prd-toolkit/tests/prd/lint_ids_support.py:119 passes `encoding="utf-8", errors="replace"`, which selects text mode on its own. Text mode translates `\r\n` and `\r` to `\n`, and `errors="replace"` turns an invalid byte into U+FFFD. The account they break, testing.md Harness, Assertions: `a test captures a command's stdout and stderr as bytes, never in text mode (whose newline translation turns a \r into \n), and compares them with the expected text encoded as UTF-8`. Run: `uv run --project prd-toolkit python -I probe.py`, from a scratch clone at aae7708, with each helper's lint script path pointed at a stub that writes stdout `x.md:1: rule: a\r\nb\xff\n` and stderr `\r`. The account expects the helper to give a test those bytes. It printed `lint_contracts_support.run_lint: stdout 'x.md:1: rule: a\nb�\n' stderr '\n'` and `lint_ids_support.run_lint: stdout 'x.md:1: rule: a\nb�\n' stderr '\n'`, while `lint_contracts_support.run_lint_bytes` printed `stdout b'x.md:1: rule: a\r\nb\xff\n' stderr b'\r'`. Callers: the lint-contracts tests (12 files, 85 calls) and the lint-ids tests (2 files, 62 calls); their whole-output checks today are empty-stderr checks, the rest line and substring checks. The helpers lie outside every adopted Boundary of adoption.md and cite no T-id.
Resolution: fixed in 7cfb309a9602f65bea6a0a7a960ca8ac1e867284, red run prd-toolkit/tests/test_lint_support_capture.py [unit]
Recurrence of: -

### E-087 The root README's slash-command list leaves out /prd-toolkit:prd-practices and /prd-toolkit:prd-pack
Detected: 2026-11-25, adoption extract of release (README.md:13 @05ae956)
Classification: code bug
Confirmed: 2026-11-26, "confirm all six as code bugs"
Touches: FR-271, FR-273
Explanation: I ran the release test for the root README's slash-command list with its expected-failure mark turned off. It failed: the list names ten commands, and the plugin ships twelve; prd-practices and prd-pack are missing. The PRD says the list shall name exactly the commands the plugin ships. That makes it a code bug: the PRD is right and the README is wrong. It is not an invalid requirement, since at adoption you said the list should include all of them.
Diagnosis: Run at 3e9bd32: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_release_readmes.py tests/prd/test_release_prd_function.py --runxfail --tb=line -rf`. T-271.3 (`test_root_readme_slash_commands`) expected the line's names to equal the stems of `prd-toolkit/commands/*.md` and printed `only on the line: []; only in commands/: ['prd-pack', 'prd-practices']`. AC-271.3: `The set of names <name> that the **Slash commands** line of README.md holds as /prd-toolkit:<name> shall equal the set of stems of the files prd-toolkit/commands/*.md`. Root cause: `README.md:13` lists ten commands and was not updated when 0.8.11 and 0.8.12 added `prd-practices` and `prd-pack`.
Resolution: T-271.3 [integration], PRD 13.1.0, fixed in 07792ba
Recurrence of: -

### E-088 The plugin README says the skills still print bare /prd-change, which 0.8.7 removed
Detected: 2026-11-25, adoption extract of release (prd-toolkit/README.md:1738 @05ae956)
Classification: code bug
Confirmed: 2026-11-26, "confirm all six as code bugs"
Touches: FR-273
Explanation: I ran the release test for the plugin README's Tests and evals section with its expected-failure mark turned off. It failed: the section still says the skills print the bare /prd-change command. That stopped being true in 0.8.7, when every skill began printing the namespaced /prd-toolkit:prd-change. The PRD says the section shall not say that. It is a code bug, the PRD right and the README wrong, not an invalid requirement: at adoption you said that behaviour is gone and the README should not describe it.
Diagnosis: Run at 3e9bd32: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_release_readmes.py tests/prd/test_release_prd_function.py --runxfail --tb=line -rf`. T-273.6 (`test_tests_and_evals_no_bare_command`) expected the section not to hold `that the skills' text still prints` and printed `AssertionError: that the skills' text still prints`. AC-273.6: `The ## Tests and evals section of prd-toolkit/README.md shall not say that the skills' text prints a bare /prd-<name> command`. Root cause: `prd-toolkit/README.md:1751` to 1753 still says `The bare /prd-change that the skills' text still prints gets "Unknown command"`; 0.8.7 namespaced every command the skills print and kept the sentence.
Resolution: T-273.6 [integration], PRD 13.1.0, fixed in 07792ba
Recurrence of: -

### E-089 The plugin README's update instruction leaves out the marketplace refresh that every Upgrade note gives
Detected: 2026-11-25, adoption extract of release (prd-toolkit/README.md:40 @05ae956)
Classification: code bug
Confirmed: 2026-11-26, "confirm all six as code bugs"
Touches: FR-273
Explanation: I ran the release test for the plugin README's update instructions with its expected-failure mark turned off. It failed: the README says to run claude plugin update and then /reload-plugins, and never says to refresh the marketplace first, so an update can find no newer version. The PRD says the README shall give three steps in order, starting with claude plugin marketplace update prdanvil, as every changelog Upgrade note does. Code bug: the PRD is right and the README is wrong; at adoption you said the marketplace refresh comes first.
Diagnosis: Run at 3e9bd32: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_release_readmes.py tests/prd/test_release_prd_function.py --runxfail --tb=line -rf`. T-273.5 (`test_update_order`) expected `claude plugin marketplace update prdanvil` in the Install section and printed `AssertionError: 'claude plugin marketplace update prdanvil' not found after offset 0`. AC-273.5: `The ## Install section of prd-toolkit/README.md shall give the update of an installed copy as claude plugin marketplace update prdanvil, then claude plugin update prd-toolkit@prdanvil, then /reload-plugins, in that order`. Root cause: `prd-toolkit/README.md:40` to 41 give only `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`; the changelog Upgrade notes (such as line 1405) give all three.
Resolution: T-273.5 [integration], PRD 13.1.0, fixed in 07792ba
Recurrence of: -

### E-090 The root README's prd function runs a scripts/prd in the working directory when no plugin is installed
Detected: 2026-11-25, confirmation of FR-274
Classification: code bug
Confirmed: 2026-11-26, "confirm all six as code bugs"
Touches: FR-274
Explanation: I ran the release test that runs the README's prd shell function with no prd-toolkit installed, with its expected-failure mark turned off. It printed the ls command's own No such file or directory error, then ran a scripts/prd it found in the current folder, and returned 0. The PRD says that in this case the function shall print prd-toolkit is not installed, run nothing and return 127. Code bug: the PRD is right and the function is wrong. You corrected FR-274 to say this at adoption.
Diagnosis: Run at 3e9bd32: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_release_readmes.py tests/prd/test_release_prd_function.py --runxfail --tb=line -rf`. T-274.3 (`test_not_installed`) expected exit 127 with `prd-toolkit is not installed` on stderr and printed exit 0, stdout `wrong-launcher` and stderr `ls: .../emptyhome/.claude/plugins/cache/prdanvil/prd-toolkit/*/: No such file or directory`. AC-274.3: `If no folder matches $HOME/.claude/plugins/cache/prdanvil/prd-toolkit/*/ when the function would run the plugin's launcher (AC-274.2), the function shall print prd-toolkit is not installed on stderr, run nothing, and return 127`. Root cause: `README.md:45` runs `sh "$(ls -d ~/.claude/plugins/cache/prdanvil/prd-toolkit/*/ | sort -V | tail -1)scripts/prd" "$@"`; when ls matches nothing the substitution is empty, so it runs `sh scripts/prd` relative to the working directory.
Resolution: T-274.3 [integration], PRD 13.1.0, fixed in 07792ba
Recurrence of: -

### E-091 The root README's Features list does not say it names a selection of the skills
Detected: 2026-11-25, characterization of release (T-273.7)
Classification: code bug
Confirmed: 2026-11-26, "confirm all six as code bugs"
Touches: FR-273
Explanation: I ran the release test for the root README's Features list with its expected-failure mark turned off. It failed: the list names some of the skills and does not say it is a selection, so a reader takes it for all of them. The PRD says the list shall say it names the main skills, and that the plugin README lists all eleven, with a link to it. Code bug: the PRD is right and the README is wrong. That wording is your answer to Q-06 at adoption.
Diagnosis: Run at 3e9bd32: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_release_readmes.py tests/prd/test_release_prd_function.py --runxfail --tb=line -rf`. T-273.7 (`test_features_list`) expected the flattened Features list to hold `the main skills` and printed `AssertionError: the Features list does not hold 'the main skills'`. AC-273.7: `The **Features:** list of README.md shall say that it names the main skills and that the plugin README lists all eleven, with a link to ./prd-toolkit/README.md`. Root cause: `README.md:5` opens the list with `**Features:**` and no sentence saying it is a selection of the eleven skills, and gives no link to the plugin README there.
Resolution: T-273.7 [integration], PRD 13.1.0, fixed in 07792ba
Recurrence of: -

### E-092 The plugin README links each design spec under docs/superpowers/specs/ instead of the folder
Detected: 2026-11-25, characterization of release (T-276.2)
Classification: code bug
Confirmed: 2026-11-26, "confirm all six as code bugs"
Touches: FR-276
Explanation: I ran the release test for the plugin README's links to the design specs with its expected-failure mark turned off. It failed: the README links each release's spec, 28 links in all, where the PRD says it shall hold exactly one, to the specs folder. Code bug: the PRD is right and the README is wrong; the single folder link is your answer to Q-05 at adoption. The fix also changes the unit tests that pin those spec links, which the build does.
Diagnosis: Run at 3e9bd32: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_release_readmes.py tests/prd/test_release_prd_function.py --runxfail --tb=line -rf`. T-276.2 (`test_one_spec_link`) expected the link targets that start with `../docs/superpowers/specs/` to be `[../docs/superpowers/specs/]` and printed `assert [../docs/superpowers/specs/2026-10-29-prd-toolkit-design.md, ...] == [../docs/superpowers/specs/]` with `Left contains 27 more items`. AC-276.2: `The plugin README prd-toolkit/README.md shall hold exactly one Markdown link whose target starts with ../docs/superpowers/specs/, and that target shall be ../docs/superpowers/specs/`. Root cause: `prd-toolkit/README.md:11` to 31 and the changelog entries link each release's spec file (`grep -c` of the prefix prints 28); unit tests such as `tests/test_release_0_5.py` pin some of those links.
Resolution: T-276.2 [integration], PRD 13.1.0, fixed in 07792ba
Recurrence of: -

### E-093 a PRD change that adds an enforced section 5 standards row leaves the generated CI workflow stale, and neither the change procedure nor `prd change approve` catches it before the push
Detected: 2026-11-26, user report (/prd-toolkit:prd-error), PR #80
Classification: spec gap
Confirmed: 2026-11-26, "Confirm the class (form)"
Touches: FR-262, FR-263
URL: https://github.com/PRDAnvil/prd-toolkit/actions/runs/45910377365/job/140217032152
Evidence: Owner's report (2026-11-26), after PR #80 (PRD 13.3.0, release-area practices):
  The change added an enforced section 5 standards row for .claude-plugin/marketplace.json.
  prd change approve committed c4b77f9 (docs(prd): approve prd-toolkit 13.3.0) with lint exit 0.
  On PR #80, CI job prd-lint failed on its second step, sh .prd-toolkit/prd hooks check --ci docs/prd/prd-toolkit:
  stale: .github/workflows/prd-toolkit.yml: re-run prd_hooks.py ci --github --force
  Regenerating added a standards-2 job (plugin validate . on .claude-plugin/marketplace.json); fixed by b76a27b.
  changing-prds step 5's close says a generated CI include is stale when the change touched testing.md or operations.md;
  it does not name a section 5 standards row, and neither lint nor approve reported the stale workflow before the push.
Explanation: In a copy of the repository at the approval commit of PRD 13.3.0, the PRD lint CI runs passed, but the CI staleness check CI also runs said the generated workflow was stale and failed. On that same tree the approval command had approved the change without a word, and the change procedure only says to regenerate the workflow when testing.md or operations.md changed, so the stale file reached the pull request and failed its merge gate. The PRD lists every check the approval makes (the reply, the review, lint, the dry-run record, the pending row and CLAUDE.md) and says nothing about the generated CI files, so the code does what the PRD says and the PRD is silent: a spec gap, not a code bug. The question for you: do you want the approval to bring the generated CI files up to date itself and commit them with the approval, as it already does for the CLAUDE.md block, or to refuse while they are stale and name the command that regenerates them, or only the change skill told to run the staleness check before asking for approval? The first two are a PRD change to FR-262 or FR-263, built in the change area; the third changes only the skill text, which no adopted area covers.
Diagnosis: Probe in a scratch clone at c4b77f9 (docs(prd): approve prd-toolkit 13.3.0): `sh .prd-toolkit/prd lint --ci docs/prd/prd-toolkit` printed nothing, `lint-exit=0`; `sh .prd-toolkit/prd hooks check --ci docs/prd/prd-toolkit` printed `stale: .github/workflows/prd-toolkit.yml: re-run prd_hooks.py ci --github --force`, `check-ci-exit=1`. On the same tree, uncommitted, `prd change approve docs/prd/prd-toolkit --reply Approved --dry-run no dry run (wording only)` printed `approved prd-toolkit 13.3.0 c4b77f9` and exit 0. Root cause: the 13.3.0 change added the enforced section 5 row for `.claude-plugin/marketplace.json`, and `prd_hooks.py ci` writes one standards-N job per enforced row, so the workflow needed a standards-2 job (b76a27b added it). FR-262 lists the checks approve makes, AC-262.1 to AC-262.7 and AC-262.8 `shall run the checks of AC-262.1 to AC-262.7 in that order before it writes anything`; none names the generated CI files, and FR-263 AC-263.3 stages the PRD folder, the README, CLAUDE.md and vendored packs but no CI file. Sections searched and silent on CI staleness at approval: FR-262, FR-263 (change area). The skill text changing-prds SKILL.md step 5 says `when the change touched testing.md or operations.md, a generated CI include is stale`, which leaves out a section 5 standards row; that file is in the skills area (not started), outside every adopted Boundary.
Resolution: T-263.8 [integration], PRD 14.0.0, fixed in bbdec9e
Recurrence of: -

### E-094 test_diagrams.py::test_a_raw_quote_in_a_label_never_stops_the_publish_for_real failed once under the parallel unit run and passed alone
Detected: 2026-11-26, unit harness run, 0.8.23 release tree (fix/ci-stale-standards)
Classification: unclassified
Evidence: Seen 2026-11-27 on branch fix/ci-stale-standards (the 0.8.23 release tree), by the unit Levels harness command:
  uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd
    run 1 (before the 0.8.23 edits, at 77c0997): 4123 passed, 1 skipped
    run 2 (with the 0.8.23 edits): FAILED tests/test_diagrams.py::test_a_raw_quote_in_a_label_never_stops_the_publish_for_real
        1 failed, 4126 passed, 1 skipped in 302.37s
  The same test alone, right after run 2:
  uv run --directory prd-toolkit pytest -q "tests/test_diagrams.py::test_a_raw_quote_in_a_label_never_stops_the_publish_for_real"
    1 passed in 2.13s
  The failure's own traceback was not kept (the run's output was cut to its last lines).
Diagnosis: not reproduced: on HEAD 7f38c23 (0.8.24), `uv run --directory prd-toolkit pytest -q -n auto tests/test_diagrams.py` printed `106 passed in 16.79s`, and the full unit Levels command `uv run --directory prd-toolkit pytest -q -n auto tests --ignore tests/prd` printed `4132 passed, 1 skipped in 290.34s`, the test passing in both; the one failure (run 2 of 2026-11-27) kept no traceback, so which of its two assertions failed (the publish exit and stderr, or the count of drawn diagrams) is unknown; what would reproduce it is the failure output of the next run where it fails, kept whole (the run written to a file, never cut to its tail)
Resolution: -
Recurrence of: -

### E-095 The prd-status command says exit 2 means a wrong path with nothing printed, but prd status also exits 2 with output and for other causes
Detected: 2026-11-27, adoption extract of commands (prd-toolkit/commands/prd-status.md:37 @2b082aa)
Classification: code bug
Touches: FR-283
Explanation: I ran prd status two ways. With --json on a wrong path it exited 2 and still printed a JSON error document; on an unmigrated PRD at the right path it exited 2 with a message to move the adoption map. The PRD says the prd-status command should tell the agent, on exit 2, to read what was printed and act on its cause: a wrong path, an unmigrated PRD or an internal error. The command instead says nothing was printed and the path is wrong, so an agent keeps "fixing" a correct path. This is a code bug, not an invalid requirement: you confirmed the intended sentence at adoption, and the command file is what falls short of it.
Diagnosis: AC-283.4 says: "When the prd-status command runs, its instructions shall tell the agent, on `prd-status-exit=2`, to read what the script printed and act on its cause: a wrong path (fix the path), an unmigrated PRD or an internal error; and shall not say that nothing was printed (E-095)." Step 4 of prd-toolkit/commands/prd-status.md says `On prd-status-exit=2, the call was wrong and nothing printed: fix the path.` Runs on HEAD ef6ef52: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_commands_status.py` reported T-283.4 XFAIL `known failure seen: flat(STEP(prd-status, 4)) holds the call was wrong and nothing printed: fix the path`. In a scratch clone, `.prd-toolkit/prd status docs/prd/nope --json` printed `{"interface": 1, "kind": "status", "error": "…/docs/prd/nope: no prd.md"}` and exited `2` (expected per AC-283.4: output to read); with adoption.md removed and a table in section 8, `.prd-toolkit/prd status docs/prd/prd-toolkit` printed `prd_status: …/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; …` and exited `2` on the right path. prd_status.py also exits 2 on `internal error` (its catch-all). Root cause: the command file's step 4 sentence; the script is right.
Resolution: open
Recurrence of: -

### E-096 The prd-context command says exit 2 means the arguments were wrong, but prd context also exits 2 for an internal error or an unmigrated PRD
Detected: 2026-11-27, adoption extract of commands (prd-toolkit/commands/prd-context.md:42 @2b082aa)
Classification: code bug
Touches: FR-284
Explanation: I ran prd context on an unmigrated PRD at the right path, with right arguments: it exited 2 with a message to move the adoption map. The PRD says the prd-context command should tell the agent, on exit 2, to read what was printed and act on its cause: wrong arguments, an unmigrated PRD or an internal error. The command instead says nothing was printed and the arguments are wrong, so an agent changes arguments that were never the problem. This is a code bug, not an invalid requirement: you confirmed the intended sentence at adoption, and the command file falls short of it. It is the same fault as E-095, in the sibling command.
Diagnosis: AC-284.5 says: "When the prd-context command runs, its instructions shall tell the agent, on `prd-context-exit=2`, to read what the script printed and act on its cause: wrong arguments (fix them), an unmigrated PRD or an internal error; and shall not say that nothing was printed (E-096)." Step 5 of prd-toolkit/commands/prd-context.md says `On prd-context-exit=2, the call was wrong and nothing printed: fix the arguments.` Runs on HEAD ef6ef52: `uv run --directory prd-toolkit pytest -q -n auto tests/prd/test_commands_context.py` reported T-284.5 XFAIL `known failure seen: flat(STEP(prd-context, 5)) holds the call was wrong and nothing printed: fix the arguments`. In a scratch clone with adoption.md removed and a table in section 8, `.prd-toolkit/prd context docs/prd/prd-toolkit --area commands` printed `prd_context: …/prd.md: section 8: the adoption map moved to adoption.md in prd-toolkit 0.3; …` and exited `2`, its arguments right. prd_context.py also exits 2 on `prd_context: internal error: …` (its catch-all). Root cause: the command file's step 5 sentence; the script is right.
Resolution: open
Recurrence of: -

### E-097 The prd-context and prd-build commands send the agent to the repo pack to find an ID's area, but the repo pack lists no requirement IDs
Detected: 2026-11-27, confirmation of FR-284 (Q-57; prd-toolkit/commands/prd-context.md:32 @2b082aa)
Classification: code bug
Touches: FR-284, FR-288
Explanation: I printed the repo pack, which prd-context and prd-build tell the agent to use to find an ID's area when no area is given: its 93 lines hold no requirement ID at all, so the area cannot be found there. Asking prd context for FR-283 with no area exits 2 with "--req needs --area". A search of the features files for the FR-283 heading found its area, commands, at once. The PRD says both commands should tell the agent to find the area from the features file that holds the ID's heading, or ask, and not name the repo pack. This is a code bug, not an invalid requirement: you chose that sentence when you answered Q-57, and the command files still send the agent to the repo pack.
Diagnosis: AC-284.6 says: "When the prd-context command is given IDs and no area, its instructions shall tell the agent to find each ID's area from the `features/<area>.md` file that holds the ID's `### <ID>` heading, or to ask; and shall not name the repo pack as that source (E-097)." AC-288.7 says the same of prd-build. Step 2 of prd-toolkit/commands/prd-context.md and step 4 of prd-toolkit/commands/prd-build.md say `find the area each ID's block lives in from the repo pack, or ask`. Runs on HEAD ef6ef52: the pytest run of tests/prd/test_commands_context.py and tests/prd/test_commands_build.py reported T-284.6 and T-288.7 XFAIL `known failure seen: … holds find the area each ID's block lives in from the repo pack, or ask`. In a scratch clone, `.prd-toolkit/prd context docs/prd/prd-toolkit` printed 93 lines with `0` matching `(FR|NFR|UJ)-[0-9]` (its Areas line reads `- commands (adopted; Boundary: prd-toolkit/commands/**)`); `.prd-toolkit/prd context docs/prd/prd-toolkit --req FR-283` printed `prd_context: --req needs --area` and exited `2`; `grep -ln "^### FR-283 " docs/prd/prd-toolkit/features/*.md` printed `docs/prd/prd-toolkit/features/commands.md`. Root cause: the sentence in both command files.
Resolution: open, intended: find each ID's area from the `features/<area>.md` file that holds the ID's `### <ID>` heading, or ask
Recurrence of: -
