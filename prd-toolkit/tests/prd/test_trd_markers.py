"""FR-265: assumption markers in the copied sections (test-cases/trd.yaml, T-265.6)."""
from __future__ import annotations

from trd_support import (
    given_steps, pack_part_lines, run, stdout_contains_line, stdout_not_contains, texts, trd_repo,  # noqa: F401
)


@given_steps("V0", "VM")
def test_markers_removed_and_open_marker_kept(trd_repo):
    """@prd T-265.6"""
    t = texts()
    r = run(trd_repo, "python TRD docs/prd/orders")
    assert r.exit == 0, r.err
    stdout_contains_line(r.out, "- Language: Python 3.12 today")
    stdout_not_contains(r.out, [t["marker_a01"], t["marker_a02"]])
    assert pack_part_lines(r.out, "Architecture") == [
        "## Architecture",
        "",
        "From: prd.md section 4.",
        "",
        t["architecture_line"],
        "",
    ]
