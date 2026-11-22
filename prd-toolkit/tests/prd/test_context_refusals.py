"""The context command's refusals, interface number and JSON error document (features/context.md FR-199 to FR-202)."""
from __future__ import annotations

from context_support import (
    CXA, N0, N0X, Scratch, assert_first_line_starts, assert_last_line_starts, given, in_dir, mkdir, one_json,
    replace_line, run, scratch,  # noqa: F401  (scratch is the fixture)
)

USAGE = "usage: prd_context.py"


@given(N0)
def test_no_folder_prints_usage(scratch: Scratch):
    """@prd T-199.1"""
    for spec in ("python CTX", "python CTX --area import"):
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert_first_line_starts(r.err, USAGE)


@given(N0, mkdir("empty"))
def test_negative_context_refused_before_the_folder_is_read(scratch: Scratch):
    """@prd T-199.2"""
    for spec in ("python CTX docs/prd/orders --area import --context -1", "python CTX <tmp>/empty --context -1"):
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert r.err_b == "prd_context: --context must be 0 or more\n".encode("utf-8"), spec


@given(mkdir("empty"))
def test_folder_without_prd_md(scratch: Scratch):
    """@prd T-199.3"""
    r = run(scratch, "python CTX <tmp>/empty --area import")
    assert r.exit == 2
    assert r.out_b == b""
    assert r.err_b == f"prd_context: {scratch.real}/empty: no prd.md\n".encode("utf-8")


@given(N0)
def test_argparse_refusals(scratch: Scratch):
    """@prd T-199.4"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --for build")
    r2 = run(scratch, "python CTX docs/prd/orders --bogus")
    for r in (r1, r2):
        assert r.exit == 2
        assert r.out_b == b""
        assert_first_line_starts(r.err, USAGE)
    assert_last_line_starts(r1.err, "prd_context.py: error: argument --for: invalid choice: ")
    assert_last_line_starts(r2.err, "prd_context.py: error: unrecognized arguments: --bogus")


def _not_utf8(s: Scratch) -> None:
    (s.orders / "features/import.md").write_bytes(bytes([0xFF, 0xFE]))


@given(N0, _not_utf8)
def test_internal_error(scratch: Scratch):
    """@prd T-199.5"""
    r = run(scratch, "python CTX docs/prd/orders --area reports")
    assert r.exit == 2
    assert r.out_b == b""
    lines = r.err.splitlines()
    assert len(lines) == 1, r.err
    assert lines[0].startswith("prd_context: internal error: UnicodeDecodeError: "), r.err


@given()
def test_help(scratch: Scratch):
    """@prd T-199.6"""
    r = run(scratch, {"env": {"COLUMNS": "1000"}, "command": "python CTX --help"})
    assert r.exit == 0
    assert r.err_b == b""
    assert r.out.splitlines()[0] == (
        "usage: prd_context.py [-h] [--area AREA] [--req ID[,ID...]] [--for {decide,implement}] [--context N] "
        "[--json] [--interface] [prd_dir]"
    )


@given(mkdir("empty"))
def test_interface(scratch: Scratch):
    """@prd T-200.1"""
    for spec in ("python CTX --interface", "python CTX <tmp>/empty --interface", "python CTX --interface --json=7"):
        r = run(scratch, spec)
        assert r.exit == 0, spec
        assert r.out_b == b"1\n", spec
        assert r.err_b == b"", spec


@given(N0)
def test_json_interface_numbers(scratch: Scratch):
    """@prd T-200.2"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --json=2")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --json=1")
    r3 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --json")
    assert r1.exit == 2
    assert r1.err_b == b"prd_context: unsupported interface 2; this toolkit speaks 1\n"
    assert one_json(r1.out) == {"interface": 1, "kind": "context",
                                "error": "unsupported interface 2; this toolkit speaks 1"}
    assert r2.exit == 0
    assert r2.err_b == b""
    assert r2.out_b == r3.out_b
    assert r3.exit == 0


@given(N0)
def test_req_needs_area(scratch: Scratch):
    """@prd T-201.1"""
    for spec in ("python CTX docs/prd/orders --req FR-001", "python CTX docs/prd/orders --req FR-001 --for implement"):
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert r.err_b == b"prd_context: --req needs --area\n", spec


@given(N0)
def test_implement_needs_area(scratch: Scratch):
    """@prd T-201.2"""
    r = run(scratch, "python CTX docs/prd/orders --for implement")
    assert r.exit == 2
    assert r.out_b == b""
    assert r.err_b == b"prd_context: --for implement needs --area\n"


@given(N0)
def test_req_names_no_id(scratch: Scratch):
    """@prd T-201.3"""
    for spec in (["python", "CTX", "docs/prd/orders", "--area", "import", "--req", " , ,"],
                 ["python", "CTX", "docs/prd/orders", "--req", ""]):
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert r.err_b == b"prd_context: --req names no ID\n", spec


def _c_without_features(s: Scratch) -> None:
    folder = s.tmp / "c" / "docs/prd/orders/features"
    (folder / "import.md").unlink()
    (folder / "reports.md").unlink()


@given(CXA, in_dir(N0, "b"), in_dir(N0, "c"), _c_without_features)
def test_unknown_area(scratch: Scratch):
    """@prd T-201.4"""
    runs = [
        ("python CTX docs/prd/orders --area nope",
         "prd_context: unknown area 'nope'; areas: import, reports, billing\n"),
        ({"cwd": "<tmp>/b", "command": "python CTX docs/prd/orders --area nope"},
         "prd_context: unknown area 'nope'; areas: import, reports\n"),
        ({"cwd": "<tmp>/c", "command": "python CTX docs/prd/orders --area nope"},
         "prd_context: unknown area 'nope'; areas: none\n"),
    ]
    for spec, stderr in runs:
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert r.err_b == stderr.encode("utf-8"), spec


@given(N0X)
def test_implement_needs_a_work_tree(scratch: Scratch):
    """@prd T-201.5"""
    r = run(scratch, "python CTX docs/prd/orders --area import --for implement")
    assert r.exit == 2
    assert r.out_b == b""
    assert r.err_b == b"prd_context: --for implement needs the PRD inside a git work tree\n"


@given(N0)
def test_unknown_ids(scratch: Scratch):
    """@prd T-201.6"""
    runs = [
        ("python CTX docs/prd/orders --area import --req FR-001,fr-099,ac-001.1,T-042.1",
         "prd_context: no requirement block defines FR-099, AC-001.1, T-042.1; pass the requirement ID (FR-001), "
         "not AC-001.1; pass the requirement ID (UJ-, FR- or NFR-nnn), not T-042.1\n"),
        ("python CTX docs/prd/orders --area import --req E-009",
         "prd_context: errors.md has no entry E-009\n"),
        ("python CTX docs/prd/orders --area import --req FR-099,E-009",
         "prd_context: no requirement block defines FR-099; errors.md has no entry E-009\n"),
    ]
    for spec, stderr in runs:
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert r.err_b == stderr.encode("utf-8"), spec


def _table_in_section_8(s: Scratch) -> None:
    replace_line(s.orders / "prd.md", "Not applicable: new project.",
                 ["| Area | State | Boundary |", "|---|---|---|", "| import | adopted | `src/importer.py` |"])


@given(N0, _table_in_section_8)
def test_unmigrated_adoption_map(scratch: Scratch):
    """@prd T-201.7"""
    stderr = (f"prd_context: {scratch.real}/docs/prd/orders/prd.md: section 8: the adoption map moved to adoption.md "
              "in prd-toolkit 0.3; move the table there and leave \"See adoption.md.\"\n")
    for spec in ("python CTX docs/prd/orders --area import", "python CTX docs/prd/orders --req FR-001"):
        r = run(scratch, spec)
        assert r.exit == 2, spec
        assert r.out_b == b"", spec
        assert r.err_b == stderr.encode("utf-8"), spec


@given(N0)
def test_json_error_document(scratch: Scratch):
    """@prd T-202.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --req FR-001 --json")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --for build --json")
    assert r1.exit == 2
    assert r2.exit == 2
    assert r1.err_b == b"prd_context: --req needs --area\n"
    assert one_json(r1.out) == {"interface": 1, "kind": "context", "error": "--req needs --area"}
    assert_last_line_starts(r2.err, "prd_context.py: error: argument --for: invalid choice: ")
    doc = one_json(r2.out)
    assert list(doc.keys()) == ["interface", "kind", "error"]
    assert doc["interface"] == 1
    assert doc["kind"] == "context"
    assert doc["error"] == r2.err.splitlines()[-1][23:]
