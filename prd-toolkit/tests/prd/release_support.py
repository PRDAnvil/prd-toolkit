"""Shared helpers for the release area's black-box tests (test-cases/release.yaml).

Every path and name below comes from the conventions at the top of
docs/prd/prd-toolkit/test-cases/release.yaml and from testing.md's Harness.
"""

import fnmatch
import json
import os
import re
import stat
import subprocess
from pathlib import Path

# prd-toolkit/tests/prd/release_support.py -> the repository root
REPO = Path(__file__).resolve().parents[3]

# Subprocess environment (testing.md Harness): the runner's environment minus these.
_DROPPED = ("PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE")
# The git variables the area's sh and git runs drop as well (T-274.x note).
_GIT_DROPPED = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR")


def read_text(rel):
    """A file of the checkout at <repo>, read as UTF-8."""
    return (REPO / rel).read_text(encoding="utf-8")


def market():
    """MARKET = <repo>/.claude-plugin/marketplace.json parsed."""
    return json.loads(read_text(".claude-plugin/marketplace.json"))


def entry():
    """ENTRY = the one element of MARKET["plugins"]."""
    plugins = market()["plugins"]
    assert isinstance(plugins, list) and len(plugins) == 1, f"MARKET['plugins'] is not one entry: {plugins!r}"
    return plugins[0]


def plugin():
    """PLUGIN = <repo>/prd-toolkit/.claude-plugin/plugin.json parsed."""
    return json.loads(read_text("prd-toolkit/.claude-plugin/plugin.json"))


def preadme():
    """PREADME = <repo>/prd-toolkit/README.md."""
    return read_text("prd-toolkit/README.md")


def rreadme():
    """RREADME = <repo>/README.md."""
    return read_text("README.md")


def flat(text):
    """Every run of white space replaced by one space."""
    return re.sub(r"\s+", " ", text)


def intro(text):
    """A README's text before the first line that starts with "## "."""
    out = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            break
        out.append(line)
    return "".join(out)


def section(text, title):
    """The text from the line "## <title>" to the next line that starts with "## ",
    or to the end of the file when no later "## " line follows."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.rstrip("\r\n") == f"## {title}":
            start = i
            break
    assert start is not None, f"no line '## {title}' in the README"
    out = [lines[start]]
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        out.append(line)
    return "".join(out)


def fenced_blocks(text):
    """The fenced code blocks of a text, each a list of its lines (fence lines excluded)."""
    blocks, current = [], None
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append(current)
                current = None
        elif current is not None:
            current.append(line)
    return blocks


def shell_glob_files(folder, pattern):
    """The files a one-level glob such as `<folder>/*.md` matches, as the shell matches it
    (testing.md, the release cases' paragraph): `*` matches no name that starts with `.`, the
    match is case-sensitive, and only regular files count (a folder, a symbolic link or any
    other kind of entry does not)."""
    folder = Path(folder)
    out = []
    for name in sorted(os.listdir(folder)):
        if name.startswith("."):
            continue
        if not fnmatch.fnmatchcase(name, pattern):
            continue
        if not stat.S_ISREG(os.lstat(folder / name).st_mode):
            continue
        out.append(folder / name)
    return out


def command_files():
    """The files <repo>/prd-toolkit/commands/*.md, matched as the shell matches the glob."""
    return shell_glob_files(REPO / "prd-toolkit" / "commands", "*.md")


def command_stems():
    """The set of stems of <repo>/prd-toolkit/commands/*.md (the glob matched as the shell
    matches it, only regular files counting)."""
    return {p.name[: -len(".md")] for p in command_files()}


def markdown_targets(text):
    """Every match of ]\\(([^)\\s]+)\\) in a text, in order."""
    return re.findall(r"\]\(([^)\s]+)\)", text)


def subprocess_env(extra=None, drop_git=False):
    """The Subprocess environment (testing.md Harness), plus a case's own env."""
    env = {k: v for k, v in os.environ.items() if k not in _DROPPED}
    if drop_git:
        for k in _GIT_DROPPED:
            env.pop(k, None)
    if extra:
        env.update(extra)
    return env


def run(cmd, cwd, env):
    """Run a command to completion, stdout and stderr captured as bytes."""
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True)


def git_ls_files():
    """The paths git -C <repo> ls-files lists (read with -z, so no path is quoted)."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z"],
        env=subprocess_env(drop_git=True),
        capture_output=True,
    )
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    return [p for p in r.stdout.decode("utf-8").split("\0") if p]


def snapshot(root):
    """Every path under root, `.git/` included, for "no file under <tmp> changes" (testing.md,
    the release cases' paragraph): a folder by its presence, a file by its bytes and a symbolic
    link by its target. Symbolic links are never followed."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames:
            p = Path(dirpath) / name
            rel = str(p.relative_to(root))
            out[rel] = ("link", os.readlink(p)) if p.is_symlink() else ("dir",)
        for name in filenames:
            p = Path(dirpath) / name
            rel = str(p.relative_to(root))
            out[rel] = ("link", os.readlink(p)) if p.is_symlink() else ("file", p.read_bytes())
    return out


def _line_text(line):
    """A line with its line ending removed."""
    return line.rstrip("\r\n")


def prd_function():
    """FUNC = the lines of RREADME from the first line that equals `prd() {` once its line ending
    is removed to the next line that equals `}` once its line ending is removed, both included,
    joined with newlines."""
    lines = [_line_text(l) for l in rreadme().splitlines(keepends=True)]
    start = None
    for i, line in enumerate(lines):
        if line == "prd() {":
            start = i
            break
    assert start is not None, "no line 'prd() {' in README.md"
    for j in range(start + 1, len(lines)):
        if lines[j] == "}":
            return "\n".join(lines[start:j + 1])
    raise AssertionError("no line '}' after 'prd() {' in README.md")


def write(path, text):
    """Write a text, creating parent folders."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_line(path, line):
    """An FR-274 setup's file: the one line the step gives and a newline, as UTF-8 bytes,
    creating parent folders, with the mode it is created with."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((line + "\n").encode("utf-8"))
