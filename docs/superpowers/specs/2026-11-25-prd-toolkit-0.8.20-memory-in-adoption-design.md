# prd-toolkit 0.8.20: Claude memory in adoption

Approved by the owner 2026-11-25 (approach A + C).

## Intent

An adoption reads the code, its history, its docs and the live system. It never reads Claude Code's
auto-memory, where the owner's sessions have recorded what the repo cannot show: which login publishes,
the order of a release, a step that needs a browser, a rule clients rely on. Two adoptions running
now (a release area, the sqlanvil.com PRD) leave runbook markers open, or write the wrong steps, that a
memory note already answers. Adoption should use that knowledge without letting it bypass the owner.

## Goals

- The adopter finds the memory notes relevant to the repo and the area, and builds a digest.
- **C:** the extractor gets the digest. Code that contradicts a note is an APPARENT BUGS entry; a note
  the code cannot show is a QUESTION. A note is never a `Source:` and never evidence of behaviour.
- **A:** the adopter proposes, from the digest, answers to bootstrap `[NEEDS CLARIFICATION]` markers
  (owner, environments, runbook steps only memory holds) and shows each requirement's notes at
  Confirm. It writes an answer only on the owner's yes.

## Non-goals

- Writing to memory; reading engram or any store other than Claude Code's auto-memory files.
- Memory in `changing-prds`, `handling-errors` or `deploying-from-prds`.
- A script to select notes: relevance is judgment, and the index is already in the session's context.

## Anti-goals (a failure even if it works)

- A note confirms a requirement, or closes a marker, without the owner's word.
- A note's text, a secret or a personal detail lands in a committed file.
- The adopter settles two conflicting notes by picking the newer.
- Adoption stops or nags because there is no memory.

## Constraints

- prd-toolkit is public: the rules name Claude Code's auto-memory layout only (`MEMORY.md` index plus
  one file per note with `name`, `description`, `metadata.type` frontmatter; `modified` when present).
- Memory is keyed by the directory a session starts in, not by repo: one directory can hold notes for
  many repos (184 notes under one parent here), so selection filters by repo, slug, packages, domains
  and the area's Boundary paths.
- Notes go stale and correct themselves; every digest entry carries its note's date.
- The skill's core rule stands: the code says what the system does, only the owner says what it should do.

## Approaches

- **A. Propose only** (picked): notes become proposals and questions, each citing its note.
- **B. Memory as a Source kind** (rejected): fills runbooks fastest, but stale notes would enter as
  requirements and lint would need a non-code Source.
- **C. Feed the extractor** (picked, with A): lets the extractor flag code that contradicts the owner's notes.

## The design

**Where.** The memory directory the session's system prompt names; also
`~/.claude/projects/<repo root, every / as ->/memory/` when that differs and exists; also a directory
the user names. Read `MEMORY.md` first, then whole every note whose name, description or body names the
repo, its slug, its packages or domains, or a path in the area's Boundary. None found: say so in one
line and go on.

**The digest.** Per note: its file name, its date (`modified`, else the file's mtime), its type, and the
quoted claims that bear on the area. It lives in the chat or the scratchpad, never in the repository.
Two notes that disagree go in as one conflict; the adopter never picks one.

**Extractor (C).** A new `<MEMORY>` slot in `extract-prompt.md`: the digest, or `none`. "Send nothing
else" gains its one exception, the digest. Rules: a note is the owner's past word, possibly stale, never
evidence of behaviour and never a `Source:`; code that contradicts a note is an APPARENT BUGS entry whose
Diagnosis names the note (`memory note <file> (<date>)`); a note the code does not show is a QUESTION;
FILES READ lists no note (the extractor reads none; it gets the digest).

**Adopter (A).** Bootstrap: for a marker a note answers, propose the answer with the note and its date;
on the owner's yes write it in plain words, otherwise the marker stays (headless: it stays). Runbook steps
only memory holds are proposed as `(actor: human)` steps the same way. Confirm: each requirement is shown
with its `Source:` and the digest entries that touch it; a note confirms nothing.

**Privacy.** A committed file gets only what the owner confirmed, in plain words, and an `E-nnn` diagnosis
that paraphrases the claim. Never a note's text verbatim, a secret, a token or a personal detail.

**Discipline.** Red Flags: "the memory note says so, so it is confirmed"; "cite the note as the Source";
"the newer note wins". Common Rationalizations rows for each.

## Tests

- Unit pins in `tests/test_adopting_skill.py` for the new skill and prompt text.
- Eval `adopting-memory-conflict`: the bare notes repo plus a fixture memory directory with a note that
  says note ids start at 0 (the code starts at 1, and nothing in the repo says otherwise), a note for
  another project holding a token, and no note answering anything else. Graders: the skill fired; an
  `errors.md` entry names a memory note; no `Source:` cites memory; no requirement is `live`; no Write or
  Edit carries the other project's token. RED on 0.8.19's skill first, then GREEN.

## Left to the builder

The exact wording of the skill and prompt text, within the rules above; the eval prompt's phrasing.
