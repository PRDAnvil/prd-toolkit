<!-- Format: references/prd-format.md, "Requirement blocks". -->

# release: the plugin's manifests, license files and READMEs

What a user installs and reads: the `prdanvil` marketplace manifest at the repository root, the plugin
manifest, the plugin's LICENSE and NOTICE, its `pyproject.toml` and `uv.lock` (the test environment), the
plugin README and the root README. Behaviour that reads these files (the dispatcher's `prd --version`,
`prd_hooks.py vendor` writing `.prd-toolkit/VERSION` and `.prd-toolkit/LICENSE`) belongs to the areas that
read them.

### FR-268 The marketplace manifest lists one plugin, prd-toolkit, from ./prd-toolkit
Status: live (since 13.1.0)
Source: .claude-plugin/marketplace.json:2 @05ae956
Acceptance (EARS):
- AC-268.1 The marketplace manifest `.claude-plugin/marketplace.json` shall be a JSON object with exactly the keys
  `name`, `owner`, `description` and `plugins`, whose `name` is `prdanvil`, whose `owner.name` is `PRDAnvil` and
  `owner.url` is `https://github.com/PRDAnvil`, and whose `plugins` list holds exactly one entry, with exactly the
  keys `name`, `source`, `version` and `description`, its `name` `prd-toolkit` and its `source` `./prd-toolkit`.
- AC-268.2 The marketplace manifest's top-level `description` shall be
  `prd-toolkit: a living PRD as the single authority Claude Code agents build, test and deploy from`.
Errors: -
Edge cases: the entry's `version` and `description` are FR-270 and FR-271; users install from GitHub `main` of PRDAnvil/prd-toolkit, so the manifest at `main` is what they get
Tests: T-268.1 [integration], T-268.2 [integration]  (test-cases/release.yaml)
Traces: `code:.claude-plugin/marketplace.json`

### FR-269 The plugin manifest names the plugin, its license and its skills and commands folders
Status: live (since 13.1.0)
Source: prd-toolkit/.claude-plugin/plugin.json:2 @05ae956
Acceptance (EARS):
- AC-269.1 The plugin manifest `prd-toolkit/.claude-plugin/plugin.json` shall be a JSON object with exactly the keys
  `name`, `version`, `description`, `author`, `homepage`, `license`, `skills` and `commands`, whose `name` is
  `prd-toolkit`, `author.name` `Ivan Histand`, `author.url` `https://github.com/PRDAnvil`, `homepage`
  `https://github.com/PRDAnvil/prd-toolkit/tree/main/prd-toolkit`, `license` `MIT`, `skills` `./skills` and
  `commands` `./commands`.
- AC-269.2 The plugin manifest's `name` shall equal the `name` of the marketplace manifest's one plugin entry, and the
  folders its `skills` and `commands` values name, resolved against `prd-toolkit/`, shall each exist as a folder.
Errors: -
Edge cases: the manifest declares no `agents` or `hooks` key; `prd-toolkit/agents/` and `prd-toolkit/hooks/` are found by Claude Code's default layout, not by this file (not asserted); `version` and `description` are FR-270 and FR-271
Tests: T-269.1 [integration], T-269.2 [integration]  (test-cases/release.yaml)
Traces: `code:prd-toolkit/.claude-plugin/plugin.json`; FR-268

### FR-270 The release version agrees in both manifests and the plugin README
Status: live (since 13.1.0)
Source: prd-toolkit/.claude-plugin/plugin.json:3 @05ae956
Acceptance (EARS):
- AC-270.1 The plugin manifest's `version` and the marketplace manifest's one plugin entry's `version` shall be the
  same string, and that string shall match `^[0-9]+\.[0-9]+\.[0-9]+$`.
- AC-270.2 The text of `prd-toolkit/README.md` before its first line that starts with `## `, with each run of white
  space replaced by one space, shall hold `Version <v>.`, `<v>` the plugin manifest's `version`.
- AC-270.3 The first line of the plugin README's `## Changelog` section that matches `^- \*\*[0-9]+\.[0-9]+\.[0-9]+:\*\*`
  shall start with `- **<v>:**`, `<v>` the plugin manifest's `version`, and the versions of all such lines, read in
  file order, shall be in strictly descending order (compared as tuples of integers), the last of them `0.1.0`.
Errors: -
Edge cases: at 05ae956 the version is 0.8.19 in all three places; the PRD pins no release number, only that the three places agree: each release's `prd-toolkit/tests/test_release_<version>.py` pins the number, so a release needs no PRD edit (Q-01, owner 2026-11-25); `.prd-toolkit/VERSION`, the third place a release bumps, is written by `prd_hooks.py vendor` and lies outside this area
Tests: T-270.1 [integration], T-270.2 [integration], T-270.3 [integration]  (test-cases/release.yaml)
Traces: `code:prd-toolkit/.claude-plugin/plugin.json`; `code:.claude-plugin/marketplace.json`

### FR-271 One description in both manifests names every command of the plugin
Status: verified
Source: prd-toolkit/.claude-plugin/plugin.json:4 @05ae956
Acceptance (EARS):
- AC-271.1 The marketplace manifest's one plugin entry's `description` shall equal the plugin manifest's
  `description`, character for character.
- AC-271.2 The set of names `<name>` that the plugin manifest's `description` holds as `/prd-toolkit:<name>` (each
  `<name>` the longest run of `a`-`z` and `-` after the colon) shall equal the set of stems of the files
  `prd-toolkit/commands/*.md`.
- AC-271.3 The set of names `<name>` that the `**Slash commands**` line of `README.md` holds as `/prd-toolkit:<name>`
  shall equal the set of stems of the files `prd-toolkit/commands/*.md` (E-087).
Errors: -
Edge cases: `/prd-toolkit:prd-change` and `/prd-toolkit:prd-change-set` are two names → AC-271.2, AC-271.3; at 05ae956 both sets of AC-271.2 hold twelve names, and the root README's line names ten (E-087)
Tests: T-271.1 [integration], T-271.2 [integration], T-271.3 [integration]  (test-cases/release.yaml)
Traces: `code:.claude-plugin/marketplace.json`; E-087

### FR-272 The rule count the manifests and READMEs name is the number of registered lint rules
Status: live (since 13.1.0)
Source: prd-toolkit/.claude-plugin/plugin.json:4 @05ae956
Acceptance (EARS):
- AC-272.1 The plugin manifest's `description`, with every run of white space in it and in each text below replaced
  by one space, the text of `prd-toolkit/README.md` before its first `## ` line and the text of `README.md` before its first `## `
  line shall each hold `a 41-rule linter`, the whole of `README.md` shall hold `checks 41 rules`, the `## Lint CLI`
  section of `prd-toolkit/README.md` shall hold `prints the 41 rules`, and `prd_lint.py --list-rules` shall exit 0 and
  print exactly 41 lines.
Errors: -
Edge cases: what `--list-rules` prints per line is lint-cli's (FR-003)
Tests: T-272.1 [integration]  (test-cases/release.yaml)
Traces: `cli:prd_lint`; FR-003

### FR-273 The READMEs install and update the plugin by the manifests' names and describe its commands as they are
Status: verified
Source: README.md:26 @05ae956
Acceptance (EARS):
- AC-273.1 The `## Install` section of `README.md` and the `## Install` section of `prd-toolkit/README.md` shall each
  hold, inside one fenced code block, the line `/plugin marketplace add PRDAnvil/prd-toolkit` and directly after it
  the line `/plugin install prd-toolkit@prdanvil`, where `prdanvil` is the marketplace manifest's `name` and `prd-toolkit`
  its one plugin entry's `name`.
- AC-273.2 The `## Install` section of `README.md` shall hold `claude plugin uninstall prd-toolkit@ihistand` and
  `at every scope`.
- AC-273.3 The `## Install` section of `README.md` shall hold ``The plugin adds no `prd` command to your shell``
  and name the two launchers `.prd-toolkit/prd <command>` and
  `~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd <command>`.
- AC-273.4 The table (the first run of lines that start with `|`) of the `## Commands and skills` section of
  `prd-toolkit/README.md` shall have one data row per
  file `prd-toolkit/commands/<name>.md`, each row's first cell starting with a backtick and `/prd-toolkit:<name>`,
  and no other data row.
- AC-273.5 The `## Install` section of `prd-toolkit/README.md` shall give the update of an installed copy as
  `claude plugin marketplace update prdanvil`, then `claude plugin update prd-toolkit@prdanvil`, then `/reload-plugins`,
  in that order, as the changelog's Upgrade notes do (E-089).
- AC-273.6 The `## Tests and evals` section of `prd-toolkit/README.md` shall not say that the skills' text prints a
  bare `/prd-<name>` command (E-088).
- AC-273.7 The `**Features:**` list of `README.md` shall say that it names the main skills and that the plugin README
  lists all eleven, with a link to `./prd-toolkit/README.md` (Q-06, owner 2026-11-25; E-091).
Errors: -
Edge cases: the root README's slash-command line is FR-271 (E-087)
Tests: T-273.1 [integration], T-273.2 [integration], T-273.3 [integration], T-273.4 [integration], T-273.5 [integration], T-273.6 [integration], T-273.7 [integration]  (test-cases/release.yaml)
Traces: `code:README.md`; FR-268; E-088, E-089, E-091

### FR-274 The root README's prd shell function picks the vendored launcher or the newest installed plugin's
Status: verified
Source: README.md:40 @05ae956
Acceptance (EARS):
- AC-274.1 When the `prd` function of `README.md` (the lines from `prd() {` to the next line `}`) runs in sh with a
  first argument other than `publish`, in a git working tree whose top level holds the file `.prd-toolkit/prd`, it
  shall run `sh <top>/.prd-toolkit/prd` with every argument it was given, in order, each kept as one argument.
- AC-274.2 When the function's first argument is `publish`, or its working directory is in no git working tree, or
  the working tree's top level holds no `.prd-toolkit/prd`, the function shall run `sh <dir>scripts/prd` with every
  argument it was given, in order, `<dir>` the last of the folders `$HOME/.claude/plugins/cache/prdanvil/prd-toolkit/*/`
  in `sort -V` order.
- AC-274.3 If no folder matches `$HOME/.claude/plugins/cache/prdanvil/prd-toolkit/*/` when the function would run the
  plugin's launcher (AC-274.2), the function shall print `prd-toolkit is not installed` on stderr, run nothing, and
  return 127 (E-090).
Errors: -
Edge cases: the function runs under sh, bash and zsh on macOS and Linux, whose `sort` supports `-V` (Q-03, owner 2026-11-25); `0.8.9` and `0.8.19` installed side by side → `0.8.19` (version order, not text order) → AC-274.2; an argument holding a space stays one argument → AC-274.1; at 05ae956, with no installed plugin folder, the function runs `sh scripts/prd` relative to the working directory (E-090)
Tests: T-274.1 [integration], T-274.2 [integration], T-274.3 [integration]  (test-cases/release.yaml)
Traces: `code:README.md`; E-090

### FR-275 The plugin ships the MIT license and a notice of the projects it adapts
Status: live (since 13.1.0)
Source: prd-toolkit/LICENSE:1 @05ae956
Acceptance (EARS):
- AC-275.1 The file `prd-toolkit/LICENSE` shall be 21 lines whose line 1 is `MIT License` and line 3 is
  `Copyright (c) 2026 Ivan Histand`, and the `## License` section of `prd-toolkit/README.md` shall hold
  `MIT; see [LICENSE](./LICENSE).` and ``A vendored `.prd-toolkit/` carries a copy of it.``
- AC-275.2 The file `prd-toolkit/NOTICE` shall name these five projects, each with its URL and license:
  GitHub Spec Kit (`https://github.com/github/spec-kit`, MIT License), cc-sdd (`https://github.com/gotalab/cc-sdd`,
  MIT License), BMAD-METHOD (`https://github.com/bmad-code-org/BMAD-METHOD`, MIT License), mattpocock/skills
  (`https://github.com/mattpocock/skills`, MIT License) and Anthropic `doc-coauthoring` skill
  (`https://github.com/anthropics/skills`, Apache License 2.0), and shall hold
  `Nothing is copied from Taskmaster (Commons Clause) or spec-workflow-mcp (GPL-3.0).` with its white space collapsed.
- AC-275.3 The `## Credits` section of `prd-toolkit/README.md` shall name GitHub Spec Kit, cc-sdd, BMAD-METHOD,
  mattpocock/skills and Anthropic's doc-coauthoring skill, and link `./NOTICE`.
Errors: -
Edge cases: the plugin manifest's `license` `MIT` is FR-269; the vendored `.prd-toolkit/LICENSE` and the root `LICENSE` are byte-identical to `prd-toolkit/LICENSE` at 05ae956 but lie outside this area; NOTICE's pointer to the design spec under `docs/superpowers/` is for readers of the repository, and an installed copy need not resolve it (Q-04, owner 2026-11-25)
Tests: T-275.1 [integration], T-275.2 [integration], T-275.3 [integration]  (test-cases/release.yaml)
Traces: `code:prd-toolkit/LICENSE`; FR-269

### FR-276 Every relative link in the two READMEs names a file the repository tracks
Status: verified
Source: prd-toolkit/README.md:11 @07792ba
Acceptance (EARS):
- AC-276.1 The target of every Markdown link `](<target>)` in `README.md` and `prd-toolkit/README.md` that does not
  start with `http`, with any `#` fragment removed and resolved against the folder of the file that holds it, shall
  be a path that `git ls-files` lists or a folder holding such a path; a target that is only a `#` fragment points
  into its own file and resolves.
- AC-276.2 The plugin README `prd-toolkit/README.md` shall hold exactly one Markdown link whose target starts with
  `../docs/superpowers/specs/`, and that target shall be `../docs/superpowers/specs/`, in place of one link per
  release's spec (Q-05, owner 2026-11-25; E-092).
Errors: -
Edge cases: links into `../docs/superpowers/` are for readers of the repository on GitHub; an installed copy (the plugin folder alone) does not hold them and need not resolve them (Q-04, owner 2026-11-25); at 05ae956 the root README's links are `./prd-toolkit/README.md` and `./LICENSE`
Tests: T-276.1 [integration], T-276.2 [integration]  (test-cases/release.yaml)
Traces: `code:prd-toolkit/README.md`; E-092

### FR-277 pyproject.toml and uv.lock define the test environment
Status: live (since 13.1.0)
Source: prd-toolkit/pyproject.toml:5 @05ae956
Acceptance (EARS):
- AC-277.1 The file `prd-toolkit/pyproject.toml` shall set `project.version` to `0.1.0`, which no release changes
  because nothing builds or reads the package (`tool.uv.package = false`; Q-02, owner 2026-11-25),
  `project.requires-python` to `>=3.11`,
  `project.dependencies` to exactly `pyyaml>=6.0`, `sqlglot>=25`, `openapi-spec-validator>=0.7` and
  `markdown-it-py>=3.0`, `dependency-groups.dev` to exactly `pytest>=8` and `pytest-xdist>=3`, and
  `tool.uv.package` to `false`.
- AC-277.2 The file `prd-toolkit/pyproject.toml` shall set `tool.pytest.ini_options.testpaths` to `["tests"]`,
  `tool.pytest.ini_options.pythonpath` to `["scripts", "tests"]`, and `tool.pytest.ini_options.norecursedirs` to a
  list that holds `fixtures`.
- AC-277.3 The file `prd-toolkit/uv.lock` shall set `requires-python` to `>=3.11` and hold one `[[package]]` named
  `prd-toolkit` with `source` `{ virtual = "." }` and the same `version` as `prd-toolkit/pyproject.toml`, whose
  `metadata.requires-dist` names exactly the four dependencies of AC-277.1 with the same specifiers and whose
  `metadata.requires-dev.dev` names exactly `pytest` `>=8` and `pytest-xdist` `>=3`.
Errors: -
Edge cases: the locked package versions are not asserted; the `prd` launcher uses `scripts/requirements.txt`, not this file (launcher, hooks-install)
Tests: T-277.1 [integration], T-277.2 [integration], T-277.3 [integration]  (test-cases/release.yaml)
Traces: `code:prd-toolkit/pyproject.toml`
