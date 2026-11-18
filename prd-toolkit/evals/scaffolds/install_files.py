"""Commit the files `prd_hooks.py install` wrote and left untracked, so a scaffold ends with a clean tree.

`prd_hooks.py install` writes `CLAUDE.md`, `docs/prd/README.md` and the PRD's own `README.md` beside the
vendored `.prd-toolkit/`. A scaffold that commits only `.gitignore` and `.prd-toolkit` leaves those untracked.
Take `untracked(repo)` before install, then call `commit_install_files(repo, before)` directly after the
commit `Vendor the PRD toolkit`: it commits, in one commit, every file untracked now that was not untracked
before install. Ignored files are never listed, so never committed. With nothing to commit it makes no commit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
from legacy import commit, git  # noqa: E402

MESSAGE = "Add the files install wrote\n\nRefs: none (no behaviour change)"
DATE = "2026-01-05T13:00:00+0000"


def untracked(repo: Path) -> set[str]:
    """The paths `git status --porcelain` lists as untracked, one per file; ignored files are not listed."""
    out = git(repo, "status", "--porcelain", "-z", "--untracked-files=all")
    return {entry[3:] for entry in out.split("\0") if entry.startswith("?? ")}


def commit_install_files(repo: Path, before: set[str]) -> list[str]:
    """Commit every file untracked now and not in `before`, as one commit; return the files, sorted."""
    files = sorted(untracked(repo) - before)
    if files:
        commit(repo, MESSAGE, "--", *files, date=DATE)
    return files
