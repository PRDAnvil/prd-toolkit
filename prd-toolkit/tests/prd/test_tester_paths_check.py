"""tester-paths: which changed files the build check calls a tester's test (test-cases/tester-paths.yaml).

Each case builds the scratch repository with its setup steps (testing.md, Setup steps: tester-paths) and runs
`python CHECK docs/prd/orders --diff base..HEAD` with <tmp> as the working directory.
"""
from __future__ import annotations

from collections import Counter

from tester_paths_support import PRD_DIR, given_steps, run_check

RUN = (PRD_DIR, "--diff", "base..HEAD")

ORDERS_LINE = ("tests/test_orders.py cites T-001.1, T-002.1, T-003.1, T-004.1, T-005.1, T-005.2, T-006.1, "
               "T-007.1, a tester's test: the builder may not edit it")


@given_steps("TP0", "TP1")
def test_changes_under_no_test_root_get_no_line(scratch):
    """@prd T-074.1"""
    r = run_check(scratch, *RUN)
    assert r.exit == 0, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout == ""
    assert r.stderr == ""


@given_steps("TP0", "TP1", "TP2")
def test_change_under_the_test_root_is_a_testers_test(scratch):
    """@prd T-074.2"""
    r = run_check(scratch, *RUN)
    assert r.exit == 1, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout.splitlines() == [ORDERS_LINE]
    assert r.stderr == ""


@given_steps("TP0", "TP3")
def test_moves_reported_by_the_path_under_the_root(scratch):
    """@prd T-074.3"""
    r = run_check(scratch, *RUN)
    assert r.exit == 1, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert Counter(r.stdout.splitlines()) == Counter([
        ORDERS_LINE,
        "tests/test_old.py cites T-003.1, a tester's test: the builder may not edit it",
    ])
    assert r.stderr == ""


@given_steps("TP0", "TP4", "TP1", "TP2")
def test_the_test_roots_of_testing_md_decide(scratch):
    """@prd T-074.4"""
    r = run_check(scratch, *RUN)
    assert r.exit == 1, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout.splitlines() == ["checks/test_a.py cites T-004.1, a tester's test: the builder may not edit it"]
    assert r.stderr == ""


@given_steps("TP0", "TP5", "TP1", "TP2")
def test_no_test_roots_text_means_tests(scratch):
    """@prd T-074.5"""
    r = run_check(scratch, *RUN)
    assert r.exit == 1, f"exit {r.exit}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert r.stdout.splitlines() == [ORDERS_LINE]
    assert r.stderr == ""
