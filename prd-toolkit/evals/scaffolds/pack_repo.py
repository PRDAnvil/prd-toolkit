"""Build the start state for the authoring-packs evals and the error-records-the-url eval.

Usage (from the eval workspace; never write into the plugin tree):
    python3 -B <this file> <dst> <pair|no-custom|error>

Two scratch repositories of one invented kind, a static leaflet site, each holding one Approved PRD that lints
clean: `north/` (docs/prd/north) and `south/` (docs/prd/south), the two sample PRDs of the toolkit's own
pack-authoring fixture, with one change: the `pages` validator is a file of each repository,
`contracts/check_pages.py` (the same bytes in both), so a written pack carries a validator file. Beside them
`plug/`, a plugin checkout (`.claude-plugin/plugin.json` and a README, no `prd-packs/`) for the owner to name.

pair       north, south and plug in <dst>. `prd pack compare` marks `pages` and `routes` `both`, `forms` `A` and
           `feeds` `B`, and prints two paired differences: the `integration` level's command (`tests/integration`
           in north, `tests/site` in south) and the Harness slot `Tools on the runner` (south adds a headless
           browser).
no-custom  as pair, but south's section 7 holds only the built-in `errors` row: its custom types, their contract
           files and the test cases that targeted them are gone, so `prd pack compare` exits 1 (`share no custom
           contract type; there is no pack to write`).
error      north alone, as the repository <dst> itself, with `site/index.html`: the PRD a user's report about a
           page of the site is recorded against.

No state holds a `.venv`, a vendored `.prd-toolkit/` or a CLAUDE.md: every `prd` command runs the plugin's own
scripts. Every commit has a fixed date and identity, so every SHA is the same on every build, and every repository
is clean.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
from legacy import commit, git  # noqa: E402

STATES = ("pair", "no-custom", "error")

CHECK_PAGES = '''"""Each pages file names an entry on its first line and gives each entry a path."""
import sys

bad = 0
for name in sys.argv[1:]:
    lines = open(name, encoding="utf-8").read().splitlines()
    if not lines or not lines[0].rstrip().endswith(":"):
        print(f"{name}: the first line does not name an entry", file=sys.stderr)
        bad = 1
    elif not any(line.strip().startswith("path:") for line in lines[1:]):
        print(f"{name}: an entry has no path", file=sys.stderr)
        bad = 1
sys.exit(bad)
'''

ROUTES_VALIDATOR = 'python3 -c "import sys; sys.exit(any(len(open(f).readlines()) < 2 for f in sys.argv[1:]))"'
FORMS_VALIDATOR = 'python3 -c "import sys; sys.exit(any(len(open(f).readlines()) < 1 for f in sys.argv[1:]))"'
FEEDS_VALIDATOR = 'python3 -c "import sys; sys.exit(any(len(open(f).readlines()) < 3 for f in sys.argv[1:]))"'

PRD = """---
prd: {slug}
version: 1.0.0
status: Approved
owner: Sample Owner
updated: 2026-11-01
---

# {title} leaflet site

## 1. Metadata & stack

- Language: HTML pages built from YAML contracts
- Not applicable: `contracts/openapi.yaml` — no HTTP API
- Not applicable: `contracts/schema.sql` — no database
- Not applicable: `contracts/events.md` — no events or jobs
- Not applicable: `contracts/permissions.yaml` — no roles
- Not applicable: `contracts/config.yaml` — no settings
- Not applicable: `contracts/data-classification.yaml` — no stored personal data
- Not applicable: `contracts/dependencies/` — no third-party service
- Not applicable: `contracts/fixtures/` — no fixture data

## 2. Summary & goals

The {slug} site is a leaflet of three pages.

Goals:

- Publish a page within 1 day of its approval.

## 3. Glossary

| Term | Meaning | Banned synonyms |
|---|---|---|
| page | One HTML file a visitor opens | screen |

## 4. Architecture

The site is a folder of static files.

## 5. Standards registry

| Object (glob) | Linter command | Rules live in | Applies to | Decision |
|---|---|---|---|---|
| `site/**/*.html` | `python3 tools/check_html.py` | `tools/check_html.py` | every page | enforced |

## 6. Skills registry

| Object or activity | Skill | Decision |
|---|---|---|
| a change to a page | code-review | recommended |

## 7. Contract types

| Type | Files (glob) | Validator |
|---|---|---|
| errors | `contracts/errors.yaml` | built-in |
{types}
## 8. Adoption map

Not applicable: new project.

## 9. Versioning

- Breaking: removing a page or a route.

## 10. Design & UI

Not applicable: the pages keep the site's own style.

## 11. Requirement index

| ID | Title | Status | File | Since |
|---|---|---|---|---|
| FR-001 | Serve each page at its path | verified | features/site.md | 1.0.0 |
| FR-002 | Redirect an old address | verified | features/site.md | 1.0.0 |
| FR-003 | {fr3} | verified | features/site.md | 1.0.0 |

## 12. Assumptions index

| ID | Assumption | Status |
|---|---|---|

## 13. Open questions

None.

## 14. Changelog

| Version | Date | Change | IDs |
|---|---|---|---|
| 1.0.0 | 2026-11-01 | Initial release; no dry run (fixture) | FR-001, FR-002, FR-003 |
"""

TYPE_ROWS = {
    "pages": "| pages | `contracts/pages.yaml` | `python3 contracts/check_pages.py` |",
    "routes": f"| routes | `contracts/routes.yaml` | `{ROUTES_VALIDATOR}` |",
    "forms": f"| forms | `contracts/forms.yaml` | `{FORMS_VALIDATOR}` |",
    "feeds": f"| feeds | `contracts/feeds.yaml` | `{FEEDS_VALIDATOR}` |",
}

FEATURES = """# Site

### FR-001 Serve each page at its path
Status: verified
Acceptance (EARS):
- AC-001.1 When a visitor opens a page's path, the site shall answer with that page's `index.html` file.
- AC-001.2 If a visitor opens a path no page holds, the site shall answer with error PAGE_MISSING.
Errors: PAGE_MISSING (contracts/errors.yaml)
Tests: T-001.1 [integration], T-001.2 [integration]  (test-cases/site.yaml)

### FR-002 Redirect an old address
Status: verified
Acceptance (EARS):
- AC-002.1 When a visitor opens an old address, the site shall redirect the visitor to its new address.
Errors: -
Tests: T-002.1 [integration]  (test-cases/site.yaml)

### FR-003 {fr3}
Status: verified
Acceptance (EARS):
- AC-003.1 {ac3}
Errors: -
Tests: T-003.1 [integration]  (test-cases/site.yaml)
"""

CASE = """T-{tid}:
  ac: AC-{tid}
  level: integration
  target: {target}
  environment: local
  identity: none
  preconditions: []
  input: {input}
  expect:
    output: {output}
    effects: []
    errors: {errors}
    leaks: none
"""

TESTING = """# Testing

## Levels

| Level | Harness command | Environment | Gate |
|---|---|---|---|
| unit | `python3 -m pytest tests/unit` | local | build |
| integration | `python3 -m pytest tests/{integration}` | local | build |

## Harness

- **Lifecycle.** Nothing runs between tests; each test serves the site folder itself.
- **Environment switch.** Not applicable: one test environment, `local`.
- **Database access.** Not applicable: no database.
- **Tools on the runner.** {tools} on PATH; `tests/` sits at the repository root.
- **Clean state.** Every test starts from its own temporary directory.
- **Persistent environments.** Not applicable: no test environment keeps data.
- **Layout.** `tests/<level>/test_<area>.py`; each test's docstring cites its T-id. Test roots: `tests/`
- **HTTP requests.** Each test requests a path of the site it serves.
- **Fixtures.** Not applicable: the cases give their input inline.
- **Browser identity.** Not applicable: no sign-in.
- **Assertions.** Fields a case does not list are not asserted.
- **Waits.** Not applicable: every request completes before the test asserts.
- **Effects.** Not applicable: the cases assert responses only.
- **Leaks.** Not applicable: no classified data.
- **Acceptance.** Not applicable: no acceptance level.

## Environments

| Environment | Purpose | Access | Base URL | Database | Logs |
|---|---|---|---|---|---|
| local | a developer's checkout | anyone with a clone | none | none | the command's output |

## Leak checks

| Sink | Read from | Scanned for |
|---|---|---|
| command output | the test captures stdout and stderr | nothing: no classified data |

## Fixtures

| Fixture | Creates | Load | Teardown |
|---|---|---|---|

## Sign-offs

| T-id | Owner | Date | Result |
|---|---|---|---|
"""

ERRORS_YAML = """PAGE_MISSING:
  meaning: No page holds the path.
  when: A visitor opens a path that no entry of contracts/pages.yaml holds.
  status: 404
  message: No page holds this path.
  log_level: info
  retryable: false
  metric: site_page_missing_total
"""

COMMON = {
    "errors.md": "# Error ledger\n\nNo entries yet. Add `### E-001 <title>` when the first error is diagnosed.\n",
    "nfr.md": "# Non-functional requirements\n\n## Observability\n\nNot applicable: the site is static files.\n",
    "operations.md": "# Operations\n\nNo environment: the fixture site is not deployed.\n",
    "contracts/errors.yaml": ERRORS_YAML,
}

PAGES_YAML = "home:\n  path: site/index.html\n  title: Home\n"
ROUTES_YAML = "old-home:\n  from: /index.htm\n  to: /\n"

SITE = {
    "north": {
        "title": "North",
        "fr3": "Send the contact form",
        "ac3": "When a visitor sends the contact form, the site shall show the thanks page.",
        "third": "forms",
        "third_case": {"target": "forms:contact", "input": "{form: contact}", "output": "{shows: thanks}"},
        "third_file": ("contracts/forms.yaml", "contact:\n  action: /thanks\n"),
        "t12_target": "pages:home",
        "integration": "integration",
        "tools": "python3",
    },
    "south": {
        "title": "South",
        "fr3": "List each story in the news feed",
        "ac3": "When an editor adds a story, the site shall list the story in the news feed.",
        "third": "feeds",
        "third_case": {"target": "feeds:news", "input": '{story: "Spring fair"}', "output": "{listed: true}"},
        "third_file": ("contracts/feeds.yaml", "news:\n  path: site/news.xml\n  items: 10\n"),
        "t12_target": "code:site.serve",
        "integration": "site",
        "tools": "python3 and a headless browser",
    },
}

PLUGIN_JSON = {"name": "plug", "description": "prd-toolkit packs for small sites."}
PLUGIN_README = """# plug

A plugin that holds prd-toolkit packs, one folder each under `prd-packs/`. It holds none yet.
"""

SITE_INDEX = "<!doctype html>\n<title>Home</title>\n<h1>Home</h1>\n"


def _case(tid: str, target: str, input: str, output: str, errors: str = "[]") -> str:
    return CASE.format(tid=tid, target=target, input=input, output=output, errors=errors)


def _prd_files(slug: str, custom: bool) -> dict[str, str]:
    """The files of docs/prd/<slug>, relative to the PRD folder. Without `custom`, section 7 keeps only `errors`, and
    every case that targeted a custom type targets `code:site.serve` instead."""
    s = SITE[slug]
    types = [TYPE_ROWS[t] for t in ("pages", "routes", s["third"])] if custom else []
    code = "code:site.serve"
    cases = [
        _case("001.1", "pages:home" if custom else code, '{path: "/"}', "{status: 200}"),
        _case("001.2", s["t12_target"] if custom else code, '{path: "/nothing"}', "{status: 404}", "[PAGE_MISSING]"),
        _case("002.1", "routes:old-home" if custom else code, '{path: "/index.htm"}', '{status: 301, location: "/"}'),
        _case("003.1", s["third_case"]["target"] if custom else code, s["third_case"]["input"],
              s["third_case"]["output"]),
    ]
    files = {
        **COMMON,
        "prd.md": PRD.format(slug=slug, title=s["title"], fr3=s["fr3"],
                             types="".join(row + "\n" for row in types)),
        "features/site.md": FEATURES.format(fr3=s["fr3"], ac3=s["ac3"]),
        "test-cases/site.yaml": "\n".join(cases),
        "testing.md": TESTING.format(integration=s["integration"], tools=s["tools"]),
    }
    if custom:
        files.update({"contracts/pages.yaml": PAGES_YAML, "contracts/routes.yaml": ROUTES_YAML,
                      "contracts/check_pages.py": CHECK_PAGES, s["third_file"][0]: s["third_file"][1]})
    return files


def _write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def _site_repo(repo: Path, slug: str, custom: bool, extra: dict[str, str] | None = None) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "--initial-branch=main")
    _write(repo / "docs/prd" / slug, _prd_files(slug, custom))
    paths = ["docs"]
    if extra:
        _write(repo, extra)
        paths += sorted({rel.split("/", 1)[0] for rel in extra})
    commit(repo, f"{slug}: the leaflet site's PRD (1.0.0)\n\nRefs: FR-001, FR-002, FR-003", *paths,
           date="2026-11-01T12:00:00+0000")


def _plugin(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "--initial-branch=main")
    _write(repo, {".claude-plugin/plugin.json": json.dumps(PLUGIN_JSON, indent=2) + "\n", "README.md": PLUGIN_README})
    commit(repo, "plug: an empty plugin for packs", ".claude-plugin", "README.md", date="2026-11-02T12:00:00+0000")


def main(dst: str, state: str) -> None:
    root = Path(dst)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        sys.exit(f"refusing a non-empty destination: {root}")
    root.mkdir(parents=True, exist_ok=True)
    if state == "error":
        _site_repo(root, "north", True, {"site/index.html": SITE_INDEX})
        return
    _site_repo(root / "north", "north", True)
    _site_repo(root / "south", "south", state == "pair")
    _plugin(root / "plug")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in STATES:
        sys.exit(f"usage: pack_repo.py <dst> <{'|'.join(STATES)}>")
    main(sys.argv[1], sys.argv[2])
