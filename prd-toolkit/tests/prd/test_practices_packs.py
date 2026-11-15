"""FR-056: a pack's sources (test-cases/practices.yaml)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import LINT, PK0, PK1, PK2, PK3, check, run  # noqa: E402


def test_pack_with_sources_is_listed(tmp_path, monkeypatch):
    """@prd T-056.1"""
    PK0(tmp_path, monkeypatch)
    PK1(tmp_path)
    check(run(tmp_path, LINT, "--list-packs"), exit=0, stderr="",
          stdout_contains_line="demo 1.0.0 (demo@example) — A pack for the practices cases.")


def test_malformed_sources_are_refused(tmp_path, monkeypatch):
    """@prd T-056.2"""
    PK0(tmp_path, monkeypatch)
    PK2(tmp_path)
    check(run(tmp_path, LINT, "--list-packs"), exit=0,
          stderr=(f"prd_lint: skipped {tmp_path}/plug/prd-packs/demo2: pack demo2: pack.yaml: "
                  "sources[1] must be a mapping with title, location and covers\n"
                  f"prd_lint: skipped {tmp_path}/plug/prd-packs/demo3: pack demo3: pack.yaml: "
                  "sources must be a list\n"),
          stdout_not_contains=["demo2 ", "demo3 "])


def test_no_sources_key_and_a_misspelt_key(tmp_path, monkeypatch):
    """@prd T-056.3"""
    PK0(tmp_path, monkeypatch)
    PK3(tmp_path)
    check(run(tmp_path, LINT, "--list-packs"), exit=0,
          stderr=f"prd_lint: skipped {tmp_path}/plug/prd-packs/demo5: pack demo5: pack.yaml: unknown key source\n",
          stdout_contains_line="demo4 1.0.0 (demo@example) — A pack without sources.",
          stdout_not_contains="demo5 ")
