---
description: Propose a pack from what two adopted PRDs share, each item with the PRD lines it comes from and each difference with both sides, for the owner to decide; then write it into the plugin the owner names, check it, and commit it on a new branch, pushing and installing nothing (prd-toolkit)
---

Write a pack from two adopted PRDs. Arguments, `<PRD folder A> <PRD folder B> [<pack name>]`: $ARGUMENTS

1. Invoke the prd-toolkit:authoring-packs skill first. Its first instruction is a Read of
   `${CLAUDE_PLUGIN_ROOT}/skills/authoring-packs/running-a-pack.md`, whole (no offset, no limit):
   make it your next tool call. Run no command, read no PRD file and write no file before it.
2. The first two arguments are the two PRD folders, each holding `prd.md`, A first and B second.
   With fewer than two, ask for them. A third argument is the pack's name.
3. Follow `${CLAUDE_PLUGIN_ROOT}/skills/authoring-packs/running-a-pack.md` exactly, steps 1 to 7,
   and report as its step 7 says. Every manifest item comes from a line of one or both PRDs; a
   difference is the owner's to settle, never merged; nothing is written before the owner decides;
   no helper, clarify file or skill is drafted; the PRDs are not edited; and nothing is pushed,
   published or installed.
