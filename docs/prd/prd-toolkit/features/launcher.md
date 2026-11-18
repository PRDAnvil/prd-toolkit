<!-- Format: references/prd-format.md, "Requirement blocks". -->

# launcher: the Python the prd launcher runs on

Every `prd <command>` runs through the launcher `prd-toolkit/scripts/prd`, an sh script that execs one
`uv run` line, `uv run --quiet --no-project --project <here> --python ">=3.11" --with-requirements <req> python <here>/prd_dispatch.py <arguments>`,
`<here>` the folder that holds the launcher (as `cd` and `pwd` give it) and `<req>` `<here>/requirements.txt`, or
`<here>/requirements-publish.txt` for `prd publish` where that file exists. Given `--python ">=3.11"`, uv inspects
a `.venv` in the working directory before any other interpreter and stops with an error when it cannot read that
`.venv`'s interpreter, so no `prd` command runs there (E-022). This area makes the launcher ask uv for a system
Python first and hand uv that interpreter's path. The launcher is this area's one module; the vendored launcher
`.prd-toolkit/prd` is the same file, byte for byte, and the same build refreshes it with
`prd_hooks.py vendor`, so it behaves the same. No other file changes.

### FR-069 The launcher runs on a system Python when uv finds one
Status: approved
Acceptance (EARS):
- AC-069.1 When the launcher runs, it shall first run `uv python find --system ">=3.11"`, printing nothing that
  command writes on stdout or stderr, and when that command exits 0 and prints a path on stdout, the launcher
  shall exec the `uv run` line it ran before this area with that path, its trailing newline removed, as the one
  value of `--python` in place of `>=3.11`, every other argument unchanged and in the same order.
- AC-069.2 If `uv python find --system ">=3.11"` exits other than 0, or exits 0 and prints nothing on stdout,
  the launcher shall exec the `uv run` line it ran before this area, with `--python ">=3.11"`, printing nothing
  the find wrote.
Errors: -
Edge cases: a path that holds a space is passed as one argument → AC-069.1; a working directory whose `.venv` interpreter cannot be read runs as anywhere else once the find answers a path → AC-069.1; with uv not on PATH the launcher prints `prd: uv is not on PATH; install uv` on stderr and exits 2, as before, and runs no find; `prd publish` takes `requirements-publish.txt` as before; the vendored launcher is the same file and needs no case of its own
Tests: T-069.1 [integration], T-069.2 [integration], T-069.3 [integration]  (test-cases/launcher.yaml)
Traces: cli:prd_launcher; E-022
