"""inbox-cards FR-254: an error-class gate answered with a question (test-cases/inbox-cards.yaml)."""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
import time

import pytest

from inbox_cards_support import (
    GATES,
    assert_nothing_written,
    before,
    build,
    groups,
    log_last,
    log_lines,
    make_inbox,
    orders,
    resolved,
    run_gates,
    subprocess_env,
)

ERROR_CLASS = "error-class:E-001"
REPLY = "What does row 1000 mean?"
WAIT_SECONDS = 30  # testing.md, Harness, Waits


def _answer_args() -> list[str]:
    return ["answer", "docs/prd/orders", ERROR_CLASS, "--choice", "question", "--reply", REPLY]


def _card(listing: dict, gate: str) -> dict:
    found = [c for c in listing["worktrees"][0]["gates"] if c["id"] == gate]
    assert len(found) == 1, f"the first group holds {len(found)} cards {gate}: {listing['worktrees'][0]}"
    return found[0]


def test_answer_a_question_from_the_cli(tmp_path, monkeypatch):
    """@prd T-254.3"""
    build(tmp_path, monkeypatch, "IC0")
    was = before(tmp_path)
    r = run_gates(tmp_path / "main", *_answer_args())
    assert r.exit == 0, r
    assert r.stdout == f"recorded a question for {ERROR_CLASS}\n", r
    assert r.stderr == "", r
    assert_nothing_written(tmp_path, was)
    assert len(log_lines(tmp_path)) == was.log_count + 1, "LOG does not hold one line more than before"
    last = log_last(tmp_path)
    assert (last.get("gate"), last.get("choice"), last.get("reply"), last.get("by")) == (
        ERROR_CLASS, "question", REPLY, "cli"), last


def test_answer_a_question_from_the_inbox(tmp_path, monkeypatch):
    """@prd T-254.4"""
    build(tmp_path, monkeypatch, "IC0")
    was = before(tmp_path)
    monkeypatch.chdir(tmp_path / "main")
    server = make_inbox(orders(tmp_path / "main"))[0]
    try:
        l1 = server.state.listing()
        card = _card(l1, ERROR_CLASS)
        status, result = server.state.answer({
            "worktree": resolved(tmp_path / "main"), "gate": ERROR_CLASS, "question": card["question"],
            "choice": "question", "words": "  What does row 1000 mean?  ",
        })
        l2 = server.state.listing()
    finally:
        server.server_close()

    got = json.loads(json.dumps({"status": status, "result": result, "after": groups(l2)}, default=str))
    assert got == {
        "status": 200,
        "result": {"gate": ERROR_CLASS, "result": {"stdout": [f"recorded a question for {ERROR_CLASS}"], "exit": 0}},
        "after": [
            {"path": resolved(tmp_path / "main"), "branch": "main", "ids": [ERROR_CLASS]},
            {"path": resolved(tmp_path / "wt"), "branch": "other", "ids": []},
        ],
    }
    assert_nothing_written(tmp_path, was)
    assert len(log_lines(tmp_path)) == was.log_count + 1, "LOG does not hold one line more than before"
    last = log_last(tmp_path)
    assert (last.get("gate"), last.get("choice"), last.get("reply"), last.get("by")) == (
        ERROR_CLASS, "question", f"Ask a question: {REPLY} (form)", "form"), last


def test_a_question_leaves_the_gate_listed(tmp_path, monkeypatch):
    """@prd T-254.5"""
    build(tmp_path, monkeypatch, "IC0")
    before(tmp_path)
    r1 = run_gates(tmp_path / "main", *_answer_args())
    assert (r1.exit, r1.stdout, r1.stderr) == (0, f"recorded a question for {ERROR_CLASS}\n", ""), r1
    r2 = run_gates(tmp_path / "main", "list", "docs/prd/orders")
    assert (r2.exit, r2.stdout, r2.stderr) == (0, "error-class:E-001 The importer stops at row 1000\n", ""), r2


def test_wait_sees_a_question(tmp_path, monkeypatch):
    """@prd T-254.6"""
    build(tmp_path, monkeypatch, "IC0")
    before(tmp_path)
    main = tmp_path / "main"
    marker_dir = main / ".git" / "prd-gates-waiting"
    waiter = subprocess.Popen(
        [sys.executable, str(GATES), "wait", "docs/prd/orders", ERROR_CLASS],
        cwd=main, env=subprocess_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + WAIT_SECONDS
        while not (marker_dir.is_dir() and any(marker_dir.iterdir())):
            if waiter.poll() is not None or time.monotonic() > deadline:
                if waiter.poll() is None:
                    waiter.kill()
                out, err = waiter.communicate()
                pytest.fail(f"no waiting marker in {marker_dir} within {WAIT_SECONDS}s; wait exit "
                            f"{waiter.returncode}, stdout {out!r}, stderr {err!r}")
            time.sleep(0.1)

        r2 = run_gates(main, *_answer_args())
        try:
            out, err = waiter.communicate(timeout=WAIT_SECONDS)
        except subprocess.TimeoutExpired:
            pytest.fail(f"wait did not end within {WAIT_SECONDS}s of the answer")
    finally:
        if waiter.poll() is None:
            waiter.kill()
            waiter.communicate()

    stdout, stderr = out.decode("utf-8"), err.decode("utf-8")
    assert waiter.returncode == 0, (waiter.returncode, stdout, stderr)
    assert stdout.endswith("\n") and len(stdout.splitlines()) == 1, f"run_1's stdout is not one line: {stdout!r}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), stdout
    for key, value in {"kind": "gates.outcome", "gate": ERROR_CLASS, "choice": "question",
                       "reply": REPLY, "by": "cli"}.items():
        assert doc.get(key) == value, f"{key}: {doc.get(key)!r}, expected {value!r}; {stdout}"
    assert stderr == "", stderr
    assert (r2.exit, r2.stdout, r2.stderr) == (0, f"recorded a question for {ERROR_CLASS}\n", ""), r2


def test_inbox_refuses_a_question_without_words(tmp_path, monkeypatch):
    """@prd T-254.7"""
    build(tmp_path, monkeypatch, "IC0")
    was = before(tmp_path)
    monkeypatch.chdir(tmp_path / "main")
    formserver = importlib.import_module("prdlint.formserver")
    server = make_inbox(orders(tmp_path / "main"))[0]
    try:
        l1 = server.state.listing()
        card = _card(l1, ERROR_CLASS)
        with pytest.raises(formserver.Bad) as raised:
            server.state.answer({
                "worktree": resolved(tmp_path / "main"), "gate": ERROR_CLASS, "question": card["question"],
                "choice": "question", "words": "   ",
            })
    finally:
        server.server_close()

    got = {"status": raised.value.status, "why": raised.value.why}
    assert got == {"status": 400, "why": "refused: Ask a question needs your words"}
    assert_nothing_written(tmp_path, was)
    assert len(log_lines(tmp_path)) == was.log_count, "LOG does not hold as many lines as before"
