"""The report's parts: layout, Header, Requirements, Areas, Adoption map, Not built and Not verified, Open errors
(FR-223 to FR-229; test-cases/status.yaml)."""
from __future__ import annotations

from status_support import part_lines, part_titles, repo, status, status_items, steps  # noqa: F401

MATRIX = ["## Matrix", "", "FR-001: T-001.1 integration build cited", "FR-002: T-002.1 integration build cited",
          "FR-003: T-003.1 integration build cited", "FR-004: T-004.1 integration build cited",
          "FR-005: T-005.1 integration build cited; T-005.2 judged build cited",
          "FR-006: T-006.1 integration build cited", "FR-007: T-007.1 integration build cited"]


def _report(repo, text="python STATUS .", **kw):
    r = status(repo, text, **kw)
    assert r.exit == 0, r.stderr
    return r


@steps("N0")
def test_t223_1_layout(repo):
    """@prd T-223.1"""
    r = _report(repo)
    assert r.err == b""
    assert part_titles(r.stdout) == [
        "## Next", "## Header", "## Requirements", "## Areas", "## Adoption map", "## Not built", "## Not verified",
        "## Open errors", "## Upstreams", "## Consumers", "## Change sets", "## CI", "## Deployed", "## Matrix"]
    assert part_lines(r.stdout, "Header") == ["## Header", "", "PRD: .", "version 1.0.0", "status Approved", ""]
    assert part_lines(r.stdout, "Not verified") == [
        "## Not verified", "", "FR-002 Skip a duplicate order (features/import.md)", ""]
    assert part_lines(r.stdout, "Matrix") == MATRIX


@steps("N0")
def test_t223_2_none_lines(repo):
    """@prd T-223.2"""
    r = _report(repo)
    for title in ("Open errors", "Upstreams", "Consumers", "Change sets", "Deployed"):
        assert part_lines(r.stdout, title) == [f"## {title}", "", "None.", ""], title


@steps("N0", "NA1", "NE1", "SK1", "SC1", "SD0", "SD1")
def test_t223_3_json_ids(repo):
    """@prd T-223.3"""
    r = _report(repo, "python STATUS --json .")
    assert status_items(r.stdout) == [
        {"part": "Header", "id": None, "text": "PRD: .\nversion 1.0.0\nstatus Approved"},
        {"part": "Requirements", "id": None, "text": "import: approved 1, built 1, live 1, verified 1"},
        {"part": "Requirements", "id": None, "text": "reports: approved 1, live 2"},
        {"part": "Areas", "id": "billing", "text": "billing: pack service (default), output language en"},
        {"part": "Areas", "id": "export", "text": "export: pack service (default), output language en"},
        {"part": "Areas", "id": "import", "text": "import: pack service (default), output language en"},
        {"part": "Areas", "id": "reports", "text": "reports: pack service (default), output language en"},
        {"part": "Adoption map", "id": "import", "text": "import | adopted | src/import/**"},
        {"part": "Adoption map", "id": "reports", "text": "reports | adopted | src/reports/**"},
        {"part": "Adoption map", "id": "billing", "text": "billing | extracted | src/billing/**"},
        {"part": "Adoption map", "id": "export", "text": "export | extracted | src/export/**"},
        {"part": "Adoption map", "id": "audit", "text": "audit | not started | src/audit/**"},
        {"part": "Not built", "id": "FR-001", "text": "FR-001 Refuse a file with no header (features/import.md)"},
        {"part": "Not built", "id": "FR-005", "text": "FR-005 Print the monthly report (features/reports.md)"},
        {"part": "Not verified", "id": "FR-002", "text": "FR-002 Skip a duplicate order (features/import.md)"},
        {"part": "Open errors", "id": "E-001", "text": "E-001 confirmed code bug — The importer stops at row 1000"},
        {"part": "Open errors", "id": "E-002", "text": "E-002 unclassified — A monthly report printed no total"},
        {"part": "Upstreams", "id": "greet",
         "text": "greet 1.1.0 at 4f1c9a2, needs default, check: not run (git URL; run prd_links.py check)"},
        {"part": "Consumers", "id": "dashboards", "text": "dashboards git@example.com:org/bi.git#docs/prd/dashboards"},
        {"part": "Change sets", "id": "CS-001", "text": "CS-001 running: billing approved; orders proposed"},
        {"part": "CI", "id": None, "text": "stale: CLAUDE.md; run prd_block.py docs/prd/orders"},
        {"part": "CI", "id": None, "text": "stale: docs/prd/orders/README.md; run prd_block.py docs/prd/orders"},
        {"part": "CI", "id": None, "text": "stale: docs/prd/README.md; run prd_block.py docs/prd/orders"},
        {"part": "Deployed", "id": "production", "text": "production: 1.0.0 at 3f2c1a9, 2026-11-02"},
        {"part": "Matrix", "id": "FR-001", "text": "FR-001: T-001.1 integration build cited"},
        {"part": "Matrix", "id": "FR-002", "text": "FR-002: T-002.1 integration build cited"},
        {"part": "Matrix", "id": "FR-003", "text": "FR-003: T-003.1 integration build cited"},
        {"part": "Matrix", "id": "FR-004", "text": "FR-004: T-004.1 integration build cited"},
        {"part": "Matrix", "id": "FR-005", "text": "FR-005: T-005.1 integration build cited; T-005.2 judged build cited"},
        {"part": "Matrix", "id": "FR-006", "text": "FR-006: T-006.1 integration build cited"},
        {"part": "Matrix", "id": "FR-007", "text": "FR-007: T-007.1 integration build cited"},
    ]


@steps("N0")
def test_t224_1_header_dot(repo):
    """@prd T-224.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Header") == ["## Header", "", "PRD: .", "version 1.0.0", "status Approved", ""]


@steps("N0")
def test_t224_2_header_relative(repo):
    """@prd T-224.2"""
    r = _report(repo, "python STATUS docs/prd/orders", cwd=repo)
    assert part_lines(r.stdout, "Header") == [
        "## Header", "", "PRD: docs/prd/orders", "version 1.0.0", "status Approved", ""]


@steps("N0")
def test_t224_3_header_absolute(repo):
    """@prd T-224.3"""
    r = _report(repo, "python STATUS ../docs/prd/orders", cwd=repo / "tests")
    assert part_lines(r.stdout, "Header") == [
        "## Header", "", f"PRD: {repo.resolve()}/docs/prd/orders", "version 1.0.0", "status Approved", ""]


@steps("N0", "SH0")
def test_t224_4_header_no_status(repo):
    """@prd T-224.4"""
    r = _report(repo)
    assert part_lines(r.stdout, "Header") == ["## Header", "", "PRD: .", "version 1.0.0", "status -", ""]


@steps("N0", "SN1")
def test_t225_1_requirements(repo):
    """@prd T-225.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Requirements") == [
        "## Requirements", "", "import: approved 1, built 1, live 1, verified 1", "reports: approved 1, live 2",
        "nfr: verified 1", ""]


@steps("N0", "SZ")
def test_t225_2_requirements_none(repo):
    """@prd T-225.2"""
    r = _report(repo)
    assert part_lines(r.stdout, "Requirements") == ["## Requirements", "", "None.", ""]


@steps("N0")
def test_t226_1_areas_default(repo):
    """@prd T-226.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Areas") == [
        "## Areas", "", "import: pack service (default), output language en",
        "reports: pack service (default), output language en", ""]


@steps("N0", "SA1")
def test_t226_2_areas_target(repo):
    """@prd T-226.2"""
    r = _report(repo)
    assert part_lines(r.stdout, "Areas") == [
        "## Areas", "", "import: pack service (default), output language en",
        "reports: pack service (default), output language pt-BR", ""]


@steps("N0", "SP1", "SA1")
def test_t226_3_areas_pack(repo):
    """@prd T-226.3"""
    r = _report(repo)
    assert part_lines(r.stdout, "Areas") == [
        "## Areas", "", "import: pack document 1.0.0, output language en",
        "reports: pack document 1.0.0, output language pt-BR", ""]


@steps("N0", "SZ")
def test_t226_4_areas_none(repo):
    """@prd T-226.4"""
    r = _report(repo)
    assert part_lines(r.stdout, "Areas") == ["## Areas", "", "None.", ""]


@steps("N0")
def test_t227_1_adoption_new_project(repo):
    """@prd T-227.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Adoption map") == ["## Adoption map", "", "Not applicable: new project", ""]


@steps("N0", "NA1")
def test_t227_2_adoption_rows(repo):
    """@prd T-227.2"""
    r = _report(repo)
    assert part_lines(r.stdout, "Adoption map") == [
        "## Adoption map", "", "import | adopted | src/import/**", "reports | adopted | src/reports/**",
        "billing | extracted | src/billing/**", "export | extracted | src/export/**",
        "audit | not started | src/audit/**", ""]


@steps("N0", "NA1", "SA2")
def test_t227_3_adoption_globs(repo):
    """@prd T-227.3"""
    r = _report(repo)
    assert part_lines(r.stdout, "Adoption map") == [
        "## Adoption map", "", "import | adopted | src/import/**, tests/test_import.py",
        "reports | adopted | src/reports/**", "billing | extracted | src/billing/**",
        "export | extracted | src/export/**", "audit | not started | -", ""]


@steps("N0", "NA1", "SA3")
def test_t227_4_adoption_no_rows(repo):
    """@prd T-227.4"""
    r = _report(repo)
    assert part_lines(r.stdout, "Adoption map") == ["## Adoption map", "", "None.", ""]


@steps("N0")
def test_t228_1_not_built(repo):
    """@prd T-228.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Not built") == [
        "## Not built", "", "FR-001 Refuse a file with no header (features/import.md)",
        "FR-005 Print the monthly report (features/reports.md)", ""]


@steps("N0", "NB2")
def test_t228_2_not_verified(repo):
    """@prd T-228.2"""
    r = _report(repo)
    assert part_lines(r.stdout, "Not built") == [
        "## Not built", "", "FR-005 Print the monthly report (features/reports.md)", ""]
    assert part_lines(r.stdout, "Not verified") == [
        "## Not verified", "", "FR-001 Refuse a file with no header (features/import.md)",
        "FR-002 Skip a duplicate order (features/import.md)", ""]


@steps("N0", "NLV")
def test_t228_3_all_live(repo):
    """@prd T-228.3"""
    r = _report(repo)
    assert part_lines(r.stdout, "Not built") == ["## Not built", "", "None.", ""]
    assert part_lines(r.stdout, "Not verified") == ["## Not verified", "", "None.", ""]


@steps("N0", "NE1")
def test_t229_1_open_errors(repo):
    """@prd T-229.1"""
    r = _report(repo)
    assert part_lines(r.stdout, "Open errors") == [
        "## Open errors", "", "E-001 confirmed code bug — The importer stops at row 1000",
        "E-002 unclassified — A monthly report printed no total", ""]


@steps("N0", "NE2")
def test_t229_2_open_errors_proposed(repo):
    """@prd T-229.2"""
    r = _report(repo)
    assert part_lines(r.stdout, "Open errors") == [
        "## Open errors", "", "E-001 proposed code bug — The importer stops at row 1000", ""]


@steps("N0", "SE1")
def test_t229_3_resolved_not_listed(repo):
    """@prd T-229.3"""
    r = _report(repo)
    assert part_lines(r.stdout, "Open errors") == ["## Open errors", "", "None.", ""]
