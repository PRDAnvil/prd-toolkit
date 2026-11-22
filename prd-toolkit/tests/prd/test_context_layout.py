"""The parts' order, the text pack's layout and the JSON context document (features/context.md FR-220, FR-221)."""
from __future__ import annotations

from context_support import (
    CXM, N0, Scratch, assert_json_at, given, in_dir, one_json, part, run,
    scratch, titles,  # noqa: F401  (scratch is the fixture)
)


@given(N0)
def test_parts_order(scratch: Scratch):
    """@prd T-220.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --for decide")
    r3 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --for implement")
    for r in (r1, r2, r3):
        assert r.exit == 0
        assert r.err_b == b""
    assert titles(r1.out) == ["## Header", "## Stack", "## Glossary", "## Requirements", "## Cited",
                              "## Known defects", "## Open questions", "## History"]
    assert titles(r3.out) == ["## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Levels",
                              "## Cited", "## Known defects", "## Open questions", "## History"]
    assert r1.out_b == r2.out_b


@given(N0)
def test_text_pack_layout(scratch: Scratch):
    """@prd T-220.2"""
    r = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    assert r.exit == 0
    assert r.err_b == b""
    assert part(r.out, "Known defects") == ["## Known defects", "", "0 open errors.md entries name no requirement", ""]
    assert part(r.out, "Open questions") == ["## Open questions", "", "0 other open questions in prd.md §13", ""]
    assert part(r.out, "History") == ["## History", "", "None."]
    # relation 1: stdout ends with `None.` and one newline, not two
    assert r.out_b.endswith(b"None.\n"), r.out
    assert not r.out_b.endswith(b"\n\n"), r.out
    # relation 2: every `## ` line is directly followed by an empty line; every one but the first stdout line
    # (`## Header`) comes directly after an empty line
    lines = r.out.splitlines()
    assert lines and lines[0] == "## Header", r.out
    part_lines = [i for i, line in enumerate(lines) if line.startswith("## ")]
    for i in part_lines:
        assert i + 1 < len(lines) and lines[i + 1] == "", f"line {i + 1} ({lines[i]}) is not followed by an empty line"
        if i != 0:
            assert lines[i - 1] == "", f"line {i + 1} ({lines[i]}) does not come directly after an empty line"
    # relation 3: the Stack part's two items are separated by exactly one empty line
    stack = part(r.out, "Stack")
    first = [i for i, line in enumerate(stack) if line == "### 1. Metadata & stack"]
    second = [i for i, line in enumerate(stack) if line == "### 4. Architecture"]
    assert len(first) == 1 and len(second) == 1, stack
    i, j = first[0], second[0]
    assert i < j, stack
    assert stack[j - 1] == "" and stack[j - 2] != "", f"the Stack items are not separated by one empty line: {stack}"


@given(N0)
def test_json_document(scratch: Scratch):
    """@prd T-221.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req fr-001 --json")
    r2 = run(scratch, "python CTX docs/prd/orders --json")
    r3 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001")
    for r in (r1, r2, r3):
        assert r.exit == 0
        assert r.err_b == b""
    doc1 = one_json(r1.out)
    assert list(doc1.keys()) == ["interface", "kind", "prd", "mode", "area", "ids", "parts"]
    assert list(doc1["parts"][0].keys()) == ["title", "id", "file", "line", "text", "stale", "counted", "moved"]
    assert_json_at(r1.out, {"interface": 1, "kind": "context", "prd": "orders", "mode": "decide", "area": "import",
                            "ids": ["FR-001"]})
    assert_json_at(r2.out, {"area": None, "ids": [], "mode": "decide"})
    titles_1 = [entry["title"] for entry in doc1["parts"]]
    assert titles_1 == ["Header", "Stack", "Stack", "Glossary", "Requirements", "Cited", "Known defects",
                        "Open questions", "History"]
    collapsed = [t for k, t in enumerate(titles_1) if k == 0 or titles_1[k - 1] != t]
    assert collapsed == [t[3:] for t in titles(r3.out)]
    assert [entry["title"] for entry in one_json(r2.out)["parts"]] == ["Header", "Stack", "Stack", "Areas", "Areas"]


@given(N0, in_dir(CXM, "b"))
def test_json_entry_fields(scratch: Scratch):
    """@prd T-221.2"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --req FR-002 --json")
    r2 = run(scratch, "python CTX docs/prd/orders --area import --req FR-001 --json")
    r3 = run(scratch, {"cwd": "<tmp>/b",
                       "command": "python CTX docs/prd/orders --area import --req FR-001 --for implement --context 0 --json"})
    for r in (r1, r2, r3):
        assert r.exit == 0
        assert r.err_b == b""
    assert_json_at(r1.out, {
        "parts.0.id": None, "parts.0.file": "prd.md", "parts.0.line": None,
        "parts.1.file": "prd.md", "parts.1.line": 11, "parts.2.line": 37,
        "parts.3.title": "Glossary", "parts.3.line": 33,
        "parts.4.id": "FR-002", "parts.4.file": "features/import.md", "parts.4.line": 10,
        "parts.5.title": "Cited", "parts.5.id": None, "parts.5.line": None, "parts.5.text": "None.",
        "parts.6.title": "Known defects", "parts.6.id": None, "parts.6.file": "errors.md", "parts.6.line": None,
        "parts.6.text": "0 open errors.md entries name no requirement",
    })
    assert_json_at(r2.out, {
        "parts.5.id": "IMPORT_NO_HEADER", "parts.5.file": "contracts/errors.yaml", "parts.5.line": 1,
        "parts.5.stale": False, "parts.5.counted": True, "parts.5.moved": None,
    })
    assert_json_at(r3.out, {
        "parts.5.title": "Code", "parts.5.id": "FR-001", "parts.5.file": "src/importer.py", "parts.5.line": 3,
        "parts.5.stale": False, "parts.5.counted": True, "parts.5.moved": 4,
        "parts.7.title": "Levels", "parts.7.file": "testing.md", "parts.7.line": 5,
    })
