"""The pre-commit hook (FR-094): test-cases/trace.yaml T-094.1 to T-094.5.

Each case writes its section 5 rows with step TR (glob `**/*.py`, Rules live in `-`, Applies to `code`, the
linter in backticks unless the case says otherwise), stages src/app.py (TB, TX), and runs
`python HOOK pre-commit docs/prd/orders` in <tmp>.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from trace_support import (  # noqa: F401
    TR, SetupError, assert_single_line_starts, given_steps, run_hook, scratch, standards_row, subprocess_env,
)


def tr(*rows: str):
    def step(tmp: Path) -> None:
        TR(tmp, list(rows))
    step.__name__ = "TR"
    return step


def pre_commit(tmp: Path):
    return run_hook(tmp, "pre-commit", "docs/prd/orders")


# T-094.1: three rows, each exactly `| `**/*.py` | `L` | - | code | D |`, except that the enforced row's Linter
# command cell holds L with no backticks around it.
DECLINED_L = "python3 -c \"open('declined.log','w').write('x')\""
PROPOSED_L = "python3 -c \"open('proposed.log','w').write('x')\""
BARE_L = "python3 -c \"open('bare.log','w').write('x')\""


@given_steps(
    "N0E",
    tr(f"| `**/*.py` | `{DECLINED_L}` | - | code | declined |",
       f"| `**/*.py` | `{PROPOSED_L}` | - | code | proposed |",
       f"| `**/*.py` | {BARE_L} | - | code | enforced |"),
    "TB", "TX",
)
def test_rows_not_enforced_or_without_a_backticked_command_do_not_run(scratch):
    """@prd T-094.1"""
    r = pre_commit(scratch)
    assert (r.exit, r.stdout, r.stderr) == (0, "", ""), r
    for name in ("declined.log", "proposed.log", "bare.log"):
        assert not (scratch / name).exists(), f"<tmp>/{name} exists"


NOSUCH = "nosuch-linter-xyz"


def tr_nosuch(tmp: Path) -> None:
    """TR: one enforced row with linter `nosuch-linter-xyz --check`; a program of that name on PATH ends the test
    as an error."""
    found = shutil.which(NOSUCH, path=subprocess_env().get("PATH"))
    if found is not None:
        raise SetupError(f"a program {NOSUCH} is on PATH: {found}")
    TR(tmp, [f"| `**/*.py` | `{NOSUCH} --check` | - | code | enforced |"])


tr_nosuch.__name__ = "TR"


@given_steps("N0E", tr_nosuch, "TB", "TX")
def test_a_command_that_cannot_start(scratch):
    """@prd T-094.2"""
    r = pre_commit(scratch)
    assert r.exit == 1, r
    assert r.stdout == "", r
    assert_single_line_starts(r.stderr, "prd-toolkit: `nosuch-linter-xyz --check` could not run: ")


@given_steps("N0E", tr(standards_row("`python3 -c \"x`")), "TB", "TX")
def test_a_command_that_cannot_be_split(scratch):
    """@prd T-094.3"""
    r = pre_commit(scratch)
    assert (r.exit, r.stdout, r.stderr) == (1, "", "prd-toolkit: `python3 -c \"x` could not run: No closing quotation\n"), r


@given_steps(
    "N0E",
    tr(standards_row("`python3 -c \"import sys; sys.exit(3)\"`"),
       standards_row("`python3 -c \"import sys; sys.exit(4)\"`")),
    "TB", "TX",
)
def test_each_failing_row_prints_one_line_in_row_order(scratch):
    """@prd T-094.4"""
    r = pre_commit(scratch)
    assert (r.exit, r.stdout, r.stderr) == (
        1, "",
        "prd-toolkit: `python3 -c \"import sys; sys.exit(3)\"` failed (exit 3) on src/app.py\n"
        "prd-toolkit: `python3 -c \"import sys; sys.exit(4)\"` failed (exit 4) on src/app.py\n",
    ), r


@given_steps(
    "N0E",
    tr(standards_row("`python3 -c \"import sys; open('ok.log','w').write(' '.join(sys.argv[1:]))\"`")),
    "TB", "TX",
)
def test_a_passing_row_runs_from_the_repository_root_on_the_staged_path(scratch):
    """@prd T-094.5"""
    r = pre_commit(scratch)
    assert (r.exit, r.stdout, r.stderr) == (0, "", ""), r
    assert (scratch / "ok.log").read_text(encoding="utf-8") == "src/app.py"
