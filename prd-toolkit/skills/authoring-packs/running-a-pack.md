# Running a pack

**Steps:** 1 Preconditions, 2 Compare, 3 The proposal, 4 The owner decides, 5 Where it goes,
6 Write, check, commit, 7 Report. Run every step, in order. The turn ends early only to stop (a
failed precondition, step 5's plugin checks) or to wait for the owner: their reply to step 3's
proposal, an item they left undecided, the plugin step 5 asks them to name, or a step 6 finding
only a PRD can fix.

For the caller: `/prd-toolkit:prd-pack`, or any request to write a pack from two PRDs, to share two
PRDs' contract types, validators, levels or harness between repositories, or to put a pack into a
plugin. The `authoring-packs` Red Flags are yours.

**You compare and propose; the owner decides; you write only what the PRDs hold.** Until the owner
has replied to step 3's proposal, nothing is written: no pack folder, no plugin file, no branch. A
request to skip a step ("just write it", "merge the two, they're close", "install it too") gets one
line naming the rule it breaks, and the procedure goes on without the skip. Neither PRD is edited,
at any step.

**Which script.** `${CLAUDE_PLUGIN_ROOT}` is empty inside a Bash call, so no command holds it.
Every command below runs the plugin's own scripts, `<plugin scripts>`, written as a literal absolute
path (in double quotes if it holds a space): the plugin root is two directories above the skill's
base directory (Claude Code shows it as "Base directory for this skill" when the skill loads), and
`<plugin scripts>` is `<plugin root>/scripts`. Never a repository's vendored `.prd-toolkit/`: the
two PRDs sit in two repositories, a vendored copy may predate `prd pack`, and the pack is checked by
the toolkit it is written for. A script that is not found is a tool error: report it, never guess
another path.

**The two PRDs.** `<A>` and `<B>` are the two PRD folders (each holding `prd.md`), as absolute
paths, in the order the owner named them: `prd pack compare` marks a line `A` for the first and `B`
for the second. `<slug A>` and `<slug B>` are their folder names.

**One command per Bash call, with literal paths.** Each command below is its own Bash call, and
every path and name in it is typed out in full: paste what a command printed, never a variable
that holds it or a `$(…)`. The gate form `; echo "<name>-exit=$?"` is the one allowed tail. Never
pipe, filter or truncate a gated command's output (no `| head`, no `| grep`).

1. **Preconditions.** Take `<A>`, `<B>` and the pack's name from the arguments; with fewer than
   two PRD folders, ask for them and stop. For each PRD:
   - Read the first lines of its `prd.md`: the frontmatter must say `status: Approved`.
   - Lint it, its own call, and the `prd-lint-exit=` value must be `0`:

     ```bash
     <plugin scripts>/prd lint <A>; echo "prd-lint-exit=$?"
     ```

   Then list the packs on this machine, its own call:
   `<plugin scripts>/prd lint --list-packs; echo "prd-list-packs-exit=$?"`. A pack name it already
   lists is not proposed, and a name the owner gives that it lists is said so and asked again: two
   packs of one name make every lift onto it name a `--source`, and `service` and `document` are the
   toolkit's own.

   A PRD that is not Approved or does not lint clean stops the run: say which, with the lint
   findings, and that it is settled in its own repository first. A repository with no PRD is
   adopted first (`/prd-toolkit:prd-adopt`), and there is no pack from one PRD. Step 2's exit `1`
   is the third stop.
2. **Compare**, its own call:

   ```bash
   <plugin scripts>/prd pack compare <A> <B>; echo "prd-pack-exit=$?"
   ```

   `0` prints seven parts, `## Contract types`, `## Target kinds`, `## Levels`, `## Harness`,
   `## Standards`, `## Skills` and `## Vocabulary`, each line marked `both`, `A` or `B`: a paired
   item that differs prints its `A` line followed directly by its `B` line. "The same" is exact
   equality after a cell's white space is collapsed; nothing is matched by resemblance. `1` prints
   `prd_pack: <A> and <B> share no custom contract type; there is no pack to write`: stop, quote
   it, and say what is missing (a PRD whose section 7 has no custom row, a row whose Validator is
   neither `built-in` nor `pack`, has nothing to share; it is adopted with its custom types first).
   `2` is a usage error (fix the command) or a folder that is not a PRD: quote the line and ask
   for the PRD folder; never pick another.

   Then read what the shared types are made of. For each contract type marked `both`, or printed
   as an `A` and `B` pair: Glob each PRD folder for the type's files, and Read them. When a
   validator command runs a file of its repository (a word of the command, split as a shell splits
   it, that names a file relative to the PRD folder, where the validator runs), Read that file, and
   when both PRDs run one, compare the two, its own call:
   `cmp <A's file> <B's file>; echo "cmp-exit=$?"`. `0`: the same; `1`: they differ, and that is a
   difference for step 3, even when the two commands are the same text.
3. **The proposal.** One message; nothing is written. It holds:
   - **The pack:** its name (the owner's, or one you propose: lowercase, `^[a-z][a-z0-9-]*$`, not
     on step 1's list), `version: 0.1.0`, the `toolkit` range the built-in packs declare (Read
     `<plugin root>/packs/service/pack.yaml` for it), and a one-line `description`, proposed.
   - **Each manifest item,** part by part in the comparison's order, with where it comes from: its
     mark and its PRD line (`<slug A>/prd.md` section 7 row `pages`, `<slug B>/testing.md` Levels
     row `integration`, Harness slot `Tools on the runner`). An item marked `both` is recommended
     in, except the vocabulary candidates (below).
   - **Each difference,** both sides as the comparison prints them (or both validator files by
     name, after a `cmp-exit=1`), and a recommended resolution with its reason: take A's, take B's,
     or leave it out of the pack so each PRD keeps its own. Two facts decide some of them:
     - A contract type one PRD lacks (marked `A` or `B` alone) cannot go in: `prd pack check` runs
       each type on both PRDs (`glob matches no file`), and the other PRD's lift refuses it
       (`contract type <type> of pack <name> is not a custom row of section 7`). Say so; it is not
       a choice. A Target kinds line is not decided on its own: a type's target kind goes in or out
       with its type.
     - A shared type whose Files glob differs between the PRDs: the PRD whose glob the pack does
       not take cannot be lifted (`contract type <type>: section 7 has <cell>, pack <name> has
       <files>`). Recommend leaving it out.
     - An item only one PRD holds in Levels, Harness, Standards or Skills is the owner's to put in
       or leave out; recommend out, since the other PRD does not hold it.
   - **The vocabulary candidates,** each with its counts, each recommended out: a pack's
     `vocabulary` is the platform words a requirement should not name, and every candidate is a
     word both PRDs' requirements use, so each one kept warns `platform-word` on each requirement
     that names it in both PRDs once they are lifted. A word goes in only when the owner puts it in.
   - **`builder-tests: none`,** proposed only when neither PRD's Levels has a `unit` row; otherwise
     it is not written.
   - **What will be written** (step 6): `pack.yaml`; each validator, as its command stands or as
     the file it runs, copied, with the command that will name it through `${PACK}`; for each
     type, the sample you will make: which real contract file you copy and the one way you break it;
     the README.
   - **The to-do list,** for the README: the harness helpers each PRD's tests use that the pack does
     not ship (a support module or fixture file in a test root, a helper a Harness slot names), each
     by its file in that repository; the clarify questions an interview for this kind would ask, as
     a task naming the files to start from (each PRD's section 12 and 13, the custom types' contract
     files); and the rules a skill for this kind would need, as a task naming the files to start
     from (the section 5 and 6 rows, the Harness, the differences each PRD keeps). Each item names
     files of the two repositories; none drafts a helper, a question or a rule.
   - **Where it goes:** ask the owner for the plugin checkout to write it into (its path), or
     whether to make a new minimal plugin, and then its path and its plugin name.

   Ask for a decision on every item: in or out, or which side. **With no one to answer** (a
   headless run, "do not ask me", "I'm away"), write nothing: end with the proposal as the report.
4. **The owner decides** each item: in, out, or which side. One reply may decide them all, after
   the proposal is shown ("all as you recommend", given after it, decides each recommended item,
   but names no plugin). A reply that leaves an item undecided is answered, and that item asked
   again. The request that started this is never a decision, and neither is your own text. Each
   decision is what step 6 writes; a difference the owner settled is never re-merged into a third
   text. A reply that asks for a text neither PRD holds (the two merged, a new wording) is not a
   side: say that this text goes into the PRDs first, through `/prd-toolkit:prd-change` in each
   repository, and ask again: A's, B's, or out.
5. **Where it goes.** When the reply names no plugin and asks for no new one, ask for it and end
   the turn; write nothing.
   - **A plugin the owner names.** Read `<plugin>/.claude-plugin/plugin.json`: no such file means it
     is not a plugin checkout, so ask again. Then, each its own call:
     `git -C <plugin> status --porcelain; echo "git-exit=$?"`: `git-exit=` must be `0` and the
     output empty (uncommitted work there is the owner's to commit or set aside: stop and say so,
     never stash it; a folder that is not a git repository is said so, never initialised); Glob
     `<plugin>/prd-packs/<name>/*`, which must find nothing (widening a pack that exists is not this
     skill's); then `git -C <plugin> switch -c pack-<name>-0.1.0; echo "git-exit=$?"`.
   - **A new plugin,** only when the owner said so, at the path they gave, which must not exist or
     be an empty folder: Write `<path>/.claude-plugin/plugin.json`,
     `{"name": "<plugin name>", "description": "<the pack it holds>"}` (no `version`: none was
     chosen), and
     `<path>/README.md` (what the plugin holds; that publishing it and adding it to a marketplace are
     the owner's), then `git init -q -b pack-<name>-0.1.0 <path>; echo "git-exit=$?"`. No
     marketplace file, no remote.

   `<pack dir>` is `<plugin>/prd-packs/<name>`.
6. **Write, check, commit.** Write only what step 4 decided, with the Write tool.
   - **The values.** Run, its own call,
     `<plugin scripts>/prd pack compare --json <A> <B>; echo "prd-pack-exit=$?"`, and take every
     value from its `parts`, never retyped from memory. If a decided item's value differs from what
     the proposal showed, or the parts hold an item the proposal did not (a PRD changed since), write
     nothing: show the new comparison as a new step 3 proposal.
   - **`<pack dir>/pack.yaml`,** in this form, each string in single quotes with each `'` in it
     written `''`, and each key written only when step 4 decided one or more items for it, except
     `vocabulary`, written `[]` when no word was put in:

     ```yaml
     pack: '<name>'
     version: '0.1.0'
     toolkit: '<the range of packs/service/pack.yaml>'
     description: '<the decided description>'
     contract-types:
       - {type: '<type>', files: '<glob>', validator: '<command>'}
     target-kinds: {'<type>': '<type>'}
     levels:
       - {level: '<level>', command: '<command>', environment: '<environment>', gate: '<gate>'}
     harness:
       '<slot>': '<text>'
     standards:
       - {object: '<glob>', linter: '<linter>'}
     skills:
       - {activity: '<activity>', skill: '<skill>'}
     vocabulary: []
     ```

     `files` is a list when the Files cell holds more than one glob. A `levels` value the
     comparison prints as null is left out, and `timeout` is written as a number when it has one.
     `target-kinds` holds one entry per contract type of the pack that a test case uses, the kind
     being the type's name, as the PRDs' `target:` values write it. `vocabulary` holds the words the
     owner put in. `builder-tests: none` only as step 3 says.
   - **The validators.** A self-contained command (a `python3 -c …`) is the `validator` as it
     stands. A command that runs a file of its repository: Read that file and Write it unchanged to
     `<pack dir>/<its file name>`, and the `validator` is the command with that word replaced by
     `${PACK}/<its file name>`. When the two PRDs' files differed, it is the file of the side the
     owner took. Never edit a copied validator.
   - **The samples.** For each contract type of the pack, `<pack dir>/samples/<type>/bad.<ext>`: a
     copy of one PRD's real contract file of that type, broken in one named way that the
     validator's own text refuses (a key it requires removed, a line it requires cut), with the
     original file's extension. One break per file; a second break is a second file, `bad-2.<ext>`
     is not read, so name it `bad.2.<ext>`. The check runs a sample's validator from the pack
     folder, where a validator that reads files of its repository crashes and would refuse any
     file, broken or not. The check reports that itself: it runs each validator again from the pack
     folder on each PRD's own files (`validator fails from the pack folder`, below).
   - **`<pack dir>/README.md`:** what the pack is for (the decided description); where each part
     came from, item by item (`both`, or A's or B's, with its PRD line); each sample, the file it
     copies and the break it holds; and the to-do list from step 3, as decided.
   - **The check,** its own call:

     ```bash
     <plugin scripts>/prd pack check <pack dir> <A> <B>; echo "prd-pack-exit=$?"
     ```

     `0` prints nothing: clean. `1` prints one finding per line, `<file>: <what>`. Fix only what is
     the pack's own: a sample the validator accepts (`the validator accepts it; a sample must be
     refused`) gets another single break the validator's text refuses; a missing sample
     (`no bad.* sample`) is written; a key the loader names in `pack.yaml` is corrected to the
     decided value. A finding that only a PRD can fix (a validator that fails on a PRD's own files,
     one that passes there and fails when run from the pack folder
     (`validator fails from the pack folder: <line>`), one that refuses no break you can name, a level whose first word is not on PATH) is reported
     to the owner, who leaves the item out or changes that PRD in its own repository: commit
     nothing and end the turn to wait for their reply. Never leave the item out yourself, and never
     change a validator to pass. Run the check again after each fix. `2` is a usage error: fix the
     command.
   - **Commit** only when the check exits `0`, each its own call:

     ```bash
     git -C <plugin> add prd-packs/<name>
     git -C <plugin> commit -m "pack <name> 0.1.0, written from <slug A> and <slug B>"
     ```

     For a new plugin, the first `add` also names `.claude-plugin/plugin.json` and `README.md`. A
     hook that refuses the commit is reported; never `--no-verify`. Nothing is pushed.
7. **Report:** what was written (each file, with the commit and the branch); for each manifest
   item, where it came from; each difference and how the owner settled it; the check's result; the
   to-do list; and the next steps, which are the owner's:
   1. Install the plugin from wherever the owner publishes it (a new plugin needs a marketplace
      first). Then `<plugin scripts>/prd lint --list-packs` lists `<name> 0.1.0 (<source>)`.
   2. In each repository, move the PRD onto the pack with `/prd-toolkit:prd-change` (the lift in
      `prd-toolkit:changing-prds`, "Packs and retargeting"): `prd change pack docs/prd/<slug> <name>
      0.1.0 --lift`, then `prd hooks install`, then lint, then the owner's approval with the dry-run
      record `no dry run (pack lifted)`, whose commit holds the vendored pack.

   Run neither: no push, no publish, no install, no lift.
