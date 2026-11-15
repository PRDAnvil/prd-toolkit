"""Helpers for the help black-box tests (docs/prd/prd-toolkit/test-cases/help.yaml).

Everything here follows docs/prd/prd-toolkit/testing.md (Harness, Fixtures, Assertions) and the
conventions at the top of test-cases/help.yaml. The fixture loaders S0, M1 and repo/vendored are
the lint-cli helper's (lint_cli_support.py), since testing.md defines them once for both areas.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from lint_cli_support import Run, load_vendored, m1, s0  # noqa: F401  (re-exported for the tests)

# <repo> is the repository root: prd-toolkit/tests/prd/<this file>.
REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "prd-toolkit" / "scripts"
HELP = SCRIPTS / "prd_help.py"
LINT = SCRIPTS / "prd_lint.py"
PRD_DIR = REPO / "docs" / "prd" / "prd-toolkit"
FIXTURES = PRD_DIR / "contracts" / "fixtures"
# FIX: the absolute path of fixture help/catalogue (testing.md, Fixtures).
FIX = FIXTURES / "help" / "catalogue.yaml"
CLI_YAML = PRD_DIR / "contracts" / "cli.yaml"
# The catalogue the toolkit ships, when it runs from the plugin (AC-037.2).
SHIPPED = REPO / "prd-toolkit" / "references" / "help.yaml"

# RULES: the 40 rule names of T-003.1 (test-cases/lint-cli.yaml), sorted; platform-word is the
# only one of severity warn.
RULES = [
    "ac-ears", "ac-has-test", "assumption-indexed", "change-sets",
    "classified-fixtures", "contracts-valid", "deny-tested", "drift-rows",
    "error-codes", "error-entries", "fr-has-ac", "frontmatter",
    "glossary-synonym", "id-format", "id-removed-reused", "id-unique",
    "index-consistent", "judged-case", "language-table", "links-format",
    "markers-open", "nfr-bound", "open-questions-empty", "pack-resolves",
    "placeholder", "platform-word", "production-gate", "registries",
    "runbook-env", "runbook-steps", "runbook-tests", "schema-refs",
    "sections", "snapshot-cited", "sufficiency", "test-cases-consistent",
    "test-level", "test-refs", "upstream-refs", "vague-word",
]

# Dropped from the runner's environment (testing.md, Harness, Subprocess environment).
_DROPPED = ("PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE")


def run(args, cwd: Path, *, catalogue: bool = False, case_env: dict | None = None,
        env: dict | None = None, script: Path = HELP) -> Run:
    """Run `python <script> <args>` as a subprocess in `cwd`, capturing stdout and stderr as bytes.

    The environment is the test process's (with any monkeypatch changes) minus PYTHONIOENCODING,
    PYTHONPATH, PYTHONHOME, PRD_LINT_CI and PRD_HELP_FILE; then PRD_HELP_FILE=FIX when
    `catalogue` (the case's preconditions name help/catalogue); then the case's own `case_env`;
    then the run's own `env`, which wins over the fixture's PRD_HELP_FILE.
    """
    full_env = dict(os.environ)
    for name in _DROPPED:
        full_env.pop(name, None)
    if catalogue:
        full_env["PRD_HELP_FILE"] = str(FIX)
    if case_env:
        full_env.update(case_env)
    if env:
        full_env.update(env)
    proc = subprocess.run(
        [sys.executable, str(script), *[str(a) for a in args]],
        cwd=str(cwd),
        env=full_env,
        capture_output=True,
        timeout=300,
    )
    return Run(proc)


def write_lines(path: Path, lines: list[str]) -> Path:
    """Write `lines` to `path`, each ending in a newline, as UTF-8."""
    path.write_bytes("".join(line + "\n" for line in lines).encode("utf-8"))
    return path


def json_doc(r: Run):
    """The one-line requirement of stdout_json, stdout_json_at and stdout_json_keys_at (testing.md,
    Assertions): the whole stdout is one line ending in a newline, parsed as one JSON object."""
    out = r.stdout
    assert out.endswith("\n"), f"stdout does not end in a newline: {out!r}"
    assert "\n" not in out[:-1], f"stdout is more than one line: {out!r}"
    doc = json.loads(out)
    assert isinstance(doc, dict), f"stdout is not a JSON object: {out!r}"
    return doc


def at(doc, path: str):
    """The value at a path of object keys and list indexes joined by `.`; "" is the document."""
    node = doc
    if path == "":
        return node
    for part in path.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        else:
            assert isinstance(node, dict), f"{path}: {part!r} reached a {type(node).__name__}"
            assert part in node, f"{path}: no key {part!r}"
            node = node[part]
    return node


def keys_at(doc, path: str) -> list:
    """stdout_json_keys_at: the keys of the object at `path`, in order."""
    node = at(doc, path)
    assert isinstance(node, dict), f"{path!r} is not an object: {node!r}"
    return list(node.keys())


def json_equal(a, b) -> bool:
    """Equality of two JSON values that keeps a bool apart from a number and a string apart from a
    number (a YAML scalar compared as the JSON value it reads as); object key order is not compared."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) or isinstance(b, (int, float)):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and a == b
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys()
                and all(json_equal(a[k], b[k]) for k in a))
    if isinstance(a, list) or isinstance(b, list):
        return (isinstance(a, list) and isinstance(b, list) and len(a) == len(b)
                and all(json_equal(x, y) for x, y in zip(a, b)))
    return type(a) is type(b) and a == b


def assert_json_at(doc, expected: dict) -> None:
    """stdout_json_at: the value at each path equals the mapping's; nothing else is compared."""
    for path, want in expected.items():
        got = at(doc, path)
        assert json_equal(got, want), f"at {path!r}: {got!r} != {want!r}"


@pytest.fixture(name="vendored")
def vendored_fixture(tmp_path) -> Path:
    """Fixture repo/vendored, loaded into <tmp>/.prd-toolkit with its check.

    The check runs in pytest's setup phase, so a mismatch ends the test as an error, not a failure
    (testing.md, Fixtures). Returns <tmp>/.prd-toolkit.
    """
    return load_vendored(tmp_path)
