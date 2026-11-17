"""pack-authoring: `prd_pack.py compare` as text (FR-057; test-cases/pack-authoring.yaml)."""
from pack_authoring_support import KG, KL, KS, KV, K0, PACK, part_lines, part_titles, run

COMPARE = ("compare", "north/docs/prd/north", "south/docs/prd/south")

PAGES = ('python3 -c "import sys; sys.exit(any(not open(f).readline().rstrip().endswith(chr(58)) '
         'for f in sys.argv[1:]))"')
PAGES_61 = ('python3 -c "import sys; sys.exit(any(not open(f).readline().rstrip().endswith(chr(61)) '
            'for f in sys.argv[1:]))"')
ROUTES = 'python3 -c "import sys; sys.exit(any(len(open(f).readlines()) < 2 for f in sys.argv[1:]))"'
FORMS = 'python3 -c "import sys; sys.exit(any(len(open(f).readlines()) < 1 for f in sys.argv[1:]))"'
FEEDS = 'python3 -c "import sys; sys.exit(any(len(open(f).readlines()) < 3 for f in sys.argv[1:]))"'

CONTRACT_TYPES = [
    "## Contract types",
    "both pages: contracts/pages.yaml; " + PAGES,
    "both routes: contracts/routes.yaml; " + ROUTES,
    "A forms: contracts/forms.yaml; " + FORMS,
    "B feeds: contracts/feeds.yaml; " + FEEDS,
    "",
]
TARGET_KINDS = [
    "## Target kinds",
    "both pages: 2 in A, 1 in B",
    "both routes: 1 in A, 1 in B",
    "A forms: 1 in A, 0 in B",
    "B feeds: 0 in A, 1 in B",
    "",
]
LEVELS = [
    "## Levels",
    "both unit: python3 -m pytest tests/unit; environment local; gate build; timeout -",
    "A integration: python3 -m pytest tests/integration; environment local; gate build; timeout -",
    "B integration: python3 -m pytest tests/site; environment local; gate build; timeout -",
    "",
]
HARNESS = [
    "## Harness",
    "both Lifecycle: Nothing runs between tests; each test serves the site folder itself.",
    "both Environment switch: Not applicable: one test environment, `local`.",
    "both Database access: Not applicable: no database.",
    "A Tools on the runner: python3 on PATH; `tests/` sits at the repository root.",
    "B Tools on the runner: python3 and a headless browser on PATH; `tests/` sits at the repository root.",
    "both Clean state: Every test starts from its own temporary directory.",
    "both Persistent environments: Not applicable: no test environment keeps data.",
    "both Layout: `tests/<level>/test_<area>.py`; each test's docstring cites its T-id. Test roots: `tests/`",
    "both HTTP requests: Each test requests a path of the site it serves.",
    "both Fixtures: Not applicable: the cases give their input inline.",
    "both Browser identity: Not applicable: no sign-in.",
    "both Assertions: Fields a case does not list are not asserted.",
    "both Waits: Not applicable: every request completes before the test asserts.",
    "both Effects: Not applicable: the cases assert responses only.",
    "both Leaks: Not applicable: no classified data.",
    "both Acceptance: Not applicable: no acceptance level.",
    "",
]
STANDARDS = [
    "## Standards",
    "both site/**/*.html: python3 tools/check_html.py",
    "",
]
SKILLS = [
    "## Skills",
    "both a change to a page: code-review",
    "",
]
VOCABULARY = [
    "## Vocabulary",
    "both page: 6 in A, 5 in B",
    "both visitor: 5 in A, 4 in B",
    "both site: 4 in A, 4 in B",
    "both address: 3 in A, 3 in B",
    "both opens: 3 in A, 3 in B",
    "both path: 3 in A, 3 in B",
    "both answer: 2 in A, 2 in B",
    "both redirect: 2 in A, 2 in B",
    "both with: 2 in A, 2 in B",
    "both each: 1 in A, 2 in B",
    "both error: 1 in A, 1 in B",
    "both file: 1 in A, 1 in B",
    "both holds: 1 in A, 1 in B",
    "both missing: 1 in A, 1 in B",
    "both serve: 1 in A, 1 in B",
    "both that: 1 in A, 1 in B",
    "",
]


def test_compare_prints_seven_parts(tmp_path, monkeypatch):
    """@prd T-057.1"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert r.stderr == ""
    assert part_titles(r.stdout) == [
        "## Contract types",
        "## Target kinds",
        "## Levels",
        "## Harness",
        "## Standards",
        "## Skills",
        "## Vocabulary",
    ]
    assert r.lines == CONTRACT_TYPES + TARGET_KINDS + LEVELS + HARNESS + STANDARDS + SKILLS + VOCABULARY


def test_compare_contract_types(tmp_path, monkeypatch):
    """@prd T-057.2"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Contract types") == CONTRACT_TYPES


def test_compare_target_kinds(tmp_path, monkeypatch):
    """@prd T-057.3"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Target kinds") == TARGET_KINDS


def test_compare_levels(tmp_path, monkeypatch):
    """@prd T-057.4"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Levels") == LEVELS


def test_compare_harness(tmp_path, monkeypatch):
    """@prd T-057.5"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Harness") == HARNESS


def test_compare_standards_and_skills(tmp_path, monkeypatch):
    """@prd T-057.6"""
    K0(tmp_path, monkeypatch)
    KS(tmp_path)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Standards") == [
        "## Standards",
        "both site/**/*.html: python3 tools/check_html.py",
        "",
    ]
    assert part_lines(r.stdout, "Skills") == [
        "## Skills",
        "both a change to a page: code-review",
        "B a new page: security-review",
        "",
    ]


def test_compare_linter_cell_without_backticks(tmp_path, monkeypatch):
    """@prd T-057.9"""
    K0(tmp_path, monkeypatch)
    KL(tmp_path)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Standards") == [
        "## Standards",
        "both site/**/*.html: python3 tools/check_html.py",
        "",
    ]


def test_compare_differences_printed_side_by_side(tmp_path, monkeypatch):
    """@prd T-057.7"""
    K0(tmp_path, monkeypatch)
    KV(tmp_path)
    KG(tmp_path)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Contract types") == [
        "## Contract types",
        "A pages: contracts/pages.yaml; " + PAGES,
        "B pages: contracts/pages.yaml; " + PAGES_61,
        "A routes: contracts/routes.yaml; " + ROUTES,
        "B routes: contracts/routes/*.yaml; " + ROUTES,
        "A forms: contracts/forms.yaml; " + FORMS,
        "B feeds: contracts/feeds.yaml; " + FEEDS,
        "",
    ]


def test_compare_vocabulary(tmp_path, monkeypatch):
    """@prd T-057.8"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *COMPARE, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert part_lines(r.stdout, "Vocabulary") == VOCABULARY
