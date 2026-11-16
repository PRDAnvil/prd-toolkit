"""FR-050: list the sources and practices (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import P0, PB10, PRACTICES, check, run, setup  # noqa: E402

ORDERS = "docs/prd/orders"
P01 = "P-01 (S-01, code, src/**/*.py): Each public function has a docstring."
P02 = "P-02 (S-01, code, tests/*.py): Each test names the case it proves in its docstring."


def test_list_everything(tmp_path):
    """@prd T-050.1"""
    setup(tmp_path, P0)
    check(run(tmp_path, PRACTICES, ORDERS), exit=0, stderr="", stdout_exact_lines=[
        "S-01 (approved, read 2026-11-01): Python style guide, https://example.com/python-style; covers Python",
        "S-02 (declined, read 2026-11-02): Team notes — imports, docs/notes/imports.md; covers the importer",
        P01,
        P02,
        "P-03 (S-01, prd, -): Each acceptance criterion names one observable result.",
    ])


def test_paths_select_code_practices(tmp_path):
    """@prd T-050.2"""
    setup(tmp_path, P0)
    arg_lists = [
        ["src/orders/importer.py"],
        ["src/a.py"],                                     # `**/` stands for zero folders
        ["tests/unit/test_a.py"],                         # `*` does not cross `/`
        ["tests/test_b.py", "README.md", "src/x/y/z.py"], # table order, not path order
        ["-"],                                            # P-03's `-` is a prd practice's
        ["SRC/orders/importer.py"],                       # case counts
        ["src/orders/importer.pyc"],                      # the whole path
        ["src/orders/importer.py", "src/a.py"],           # each practice once
    ]
    runs = [run(tmp_path, PRACTICES, ORDERS, "--paths", *paths) for paths in arg_lists]
    for r in runs:
        check(r, exit=0, stderr="")
    check(runs[0], stdout_exact_lines=[P01])
    check(runs[1], stdout_exact_lines=[P01])
    check(runs[2], stdout="")
    check(runs[3], stdout_exact_lines=[P01, P02])
    check(runs[4], stdout="")
    check(runs[5], stdout="")
    check(runs[6], stdout="")
    check(runs[7], stdout_exact_lines=[P01])


def test_glob_matching_no_file(tmp_path):
    """@prd T-050.3"""
    setup(tmp_path, P0, PB10)
    r1 = run(tmp_path, PRACTICES, ORDERS, "--paths", "src/orders/importer.py")
    r2 = run(tmp_path, PRACTICES, ORDERS)
    for r in (r1, r2):
        check(r, exit=0, stderr="")
    check(r1, stdout="")
    check(r2, stdout_contains_line="P-01 (S-01, code, lib/**/*.rb): Each public function has a docstring.")
