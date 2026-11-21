---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*?\bgit\s+(?:-[Cc]\s+(?:\\"(?:[^"\\]|\\.)*?\\"|[^\s"\\]+)\s+)*restore\s(?:[^"\;&|]|\\.)*?errors\.md'
min: 1
---

The ledger is put back with `git restore` of `errors.md` (`--staged --worktree` or `-S -W`, in either order), as step 6
says: a `sed`, a `git checkout --`, a `cp` or a Write that restores the file leaves no such call. The match stops at
`;`, `&` and `|`, so a `git restore` of another path chained before a mention of `errors.md` does not count.
