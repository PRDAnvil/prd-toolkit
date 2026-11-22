"""The repository pack, the Header part and the Stack part (features/context.md FR-203 to FR-205)."""
from __future__ import annotations

from context_support import (
    CXA, CXE, N0, SIZE_RE, SIZE_RE_AREA, Scratch, delete_range, given, in_dir, one_json, part, run,
    scratch, titles,  # noqa: F401  (scratch is the fixture)
)


@given(N0)
def test_repository_pack(scratch: Scratch):
    """@prd T-203.1"""
    r = run(scratch, "python CTX docs/prd/orders")
    assert r.exit == 0
    assert r.err_b == b""
    assert titles(r.out) == ["## Header", "## Stack", "## Areas"]
    header = part(r.out, "Header")
    assert len(header) == 5, header
    assert header[0] == "## Header"
    assert header[1] == ""
    assert header[2] == "PRD: docs/prd/orders version 1.0.0 mode decide"
    assert header[4] == ""
    m = SIZE_RE.fullmatch(header[3])
    assert m, header[3]
    assert m.group(3) == format((scratch.orders / "prd.md").stat().st_size, ",")


@given(CXA, in_dir(CXE, "b"))
def test_areas_from_adoption_md(scratch: Scratch):
    """@prd T-203.2"""
    r1 = run(scratch, "python CTX docs/prd/orders")
    r2 = run(scratch, {"cwd": "<tmp>/b", "command": "python CTX docs/prd/orders"})
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Areas") == [
        "## Areas", "", "- import (adopted; Boundary: src/importer.py, tests/test_orders.py)", "- reports (not started)",
    ]
    assert part(r2.out, "Areas") == ["## Areas", "", "None."]


@given(N0)
def test_areas_from_features_files(scratch: Scratch):
    """@prd T-203.3"""
    r = run(scratch, "python CTX docs/prd/orders")
    assert r.exit == 0
    assert part(r.out, "Areas") == ["## Areas", "", "- import", "- reports"]


def _header_body(out: str) -> list[str]:
    header = part(out, "Header")
    assert header[:2] == ["## Header", ""], header
    assert len(header) == 7 and header[6] == "", f"the Header part is not four lines and one closing empty line: {header}"
    return header[2:6]


@given(CXA)
def test_area_header(scratch: Scratch):
    """@prd T-204.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import")
    r2 = run(scratch, "python CTX docs/prd/orders --area reports --for implement")
    r3 = run(scratch, "python CTX docs/prd/orders --area billing")
    for r in (r1, r2, r3):
        assert r.exit == 0, r.err
        assert r.err_b == b""
    b1 = _header_body(r1.out)
    assert b1[:3] == [
        "PRD: docs/prd/orders version 1.0.0 mode decide",
        "Area: import (adopted; Boundary: src/importer.py, tests/test_orders.py)",
        "Target: pack service (default), output language en",
    ]
    assert b1[3].startswith("pack "), b1[3]
    b2 = _header_body(r2.out)
    assert b2[:3] == [
        "PRD: docs/prd/orders version 1.0.0 mode implement",
        "Area: reports (not started)",
        "Target: pack service (default), output language en",
    ]
    assert b2[3].startswith("pack "), b2[3]
    b3 = _header_body(r3.out)
    assert b3[:3] == [
        "PRD: docs/prd/orders version 1.0.0 mode decide",
        "Area: billing (-)",
        "Target: pack service (default), output language en",
    ]
    assert b3[3].startswith("pack ") and b3[3].endswith("; features/billing.md 10"), b3[3]


@given(N0)
def test_size_line(scratch: Scratch):
    """@prd T-204.2"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --json")
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    header = part(r1.out, "Header")
    last = [line for line in header if line][-1]
    m = SIZE_RE_AREA.fullmatch(last)
    assert m, last
    start = r1.out_b.find(b"\n## Stack\n")
    assert start >= 0, r1.out
    n = len(r1.out_b) - (start + 1)
    assert m.group(1) == format(n, ",")
    assert m.group(2) == format(n / 4 / 1000, ".1f")
    assert m.group(3) == format((scratch.orders / "prd.md").stat().st_size, ",")
    assert m.group(4) == format((scratch.orders / "features/import.md").stat().st_size, ",")
    assert one_json(r2.out)["parts"][0]["text"] == "\n".join(header[2:6])


def _strip_sections(s: Scratch) -> None:
    prd_md = s.tmp / "c" / "docs/prd/orders/prd.md"
    delete_range(prd_md, "## 1. Metadata & stack", "## 2. Summary & goals")
    delete_range(prd_md, "## 4. Architecture", "## 5. Standards registry")


@given(N0, in_dir(N0, "c"), _strip_sections)
def test_stack_part(scratch: Scratch):
    """@prd T-205.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, {"cwd": "<tmp>/c", "command": "python CTX docs/prd/orders --area import --req FR-001"})
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Stack") == [
        "## Stack",
        "",
        "### 1. Metadata & stack",
        "",
        "- Language: Python 3.12",
        "- Not applicable: `contracts/openapi.yaml` — no HTTP API",
        "- Not applicable: `contracts/schema.sql` — no database",
        "- Not applicable: `contracts/events.md` — no events or jobs",
        "- Not applicable: `contracts/permissions.yaml` — no roles",
        "- Not applicable: `contracts/config.yaml` — no settings",
        "- Not applicable: `contracts/data-classification.yaml` — no stored personal data",
        "- Not applicable: `contracts/dependencies/` — no third-party service",
        "- Not applicable: `contracts/fixtures/` — no fixture data",
        "",
        "### 4. Architecture",
        "",
        "The importer stores orders; the report command reads them.",
        "",
    ]
    assert part(r2.out, "Stack") == ["## Stack", "", "None.", ""]
