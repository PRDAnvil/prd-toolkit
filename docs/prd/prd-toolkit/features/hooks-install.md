<!-- Format: references/prd-format.md, "Requirement blocks". -->

# hooks-install: vendoring the toolkit, installing its git hooks, the generated CI, and the prd dispatcher

`prd_hooks.py <action> <prd_dir>` is the hooks command. `install` and `vendor` write the vendored copy `.prd-toolkit/`
at the top of the git checkout. `install` also writes the git hooks, the `.gitignore` lines and the managed blocks.
`check` compares what is installed with the plugin. `uninstall` removes the toolkit's hooks. `ci` writes the merge-gate
CI include. `prd_dispatch.py` runs one toolkit script by its command name, and the `prd` launcher runs it (FR-069).
`requirements.txt` lists the packages the launcher installs for the vendored scripts.

Words used below:
- The **top** is the folder `git rev-parse --show-toplevel` prints.
- `<prd>` is the PRD folder's path relative to the top.
- `<hooks>` is the hooks folder as `git rev-parse --git-path hooks` prints it.
- A hook file is **the toolkit's own** when its second line starts with `# prd-toolkit hook`; any other file is the
  user's own.
- **From the plugin** means the script runs from a `scripts/` folder whose parent holds `.claude-plugin/plugin.json`.
  **From the vendored copy** means it runs from `.prd-toolkit/`.
- **The hook line** for a hook is the one sh line FR-102 prints and FR-103 describes.
- What install writes where `core.hooksPath` is set belongs to FR-070 (area hook-shims). What the shim templates do
  when git runs them belongs to FR-096 (area trace). The command of a `standards-<n>` job belongs to FR-068 (area
  standards-run).

### FR-097 Refuse a malformed hooks command line
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prd_hooks.py:21 @07f77b1
Acceptance (EARS):
- AC-097.1 If `prd_hooks.py ci` is given both `--gitlab` and `--github`, or neither, the hooks command shall print
  `prd_hooks: ci needs exactly one of --gitlab or --github` on stderr, write no file and exit 2.
- AC-097.2 If `--gitlab`, `--github` or `--force` is given with an action other than `ci`, the hooks command shall
  print `prd_hooks: --gitlab, --github and --force belong to ci` on stderr, write no file and exit 2.
- AC-097.3 If `--ci` is given with an action other than `check`, the hooks command shall print
  `prd_hooks: --ci belongs to check` on stderr, write no file and exit 2.
- AC-097.4 If the action is not one of `install`, `check`, `uninstall`, `ci` and `vendor`, or no PRD folder is given,
  the hooks command shall print its usage line and a `prd_hooks.py: error:` line on stderr and exit 2. Given `-h` or
  `--help`, it shall print its help on stdout and exit 0.
- AC-097.5 If the PRD folder holds no file `prd.md`, the hooks command shall print
  `prd_hooks: <folder>: no prd.md` on stderr, `<folder>` the absolute path of the folder, write no file and exit 2.
Errors: -
Edge cases: the flag checks run before the folder is read, so `ci` with no forge on a folder with no `prd.md` prints the forge line → AC-097.1; FR-010's missing-package message and exit 2 come before any of these (area lint-cli); an unexpected failure prints `prd_hooks: internal error: <type>: <message>` and exits 2 (no test: no black-box input triggers it); stdout and stderr are UTF-8 whatever the locale when the command runs as a script
Tests: T-097.1 [integration], T-097.2 [integration], T-097.3 [integration], T-097.4 [integration], T-097.5 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-098 Install writes the vendored copy of the toolkit's files
Status: approved
Source: prd-toolkit/scripts/prdlint/hooks.py:212 @07f77b1
  prd-toolkit/scripts/prdlint/hooks.py:73 @07f77b1
Acceptance (EARS):
- AC-098.1 When `prd_hooks.py install <prd_dir>` runs from the plugin in a git checkout that holds the PRD folder,
  the hooks command shall write `.prd-toolkit/` at the top with these files, each byte-identical to the plugin's file
  and with that file's permission bits, in this order (a path below is relative to the plugin's own folder, the one that
  holds `scripts/`, `templates/` and `references/`):
  - from `scripts/`, each at its own name (`.prd-toolkit/prd_lint.py`): `prd_lint.py`, `prd_trace.py`, `prd_status.py`, `prd_context.py`, `prd_build_check.py`,
    `prd_hooks.py`, `prd_git_hook.py`, `prd_deploy.py`, `prd_drift.py`, `prd_block.py`, `prd_error.py`,
    `prd_links.py`, `prd_confirm.py`, `prd_judge.py`, `prd_change.py`, `prd_gates.py`, `prd_dispatch.py`,
    `prd_help.py`, `prd_practices.py`, `prd_pack.py`, `requirements.txt` and `prd`;
  - every file under `scripts/prdlint/` outside a `__pycache__` folder and not ending `.pyc`, at `prdlint/<path>`;
  - `templates/hooks/commit-msg` and `templates/hooks/pre-commit`, at `hooks/`;
  - `templates/claude-block.md`, `templates/readme-prd.md` and `templates/readme-prds.md`, at `templates/`;
  - `templates/confirm/form.html` and `templates/confirm/panel.html`, at `confirm/`;
  - `templates/gates/inbox.html`, at `gates/inbox.html`;
  - every file under `templates/judge/`, a folder that holds no Python file and so no `__pycache__` folder, at `judge/<path>`;
  - each `references/languages/*.yaml`, at `languages/<name>`;
  - `references/help.yaml`, at `help.yaml`;
  - the file `LICENSE` of the plugin's own folder, the one that holds its `scripts/` folder, at `LICENSE`.
- AC-098.2 When install writes `.prd-toolkit/`, the hooks command shall write `.prd-toolkit/VERSION` as the `version`
  of the plugin's `.claude-plugin/plugin.json` followed by a newline, write `.prd-toolkit/.gitignore` as the one line
  `__pycache__/`, and print `vendored the toolkit into .prd-toolkit/ (version <version>)` as its first stdout line.
- AC-098.3 Where the plugin's `plugin.json` has a `homepage` that is a string with text other than white space,
  install shall write `.prd-toolkit/HOMEPAGE` as that string, trimmed, followed by a newline. Where it has none,
  install shall leave no `.prd-toolkit/HOMEPAGE`.
- AC-098.4 When `.prd-toolkit/` already holds a file under `prdlint/`, `hooks/`, `confirm/`, `gates/`, `judge/` or
  `languages/` that AC-098.1 does not write, install shall delete that file, and every folder under those six that
  is empty once the files are deleted, a folder that was empty before the run included.
- AC-098.5 The `.prd-toolkit/requirements.txt` that install writes shall hold exactly the three lines
  `openapi-spec-validator>=0.7`, `pyyaml>=6.0` and `sqlglot>=25`, and install shall write neither `prd_publish.py` nor
  `requirements-publish.txt` into `.prd-toolkit/`.
- AC-098.6 If the PRD folder is not inside a git checkout, install shall write no file (no `.prd-toolkit/`, hook,
  `.gitignore` line or managed block), print `prd_hooks: <folder> is not inside a git checkout` on stderr, `<folder>` the
  absolute path of the PRD folder, and exit 2.
Errors: -
Edge cases: a PRD folder resolved outside the top prints `prd_hooks: <folder> is not inside the repository at <top>` and exits 2 (no test: a folder git resolves always lies under its own top); outside a git checkout install refuses before it writes → AC-098.6; install deletes no file of `.prd-toolkit/` that the plugin no longer ships, and check reports it → AC-108.2
Tests: T-098.1 [integration], T-098.2 [integration], T-098.3 [integration], T-098.4 [integration], T-098.5 [integration], T-098.6 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; cli:prd_launcher; FR-069

### FR-099 Install vendors the PRD's packs and records where each came from
Status: verified
Source: prd-toolkit/scripts/prdlint/hooks.py:107 @07f77b1
  prd-toolkit/scripts/prdlint/hooks.py:125 @07f77b1
  prd-toolkit/scripts/prdlint/hooks.py:229 @07f77b1
Acceptance (EARS):
- AC-099.1 When install runs from the plugin, the hooks command shall write `.prd-toolkit/packs/<name>/` for each pack
  the PRD names (its §1 `Pack:` line and each area's `Target:` pack, one per name) and for `service` whether named or
  not. Each folder shall be a copy of the folder the pack resolves to from the plugin (the toolkit's own
  `packs/<name>/` for source `prd-toolkit`), leaving out `__pycache__` folders and `.pyc` files. Every other entry of
  `.prd-toolkit/packs/` shall be deleted.
- AC-099.2 When install writes the packs, the hooks command shall write `.prd-toolkit/pack-sources.json` as one JSON
  object that maps each vendored pack's name to its source, keys in name order and indented two spaces, followed by a
  newline.
- AC-099.3 If a pack the PRD names cannot be resolved, install shall print
  `prd_hooks: install refused: <reason>` on stderr, write no file (no `.prd-toolkit/`, hook, `.gitignore` line or
  managed block) and exit 2. `<reason>` is the resolver's message,
  `pack <name> <X.Y.Z> (<source>) not found; looked in: <places>`.
- AC-099.4 If the PRD names a version for a pack it cannot resolve, and a place AC-099.3 names holds that pack at
  another version `<have>`, the refusal line shall end with
  `; to move the PRD to <name> <have>, run prd_change.py pack <prd> <name> <have>`.
Errors: -
Edge cases: the order in which places are searched, the text of `<places>`, and which `<have>` is named when several places hold the pack at different versions belong to the packs area; `vendor` refuses the same way under its own name → AC-107.3
Tests: T-099.1 [integration], T-099.2 [integration], T-099.3 [integration], T-099.4 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-100 Install adds the judge record and the review verdict to .gitignore
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:146 @07f77b1
Acceptance (EARS):
- AC-100.1 When install runs from the plugin, it shall append to `.gitignore` at the top each of the lines
  `.prd-judge/` and `.prd-review.json`, in that order, that the file does not already hold as a line with white space
  at its ends removed. When the file's text is not empty and does not end in a newline, install shall write a newline
  first. Install shall create the file when it is absent, and leave it unchanged when it holds both lines.
Errors: -
Edge cases: install from the vendored copy writes no `.gitignore` line → AC-106.1; install writes `.gitignore` back with LF line ends, whatever line ends the file had → AC-100.1
Tests: T-100.1 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-101 Install writes the hook shims where core.hooksPath is not set
Status: approved
Source: prd-toolkit/scripts/prdlint/hooks.py:333 @07f77b1
  prd-toolkit/scripts/prdlint/hooks.py:343 @07f77b1
Acceptance (EARS):
- AC-101.1 When install runs where `core.hooksPath` is not set, for each of `commit-msg` and `pre-commit`, in that
  order, whose file in `<hooks>` is absent or the toolkit's own, the hooks command shall:
  - write the hook's template (`templates/hooks/<hook>` from the plugin, `.prd-toolkit/hooks/<hook>` from the vendored
    copy) with every `{{hook}}` replaced by the hook's name and every `{{prd}}` by `<prd>`, escaped for sh double quotes
    (a backslash before each `\`, `"`, `$` and backtick), with LF line ends;
  - set the file's mode to 0755;
  - print `replaced <hooks>/<hook> (it used uv run --script)` when the replaced file held a line holding both
    `uv run --script` and `prd_git_hook.py`, and `installed <hooks>/<hook>` otherwise.
- AC-101.2 When install runs where `core.hooksPath` is not set, the hooks command shall create the folder `<hooks>`
  when it is absent, and shall leave `core.hooksPath` unset.
Errors: -
Edge cases: in a linked worktree `<hooks>` is the clone's shared hooks folder, as git prints it; where `core.hooksPath` is set, FR-070 applies; a hook file that is the toolkit's own is overwritten, and only a hook of the user's own is left alone (FR-102) → AC-101.1
Tests: T-101.1 [integration], T-101.2 [integration], T-101.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; cli:git_hook_shims; FR-096

### FR-102 Install leaves a user's own hook alone and prints the line to add
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:294 @07f77b1
  prd-toolkit/scripts/prdlint/hooks.py:256 @07f77b1
Acceptance (EARS):
- AC-102.1 If install runs where `core.hooksPath` is not set and a hook's file in `<hooks>` exists and is not the
  toolkit's own, the hooks command shall leave the file unchanged and print
  ``<hooks>/<hook> already exists and was left alone; add this line to <hooks>/<hook> (an sh hook; place it before any `exit 0` in it): <line>``,
  `<line>` being the hook line for that hook and `<prd>`, exactly:
  `prd_top="$(git rev-parse --show-toplevel)" || exit 1; if [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ ! -f "$prd_top/.prd-toolkit/prd" ]; then echo "prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped" >&2; elif [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ -f "$prd_top/.prd-toolkit/prd" ] && [ -d "$prd_top/<prd>" ]; then command -v uv >/dev/null 2>&1 || { echo "prd-toolkit: uv is not on PATH; install uv to run this hook" >&2; exit 1; }; sh "$prd_top/.prd-toolkit/prd" git-hook <hook> "$prd_top/<prd>" "$@" || exit $?; else echo "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped" >&2; fi`,
  with `<prd>` escaped as AC-101.1 says.
- AC-102.2 If that file holds a line holding both `uv run --script` and `prd_git_hook.py`, the hooks command shall
  instead print
  `<hooks>/<hook> already exists and was left alone; replace its uv run --script … prd_git_hook.py line in <hooks>/<hook> with this line: <line>`.
Errors: -
Edge cases: where `core.hooksPath` is set, the same instruction follows FR-070's prefix → AC-070.2
Tests: T-102.1 [integration], T-102.2 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-103 The hook line runs the vendored launcher or skips a branch without it
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:256 @07f77b1
Flow: 1. find the top → 2. copy without launcher: skip → 3. copy, launcher and PRD folder present: uv guard, then the launcher → 4. otherwise: skip
Acceptance (EARS):
- AC-103.1 When an sh hook that holds the hook line runs in a work tree whose top holds
  `.prd-toolkit/prd_git_hook.py`, `.prd-toolkit/prd` and the PRD folder, with `uv` on PATH, the hook line shall run
  `sh <top>/.prd-toolkit/prd git-hook <hook> <top>/<prd>` followed by the arguments the hook was given. When that
  command exits 0, the hook shall go on to its next line.
- AC-103.2 If the command AC-103.1 runs exits with a code other than 0, the hook shall exit with that code.
- AC-103.3 If `.prd-toolkit/prd_git_hook.py`, `.prd-toolkit/prd` and the PRD folder are present and `uv` is not on
  PATH, the hook line shall print `prd-toolkit: uv is not on PATH; install uv to run this hook` on stderr, and the
  hook shall exit 1.
- AC-103.4 If `.prd-toolkit/prd_git_hook.py` is present and `.prd-toolkit/prd` is not, the hook line shall print
  `prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped` on stderr, and the
  hook shall go on to its next line.
- AC-103.5 If `.prd-toolkit/prd_git_hook.py` or the PRD folder is absent, the hook line shall print
  `prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped` on stderr, and the hook shall go
  on to its next line.
- AC-103.6 If `git rev-parse --show-toplevel` fails, the hook shall exit 1.
Errors: -
Edge cases: the launcher runs through `sh`, so a launcher without its executable bit still runs → AC-103.1; a PRD path holding a space or `$` is one argument → AC-103.1
Tests: T-103.1 [integration], T-103.2 [integration], T-103.3 [integration], T-103.4 [integration], T-103.5 [integration], T-103.6 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-096

### FR-104 Install refreshes the managed blocks and refuses a broken marker
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:316 @07f77b1
  prd-toolkit/scripts/prdlint/hooks.py:360 @07f77b1
Acceptance (EARS):
- AC-104.1 When install runs from the plugin, after the hook lines it shall write the managed blocks that
  `prd_block.py` writes for the PRD: `CLAUDE.md` at the top, the PRD folder's `README.md`, and the parent folder's
  `README.md` when that parent is named `prd`. For each file it changes, in that order, it shall print
  `refreshed <path>`, `<path>` relative to the top. A file already current gets no line.
- AC-104.2 If a managed block's markers in one of those files are broken, install shall print
  `prd_hooks: install refused: <file>: <problem>; fix the marker, then run prd_block.py <prd>` on stderr, `<file>`
  relative to the top. It shall write no file (no `.prd-toolkit/`, hook, `.gitignore` line or block) and exit 1.
Errors: -
Edge cases: what a block holds, and the text of `<problem>`, belong to `prd_block.py` (area status); install from the vendored copy writes no block → AC-106.1
Tests: T-104.1 [integration], T-104.2 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-105 Install names a stale CI file and never rewrites it
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:353 @07f77b1
Acceptance (EARS):
- AC-105.1 When install runs and `.gitlab/prd-toolkit.yml` or `.github/workflows/prd-toolkit.yml` exists at the top
  with text other than what `prd_hooks.py ci` would write for the PRD now, install shall print, as its last stdout
  lines, `stale: <file>: re-run prd_hooks.py ci --<forge> --force` for each such file, the GitLab file first. It shall
  leave each file unchanged and exit 0.
Errors: -
Edge cases: a CI file identical to what `ci` writes gets no line → AC-105.1; no CI file gets no line
Tests: T-105.1 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-068

### FR-106 Install from the vendored copy writes the hooks only
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:316 @07f77b1
Acceptance (EARS):
- AC-106.1 When `.prd-toolkit/prd_hooks.py install <prd_dir>` runs from the vendored copy, the hooks command shall
  write and print the hooks as AC-101.1 and AC-102.1 say, from `.prd-toolkit/hooks/`, and print AC-105.1's stale
  lines. It shall leave `.prd-toolkit/` unchanged, write no `.gitignore` line and no managed block, and print no
  `vendored` or `refreshed` line.
Errors: -
Tests: T-106.1 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-107 Vendor refreshes .prd-toolkit/ and writes nothing else
Status: approved
Source: prd-toolkit/scripts/prdlint/hooks.py:311 @07f77b1
  prd-toolkit/scripts/prd_hooks.py:73 @07f77b1
Acceptance (EARS):
- AC-107.1 When `prd_hooks.py vendor <prd_dir>` runs from the plugin in a git checkout, the hooks command shall write
  `.prd-toolkit/` byte for byte as install writes it (FR-098, FR-099) and print the one line
  `vendored the toolkit into .prd-toolkit/ (version <version>)`. It shall write no hook, no `.gitignore` line, no
  managed block and no CI file, and exit 0.
- AC-107.2 If `vendor` runs from the vendored copy, the hooks command shall print
  `prd_hooks: vendor runs from the plugin, not from .prd-toolkit/` on stderr, write no file and exit 2.
- AC-107.3 If a pack the PRD names cannot be resolved, `vendor` shall print `prd_hooks: vendor refused: <reason>` on stderr,
  `<reason>` as AC-099.3 gives it, write no file and exit 2.
- AC-107.4 If the PRD folder is not inside a git checkout, `vendor` shall write no file, print
  `prd_hooks: <folder> is not inside a git checkout` on stderr, `<folder>` the absolute path of the PRD folder, and exit 2.
Errors: -
Edge cases: the refusal names `vendor`, not `install` → AC-107.3
Tests: T-107.1 [integration], T-107.2 [integration], T-107.3 [integration], T-107.4 [integration], T-107.5 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-108 Check compares the vendored copy with the plugin
Status: approved
Source: prd-toolkit/scripts/prdlint/hooks.py:437 @07f77b1
Acceptance (EARS):
- AC-108.1 If `.prd-toolkit/` is absent at the top, `prd_hooks.py check <prd_dir>`, run from the plugin, shall print
  the one line `.prd-toolkit/ is missing; run prd_hooks.py install` and exit 1.
- AC-108.2 When check runs from the plugin and `.prd-toolkit/` exists, it shall print, in this order:
  - `.prd-toolkit/VERSION <vendored> differs from the plugin version <version>` when the text of
    `.prd-toolkit/VERSION`, white space removed at its ends, is not the plugin's version;
  - for each file AC-098.1 lists, in its order, `.prd-toolkit/<path> is missing` or
    `.prd-toolkit/<path> differs from the plugin copy`;
  - then `.prd-toolkit/<path> is not in the plugin` for each file under `.prd-toolkit/`, wherever it lies, outside a
    `__pycache__` folder, that AC-098.1 does not list and install does not generate: `VERSION`, `HOMEPAGE`,
    `pack-sources.json`, `.gitignore` and every file under `packs/` are never reported.
  It shall exit 1 when it prints any line.
- AC-108.3 When check runs from the plugin and none of FR-108 to FR-111 finds anything, it shall print nothing and
  exit 0.
- AC-108.4 If `.prd-toolkit/VERSION` is absent, check shall print
  `.prd-toolkit/VERSION (none) differs from the plugin version <version>`.
- AC-108.5 If `prd_hooks.py check <prd_dir>` runs from the vendored copy without `--ci`, the hooks command shall print
  `prd_hooks: run check from the plugin, not the vendored copy` on stderr and exit 2.
Errors: -
Edge cases: check without `--ci` from the vendored copy compares nothing and refuses → AC-108.5; the lines of FR-109, FR-110 and FR-111 follow these in that order
Tests: T-108.1 [integration], T-108.2 [integration], T-108.3 [integration], T-108.4 [integration], T-108.5 [integration], T-108.6 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-109 Check reports a stale hook
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:466 @07f77b1
Acceptance (EARS):
- AC-109.1 When check runs and a hook file in `<hooks>` is the toolkit's own and is not the plugin's template for that
  hook filled as AC-101.1 says for some PRD folder path (one and the same path at every `{{prd}}`), check shall print
  `stale: <hooks>/<hook>; run prd_hooks.py install`.
- AC-109.2 When check runs and a hook file in `<hooks>` is the user's own and holds a line holding both
  `uv run --script` and `prd_git_hook.py`, check shall print
  `stale: <hooks>/<hook>; replace its uv run --script … prd_git_hook.py line with the line prd_hooks.py install prints`.
- AC-109.3 When check runs, a toolkit hook filled for another PRD folder's path, a hook that is absent, and a user's
  own hook without such a line shall each give no `stale: <hooks>/` line.
Errors: -
Edge cases: where `core.hooksPath` is set, `<hooks>` is that folder and the same rules apply → AC-070.3; `check --ci` never reads the hooks → AC-111.4
Tests: T-109.1 [integration], T-109.2 [integration], T-109.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-070

### FR-110 Check reports a stale vendored pack
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:407 @07f77b1
Acceptance (EARS):
- AC-110.1 If a pack of AC-099.1 has no folder `.prd-toolkit/packs/<name>/`, check shall print
  `packs/<name>: missing; source <source> <version>; run prd_hooks.py install`, `<version>` being the version of the
  folder the pack resolves to from the plugin.
- AC-110.2 If that folder's files, outside `__pycache__` folders and `.pyc` files, differ in any path or byte from the
  folder the pack resolves to, check shall print `packs/<name>: differs from <source> <version>; run prd_hooks.py install`.
- AC-110.3 If the folder matches and `.prd-toolkit/pack-sources.json` does not record the pack's source for its name,
  check shall print
  `packs/<name>: vendored from <recorded>, the PRD names <source>; run prd_hooks.py install`. `<recorded>` is the
  recorded source, or `an unrecorded source` when the file records none for that name or cannot be read as a JSON
  object.
Errors: -
Edge cases: a pack that cannot be resolved gives no line here; lint's `pack-resolves` reports it
Tests: T-110.1 [integration], T-110.2 [integration], T-110.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-111 Check reports stale managed blocks and CI files
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:370 @07f77b1
  prd-toolkit/scripts/prd_hooks.py:51 @07f77b1
Acceptance (EARS):
- AC-111.1 When `check` or `check --ci` runs and a managed block file of AC-104.1 is not what `prd_block.py` would
  write now, the hooks command shall print `stale: <file>; run prd_block.py <prd>`, `<file>` relative to the top,
  and exit 1.
- AC-111.2 If a managed block's markers are broken, `check` and `check --ci` shall print
  `stale: <file>: <problem>; run prd_block.py <prd>` and exit 1.
- AC-111.3 Where git ignores the file `CLAUDE.md` at the top, `check` and `check --ci` shall print no stale line for it.
- AC-111.4 When `check --ci` runs, it shall print only the lines of AC-111.1, AC-111.2 and AC-068.5, and none of
  FR-108, FR-109 or FR-110. It shall run the same way from the vendored copy as from the plugin.
- AC-111.5 If `check --ci` runs on a PRD folder that is not inside a git checkout, the hooks command shall print
  `prd_hooks: <folder> is not inside a git checkout` on stderr, `<folder>` the absolute path of the PRD folder, and
  exit 2.
- AC-111.6 When `check` without `--ci` runs from the plugin, it shall also print AC-068.5's line
  `stale: <file>: re-run prd_hooks.py ci --<forge> --force` for each CI file present that differs from what `ci`
  would write now.
Errors: -
Edge cases: a broken marker in `check --ci` is a stale line and exit 1, never exit 2 → AC-111.2
Tests: T-111.1 [integration], T-111.2 [integration], T-111.3 [integration], T-111.4 [integration], T-111.5 [integration], T-111.6 [integration], T-111.7 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-068

### FR-112 Uninstall removes only the toolkit's own hooks
Status: approved
Source: prd-toolkit/scripts/prdlint/hooks.py:492 @07f77b1
Acceptance (EARS):
- AC-112.1 When `prd_hooks.py uninstall <prd_dir>` runs where `core.hooksPath` is not set, for each of `commit-msg`
  and `pre-commit`, in that order, whose file in `<hooks>` is the toolkit's own, the hooks command shall delete the file
  and print `removed <hooks>/<hook>`. It shall leave every other hook file and `.prd-toolkit/` unchanged, and exit 0.
- AC-112.2 Where `core.hooksPath` is set, for each of `commit-msg` and `pre-commit`, in that order, whose file in `<hooks>`
  is the toolkit's own, uninstall shall delete the file and print `removed <hooks>/<hook>`. It shall leave a hook file of
  the user's own unchanged, and exit 0.
Errors: -
Edge cases: with no toolkit hook, uninstall prints nothing and exits 0 → AC-112.1; where `core.hooksPath` is set, `<hooks>` is the folder it names, as git prints it → AC-112.2
Tests: T-112.1 [integration], T-112.2 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-070

### FR-113 CI writes the include file and refuses to overwrite a different one
Status: approved
Source: prd-toolkit/scripts/prdlint/hooks.py:626 @07f77b1
  prd-toolkit/scripts/prd_hooks.py:59 @07f77b1
Acceptance (EARS):
- AC-113.1 When `prd_hooks.py ci --github <prd_dir>` runs, the hooks command shall write
  `.github/workflows/prd-toolkit.yml` at the top with LF line ends, creating its folders, print
  `wrote .github/workflows/prd-toolkit.yml` and exit 0. With `--gitlab` it shall write `.gitlab/prd-toolkit.yml`,
  print `wrote .gitlab/prd-toolkit.yml` and then `include: '.gitlab/prd-toolkit.yml'`, and exit 0.
- AC-113.2 If that file exists with other text and `--force` is not given, the hooks command shall print the unified
  diff of the existing text against the generated one, headed `--- <file> (existing)` and `+++ <file> (generated)`,
  then `<file> exists and differs; rerun with --force to overwrite it`. It shall leave the file unchanged and exit 1.
  With `--force`, it shall write the file as AC-113.1 says.
- AC-113.3 When that file exists with the generated text, the hooks command shall print AC-113.1's lines and exit 0.
- AC-113.4 If `.prd-toolkit/` exists at the top and holds no file `prd`, the hooks command shall print
  `prd_hooks: .prd-toolkit/ predates 0.8.8 (no .prd-toolkit/prd); run prd_hooks.py install <prd_dir> first` on
  stderr, `<prd_dir>` the argument as given, write no file and exit 2. With no `.prd-toolkit/` at all, `ci` shall
  write as AC-113.1 says.
- AC-113.5 If the PRD folder is not inside a git checkout, `ci` shall write no file, print
  `prd_hooks: <folder> is not inside a git checkout` on stderr, `<folder>` the absolute path of the PRD folder, and exit 2.
Errors: -
Edge cases: `ci` runs from the vendored copy as from the plugin; outside a git checkout `ci` refuses before it writes → AC-113.5
Tests: T-113.1 [integration], T-113.2 [integration], T-113.3 [integration], T-113.4 [integration], T-113.5 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-068

### FR-114 The merge-gate jobs
Status: verified
Source: prd-toolkit/scripts/prdlint/hooks.py:566 @2450062
  prd-toolkit/scripts/prdlint/hooks.py:545 @2450062
Acceptance (EARS):
- AC-114.1 When `ci` writes a CI file, the file shall hold these merge-gate jobs, in this order:
  - `prd-lint`, with the commands `sh .prd-toolkit/prd lint --ci <q>` and `sh .prd-toolkit/prd hooks check --ci <q>`,
    and a third, `sh .prd-toolkit/prd links check --ci <q>`, when the PRD folder holds `links.md`;
  - `prd-trace`, with `sh .prd-toolkit/prd trace <q> --range <range>`;
  - one `standards-<n>` job per enforced section 5 row that has a linter command (FR-068);
  - one `test-<level>` job per Levels row of `testing.md` whose Gate is `build` and whose Harness command cell holds a
    backticked command, in Levels order, whose one command is that backticked text.
  `<q>` is `<prd>` written as one POSIX shell word (quoted only when it holds a character that needs it).
- AC-114.2 When `ci` names a job, the hooks command shall replace each character of the name other than an ASCII
  letter, a digit, `_` or `-` with `-`. A job whose name is already taken shall gain `-<n>`, `<n>` the lowest number from
  2 whose name is not yet taken, in job order.
- AC-114.3 When the `## Harness` section of `testing.md` holds a slot bullet `- **Runner setup.**`, each backticked
  text on that bullet (its first line and the lines indented under it), in order, shall be one setup command, and every
  job `ci` writes, merge-gate and manual (FR-115) alike, shall run the setup commands, in that order, before its own
  commands. Where the Harness holds no such bullet, or the bullet holds no backticked text, no job shall have a setup
  command, and `ci` shall write the CI file it writes without the bullet.
Errors: -
Edge cases: a deploy-gate level gets no merge-gate job → AC-114.1; a level whose Harness command cell has no backticked command gets no job → AC-114.1; two `Runner setup` bullets give their setup commands in bullet order → AC-114.3; the slot is not one of the fifteen lint checks, so lint reports nothing for it (AC-025.4) → AC-114.3
Tests: T-114.1 [integration], T-114.2 [integration], T-114.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks; FR-068

### FR-115 The manual drift and deploy-test jobs
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:562 @07f77b1
Acceptance (EARS):
- AC-115.1 When `ci` writes a CI file, the file shall hold, after the merge-gate jobs, these manual jobs:
  - `drift-<env>` for each environment of `operations.md`'s Environments table, in its order, that has a `## Drift`
    row, with the one command `sh .prd-toolkit/prd drift <q> --env <env>`;
  - then `test-deploy-<env>` for each environment, in that order, that a runbook `tests` step runs on, with one
    command `export PRD_ENV=<env> TEST_ENV=<env>; <harness command>` for each level those steps name, in step order,
    that has a Harness command.
  `<env>` is written as one POSIX shell word. There is no `test-deploy-<env>` job when none of its levels has a command.
  Job names follow AC-114.2, counted after the merge-gate jobs.
Errors: -
Edge cases: a level named twice on one environment gives its command twice → AC-115.1; CI never runs `prd_deploy.py`
Tests: T-115.1 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-116 The GitLab include file
Status: verified
Source: prd-toolkit/scripts/prdlint/hooks.py:619 @2450062
Acceptance (EARS):
- AC-116.1 When `ci --gitlab` writes `.gitlab/prd-toolkit.yml`, the file shall start with the line
  `# Generated by prd_hooks.py ci --gitlab; regenerate rather than edit.`, then AC-118.1's line when it applies,
  then an empty line. Each merge-gate job then has these lines:
  - `<id>:`, `  image: python:3.12`, `  rules:` and `    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'`;
  - for `prd-trace` only, `  variables:` and `    GIT_DEPTH: "0"`;
  - `  before_script:`, `    - "pip install uv"` and `  script:`;
  - one `    - <command>` line per command, `<command>` a JSON string with `<range>` written as
    `$CI_MERGE_REQUEST_DIFF_BASE_SHA..HEAD`;
  - an empty line.
  The file ends with one newline.
- AC-116.2 When the GitLab file holds a manual job, that job's rules shall be the two lines `    - when: manual` and
  `  allow_failure: true` in place of the `- if:` line, and its other lines shall be as AC-116.1 says.
- AC-116.3 When the jobs have setup commands (AC-114.3), each job of the GitLab file shall hold, directly after its
  `    - "pip install uv"` line, one `    - <setup command>` line per setup command, in their order,
  `<setup command>` a JSON string, and its other lines shall be as AC-116.1 and AC-116.2 say.
Errors: -
Tests: T-116.1 [integration], T-116.2 [integration], T-116.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-117 The GitHub workflow file
Status: verified
Source: prd-toolkit/scripts/prdlint/hooks.py:635 @2450062
Acceptance (EARS):
- AC-117.1 When `ci --github` writes `.github/workflows/prd-toolkit.yml` with no manual job, the file shall hold:
  - `# Generated by prd_hooks.py ci --github; regenerate rather than edit.`, `name: prd-toolkit`, `on:`,
    `  pull_request:`, an empty line, `permissions:`, `  contents: read`, an empty line and `jobs:`;
  - per job, `  <id>:`, `    runs-on: ubuntu-latest`, `    steps:`, `      - uses: actions/checkout@v4`,
    `        with:`, `          fetch-depth: 0` and `      - uses: astral-sh/setup-uv@v5`;
  - one `      - run: <command>` line per command, `<command>` a JSON string with `<range>` written as
    `${{ github.event.pull_request.base.sha }}..HEAD`;
  - an empty line.
  The file ends with one newline.
- AC-117.2 When the GitHub file holds a manual job, the line `  workflow_dispatch:` shall follow `  pull_request:`,
  AC-118.1's line shall follow the first line when it applies, and each job shall have, directly after its `<id>:`
  line, `    if: "github.event_name == 'workflow_dispatch'"` for a manual job and
  `    if: "github.event_name == 'pull_request'"` for a merge-gate job.
- AC-117.3 When the jobs have setup commands (AC-114.3), each job of the GitHub file shall hold, directly after its
  `      - uses: astral-sh/setup-uv@v5` line, one `      - run: <setup command>` line per setup command, in their
  order, `<setup command>` a JSON string, and its other lines shall be as AC-117.1 and AC-117.2 say.
Errors: -
Tests: T-117.1 [integration], T-117.2 [integration], T-117.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-118 The CI file names the secrets the manual jobs may need
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prdlint/hooks.py:581 @07f77b1
Acceptance (EARS):
- AC-118.1 When the jobs `ci` writes include a manual job and `operations.md`'s `## Secrets` section names one or more
  secrets, the CI file's second line shall be
  `# Manual jobs may need these secrets (operations.md Secrets): <names>`, `<names>` the secret names in their order
  in that section, joined by `, `.
- AC-118.2 When the jobs `ci` writes include no manual job, or the `## Secrets` section names no secret, the CI file
  shall hold no line starting `# Manual jobs may need these secrets`.
Errors: -
Edge cases: which bullet text counts as a secret name is the model's (area lint-cli)
Tests: T-118.1 [integration], T-118.2 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_hooks

### FR-119 The dispatcher runs one script by its command name
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prd_dispatch.py:47 @07f77b1
Acceptance (EARS):
- AC-119.1 When `prd_dispatch.py <command> [arguments]` runs with one of the commands `block`, `build-check`, `change`,
  `confirm`, `context`, `deploy`, `drift`, `error`, `gates`, `git-hook`, `help`, `hooks`, `judge`, `links`, `lint`,
  `pack`, `practices`, `publish`, `status` and `trace`, the dispatcher shall run the script
  `prd_<command, each - written as _>.py` from its own folder with its own Python interpreter and the remaining
  arguments, so that stdout, stderr and the exit code are that script's.
- AC-119.2 If the first argument is not one of those commands and is none of `-h`, `--help` and `--version`, the
  dispatcher shall print `prd: unknown command '<command>'` and then `commands: <the twenty commands in name order, joined by , >`
  on stderr, and exit 2.
- AC-119.3 If the command's script is absent from the dispatcher's folder, the dispatcher shall print
  `prd: <script> is not in <folder>; run prd_hooks.py install` on stderr, `<folder>` the absolute path of the
  dispatcher's folder, and exit 2.
- AC-119.4 If the command is `publish`, its script is absent and the dispatcher's folder holds a file `VERSION`, the
  dispatcher shall print `prd: publish runs from the plugin, not from a vendored copy` on stderr and exit 2.
Errors: -
Edge cases: `prd <command> -h` is the script's own help → AC-119.1; `publish` with no `VERSION` beside the dispatcher prints AC-119.3's line → AC-119.3
Tests: T-119.1 [integration], T-119.2 [integration], T-119.3 [integration], T-119.4 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_dispatch; cli:prd_launcher

### FR-120 The dispatcher's help and version
Status: live (since 9.2.0)
Source: prd-toolkit/scripts/prd_dispatch.py:37 @07f77b1
  prd-toolkit/scripts/prd_dispatch.py:30 @07f77b1
Acceptance (EARS):
- AC-120.1 When `prd_dispatch.py` runs with no argument, or with `-h` or `--help` first, it shall print on stdout the
  line `usage: prd <command> [arguments]`. One line shall follow for each command of AC-119.1 whose script is in the
  dispatcher's folder, in name order. Each line is the command name padded with spaces to the length of the longest
  listed name, two spaces, and the first line of the script's docstring, with trailing white space removed. The
  dispatcher shall then exit 0.
- AC-120.2 When `prd_dispatch.py --version` runs, it shall print the text of the file `VERSION` in its folder with
  white space removed at its ends, or, with no such file, the `version` of `.claude-plugin/plugin.json` in its
  folder's parent, followed by a newline, and exit 0.
Errors: -
Edge cases: a folder with no script prints the usage line alone → AC-120.1; a script whose docstring cannot be read gets its name alone on the line → AC-120.1
Tests: T-120.1 [integration], T-120.2 [integration], T-120.3 [integration]  (test-cases/hooks-install.yaml)
Traces: cli:prd_dispatch
