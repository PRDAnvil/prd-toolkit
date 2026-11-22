"""Characterization tests of FR-090 (test-cases/trace.yaml): trace --range checks each commit against the commit rule.

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/trace.yaml and testing.md (Setup steps,
the trace steps).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from trace_support import (
    TA, given_steps, git, git_out, orders, replace_in_line, run_trace, write_lines,
    scratch,  # noqa: F401  (the fixture given_steps parametrizes)
)

NO_REFS = "no `Refs:` trailer (`Refs: FR-001`, or `Refs: none (no behaviour change)`)"
REFS_NONE = "Refs: none (no behaviour change)"

# Values a case's steps name (`<base>`), kept per scratch repository for the test to read after the steps.
CAPTURED: dict[Path, dict[str, str]] = {}


def boundary_line(sha8: str, path: str, problem: str) -> str:
    return f"docs/prd/orders/prd.md:1: commit-refs: commit {sha8} touches {path} inside the Boundary: {problem}"


def head8(tmp: Path, rev: str = "HEAD") -> str:
    return git_out(tmp, "rev-parse", rev)[:8]


def commit(tmp: Path, *messages: str) -> None:
    git(tmp, "add", "-A")
    args: list[str] = ["commit", "-q"]
    for m in messages:
        args += ["-m", m]
    git(tmp, *args)


# -- T-090.1 --

def app_and_zed(tmp: Path) -> None:
    write_lines(tmp / "src/app.py", ["x = 1"])
    write_lines(tmp / "src/zed.py", ["x = 1"])
    commit(tmp, "app")


@given_steps("N0E", "TB", app_and_zed)
def test_range_commit_without_refs(scratch):
    """@prd T-090.1"""
    r = run_trace(scratch, "docs/prd/orders", "--range", "HEAD~1..HEAD")
    assert r.exit == 1
    assert r.stdout == boundary_line(head8(scratch), "src/app.py", NO_REFS) + "\n"
    assert r.stderr == ""


# -- T-090.2 --

def app_bad_refs(tmp: Path) -> None:
    write_lines(tmp / "src/app.py", ["x = 1"])
    commit(tmp, "app", "Refs: FR-009, JIRA-1")


@given_steps("N0E", "TB", app_bad_refs)
def test_range_one_finding_per_problem(scratch):
    """@prd T-090.2"""
    r = run_trace(scratch, "docs/prd/orders", "--range", "HEAD~1..HEAD")
    sha8 = head8(scratch)
    assert r.exit == 1
    assert r.stdout.splitlines() == [
        boundary_line(sha8, "src/app.py", "FR-009 is not defined in the PRD"),
        boundary_line(sha8, "src/app.py", "`JIRA-1` is not a PRD ID; give other keys their own trailer"),
    ], r.stdout
    assert r.stderr == ""


# -- T-090.3 --

def notes_and_vendored(tmp: Path) -> None:
    """Write <tmp>/docs/prd/orders/notes.md (`notes`) and <tmp>/.prd-toolkit/x.txt (`x`); in <tmp> run
    git add -A and git commit -q -m notes."""
    write_lines(tmp / "docs" / "prd" / "orders" / "notes.md", ["notes"])
    write_lines(tmp / ".prd-toolkit" / "x.txt", ["x"])
    git(tmp, "add", "-A")
    git(tmp, "commit", "-q", "-m", "notes")


@given_steps("N0E", "TB", notes_and_vendored)
def test_range_outside_boundary_without_adoption(scratch):
    """@prd T-090.3"""
    r = run_trace(scratch, "docs/prd/orders", "--range", "HEAD~1..HEAD")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


# -- T-090.4 --

def base_is_head(tmp: Path) -> None:
    CAPTURED.setdefault(tmp, {})["base"] = git_out(tmp, "rev-parse", "HEAD")


def early(tmp: Path) -> None:
    write_lines(tmp / "src/early.py", ["x = 1"])
    commit(tmp, "early")


def map_adopted(tmp: Path) -> None:
    TA(tmp, "adopted")
    commit(tmp, "map", REFS_NONE)


def app_no_refs(tmp: Path) -> None:
    write_lines(tmp / "src/app.py", ["x = 1"])
    commit(tmp, "app")


@given_steps("N0E", "TB", base_is_head, early, map_adopted, app_no_refs)
def test_range_judges_by_each_commits_adoption_map(scratch):
    """@prd T-090.4"""
    base = CAPTURED[scratch]["base"]
    r = run_trace(scratch, "docs/prd/orders", "--range", f"{base}..HEAD")
    assert r.exit == 1
    assert r.stdout == boundary_line(head8(scratch), "src/app.py", NO_REFS) + "\n"
    assert r.stderr == ""


# -- T-090.5 --

def adopt(tmp: Path) -> None:
    replace_in_line(orders(tmp) / "adoption.md", 5, "extracted", "adopted")  # SetupError unless held once
    commit(tmp, "adopt", REFS_NONE)


@given_steps("N0E", "TA:extracted", "TB", base_is_head, early, adopt, app_no_refs)
def test_range_no_adopted_row_judges_nothing(scratch):
    """@prd T-090.5"""
    base = CAPTURED[scratch]["base"]
    r = run_trace(scratch, "docs/prd/orders", "--range", f"{base}..HEAD")
    assert r.exit == 1
    assert r.stdout == boundary_line(head8(scratch), "src/app.py", NO_REFS) + "\n"
    assert r.stderr == ""


# -- T-090.6 --

def app_staged_alone(tmp: Path) -> None:
    write_lines(tmp / "src/app.py", ["x = 1"])
    git(tmp, "add", "src/app.py")
    git(tmp, "commit", "-q", "-m", "app")


@given_steps("N0E", "TB", "TA:adopted", app_staged_alone)
def test_range_uncommitted_adoption_map(scratch):
    """@prd T-090.6"""
    r = run_trace(scratch, "docs/prd/orders", "--range", "HEAD~1..HEAD")
    assert r.exit == 1
    assert r.stdout == boundary_line(head8(scratch), "src/app.py", NO_REFS) + "\n"
    assert r.stderr == ""


# -- T-090.7 --

@given_steps("N0E", "TB", app_no_refs)
def test_no_range_no_commit_refs(scratch):
    """@prd T-090.7"""
    r = run_trace(scratch, "docs/prd/orders")
    assert (r.exit, r.stdout, r.stderr) == (0, "", "")


# -- T-090.8 --

def notes_change_set(tmp: Path) -> None:
    """Write <tmp>/docs/prd/orders/notes.md (`notes`); git add -A; git commit -q -m notes
    -m "Refs: none (no behaviour change)" -m "Change-set: orders/CS-001"."""
    write_lines(tmp / "docs" / "prd" / "orders" / "notes.md", ["notes"])
    git(tmp, "add", "-A")
    git(tmp, "commit", "-q", "-m", "notes", "-m", "Refs: none (no behaviour change)",
        "-m", "Change-set: orders/CS-001")


@given_steps("N0E", "TB", notes_change_set)
def test_range_change_set_without_record(scratch):
    """@prd T-090.8"""
    sha8 = git_out(scratch, "rev-parse", "HEAD")[:8]  # <sha8> as in T-090.1
    r = run_trace(scratch, "docs/prd/orders", "--range", "HEAD~1..HEAD")
    assert r.exit == 1
    assert r.stdout == (
        f"docs/prd/orders/prd.md:1: commit-refs: commit {sha8}: "
        "Change-set: orders/CS-001 has no record in changes/\n"
    )
    assert r.stderr == ""


# -- T-090.9 (known-failing E-040, with a symptom) --

class KnownFailureE040(Exception):
    """The symptom T-090.9 names: exit 1, stderr empty, and stdout exactly one line, the expected line of the newest
    commit (<sha8_b>, src/b.py), so no line holds <sha8_a>."""


def commit_a(tmp: Path) -> None:
    write_lines(tmp / "src/a.py", ["x = 1"])
    commit(tmp, "a")
    CAPTURED.setdefault(tmp, {})["sha8_a"] = git_out(tmp, "rev-parse", "HEAD")[:8]


def commit_b(tmp: Path) -> None:
    write_lines(tmp / "src/b.py", ["x = 1"])
    commit(tmp, "b")
    CAPTURED.setdefault(tmp, {})["sha8_b"] = git_out(tmp, "rev-parse", "HEAD")[:8]


@given_steps("T256", "TB", commit_a, commit_b)
def test_range_sha256_checks_every_commit(scratch):
    """@prd T-090.9"""
    sha8_a = CAPTURED[scratch]["sha8_a"]
    sha8_b = CAPTURED[scratch]["sha8_b"]
    r = run_trace(scratch, "docs/prd/orders", "--range", "HEAD~2..HEAD")
    line_a = boundary_line(sha8_a, "src/a.py", NO_REFS)
    line_b = boundary_line(sha8_b, "src/b.py", NO_REFS)
    lines = r.stdout.splitlines()
    # The symptom, and only it, is the known failure (E-040).
    if r.exit == 1 and r.stderr == "" and lines == [line_b] and not any(sha8_a in line for line in lines):
        raise KnownFailureE040(f"stdout is only the line of the newest commit {sha8_b}: {r.stdout!r}")
    assert r.exit == 1, (r.exit, r.stdout, r.stderr)
    # stdout_lines_any_order_exact: the same lines as the list, in any order, and nothing else.
    assert sorted(lines) == sorted([line_a, line_b]), r.stdout
    assert r.stderr == ""
