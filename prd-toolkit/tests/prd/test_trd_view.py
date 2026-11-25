"""FR-265: print the technical view (test-cases/trd.yaml, T-265.1 to T-265.5)."""
from __future__ import annotations

import datetime

from trd_support import (  # noqa: F401
    gen_line, given_steps, pack_part_lines, pack_part_titles, run, stdout_first_line, trd_repo,
)

VIEW = "python TRD docs/prd/orders"


@given_steps("V0")
def test_trd_header_and_sections(trd_repo):
    """@prd T-265.1"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    assert r.stderr == b""
    out = r.out
    assert stdout_first_line(out) == "# Technical view: orders 1.0.0"
    assert pack_part_titles(out) == [
        "## Stack",
        "## Architecture",
        "## Components",
        "## Requirements to code",
        "## Standards",
        "## Skills",
        "## Contracts",
        "## Uncovered code",
    ]
    lines = out.splitlines()
    # relation: stdout's second line is empty and its third line is GEN
    assert len(lines) >= 3, out
    assert lines[1] == ""
    assert lines[2] == gen_line(tmp)
    # relation: every `## ` line is directly preceded and followed by an empty line, and the line after that
    # empty line starts with `From: `
    for i, line in enumerate(lines):
        if line.startswith("## "):
            assert i >= 1 and lines[i - 1] == "", f"line {i + 1} {line!r} is not preceded by an empty line"
            assert i + 2 < len(lines), f"line {i + 1} {line!r} has no From: line after it"
            assert lines[i + 1] == "", f"line {i + 1} {line!r} is not followed by an empty line"
            assert lines[i + 2].startswith("From: "), f"line {i + 3} {lines[i + 2]!r} does not start with From: "
    # relation: stdout ends with a newline, and its last line is not empty
    assert r.stdout.endswith(b"\n")
    assert lines[-1] != ""


@given_steps("V0")
def test_trd_stack_architecture_standards_skills(trd_repo):
    """@prd T-265.2"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    out = r.out
    assert pack_part_lines(out, "Stack") == [
        "## Stack",
        "",
        "From: prd.md section 1.",
        "",
        "- Language: Python 3.12",
        "- Not applicable: `contracts/openapi.yaml` — no HTTP API",
        "- Not applicable: `contracts/schema.sql` — no database",
        "- Not applicable: `contracts/events.md` — no events or jobs",
        "- Not applicable: `contracts/permissions.yaml` — no roles",
        "- Not applicable: `contracts/config.yaml` — no settings",
        "- Not applicable: `contracts/data-classification.yaml` — no stored personal data",
        "- Not applicable: `contracts/dependencies/` — no third-party service",
        "- Not applicable: `contracts/fixtures/` — no fixture data",
        "",
    ]
    assert pack_part_lines(out, "Architecture") == [
        "## Architecture",
        "",
        "From: prd.md section 4.",
        "",
        "The importer stores orders; the report command reads them.",
        "",
    ]
    assert pack_part_lines(out, "Standards") == [
        "## Standards",
        "",
        "From: prd.md section 5.",
        "",
        "Not applicable: the fixture runs no linter.",
        "",
    ]
    assert pack_part_lines(out, "Skills") == [
        "## Skills",
        "",
        "From: prd.md section 6.",
        "",
        "Not applicable: the fixture requires no skill.",
        "",
    ]


@given_steps("V0")
def test_trd_contracts(trd_repo):
    """@prd T-265.3"""
    tmp = trd_repo
    r = run(tmp, VIEW)
    assert r.exit == 0, r.err
    assert pack_part_lines(r.out, "Contracts") == [
        "## Contracts",
        "",
        "From: prd.md section 7.",
        "",
        "These stay in the PRD: the black-box tester writes its tests from them.",
        "",
        "| Type | Files (glob) |",
        "|---|---|",
        "| errors | `contracts/errors.yaml` |",
        "",
    ]


@given_steps("V0", "VA", "VS")
def test_trd_same_bytes_and_no_date(trd_repo):
    """@prd T-265.4"""
    tmp = trd_repo
    results, dates = [], []
    for _ in range(2):
        before = datetime.date.today().isoformat()
        r = run(tmp, VIEW)
        after = datetime.date.today().isoformat()
        results.append(r)
        dates.append((before, after))
    for n, r in enumerate(results, 1):
        assert r.exit == 0, f"run_{n}: {r.err}"
    # relation: run_2's stdout is byte for byte run_1's stdout
    assert results[1].stdout == results[0].stdout
    # relation: neither run's stdout holds the date taken just before that run nor the one just after it
    for n, (r, (before, after)) in enumerate(zip(results, dates), 1):
        assert before.encode("utf-8") not in r.stdout, f"run_{n}'s stdout holds {before}"
        assert after.encode("utf-8") not in r.stdout, f"run_{n}'s stdout holds {after}"


@given_steps("V0", "VO")
def test_trd_out_writes_the_view(trd_repo):
    """@prd T-265.5"""
    tmp = trd_repo
    r1 = run(tmp, VIEW)
    r2 = run(tmp, VIEW + " --out view.md")
    assert r1.exit == 0, f"run_1: {r1.err}"
    assert r2.exit == 0, f"run_2: {r2.err}"
    assert r2.stdout == "wrote view.md\n".encode("utf-8")
    assert r2.stderr == b""
    # relation: after run_2, the bytes of <tmp>/view.md are run_1's stdout, and the line `old text` is gone
    written = (tmp / "view.md").read_bytes()
    assert written == r1.stdout
    assert "old text" not in written.decode("utf-8").splitlines()
