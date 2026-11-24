"""lint-contracts FR-181: resolve each section 7 custom type to its files and validator.

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml
and features/lint-contracts.md.
"""
from __future__ import annotations

import pytest

from lint_contracts_support import (
    KnownFailure,
    S0,
    assert_contains_line,
    assert_exact_lines,
    assert_not_contains,
    run_lint,
)

PRD_MD = "docs/prd/orders/prd.md"


@pytest.fixture
def plain_tmp(tmp_path):
    """T-181.7's header precondition: <tmp> holds no white space, comma or * ? [ ]."""
    text = str(tmp_path)
    bad = [c for c in text if c.isspace() or c in ",*?[]"]
    if bad:
        raise RuntimeError(f"temporary folder {text!r} breaks the T-181.7 precondition: {bad!r}")
    return tmp_path


def test_t181_1_files_split_deduplicated_and_sorted(tmp_path, monkeypatch):
    """@prd T-181.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace(
        "prd.md",
        80,
        '| lookml | `contracts/custom/*.lkml, contracts/custom/a.lkml` | '
        '`python3 -c "import sys; print(*sys.argv[1:], file=sys.stderr); sys.exit(1)"` |',
    )
    p.write("contracts/custom/b.lkml", "view: b")
    p.write("contracts/custom/a.lkml", "view: a")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(
        r.stdout,
        f"{PRD_MD}:80: contracts-valid: custom type lookml: validator failed: "
        "contracts/custom/a.lkml contracts/custom/b.lkml contracts/custom/sample.lkml",
    )
    assert r.stderr == ""


def test_t181_2_pack_validator_with_no_named_pack(tmp_path, monkeypatch):
    """@prd T-181.2"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, "| lookml | `contracts/custom/*.lkml` | pack |")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(
        r.stdout,
        f"{PRD_MD}:80: contracts-valid: custom type lookml: no named pack declares contract type lookml",
    )
    assert r.stderr == ""


def test_t181_3_pack_validator_from_named_pack(tmp_path, monkeypatch):
    """@prd T-181.3"""
    p = S0(tmp_path, monkeypatch)
    p.insert_after("prd.md", 19, "- Pack: document 1.0.0 (prd-toolkit)")
    p.replace("prd.md", 80, "| outline | `contracts/none/*.yaml` | pack |")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, f"{PRD_MD}:81: contracts-valid: custom type outline: glob matches no file")
    assert_not_contains(r.stdout, "no named pack declares contract type outline")
    assert r.stderr == ""


def test_t181_4_glob_matches_no_file_runs_no_validator(tmp_path, monkeypatch):
    """@prd T-181.4"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, '| lookml | `contracts/custom/*.nope` | `python3 -c "import sys; sys.exit(1)"` |')
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, f"{PRD_MD}:80: contracts-valid: custom type lookml: glob matches no file")
    assert_not_contains(r.stdout, "validator failed")
    assert r.stderr == ""


def test_t181_5_built_in_row_is_no_custom_type(tmp_path, monkeypatch):
    """@prd T-181.5"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, "| lookml | `contracts/custom/*.nope` | built-in |")
    r = run_lint(tmp_path)
    assert_not_contains(r.stdout, "custom type lookml")
    assert r.stderr == ""


def test_t181_6_file_outside_prd_folder_by_dotdot(tmp_path, monkeypatch):
    """@prd T-181.6"""
    p = S0(tmp_path, monkeypatch)
    outside = tmp_path / "docs" / "prd" / "outside.lkml"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_bytes("view: outside {}\n".encode("utf-8"))
    p.write("tools/args.py", "import sys; sys.exit(sys.argv[1:] != ['contracts/custom/sample.lkml'])")
    p.replace("prd.md", 80, "| lookml | `contracts/custom/*.lkml ../outside.lkml` | `python3 tools/args.py` |")
    r = run_lint(tmp_path)
    symptom = [f"{PRD_MD}:80: contracts-valid: custom type lookml: validator failed: exit 1"]
    if r.stdout.splitlines() == symptom:
        raise KnownFailure("E-063: stdout holds only the validator-failed line")
    assert r.returncode == 1, r.stdout + r.stderr
    assert_exact_lines(
        r.stdout,
        [f"{PRD_MD}:80: contracts-valid: custom type lookml: file ../outside.lkml is outside the PRD folder"],
    )
    assert r.stderr == ""


def test_t181_7_file_outside_prd_folder_by_absolute_glob(plain_tmp, monkeypatch):
    """@prd T-181.7"""
    tmp = plain_tmp
    p = S0(tmp, monkeypatch)
    outside = tmp / "docs" / "prd" / "outside.lkml"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_bytes("view: outside {}\n".encode("utf-8"))
    p.replace("prd.md", 80, f'| lookml | `{tmp}/docs/prd/outside.lkml` | `python3 -c "import sys; sys.exit(0)"` |')
    r = run_lint(tmp)
    if r.returncode == 0 and r.stdout == "":
        raise KnownFailure("E-063: exit 0 and empty stdout")
    assert r.returncode == 1, r.stdout + r.stderr
    assert_exact_lines(
        r.stdout,
        [
            f"{PRD_MD}:80: contracts-valid: custom type lookml: file {tmp}/docs/prd/outside.lkml is outside the PRD folder",
            f"{PRD_MD}:80: contracts-valid: custom type lookml: glob matches no file",
        ],
    )
    assert r.stderr == ""
