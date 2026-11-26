<!-- Format: references/prd-format.md, "Requirement blocks". -->

# edit-hook: the PRD rule, checked as the agent edits

The git hooks see a change only when it is committed: an agent that edits code in an adopted area with nothing
approved, or leaves a PRD folder that lint refuses, hears of it at the commit, after the work is done. This area is
a Claude Code plugin hook in two tiers that tells the agent sooner. The edit tier runs after each file edit, is
cheap and mechanical, and reminds the agent once per session and area that a behaviour change starts with
`/prd-toolkit:prd-change`. The Stop tier runs when the agent ends its turn, runs lint on each PRD folder the session
edited, and reports only findings the session has not been told of; it is silent when lint is clean. Both tiers
only add context: neither blocks an edit or a stop. The script is `prd-toolkit/scripts/prd_edit_hook.py`, run by
the plugin, never vendored and not a command of the `prd` dispatcher, as the tester guard is not; the same build
adds its two entries to `prd-toolkit/hooks/hooks.json` (area `tester-guard`, which is not adopted), and what that
file holds is stated here. "At `HEAD`" means the file as `git show HEAD:<path>` prints it: what is approved is
what the branch has committed, so a `Status: approved` written into the working tree during a change, before its
approval commit, approves nothing.

### FR-278 Remind once per session when an edit lands where nothing is approved
Status: approved
Flow: 1. read the hook input → 2. find the repository of the edited path and the PRD folders its `HEAD` holds
      → 3. find the area whose Boundary holds the path → 4. no block of it approved at `HEAD`: remind, once per session and area
Acceptance (EARS):
- AC-278.1 When `prd_edit_hook.py post` reads on stdin a JSON object whose `tool_name` is `Edit`, `Write`, `MultiEdit`
  or `NotebookEdit` and whose edited path (`tool_input.file_path`, or `tool_input.notebook_path` for `NotebookEdit`)
  is an absolute path in the working tree of a git repository whose `HEAD` holds a PRD folder `docs/prd/<slug>/`
  (a folder holding `prd.md`) with an `adoption.md`, and the path from the repository root matches a Boundary glob of
  a row of that `adoption.md` whose State is `adopted`, and no block of the row's `features/<area>.md` has a
  `Status:` value that is `approved`, all read at `HEAD`, the hook shall print on stdout the one line
  `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": <reminder>}}` (JSON) and exit 0,
  where `<reminder>` is
  `prd-toolkit: <path> is in area <area> of docs/prd/<slug>, and no block of that area is approved at HEAD; a behaviour change there starts with /prd-toolkit:prd-change before any code, and a change of no behaviour cites Refs: none (no behaviour change).`
  and `<path>` the path from the repository root.
- AC-278.2 Where that PRD folder has no `adoption.md` at `HEAD` (a new project), the hook shall read every path of
  the working tree outside the PRD folder and outside `.prd-toolkit/` as in its Boundary, and every block of its
  `features/*.md` and `nfr.md` at `HEAD` as the blocks AC-278.1 reads, and the reminder shall read
  `prd-toolkit: <path> is in the Boundary of docs/prd/<slug>, and no block of that PRD is approved at HEAD; a behaviour change there starts with /prd-toolkit:prd-change before any code, and a change of no behaviour cites Refs: none (no behaviour change).`
- AC-278.3 When one of the blocks AC-278.1 or AC-278.2 reads is `approved` at `HEAD`, the hook shall print nothing on
  stdout and exit 0; and when none is, it shall remind whatever the working tree's copies of those files say, a
  `Status: approved` not yet committed included.
- AC-278.4 When the hook has reminded about an area (or, by AC-278.2, a PRD folder) in a session, it shall print
  nothing on stdout for a later edit in the same area and session; a session is the input's `session_id` when it is
  a string of 1 to 128 letters, digits, `-` and `_`, and with no such `session_id` the hook shall remind at every
  edit AC-278.1 or AC-278.2 covers.
- AC-278.5 The hook shall print nothing on stdout and exit 0, reminding of nothing, when stdin is not a JSON object;
  `tool_name` is another tool; the edited path is missing, empty or relative; the path lies in no git working tree,
  or in one whose `HEAD` holds no PRD folder (a repository with no commit included); the path lies inside a PRD
  folder or under `.prd-toolkit/`; the path matches no Boundary glob of an `adopted` row (a path of a `not started`,
  `extracted` or `confirmed` row included); the input's `agent_type` is `prd-tester` or ends with `:prd-tester`; or
  the environment variable `PRD_TOOLKIT_EDIT_HOOK` is `off`.
- AC-278.6 If the hook fails in any other way (a file it reads at `HEAD` that is not UTF-8 text, say), it shall print
  one stderr line that starts `prd-toolkit edit hook: `, print nothing on stdout, and exit 0.
- AC-278.7 The hook shall run with the Python standard library alone, so that `python3 -S prd_edit_hook.py post`,
  which loads no site packages, prints what `python3 prd_edit_hook.py post` prints for the same input.
Errors: -
Edge cases: a Boundary glob is matched against the whole path from the repository root, as the commit rule matches
  it: `**/` zero or more folders, `**` any characters, `*` any characters but `/`, `?` one character but `/` → AC-278.1;
  a path in the Boundary of two PRD folders gets one reminder line per folder, in slug order, joined by a newline in the
  one `additionalContext` → AC-278.1; a status with a `(since …)` after it is not `approved` → AC-278.1; a features
  file absent at `HEAD` holds no approved block → AC-278.3; the hook reads the working tree only to find the
  repository, never to decide what is approved → AC-278.3; prd-builder's edits during a build fall in an area whose
  blocks are `approved` at `HEAD`, so they get no reminder → AC-278.3; the session's record lives in the system
  temporary folder, in a file named for the `session_id` → AC-278.4
Tests: T-278.1 [integration], T-278.2 [integration], T-278.3 [integration], T-278.4 [integration], T-278.5 [integration], T-278.6 [integration], T-278.7 [integration], T-278.8 [integration]  (test-cases/edit-hook.yaml)
Traces: cli:prd_edit_hook; the commit rule's Boundary (trace)

### FR-279 Report lint's new findings at Stop for the PRD folders the session edited
Status: approved
Flow: 1. the edit tier notes each PRD folder an edit lands in → 2. at Stop, lint runs on each noted folder
      → 3. the error findings the session has not been told of go back to the agent; a clean lint says nothing
Acceptance (EARS):
- AC-279.1 When `prd_edit_hook.py post` reads an `Edit`, `Write`, `MultiEdit` or `NotebookEdit` call whose edited path
  lies inside a PRD folder of a git working tree (a folder `docs/prd/<slug>/` that holds `prd.md` in the working
  tree), the hook shall note that folder as edited in the session (AC-278.4), print nothing on stdout for it, and
  exit 0.
- AC-279.2 When `prd_edit_hook.py stop` reads on stdin a JSON object whose `session_id` names a session that noted a
  PRD folder since its last Stop run, the hook shall run `sh <launcher> lint <folder>` with the folder's repository
  root as the working directory, `<folder>` the folder's path from that root and `<launcher>` the repository's
  `.prd-toolkit/prd` when it is a file and otherwise the `prd` launcher beside `prd_edit_hook.py`; and when lint
  exits 1, print on stdout the one line
  `{"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": <report>}}` (JSON) and exit 0, where
  `<report>` is these lines joined by newlines: `prd-toolkit: prd lint fails on <folder> after this session's edits:`;
  each error finding line lint printed on stdout (a line that does not hold `: warn: `) that no earlier Stop run of
  the session reported for that folder, in lint's order, at most 20 of them; `and <k> more` when `<k>` more remain;
  and `Finish the PRD edit through /prd-toolkit:prd-change, which runs lint itself.`
- AC-279.3 Where more than one noted folder has a report, the hook shall print them in the one line's
  `additionalContext`, joined by one empty line, in the order of the folders' absolute paths.
- AC-279.4 When lint exits 0 for a noted folder, or every error finding line it printed was reported for that folder
  by an earlier Stop run of the session, the hook shall report nothing for that folder; with no folder to report it
  prints nothing on stdout and exits 0.
- AC-279.5 If lint exits other than 0 and 1, or has not ended after 50 seconds (the hook then stops it), the hook shall
  report for that folder, in place of AC-279.2's report and once per session and folder, the one line
  `prd-toolkit: prd lint could not run on <folder>: <reason>`, `<reason>` lint's first stderr line, or
  `exit <code>` when its stderr is empty, or `timed out after 50 s`.
- AC-279.6 When a Stop run ends, the hook shall hold no folder noted for the session, so that a Stop run with no PRD
  folder edited since the last one runs no lint and prints nothing on stdout.
- AC-279.7 The Stop run shall run no lint, print nothing on stdout and exit 0 when stdin is not a JSON object, its
  `session_id` is missing or not of AC-278.4's form, or `PRD_TOOLKIT_EDIT_HOOK` is `off`; any other failure prints one
  stderr line that starts `prd-toolkit edit hook: ` and exits 0, as AC-278.6 says.
Errors: -
Edge cases: Claude Code runs the Stop hook at the end of every turn, so "since its last Stop run" is per turn →
  AC-279.6; the report never blocks the stop: the agent reads it on its next turn → AC-279.2; a lint finding of
  severity `warn` (a line holding `: warn: `) is never reported → AC-279.2; lint reads the working tree, the folder's uncommitted edits included →
  AC-279.2; a finding fixed and then broken again in one session is not reported the second time → AC-279.4; the
  input's `stop_hook_active` is not read, since the hook never blocks → AC-279.2
Tests: T-279.1 [integration], T-279.2 [integration], T-279.3 [integration], T-279.4 [integration], T-279.5 [integration], T-279.6 [integration], T-279.7 [integration], T-279.8 [integration]  (test-cases/edit-hook.yaml)
Traces: cli:prd_edit_hook; cli:prd_lint

### FR-280 The plugin wires the edit hook in both tiers
Status: approved
Acceptance (EARS):
- AC-280.1 The plugin's `prd-toolkit/hooks/hooks.json` shall hold, under `hooks`, the `PreToolUse` entry of the tester
  guard as it stands, a `PostToolUse` entry whose `matcher` is `Edit|Write|MultiEdit|NotebookEdit` and whose one hook
  is `{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/prd_edit_hook.py\" post", "timeout": 5}`,
  and a `Stop` entry with no `matcher` whose one hook is
  `{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/prd_edit_hook.py\" stop", "timeout": 60}`,
  in that order and with no other key under `hooks`.
- AC-280.2 If `prd_edit_hook.py` is run with no argument, or with a first argument other than `post` and `stop`, it
  shall print the one stderr line `usage: prd_edit_hook.py post|stop`, print nothing on stdout, read no stdin, and
  exit 2.
Errors: -
Edge cases: the tester guard's entry is unchanged by this area → AC-280.1; the Stop timeout leaves room for lint's
  50 seconds (AC-279.5) → AC-280.1; the hook runs from the plugin and is never copied into `.prd-toolkit/`, so
  `prd hooks install` and `prd hooks check` are unchanged → AC-280.1
Tests: T-280.1 [integration], T-280.2 [integration]  (test-cases/edit-hook.yaml)
Traces: cli:prd_edit_hook
