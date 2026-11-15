"""prd_status.py: the Next part (status-next); the builder's unit tests."""
import os
import subprocess
from pathlib import Path

import yaml

import prd_status
from prdlint import nextpart

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "docs/prd/prd-toolkit/contracts/fixtures/status-next"
# the Subprocess environment (testing.md Harness) minus the git variables of Setup steps
DROPPED = ("PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
           "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR")


def _n0(tmp: Path, monkeypatch) -> Path:
    """Setup step N0: write fixture status-next/base under tmp, then `git init -q`; no commit."""
    for name in DROPPED:
        monkeypatch.delenv(name, raising=False)
    base = yaml.safe_load((FIXTURES / "base.yaml").read_text(encoding="utf-8"))
    for key, text in base.items():
        path = tmp / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True, capture_output=True, env=dict(os.environ))
    return tmp / "docs/prd/orders"


def test_next_part_error_fails_the_report(tmp_path, monkeypatch, capsys):
    """@prd T-040.3"""
    orders = _n0(tmp_path, monkeypatch)
    monkeypatch.chdir(orders)

    def boom(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(nextpart, "next_items", boom)

    code = prd_status.main(["."])
    out, err = capsys.readouterr()
    assert code == 2
    assert err.splitlines() == ["prd_status: internal error: ValueError: boom"]
    assert out == ""

    code = prd_status.main(["--json", "."])
    out, err = capsys.readouterr()
    assert code == 2
    assert err.splitlines() == ["prd_status: internal error: ValueError: boom"]
    assert out.splitlines() == ['{"interface": 1, "kind": "status", "error": "internal error: ValueError: boom"}']
