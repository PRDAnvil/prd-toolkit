"""Black-box tests of the lint-ids area (docs/prd/prd-toolkit/features/lint-ids.md, test-cases/lint-ids.yaml).

Each case's setup runs in the `built` fixture, so a step that does not find its file or line ends the test as
an error, not a failure (the case file's conventions).
"""
from __future__ import annotations

import pytest

from lint_ids_support import (
    KnownFailure,
    S0,
    assert_contains,
    assert_contains_line,
    assert_count_of_line,
    assert_exit,
    assert_not_contains,
    assert_stderr_empty,
    known_failure_if,
    load_texts,
    run_lint,
)

T = load_texts()

REMOVED_FR003_ROW = "| FR-003 | Delete an order | removed | features/api.md | 1.0.0 |"
AC_001_3_REMOVED = (
    "- AC-001.3 (removed in 2.0.0) If the import file is empty, the importer shall finish with status `empty`,"
)


def R3(f):
    """R3: FR-003 removed in both places."""
    f.replace("prd.md", 105, REMOVED_FR003_ROW)
    f.replace("features/api.md", 22, "Status: removed")


@pytest.fixture
def built(request, tmp_path, monkeypatch):
    f = S0(tmp_path, monkeypatch)
    for step in request.param:
        step(f)
    return tmp_path


def setup(*steps):
    return pytest.mark.parametrize("built", [pytest.param(steps, id="setup")], indirect=True)


# FR-121 id-format


@setup(lambda f: f.replace("features/api.md", 19, T["traces_line"]))
def test_traces_line_malformed_fr(built):
    """@prd T-121.1"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, T["traces_expect"])
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 34, T["kinds_line"]))
def test_every_kind_malformed(built):
    """@prd T-121.2"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(r, T["kinds_expect"])
    assert_not_contains(r, "id-format: 'FR-001'")
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 34, T["span_line"]))
def test_code_span_not_checked(built):
    """@prd T-121.3"""
    r = run_lint(built)
    assert_not_contains(r, T["span_absent"])
    assert_stderr_empty(r)


@setup(lambda f: f.replace("contracts/openapi.yaml", 43, T["openapi_line"]))
def test_contract_list_item_at_key_line(built):
    """@prd T-121.4"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, T["openapi_expect"])
    assert_stderr_empty(r)


@setup(lambda f: f.replace("test-cases/import.yaml", 37, T["case_ac_line"]))
def test_test_case_body_value(built):
    """@prd T-121.5"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, T["case_ac_expect"])
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 34, T["dot_line"]))
def test_trailing_dot_not_part_of_token(built):
    """@prd T-121.6"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, T["dot_expect"])
    assert_not_contains(r, ["id-format: 'FR-001.'", "id-format: 'FR-001' "])
    assert_stderr_empty(r)


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-047")
@setup(lambda f: f.replace("test-cases/import.yaml", 36, T["key_line"]))
def test_malformed_test_case_key_at_its_line(built):
    """@prd T-121.7 known-failing E-047"""
    r = run_lint(built)
    at_line_1 = T["key_expect"].replace("test-cases/import.yaml:36:", "test-cases/import.yaml:1:", 1)
    out = r.stdout.splitlines()
    known_failure_if(
        at_line_1 in out and T["key_expect"] not in out,
        "E-047",
        "the expected finding is at test-cases/import.yaml:1, not at line 36",
        r,
    )
    assert_exit(r, 1)
    assert_contains_line(r, T["key_expect"])
    assert_stderr_empty(r)


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-048")
@setup(
    lambda f: f.write(".notes.md", T["hidden_md"]),
    lambda f: f.write("contracts/.draft.yaml", T["hidden_yaml"]),
)
def test_hidden_files_not_read(built):
    """@prd T-121.8 known-failing E-048"""
    r = run_lint(built)
    prefixes = ("docs/prd/orders/.notes.md:", "docs/prd/orders/contracts/.draft.yaml:")
    known_failure_if(
        any(line.startswith(prefixes) and T["span_absent"] in line for line in r.stdout.splitlines()),
        "E-048",
        "a hidden file's token is reported",
        r,
    )
    assert_not_contains(r, T["span_absent"])
    assert_stderr_empty(r)


# FR-122 id-unique


@setup(lambda f: f.insert_before("features/import.md", 12, "- AC-001.2 When a row repeats, the importer shall skip it."))
def test_repeated_ac(built):
    """@prd T-122.1"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/features/import.md:12: id-unique: AC-001.2 is already defined at features/import.md:10"
    )
    assert_stderr_empty(r)


@setup(
    lambda f: f.append(
        "features/import.md",
        ["", "### FR-002 Get an order", "Status: live (since 1.0.0)", "Acceptance (EARS):",
         "- AC-002.9 When asked, the API shall answer."],
    )
)
def test_repeated_block_heading(built):
    """@prd T-122.2"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/features/import.md:19: id-unique: FR-002 is already defined at features/api.md:9"
    )
    assert_stderr_empty(r)


@setup(lambda f: f.append("test-cases/import.yaml", ["", "T-002.1:", "  ac: AC-002.1"]))
def test_repeated_test_case_key_across_files(built):
    """@prd T-122.3"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(r, "id-unique: T-002.1 is already defined at test-cases/api.yaml:1")
    assert_stderr_empty(r)


@setup(lambda f: f.append("errors.md", ["### E-001 Again", "Recurrence of: -"]))
def test_repeated_error_heading(built):
    """@prd T-122.4"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, "docs/prd/orders/errors.md:9: id-unique: E-001 is already defined at errors.md:3")
    assert_stderr_empty(r)


@setup(
    lambda f: f.insert_after("prd.md", 112, "| A-01 | Another | open |"),
    lambda f: f.insert_after("prd.md", 113, "| A-01 | A third | open |"),
)
def test_third_definition_against_first(built):
    """@prd T-122.5"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(
        r,
        [
            "docs/prd/orders/prd.md:113: id-unique: A-01 is already defined at prd.md:112",
            "docs/prd/orders/prd.md:114: id-unique: A-01 is already defined at prd.md:112",
        ],
    )
    assert_stderr_empty(r)


@setup(
    lambda f: f.append(
        "features/api.md",
        ["", "### FR-004 Extra", "Status: approved", "Acceptance (EARS):", "- AC-004.7 When asked, the API shall answer."],
    )
)
def test_fr_and_nfr_share_a_number(built):
    """@prd T-122.6"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_count_of_line(
        r,
        "docs/prd/orders/nfr.md:3: id-unique: FR-004 and NFR-004 share a number; FR and NFR use one sequence",
        1,
    )
    assert_stderr_empty(r)


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-046")
@setup(lambda f: f.append("errors.md", T["fence_lines"]))
def test_fenced_error_heading_is_no_definition(built):
    """@prd T-122.7 known-failing E-046"""
    r = run_lint(built)
    known_failure_if(
        any(line.endswith("id-unique: E-001 is already defined at errors.md:3") for line in r.stdout.splitlines()),
        "E-046",
        "a fenced ### E-001 heading is counted as a definition",
        r,
    )
    assert_not_contains(r, "id-unique: E-001")
    assert_stderr_empty(r)


# FR-123 removal in both the index and the block


@setup(lambda f: f.replace("prd.md", 105, REMOVED_FR003_ROW))
def test_removed_in_index_only(built):
    """@prd T-123.1"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r,
        "docs/prd/orders/prd.md:105: id-removed-reused: FR-003 is 'removed' in the index but 'live' in "
        "features/api.md:21; both must say removed or neither",
    )
    assert_stderr_empty(r)


@setup(lambda f: f.replace("features/api.md", 22, "Status: removed"))
def test_removed_in_block_only(built):
    """@prd T-123.2"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r,
        "docs/prd/orders/prd.md:105: id-removed-reused: FR-003 is 'live' in the index but 'removed' in "
        "features/api.md:21; both must say removed or neither",
    )
    assert_not_contains(r, "index-consistent: FR-003: index status")
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 105, REMOVED_FR003_ROW))
def test_removal_mismatch_not_index_consistent(built):
    """@prd T-123.3"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_not_contains(r, "index-consistent: FR-003: index status")
    assert_stderr_empty(r)


# FR-124 never cite a removed requirement or AC


@setup(R3)
def test_test_case_cites_ac_of_removed_fr(built):
    """@prd T-124.1"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(
        r,
        [
            "docs/prd/orders/test-cases/api.yaml:36: id-removed-reused: test case T-003.1 cites AC-003.1 of removed FR-003",
            "docs/prd/orders/test-cases/api.yaml:52: id-removed-reused: test case T-003.2 cites AC-003.2 of removed FR-003",
        ],
    )
    assert_not_contains(r, "both must say removed or neither")
    assert_stderr_empty(r)


@setup(R3)
def test_x_prd_ids_cite_removed(built):
    """@prd T-124.2"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(
        r,
        [
            "docs/prd/orders/contracts/openapi.yaml:43: id-removed-reused: x-prd-ids cites removed FR-003",
            "docs/prd/orders/contracts/openapi.yaml:43: id-removed-reused: x-prd-ids cites AC-003.1 of removed FR-003",
            "docs/prd/orders/contracts/openapi.yaml:43: id-removed-reused: x-prd-ids cites AC-003.2 of removed FR-003",
        ],
    )
    assert_stderr_empty(r)


@setup(R3, lambda f: f.insert_after("features/api.md", 19, "  FR-003"))
def test_traces_and_continuation_cite_removed(built):
    """@prd T-124.3"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(
        r,
        [
            "docs/prd/orders/features/api.md:7: id-removed-reused: UJ-01 Traces cites removed FR-003",
            "docs/prd/orders/features/api.md:20: id-removed-reused: FR-002 Traces cites removed FR-003",
        ],
    )
    assert_stderr_empty(r)


@setup(lambda f: f.replace("features/import.md", 12, AC_001_3_REMOVED))
def test_test_case_cites_removed_ac(built):
    """@prd T-124.4"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/test-cases/import.yaml:37: id-removed-reused: test case T-001.3 cites removed AC-001.3"
    )
    assert_stderr_empty(r)


@setup(
    lambda f: f.replace("features/import.md", 12, AC_001_3_REMOVED),
    lambda f: f.replace("features/api.md", 19, "Traces: UJ-01; AC-001.3; `orders.id`"),
)
def test_traces_cites_removed_ac(built):
    """@prd T-124.5"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/features/api.md:19: id-removed-reused: FR-002 Traces cites removed AC-001.3"
    )
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 105, REMOVED_FR003_ROW))
def test_half_removed_is_not_removed(built):
    """@prd T-124.6"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_not_contains(r, ["cites removed FR-003", "of removed FR-003"])
    assert_stderr_empty(r)


# FR-125 index and blocks in step


@setup(lambda f: f.insert_after("prd.md", 104, "| FR-002 | Get an order | live | features/api.md | 1.0.0 |"))
def test_id_twice_in_index(built):
    """@prd T-125.1"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/prd.md:105: index-consistent: FR-002 appears twice in the section 11 index (first at prd.md:104)"
    )
    assert_stderr_empty(r)


@setup(lambda f: f.delete("prd.md", 102))
def test_block_with_no_row(built):
    """@prd T-125.2"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, "docs/prd/orders/features/api.md:3: index-consistent: UJ-01 has no row in the section 11 index")
    assert_stderr_empty(r)


@setup(lambda f: f.insert_after("prd.md", 106, "| FR-005 | Ghost | approved | features/api.md |  |"))
def test_row_with_no_block(built):
    """@prd T-125.3"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, "docs/prd/orders/prd.md:107: index-consistent: FR-005 is in the index but has no block")
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 104, "| FR-002 | Fetch an order | live | features/import.md | 1.0.0 |"))
def test_title_and_file_differ(built):
    """@prd T-125.4"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains(
        r,
        [
            "docs/prd/orders/prd.md:104: index-consistent: FR-002: index title 'Fetch an order' differs from block title 'Get an order'",
            "docs/prd/orders/prd.md:104: index-consistent: FR-002: index file 'features/import.md' differs from block file 'features/api.md'",
        ],
    )
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 104, "| FR-002 | Get an order | shipped | features/api.md | 1.0.0 |"))
def test_unknown_index_status(built):
    """@prd T-125.5"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, "docs/prd/orders/prd.md:104: index-consistent: FR-002: unknown index status 'shipped'")
    assert_not_contains(r, "index status 'shipped' differs")
    assert_stderr_empty(r)


@setup(lambda f: f.replace("features/import.md", 4, "Status: shipped"))
def test_unknown_block_status(built):
    """@prd T-125.6"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, "docs/prd/orders/features/import.md:3: index-consistent: FR-001: unknown status 'shipped'")
    assert_not_contains(r, "FR-001: index status 'live' differs")
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 104, "| FR-002 | Get an order | live | features/api.md |  |"))
def test_live_row_with_no_since(built):
    """@prd T-125.7"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(r, "docs/prd/orders/prd.md:104: index-consistent: FR-002 is live but the index has no Since")
    assert_stderr_empty(r)


@setup(lambda f: f.replace("features/api.md", 10, "Status: live"))
def test_live_block_with_no_since(built):
    """@prd T-125.8"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/features/api.md:9: index-consistent: FR-002 is live but its Status line has no '(since X.Y.Z)'"
    )
    assert_stderr_empty(r)


@setup(lambda f: f.replace("prd.md", 104, "| FR-002 | Get an order | built | features/api.md | 1.0.0 |"))
def test_statuses_differ(built):
    """@prd T-125.9"""
    r = run_lint(built)
    assert_exit(r, 1)
    assert_contains_line(
        r, "docs/prd/orders/prd.md:104: index-consistent: FR-002: index status 'built' differs from block status 'live'"
    )
    assert_stderr_empty(r)


@setup()
def test_fixture_index_consistent(built):
    """@prd T-125.10"""
    r = run_lint(built)
    assert_exit(r, 0)
    assert_not_contains(r, "index-consistent")
    assert_stderr_empty(r)


@pytest.mark.xfail(strict=True, raises=KnownFailure, reason="E-049")
@setup(
    lambda f: f.replace("prd.md", 104, T["title_row"]),
    lambda f: f.replace("features/api.md", 9, T["title_heading"]),
)
def test_title_with_code_span_matches(built):
    """@prd T-125.11 known-failing E-049"""
    r = run_lint(built)
    known_failure_if(
        any(
            "index-consistent: FR-002: index title" in line and "differs from block title" in line
            for line in r.stdout.splitlines()
        ),
        "E-049",
        "matching titles with a code span are reported as different",
        r,
    )
    assert_not_contains(r, "FR-002: index title")
    assert_stderr_empty(r)
