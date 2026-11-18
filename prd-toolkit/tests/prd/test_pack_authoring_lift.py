"""pack-authoring: `prd_change.py pack ... --lift` and the version move beside it (FR-060; test-cases/pack-authoring.yaml)."""
from pack_authoring_support import (
    CHANGE, CONTEXT, FIXTURES_LINE, KA, KB, KC, KD, KE, KH, KP7, KR1, KT1, KT2, KX, K0, LINT,
    diff, hunk_lines, north, read, run, sites, status, untoday,
)

PRD = "docs/prd/north"
LIFT = ("pack", PRD, "leaflet", "0.1.0", "--lift")
PACK_LINE = "- Pack: leaflet 0.1.0 (leaflet-kit@example)"
ROW = "| 1.0.1 | <today> | pack leaflet 0.1.0 lifted; pending | - |"
PAGES_ROW = ('| pages | `contracts/pages.yaml` | `python3 -c "import sys; sys.exit(any(not open(f).readline()'
             '.rstrip().endswith(chr(58)) for f in sys.argv[1:]))"` |')
ROUTES_ROW = ('| routes | `contracts/routes.yaml` | `python3 -c "import sys; sys.exit(any(len(open(f).readlines())'
              ' < 2 for f in sys.argv[1:]))"` |')
PAGES_PACK = "| pages | `contracts/pages.yaml` | pack |"
ROUTES_PACK = "| routes | `contracts/routes.yaml` | pack |"
PORCELAIN_PRD = [" M docs/prd/north/prd.md"]


def _north_prd_text() -> str:
    return sites()["north/docs/prd/north/prd.md"]


def _lifted_lines(original: str) -> list:
    """north's prd.md as T-060.1's effects give it, from the text K0 committed; `<today>` left as written."""
    orig = original.splitlines()
    assert orig[20] == FIXTURES_LINE, orig[20]
    head = orig[:21]
    head[head.index("version: 1.0.0")] = "version: 1.0.1"
    head[head.index("updated: 2026-11-01")] = "updated: <today>"
    tail = orig[21:]
    tail[tail.index(PAGES_ROW)] = PAGES_PACK
    tail[tail.index(ROUTES_ROW)] = ROUTES_PACK
    assert orig[-1].startswith("| 1.0.0 |"), orig[-1]
    return head + [PACK_LINE] + tail + [ROW]


def test_lift(tmp_path, monkeypatch):
    """@prd T-060.1"""
    K0(tmp_path, monkeypatch)
    repo = tmp_path / "north"
    r = run(CHANGE, *LIFT, cwd=repo)
    assert r.code == 0, r.stderr
    assert r.stderr == ""
    out = ["1.0.1", ROW]
    assert untoday(r.lines, out, r.dates) == out
    expected = _lifted_lines(_north_prd_text())
    actual = read(north(tmp_path) / "prd.md").splitlines()
    assert untoday(actual, expected, r.dates) == expected
    assert actual[21] == PACK_LINE
    assert actual[20] == FIXTURES_LINE
    assert status(repo).splitlines() == PORCELAIN_PRD


def test_lift_refused_when_a_pack_is_named(tmp_path, monkeypatch):
    """@prd T-060.2"""
    K0(tmp_path, monkeypatch)
    KR1(tmp_path)
    left = (north(tmp_path) / "prd.md").read_bytes()
    r = run(CHANGE, *LIFT, cwd=tmp_path / "north")
    assert r.code == 1, r.stderr
    assert r.stdout == ""
    assert r.stderr == "refused: the PRD already names pack document at prd.md:22; a lift moves a PRD that names none\n"
    assert (north(tmp_path) / "prd.md").read_bytes() == left


def test_lift_refused_unknown_version(tmp_path, monkeypatch):
    """@prd T-060.3"""
    K0(tmp_path, monkeypatch)
    repo = tmp_path / "north"
    r = run(CHANGE, "pack", PRD, "leaflet", "0.2.0", "--lift", cwd=repo)
    assert r.code == 1, r.stderr
    assert r.stdout == ""
    assert r.stderr == ("refused: no pack leaflet 0.2.0 is on this machine; "
                        "prd lint --list-packs lists the packs it finds\n")
    assert status(repo) == ""


def test_lift_refused_type_not_custom(tmp_path, monkeypatch):
    """@prd T-060.4"""
    K0(tmp_path, monkeypatch)
    KT1(tmp_path)
    KC(tmp_path)
    repo = tmp_path / "north"
    r = run(CHANGE, *LIFT, cwd=repo)
    assert r.code == 1, r.stderr
    assert r.stdout == ""
    assert r.stderr == "refused: contract type routes of pack leaflet is not a custom row of section 7\n"
    assert status(repo) == ""


def test_lift_refused_glob_differs(tmp_path, monkeypatch):
    """@prd T-060.5"""
    K0(tmp_path, monkeypatch)
    KT2(tmp_path)
    KC(tmp_path)
    repo = tmp_path / "north"
    r = run(CHANGE, *LIFT, cwd=repo)
    assert r.code == 1, r.stderr
    assert r.stdout == ""
    assert r.stderr == ("refused: contract type routes: section 7 has contracts/routes*.yaml, "
                        "pack leaflet has contracts/routes.yaml\n")
    assert status(repo) == ""


def test_lift_refused_uncommitted_and_bad_version(tmp_path, monkeypatch):
    """@prd T-060.6"""
    K0(tmp_path, monkeypatch)
    committed = (north(tmp_path) / "prd.md").read_bytes()
    KD(tmp_path)
    repo = tmp_path / "north"
    r1 = run(CHANGE, *LIFT, cwd=repo)
    assert (north(tmp_path) / "prd.md").read_bytes() == committed
    r2 = run(CHANGE, "pack", PRD, "leaflet", "0.1", "--lift", cwd=repo)
    assert (north(tmp_path) / "prd.md").read_bytes() == committed
    assert r1.code == 1, r1.stderr
    assert r1.stdout == ""
    assert r1.stderr == "refused: docs/prd/north has uncommitted changes; commit or set them aside first\n"
    assert r2.code == 2, r2.stderr
    assert r2.stdout == ""
    assert r2.stderr == "pack: 0.1 is not a version X.Y.Z\n"


def test_version_move_without_lift(tmp_path, monkeypatch):
    """@prd T-060.7"""
    K0(tmp_path, monkeypatch)
    repo = tmp_path / "north"
    r1 = run(CHANGE, "pack", PRD, "leaflet", "0.1.0", cwd=repo)
    KH(tmp_path)
    r2 = run(CHANGE, "pack", PRD, "leaflet", "0.2.0", cwd=repo)
    assert r1.code == 1, r1.stderr
    assert r1.stdout == ""
    assert r1.stderr == "refused: no Pack: or Target: pack line names leaflet\n"
    assert r2.code == 1, r2.stderr
    assert r2.stdout == ""
    assert r2.stderr == (f"refused: pack leaflet 0.2.0 (leaflet-kit@example) not found; "
                         f"looked in: {tmp_path}/plug/prd-packs/leaflet/ (holds 0.1.0)\n")


def test_lift_changes_nothing_a_prd_produces(tmp_path, monkeypatch):
    """@prd T-060.8"""
    K0(tmp_path, monkeypatch)
    repo = tmp_path / "north"
    context = (CONTEXT, PRD, "--area", "site", "--for", "implement")
    r1 = run(LINT, PRD, cwd=repo)
    r2 = run(*context, cwd=repo)
    r3 = run(CHANGE, *LIFT, cwd=repo)
    lift_diff = diff(repo, PRD)
    r4 = run(LINT, PRD, cwd=repo)
    r5 = run(*context, cwd=repo)
    for i, r in enumerate((r1, r2, r3, r4, r5), 1):
        assert r.code == 0, f"run_{i}: {r.stdout}{r.stderr}"

    # run_4's stdout and stderr equal run_1's, byte for byte.
    assert r4.stdout == r1.stdout
    assert r4.stderr == r1.stderr

    # After run_3, the diff changes prd.md alone, with exactly these removed and added lines.
    removed, added, files = hunk_lines(lift_diff)
    assert files == ["diff --git a/docs/prd/north/prd.md b/docs/prd/north/prd.md"], lift_diff
    assert removed == ["version: 1.0.0", "updated: 2026-11-01", PAGES_ROW, ROUTES_ROW], lift_diff
    want_added = ["version: 1.0.1", "updated: <today>", PACK_LINE, PAGES_PACK, ROUTES_PACK, ROW]
    assert untoday(added, want_added, r3.dates) == want_added, lift_diff
    fixture = sites()
    for rel in ("testing.md", "test-cases/site.yaml"):
        assert read(north(tmp_path) / rel) == fixture[f"north/docs/prd/north/{rel}"], rel
    prd_lines = read(north(tmp_path) / "prd.md").splitlines()
    assert "| `site/**/*.html` | `python3 tools/check_html.py` | `tools/check_html.py` | every page | enforced |" in prd_lines
    assert "| a change to a page | code-review | recommended |" in prd_lines

    # run_5's stdout lines are run_2's with these changes and no other.
    want = list(r2.lines)
    assert want and want[0] == "## Header", r2.stdout
    header_end = next(i for i in range(1, len(want)) if want[i].startswith("## "))
    for old, new in (
        ("PRD: docs/prd/north version 1.0.0 mode implement", "PRD: docs/prd/north version 1.0.1 mode implement"),
        ("Target: pack service (default), output language en",
         "Target: pack leaflet 0.1.0 (leaflet-kit@example), output language en"),
        ("pack 2,269 bytes (~0.6k tokens, bytes / 4); prd.md 2,645; features/site.md 867",
         "pack 2,387 bytes (~0.6k tokens, bytes / 4); prd.md 2,556; features/site.md 867"),
    ):
        header = want[:header_end]
        assert header.count(old) == 1, f"run_2's Header part holds {header.count(old)} of {old!r}:\n{r2.stdout}"
        want[header.index(old)] = new
    assert want.count("## Stack") == 1, r2.stdout
    stack = want.index("## Stack")
    stack_end = next((i for i in range(stack + 1, len(want)) if want[i].startswith("## ")), len(want))
    in_stack = want[stack:stack_end]
    assert in_stack.count(FIXTURES_LINE) == 1, r2.stdout
    want.insert(stack + in_stack.index(FIXTURES_LINE) + 1, PACK_LINE)
    assert want.count("## Cited") == 1, r2.stdout
    cited = want.index("## Cited")
    assert want[cited - 1] == "", r2.stdout
    assert [line for line in want[:cited] if line.startswith("## ")][-1] == "## Levels", r2.stdout
    want[cited:cited] = ["## Harness defaults", "", "- **Database access.** Not applicable: no database.", ""]
    assert r5.lines == want


def test_lift_refused_two_sources(tmp_path, monkeypatch):
    """@prd T-060.9"""
    K0(tmp_path, monkeypatch)
    KP7(tmp_path)
    repo = tmp_path / "north"
    r = run(CHANGE, *LIFT, cwd=repo)
    assert r.code == 1, r.stderr
    assert r.stdout == ""
    assert r.stderr == ("refused: pack leaflet 0.1.0 comes from more than one source: "
                        "leaflet-kit@example, leaflet-copy@example; name one with --source <source>\n")
    assert status(repo) == ""


def test_lift_with_source(tmp_path, monkeypatch):
    """@prd T-060.10"""
    K0(tmp_path, monkeypatch)
    KP7(tmp_path)
    repo = tmp_path / "north"
    r1 = run(CHANGE, "pack", PRD, "leaflet", "0.1.0", "--source", "leaflet-copy@example", cwd=repo)
    r2 = run(CHANGE, *LIFT, "--source", "nobody@example", cwd=repo)
    after_2 = status(repo)
    r3 = run(CHANGE, *LIFT, "--source", "leaflet-copy@example", cwd=repo)
    assert r1.code == 2, r1.stderr
    assert r1.stdout == ""
    assert r1.stderr == "pack: --source belongs to --lift\n"
    assert r2.code == 1, r2.stderr
    assert r2.stdout == ""
    assert r2.stderr == ("refused: no pack leaflet 0.1.0 (nobody@example) is on this machine; "
                         "prd lint --list-packs lists the packs it finds\n")
    assert after_2 == ""
    assert r3.code == 0, r3.stderr
    assert r3.stderr == ""
    out = ["1.0.1", ROW]
    assert untoday(r3.lines, out, r3.dates) == out
    assert read(north(tmp_path) / "prd.md").splitlines()[21] == "- Pack: leaflet 0.1.0 (leaflet-copy@example)"
    assert status(repo).splitlines() == PORCELAIN_PRD


def test_lift_section_1_without_bullets(tmp_path, monkeypatch):
    """@prd T-060.11"""
    K0(tmp_path, monkeypatch)
    KB(tmp_path)
    repo = tmp_path / "north"
    r = run(CHANGE, *LIFT, cwd=repo)
    assert r.code == 0, r.stderr
    assert r.stderr == ""
    out = ["1.0.1", ROW]
    assert untoday(r.lines, out, r.dates) == out
    lines = read(north(tmp_path) / "prd.md").splitlines()
    assert lines[10:15] == ["## 1. Metadata & stack", PACK_LINE, "", "", "## 2. Summary & goals"]
    assert status(repo).splitlines() == PORCELAIN_PRD


def test_lift_moves_lint_findings_down_one_line(tmp_path, monkeypatch):
    """@prd T-060.12"""
    K0(tmp_path, monkeypatch)
    KA(tmp_path)
    repo = tmp_path / "north"
    r1 = run(LINT, PRD, cwd=repo)
    r2 = run(CHANGE, *LIFT, cwd=repo)
    r3 = run(LINT, PRD, cwd=repo)
    assert r1.code == 1, r1.stderr
    assert r1.stderr == ""
    assert r1.lines == ["docs/prd/north/prd.md:40: assumption-indexed: A-99 has no row in section 12"]
    assert r2.code == 0, r2.stderr
    assert r2.stderr == ""
    assert r3.code == 1, r3.stderr
    assert r3.stderr == ""
    assert r3.lines == ["docs/prd/north/prd.md:41: assumption-indexed: A-99 has no row in section 12"]


def test_lift_refused_pack_without_contract_types(tmp_path, monkeypatch):
    """@prd T-060.14"""
    K0(tmp_path, monkeypatch)
    KE(tmp_path)
    repo = tmp_path / "north"
    r = run(CHANGE, *LIFT, cwd=repo)
    assert r.code == 1, r.stderr
    assert r.stdout == ""
    assert r.stderr == ("refused: pack leaflet 0.1.0 declares no contract type; "
                        "a lift moves a PRD onto a pack that declares its custom types\n")
    assert status(repo) == ""


def test_lift_brings_the_pack_vocabulary_into_lint(tmp_path, monkeypatch):
    """@prd T-060.15"""
    K0(tmp_path, monkeypatch)
    KX(tmp_path)
    repo = tmp_path / "north"
    r1 = run(LINT, PRD, cwd=repo)
    r2 = run(CHANGE, *LIFT, cwd=repo)
    r3 = run(LINT, PRD, cwd=repo)
    for i, r in enumerate((r1, r2, r3), 1):
        assert r.code == 0, f"run_{i}: {r.stdout}{r.stderr}"
        assert r.stderr == "", f"run_{i}: {r.stderr}"
    assert r1.stdout == ""
    hint = "a word of pack leaflet: move it to a contract, a Harness slot or the area's Target"
    assert r3.stdout == (
        f"docs/prd/north/features/site.md:6: warn: platform-word: AC-001.1 names 'visitor', {hint}\n"
        f"docs/prd/north/features/site.md:7: warn: platform-word: AC-001.2 names 'visitor', {hint}\n"
        f"docs/prd/north/features/site.md:14: warn: platform-word: AC-002.1 names 'visitor', {hint}\n"
        f"docs/prd/north/features/site.md:21: warn: platform-word: AC-003.1 names 'visitor', {hint}\n"
    )
