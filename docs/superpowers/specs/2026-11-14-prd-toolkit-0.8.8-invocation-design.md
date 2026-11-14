# prd-toolkit 0.8.8: invocation — design

> **Date:** 2026-11-14
> **Author:** Ivan Histand & Claude Code
> **Status:** Approved by the owner 2026-11-14.
> **Extends:** `2026-11-03-prd-toolkit-0.8-umbrella.md` (its 0.8.8 row) and the specs it extends.
> **Needs:** 0.8.7 merged (it is: PR #10, bfb63da).
> **Addresses:** PRDAnvil/prd-toolkit#2 (see Revisions for what remains). **Closes:** item 3 of
> `2026-11-08-prd-toolkit-0.8.6-backlog.md`.

> **Revisions.**
> - §1, §2, §4 (owner, 2026-11-14): the release widens to every skill, command and agent line.
>   §2 said the 80 `uv run --script <scripts>/…` lines run the plugin's own scripts, at one path per
>   installed version. That was wrong: nine files define `<scripts>` as `.prd-toolkit` whenever the
>   repository has a vendored copy, so those lines run the vendored copy by its file and keep one
>   environment per script and per clone, which is most of what remains of #2. Every such line
>   becomes `<scripts>/prd <command>`; each "Which script" paragraph stops on a vendored copy with
>   no launcher; every grader that names a script accepts both forms; the README's vendored-copy
>   examples follow. Found by Task 6's review; plan Tasks 6b, 6c and 6d. "Out" in §2 keeps only the
>   evals' prompts, scaffolds and baselines, Windows without `sh`, and the scripts' uv headers.
> - §2 (plan, 2026-11-14): six eval graders match a script's file name in a command
>   (`prd_links\.py`, `prd_judge\.py`). They are changed to accept both forms, in the task that
>   changes the skill lines; the evals' prompts and baselines stay out of scope. The 80 plugin-path
>   lines are 77 in skills, 2 in commands and 1 in agents.
> - §3.1, §3.3 (build, 2026-11-14): requirements.txt holds only the three packages the vendored scripts need; prd_publish.py's five are in an unvendored requirements-publish.txt, which the launcher uses for `prd publish` when the file is beside it. The union pulled a publish-only, date-pinned package into every hook run, which failed in a host repository whose uv settings exclude newer packages. `--no-config` was refused: it would also drop a user's own uv.toml.
> - §5 (build, 2026-11-14): `prd_hooks.py check --ci` does not inspect installed hook shims; the plain `check` does. A CI checkout has no installed hooks, and `scripts/ci-local.sh` runs `check --ci` in a developer's clone.
> - §3.1 (build, 2026-11-14): the uv line gains `--project "$here"`, so uv reads its settings from the launcher's directory as `--script` read them from the script's, and a launcher in the plugin does not apply the host repository's uv settings; found by the eval run, where `prd publish` failed in a repository with `exclude-newer`.
> - §5 (final review, 2026-11-14): `prd_hooks.py ci` refuses, exit 2, when `.prd-toolkit/` exists without `prd`:
>   `prd_hooks: .prd-toolkit/ predates 0.8.8 (no .prd-toolkit/prd); run prd_hooks.py install <prd dir> first`. The
>   workflow it would write runs `sh .prd-toolkit/prd`, which fails in CI over a 0.8.7 copy. With no `.prd-toolkit/` at
>   all it writes as before.
> - §5 (final review, 2026-11-14): `install` appends the `stale:` line of each generated CI file present, and never
>   rewrites one; the eight `<scripts>` definitions' 0.8.8 guard names the `ci --<forge> --force` rerun. The upgrade
>   note's commit is made once: `.prd-toolkit/`, the workflow and the blocks are committed; a later clone runs `install`
>   only for its own shims. A user's own hook holding the 0.8.7 line is fixed by hand: `install` says to replace that
>   line with the one it prints, and plain `check`'s `stale:` line says the same, so the two no longer loop.
> - §3.2 (final review, 2026-11-14): a `VERSION` beside the dispatcher marks a vendored copy. There a command whose
>   script install never vendors (`PLUGIN_ONLY = ("publish",)`) exits 2 with `prd: publish runs from the plugin, not
>   from a vendored copy`; every other missing script keeps §3.2's message. `prd --help` lists only the commands whose
>   script is present.
> - §4 (final review, 2026-11-14): the shims and the appended line skip a branch whose `.prd-toolkit/` predates the
>   launcher with their own line, `prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook
>   skipped`, tested before the general skip, which keeps its message for the other cases. A shim installed from the
>   earlier 0.8.8 template is stale to plain `check`.
> - §3 (final review, 2026-11-14): the dispatcher's uv header holds the three packages of `requirements.txt`, not
>   five: publish is never vendored, and a direct script-mode run of the vendored dispatcher must not pull the
>   publish-only, date-pinned package.
> - §2 (final review, 2026-11-14), known limit: `packs/document/pack.yaml`'s validator line still runs
>   `uv run --quiet --script ${PACK}/validate_outline.py` from the vendored copy, so a PRD naming the `document` pack adds
>   one environment per clone on every lint. Fixing it bumps the pack's version, which every PRD naming the pack must
>   follow with a patch; it goes in the next release. This is what remains of #2.

## 1. Why

uv keys the cached environment of `uv run --script <path>` on the script's path, not its contents.
Every clone and worktree that vendors the toolkit has its own `.prd-toolkit/` copy, so its git
hooks, its CI and the skill lines that run the vendored copy each add an environment per script
to `~/.cache/uv/environments-v2`, and nothing removes them. On 2026-11-09 one machine held 26,888
of them, about 90 GB and 27 million files. 0.8.5 (NFR-019) fixed the test suite only.

The toolkit also has 17 scripts and no single entry point, which every caller works around by
naming a script file.

**Outcome.** A clone or worktree that uses the toolkit adds no environment of its own, and one
`prd` command runs every script.

**Measured, 2026-11-14, uv 0.13.8.** Three script paths under `--script`: three environments.
The same three under `--with-requirements` with one requirements file: one environment, shared.
A shell launcher costs 44 ms against 26 ms for `--script`, both cached.

## 2. Scope

**In:** the callers that run a vendored copy — the two hook shims, the one-line form for an
existing hook, the generated CI (GitHub and GitLab), the CLAUDE.md block, the `readme-prds.md`
template, and the 18 skill and agent lines that name a `.prd-toolkit/` path. The `prd` command.
Three leftovers from the move (section 8).

**Out:** the 80 skill lines that run the plugin's own scripts (one path per installed version, so
a fixed 17 environments per version); the README's examples; the evals' text; Windows without
`sh`; removing the scripts' uv headers. The `document` pack's validator line, run by file from
the vendored copy (a known limit: see Revisions).

## 3. The pieces

| File | Is | Vendored |
|---|---|---|
| `prd-toolkit/scripts/prd` | The launcher: an `sh` script, mode 755, holding the one uv line | yes, as `.prd-toolkit/prd` |
| `prd-toolkit/scripts/prd_dispatch.py` | The dispatcher: a command name to its script, run under the script's own name | yes |
| `prd-toolkit/scripts/requirements.txt` | The union of the scripts' dependency headers, one requirement per line, sorted (superseded: see Revisions) | yes |

The scripts keep their uv headers. `uv run --script prd_lint.py …` works as before.

### 3.1 The launcher

(superseded: see Revisions)

```sh
#!/bin/sh
# prd-toolkit launcher: one uv environment per requirements list, not per script path.
here=$(cd "$(dirname "$0")" && pwd) || exit 2
command -v uv >/dev/null 2>&1 || { echo "prd: uv is not on PATH; install uv" >&2; exit 2; }
exec uv run --quiet --no-project --python ">=3.11" \
  --with-requirements "$here/requirements.txt" python "$here/prd_dispatch.py" "$@"
```

- `--no-project`: inside a repository with its own `pyproject.toml`, uv must not sync or use that
  project. `--script` ignores the project today; this keeps that.
- `--quiet`: a first run must print nothing of uv's on stderr. uv's `Installed N packages` line is
  the fault behind E-017.
- `--python ">=3.11"`: the scripts' own floor.
- It resolves its own directory, so it runs the same from the plugin and from a vendored copy.

### 3.2 The dispatcher

- `COMMANDS: dict[str, str]`, command to script file. The 17: `block`, `build-check`, `change`,
  `confirm`, `context`, `deploy`, `drift`, `error`, `gates`, `git-hook`, `hooks`, `judge`, `links`,
  `lint`, `publish`, `status`, `trace`. A command is its script's name without `prd_` and `.py`,
  `_` written `-`.
- `prd <command> <args…>` replaces its process with
  `<this interpreter> <dir>/prd_<command>.py <args…>` (`os.execv`). The script therefore prints its
  own usage line (`usage: prd_lint.py …`), its own stderr prefix and its own exit code. Nothing a
  test of an adopted area pins can change.
- `prd`, `prd -h`, `prd --help`: exit 0, stdout `usage: prd <command> [arguments]`, then one line
  per command, sorted: the name and the first line of the script's docstring.
- `prd --version`: exit 0, the plugin's version (`.prd-toolkit/VERSION` when vendored,
  `.claude-plugin/plugin.json` otherwise).
- An unknown command: exit 2, stderr `prd: unknown command '<x>'`, then the command names.
- A command whose script file is missing (a vendored copy older than the dispatcher's table):
  exit 2, stderr `prd: <script> is not in <dir>; run prd_hooks.py install`.
- `prd_tester_guard.py` is not a command: it is a Claude Code hook, not vendored, and reads a
  payload on stdin.

### 3.3 requirements.txt

(superseded: see Revisions)

The five lines the headers hold today: `markdown-it-py>=3.0`, `mermaidx==0.11.3`,
`openapi-spec-validator>=0.7`, `pyyaml>=6.0`, `sqlglot>=25`. It is committed, not generated at
vendor time. A test fails when it is not exactly the union of the `# dependencies` lists of the
scripts in `COMMANDS`.

## 4. What each caller becomes

| Caller | Today | 0.8.8 |
|---|---|---|
| `templates/hooks/pre-commit`, `commit-msg` | `exec uv run --script "$top/.prd-toolkit/prd_git_hook.py" {{hook}} "$top/{{prd}}"` | `exec sh "$top/.prd-toolkit/prd" git-hook {{hook}} "$top/{{prd}}"` |
| `hooks._append_line` | `uv run --script {script} {hook} {prd} "$@"` | `sh "$prd_top/.prd-toolkit/prd" git-hook {hook} {prd} "$@"` |
| `hooks.ci_jobs`, `deploy_jobs` | `uv run --script .prd-toolkit/prd_lint.py --ci <prd>` and the like | `sh .prd-toolkit/prd lint --ci <prd>` and the like |
| `templates/claude-block.md`, `readme-prds.md` | `uv run --script .prd-toolkit/prd_hooks.py install <prd>` | `.prd-toolkit/prd hooks install <prd>` |
| The 18 skill and agent lines | `uv run --script <start>/.prd-toolkit/prd_<x>.py …` | `<start>/.prd-toolkit/prd <x> …` |

- Shims and CI go through `sh`, so a checkout that lost the launcher's executable bit still runs.
  Skill lines call the launcher directly.
- The shims' existing guards stay: the skip on a branch with no `.prd-toolkit/`, and the uv check.
  The skip tests for `.prd-toolkit/prd` beside `prd_git_hook.py`: a branch whose vendored copy
  predates 0.8.8 has no launcher, and its hook must be skipped with the existing message, not fail.
- The 18 lines: `skills/coordinating-prds/running-a-change-set.md` (13),
  `skills/changing-prds/SKILL.md` (2), `skills/testing-from-prds/SKILL.md` (1),
  `skills/testing-from-prds/dispatching.md` (1), `agents/prd-tester.md` (1).
- `prd_tester_guard.py` allows the tester the harness commands `testing.md` names. If it matches a
  vendored script by the `uv run --script` form anywhere, the same change admits the launcher form;
  the plan's first task reads the guard and records what it matches.

## 5. Vendoring and upgrade

- `VENDORED` in `prdlint/hooks.py` gains `prd`, `prd_dispatch.py` and `requirements.txt`. `_vendor`
  copies with `shutil.copy2`, which keeps the mode; a test asserts the vendored launcher is 755.
- `prd_hooks.py install`, run from the 0.8.8 plugin, refreshes `.prd-toolkit/` and rewrites the two
  shims; `prd_hooks.py ci --force` rewrites the workflow. `install` prints one line when it replaced
  a shim of the old form.
- `prd_hooks.py check` reports an installed shim that differs from the vendored template, as it
  already reports a stale block or CI file: `stale: <hooks dir>/<hook>; run prd_hooks.py install`.
  A hook the user appended by hand to their own script is reported only when its line holds
  `uv run --script` and `prd_git_hook.py`.
- A repository that has not reinstalled keeps working: its 0.8.7 shims run the 0.8.7 vendored
  scripts by their headers. It keeps adding environments until it reinstalls.

**Upgrade note, for the changelog** (superseded: see Revisions)**.** Run `prd_hooks.py install docs/prd/<slug>` and
`prd_hooks.py ci --github` (or `--gitlab`) `--force` from the 0.8.8 plugin, in each clone, and
commit `.prd-toolkit/`, the workflow file and the refreshed blocks. The environments already in
`~/.cache/uv/environments-v2` can be deleted at any time; uv rebuilds the ones it still needs.

## 6. The toolkit's own PRD

- No adopted behaviour changes. `lint-cli`'s missing-package hint names `uv run --script <script>`,
  which stays true, and `contracts/cli.yaml`'s `invocation:` lines stay valid.
- One wording patch through `/prd-toolkit:prd-change`, 6.2.2 to 6.2.3, "no dry run (wording
  only)": `adoption.md`'s `trace-and-hooks` row gains `prd-toolkit/scripts/prd`,
  `prd-toolkit/scripts/prd_dispatch.py` and `prd-toolkit/scripts/requirements.txt`; and section 2's
  stale line "Out of scope: the repository's other plugins and the `web/` docs site" is corrected
  for the toolkit's own repository.
- This repository's own `.prd-toolkit/`, shims text and `.github/workflows/prd-toolkit.yml` are
  refreshed with `prd_hooks.py vendor` and `ci --github --force`, in the commits that change their
  sources. `scripts/ci-local.sh` reads the workflow's commands and needs no change unless it
  matches `uv run --script` by text; the plan checks.

## 7. Tests

Unit (the builder's), each named for the plan:

- `test_launcher_two_clones_one_environment` — the hook command run from two copies at two paths
  leaves exactly one directory more in the test cache's `environments-v2` than before, not two.
- `test_launcher_ignores_host_project` — run inside a directory holding a `pyproject.toml` that
  declares an uninstallable dependency: exit 0, and no `.venv` or `uv.lock` appears there.
- `test_launcher_first_run_quiet` — on an empty cache, stderr holds nothing but the script's own.
- `test_launcher_without_uv` — with uv off `PATH`: exit 2 and the one line.
- `test_launcher_from_another_cwd` and `test_launcher_path_with_spaces`.
- `test_dispatch_output_is_the_scripts` — `prd lint --help` equals `prd_lint.py --help`, stdout and
  stderr, byte for byte.
- `test_dispatch_exit_codes` — 0, 1 and 2 pass through.
- `test_dispatch_table_covers_every_script` — every `prd_*.py` with a `main`, less
  `prd_dispatch.py` and `prd_tester_guard.py`, is in `COMMANDS`, and every entry's file exists.
- `test_dispatch_help`, `test_dispatch_version`, `test_dispatch_unknown_command`,
  `test_dispatch_missing_script`.
- `test_requirements_is_the_headers_union`.
- `test_no_generated_line_uses_script_mode` — no shim, appended line or CI job, GitHub or GitLab,
  holds `--script`.
- `test_shim_skips_without_launcher` — a branch whose `.prd-toolkit/` has no `prd`: exit 0 and the
  skip message.
- `test_install_rewrites_old_shims` — a repository installed by 0.8.7's templates is on the new
  form after `install`, and `check` is clean.
- `test_check_reports_old_shim` and `test_check_reports_old_appended_line`.
- `test_vendored_launcher_is_executable`, and `test_vendored_copy.py` extended to the three files.

The tests run the launcher with the session's `UV_CACHE_DIR` (NFR-019), so none of them writes to
the user's cache. Note for whoever runs them: a uv-managed interpreter that already holds a
required package in its own site-packages needs no environment for it, which hides the count the
first test asserts; that test uses the full five-line requirements file, as measured in section 1 (superseded: see Revisions).

Evals: the cases of `coordinating-prds`, `changing-prds` and `testing-from-prds` run before the
version bump, since their skill text changes.

## 8. Leftovers from the move

1. **The stale Out of scope line** in `prd.md` section 2: section 6's patch.
2. **Old-repository SHAs.** One sentence in the plugin README's changelog head and in
   `evals/BASELINE.md`: commit SHAs dated before 2026-11-10 resolve in `ihistand/claude-plugins`.
3. **`prd_error.py check` across the move.** A range that spans c8f48cf reports
   `Detected: changed` on entries whose provenance SHA the move rewrote. No code change: the
   repository's `CLAUDE.md` says to start such a range after c8f48cf. The rewrite was one event.

## 9. Release

Version 0.8.8 in `plugin.json`, `marketplace.json` and `.prd-toolkit/VERSION`; a new
`tests/test_release_0_8_8.py`; the changelog entry with the upgrade note and the PRD version
(6.2.3). Pack manifests keep `toolkit: ">=0.8.0,<0.9"`.

## 10. Decisions and what was set aside

- **Vendored callers only** (owner, 2026-11-14; superseded: see Revisions), over rewriting every skill line: the 80
  plugin-path lines do not leak per clone, and moving them touches every skill, about 100 test
  lines and every eval baseline.
- **A launcher file** (owner, 2026-11-14), over spelling the uv line out in each caller (about 25
  copies, and another reinstall everywhere if it changes) and over `uv tool install` (a
  machine-wide tool can differ in version from the copy a repository vendored, which breaks the
  rule that hooks and CI run the vendored copy).
- **The dispatcher executes; it does not import.** Importing would change `argv[0]` and with it the
  usage lines the adopted areas' tests assert.
- **requirements.txt is committed**, not generated by `vendor`: the vendored copy must match the
  plugin byte for byte, and a generated file would need its own rule.
