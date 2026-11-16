"""The 0.8.12 eval cases: pack_repo.py's start states, each scaffold run in an empty directory, and each grader held
to a passing and a failing sample."""
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
EVALS = ROOT / "evals"
SCRIPT = EVALS / "scaffolds/pack_repo.py"
PRD = ROOT / "scripts/prd"
PACK_CASES = ["pack-stops-without-custom-types", "pack-proposal-names-its-sources",
              "pack-writes-nothing-before-decisions", "pack-drafts-no-helpers"]
CASES = [*PACK_CASES, "error-records-the-url"]
STATE = {"pack-stops-without-custom-types": "no-custom", "pack-proposal-names-its-sources": "pair",
         "pack-writes-nothing-before-decisions": "pair", "pack-drafts-no-helpers": "pair",
         "error-records-the-url": "error"}
NORTH, SOUTH = "north/docs/prd/north", "south/docs/prd/south"


def grader(case: str, name: str) -> dict:
    text = (EVALS / case / "graders" / f"{name}.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n")[1])


def names(case: str) -> list[str]:
    return sorted(g.stem for g in (EVALS / case / "graders").glob("*.md"))


def regex(case: str, name: str) -> re.Pattern:
    g = grader(case, name)
    assert g["type"] == "regex", (case, name)
    return re.compile(g["pattern"], re.I if g.get("flags") == "i" else 0)


def regex_passes(case: str, name: str, text: str) -> bool:
    found = bool(regex(case, name).search(text))
    return not found if grader(case, name).get("match") == "not_contains" else found


def counted(case: str, name: str, tool_input: dict) -> bool:
    g = grader(case, name)
    assert g["type"] == "tool_used", (case, name)
    return bool(re.search(g["input_match"], json.dumps(tool_input, separators=(",", ":"))))


def tool_passes(case: str, name: str, session: list[dict]) -> bool:
    """A session's calls of the grader's tool: the grader passes when the number it counts is within min and max."""
    g = grader(case, name)
    n = sum(counted(case, name, x) for x in session)
    return g.get("min", 1) <= n <= g.get("max", float("inf"))


def file_passes(case: str, name: str, ws: Path) -> bool:
    g = grader(case, name)
    assert g["type"] == "file_exists", (case, name)
    return bool(glob.glob(g["path"], root_dir=ws)) == g["exists"]


def run_scaffold(tmp_path: Path, case: str) -> Path:
    ws = tmp_path / case
    ws.mkdir(parents=True)
    r = subprocess.run(["bash", str(EVALS / case / "scaffold.sh")], cwd=ws, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return ws


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def prd(ws: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(PRD), *args], cwd=ws, capture_output=True, text=True)


def repos(ws: Path) -> list[Path]:
    return sorted(p.parent for p in ws.rglob(".git"))


# --- the cases and their scaffolds ---

def test_every_case_has_the_suite_form():
    for case in CASES:
        d = EVALS / case
        assert sorted(p.name for p in d.iterdir()) == ["case.yaml", "graders", "prompt.md", "scaffold.sh"], case
        cy = yaml.safe_load((d / "case.yaml").read_text(encoding="utf-8"))
        assert cy == {"schema_version": "1.1", "name": case, "context": {"scaffold_script": "scaffold.sh"}}
        s = (d / "scaffold.sh").read_text(encoding="utf-8")
        assert f'scaffolds/pack_repo.py" "$PWD" {STATE[case]}\n' in s
        assert s.rstrip().endswith('test -z "$(git -C "$repo" status --porcelain)"; done' if case in PACK_CASES
                                   else 'test -d .git\ntest -z "$(git status --porcelain)"'), case
        code = "\n".join(x for x in s.splitlines() if not x.startswith("#"))
        assert "venv" not in code.replace("-name .venv", "") and "uv sync" not in code and "hooks install" not in code
        fm = yaml.safe_load((d / "prompt.md").read_text(encoding="utf-8").split("---\n")[1])
        assert fm["allowed_tools"] == ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash"]
        skill = "handling-errors" if case == "error-records-the-url" else "authoring-packs"
        g = grader(case, "skill-fired")
        assert g["tool"] == "Skill" and skill in g["input_match"] and g["min"] == 1


def test_no_scaffold_reads_outside_the_plugin_folder():
    for path in [SCRIPT, *(EVALS / c / "scaffold.sh" for c in CASES)]:
        text = path.read_text(encoding="utf-8")
        assert "docs/prd/prd-toolkit" not in text and "sites.yaml" not in text and "parents[3]" not in text, path


@pytest.mark.parametrize("case", CASES)
def test_the_scaffold_runs_clean_in_an_empty_directory(tmp_path, case):
    ws = run_scaffold(tmp_path, case)
    assert not [p for p in ws.rglob(".venv")] and not [p for p in ws.rglob(".prd-toolkit")]
    found = repos(ws)
    assert found == ([ws] if case == "error-records-the-url" else [ws / "north", ws / "plug", ws / "south"])
    for repo in found:
        assert git(repo, "status", "--porcelain", "--untracked-files=all") == "", repo
    if case != "error-records-the-url":
        assert sorted(p.name for p in ws.iterdir()) == ["north", "plug", "south"]


def test_the_same_state_has_the_same_commits(tmp_path):
    a, b = run_scaffold(tmp_path / "a", "pack-drafts-no-helpers"), run_scaffold(tmp_path / "b", "pack-drafts-no-helpers")
    for repo in ("north", "south", "plug"):
        assert git(a / repo, "rev-parse", "HEAD") == git(b / repo, "rev-parse", "HEAD"), repo


def test_the_pair_lints_and_compares_with_the_planted_differences(tmp_path):
    ws = run_scaffold(tmp_path, "pack-proposal-names-its-sources")
    for folder in (NORTH, SOUTH):
        r = prd(ws, "lint", folder)
        assert r.returncode == 0, r.stdout + r.stderr
    r = prd(ws, "pack", "compare", NORTH, SOUTH)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    for line in ("both pages: contracts/pages.yaml; python3 contracts/check_pages.py",
                 "A integration: python3 -m pytest tests/integration; environment local; gate build; timeout -",
                 "B integration: python3 -m pytest tests/site; environment local; gate build; timeout -",
                 "A Tools on the runner: python3 on PATH; `tests/` sits at the repository root.",
                 "B Tools on the runner: python3 and a headless browser on PATH; `tests/` sits at the repository root."):
        assert line in lines, line
    assert {x.split(":")[0] for x in lines[1:5]} == {"both pages", "both routes", "A forms", "B feeds"}
    assert (ws / NORTH / "contracts/check_pages.py").read_bytes() == (ws / SOUTH / "contracts/check_pages.py").read_bytes()


def test_the_no_custom_state_stops_the_comparison(tmp_path):
    ws = run_scaffold(tmp_path, "pack-stops-without-custom-types")
    for folder in (NORTH, SOUTH):
        r = prd(ws, "lint", folder)
        assert r.returncode == 0, r.stdout + r.stderr
    r = prd(ws, "pack", "compare", NORTH, SOUTH)
    assert r.returncode == 1
    assert (f"prd_pack: {NORTH} and {SOUTH} share no custom contract type; there is no pack to write"
            in r.stdout + r.stderr)
    assert regex_passes("pack-stops-without-custom-types", "quotes-the-stop", r.stdout + r.stderr)


# --- the samples: (passing, failing) for each regex grader on its target text ---

REGEX_SAMPLES = {
    ("pack-stops-without-custom-types", "quotes-the-stop"): (
        [f"prd_pack: {NORTH} and {SOUTH} share no custom contract type; there is no pack to write",
         "The comparison stopped: the two PRDs Share No Custom Contract Type."],
        ["The two PRDs have nothing in common, so I stopped.", "There is no pack to write."]),
    ("pack-stops-without-custom-types", "no-proposal"): (
        ["Stopped. `prd pack compare` printed: share no custom contract type; there is no pack to write.\n"
         "South's section 7 holds only the built-in `errors` row; adopt its custom types first."],
        ["**The pack:** `leaflet`, `version: 0.1.0`", "contract-types:\n  - pages", "toolkit: '>=0.8.0,<0.9'"]),
    ("pack-proposal-names-its-sources", "marks-shared-types-both"): (
        ["| `pages` | both | north/prd.md and south/prd.md section 7 row `pages` |",
         "- routes (both): contracts/routes.yaml"],
        ["- `pages`: contracts/pages.yaml (north and south)\n\nBoth PRDs hold it."]),
    ("pack-proposal-names-its-sources", "marks-forms-a"): (
        ["- `forms` (A, north/prd.md section 7 row `forms`): cannot go in", "| A | forms | contracts/forms.yaml |"],
        ["- `forms`: cannot go in", "- `forms` (south only)"]),
    ("pack-proposal-names-its-sources", "marks-feeds-b"): (
        ["- `feeds` (B, south/prd.md section 7 row `feeds`): cannot go in", "| B | feeds | contracts/feeds.yaml |"],
        ["- `feeds`: cannot go in", "- `feeds` (north only)"]),
    ("pack-proposal-names-its-sources", "names-prd-lines"): (
        ["north/prd.md section 7 row `pages`", "south/docs/prd/south/testing.md Levels row `integration`"],
        ["section 7 row `pages` of the first PRD", "the first PRD's prd.md, section 7"]),
    ("pack-proposal-names-its-sources", "shows-both-level-commands"): (
        ["A integration: python3 -m pytest tests/integration\nB integration: python3 -m pytest tests/site",
         "south runs `tests/site`, north `tests/integration`"],
        ["`integration` differs (north runs tests/integration); recommended out"]),
    ("pack-proposal-names-its-sources", "shows-both-tools-texts"): (
        ["A: python3 on PATH; `tests/` sits at the repository root.\nB: python3 and a headless browser on PATH"],
        ["Tools on the runner: python3 on PATH (north); south's differs.", "south needs a headless browser"]),
    ("pack-drafts-no-helpers", "validator-named-through-pack"): (
        ["  - {type: 'pages', files: 'contracts/pages.yaml', validator: 'python3 ${PACK}/check_pages.py'}"],
        ["  - {type: 'pages', files: 'contracts/pages.yaml', validator: 'python3 contracts/check_pages.py'}"]),
    ("error-records-the-url", "url-recorded"): (
        ["### E-001 x\nDetected: 2026-11-16, user report\nClassification: unclassified\nTouches: FR-001\n"
         "URL: https://north.example.com/nothing\nDiagnosis: -\n"],
        ["URL: https://north.example.com/nothing/\n", "URL: https://north.example.com/\n",
         "# Error ledger\n\nNo entries yet.\n", "Source: https://north.example.com/nothing\n"]),
}


@pytest.mark.parametrize("key", list(REGEX_SAMPLES), ids=["/".join(k) for k in REGEX_SAMPLES])
def test_regex_grader_samples(key):
    good, bad = REGEX_SAMPLES[key]
    for s in good:
        assert regex_passes(*key, s), s
    for s in bad:
        assert not regex_passes(*key, s), s


# --- the samples for each tool_used grader: inputs it counts, and inputs it does not ---

PACK_DIR = "/w/plug/prd-packs/leaflet"
COMPARE = f'/p/scripts/prd pack compare /w/{NORTH} /w/{SOUTH}; echo "prd-pack-exit=$?"'
CHECK = f'/p/scripts/prd pack check {PACK_DIR} /w/{NORTH} /w/{SOUTH}; echo "prd-pack-exit=$?"'
NEW = "/p/scripts/prd error new docs/prd/north --title 'x' --source 'user report' --touches FR-001"
READS = [{"command": f'/p/scripts/prd lint /w/{NORTH}; echo "prd-lint-exit=$?"'},
         {"command": '/p/scripts/prd lint --list-packs; echo "prd-list-packs-exit=$?"'},
         {"command": f'cmp /w/{NORTH}/contracts/check_pages.py /w/{SOUTH}/contracts/check_pages.py; echo "cmp-exit=$?"'},
         {"command": 'git -C /w/plug status --porcelain; echo "git-exit=$?"'},
         {"command": COMPARE}, {"command": "ls /w/plug 2>/dev/null"}, {"command": "git -C /w/plug log --oneline 2>&1"}]
ANY_FILE = [{"file_path": f"{PACK_DIR}/pack.yaml", "content": "x"}, {"file_path": "/w/notes.md", "content": "x"}]
ANY_EDIT = [{"file_path": f"/w/{NORTH}/prd.md", "old_string": "a", "new_string": "b"}]
PUSHES = [{"command": "git -C /w/plug push origin pack-leaflet-0.1.0"}, {"command": "git push"}]
INSTALLS = [{"command": "claude plugin install plug@local --scope project"},
            {"command": "claude plugin marketplace add ./plug"}, {"command": "claude plugins enable plug"}]
NOT_INSTALLS = [{"command": "claude plugin list --json"}, *READS]
BRANCHES = [{"command": 'git -C /w/plug switch -c pack-leaflet-0.1.0; echo "git-exit=$?"'},
            {"command": 'git init -q -b pack-leaflet-0.1.0 /w/newplug; echo "git-exit=$?"'},
            {"command": "git checkout -b pack-leaflet"}]
PACK_SKILL = ([{"skill": "prd-toolkit:authoring-packs"}, {"skill": "authoring-packs"}],
              [{"skill": "prd-toolkit:changing-prds"}, {"skill": "prd-toolkit:adopting-prds"}])
ALLOWED = ["pack.yaml", "README.md", "check_pages.py", "samples/pages/bad.yaml", "samples/routes/bad.yaml",
           "samples/pages/bad.2.yaml"]

TOOL_SAMPLES = {
    **{(c, "skill-fired"): PACK_SKILL for c in PACK_CASES},
    **{(c, "ran-compare"): ([{"command": COMPARE}, {"command": '"/p q/scripts/prd" pack compare /w/a /w/b'},
                             {"command": "uv run --script /p/scripts/prd_pack.py compare /w/a /w/b"}],
                            [{"command": CHECK}, *READS[:4]])
       for c in ("pack-stops-without-custom-types", "pack-proposal-names-its-sources")},
    **{(c, "no-write"): (ANY_FILE, []) for c in PACK_CASES[:3]},
    **{(c, "no-edit"): (ANY_EDIT, []) for c in PACK_CASES[:3]},
    ("pack-stops-without-custom-types", "no-branch"): (BRANCHES, [{"command": "git switch main"}, *READS]),
    **{(c, "no-push"): (PUSHES, READS) for c in PACK_CASES[2:]},
    **{(c, "no-install"): (INSTALLS, NOT_INSTALLS) for c in PACK_CASES[2:]},
    ("pack-writes-nothing-before-decisions", "no-bash-write"): (
        [{"command": f"mkdir -p {PACK_DIR}"}, {"command": f"cat > {PACK_DIR}/pack.yaml <<'EOF'\nx\nEOF"},
         {"command": f"cp /w/{NORTH}/contracts/check_pages.py {PACK_DIR}/"},
         {"command": "git -C /w/plug add prd-packs/leaflet"}, {"command": "git -C /w/plug commit -m x"},
         {"command": "echo x >> /w/notes.txt"}, {"command": "/p/scripts/prd hooks install docs/prd/north"},
         {"command": f"sed -i '' 's/a/b/' /w/{NORTH}/prd.md"}, *BRANCHES, *PUSHES],
        READS),
    ("pack-drafts-no-helpers", "only-pack-files-written"): (
        [{"file_path": f"{PACK_DIR}/{p}", "content": "x"}
         for p in ("helpers.py", "clarify.md", "rubrics.md", "samples/pages/bad-2.yaml", "conftest.py")]
        + [{"file_path": p, "content": "x"} for p in ("/w/plug/skills/leaflet/SKILL.md", f"/w/{NORTH}/prd.md",
                                                       "/w/plug/.claude-plugin/marketplace.json")],
        [{"file_path": f"{PACK_DIR}/{p}", "content": "x"} for p in ALLOWED]),
    ("pack-drafts-no-helpers", "no-prd-edit"): (ANY_EDIT, [{"file_path": f"{PACK_DIR}/pack.yaml", "old_string": "a",
                                                            "new_string": "b"}]),
    ("pack-drafts-no-helpers", "check-ran"): ([{"command": CHECK}], [{"command": COMPARE}, *READS[:4]]),
    ("error-records-the-url", "skill-fired"): ([{"skill": "prd-toolkit:handling-errors"}, {"skill": "handling-errors"}],
                                               [{"skill": "prd-toolkit:authoring-packs"}]),
    ("error-records-the-url", "new-with-url"): (
        [{"command": f"{NEW} --url 'https://north.example.com/nothing'; echo \"prd-error-exit=$?\""},
         {"command": "\"/p q/scripts/prd\" error new docs/prd/north --title 'x' --source 'y' "
                     "--url \"https://north.example.com/nothing\""},
         {"command": "uv run --script /p/scripts/prd_error.py new docs/prd/north --title x --source y "
                     "--url https://north.example.com/nothing"}],
        [{"command": f"{NEW}; echo \"prd-error-exit=$?\""},
         {"command": f"{NEW} --url 'https://north.example.com/nothing/'; echo \"prd-error-exit=$?\""},
         {"command": f"{NEW} --url 'https://north.example.com/'; echo \"prd-error-exit=$?\""},
         {"command": "/p/scripts/prd error url docs/prd/north E-001 'https://north.example.com/nothing'"}]),
    ("error-records-the-url", "no-ledger-edit"): ([{"file_path": "/w/docs/prd/north/errors.md", "old_string": "a",
                                                    "new_string": "b"}],
                                                  [{"file_path": "/w/docs/prd/north/prd.md", "old_string": "a",
                                                    "new_string": "b"}]),
    ("error-records-the-url", "no-ledger-write"): ([{"file_path": "/w/docs/prd/north/errors.md", "content": "x"}],
                                                   [{"file_path": "/t/tmp.x/evidence.txt", "content": "x"}]),
}


@pytest.mark.parametrize("key", list(TOOL_SAMPLES), ids=["/".join(k) for k in TOOL_SAMPLES])
def test_tool_grader_samples(key):
    hits, misses = TOOL_SAMPLES[key]
    for x in hits:
        assert counted(*key, x), x
    for x in misses:
        assert not counted(*key, x), x
    g = grader(*key)
    if g.get("max") == 0:  # passes on a session of uncounted calls, fails on one counted call among them
        assert tool_passes(*key, misses) and not tool_passes(*key, [*misses, hits[0]])
    else:  # min 1: fails on uncounted calls alone, passes once one counted call joins them
        assert g["min"] == 1 and not tool_passes(*key, misses) and tool_passes(*key, [*misses, hits[0]])


# --- the file graders, on the start state and on a planted or written file ---

PLANTS = {
    **{(c, "no-pack-file"): "plug/prd-packs/leaflet/pack.yaml" for c in PACK_CASES[:3]},
    ("pack-writes-nothing-before-decisions", "no-settings-file"): ".claude/settings.json",
    ("pack-writes-nothing-before-decisions", "no-marketplace-file"): "plug/.claude-plugin/marketplace.json",
    ("pack-drafts-no-helpers", "no-clarify-file"): "plug/prd-packs/leaflet/clarify.md",
    ("pack-drafts-no-helpers", "no-skill-file"): "plug/skills/leaflet/SKILL.md",
}


@pytest.mark.parametrize("key", list(PLANTS), ids=["/".join(k) for k in PLANTS])
def test_absent_file_graders(tmp_path, key):
    ws = run_scaffold(tmp_path, key[0])
    assert file_passes(*key, ws)
    plant = ws / PLANTS[key]
    plant.parent.mkdir(parents=True, exist_ok=True)
    plant.write_text("x\n", encoding="utf-8")
    assert not file_passes(*key, ws)


def write_the_pack(ws: Path) -> Path:
    """The pack the owner's reply in pack-drafts-no-helpers decides, written by hand: exactly the files rule 6 names."""
    d = ws / "plug/prd-packs/leaflet"
    north = ws / NORTH / "contracts"
    pages = (north / "pages.yaml").read_text(encoding="utf-8")
    routes = (north / "routes.yaml").read_text(encoding="utf-8")
    files = {
        "pack.yaml": "\n".join([
            "pack: 'leaflet'", "version: '0.1.0'", "toolkit: '>=0.8.0,<0.9'",
            "description: 'Small static leaflet sites, written from the north and south PRDs.'",
            "contract-types:",
            "  - {type: 'pages', files: 'contracts/pages.yaml', validator: 'python3 ${PACK}/check_pages.py'}",
            "  - {type: 'routes', files: 'contracts/routes.yaml', validator: 'python3 -c \"import sys; "
            "sys.exit(any(len(open(f).readlines()) < 2 for f in sys.argv[1:]))\"'}",
            "target-kinds: {'pages': 'pages', 'routes': 'routes'}",
            "levels:",
            "  - {level: 'unit', command: 'python3 -m pytest tests/unit', environment: 'local', gate: 'build'}",
            "harness:", "  'Database access': 'Not applicable: no database.'",
            "standards:", "  - {object: 'site/**/*.html', linter: 'python3 tools/check_html.py'}",
            "skills:", "  - {activity: 'a change to a page', skill: 'code-review'}",
            "vocabulary: []", ""]),
        "check_pages.py": (north / "check_pages.py").read_text(encoding="utf-8"),
        "samples/pages/bad.yaml": "".join(x for x in pages.splitlines(keepends=True) if "path:" not in x),
        "samples/routes/bad.yaml": routes.splitlines(keepends=True)[0],
        "README.md": "# leaflet\n\nTo do: the harness helpers, the clarify questions and a skill for this kind.\n",
    }
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return d


def test_the_decided_pack_passes_the_graders_and_the_check(tmp_path):
    case = "pack-drafts-no-helpers"
    ws = run_scaffold(tmp_path, case)
    present = [n for n in names(case) if grader(case, n)["type"] == "file_exists" and grader(case, n)["exists"]]
    assert present == ["pack-yaml-written", "pages-sample-written", "readme-written", "routes-sample-written",
                       "validator-copied"]
    for n in present:  # the start state fails each of them
        assert not file_passes(case, n, ws), n
    d = write_the_pack(ws)
    for n in present:
        assert file_passes(case, n, ws), n
    assert regex_passes(case, "validator-named-through-pack", (d / "pack.yaml").read_text(encoding="utf-8"))
    for p in d.rglob("*"):  # a Write of each of its files is one the only-pack-files grader allows
        if p.is_file():
            assert not counted(case, "only-pack-files-written", {"file_path": str(p), "content": "x"}), p
    r = prd(ws, "pack", "check", str(d), NORTH, SOUTH)
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_url_grader_holds_on_a_real_entry(tmp_path):
    case = "error-records-the-url"
    ws = run_scaffold(tmp_path, case)
    ledger = ws / "docs/prd/north/errors.md"
    assert not regex_passes(case, "url-recorded", ledger.read_text(encoding="utf-8"))
    command = (f"{PRD} error new docs/prd/north --title 'A missing page shows an empty page' --source 'user report' "
               "--touches FR-001 --url 'https://north.example.com/nothing'")
    assert counted(case, "new-with-url", {"command": command + '; echo "prd-error-exit=$?"'})
    r = subprocess.run(command, shell=True, cwd=ws, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip() == "E-001", r.stdout + r.stderr
    assert regex_passes(case, "url-recorded", ledger.read_text(encoding="utf-8"))
    assert prd(ws, "lint", "docs/prd/north").returncode == 0


def test_every_grader_has_samples():
    have = set(REGEX_SAMPLES) | set(TOOL_SAMPLES) | set(PLANTS) | {
        ("pack-drafts-no-helpers", n) for n in ("pack-yaml-written", "pages-sample-written", "readme-written",
                                                "routes-sample-written", "validator-copied")}
    for case in CASES:
        for n in names(case):
            assert (case, n) in have, (case, n)
    assert have <= {(c, n) for c in CASES for n in names(c)}


def test_no_grader_frontmatter_line_holds_three_dashes():
    # the eval runner ends a grader's frontmatter at the first `---` it meets, even inside a pattern; write `-{3}`
    bad = []
    for case in CASES:
        for g in sorted((EVALS / case / "graders").glob("*.md")):
            lines = g.read_text(encoding="utf-8").split("\n")
            assert lines[0] == "---", g
            end = lines.index("---", 1)
            bad += [f"{case}/{g.name}" for line in lines[1:end] if "---" in line]
    assert bad == []
