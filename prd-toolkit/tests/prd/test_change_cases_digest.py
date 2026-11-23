"""The digest of a PRD folder (features/change.md FR-257; test-cases/change.yaml)."""
from __future__ import annotations

import re

from status_next_support import N0X, SetupError

from change_support import (
    G0, GL, GQ, GX, UNDO_GX, StepError, case, exit_is, given, line_becomes, named, one_json_line, stderr_is,
    write, write_text,
)

__all__ = ["case"]


@given(G0)
def test_t257_1_digest_line_and_json(case):
    """@prd T-257.1"""
    r1 = case.run("python CHANGE digest docs/prd/orders")
    r2 = case.run("python CHANGE digest docs/prd/orders --json")
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    assert len(r1.lines) == 1 and re.fullmatch(r"[0-9a-f]{64}", r1.lines[0]), str(r1)
    assert one_json_line(r2) == {"interface": 1, "kind": "change.digest", "digest": r1.lines[0]}, str(r2)


@named("prd.md line 3 becomes `version: 9.9.9` and line 6 `updated: 2030-01-01`")
def _version_and_updated(c):
    line_becomes("prd.md", 3, "version: 1.0.0", "version: 9.9.9")(c)
    line_becomes("prd.md", 6, "updated: 2026-11-01", "updated: 2030-01-01")(c)


@named("FR-001's §11 Status cell becomes `built`")
def _fr001_built(c):
    path = c.path("prd.md")
    lines = path.read_bytes().decode("utf-8").split("\n")
    old = "| FR-001 | Refuse a file with no header | approved | features/import.md | 1.0.0 |"
    if lines.count(old) != 1:
        raise StepError(f"FR-001's §11 row {old!r} not found once")
    lines[lines.index(old)] = "| FR-001 | Refuse a file with no header | built | features/import.md | 1.0.0 |"
    path.write_bytes("\n".join(lines).encode("utf-8"))


@named("write .notes/a.txt and __pycache__/b.txt, each with the line `x`")
def _hidden_files(c):
    write_text(c.path(".notes/a.txt"), "x\n")
    write_text(c.path("__pycache__/b.txt"), "x\n")


@given(G0)
def test_t257_2_left_out_of_the_digest(case):
    """@prd T-257.2"""
    r1 = case.run("python CHANGE digest docs/prd/orders")
    case.steps(_version_and_updated, GL, _fr001_built, write("README.md", "hi"), write(".prd-review.json", "{}"),
               _hidden_files)
    r2 = case.run("python CHANGE digest docs/prd/orders")
    for r in (r1, r2):
        exit_is(r, 0)
        stderr_is(r, "")
    assert r2.out == r1.out, f"run_1: {r1}\nrun_2: {r2}"


@given(G0)
def test_t257_3_an_ac_or_the_status_changes_the_digest(case):
    """@prd T-257.3"""
    r1 = case.run("python CHANGE digest docs/prd/orders")
    case.steps(GX)
    r2 = case.run("python CHANGE digest docs/prd/orders")
    case.steps(UNDO_GX, GQ)
    r3 = case.run("python CHANGE digest docs/prd/orders")
    for r in (r1, r2, r3):
        exit_is(r, 0)
    assert r2.out != r1.out, f"run_2's stdout equals run_1's: {r1}"
    assert r3.out != r1.out and r3.out != r2.out, f"run_1: {r1}\nrun_2: {r2}\nrun_3: {r3}"


@given(G0, write("<tmp>/.gitignore", "docs/prd/orders/notes.txt"))
def test_t257_4_read_from_disk(case, tmp_path_factory):
    """@prd T-257.4"""
    r1 = case.run("python CHANGE digest docs/prd/orders")
    case.steps(write("notes.txt", "x"))
    r2 = case.run("python CHANGE digest docs/prd/orders")
    tmp2 = tmp_path_factory.mktemp("outside")
    try:
        N0X(tmp2)
    except SetupError as exc:
        raise StepError(f"N0X into <tmp2>: {exc}") from exc
    r3 = case.run("python CHANGE digest docs/prd/orders", cwd=tmp2)
    for r in (r1, r2, r3):
        exit_is(r, 0)
        stderr_is(r, "")
    assert r2.out != r1.out, f"run_2's stdout equals run_1's: {r1}"
    assert r3.out == r1.out, f"run_1: {r1}\nrun_3: {r3}"
