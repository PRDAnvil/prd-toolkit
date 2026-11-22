"""lint-contracts FR-182: run each custom type's validator and report its failure.

Every input and expected value comes from docs/prd/prd-toolkit/test-cases/lint-contracts.yaml
and features/lint-contracts.md.
"""
from __future__ import annotations

import shutil

import pytest

from lint_contracts_support import (
    KnownFailure,
    S0,
    assert_contains,
    assert_contains_line,
    run_lint,
)

PRD_MD = "docs/prd/orders/prd.md"
FINDING = f"{PRD_MD}:80: contracts-valid: custom type lookml: "


@pytest.fixture
def no_such_validator():
    """T-182.3's note: no file named no-such-validator-xyz is on the runner's PATH."""
    if shutil.which("no-such-validator-xyz") is not None:
        raise RuntimeError("no-such-validator-xyz is on PATH: T-182.3's precondition does not hold")


def test_t182_1_validator_exit_0_gets_no_finding(tmp_path, monkeypatch):
    """@prd T-182.1"""
    p = S0(tmp_path, monkeypatch)
    p.replace(
        "prd.md",
        80,
        """| lookml | `contracts/custom/*.lkml` | `python3 -c "import os, sys; sys.exit(0 if sys.argv[1:] == """
        """['contracts/custom/sample.lkml'] and os.path.isfile('prd.md') else 1)"` |""",
    )
    r = run_lint(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout == ""
    assert r.stderr == ""


def test_t182_2_validator_does_not_parse(tmp_path, monkeypatch):
    """@prd T-182.2"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, '| lookml | `contracts/custom/*.lkml` | `python3 -c "import sys` |')
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator does not parse: No closing quotation")
    assert r.stderr == ""


def test_t182_3_validator_not_found(tmp_path, monkeypatch, no_such_validator):
    """@prd T-182.3"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, "| lookml | `contracts/custom/*.lkml` | `no-such-validator-xyz` |")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator not found: no-such-validator-xyz")
    assert r.stderr == ""


def test_t182_4_validator_not_executable(tmp_path, monkeypatch):
    """@prd T-182.4"""
    p = S0(tmp_path, monkeypatch)
    p.write("tools/check.sh", "exit 0")
    p.replace("prd.md", 80, "| lookml | `contracts/custom/*.lkml` | `./tools/check.sh` |")
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator not executable: ./tools/check.sh")
    assert r.stderr == ""


def test_t182_5_validator_timed_out(tmp_path, monkeypatch):
    """@prd T-182.5"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, '| lookml | `contracts/custom/*.lkml` | `python3 -c "import time; time.sleep(5)"` |')
    r = run_lint(tmp_path, env={"PRD_VALIDATOR_TIMEOUT": "1"})
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator timed out after 1s")
    assert r.stderr == ""


def test_t182_6_timeout_not_an_integer_uses_default(tmp_path, monkeypatch):
    """@prd T-182.6"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, '| lookml | `contracts/custom/*.lkml` | `python3 -c "import time; time.sleep(2)"` |')
    r = run_lint(tmp_path, env={"PRD_VALIDATOR_TIMEOUT": "soon"})
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout == ""
    assert r.stderr == ""


def test_t182_7_failed_reports_first_non_blank_stderr_line(tmp_path, monkeypatch):
    """@prd T-182.7"""
    p = S0(tmp_path, monkeypatch)
    p.replace(
        "prd.md",
        80,
        """| lookml | `contracts/custom/*.lkml` | `python3 -c "import sys; print('out line'); """
        """print(' ', file=sys.stderr); print('err line', file=sys.stderr); sys.exit(2)"` |""",
    )
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator failed: err line")
    assert r.stderr == ""


def test_t182_8_failed_reports_first_non_blank_stdout_line(tmp_path, monkeypatch):
    """@prd T-182.8"""
    p = S0(tmp_path, monkeypatch)
    p.replace(
        "prd.md",
        80,
        """| lookml | `contracts/custom/*.lkml` | `python3 -c "import sys; print(); print('  '); """
        """print('bad: x'); print('second'); sys.exit(1)"` |""",
    )
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator failed: bad: x")
    assert r.stderr == ""


def test_t182_9_failed_with_no_output_reports_exit_code(tmp_path, monkeypatch):
    """@prd T-182.9"""
    p = S0(tmp_path, monkeypatch)
    p.replace("prd.md", 80, '| lookml | `contracts/custom/*.lkml` | `python3 -c "import sys; sys.exit(4)"` |')
    r = run_lint(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains_line(r.stdout, FINDING + "validator failed: exit 4")
    assert r.stderr == ""


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_t182_10_validator_cannot_run(tmp_path, monkeypatch):
    """@prd T-182.10 known-failing E-059"""
    p = S0(tmp_path, monkeypatch)
    p.write("tools/check.sh", "exit 0")
    p.make_executable("tools/check.sh")
    p.replace("prd.md", 80, "| lookml | `contracts/custom/*.lkml` | `./tools/check.sh` |")
    r = run_lint(tmp_path)
    err_lines = r.stderr.splitlines()
    if (
        r.returncode == 2
        and r.stdout == ""
        and err_lines
        and err_lines[0].startswith("prd_lint: internal error in rule contracts-valid: OSError:")
    ):
        raise KnownFailure("E-059: internal OSError, exit 2")
    assert r.returncode == 1, r.stdout + r.stderr
    assert_contains(r.stdout, FINDING + "validator cannot run: ./tools/check.sh: ")
    assert r.stderr == ""
