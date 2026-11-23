"""Move a PRD to a new version of its pack (features/change.md FR-261; test-cases/change.yaml)."""
from __future__ import annotations

from change_support import (
    G0, GC, GN, GP, append, case, diff, exit_is, given, insert_after, snapshot, stderr_is,
    stderr_single_line_starts, stdout_is,
)

__all__ = ["case"]

PACK = "python CHANGE pack docs/prd/orders service"
NOTE = append("errors.md", "A note.", name="append the line `A note.` to errors.md")


@given(G0, GP, GC)
def test_t261_1_pack_moves_and_records(case):
    """@prd T-261.1"""
    r = case.run(PACK + " 1.0.0")
    exit_is(r, 0)
    stderr_is(r, "")
    rows = case.today("| 1.0.1 | <today> | pack service 0.9.0 → 1.0.0; pending | - |")
    assert any(r.lines == ["1.0.1", row] for row in rows), str(r)
    lines = (case.orders / "prd.md").read_bytes().decode("utf-8").splitlines()
    assert lines[13] == "- Pack: service 1.0.0 (prd-toolkit)", lines[13]
    assert lines[2] == "version: 1.0.1", lines[2]
    status = case.git("status", "--porcelain")
    assert status.lines == [" M docs/prd/orders/prd.md"], str(status)


@given(G0)
def test_t261_2_refusals_in_order(case):
    """@prd T-261.2"""
    def checked(run):
        before = snapshot(case.orders)
        r = run()
        assert diff(before, snapshot(case.orders)) == [], f"the run changed the PRD folder\n{r}"
        return r

    r1 = checked(lambda: case.run(PACK + " 1.0"))
    exit_is(r1, 2)
    stderr_is(r1, "pack: 1.0 is not a version X.Y.Z\n")

    r2 = checked(lambda: case.run(PACK + " 1.0.0"))
    exit_is(r2, 1)
    stderr_is(r2, "refused: no Pack: or Target: pack line names service\n")

    case.steps(GP, GC)
    r3 = checked(lambda: case.run(PACK + " 0.9.0"))
    exit_is(r3, 1)
    stderr_is(r3, "refused: every line naming service already names 0.9.0\n")

    r4 = checked(lambda: case.run(PACK + " 2.0.0"))
    exit_is(r4, 1)
    stderr_single_line_starts(r4, "refused: pack service")
    assert "not found; looked in: " in r4.stderr, str(r4)

    case.steps(NOTE)
    r5 = checked(lambda: case.run(PACK + " 1.0.0"))
    exit_is(r5, 1)
    stderr_is(r5, "refused: docs/prd/orders has uncommitted changes; commit or set them aside first\n")


@given(G0, GP, insert_after("features/import.md", 1, "Target: pack service 0.8.0 (prd-toolkit)"), GC)
def test_t261_3_lines_disagree(case):
    """@prd T-261.3"""
    r = case.run(PACK + " 1.0.0")
    exit_is(r, 1)
    stdout_is(r, "")
    stderr_is(r, "refused: the lines naming service disagree on its version or source\n")


@given(G0, GN, GP, GC)
def test_t261_4_record_refuses_after_the_move(case):
    """@prd T-261.4"""
    r = case.run(PACK + " 1.0.0")
    exit_is(r, 1)
    stderr_is(r, "refused: §14 has no changelog table\n")
    committed = case.git("show", "HEAD:docs/prd/orders/prd.md")
    exit_is(committed, 0)
    text = (case.orders / "prd.md").read_bytes()
    assert text == committed.out, "prd.md differs from its committed text"
    assert text.decode("utf-8").splitlines()[13] == "- Pack: service 0.9.0 (prd-toolkit)"
    status = case.git("status", "--porcelain")
    stdout_is(status, "")
