"""Helpers for the commands cases (docs/prd/prd-toolkit/test-cases/commands.yaml).

The names follow the case file's header: NAMES, CMD, FM, BODY, STEP, PARA and flat.
Every helper reads the checkout at REPO; only ls_files runs a command (git).
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

# <repo>, found as in testing.md's paragraph on the release cases:
# parents[0] is prd, [1] tests, [2] prd-toolkit, [3] the repository root.
REPO = Path(__file__).resolve().parents[3]

NAMES = [
    "prd-adopt",
    "prd-build",
    "prd-change-set",
    "prd-change",
    "prd-context",
    "prd-deploy",
    "prd-error",
    "prd-new",
    "prd-pack",
    "prd-practices",
    "prd-publish",
    "prd-status",
]

WHICH_SCRIPT = "**Which script.**"

_DROPPED = (
    "PYTHONIOENCODING",
    "PYTHONPATH",
    "PYTHONHOME",
    "PRD_LINT_CI",
    "PRD_HELP_FILE",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
)


def _bare(line: str) -> str:
    return line.rstrip("\r\n")


def cmd(name: str) -> str:
    """CMD(<name>): the text of <repo>/prd-toolkit/commands/<name>.md, read as UTF-8."""
    path = REPO / "prd-toolkit" / "commands" / f"{name}.md"
    if not path.is_file():
        pytest.fail(f"{name}: {path} is not a file")
    return path.read_bytes().decode("utf-8")


def _lines(name: str) -> list[str]:
    return cmd(name).splitlines(keepends=True)


def first_line(name: str) -> str:
    lines = _lines(name)
    return _bare(lines[0]) if lines else ""


def _closing(name: str) -> tuple[list[str], int]:
    lines = _lines(name)
    for i in range(1, len(lines)):
        if _bare(lines[i]) == "---":
            return lines, i
    pytest.fail(f"{name}: no line `---` after the first line, so FM and BODY are not defined")


def fm(name: str) -> list[str]:
    """FM(<name>): the lines after the first line, up to and not including the next `---` line."""
    lines, i = _closing(name)
    return [_bare(line) for line in lines[1:i]]


def body(name: str) -> str:
    """BODY(<name>): the text after the closing `---` line."""
    lines, i = _closing(name)
    return "".join(lines[i + 1:])


def body_lines(name: str) -> list[str]:
    return [_bare(line) for line in body(name).splitlines(keepends=True)]


def step(name: str, n: int) -> str:
    """STEP(<name>, <n>): from the first line starting "<n>. " to the next starting "<n+1>. "."""
    lines = body_lines(name)
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{n}. ")), None)
    if start is None:
        pytest.fail(f"{name}: BODY has no line that starts with {f'{n}. '!r}, so STEP({name}, {n}) is not defined")
    end = next(
        (j for j in range(start + 1, len(lines)) if lines[j].startswith(f"{n + 1}. ")),
        len(lines),
    )
    return "\n".join(lines[start:end])


def paragraphs(name: str) -> list[str]:
    """The paragraphs of BODY(<name>): runs of lines between blank (empty or white-space-only) lines."""
    found: list[str] = []
    run: list[str] = []
    for line in body_lines(name):
        if line.strip() == "":
            if run:
                found.append("\n".join(run))
                run = []
        else:
            run.append(line)
    if run:
        found.append("\n".join(run))
    return found


def which_script_paragraphs(name: str) -> list[str]:
    return [p for p in paragraphs(name) if p.startswith(WHICH_SCRIPT)]


def para(name: str) -> str:
    """PARA(<name>): the paragraph of BODY(<name>) whose first line starts with **Which script.**."""
    found = which_script_paragraphs(name)
    if len(found) != 1:
        pytest.fail(f"{name}: BODY holds {len(found)} paragraphs that start with {WHICH_SCRIPT}, not one")
    return found[0]


def flat(text: str) -> str:
    """flat(x): every run of white space replaced by one space, leading and trailing white space removed."""
    return re.sub(r"\s+", " ", text).strip()


def git_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in _DROPPED:
        env.pop(key, None)
    return env


def ls_files(rel: str) -> list[str]:
    """The lines `git -C <repo> ls-files <rel>` prints, sorted."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", rel],
        capture_output=True,
        env=git_env(),
    )
    if r.returncode != 0:
        pytest.fail(f"git ls-files exited {r.returncode}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return sorted(r.stdout.decode("utf-8").splitlines())


def missing(text: str, wanted: list[str]) -> list[str]:
    """The strings of `wanted` that are not substrings of `text`."""
    return [w for w in wanted if w not in text]


def present(text: str, unwanted: list[str]) -> list[str]:
    """The entries of `unwanted` found in `text`: a plain substring, or with a "re:" prefix a re.search."""
    hits = []
    for u in unwanted:
        if u.startswith("re:"):
            if re.search(u[3:], text):
                hits.append(u)
        elif u in text:
            hits.append(u)
    return hits


def known_failure(problems: list[str], symptom_seen: bool, symptom: str) -> None:
    """End a known-failing case: pass through when nothing failed (strict xfail reports the unexpected
    pass), pytest's own expected-failure exception when the case's symptom is seen, else a plain failure."""
    if not problems:
        return
    if symptom_seen:
        pytest.xfail(f"known failure seen: {symptom}")
    raise AssertionError("not the known failure: " + "; ".join(problems))
