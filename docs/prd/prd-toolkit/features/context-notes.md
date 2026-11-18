<!-- Format: references/prd-format.md, "Requirement blocks". -->

# context-notes: the text a features file gives before its first block

A features file may say, between its title and its first block, what its blocks share: the words their criteria
use, the module the area is, the files the same build edits. The context pack of an area
(`prd context <prd_dir> --area <area>`) printed the blocks and none of that text, so a builder working from the pack missed the definitions its
criteria used and read the file outside the pack (E-028). This area adds that text to the pack as a part of its
own. One module says what the text is and how it prints, `prd-toolkit/scripts/prdlint/contextnotes.py`; the same
build makes `prd_context.py` and `prdlint/context.py` (area `context`, which is not adopted) call it, and what the
pack prints is stated here.

Words used below. A features file's **title line** is its first line that starts with `# `. Its **area notes**
are the lines after the title line and before the file's first line that starts with `### ` (to the end of the
file when there is none), less the `Target:` line (a line starting `Target:` at column 0), less every HTML
comment that fills whole lines (a line that starts with `<!--` once leading white space is removed, and the lines
after it up to and including the first line that ends with `-->` once trailing white space is removed; the same
line when it holds both), and less the empty lines (empty or only white space) at the start and at the end of
what is left. Every other line is kept as it stands, its order, its indentation and the empty lines between kept
lines included. A file with no title line has no area notes, and neither does one where nothing is left.

### FR-072 The context pack prints an area's notes
Status: verified
Source: prd-toolkit/scripts/prdlint/contextnotes.py:1 @3a021bf
Acceptance (EARS):
- AC-072.1 When `prd_context.py <prd_dir> --area <area>` prints a pack, with `--for decide` or `--for implement`
  and with or without `--req`, and the area's features file holds area notes, the pack shall hold the part
  `## Area notes` directly before the part `## Requirements`: in the text output the line `## Area notes`, one
  empty line, the lines of the area notes, and one empty line; in `--json` one entry of `parts` directly before
  the first entry whose title is `Requirements`, with the title `Area notes`, the id null, the file
  `features/<area>.md`, the line the number of the notes' first line in that file, the text the notes' lines
  joined by a newline, stale false, counted true and moved null, its keys in the order of every part entry
  (`title`, `id`, `file`, `line`, `text`, `stale`, `counted`, `moved`).
- AC-072.2 If the area's features file holds no area notes, the pack shall be, byte for byte, the pack
  `prd_context.py` printed before this area for the same command and files.
Errors: -
Edge cases: a file whose lines before the first block are only its title, empty lines, HTML comments and the `Target:` line has no area notes → AC-072.2; a comment inside a line of prose is part of that line and kept → AC-072.1; the repository pack (no `--area`) is unchanged; nothing else of the pack moves, so every other part keeps its place and text → AC-072.1
Tests: T-072.1 [integration], T-072.2 [integration]  (test-cases/context-notes.yaml)
Traces: cli:prd_context; E-028
