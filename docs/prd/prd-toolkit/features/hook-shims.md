<!-- Format: references/prd-format.md, "Requirement blocks". -->

# hook-shims: the toolkit's own hooks where core.hooksPath is set

`prd_hooks.py install <prd_dir>` writes the toolkit's two git hooks, `commit-msg` and `pre-commit`, into the
repository's hooks folder, the folder `git rev-parse --git-path hooks` prints. Where git's `core.hooksPath` is set,
it wrote neither before this area and printed, for each hook, an instruction to edit the file by hand, while
`prd_hooks.py check <prd_dir>` called a toolkit hook that had been edited so `stale: …; run prd_hooks.py install`,
an instruction that changed nothing: a loop (E-024). This area makes install rewrite a hook that is the toolkit's
own wherever the hooks folder is. A hook file is the toolkit's own when its second line starts with
`# prd-toolkit hook`, as check already reads it; any other file there is the user's own. One module says which
hooks install writes where `core.hooksPath` is set, `prd-toolkit/scripts/prdlint/hookshims.py`; the same build
makes `prdlint/hooks.py` (area `trace-and-hooks`, which is not adopted) call it, and what install and check do is
stated here. `<hooks>` below is the hooks folder as `git rev-parse --git-path hooks` prints it, and `<value>` the
value of `core.hooksPath`.

### FR-070 Install rewrites the toolkit's own hooks where core.hooksPath is set
Status: approved
Acceptance (EARS):
- AC-070.1 When `prd_hooks.py install <prd_dir>` runs where `core.hooksPath` is set, for each of `commit-msg` and
  `pre-commit` whose file in `<hooks>` is the toolkit's own, install shall write the text it writes for that hook
  and PRD folder where `core.hooksPath` is not set, make the file executable as it does there, and print the line
  it prints there: `replaced <hooks>/<hook> (it used uv run --script)` when the file held a line holding both
  `uv run --script` and `prd_git_hook.py`, and `installed <hooks>/<hook>` otherwise.
- AC-070.2 If `prd_hooks.py install <prd_dir>` runs where `core.hooksPath` is set and a hook's file in `<hooks>` is
  absent or the user's own, install shall leave it as it is, writing no file, and print, as before this area, the
  line `core.hooksPath is set to <value>; no shim written; ` followed by the instruction install gives for a hook
  of the user's own: ``add this line to <hooks>/<hook> (an sh hook; place it before any `exit 0` in it): <line>``,
  or, when the file holds a line holding both `uv run --script` and `prd_git_hook.py`,
  `replace its uv run --script … prd_git_hook.py line in <hooks>/<hook> with this line: <line>`, `<line>` the one
  sh line install gives for that hook and PRD folder, as before this area.
- AC-070.3 When `prd_hooks.py check <prd_dir>` runs after an install that wrote a hook by AC-070.1, with nothing
  changed since, check shall print no line starting `stale: <hooks>/<hook>` for that hook.
Errors: -
Edge cases: `core.hooksPath` set to the repository's own `.git/hooks` and to a folder of the working tree are the same rule → AC-070.1; a toolkit hook whose other lines the user edited is the toolkit's own and is rewritten, as where `core.hooksPath` is not set → AC-070.1; the lines install prints for vendoring, the managed blocks and CI are unchanged, in the same order around the hook lines; where `core.hooksPath` is not set install is unchanged; `prd_hooks.py uninstall` is unchanged: where `core.hooksPath` is set it removes nothing and prints `core.hooksPath is set to <value>; removed nothing`; check's `stale:` line for a hook of the user's own that holds a `uv run --script … prd_git_hook.py` line is unchanged
Tests: T-070.1 [integration], T-070.2 [integration], T-070.3 [integration]  (test-cases/hook-shims.yaml)
Traces: cli:prd_hooks; E-024
