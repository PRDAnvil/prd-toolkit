"""FR-051: print the record as one JSON document (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import P0, PRACTICES, check, one_json_line, run, same, setup  # noqa: E402

ORDERS = "docs/prd/orders"

SOURCES = [
    {"id": "S-01", "title": "Python style guide", "location": "https://example.com/python-style",
     "covers": "Python", "read": "2026-11-01", "decision": "approved", "line": 7},
    {"id": "S-02", "title": "Team notes — imports", "location": "docs/notes/imports.md",
     "covers": "the importer", "read": "2026-11-02", "decision": "declined", "line": 8},
]
P02 = {"id": "P-02", "source": "S-01", "glob": "tests/*.py", "applies_to": "code",
       "practice": "Each test names the case it proves in its docstring.", "line": 15}


def test_the_json_document(tmp_path):
    """@prd T-051.1"""
    setup(tmp_path, P0)
    r = run(tmp_path, PRACTICES, "--json", ORDERS)
    check(r, exit=0, stderr="",
          stdout_json_keys_at={
              "": ["interface", "kind", "sources", "practices"],
              "sources.0": ["id", "title", "location", "covers", "read", "decision", "line"],
              "practices.0": ["id", "source", "glob", "applies_to", "practice", "line"],
          },
          stdout_json={
              "interface": 1, "kind": "practices", "sources": SOURCES,
              "practices": [
                  {"id": "P-01", "source": "S-01", "glob": "src/**/*.py", "applies_to": "code",
                   "practice": "Each public function has a docstring.", "line": 14},
                  P02,
                  {"id": "P-03", "source": "S-01", "glob": "-", "applies_to": "prd",
                   "practice": "Each acceptance criterion names one observable result.", "line": 16},
              ]},
          stdout_contains="notes — imports",
          stdout_not_contains="\\u2014")
    assert "notes — imports".encode("utf-8") in r.stdout_bytes  # the bytes e2 80 94


def test_json_with_paths(tmp_path):
    """@prd T-051.2"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, PRACTICES, "--json", ORDERS, "--paths", "tests/test_b.py")
    r2 = run(tmp_path, PRACTICES, "--json", ORDERS)
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    check(r1, stdout_json_at={"practices": [P02]})
    # relation: run_1's `sources` list equals run_2's `sources` list
    s1 = one_json_line(r1)["sources"]
    s2 = one_json_line(r2)["sources"]
    assert same(s1, s2), f"run_1 sources {s1!r} != run_2 sources {s2!r}"


def test_json_equals_1(tmp_path):
    """@prd T-051.3"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, PRACTICES, "--json=1", ORDERS)
    r2 = run(tmp_path, PRACTICES, "--json", ORDERS)
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    # relation: run_1's stdout equals run_2's stdout, byte for byte
    assert r1.stdout_bytes == r2.stdout_bytes, f"{r1!r} != {r2!r}"


def test_interface(tmp_path):
    """@prd T-051.4"""
    arg_lists = [
        ["--interface"],
        ["--interface", "--json=2"],
        ["--interface", "docs/prd/nothing"],  # the folder does not exist, and is not read
        ["--interface", "--bogus"],
    ]
    for args in arg_lists:
        check(run(tmp_path, PRACTICES, *args), exit=0, stderr="", stdout="1\n")
