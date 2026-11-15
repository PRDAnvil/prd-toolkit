"""FR-055: the Practices part of the implement context pack (test-cases/practices.yaml)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import (CONTEXT, P0, P0B, PA1, PB10, check, pack_parts, run, same,  # noqa: E402
                               setup)

ORDERS = "docs/prd/orders"
P01 = "P-01 (S-01): Each public function has a docstring."
P02 = "P-02 (S-01): Each test names the case it proves in its docstring."
IMPLEMENT_TITLES = ["## Header", "## Stack", "## Glossary", "## Requirements", "## Code", "## Practices",
                    "## Levels", "## Cited", "## Known defects", "## Open questions", "## History"]


def implement(tmp_path, area, folder=ORDERS):
    return run(tmp_path, CONTEXT, folder, "--area", area, "--for", "implement")


def test_practices_part_of_the_area(tmp_path):
    """@prd T-055.1"""
    setup(tmp_path, P0)
    check(implement(tmp_path, "import"), exit=0, stderr="",
          pack_part_titles=IMPLEMENT_TITLES,
          pack_part_lines={"Practices": ["## Practices", "", P01, "", P02, ""]})


def test_paths_without_adoption_md(tmp_path):
    """@prd T-055.2"""
    setup(tmp_path, P0, PA1)
    check(implement(tmp_path, "import"), exit=0, stderr="",
          pack_part_lines={"Practices": ["## Practices", "", P01, ""]})


def test_glob_matching_no_path_of_the_area(tmp_path):
    """@prd T-055.3"""
    setup(tmp_path, P0, PB10)
    check(implement(tmp_path, "import"), exit=0, stderr="",
          pack_part_lines={"Practices": ["## Practices", "", P02, ""]})


def test_no_practice_matches(tmp_path):
    """@prd T-055.4"""
    setup(tmp_path, P0)
    check(implement(tmp_path, "reports"), exit=0, stderr="",
          pack_part_lines={"Practices": ["## Practices", "", "None.", ""]})


def test_pack_unchanged_but_for_the_part(tmp_path):
    """@prd T-055.5"""
    setup(tmp_path, P0, P0B)
    r1 = run(tmp_path, CONTEXT, ORDERS, "--area", "import")
    r2 = implement(tmp_path, "import")
    r3 = implement(tmp_path, "import", folder=str(tmp_path / "b" / ORDERS))
    for r in (r1, r2, r3):
        check(r, exit=0, stderr="")
    check(r1, pack_part_titles=["## Header", "## Stack", "## Glossary", "## Requirements", "## Cited",
                                "## Known defects", "## Open questions", "## History"])
    check(r2, pack_part_titles=IMPLEMENT_TITLES)
    check(r3, pack_part_titles=["## Header", "## Stack", "## Glossary", "## Requirements", "## Code",
                                "## Levels", "## Cited", "## Known defects", "## Open questions",
                                "## History"])

    # relation 1: every part of run_2 other than Header and Practices equals, line for line, the part of the
    # same title in run_3
    parts2 = pack_parts(r2.stdout)
    parts3 = dict(pack_parts(r3.stdout))
    for title, lines in parts2:
        if title in ("Header", "Practices"):
            continue
        assert title in parts3, f"run_3 has no part {title!r}"
        assert lines == parts3[title], f"part {title!r}: run_2 {lines!r} != run_3 {parts3[title]!r}"

    # relation 2: the Header parts have the same number of lines; each holds exactly one line starting `PRD: `
    # and exactly one starting `pack `, at the same positions in both; every other line is equal in both
    h2 = dict(parts2)["Header"]
    h3 = parts3["Header"]
    assert len(h2) == len(h3), f"Header parts differ in length: {h2!r} vs {h3!r}"
    for prefix in ("PRD: ", "pack "):
        at2 = [i for i, line in enumerate(h2) if line.startswith(prefix)]
        at3 = [i for i, line in enumerate(h3) if line.startswith(prefix)]
        assert len(at2) == 1 and len(at3) == 1 and at2 == at3, (
            f"lines starting {prefix!r}: run_2 at {at2}, run_3 at {at3}")
    for i, (a, b) in enumerate(zip(h2, h3)):
        if a.startswith(("PRD: ", "pack ")):
            continue
        assert a == b, f"Header line {i}: run_2 {a!r} != run_3 {b!r}"


def test_practices_items_in_json(tmp_path):
    """@prd T-055.6"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, CONTEXT, "--json", ORDERS, "--area", "import", "--for", "implement")
    r2 = run(tmp_path, CONTEXT, "--json", ORDERS, "--area", "reports", "--for", "implement")
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    parts1 = json.loads(r1.stdout)["parts"]
    parts2 = json.loads(r2.stdout)["parts"]

    # relation 1: run_1's Practices entries are exactly these two, in order
    want1 = [
        {"title": "Practices", "id": "P-01", "file": "practices.md", "line": 14, "text": P01,
         "stale": False, "counted": True, "moved": None},
        {"title": "Practices", "id": "P-02", "file": "practices.md", "line": 15, "text": P02,
         "stale": False, "counted": True, "moved": None},
    ]
    got1 = [p for p in parts1 if p.get("title") == "Practices"]
    assert same(got1, want1), f"run_1 Practices entries {got1!r} != {want1!r}"

    # relation 2: the two come directly after the last Code entry and directly before the first Levels entry
    at = [i for i, p in enumerate(parts1) if p.get("title") == "Practices"]
    code = [i for i, p in enumerate(parts1) if p.get("title") == "Code"]
    levels = [i for i, p in enumerate(parts1) if p.get("title") == "Levels"]
    assert code and levels, f"run_1 has no Code or no Levels entry: {parts1!r}"
    assert at == [code[-1] + 1, code[-1] + 2], f"Practices at {at}, last Code at {code[-1]}"
    assert levels[0] == at[-1] + 1, f"first Levels at {levels[0]}, last Practices at {at[-1]}"

    # relation 3: run_2's Practices entries are exactly the one None. entry
    want2 = [{"title": "Practices", "id": None, "file": "practices.md", "line": None, "text": "None.",
              "stale": False, "counted": True, "moved": None}]
    got2 = [p for p in parts2 if p.get("title") == "Practices"]
    assert same(got2, want2), f"run_2 Practices entries {got2!r} != {want2!r}"
