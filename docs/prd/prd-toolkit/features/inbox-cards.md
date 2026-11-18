<!-- Format: references/prd-format.md, "Requirement blocks". -->

# inbox-cards: one card for an error entry that several worktrees hold

The decision inbox (`prd gates serve <prd_dir>`) lists the gates of the PRD folder in every worktree of the
repository whose checkout holds it, one group per worktree: the worktree the inbox was started from first, then
the others in the order `git worktree list` gives, as before this area. An entry that is `proposed` in a commit
two branches share is `proposed` in both worktrees, so the inbox showed its `error-class:<E-id>` card once per
worktree, and each answer was a commit of the same `errors.md` text on each branch (E-023). This area shows that
card once, in the first group whose PRD folder holds the entry; its answer is committed on that worktree's branch
only, and the other branches get it when they merge. One module says which `error-class` gates a group leaves
out, `prd-toolkit/scripts/prdlint/inboxcards.py`; the same build makes the inbox's listing in `prdlint/gates.py`
(area `gates`, which is not adopted) call it, and what the listing does is stated here. An entry's title is the
text after `### <E-id> ` on its heading line, and its `Detected:` value the text after `Detected:` on its
`Detected:` line, both with surrounding white space removed.

### FR-071 The inbox shows an error entry's card in the first worktree that holds it
Status: verified
Source: prd-toolkit/scripts/prdlint/inboxcards.py:6 @ba1736f
Acceptance (EARS):
- AC-071.1 When the inbox lists its gates, it shall leave the gate `error-class:<E-id>` out of a group when the
  PRD folder of an earlier group holds an `errors.md` entry with that ID, the same title and the same `Detected:`
  value, whatever that entry's state there, and shall list every other gate of the group as before this area; an
  entry of that ID with another title or another `Detected:` value is another entry and leaves nothing out.
- AC-071.2 When the owner answers an `error-class` card in the inbox, the inbox shall run the answer in the
  worktree of that card's group alone, as before this area: the commit `docs(prd): confirm <E-id>` on that
  worktree's branch, every other worktree's files and branch left as they were.
- AC-071.3 The command `prd_gates.py list <prd_dir>` shall list the gates of the PRD folder it is given as before
  this area, whatever another worktree's PRD folder holds.
Errors: -
Edge cases: the inbox started from a worktree whose PRD folder holds no such entry shows the card in the first other group that holds it → AC-071.1; once the answer is committed in the first group, the entry there is `confirmed` and the later groups still leave the card out, while that group holds the entry → AC-071.1, AC-071.2; a group listed with an error (its PRD folder could not be read) holds no entry for this rule; a `deploy-step` gate is listed once, in the first group, as before; the approval, adoption and signoff gates are unchanged; `prd status` and `prd gates list --worktrees` are unchanged → AC-071.3
Tests: T-071.1 [integration], T-071.2 [integration], T-071.3 [integration], T-071.4 [integration], T-071.5 [integration]  (test-cases/inbox-cards.yaml)
Traces: cli:prd_gates; E-023
