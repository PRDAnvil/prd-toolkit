"""The Code part of the implement pack, how a cited line stands, and the exit code (features/context.md FR-215 to
FR-217)."""
from __future__ import annotations

import shutil

from context_support import (
    CX0, CXB, CXM, CXO, CXP, CXS, CXT, N0, Scratch, SetupError, assert_relative_order, given, in_dir, insert_after,
    one_json, part, run, scratch, titles, write_lines,  # noqa: F401  (scratch is the fixture)
)

IMPLEMENT_0 = "python CTX docs/prd/orders --area import --req FR-001 --for implement --context 0"


@given(CXS)
def test_code_lines_around_the_cited_line(scratch: Scratch):
    """@prd T-215.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --for implement --context 1")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --for implement")
    for r in (r1, r2):
        assert r.exit == 0, r.out
        assert r.err_b == b""
    sha = scratch.sha
    assert part(r1.out, "Code") == [
        "## Code", "", f"### src/importer.py:3 @{sha}", "    2      header = read_header(path)",
        "    3      if header is None:", "    4          raise SystemExit(2)", "",
    ]
    assert part(r2.out, "Code") == [
        "## Code", "", f"### src/importer.py:3 @{sha}", "    1  def import_file(path):",
        "    2      header = read_header(path)", "    3      if header is None:", "    4          raise SystemExit(2)",
        "    5  ", "    6      return header", "",
    ]


def _bad_source(s: Scratch) -> None:
    insert_after(s.orders / "features/import.md", "Status: approved", ["Source: somewhere in the importer"])


@given(N0, _bad_source)
def test_source_not_in_form(scratch: Scratch):
    """@prd T-215.2"""
    r = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --for implement")
    assert r.exit == 1
    assert r.err_b == b""
    # `<path>`, `<line>` and `<sha>` are literal text here (the case's note).
    assert part(r.out, "Code") == [
        "## Code", "", "### FR-001 Source: somewhere in the importer",
        "STALE: Source not in <path>:<line> @<sha> form", "",
    ]


@given(CXO, in_dir(CX0, "b"))
def test_one_item_per_distinct_citation(scratch: Scratch):
    """@prd T-215.3"""
    r1 = run(scratch, IMPLEMENT_0)
    r2 = run(scratch, {"cwd": "<tmp>/b", "command": "python CTX docs/prd/orders --area import --for implement"})
    assert r1.exit == 1
    assert part(r1.out, "Code") == [
        "## Code", "", f"### src/importer.py:3 @{scratch.sha}", "STALE: the cited line's text is gone",
        "    3      if not header:", "",
    ]
    assert r2.exit == 0
    assert part(r2.out, "Code") == ["## Code", "", "None.", ""]


@given(CXM)
def test_current_line_has_no_state_line(scratch: Scratch):
    """@prd T-216.1"""
    r = run(scratch, IMPLEMENT_0)
    assert r.exit == 0
    assert r.err_b == b""
    heading = f"### src/calc.py:1 @{scratch.sha}"
    assert_relative_order(r.out, ["## Code", heading, "    1  total = 0", "## Levels"])
    lines = r.out.splitlines()
    assert lines[lines.index(heading) + 1] == "    1  total = 0"


@given(CXM)
def test_moved_line(scratch: Scratch):
    """@prd T-216.2"""
    r = run(scratch, IMPLEMENT_0)
    assert r.exit == 0
    assert r.err_b == b""
    sha = scratch.sha
    assert part(r.out, "Code") == [
        "## Code", "", f"### src/importer.py:3 @{sha}", "MOVED: line 3 is now line 4", "    4      if header is None:",
        "", f"### src/calc.py:1 @{sha}", "    1  total = 0", "",
    ]


@given(CXT)
def test_stale_reasons(scratch: Scratch):
    """@prd T-216.3"""
    r = run(scratch, IMPLEMENT_0)
    assert r.exit == 1
    assert r.err_b == b""
    sha = scratch.sha
    assert part(r.out, "Code") == [
        "## Code",
        "",
        f"### src/importer.py:3 @{sha}",
        "STALE: the cited line's text is gone",
        "    3      if not header:",
        "",
        f"### src/importer.py:9 @{sha}",
        "STALE: line 9 is past the end (6 lines)",
        "",
        f"### src/gone.py:1 @{sha}",
        "STALE: file missing",
        "",
        f"### src/new.py:1 @{sha}",
        f"STALE: src/new.py is not in {sha}",
        "    1  x = 1",
        "",
        "### src/importer.py:2 @0000000",
        "STALE: unknown commit 0000000",
        "    2      header = read_header(path)",
        "",
        f"### src/twice.py:2 @{sha}",
        "STALE: the cited line's text appears 2 times",
        "    2  a = 1",
        "",
    ]


@given(CXB)
def test_empty_cited_line(scratch: Scratch):
    """@prd T-216.4"""
    r = run(scratch, IMPLEMENT_0)
    assert r.exit == 1
    assert r.err_b == b""
    sha = scratch.sha
    assert part(r.out, "Code") == [
        "## Code", "", f"### src/a.py:2 @{sha}", "    2  ", "",
        f"### src/b.py:2 @{sha}", "STALE: uncommitted changes; the cited line may have moved", "    2  ", "",
        f"### src/c.py:2 @{sha}", f"STALE: changed since {sha}; the cited line may have moved", "    2  ", "",
    ]


def _git_without_log(s: Scratch) -> None:
    real_git = shutil.which("git")
    if not real_git:
        raise SetupError("no git on PATH")
    stub = s.tmp / "bin" / "git"
    write_lines(stub, ["#!/bin/sh", 'for a in "$@"; do [ "$a" = log ] && exit 128; done', f'exec {real_git} "$@"'])
    stub.chmod(0o755)


@given(CXB, _git_without_log)
def test_cannot_compare(scratch: Scratch):
    """@prd T-216.5"""
    r = run(scratch, {"env": {"PATH": "<tmp>/bin:<the runner's PATH>"}, "command": IMPLEMENT_0})
    assert r.exit == 1
    assert r.err_b == b""
    sha = scratch.sha
    stale = f"STALE: cannot compare with {sha}; the cited line may have moved"
    assert part(r.out, "Code") == [
        "## Code", "", f"### src/a.py:2 @{sha}", stale, "    2  ", "",
        f"### src/b.py:2 @{sha}", stale, "    2  ", "",
        f"### src/c.py:2 @{sha}", stale, "    2  ", "",
    ]


@given(CXP)
def test_exit_code(scratch: Scratch):
    """@prd T-217.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --for implement --context 0")
    for r in (r1, r2):
        assert r.err_b == b""
    assert r1.exit == 0
    assert titles(r1.out) == ["## Header", "## Stack", "## Glossary", "## Requirements", "## Cited",
                              "## Known defects", "## Open questions", "## History"]
    assert r2.exit == 1
    assert titles(r2.out) == ["## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Levels",
                              "## Cited", "## Known defects", "## Open questions", "## History"]


@given(CXP)
def test_blocks_counted_for_the_exit(scratch: Scratch):
    """@prd T-217.2"""
    r1 = run(scratch, IMPLEMENT_0)
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001,UJ-01 --for implement --context 0")
    r3 = run(scratch, "python CTX docs/prd/orders --area import --for implement --context 0")
    r4 = run(scratch, IMPLEMENT_0 + " --json")
    for r in (r1, r2, r3, r4):
        assert r.err_b == b""
    sha = scratch.sha
    code_1 = part(r1.out, "Code")
    assert r1.exit == 0
    assert code_1 == [
        "## Code", "", f"### src/importer.py:3 @{sha}",
        "STALE: the cited line's text is gone (pulled in; not counted)", "    3      if not header:", "",
    ]
    assert r2.exit == 1
    assert part(r2.out, "Code") == [
        "## Code", "", f"### src/importer.py:3 @{sha}", "STALE: the cited line's text is gone",
        "    3      if not header:", "",
    ]
    assert r3.exit == 1
    assert "STALE: the cited line's text is gone" in r3.out.splitlines()
    assert r4.exit == 0
    assert {
        "title": "Code", "id": "UJ-01", "file": "src/importer.py", "line": 3, "text": "\n".join(code_1[2:-1]),
        "stale": True, "counted": False, "moved": None,
    } in one_json(r4.out)["parts"]
