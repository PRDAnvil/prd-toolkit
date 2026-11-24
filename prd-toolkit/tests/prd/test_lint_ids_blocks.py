"""Black-box tests of lint-ids FR-126 to FR-131 (docs/prd/prd-toolkit/test-cases/lint-ids.yaml).

Every input and expected value comes from that case file, features/lint-ids.md and testing.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from lint_ids_support import (
    KnownFailure,
    S0,
    assert_contains,
    assert_contains_line,
    assert_exit,
    assert_not_contains,
    assert_stderr_empty,
    known_failure_if,
    run_lint,
)

P = "docs/prd/orders/"


def A2(folder) -> None:
    """Step A2 of the case file: write <P>/adoption.md, rows at lines 5 to 8."""
    lines = [
        "# Adoption map",
        "",
        "| Area | State | Boundary |",
        "|---|---|---|",
        "| import | adopted | `features/import.md` |",
        "| ghost | extracted | `src/ghost/**` |",
        "| spare | confirmed | `src/spare/**` |",
        "| later | not started | |",
    ]
    path = Path(folder.root) / "adoption.md"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(line + "\n" for line in lines))


def R3(folder) -> None:
    """Step R3 of the case file: FR-003 removed in the index and in its block."""
    folder.replace("prd.md", 105, "| FR-003 | Delete an order | removed | features/api.md | 1.0.0 |")
    folder.replace("features/api.md", 22, "Status: removed")


def _as_built(folder) -> None:
    """The two replacements of T-126.1."""
    folder.replace("prd.md", 104, "| FR-002 | Get an order | as-built | features/api.md |  |")
    folder.replace("features/api.md", 10, "Status: as-built")


def _has_line_with(r, text: str) -> bool:
    return any(text in line for line in r.stdout.splitlines())


# FR-126


def test_as_built_without_source(tmp_path, monkeypatch):
    """@prd T-126.1"""
    folder = S0(tmp_path, monkeypatch)
    _as_built(folder)
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(
        r,
        P + "features/api.md:9: index-consistent: FR-002 is as-built but has no "
        "'Source: <file>:<line> @<commit>' line",
    )
    assert_stderr_empty(r)


def test_as_built_with_source(tmp_path, monkeypatch):
    """@prd T-126.2"""
    folder = S0(tmp_path, monkeypatch)
    _as_built(folder)
    folder.insert_after("features/api.md", 10, "Source: src/api.py:10 @abc1234")
    r = run_lint(tmp_path)
    assert_not_contains(r, "is as-built but has no")
    assert_stderr_empty(r)


@pytest.mark.xfail(strict=True, raises=KnownFailure)
def test_as_built_malformed_source(tmp_path, monkeypatch):
    """@prd T-126.3 known-failing E-051"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("prd.md", 104, "| FR-002 | Get an order | as-built | features/api.md |  |")
    folder.replace("features/api.md", 10, "Status: as-built")
    folder.insert_after("features/api.md", 10, "Source: somewhere in the code")
    r = run_lint(tmp_path)
    known_failure_if(
        not _has_line_with(r, "index-consistent: FR-002"),
        "E-051",
        "stdout holds no index-consistent line for FR-002",
        r,
    )
    assert_exit(r, 1)
    assert_contains_line(
        r,
        P + "features/api.md:9: index-consistent: FR-002 is as-built but its Source line is not "
        "'<file>:<line> @<commit>'",
    )
    assert_stderr_empty(r)


# FR-127


def test_resolved_entry_unclassified(tmp_path, monkeypatch):
    """@prd T-127.1"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("errors.md", 5, "Classification: unclassified")
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(
        r, P + "errors.md:3: index-consistent: E-001: unclassified is allowed only on an open entry"
    )
    assert_stderr_empty(r)


def test_open_entry_unclassified(tmp_path, monkeypatch):
    """@prd T-127.2"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("errors.md", 5, "Classification: unclassified")
    folder.replace("errors.md", 7, "Resolution: open")
    r = run_lint(tmp_path)
    assert_not_contains(r, "unclassified is allowed only on an open entry")
    assert_stderr_empty(r)


def test_touches_unknown_id(tmp_path, monkeypatch):
    """@prd T-127.3"""
    folder = S0(tmp_path, monkeypatch)
    folder.insert_before("errors.md", 6, "Touches: FR-001, FR-099")
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, P + "errors.md:6: index-consistent: E-001 Touches FR-099, which no block defines")
    assert_not_contains(r, "E-001 Touches FR-001")
    assert_stderr_empty(r)


def test_resolved_entry_without_classification(tmp_path, monkeypatch):
    """@prd T-127.4"""
    folder = S0(tmp_path, monkeypatch)
    folder.delete("errors.md", 5)
    r = run_lint(tmp_path)
    known_failure_if(
        not _has_line_with(r, "index-consistent: E-001"),
        "E-050",
        "stdout holds no index-consistent line for E-001",
        r,
    )
    assert_exit(r, 1)
    assert_contains_line(
        r, P + "errors.md:3: index-consistent: E-001: unclassified is allowed only on an open entry"
    )
    assert_stderr_empty(r)


# FR-128


def test_adoption_area_without_features_file(tmp_path, monkeypatch):
    """@prd T-128.1"""
    folder = S0(tmp_path, monkeypatch)
    A2(folder)
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains(
        r,
        [
            P + "adoption.md:6: index-consistent: adoption area 'ghost' is extracted but "
            "features/ghost.md does not exist",
            P + "adoption.md:7: index-consistent: adoption area 'spare' is confirmed but "
            "features/spare.md does not exist",
        ],
    )
    assert_stderr_empty(r)


def test_adoption_area_not_started_or_present(tmp_path, monkeypatch):
    """@prd T-128.2"""
    folder = S0(tmp_path, monkeypatch)
    A2(folder)
    r = run_lint(tmp_path)
    assert_not_contains(r, ["adoption area 'import'", "adoption area 'later'"])
    assert_stderr_empty(r)


# FR-129


def _delete_lines(folder, rel: str, first: int, last: int) -> None:
    """delete lines first to last of F (as S0 wrote them): the line at `first` is removed each time."""
    for _ in range(first, last + 1):
        folder.delete(rel, first)


def test_fr_without_ac(tmp_path, monkeypatch):
    """@prd T-129.1"""
    folder = S0(tmp_path, monkeypatch)
    _delete_lines(folder, "features/api.md", 25, 29)
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, P + "features/api.md:21: fr-has-ac: FR-003 has no acceptance criteria")
    assert_stderr_empty(r)


def test_nfr_with_only_removed_ac(tmp_path, monkeypatch):
    """@prd T-129.2"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace(
        "nfr.md",
        6,
        "- AC-004.1 (removed in 2.0.0) The API shall answer getOrder within 300 ms at p95 under 50 requests/s.",
    )
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(
        r,
        P + "nfr.md:3: fr-has-ac: NFR-004 has no live acceptance criteria; remove the requirement instead",
    )
    assert_stderr_empty(r)


def test_removed_fr_without_ac(tmp_path, monkeypatch):
    """@prd T-129.3"""
    folder = S0(tmp_path, monkeypatch)
    R3(folder)
    _delete_lines(folder, "features/api.md", 25, 29)
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_not_contains(r, "fr-has-ac: FR-003")
    assert_stderr_empty(r)


def test_uj_without_ac(tmp_path, monkeypatch):
    """@prd T-129.4"""
    S0(tmp_path, monkeypatch)
    r = run_lint(tmp_path)
    assert_exit(r, 0)
    assert_not_contains(r, "fr-has-ac")
    assert_stderr_empty(r)


# FR-130

EN_OPENERS = "must start with When, While, If, Where or 'The <thing> shall'"


def test_ac_no_opener(tmp_path, monkeypatch):
    """@prd T-130.1"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("features/import.md", 8, "- AC-001.1 Rows get inserted.")
    folder.delete("features/import.md", 9)
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, P + "features/import.md:8: ac-ears: AC-001.1 " + EN_OPENERS)
    assert_stderr_empty(r)


def test_ac_lower_case_opener(tmp_path, monkeypatch):
    """@prd T-130.2"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace(
        "features/import.md",
        8,
        "- AC-001.1 when an imported row has a new order_key, the importer shall insert the row",
    )
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, P + "features/import.md:8: ac-ears: AC-001.1 " + EN_OPENERS)
    assert_stderr_empty(r)


def test_ac_without_shall(tmp_path, monkeypatch):
    """@prd T-130.3"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace(
        "features/import.md",
        8,
        "- AC-001.1 When an imported row has a new order_key, the importer inserts the row",
    )
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, P + "features/import.md:8: ac-ears: AC-001.1 must contain 'shall'")
    assert_stderr_empty(r)


def test_fixture_acs_are_ears(tmp_path, monkeypatch):
    """@prd T-130.4"""
    S0(tmp_path, monkeypatch)
    r = run_lint(tmp_path)
    assert_exit(r, 0)
    assert_not_contains(r, "ac-ears")
    assert_stderr_empty(r)


def test_removed_ac_not_checked(tmp_path, monkeypatch):
    """@prd T-130.5"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("features/import.md", 8, "- AC-001.1 (removed in 2.0.0) Rows get inserted.")
    folder.delete("features/import.md", 9)
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_not_contains(r, "ac-ears: AC-001.1")
    assert_stderr_empty(r)


def test_es_table_openers(tmp_path, monkeypatch):
    """@prd T-130.6"""
    folder = S0(tmp_path, monkeypatch)
    folder.insert_before("prd.md", 8, "language: es")
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(
        r,
        P + "features/import.md:8: ac-ears: AC-001.1 must start with Cuando, Mientras, Si, Donde or "
        "'El/La/Los/Las <cosa> deberá'",
    )
    assert_stderr_empty(r)


def test_es_ac_passes(tmp_path, monkeypatch):
    """@prd T-130.7"""
    folder = S0(tmp_path, monkeypatch)
    folder.insert_before("prd.md", 8, "language: es")
    folder.replace(
        "features/import.md",
        8,
        "- AC-001.1 Cuando una fila importada trae un order_key nuevo, el importador deberá insertarla",
    )
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_not_contains(r, "ac-ears: AC-001.1 ")
    assert_stderr_empty(r)


def test_es_ac_without_modal(tmp_path, monkeypatch):
    """@prd T-130.8"""
    folder = S0(tmp_path, monkeypatch)
    folder.insert_before("prd.md", 8, "language: es")
    folder.replace(
        "features/import.md",
        8,
        "- AC-001.1 Cuando una fila importada trae un order_key nuevo, el importador la inserta",
    )
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, P + "features/import.md:8: ac-ears: AC-001.1 must contain 'deberá'")
    assert_stderr_empty(r)


# FR-131

NFR_BOUND = (
    P + "nfr.md:3: nfr-bound: NFR-004 states no measurable bound (a number with a unit such as ms, %, requests/s)"
)


def test_nfr_without_bound(tmp_path, monkeypatch):
    """@prd T-131.1"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("nfr.md", 6, "- AC-004.1 The API shall answer getOrder quickly.")
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, NFR_BOUND)
    assert_stderr_empty(r)


def test_nfr_number_inside_id(tmp_path, monkeypatch):
    """@prd T-131.2"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("nfr.md", 6, "- AC-004.1 The API shall answer getOrder within the bound NFR-300 ms names.")
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_contains_line(r, NFR_BOUND)
    assert_stderr_empty(r)


def test_nfr_percent_bound(tmp_path, monkeypatch):
    """@prd T-131.3"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("nfr.md", 6, "- AC-004.1 The API shall reach 99.9% availability.")
    r = run_lint(tmp_path)
    assert_not_contains(r, "nfr-bound")
    assert_stderr_empty(r)


def test_nfr_req_per_min_bound(tmp_path, monkeypatch):
    """@prd T-131.4"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("nfr.md", 6, "- AC-004.1 The API shall sustain 600 req/min.")
    r = run_lint(tmp_path)
    assert_not_contains(r, "nfr-bound")
    assert_stderr_empty(r)


def test_nfr_bound_on_another_line(tmp_path, monkeypatch):
    """@prd T-131.5"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("nfr.md", 6, "- AC-004.1 The API shall answer getOrder within its budget.")
    folder.insert_before("nfr.md", 7, "Edge cases: the budget is 300 ms at p95")
    r = run_lint(tmp_path)
    assert_not_contains(r, "nfr-bound")
    assert_stderr_empty(r)


def test_removed_nfr_not_checked(tmp_path, monkeypatch):
    """@prd T-131.6"""
    folder = S0(tmp_path, monkeypatch)
    folder.replace("prd.md", 106, "| NFR-004 | Order lookup latency | removed | nfr.md | 1.0.0 |")
    folder.replace("nfr.md", 4, "Status: removed")
    folder.replace("nfr.md", 6, "- AC-004.1 The API shall answer getOrder quickly.")
    r = run_lint(tmp_path)
    assert_exit(r, 1)
    assert_not_contains(r, "nfr-bound")
    assert_stderr_empty(r)
