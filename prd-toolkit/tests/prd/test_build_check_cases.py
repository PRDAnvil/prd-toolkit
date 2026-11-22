"""Characterization tests of the build-check area (docs/prd/prd-toolkit/test-cases/build-check.yaml).

Every input and expected value comes from that file and from testing.md; see build_check_support.py.
"""
from __future__ import annotations

import os

import pytest

from build_check_support import (  # noqa: F401  (scratch is a fixture)
    KnownFailure, R, SLOW_RUN_TIMEOUT, assert_first_line_starts, assert_last_line, assert_single_line_starts,
    given_steps, h_of, head12, porcelain, run, scratch, write_files,
)

USAGE_LAST = ("prd_build_check: give exactly one of --diff, --results (with --tids) or --stale (with --tids); "
              "--sources goes with --diff")
PRD_FOLDER_LINE = "docs/prd/orders/notes.txt: the builder may not edit the PRD folder"
VENDORED_EXTRA = ".prd-toolkit/extra.txt: the builder may not edit the vendored .prd-toolkit/ copy"


def _each(results, exit_code, stdout=None, stderr=None):
    for i, r in enumerate(results, 1):
        assert r.exit == exit_code, f"run {i}: exit {r.exit}, expected {exit_code}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        if stdout is not None:
            assert r.stdout == stdout, f"run {i}: stdout {r.stdout!r}, expected {stdout!r}"
        if stderr is not None:
            assert r.stderr == stderr, f"run {i}: stderr {r.stderr!r}, expected {stderr!r}"


# -- FR-186 --

@given_steps("N0")
def test_usage_refusals(scratch):
    """@prd T-186.1"""
    runs = [
        "python CHECK",
        "python CHECK docs/prd/orders",
        "python CHECK docs/prd/orders --diff base..HEAD --stale --tids T-001.1",
        "python CHECK docs/prd/orders --results report.md",
        'python CHECK docs/prd/orders --stale --tids ""',
        "python CHECK docs/prd/orders --results report.md --tids T-001.1 --sources s.txt",
        "python CHECK --diff base..HEAD",
    ]
    results = [run(scratch, c) for c in runs]
    _each(results, 2, stdout="")
    for i, r in enumerate(results, 1):
        assert_first_line_starts(r.stderr, "usage: prd_build_check.py", f"run {i}: stderr")
        assert_last_line(r.stderr, USAGE_LAST, f"run {i}: stderr")


@given_steps("N0")
def test_parser_errors(scratch):
    """@prd T-186.2"""
    r1 = run(scratch, "python CHECK docs/prd/orders --bogus")
    r2 = run(scratch, "python CHECK docs/prd/orders --diff")
    _each([r1, r2], 2, stdout="")
    assert "prd_build_check.py: error: unrecognized arguments: --bogus" in r1.stderr, r1.stderr
    assert "prd_build_check.py: error: argument --diff: expected one argument" in r2.stderr, r2.stderr


@given_steps()
def test_help(scratch):
    """@prd T-186.3"""
    results = [run(scratch, "python CHECK --help"), run(scratch, "python CHECK -h")]
    _each(results, 0, stderr="")
    for i, r in enumerate(results, 1):
        assert_first_line_starts(r.stdout, "usage: prd_build_check.py", f"run {i}: stdout")
        for text in ["Mechanical checks for a build round.", "--diff BASE..HEAD", "--sources FILE",
                     "--results REPORT", "--stale", "--tids TIDS"]:
            assert text in r.stdout, f"run {i}: stdout lacks {text!r}:\n{r.stdout}"


# -- FR-187 --

@given_steps("VENV")
def test_missing_package(scratch):
    """@prd T-187.1"""
    env = {"LC_ALL": "C.UTF-8"}
    results = [
        run(scratch, "<tmp>/venv/bin/python CHECK --help", env=env),
        run(scratch, "<tmp>/venv/bin/python CHECK docs/prd/orders --results report.md --tids T-001.1", env=env),
    ]
    _each(results, 2, stdout="", stderr=(
        "prd_build_check: missing Python package 'pyyaml'. Run with: uv run --script prd_build_check.py …, "
        "or: pip install pyyaml sqlglot openapi-spec-validator\n"))


# -- FR-188 --

@given_steps("EMPTY")
def test_no_prd_md(scratch):
    """@prd T-188.1"""
    r = run(scratch, "python CHECK empty --results report.md --tids T-001.1")
    _each([r], 2, stdout="")
    e = os.path.realpath(scratch / "empty").replace(os.sep, "/")
    assert r.stderr.splitlines() == [f"prd_build_check: {e}: no prd.md"], r.stderr


@given_steps("N0", "BM1")
def test_unmigrated_adoption_map(scratch):
    """@prd T-188.2"""
    results = [
        run(scratch, "python CHECK docs/prd/orders --results missing.md --tids T-001.1"),
        run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1"),
    ]
    _each(results, 2, stdout="")
    line = (f"prd_build_check: {R(scratch)}/prd.md: section 8: the adoption map moved to adoption.md in "
            'prd-toolkit 0.3; move the table there and leave "See adoption.md."')
    for i, r in enumerate(results, 1):
        assert r.stderr.splitlines() == [line], f"run {i}: {r.stderr}"


# -- FR-189 --

@given_steps("TP0")
def test_bad_range_shape(scratch):
    """@prd T-189.1"""
    cases = [
        ("python CHECK docs/prd/orders --diff base", "prd_build_check: bad range base: expected <base>..<head>"),
        ("python CHECK docs/prd/orders --diff base...HEAD",
         "prd_build_check: bad range base...HEAD: expected <base>..<head>"),
        ("python CHECK docs/prd/orders --diff ..HEAD", "prd_build_check: bad range ..HEAD: expected <base>..<head>"),
        ("python CHECK docs/prd/orders --diff base...HEAD --sources s.txt",
         "prd_build_check: bad range base...HEAD: expected <base>..<head>"),
    ]
    results = [run(scratch, c) for c, _ in cases]
    _each(results, 2, stdout="")
    for i, (r, (_, line)) in enumerate(zip(results, cases), 1):
        assert r.stderr.splitlines() == [line], f"run {i}: {r.stderr}"


@given_steps("TP0")
def test_range_end_not_a_commit(scratch):
    """@prd T-189.2"""
    cases = [
        ("python CHECK docs/prd/orders --diff base..nope", "prd_build_check: bad range base..nope: nope is not a commit"),
        ("python CHECK docs/prd/orders --diff nope..HEAD", "prd_build_check: bad range nope..HEAD: nope is not a commit"),
        ("python CHECK docs/prd/orders --diff nope..never",
         "prd_build_check: bad range nope..never: nope is not a commit"),
    ]
    results = [run(scratch, c) for c, _ in cases]
    _each(results, 2, stdout="")
    for i, (r, (_, line)) in enumerate(zip(results, cases), 1):
        assert r.stderr.splitlines() == [line], f"run {i}: {r.stderr}"


# -- FR-190 --

@given_steps("TP0", "BD1")
def test_prd_folder_edit(scratch):
    """@prd T-190.1"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [PRD_FOLDER_LINE], r.stdout


@given_steps("TP0", "BD3")
def test_prd_folder_move_out(scratch):
    """@prd T-190.2"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [PRD_FOLDER_LINE], r.stdout


@given_steps("TP0", "BD2")
def test_clean_range(scratch):
    """@prd T-190.3"""
    results = [
        run(scratch, "python CHECK docs/prd/orders --diff base..HEAD"),
        run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --tids T-001.1"),
    ]
    _each(results, 0, stdout="", stderr="")


# -- FR-191 --

@given_steps("TP0", "BV1")
def test_vendored_edit_no_plugin(scratch):
    """@prd T-191.1"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [PRD_FOLDER_LINE, VENDORED_EXTRA], r.stdout


@given_steps("TP0", "BP0", "BP4")
def test_vendored_edit_two_plugins(scratch):
    """@prd T-191.2"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [VENDORED_EXTRA], r.stdout


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-066")
@given_steps("TP0", "BU0", "BU2")
def test_plugin_under_non_ascii_folder(scratch):
    """@prd T-191.3 known-failing E-066"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    # The symptom: the check prints exactly the one line below and exits 1.
    symptom = [".prd-toolkit/prd_lint.py: the builder may not edit the vendored .prd-toolkit/ copy"]
    if r.exit == 1 and r.stdout.splitlines() == symptom:
        raise KnownFailure("E-066: " + symptom[0])
    _each([r], 0, stdout="", stderr="")


# -- FR-192 --

@given_steps("TP0", "BP0", "BP1")
def test_vendored_copy_differs(scratch):
    """@prd T-192.1"""
    before = porcelain(scratch)
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    after = porcelain(scratch)
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        ".prd-toolkit/VERSION: differs from the plugin; refresh it with prd_hooks.py vendor",
        ".prd-toolkit/extra.txt: differs from the plugin; refresh it with prd_hooks.py vendor",
        ".prd-toolkit/prd_lint.py: differs from the plugin; refresh it with prd_hooks.py vendor",
        ".prd-toolkit/requirements.txt: differs from the plugin; refresh it with prd_hooks.py vendor",
    ], r.stdout
    assert before == after, f"git status --porcelain changed:\nbefore:\n{before}\nafter:\n{after}"


@given_steps("TP0", "BP0", "BP3")
def test_vendored_copy_unchanged_path_compared(scratch):
    """@prd T-192.2"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        ".prd-toolkit/extra.txt: differs from the plugin; refresh it with prd_hooks.py vendor",
        ".prd-toolkit/prd_lint.py: differs from the plugin; refresh it with prd_hooks.py vendor",
    ], r.stdout


@given_steps("TP0", "BP0", "BP2")
def test_exact_refresh(scratch):
    """@prd T-192.3"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 0, stdout="", stderr="")


@given_steps("TP0", "BF1")
def test_vendor_run_fails(scratch):
    """@prd T-192.4"""
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD")
    _each([r], 2, stdout="")
    assert r.stderr.splitlines() == [f"prd_build_check: vendor at {head12(scratch)}: vendor broke"], r.stderr


# -- FR-193 --

@given_steps("TP0", "BS1")
def test_sources_lines(scratch):
    """@prd T-193.1"""
    write_files(scratch, {"<tmp>/sources.txt": (
        "FR-001: src/app.py:2\n\n- FR-002: src/app.py:3\nSOURCES: FR-003: src/app.py:1\nFR-004: src/other.py:1\n"
        "FR-005: src/app.py\nFR-006: src/app.py:2 (the importer)\n")})
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources sources.txt")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        "sources: FR-003: src/app.py:1 is outside the round's changes (hunks 2-3)",
        "sources: FR-004: src/other.py is not changed in base..HEAD",
        "sources: line 6 is not '<ID>: <path>:<line>'",
        "sources: line 7 is not '<ID>: <path>:<line>'",
    ], r.stdout


@given_steps("TP0", "BS2")
def test_sources_deleting_hunk(scratch):
    """@prd T-193.2"""
    write_files(scratch, {"<tmp>/sources.txt":
                          "FR-001: src/app.py:2\nFR-002: src/app.py:3\nFR-003: src/app.py:1\nFR-004: src/app.py:4\n"})
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources sources.txt")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        "sources: FR-003: src/app.py:1 is outside the round's changes (hunks 2-3)",
        "sources: FR-004: src/app.py:4 is outside the round's changes (hunks 2-3)",
    ], r.stdout


@given_steps("TP0", "BD1")
def test_sources_after_diff_lines(scratch):
    """@prd T-193.3"""
    write_files(scratch, {
        "<tmp>/sources.txt": "FR-001: src/app.py:2\nFR-002: src/app.py:1\n",
        "<tmp>/good.txt": "FR-001: src/app.py:2\n",
    })
    r1 = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources sources.txt")
    r2 = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources good.txt")
    _each([r1, r2], 1, stderr="")
    assert r1.stdout.splitlines() == [
        PRD_FOLDER_LINE,
        "sources: FR-002: src/app.py:1 is outside the round's changes (hunks 2-2)",
    ], r1.stdout
    assert r2.stdout.splitlines() == [PRD_FOLDER_LINE], r2.stdout


@given_steps("TP0", "BS1")
def test_sources_path_not_changed(scratch):
    """@prd T-193.4"""
    write_files(scratch, {"<tmp>/sources.txt":
                          "FR-001: src/app.py:2\nFR-004: src/other.py:1\nFR-005: docs/prd/orders/prd.md:1\n"})
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources sources.txt")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        "sources: FR-004: src/other.py is not changed in base..HEAD",
        "sources: FR-005: docs/prd/orders/prd.md is not changed in base..HEAD",
    ], r.stdout


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-065")
@given_steps("TP0", "BS3")
def test_sources_path_read_literally(scratch):
    """@prd T-193.5 known-failing E-065"""
    write_files(scratch, {"<tmp>/sources.txt": "FR-001: src/x*.py:3\n"})
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources sources.txt")
    # The symptom: no `sources:` line for `FR-001: src/x*.py:3`, the file's one line, and exit 0.
    if r.exit == 0 and not any(line.startswith("sources:") for line in r.stdout.splitlines()):
        raise KnownFailure("E-065: no sources: line for FR-001: src/x*.py:3, exit 0")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        "sources: FR-001: src/x*.py:3 is outside the round's changes (hunks 1-1)"], r.stdout


# -- FR-194 --

@given_steps("N0")
def test_results_accepted(scratch):
    """@prd T-194.1"""
    write_files(scratch, {
        "<tmp>/r1.md": ("Notes before the block.\n## RESULTS\n\nT-001.1: pass\n- T-002.1: fail: expected 2, got 3\n"
                        "* T-003.1: known-failing E-001\n\nNotes: T-004.1 was not run.\n"),
        "<tmp>/r2.md": "3. RESULTS\nT-001.1: pass\nT-002.1: pass\nT-003.1: pass\n",
        "<tmp>/r3.md": "**RESULTS**\n  T-001.1: pass\n  T-002.1: pass\n  T-003.1: pass\n",
    })
    results = [
        run(scratch, "python CHECK docs/prd/orders --results r1.md --tids T-001.1,T-002.1,T-003.1"),
        run(scratch, 'python CHECK docs/prd/orders --results r2.md --tids "T-001.1, T-002.1, T-003.1"'),
        run(scratch, "python CHECK docs/prd/orders --results r3.md --tids T-001.1,T-002.1,T-003.1,"),
    ]
    _each(results, 0, stdout="", stderr="")


@given_steps("N0")
def test_results_block_bounds(scratch):
    """@prd T-194.2"""
    write_files(scratch, {
        "<tmp>/blank.md": "RESULTS\n\nT-001.1: pass\n- T-002.1: fail: expected 2, got 3\n\nT-003.1: known-failing E-001\n",
        "<tmp>/prose.md": "RESULTS\nAll passed.\nT-001.1: pass\n",
        "<tmp>/none.md": "T-001.1: pass\n",
        "<tmp>/before.md": "T-001.1: pass\nRESULTS\nT-002.1: pass\n",
    })
    cases = [
        ("python CHECK docs/prd/orders --results blank.md --tids T-001.1,T-002.1,T-003.1", ["T-003.1 has no RESULTS line"]),
        ("python CHECK docs/prd/orders --results prose.md --tids T-001.1", ["T-001.1 has no RESULTS line"]),
        ("python CHECK docs/prd/orders --results none.md --tids T-001.1", ["T-001.1 has no RESULTS line"]),
        ("python CHECK docs/prd/orders --results before.md --tids T-001.1,T-002.1", ["T-001.1 has no RESULTS line"]),
    ]
    results = [run(scratch, c) for c, _ in cases]
    _each(results, 1, stderr="")
    for i, (r, (_, lines)) in enumerate(zip(results, cases), 1):
        assert r.stdout.splitlines() == lines, f"run {i}: {r.stdout}"


@given_steps("N0")
def test_results_line_problems(scratch):
    """@prd T-194.3"""
    write_files(scratch, {"<tmp>/report.md": (
        "# Suite report\nRESULTS\n- T-001.1: pass\nT-001.1: pass\nT-002.1: passed\nT-009.1: pass\n"
        "* T-009.1: fail: no such test\n")})
    r = run(scratch, "python CHECK docs/prd/orders --results report.md --tids T-001.1,T-002.1,T-003.1")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        "T-002.1: not one of pass, fail: <reason>, known-failing E-nnn",
        "T-009.1 was not dispatched",
        "T-009.1 was not dispatched",
        "T-001.1: more than one RESULTS line",
        "T-003.1 has no RESULTS line",
    ], r.stdout


@given_steps("N0")
def test_results_repeated_lines(scratch):
    """@prd T-194.4"""
    write_files(scratch, {"<tmp>/report.md":
                          "RESULTS\nT-002.1: pass\nT-001.1: pass\nT-002.1: fail: again\nT-001.1: pass\nT-002.1: pass\n"})
    r = run(scratch, "python CHECK docs/prd/orders --results report.md --tids T-001.1,T-002.1")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        "T-002.1: more than one RESULTS line",
        "T-001.1: more than one RESULTS line",
    ], r.stdout


@given_steps("N0")
def test_results_missing_in_tids_order(scratch):
    """@prd T-194.5"""
    write_files(scratch, {"<tmp>/report.md": "RESULTS\nT-002.1: pass\n"})
    r = run(scratch, "python CHECK docs/prd/orders --results report.md --tids T-003.1,T-002.1,T-001.1")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == ["T-003.1 has no RESULTS line", "T-001.1 has no RESULTS line"], r.stdout


# -- FR-195 --

def _stale(tid: str, path: str, sha: str) -> str:
    return f"stale {tid} {path}: its test case changed after the test (last changed in {sha})"


@given_steps("TP0", "BT9")
def test_stale_working_tree_change(scratch):
    """@prd T-195.1"""
    h = h_of(scratch, "tests/test_orders.py")
    before = porcelain(scratch)
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-003.1,T-001.1,T-002.1")
    after = porcelain(scratch)
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [
        _stale("T-003.1", "tests/test_orders.py", h),
        _stale("T-001.1", "tests/test_orders.py", h),
    ], r.stdout
    assert before == after, f"git status --porcelain changed:\nbefore:\n{before}\nafter:\n{after}"


@given_steps("TP0", "BT2")
def test_stale_committed_change(scratch):
    """@prd T-195.2"""
    h = h_of(scratch, "tests/test_orders.py")
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [_stale("T-001.1", "tests/test_orders.py", h)], r.stdout


@given_steps("TP0", "BT6")
def test_stale_latest_committer_time(scratch):
    """@prd T-195.3"""
    h = h_of(scratch, "tests/test_orders.py")
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [_stale("T-001.1", "tests/test_orders.py", h)], r.stdout


@given_steps("TP0", "BT4")
def test_stale_citing_file_changed(scratch):
    """@prd T-195.4"""
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1")
    _each([r], 0, stdout="", stderr="")


@given_steps("TP0", "BT5")
def test_stale_untracked_citing_file(scratch):
    """@prd T-195.5"""
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1")
    _each([r], 0, stdout="", stderr="")


@given_steps("TP0", "BT3")
def test_stale_none(scratch):
    """@prd T-195.6"""
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1,T-009.1,nonsense")
    _each([r], 0, stdout="", stderr="")


@given_steps("TP0", "BT8")
def test_stale_no_case(scratch):
    """@prd T-195.7"""
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1")
    _each([r], 0, stdout="", stderr="")


@given_steps("TP0", "BT7")
def test_stale_case_absent_at_commit(scratch):
    """@prd T-195.8"""
    h8 = h_of(scratch, "tests/test_extra.py")
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-008.1")
    _each([r], 1, stderr="")
    assert r.stdout.splitlines() == [_stale("T-008.1", "tests/test_extra.py", h8)], r.stdout


# -- FR-196 --

@given_steps("N0X")
def test_stale_outside_git(scratch):
    """@prd T-196.1"""
    r = run(scratch, "python CHECK docs/prd/orders --stale --tids T-001.1")
    _each([r], 2, stdout="")
    assert r.stderr.splitlines() == [f"prd_build_check: {R(scratch)} is not in a git working tree"], r.stderr


# -- FR-197 --

@given_steps("TP0", "BD2", "SLOWGIT")
def test_git_timeout(scratch):
    """@prd T-197.1"""
    env = {"PATH": f"{scratch}/bin:{os.environ.get('PATH', '')}"}
    r = run(scratch, "python CHECK docs/prd/orders --diff base..HEAD", env=env, timeout=SLOW_RUN_TIMEOUT)
    _each([r], 2, stdout="")
    assert r.stderr.splitlines() == ["prd_build_check: git diff timed out after 120 s"], r.stderr


# -- FR-198 --

@given_steps("TP0", "BD1", "BADMD")
def test_unreadable_input(scratch):
    """@prd T-198.1"""
    results = [
        run(scratch, "python CHECK docs/prd/orders --results missing.md --tids T-001.1"),
        run(scratch, "python CHECK docs/prd/orders --results bad.md --tids T-001.1"),
        run(scratch, "python CHECK docs/prd/orders --diff base..HEAD --sources missing.txt"),
    ]
    _each(results, 2, stdout="")
    for i, r in enumerate(results, 1):
        assert_single_line_starts(r.stderr, "prd_build_check: internal error: ", f"run {i}: stderr")
