<!-- Format: references/prd-format.md, "Requirement blocks". -->

# commands: the plugin's slash-command files

Each file in `prd-toolkit/commands/` is a Claude Code slash command, `/prd-toolkit:<name>`: a one-line description
and a short body of instructions that hands the run to a skill or a script. The requirements of this area state what
each file instructs the agent to do; what the skill or script then does belongs to its own area.

### FR-281 The commands folder holds twelve command files of one shape
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-adopt.md:2 @2b082aa
Acceptance (EARS):
- AC-281.1 The folder `prd-toolkit/commands/` shall hold exactly twelve tracked files: `prd-adopt.md`, `prd-build.md`,
  `prd-change-set.md`, `prd-change.md`, `prd-context.md`, `prd-deploy.md`, `prd-error.md`, `prd-new.md`, `prd-pack.md`,
  `prd-practices.md`, `prd-publish.md` and `prd-status.md`.
- AC-281.2 The command files shall each start with a line `---`, then exactly one frontmatter line, `description: ` and its
  value, then a line `---`; the value shall end with ` (prd-toolkit)` and hold neither `: ` nor ` #`.
- AC-281.3 The command files shall each hold `$ARGUMENTS` exactly once in the body, the text after the
  frontmatter's closing `---` line.
- AC-281.4 The command files shall hold no command name written as `/prd-` and the command's name with no `prd-toolkit:`
  prefix before it (as `/prd-build`), no text `uv run --script`, and no text `${CLAUDE_PLUGIN_ROOT}/scripts`.
- AC-281.5 When the prd-build, prd-change-set, prd-context, prd-deploy, prd-error, prd-publish or prd-status command
  runs, its instructions shall tell the agent to find the one `docs/prd/*/prd.md` and, if there is more than one, to
  ask which PRD.
Errors: -
Edge cases: Claude Code lists each file as `/prd-toolkit:<stem>` and fills `$ARGUMENTS` with the words typed after it (outside this repo, not asserted); prd-practices finds the PRD its own way (AC-293.3); prd-new, prd-adopt and prd-change leave finding the PRD to their skill
Tests: T-281.1 [integration], T-281.2 [integration], T-281.3 [integration], T-281.4 [integration], T-281.5 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands`; FR-271; FR-273

### FR-282 The prd-status and prd-context commands share one Which script paragraph
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-status.md:7 @2b082aa
Acceptance (EARS):
- AC-282.1 The prd-status and prd-context command files shall each hold exactly one paragraph whose first line starts
  with `**Which script.**`, and the two paragraphs shall be identical.
- AC-282.2 When the prd-status or prd-context command runs, its Which script paragraph shall tell the agent that
  `${CLAUDE_PLUGIN_ROOT}` is empty inside a Bash call; that `<scripts>` is `.prd-toolkit` when the repository has a
  `.prd-toolkit/` directory, and otherwise the plugin's `scripts` directory written as a literal absolute path (in
  double quotes when it holds a space), the plugin root being two directories above the skill's base directory, with
  `prd-toolkit:changing-prds` loaded only to read that directory when no prd-toolkit skill has loaded; to Glob for
  `.prd-toolkit/prd*` once and use the same `<scripts>` for every command; and that a script that is not found is a
  tool error to report, never a reason to guess another path.
- AC-282.3 When the prd-status or prd-context command runs, its Which script paragraph shall tell the agent that, when
  `.prd-toolkit/` exists but holds no `prd_error.py`, the vendored copy predates 0.6, and to stop and tell the user to
  run `prd_hooks.py install docs/prd/<slug>` from the plugin and commit `.prd-toolkit/`.
- AC-282.4 When the prd-status or prd-context command runs, its Which script paragraph shall tell the agent that, when
  `.prd-toolkit/` exists but holds no `prd`, the vendored copy predates 0.8.8, and to stop and tell the user the same
  and, when `.github/workflows/prd-toolkit.yml` or `.gitlab/prd-toolkit.yml` exists, also to run
  `prd_hooks.py ci --<forge> --force docs/prd/<slug>` from the plugin and commit both together.
Errors: -
Edge cases: seven skill procedure files hold the same paragraph (the unit test test_release_0_8_8.py counts nine files across skills and commands); those copies belong to the skills areas
Tests: T-282.1 [integration], T-282.2 [integration], T-282.3 [integration], T-282.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-status.md`; `code:prd-toolkit/commands/prd-context.md`; FR-283; FR-284

### FR-283 The prd-status command runs prd status once, unfiltered, and prints the report as it is
Status: verified
Source: prd-toolkit/commands/prd-status.md:27 @2b082aa
Acceptance (EARS):
- AC-283.1 The prd-status command file's body shall start with
  `Print the prd-toolkit status report. Arguments: $ARGUMENTS`.
- AC-283.2 When the prd-status command runs, its instructions shall tell the agent to run
  `<scripts>/prd status docs/prd/<slug>; echo "prd-status-exit=$?"` in one Bash call with the literal PRD folder, to
  add `--json` only when asked for JSON, and never to pipe, filter or truncate the output (no `| head`, no `| grep`).
- AC-283.3 When the prd-status command runs, its instructions shall tell the agent to print the output as it is; they
  shall name the report's parts in the order Next, Header, Requirements, Areas, Adoption map, Not built, Not verified,
  Open errors, Upstreams, Consumers, Change sets, CI, Deployed and Matrix, and say that a vendored copy older than
  0.8.10 prints no Next part and that the script changes nothing itself but runs lint, which runs the PRD's section 7
  validator commands.
- AC-283.4 When the prd-status command runs, its instructions shall tell the agent, on `prd-status-exit=2`, to read
  what the script printed and act on its cause: a wrong path (fix the path), an unmigrated PRD or an internal error;
  and shall not say that nothing was printed (E-095).
Errors: -
Edge cases: under `--json` an exit 2 prints the error document on stdout (`cli:prd_status` `json_error`) → AC-283.4; the report itself is the status and status-next areas
Tests: T-283.1 [integration], T-283.2 [integration], T-283.3 [integration], T-283.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-status.md`; FR-282; `cli:prd_status`

### FR-284 The prd-context command maps its arguments to prd context options and prints the pack as it is
Status: approved
Source: prd-toolkit/commands/prd-context.md:27 @2b082aa
Acceptance (EARS):
- AC-284.1 The prd-context command file's body shall start with
  `Print the prd-toolkit context pack. Arguments: $ARGUMENTS`.
- AC-284.2 When the prd-context command runs, its instructions shall tell the agent that a token that starts with
  `UJ-`, `FR-`, `NFR-`, `AC-`, `T-` or `E-` is an ID and never the area; that the first argument that is neither an ID
  nor `implement` is the area, passed as `--area <area>`; to pass only UJ, FR, NFR and E IDs, together as one `--req`,
  an AC or T id mapped to its FR (`AC-005.2` and `T-005.1` to `FR-005`) and an `E-nnn` passed as it is; that the word
  `implement` becomes `--for implement`; and that with no area and no IDs the pack is the repo pack, the stack and one
  line per area.
- AC-284.3 When the prd-context command runs, its instructions shall tell the agent to run
  `<scripts>/prd context docs/prd/<slug> --area <area> --req <IDs> --for implement; echo "prd-context-exit=$?"` in one
  Bash call with the literal PRD folder, leaving out the options the arguments did not give; that `--req` and
  `--for implement` both need `--area`; and never to pipe, filter or truncate the pack's output.
- AC-284.4 When the prd-context command runs, its instructions shall tell the agent to print the output as it is and
  work from it, and, on `prd-context-exit=1`, to re-read the regions marked STALE before relying on them.
- AC-284.5 When the prd-context command runs, its instructions shall tell the agent, on `prd-context-exit=2`, to read
  what the script printed and act on its cause: wrong arguments (fix them), an unmigrated PRD or an internal error;
  and shall not say that nothing was printed (E-096).
- AC-284.6 When the prd-context command is given IDs and no area, its instructions shall tell the agent to find each
  ID's area from the `features/<area>.md` file that holds the ID's `### <ID>` heading, or to ask; and shall not name
  the repo pack as that source (E-097).
Errors: -
Edge cases: the repo pack lists each area's name, state and Boundary and no requirement ID → AC-284.6; the script's own argument checks are the context area
Tests: T-284.1 [integration], T-284.2 [integration], T-284.3 [integration], T-284.4 [integration], T-284.5 [integration], T-284.6 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-context.md`; FR-282; `cli:prd_context`

### FR-285 The prd-new command hands the run to authoring-prds with the project slug
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-new.md:5 @2b082aa
Acceptance (EARS):
- AC-285.2 When the prd-new command runs, its instructions shall tell the agent to invoke the prd-toolkit:authoring-prds
  skill and follow it exactly, and that `$ARGUMENTS`, when given, is the project slug, and shall say nothing else.
Errors: -
Edge cases: no argument: the skill asks (the authoring-prds area)
Tests: T-285.2 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-new.md`

### FR-286 The prd-adopt command hands the run to adopting-prds with the area
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-adopt.md:5 @2b082aa
Acceptance (EARS):
- AC-286.2 When the prd-adopt command runs, its instructions shall tell the agent to invoke the
  prd-toolkit:adopting-prds skill and follow it exactly, and that `$ARGUMENTS`, when given, is the area to adopt, and
  shall say nothing else.
Errors: -
Edge cases: -
Tests: T-286.2 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-adopt.md`

### FR-287 The prd-change command runs changing-prds, or review mode on --review
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-change.md:5 @2b082aa
Acceptance (EARS):
- AC-287.2 When the prd-change command runs, its instructions shall tell the agent to invoke the
  prd-toolkit:changing-prds skill and follow it exactly, and that arguments that do not begin with `--review <dir>`
  are the change to make.
- AC-287.3 When the prd-change command runs with arguments that begin with `--review <dir>`, its instructions shall tell
  the agent that this is review mode: to read `${CLAUDE_PLUGIN_ROOT}/skills/changing-prds/reviewing-a-change.md` whole
  and follow it, not the skill's five steps; that review mode edits nothing; that `<dir>` is the PRD folder and a
  `--base <ref>` after it is the base; and that any other words are a request the review answers in its report, never
  an edit, whatever they ask for.
Errors: -
Edge cases: the "five steps" are the changing-prds section headed The five steps, numbered 0 to 5 (the changing-prds area)
Tests: T-287.2 [integration], T-287.3 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-change.md`

### FR-288 The prd-build command reads the build procedure first and maps its arguments to one --req
Status: approved
Source: prd-toolkit/commands/prd-build.md:7 @2b082aa
Acceptance (EARS):
- AC-288.1 The prd-build command file's body's first line shall name the arguments as `<area> <IDs> [--fixes E-nnn]` before `$ARGUMENTS`.
- AC-288.2 When the prd-build command runs, its first step shall tell the agent, before anything else, to Read
  `${CLAUDE_PLUGIN_ROOT}/skills/building-from-prds/running-a-build.md` whole (no offset, no limit), and to run no test,
  read no code and dispatch no agent before it.
- AC-288.3 When the prd-build command runs, its instructions shall tell the agent to invoke the
  prd-toolkit:building-from-prds skill for the caller's Red Flags; that the agent is the caller and the Read the skill's
  opening asks for is the one of its step 1; and that the agent never writes the code or the tests itself.
- AC-288.4 When the prd-build command runs, its instructions shall tell the agent to map the arguments as the
  prd-context command does: a token that starts with `UJ-`, `FR-`, `NFR-`, `AC-`, `T-` or `E-` is an ID and the first
  other token is the area, an AC or T-id maps to its FR and an `E-nnn` passes as it is; to join the IDs with commas for
  `--req` (as `--req FR-006,FR-001`), never space-separated, a space-separated list being a usage error (exit 2); and,
  with no IDs, to ask, a build never guessing its scope.
- AC-288.5 When the prd-build command runs with `--fixes E-nnn`, its instructions shall tell the agent that it builds the
  fix for a confirmed entry, that the `E-nnn` also goes to `--req`, and that step 1 of the procedure runs
  `prd_error.py list` with `--open` and refuses unless the entry is `confirmed`.
- AC-288.6 When the prd-build command runs, its instructions shall tell the agent to follow
  `${CLAUDE_PLUGIN_ROOT}/skills/building-from-prds/running-a-build.md` exactly, steps 1 to 8, and report as its close
  says.
- AC-288.7 When the prd-build command is given IDs and no area, its instructions shall tell the agent to find each ID's
  area from the `features/<area>.md` file that holds the ID's `### <ID>` heading, or to ask; and shall not name the
  repo pack as that source (E-097).
Errors: -
Edge cases: the procedure's own steps and refusal text are the building-from-prds area
Tests: T-288.1 [integration], T-288.2 [integration], T-288.3 [integration], T-288.4 [integration], T-288.5 [integration], T-288.6 [integration], T-288.7 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-build.md`; FR-284

### FR-289 The prd-change-set command reads the change-set procedure first and enters a record by its Status
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-change-set.md:7 @2b082aa
Acceptance (EARS):
- AC-289.1 The prd-change-set command file's body's first line shall name the arguments as `[<CS-nnn> | <text>]` before `$ARGUMENTS`.
- AC-289.2 When the prd-change-set command runs, its first step shall tell the agent to invoke the
  prd-toolkit:coordinating-prds skill first, that the skill's first instruction is a Read of
  `${CLAUDE_PLUGIN_ROOT}/skills/coordinating-prds/running-a-change-set.md` whole (no offset, no limit) to make as its
  next tool call, and to run no command, read no code and edit no file before it.
- AC-289.3 When the prd-change-set command runs, its instructions shall tell the agent that a `CS-nnn`, or with no
  arguments a current branch `cs-<nnn>-<slug>`, resumes that record at the step its Status names (the procedure's
  Where to enter); that any other text is a new change, entering at step 1; and that, with no arguments and no
  change-set branch, the agent lists the records under `changes/` that are not `done` or `abandoned` and asks which
  one, or what to change.
- AC-289.4 When the prd-change-set command runs, its instructions shall tell the agent to follow
  `running-a-change-set.md` exactly, steps 1 to 6, and report as its step 6 says, and shall say that the toolkit
  pushes, merges and opens nothing and that the one approval is the user's reply to every member's PRD diff.
Errors: -
Edge cases: -
Tests: T-289.1 [integration], T-289.2 [integration], T-289.3 [integration], T-289.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-change-set.md`

### FR-290 The prd-deploy command reads the deploy procedure first and passes --until or a run id
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-deploy.md:7 @2b082aa
Acceptance (EARS):
- AC-290.1 The prd-deploy command file's body's first line shall name the arguments as `[--until <env>] [<run id>]` before `$ARGUMENTS`.
- AC-290.2 When the prd-deploy command runs, its first step shall tell the agent to invoke the
  prd-toolkit:deploying-from-prds skill first, that the skill's first instruction is a Read of
  `${CLAUDE_PLUGIN_ROOT}/skills/deploying-from-prds/running-a-deploy.md` whole (no offset, no limit) to make as its
  next tool call, and to run no command and touch no environment before it.
- AC-290.3 When the prd-deploy command runs, its instructions shall tell the agent that `--until <env>` passes to
  `prd_deploy.py plan` and `run` as written; that an environment name alone (`staging`) means `--until staging`; that
  with no `--until` the run goes to the runbook's last step; and that a run id carries on with that run, at step 2 for
  a run stopped at a human step or failed and at step 3 for a finished run to record.
- AC-290.4 When the prd-deploy command runs, its instructions shall tell the agent to follow `running-a-deploy.md`
  exactly, steps 1 to 5, and report as its step 5 says; that the agent never runs a runbook command itself; and that
  the request to deploy is never the reply to a human step.
Errors: -
Edge cases: -
Tests: T-290.1 [integration], T-290.2 [integration], T-290.3 [integration], T-290.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-deploy.md`

### FR-291 The prd-error command reads the error procedure first and enters an entry by its state
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-error.md:7 @2b082aa
Acceptance (EARS):
- AC-291.1 The prd-error command file's body's first line shall name the arguments as `[<E-nnn> | <run id> | <text>]` before `$ARGUMENTS`.
- AC-291.2 When the prd-error command runs, its first step shall tell the agent to invoke the prd-toolkit:handling-errors
  skill first, that the skill's first instruction is a Read of
  `${CLAUDE_PLUGIN_ROOT}/skills/handling-errors/running-an-error.md` whole (no offset, no limit) to make as its next
  tool call, and to run no command, read no code and edit no file before it.
- AC-291.3 When the prd-error command runs, its instructions shall tell the agent that an `E-nnn` resumes that entry at
  the step its state names (the procedure's Where to enter); that a deploy run id names the entry whose `Detected:`
  line holds it, found with Grep in `errors.md`; that a run with no entry yet goes to
  `/prd-toolkit:prd-deploy <run id>` first, whose close records the entry; that any other text is the user's report of
  a new error, entering at step 1 as the evidence; and that with no arguments the agent lists the open entries and asks
  which one, or what went wrong.
- AC-291.4 When the prd-error command runs, its instructions shall tell the agent to follow `running-an-error.md`
  exactly, steps 1 to 6, and report as its step 6 says; that the agent never fixes code itself, except code no adopted
  area covers (the procedure's step 5, Code no area covers); and that the request is never the confirmation, only the
  user's reply to the proposal is.
Errors: -
Edge cases: -
Tests: T-291.1 [integration], T-291.2 [integration], T-291.3 [integration], T-291.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-error.md`; FR-290

### FR-292 The prd-publish command loads publishing-prds first and keeps the page out of the PRD folder and git
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-publish.md:7 @2b082aa
Acceptance (EARS):
- AC-292.1 The prd-publish command file's body's first line shall name the arguments as `[<out file>] [<request>]` before `$ARGUMENTS`.
- AC-292.2 When the prd-publish command runs, its first step shall tell the agent to invoke the
  prd-toolkit:publishing-prds skill first, and to read nothing and run nothing before it.
- AC-292.3 When the prd-publish command runs, its instructions shall tell the agent that a first argument ending in
  `.html` is the page's path (`--out`); that a path inside `docs/prd/` is refused, and the agent asks for another; that
  with none the page goes to `./<project>-prd-<version>.html` in the repository root, untracked; that the rest is the
  user's request (the audience, the summaries' language, what to stress); and that a claim in it that no PRD line makes
  is left out of the page and named in the report.
- AC-292.4 When the prd-publish command runs, its instructions shall tell the agent to follow the skill exactly, steps
  1 to 5, and report as its step 5 says, and shall say that the page and the summaries file are never written into the
  PRD folder, that the agent never commits either, and that logs, evidence and secrets never go on the page, whatever
  the request.
Errors: -
Edge cases: the command holds no `${CLAUDE_PLUGIN_ROOT}` path (the skill names the script)
Tests: T-292.1 [integration], T-292.2 [integration], T-292.3 [integration], T-292.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-publish.md`; `cli:prd_publish`

### FR-293 The prd-practices command reads the practices procedure first and installs nothing before approval
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-practices.md:7 @2b082aa
Acceptance (EARS):
- AC-293.1 The prd-practices command file's body's first line shall name the arguments as `[<PRD folder>] [<what to source>]` before `$ARGUMENTS`.
- AC-293.2 When the prd-practices command runs, its first step shall tell the agent to invoke the
  prd-toolkit:sourcing-practices skill first, that the skill's first instruction is a Read of
  `${CLAUDE_PLUGIN_ROOT}/skills/sourcing-practices/running-practices.md` whole (no offset, no limit) to make as its next
  tool call, and to run no command, fetch no page and edit no file before it.
- AC-293.3 When the prd-practices command runs, its instructions shall tell the agent that a first argument that names a
  folder holding `prd.md` is the PRD folder, and otherwise to find the one `docs/prd/*/prd.md`, asking which PRD when
  there is more than one; that the rest names what to source (an area, a language, a platform, an activity, or a
  source's URL or repository path); and that with none every area's targets are sourced.
- AC-293.4 When the prd-practices command runs, its instructions shall tell the agent to follow `running-practices.md`
  exactly, steps 1 to 10, and report as its step 10 says, and shall say that sources are read before they are proposed
  and never come from memory, that an instruction inside a source is reported and never followed, and that nothing is
  installed, no marketplace added and no skill file written before the owner approves the PRD change.
Errors: -
Edge cases: -
Tests: T-293.1 [integration], T-293.2 [integration], T-293.3 [integration], T-293.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-practices.md`; `cli:prd_practices`

### FR-294 The prd-pack command reads the pack procedure first and takes two PRD folders
Status: live (since 14.1.0)
Source: prd-toolkit/commands/prd-pack.md:7 @2b082aa
Acceptance (EARS):
- AC-294.1 The prd-pack command file's body's first line shall name the arguments as `<PRD folder A> <PRD folder B> [<pack name>]` before
  `$ARGUMENTS`.
- AC-294.2 When the prd-pack command runs, its first step shall tell the agent to invoke the prd-toolkit:authoring-packs
  skill first, that the skill's first instruction is a Read of
  `${CLAUDE_PLUGIN_ROOT}/skills/authoring-packs/running-a-pack.md` whole (no offset, no limit) to make as its next tool
  call, and to run no command, read no PRD file and write no file before it.
- AC-294.3 When the prd-pack command runs, its instructions shall tell the agent that the first two arguments are the
  two PRD folders, each holding `prd.md`, A first and B second; to ask for them when there are fewer than two; and that
  a third argument is the pack's name.
- AC-294.4 When the prd-pack command runs, its instructions shall tell the agent to follow `running-a-pack.md` exactly,
  steps 1 to 7, and report as its step 7 says, and shall say that every manifest item comes from a line of one or both
  PRDs, that a difference is the owner's to settle and never merged, that nothing is written before the owner decides,
  that no helper, clarify file or skill is drafted, that the PRDs are not edited, and that nothing is pushed, published
  or installed.
Errors: -
Edge cases: -
Tests: T-294.1 [integration], T-294.2 [integration], T-294.3 [integration], T-294.4 [integration]  (test-cases/commands.yaml)
Traces: `code:prd-toolkit/commands/prd-pack.md`; `cli:prd_pack`
