"""FR-048: the practices loader (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import (CHANGE, CONTEXT, LINT, P0, PF1, PF2, PM, PRACTICES,  # noqa: E402
                               check, run, setup)

ORDERS = "docs/prd/orders"

SOURCES = [
    {"id": "S-01", "title": "Python style guide", "location": "https://example.com/python-style",
     "covers": "Python", "read": "2026-11-01", "decision": "approved", "line": 7},
    {"id": "S-02", "title": "Team notes — imports", "location": "docs/notes/imports.md",
     "covers": "the importer", "read": "2026-11-02", "decision": "declined", "line": 8},
]


def test_no_practices_md_in_the_folder(tmp_path):
    """@prd T-048.1"""
    setup(tmp_path, P0, PM)
    runs = [
        run(tmp_path, LINT, ORDERS),
        run(tmp_path, PRACTICES, ORDERS),
        run(tmp_path, PRACTICES, "--json", ORDERS),
        run(tmp_path, CHANGE, "ids", "next", ORDERS, "S"),
        run(tmp_path, CHANGE, "ids", "next", ORDERS, "P"),
        run(tmp_path, CONTEXT, ORDERS, "--area", "import", "--for", "implement"),
    ]
    for r in runs:
        check(r, exit=0, stderr="")
    check(runs[0], stdout="")
    check(runs[1], stdout="")
    check(runs[2], stdout_json={"interface": 1, "kind": "practices", "sources": [], "practices": []})
    check(runs[3], stdout="S-01\n")
    check(runs[4], stdout="P-01\n")
    check(runs[5], pack_part_titles=["## Header", "## Stack", "## Glossary", "## Requirements", "## Code",
                                     "## Levels", "## Cited", "## Known defects", "## Open questions",
                                     "## History"])


def test_a_missing_heading_reads_no_row_of_that_kind(tmp_path):
    """@prd T-048.2"""
    setup(tmp_path, P0, PF2)
    r = run(tmp_path, PRACTICES, "--json", ORDERS)
    check(r, exit=0, stderr="",
          stdout_json={"interface": 1, "kind": "practices", "sources": SOURCES, "practices": []})


def test_cells_are_read_by_position(tmp_path):
    """@prd T-048.3"""
    setup(tmp_path, P0, PF1)
    r1 = run(tmp_path, PRACTICES, "--json", ORDERS)
    r2 = run(tmp_path, LINT, ORDERS)
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    check(r1, stdout_json={
        "interface": 1, "kind": "practices", "sources": SOURCES,
        "practices": [
            {"id": "P-01", "source": "S-01", "glob": "src/**/*.py", "applies_to": "code",
             "practice": "Each public function has a docstring; `pydoc a | less` shows it.", "line": 14},
            {"id": "P-02", "source": "S-01", "glob": "tests/*.py", "applies_to": "code",
             "practice": "Each test names the case it proves in its docstring.", "line": 15},
            {"id": "P-03", "source": "S-01", "glob": "-", "applies_to": "prd", "practice": "", "line": 16},
        ]})
    check(r2, stdout="")
