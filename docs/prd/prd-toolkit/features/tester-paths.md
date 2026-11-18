<!-- Format: references/prd-format.md, "Requirement blocks". -->

# tester-paths: which changed files the build check calls a tester's test

A build round ends with `prd_build_check.py <prd_dir> --diff <base>..<head>`, which fails the round when the
builder changed the PRD folder, the vendored `.prd-toolkit/` copy or a tester's test. It called every changed
file a tester's test whose text cites a T-id of a level other than `unit`, wherever the file was. A file that is
no test and holds such a text for another PRD (an eval scaffold that writes a demo repository's test files)
could then be changed by no build (E-031). `testing.md` says where a tester's test is: under the test roots of
its Layout line, the folders trace reads citations from. This area holds the check to those roots. Its one
module is `prd-toolkit/scripts/prdlint/testerpaths.py`, which says whether a changed path is a tester's test;
the same build makes `diff_findings` in `prd-toolkit/scripts/prdlint/buildcheck.py` (area `build-check`, which
is not adopted) call it, and what the check prints for such a path is stated here. No other file changes.

Words used below. A **changed path** is a path the range's `git diff --name-status -M` names, written from the
repository root with `/` between its parts; a renamed file gives two changed paths, its old one and its new
one. A **test root** is a backticked path of the `Test roots:` list in the Layout line of the PRD's
`testing.md`, as that file stands on disk, less the white space around it and every `/` at its end; when
`testing.md` holds no `Test roots:` text, or its list is empty, the one test root is `tests`. A changed path
**lies under** a test root when it equals the root, or starts with the root followed by `/`. A text **cites** a
T-id when one of its lines holds `@prd`, white space and the T-id (`T-nnn.n`), as trace reads a citation.

### FR-074 The build check calls a changed file a tester's test only under a test root
Status: verified
Source: prd-toolkit/scripts/prdlint/testerpaths.py:1 @e4903d9
Acceptance (EARS):
- AC-074.1 When `prd_build_check.py <prd_dir> --diff <base>..<head>` reads a changed path that is outside the
  PRD folder and outside `.prd-toolkit/`, that lies under a test root, and whose text at `<base>` or at `<head>`
  cites at least one T-id whose test case has a level other than `unit` (a T-id with no test case counts as
  such), it shall print the line `<path> cites <T-ids>, a tester's test: the builder may not edit it` and exit
  1; `<T-ids>` are those T-ids, each once, in the order of their first citation, the text at `<base>` read
  before the text at `<head>`, joined by a comma and a space.
- AC-074.2 If a changed path lies under no test root, the check shall print no `a tester's test` line for it,
  whatever its text cites; when the range gives no other finding, the check prints nothing and exits 0.
Errors: -
Edge cases: a path that only shares a root's first letters (`tests-old/test_old.py` beside the root `tests`) lies under no root → AC-074.2; a file moved out of a test root is reported by its old path and not by its new one, and one moved into a root by its new path → AC-074.1, AC-074.2; a path under a test root whose text cites only T-ids of level `unit` gets no line, as before; a folder a dry run left under a test root lies under that root → AC-074.1; the lines for the PRD folder and for `.prd-toolkit/`, and `--sources`, `--results` and `--stale`, are unchanged; the check reads `testing.md` from the files on disk, never from `<base>` or `<head>`
Tests: T-074.1 [integration], T-074.2 [integration], T-074.3 [integration], T-074.4 [integration], T-074.5 [integration]  (test-cases/tester-paths.yaml)
Traces: cli:prd_build_check; E-031
