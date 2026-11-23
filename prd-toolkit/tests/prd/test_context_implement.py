"""The Levels, Harness defaults and Rubric conventions parts of the implement pack (features/context.md FR-218,
FR-219)."""
from __future__ import annotations

import yaml

from context_support import (
    CX0, CXK, N0, REPO, Scratch, given, in_dir, insert_at, part, run,
    scratch, titles,  # noqa: F401  (scratch is the fixture)
)

DOCUMENT_PACK = REPO / "prd-toolkit" / "packs" / "document"


def _no_testing_md(s: Scratch) -> None:
    (s.tmp / "b" / "docs/prd/orders/testing.md").unlink()


@given(N0, in_dir(CX0, "b"), _no_testing_md)
def test_levels_part(scratch: Scratch):
    """@prd T-218.1"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --for implement")
    r2 = run(scratch, {"cwd": "<tmp>/b", "command": "python CTX docs/prd/orders --area import --for implement"})
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert part(r1.out, "Levels") == [
        "## Levels", "", "| Level | Harness command | Environment | Gate |", "|---|---|---|---|",
        "| unit | `pytest tests/unit` | local | build |", "| integration | `pytest tests/integration` | local | build |",
        "| judged | `pytest tests/judged` | local | build |", "",
    ]
    assert part(r2.out, "Levels") == ["## Levels", "", "None.", ""]


@given(CXK)
def test_harness_defaults_part(scratch: Scratch):
    """@prd T-219.1"""
    r = run(scratch, "python CTX docs/prd/orders --area reports --for implement")
    assert r.exit == 0
    assert r.err_b == b""
    assert titles(r.out) == [
        "## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Levels", "## Harness defaults",
        "## Rubric conventions", "## Cited", "## Known defects", "## Open questions", "## History",
    ]
    assert "Target: pack document 1.0.0 (prd-toolkit), output language en" in r.out.splitlines()
    harness = yaml.safe_load((DOCUMENT_PACK / "pack.yaml").read_text(encoding="utf-8"))["harness"]
    assert part(r.out, "Harness defaults") == (
        ["## Harness defaults", ""] + [f"- **{key}.** {value}" for key, value in harness.items()] + [""]
    )


@given(CXK)
def test_rubric_conventions_part(scratch: Scratch):
    """@prd T-219.2"""
    r = run(scratch, "python CTX docs/prd/orders --area reports --for implement")
    assert r.exit == 0
    assert r.err_b == b""
    rubrics = (DOCUMENT_PACK / "rubrics.md").read_text(encoding="utf-8")
    assert part(r.out, "Rubric conventions") == (
        ["## Rubric conventions", ""] + rubrics.rstrip("\n").splitlines() + [""]
    )


def _import_names_the_document_pack(s: Scratch) -> None:
    insert_at(s.orders / "features/import.md", 3, ["Target: pack document 1.0.0 (prd-toolkit)", ""])


@given(CXK, _import_names_the_document_pack, in_dir(CX0, "b"))
def test_parts_left_out(scratch: Scratch):
    """@prd T-219.3"""
    r1 = run(scratch, "python CTX docs/prd/orders --area import --for implement")
    r2 = run(scratch, {"cwd": "<tmp>/b", "command": "python CTX docs/prd/orders --area reports --for implement"})
    for r in (r1, r2):
        assert r.exit == 0
        assert r.err_b == b""
    assert titles(r1.out) == [
        "## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Levels", "## Harness defaults",
        "## Cited", "## Known defects", "## Open questions", "## History",
    ]
    assert titles(r2.out) == [
        "## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Levels", "## Cited",
        "## Known defects", "## Open questions", "## History",
    ]
