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

An error-class card showed the entry's class and its Diagnosis, written for someone who has read the code, and
offered two answers, Confirm and Correct, so an owner who did not follow the diagnosis could only confirm or
guess. FR-254 shows the entry's `Explanation:` line (error-reopen FR-253) first and offers a third answer, a
question, which writes nothing and leaves the gate pending. Its code is in `prdlint/gates.py` and
`templates/gates/inbox.html` (area `gates`); what they do is stated here.

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

### FR-254 An error-class card explains the class and takes a question
Status: approved
Flow: 1. the inbox lists an `error-class:<E-id>` gate → 2. its card holds the entry's explanation → 3. the
      owner confirms, corrects or asks a question → 4. a question is logged for `wait` and changes nothing else
Acceptance (EARS):
- AC-254.1 The card of a gate `error-class:<E-id>`, the object `prdlint.gates.card(gate, prd, root, rel)`
  returns, shall hold after `diagnosis` and before `waiting` the key `explanation`: the text after
  `Explanation:` on the entry's first line that starts with `Explanation:`, with the white space around it
  removed, or null when the entry has no such line.
- AC-254.2 The gate `error-class:<E-id>` shall offer the choices `confirm`, `correct` and `question`, in that
  order, in its `choices` as `prd_gates.py list <prd_dir> --json` prints them and as its card holds them.
- AC-254.3 When an `error-class:<E-id>` gate is answered with the choice `question` and a reply that is not
  empty, through `prd_gates.py answer <prd_dir> error-class:<E-id> --choice question --reply <words>` or the
  inbox's answer `{"choice": "question", "words": <words>, …}`, the gates command shall leave `errors.md` byte
  for byte as it was, make no commit, append one line to the answer log with `choice` `question` and the
  reply, and give the result `{"stdout": ["recorded a question for error-class:<E-id>"], "exit": 0}`; the
  inbox's reply is `Ask a question: <words> (form)`, `<words>` with the white space around it removed.
- AC-254.4 While an `error-class:<E-id>` gate has been answered with the choice `question`, the gates command
  shall list it as before the answer, in `prd_gates.py list` and in the inbox's listing.
- AC-254.5 When `prd_gates.py wait <prd_dir> error-class:<E-id>` is running and the gate is answered with the
  choice `question`, the gates command shall exit 0 and print the outcome whose `choice` is `question` and
  whose `reply` is that answer's reply.
- AC-254.6 If the inbox's answer to an `error-class:<E-id>` gate has the choice `question` and words that are
  empty or only white space, the inbox shall refuse it with status 400 and the error
  `refused: Ask a question needs your words`, run nothing and log nothing.
- AC-254.7 The decision inbox page (`templates/gates/inbox.html`) shall show on an error-class card whose
  `explanation` is a string that text first, then the card's `diagnosis` inside a `details` element whose
  `summary` reads `Diagnosis`; on one whose `explanation` is null, the `diagnosis` as before this requirement;
  and on each error-class card a button `Ask a question` that sends the choice `question` with the words typed
  on the card; each text inserted as text, never as HTML.
Errors: -
Edge cases: a question names no class, so `--class` with `--choice question` is refused as a class is with
`confirm` → AC-254.3; the gate's `question` text is unchanged → AC-254.2; the owner's next answer, a
confirmation or a correction, is run and committed as before → AC-254.4; a `wait` started after the question
was logged waits for the next answer → AC-254.5; a correction to `not a defect` is run as one to any other
class (error-reopen AC-253.5)
Tests: T-254.1 [integration], T-254.2 [integration], T-254.3 [integration], T-254.4 [integration], T-254.5 [integration], T-254.6 [integration], T-254.7 [integration], T-254.8 [unit]  (test-cases/inbox-cards.yaml)
Traces: cli:prd_gates; error-reopen FR-253
