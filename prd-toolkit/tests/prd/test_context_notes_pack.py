"""Characterization tests of the context-notes area (docs/prd/prd-toolkit/test-cases/context-notes.yaml).

Every input and expected value comes from the test cases T-072.1 and T-072.2, AC-072.1 and AC-072.2
(features/context-notes.md), and testing.md (Harness, Fixtures, Setup steps).
"""
from __future__ import annotations

import json

from context_notes_support import (  # noqa: F401  (scratch is a pytest fixture)
    given_steps,
    json_equal,
    one_json_line,
    pack_part_lines,
    pack_part_titles,
    parts_of,
    run_context,
    scratch,
)

ORDERS = "docs/prd/orders"


def _assert_clean(result, label: str) -> None:
    """each_run: exit 0 and an empty stderr."""
    assert result.exit == 0, f"{label}: exit {result.exit}, stderr:\n{result.stderr}"
    assert result.stderr == "", f"{label}: stderr is not empty:\n{result.stderr!r}"


AREA_NOTES_LINES = [
    "## Area notes",
    "",
    "Words used below. A **header line** is the first line of an import file;",
    "  an **order key** is the order's number and its date.",
    "",
    "The importer reads one file at a time. <!-- an inline comment, kept with its line -->",
    "",
]

NOTES = (
    "Words used below. A **header line** is the first line of an import file;"
    "\n"
    "  an **order key** is the order's number and its date."
    "\n\n"
    "The importer reads one file at a time. <!-- an inline comment, kept with its line -->"
)


@given_steps("N0", "CN1")
def test_area_notes_part(scratch):
    """@prd T-072.1"""
    tmp = scratch
    run_1 = run_context(tmp, ORDERS, "--area", "import", "--req", "FR-001", "--for", "decide")
    run_2 = run_context(tmp, ORDERS, "--area", "import", "--for", "implement")
    run_3 = run_context(tmp, ORDERS, "--area", "import", "--req", "FR-001", "--json")
    for label, result in (("run_1", run_1), ("run_2", run_2), ("run_3", run_3)):
        _assert_clean(result, label)

    # run_1
    assert pack_part_titles(run_1.stdout) == [
        "## Header", "## Stack", "## Glossary", "## Area notes", "## Requirements", "## Cited",
        "## Known defects", "## Open questions", "## History",
    ], run_1.stdout
    assert pack_part_lines(run_1.stdout, "Area notes") == AREA_NOTES_LINES, run_1.stdout

    # run_2
    assert pack_part_titles(run_2.stdout) == [
        "## Header", "## Stack", "## Glossary", "## Area notes", "## Requirements", "## Code", "## Levels",
        "## Cited", "## Known defects", "## Open questions", "## History",
    ], run_2.stdout
    assert pack_part_lines(run_2.stdout, "Area notes") == AREA_NOTES_LINES, run_2.stdout

    # relations: run_3's stdout is one line ending in a newline, one JSON object
    doc = one_json_line(run_3.stdout)
    parts = doc["parts"]
    assert isinstance(parts, list), f"`parts` is not a list: {parts!r}"
    titles = [p.get("title") if isinstance(p, dict) else None for p in parts]
    assert "Requirements" in titles, f"no entry of `parts` has the title Requirements: {titles}"
    r = titles.index("Requirements")
    assert r >= 1, f"no entry comes directly before the first Requirements entry: {titles}"
    n = r - 1
    entry = parts[n]

    expected = {
        "title": "Area notes", "id": None, "file": "features/import.md", "line": 7, "text": NOTES,
        "stale": False, "counted": True, "moved": None,
    }
    assert isinstance(entry, dict), f"N is not an object: {entry!r}"
    assert json_equal(entry, expected), f"N: {json.dumps(entry)} != {json.dumps(expected)}"
    assert list(entry.keys()) == ["title", "id", "file", "line", "text", "stale", "counted", "moved"], \
        f"N's keys: {list(entry.keys())}"

    assert n >= 1, f"no entry comes directly before N: {titles}"
    assert titles[n - 1] == "Glossary", f"the entry before N is {titles[n - 1]!r}, not Glossary: {titles}"
    others = [i for i, t in enumerate(titles) if t == "Area notes" and i != n]
    assert others == [], f"entries other than N with the title Area notes, at {others}: {titles}"


QUIET_TITLES = [
    "## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Levels", "## Cited",
    "## Known defects", "## Open questions", "## History",
]


@given_steps("N0", "CN2", "CNB")
def test_no_area_notes_pack_unchanged(scratch):
    """@prd T-072.2"""
    tmp = scratch
    run_1 = run_context(tmp, ORDERS, "--area", "import", "--for", "implement")
    run_2 = run_context(tmp / "b", ORDERS, "--area", "import", "--for", "implement")
    run_3 = run_context(tmp, ORDERS, "--area", "import", "--req", "FR-001", "--json")
    for label, result in (("run_1", run_1), ("run_2", run_2), ("run_3", run_3)):
        _assert_clean(result, label)

    assert pack_part_titles(run_1.stdout) == QUIET_TITLES, run_1.stdout
    assert pack_part_titles(run_2.stdout) == QUIET_TITLES, run_2.stdout

    # relations: every part of run_1 other than Header equals, line for line, the part of the same title in run_2
    parts_1 = dict(parts_of(run_1.stdout))
    parts_2 = dict(parts_of(run_2.stdout))
    for title, lines in parts_1.items():
        if title == "Header":
            continue
        assert title in parts_2, f"run_2 has no part {title!r}"
        assert lines == parts_2[title], (
            f"part {title!r} differs:\nrun_1:\n" + "\n".join(lines) + "\nrun_2:\n" + "\n".join(parts_2[title]))

    # relations: the Header parts have the same number of lines and differ in one line at most, and a line that
    # differs starts with `pack ` in both runs
    header_1, header_2 = parts_1["Header"], parts_2["Header"]
    assert len(header_1) == len(header_2), (
        f"Header parts differ in length: {len(header_1)} != {len(header_2)}\n"
        + "\n".join(header_1) + "\n---\n" + "\n".join(header_2))
    differ = [i for i, (a, b) in enumerate(zip(header_1, header_2)) if a != b]
    assert len(differ) <= 1, f"Header parts differ in {len(differ)} lines: {[(header_1[i], header_2[i]) for i in differ]}"
    for i in differ:
        assert header_1[i].startswith("pack ") and header_2[i].startswith("pack "), (
            f"the Header line that differs does not start with `pack ` in both runs: {header_1[i]!r} / {header_2[i]!r}")

    # relations: no entry of `parts` of run_3's stdout, parsed as one JSON object, has the title Area notes
    doc = json.loads(run_3.stdout)
    assert isinstance(doc, dict), f"run_3's stdout is not a JSON object:\n{run_3.stdout}"
    parts = doc["parts"]
    assert isinstance(parts, list), f"`parts` is not a list: {parts!r}"
    titles = [p.get("title") if isinstance(p, dict) else None for p in parts]
    assert "Area notes" not in titles, f"an entry of `parts` has the title Area notes: {titles}"
