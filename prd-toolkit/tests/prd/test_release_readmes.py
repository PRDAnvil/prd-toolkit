"""Black-box tests of the release area's READMEs (test-cases/release.yaml)."""

import os
import re
import sys

import pytest

from release_support import (
    REPO,
    command_files,
    command_stems,
    entry,
    fenced_blocks,
    flat,
    git_ls_files,
    intro,
    market,
    markdown_targets,
    plugin,
    preadme,
    rreadme,
    run,
    section,
    subprocess_env,
)


def test_plugin_readme_names_version():
    """@prd T-270.2"""
    v = plugin()["version"]
    assert f"Version {v}." in flat(intro(preadme()))


def test_changelog_versions_descend():
    """@prd T-270.3"""
    v = plugin()["version"]
    pat = re.compile(r"^- \*\*([0-9]+)\.([0-9]+)\.([0-9]+):\*\*")
    versions = []
    for line in section(preadme(), "Changelog").splitlines():
        m = pat.match(line)
        if m:
            versions.append(tuple(int(g) for g in m.groups()))
    assert versions, "no changelog line matches the version pattern"
    assert ".".join(map(str, versions[0])) == v
    for a, b in zip(versions, versions[1:]):
        assert a > b, f"{a} is not greater than {b}"
    assert ".".join(map(str, versions[-1])) == "0.1.0"


def test_root_readme_slash_commands():
    """@prd T-271.3"""
    # The one line of RREADME that starts with `- **Slash commands**` ("starts with" on the
    # line as written); no such line, or more than one, is a test failure.
    lines = [l for l in rreadme().splitlines() if l.startswith("- **Slash commands**")]
    assert len(lines) == 1, f"lines of README.md starting with '- **Slash commands**': {len(lines)}"
    names = set(re.findall(r"/prd-toolkit:([a-z-]+)", lines[0]))
    # The set of stems of <repo>/prd-toolkit/commands/*.md, the glob matched as the shell
    # matches it, only regular files counting (testing.md, the release cases' paragraph).
    stems = command_stems()
    assert names == stems, (
        f"only on the line: {sorted(names - stems)}; only in commands/: {sorted(stems - names)}"
    )


def test_rule_count(tmp_path):
    """@prd T-272.1"""
    # <tmp> is the test's tmp_path resolved (testing.md, the release cases' paragraph).
    tmp = tmp_path.resolve()
    r = run(
        [sys.executable, str(REPO / "prd-toolkit" / "scripts" / "prd_lint.py"), "--list-rules"],
        cwd=tmp,
        env=subprocess_env(),
    )
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    lines = r.stdout.decode("utf-8").splitlines()
    assert len(lines) == 41, f"--list-rules printed {len(lines)} lines"
    # Every text flattened, as AC-272.1 says.
    assert "a 41-rule linter" in flat(plugin()["description"]), "plugin.json description"
    assert "a 41-rule linter" in flat(intro(preadme())), "intro of prd-toolkit/README.md"
    assert "a 41-rule linter" in flat(intro(rreadme())), "intro of README.md"
    assert "checks 41 rules" in flat(rreadme()), "README.md"
    assert "prints the 41 rules" in flat(section(preadme(), "Lint CLI")), "section Lint CLI of prd-toolkit/README.md"


def _file_lines(text):
    """A file's lines, each with its line ending removed."""
    return [line.rstrip("\r\n") for line in text.splitlines(keepends=True)]


def _section_range(lines, title):
    """The line indexes [start, end) of section <title>: from the line that equals "## <title>"
    once its line ending is removed, that line included, up to and not including the next line
    that starts with "## ", or to the end of the file when no later "## " line follows."""
    start = None
    for i, line in enumerate(lines):
        if line == f"## {title}":
            start = i
            break
    assert start is not None, f"no line '## {title}'"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return start, end


def _file_blocks(lines):
    """The fenced blocks of the whole file: a fence is a line whose text, with its leading white
    space removed, starts with three backticks; fences pair in file order (first opens, second
    closes, third opens the next, ...). Each block is (opening fence index, closing fence index)."""
    fences = [i for i, line in enumerate(lines) if line.lstrip().startswith("```")]
    return [(fences[k], fences[k + 1]) for k in range(0, len(fences) - 1, 2)]


def _section_blocks(lines, title):
    """The blocks that belong to section <title>: both of their fences lie inside it. Each is
    the list of its lines with their leading and trailing white space removed."""
    start, end = _section_range(lines, title)
    return [
        [lines[i].strip() for i in range(o + 1, c)]
        for o, c in _file_blocks(lines)
        if start <= o < end and start <= c < end
    ]


def _has_install_pair(text, title):
    """Inside one fenced block of section <title>, the line `/plugin marketplace add
    PRDAnvil/prd-toolkit`, and directly after it the line `/plugin install prd-toolkit@prdanvil`."""
    first = "/plugin marketplace add PRDAnvil/prd-toolkit"
    second = "/plugin install prd-toolkit@prdanvil"
    for block in _section_blocks(_file_lines(text), title):
        for a, b in zip(block, block[1:]):
            if a == first and b == second:
                return True
    return False


def test_install_lines():
    """@prd T-273.1"""
    assert _has_install_pair(rreadme(), "Install"), "README.md section Install: no fenced block with the two lines"
    assert _has_install_pair(preadme(), "Install"), "prd-toolkit/README.md section Install: no fenced block with the two lines"
    assert market()["name"] == "prdanvil"
    assert entry()["name"] == "prd-toolkit"


def test_install_uninstall_old():
    """@prd T-273.2"""
    text = flat(section(rreadme(), "Install"))
    for s in ["claude plugin uninstall prd-toolkit@ihistand", "at every scope"]:
        assert s in text, s


def test_install_launchers():
    """@prd T-273.3"""
    text = flat(section(rreadme(), "Install"))
    for s in [
        "The plugin adds no `prd` command to your shell",
        "`.prd-toolkit/prd <command>`",
        "`~/.claude/plugins/cache/prdanvil/prd-toolkit/<version>/scripts/prd <command>`",
    ]:
        assert s in text, s


def test_commands_table():
    """@prd T-273.4"""
    lines = section(preadme(), "Commands and skills").splitlines()
    # The table: the first run of lines in the section that start with `|` (as written).
    table = []
    for line in lines:
        if line.startswith("|"):
            table.append(line)
        elif table:
            break
    assert table, "no line starting with '|' in section Commands and skills"
    # Data rows: the third line on.
    rows = table[2:]
    # The files <repo>/prd-toolkit/commands/*.md, the glob matched as the shell matches it,
    # only regular files counting (testing.md, the release cases' paragraph), and their stems.
    files = command_files()
    stems = command_stems()
    # row_count_equals_file_count
    assert len(rows) == len(files), f"{len(rows)} data rows, {len(files)} command files"
    prefix = "`/prd-toolkit:"
    names = set()
    for row in rows:
        # First cell: the text between the row's first and second `|`, with its leading and
        # trailing white space removed.
        first = row.find("|")
        second = row.find("|", first + 1)
        assert second >= 0, f"row has no second '|': {row!r}"
        cell = row[first + 1:second].strip()
        # Every first cell starts with a backtick followed by /prd-toolkit:.
        assert cell.startswith(prefix), f"first cell does not start with {prefix!r}: {cell!r}"
        # Its command name: the run of a-z and - after that prefix.
        names.add(re.match(r"[a-z-]*", cell[len(prefix):]).group(0))
    # The rows' command names, as a set, equal the stems, as a set.
    assert names == stems, f"only in the table: {sorted(names - stems)}; only in commands/: {sorted(stems - names)}"


def test_update_order():
    """@prd T-273.5"""
    text = flat(section(preadme(), "Install"))
    pos = 0
    for s in ["claude plugin marketplace update prdanvil", "claude plugin update prd-toolkit@prdanvil", "/reload-plugins"]:
        i = text.find(s, pos)
        assert i >= 0, f"{s!r} not found after offset {pos}"
        pos = i + len(s)


def test_tests_and_evals_no_bare_command():
    """@prd T-273.6"""
    text = flat(section(preadme(), "Tests and evals"))
    for s in ["that the skills' text still prints", "the skills' text prints"]:
        assert s not in text, s


def test_features_list():
    """@prd T-273.7"""
    # The lines of RREADME from the first line that starts with `**Features:**` ("starts with"
    # on the line as written), that line included, up to and not including the first later
    # line that starts with `**` or `## `, or to the end of the file when no such line follows.
    # No such first line is a test failure (testing.md, the release cases' paragraph).
    lines = rreadme().splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith("**Features:**")]
    assert starts, "no line of README.md starts with '**Features:**'"
    start = starts[0]
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("**") or lines[j].startswith("## "):
            end = j
            break
    text = flat("".join(lines[start:end]))
    # holds: each listed string is a substring of the flattened text.
    for s in ["the main skills", "the plugin README lists all eleven", "](./prd-toolkit/README.md"]:
        assert s in text, f"the Features list does not hold {s!r}"


def test_relative_links_resolve():
    """@prd T-276.1"""
    # The output of git -C <repo> ls-files (read with -z, so no path comes back quoted).
    listed = git_ls_files()
    listed_set = set(listed)

    def resolves(path):
        # A target resolves when, after normalising, it is `.` (the repository root, which
        # holds every listed path), a listed path, or a prefix of one followed by /.
        if path == ".":
            return True
        if path in listed_set:
            return True
        return any(p.startswith(path + "/") for p in listed)

    unresolved = []
    # The holding file's folder relative to <repo>: "" for the root README, "prd-toolkit"
    # for the plugin README.
    for rel, text in [("README.md", rreadme()), ("prd-toolkit/README.md", preadme())]:
        folder = os.path.dirname(rel)
        # Every match of ]\(([^)\s]+)\) whose target does not start with http.
        for target in markdown_targets(text):
            if target.startswith("http"):
                continue
            # Any #... removed; compared as written, with no percent-decoding. A target that is
            # only a # fragment becomes "" and normalises to the holding file's folder.
            bare = target.split("#", 1)[0]
            path = os.path.normpath(os.path.join(folder, bare))
            if not resolves(path):
                unresolved.append(f"{rel}: {target} -> {path}")
    assert unresolved == []


def test_one_spec_link():
    """@prd T-276.2"""
    folder = "../docs/superpowers/specs/"
    targets = [t for t in markdown_targets(preadme()) if t.startswith(folder)]
    assert targets == ["../docs/superpowers/specs/"]
