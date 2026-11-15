"""FR-052: refuse what it cannot read (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import P0, PRACTICES, PU1, check, one_json_line, run, setup, write_text  # noqa: E402

ORDERS = "docs/prd/orders"
USAGE = "usage: prd_practices.py [-h] [--paths PATH [PATH ...]] [--json] [--interface] prd_dir\n"


def test_no_prd_md(tmp_path):
    """@prd T-052.1"""
    write_text(tmp_path / "docs/prd/upper/PRD.md", "x\n")
    resolved = tmp_path.resolve()
    r1 = run(tmp_path, PRACTICES, "docs/prd/nothing")  # the folder does not exist
    r2 = run(tmp_path, PRACTICES, "docs/prd/upper")
    for r in (r1, r2):
        check(r, exit=2, stdout="")
    check(r1, stderr=f"prd_practices: {resolved}/docs/prd/nothing: no prd.md\n")
    check(r2, stderr=f"prd_practices: {resolved}/docs/prd/upper: no prd.md; found PRD.md; "
                     "the file name is lowercase prd.md\n")


def test_usage_errors(tmp_path):
    """@prd T-052.2"""
    env = {"COLUMNS": "40"}
    r1 = run(tmp_path, PRACTICES, env=env)
    r2 = run(tmp_path, PRACTICES, ORDERS, "--bogus", env=env)
    r3 = run(tmp_path, PRACTICES, ORDERS, "extra", env=env)
    r4 = run(tmp_path, PRACTICES, ORDERS, "--paths", env=env)
    for r in (r1, r2, r3, r4):
        check(r, exit=2, stdout="")
    check(r1, stderr=USAGE + "prd_practices.py: error: the following arguments are required: prd_dir\n")
    check(r2, stderr=USAGE + "prd_practices.py: error: unrecognized arguments: --bogus\n")
    check(r3, stderr=USAGE + "prd_practices.py: error: unrecognized arguments: extra\n")
    check(r4, stderr=USAGE + "prd_practices.py: error: argument --paths: expected at least one argument\n")


def test_internal_error(tmp_path):
    """@prd T-052.3"""
    setup(tmp_path, P0, PU1)
    check(run(tmp_path, PRACTICES, ORDERS), exit=2, stdout="",
          stderr_single_line_starts="prd_practices: internal error: UnicodeDecodeError: ",
          stderr_not_contains="Traceback")


def test_json_errors(tmp_path):
    """@prd T-052.4"""
    setup(tmp_path, P0, PU1)
    resolved = tmp_path.resolve()
    r1 = run(tmp_path, PRACTICES, "--json", "docs/prd/nothing")
    r2 = run(tmp_path, PRACTICES, "--json")
    r3 = run(tmp_path, PRACTICES, "--json", ORDERS)
    for r in (r1, r2, r3):
        check(r, exit=2)
    check(r1, stdout_json={"interface": 1, "kind": "practices",
                           "error": f"{resolved}/docs/prd/nothing: no prd.md"},
          stderr=f"prd_practices: {resolved}/docs/prd/nothing: no prd.md\n")
    check(r2, stdout_json={"interface": 1, "kind": "practices",
                           "error": "the following arguments are required: prd_dir"},
          stderr_first_line_starts="usage: prd_practices.py",
          stderr_last_line="prd_practices.py: error: the following arguments are required: prd_dir")
    check(r3, stdout_json_keys_at={"": ["interface", "kind", "error"]},
          stdout_json_at={"interface": 1, "kind": "practices"},
          stderr_single_line_starts="prd_practices: internal error: UnicodeDecodeError: ")
    # relation: run_3's `error` starts with `internal error: UnicodeDecodeError: ` and equals run_3's stderr
    # line without its `prd_practices: ` prefix and its line end
    error = one_json_line(r3)["error"]
    line = r3.stderr.splitlines()[0]
    assert error.startswith("internal error: UnicodeDecodeError: "), f"error is {error!r}"
    assert line.startswith("prd_practices: ") and error == line[len("prd_practices: "):], (
        f"error {error!r} is not the stderr line {line!r} without its prefix")


def test_unsupported_interface(tmp_path):
    """@prd T-052.5"""
    r = run(tmp_path, PRACTICES, "--json=2", "docs/prd/nothing")  # the folder does not exist, and is not read
    check(r, exit=2,
          stdout_json={"interface": 1, "kind": "practices",
                       "error": "unsupported interface 2; this toolkit speaks 1"},
          stderr="prd_practices: unsupported interface 2; this toolkit speaks 1\n")
