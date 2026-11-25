"""FR-267: keep the view out of the PRD (test-cases/trd.yaml, T-267.1 to T-267.3)."""
from __future__ import annotations

import os
from collections import Counter

from trd_support import (  # noqa: F401
    given_steps, orders, porcelain_lines, run, snapshot, stderr_single_line_starts, trd_repo,
)

REFUSED = "refused: --out must lie outside the PRD folder and .prd-toolkit/\n"


@given_steps("V0", "VL")
def test_trd_refuses_out_inside_the_prd_or_vendored_copy(trd_repo):
    """@prd T-267.1"""
    tmp = trd_repo
    prd_md = orders(tmp) / "prd.md"
    prd_before = prd_md.read_bytes()
    runs = [
        "python TRD docs/prd/orders --out docs/prd/orders/view.md",
        "python TRD docs/prd/orders --out link/view.md",
        "python TRD docs/prd/orders --out docs/prd/orders",
        "python TRD docs/prd/orders --out .prd-toolkit/view.md",
    ]
    for n, text in enumerate(runs, 1):
        r = run(tmp, text)
        assert r.exit == 1, f"run_{n}: exit {r.exit}, stderr {r.stderr!r}"
        assert r.stdout == b"", f"run_{n}: stdout {r.stdout!r}"
        assert r.stderr == REFUSED.encode("utf-8"), f"run_{n}: stderr {r.stderr!r}"
    # effect: ORDERS holds no file view.md, ORDERS/prd.md is still a file with its bytes, <tmp> holds no .prd-toolkit
    assert not os.path.lexists(orders(tmp) / "view.md")
    assert prd_md.is_file() and not prd_md.is_symlink()
    assert prd_md.read_bytes() == prd_before
    assert not os.path.lexists(tmp / ".prd-toolkit")


@given_steps("VE", "VX", "VN", "VR")
def test_trd_refuses_a_folder_it_cannot_read(trd_repo):
    """@prd T-267.2"""
    tmp = trd_repo
    rtmp = tmp.resolve()
    runs = [
        "python TRD <tmp>/empty",
        "python TRD <tmp>/nogit/docs/prd/orders",
        "python TRD <tmp>/nocommit/docs/prd/orders",
        "python TRD <tmp>/repo/docs/prd/orders --out <tmp>/missing/view.md",
    ]
    results = [run(tmp, text) for text in runs]
    for n, r in enumerate(results, 1):
        assert r.exit == 2, f"run_{n}: exit {r.exit}, stderr {r.stderr!r}"
        assert r.stdout == b"", f"run_{n}: stdout {r.stdout!r}"
    assert results[0].stderr == f"prd_trd: {rtmp}/empty: no prd.md\n".encode("utf-8")
    assert results[1].stderr == f"prd_trd: {rtmp}/nogit/docs/prd/orders is not in a git work tree\n".encode("utf-8")
    assert results[2].stderr == b"prd_trd: the repository has no commit\n"
    stderr_single_line_starts(results[3].stderr.decode("utf-8"), f"prd_trd: cannot write {tmp}/missing/view.md: ")
    # effect: after the last run, <tmp> holds no folder `missing`
    assert not os.path.lexists(tmp / "missing")


@given_steps("V0", "VA", "VS")
def test_trd_changes_nothing_but_the_out_file(trd_repo):
    """@prd T-267.3"""
    tmp = trd_repo
    folders = [orders(tmp), tmp / ".prd-toolkit"]
    before = [snapshot(folder) for folder in folders]
    status_before = porcelain_lines(tmp)
    r = run(tmp, "python TRD docs/prd/orders --out view.md")
    assert r.exit == 0, r.err
    assert r.stdout == "wrote view.md\n".encode("utf-8")
    # effect: every file under ORDERS and <tmp>/.prd-toolkit is unchanged, and none was added or removed
    for folder, old in zip(folders, before):
        assert snapshot(folder) == old, f"{folder} changed"
    # effect: git status --porcelain lines after, in any order, are those before plus `?? view.md`
    assert Counter(porcelain_lines(tmp)) == Counter(status_before + ["?? view.md"])
