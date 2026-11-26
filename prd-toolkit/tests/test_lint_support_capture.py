"""The lint helpers of the black-box tests capture the lint's output as bytes (E-086).

testing.md, Harness, Assertions: "a test captures a command's stdout and stderr as bytes, never in text mode
(whose newline translation turns a \\r into \\n), and compares them with the expected text encoded as UTF-8".
Each helper's lint script is pointed at a stub that writes known bytes, and the helper must hand the test
exactly those bytes, decoded as UTF-8: every carriage return kept, and output that is not UTF-8 never
turned into text that a comparison could pass.
"""
import importlib.util
from pathlib import Path

import pytest

PRD_TESTS = Path(__file__).resolve().parent / "prd"

# (support module, the name of its lint script path)
HELPERS = [("lint_contracts_support", "LINT_SCRIPT"), ("lint_ids_support", "LINT")]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"e086_{name}", PRD_TESTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stub(tmp_path: Path, stdout: bytes, stderr: bytes) -> Path:
    stub = tmp_path / "stub_lint.py"
    stub.write_text(
        "import sys\n"
        f"sys.stdout.buffer.write({stdout!r})\n"
        f"sys.stderr.buffer.write({stderr!r})\n",
        encoding="utf-8",
    )
    return stub


@pytest.mark.parametrize("name,attr", HELPERS)
def test_run_lint_keeps_every_carriage_return(tmp_path, monkeypatch, name, attr):
    module = _load(name)
    monkeypatch.setattr(module, attr, _stub(tmp_path, b"x.md:1: rule: a\r\nb\rc\n", b"\r"))
    r = module.run_lint(tmp_path)
    assert (r.returncode, r.stdout, r.stderr) == (0, "x.md:1: rule: a\r\nb\rc\n", "\r")


@pytest.mark.parametrize("name,attr", HELPERS)
def test_run_lint_never_passes_output_that_is_not_utf8(tmp_path, monkeypatch, name, attr):
    module = _load(name)
    monkeypatch.setattr(module, attr, _stub(tmp_path, b"x.md:1: rule: b\xff\n", b""))
    with pytest.raises(UnicodeDecodeError):
        module.run_lint(tmp_path)
