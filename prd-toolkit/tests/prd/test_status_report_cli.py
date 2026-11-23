"""The status command's arguments and refusals (FR-222; test-cases/status.yaml)."""
from __future__ import annotations

from status_support import one_json_line, repo, rtmp, status, steps  # noqa: F401 (repo is a fixture)

USAGE = "usage: prd_status.py [-h] [--json] [--interface] [prd_dir]"


@steps("N0")
def test_t222_1_interface(repo):
    """@prd T-222.1"""
    for text in ("python STATUS --interface", "python STATUS --interface --json=2"):
        r = status(repo, text)
        assert (r.exit, r.out, r.err) == (0, b"1\n", b""), text


@steps("N0")
def test_t222_2_no_folder(repo):
    """@prd T-222.2"""
    r1 = status(repo, "python STATUS")
    r2 = status(repo, "python STATUS --json")
    for r in (r1, r2):
        assert r.exit == 2
        assert r.err == (USAGE + "\n").encode("utf-8")
    assert r1.out == b""
    assert one_json_line(r2.stdout) == {"interface": 1, "kind": "status", "error": USAGE}


@steps("N0")
def test_t222_3_unsupported_interface(repo):
    """@prd T-222.3"""
    r = status(repo, "python STATUS --json=2 .")
    assert r.exit == 2
    assert r.err == b"prd_status: unsupported interface 2; this toolkit speaks 1\n"
    assert one_json_line(r.stdout) == {"interface": 1, "kind": "status",
                                       "error": "unsupported interface 2; this toolkit speaks 1"}


@steps("N0")
def test_t222_4_no_prd_md(repo):
    """@prd T-222.4"""
    r1 = status(repo, "python STATUS <tmp>/nowhere", cwd=repo)
    r2 = status(repo, "python STATUS --json <tmp>/nowhere", cwd=repo)
    message = f"{rtmp(repo)}/nowhere: no prd.md"
    for r in (r1, r2):
        assert r.exit == 2
        assert r.err == f"prd_status: {message}\n".encode("utf-8")
    assert r1.out == b""
    assert one_json_line(r2.stdout) == {"interface": 1, "kind": "status", "error": message}


@steps("N0", "SU8")
def test_t222_5_table_in_section_8(repo):
    """@prd T-222.5"""
    r = status(repo, "python STATUS .")
    assert r.exit == 2
    assert r.out == b""
    expected = (f"prd_status: {rtmp(repo)}/docs/prd/orders/prd.md: section 8: the adoption map moved to adoption.md "
                'in prd-toolkit 0.3; move the table there and leave "See adoption.md."\n')
    assert r.err == expected.encode("utf-8")
