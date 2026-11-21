"""Pins for the 0.8.14 release, the replay and the red run: the version, the README sections for the replay, the
fourth resolution form and the `One test` column, the changelog entry, the 0.8.13 entry's open lines, and the
priority plan's row."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def flat(s: str) -> str:
    return " ".join(s.split())


def section(title: str) -> str:
    a = README.index(f"\n## {title}\n")
    return README[a:README.index("\n## ", a + 1)]


def entry(version: str, before: str) -> str:
    c = section("Changelog")
    return flat(c[c.index(f"- **{version}:**"):c.index(f"- **{before}:**")])


def test_versions():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert plugin["version"] == "0.8.14"
    d = plugin["description"]
    assert "a replay that proves a fix turned its test green" in d and "a 41-rule linter" in d
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.14", d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.14"
    intro = flat(README[:README.index("\n## ")])
    assert "Version 0.8.14." in intro and "`prd error replay`" in intro
    # the release has no design link in the README: its spec stays in the repository
    assert "0.8.14" not in README[README.index("Design: "):README.index("\n## ")].split("Version")[0]


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12
    table = section("Commands and skills")
    for name in commands:
        assert f"`/prd-toolkit:{name}" in table, name


def test_the_commands_table_and_the_steps_name_the_route_for_uncovered_code():
    row = next(l for l in section("Commands and skills").splitlines() if l.startswith("| `/prd-toolkit:prd-error"))
    assert "`/prd-toolkit:prd-build --fixes E-nnn`" in row and "`prd error resolve --red-run`" in row
    assert "code no adopted area covers" in row and "`prd error replay`" in row
    s = flat(section("Handling errors"))
    assert "except code no adopted area covers" in s
    assert "`fixed in <commit>, red run <test id> [<level>]`" in s


def test_readme_the_replay():
    s = flat(section("Handling errors"))
    for needle in ("**Replay a fix (0.8.14).**",
                   ".prd-toolkit/prd error replay docs/prd/<slug> E-nnn [--timeout <seconds>] [--json]",
                   "the resolving commit", "`<sha>^`",
                   "`E-001: T-001.2 passes on 6c3a03e^; 6c3a03e did not turn it green`",
                   "`E-001: tests/unit/test_count_names.py fails on 6c1f39f^ and passes on 6c1f39f`",
                   "`skipped: E-001: resolved as not a defect`", "`skipped: E-001: unit has no One test command`",
                   "`<E-nnn>: <T-id or test id> fails on <sha>: <file or test id>`",
                   "`<E-nnn>: <T-id> is cited by no test in <resolving commit>`",
                   "`<E-nnn>: timed out after <N> s on <commit>`", "`<E-nnn>: <program> cannot start on <commit>`",
                   '{"interface": 1, "kind": "error-replay", "entry": "E-001", "outcome": "findings"',
                   '"when": "before"', "`holds`, `skipped` or `findings`",
                   "git restore --staged --worktree docs/prd/<slug>/errors.md",
                   "own git commands never write the working tree, the index or the git folder", "`git clone --shared --no-checkout`"):
        assert needle in s, needle


def test_readme_the_fourth_form():
    s = flat(section("Handling errors"))
    for needle in ("**Code no area covers: a red run (0.8.14).**",
                   ".prd-toolkit/prd error resolve docs/prd/<slug> E-nnn --commit <sha> --red-run <test id> --level <level>",
                   "`Resolution: fixed in 6c1f39f, red run tests/unit/test_count_names.py [unit]`",
                   "`refused: 3845582 changes tests/unit/test_count_names.py, which area greet covers; resolve with a regression T-id`",
                   "`refused: system is a deploy-gate level`",
                   "`refused: the test id must hold no white space and must not start with -`",
                   "`prd_error: --red-run takes --commit and --level, and no --t, --version, --run or --not-a-defect`",
                   "`refused: <level> has no One test command; add the One test column to testing.md Levels through /prd-toolkit:prd-change`",
                   "a red run resolves a code bug only", "commit the failing test alone, before the fix",
                   "`resolution is not one of the four forms`"):
        assert needle in s, needle


def test_readme_the_known_limits():
    s = flat(section("Handling errors"))
    for needle in ("An exit code cannot tell a test that failed from one that could not run",
                   "The proof is per file", "a test added to the same file between the fix and the resolve",
                   "`uv run --project <folder> pytest -q`", "SIGINT (exit 130)", "SIGTERM is not handled",
                   "leaves its folder under the system temporary folder", "press it again", "do not start a replay from inside a git hook",
                   "`GIT_INDEX_FILE`, `GIT_DIR` and `GIT_WORK_TREE`", "`resolve --red-run=`"):
        assert needle in s, needle


def test_readme_the_one_test_column():
    s = flat(section("Testing from the PRD"))
    for needle in ("**One test (0.8.14).**", "| Level | Harness command | Environment | Gate | One test |",
                   "| unit | `uv run pytest tests/unit` | local | build | `uv run pytest -q` |",
                   "`uv run --project <folder> pytest -q`", "`uv run --directory <folder> pytest -q`",
                   "testing.md:7: runbook-tests: level 'unit': One test '`cd tests && uv run pytest -q`' is not one simple command in backticks",
                   "`format: One test column (prd-toolkit 0.8.14)`", "the rule count stays 41",
                   "the tester guard allows what it allowed"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.14", "0.8.13")
    for needle in ("`prd error replay`", "`--red-run`", "`One test`", "fixed in <commit>, red run <test id> [<level>]",
                   "9.0.0", "8.5.0", "8.4.0", "`error-replay`", "UJ-07", "FR-075", "FR-081", "E-017", "E-032", "E-033", "E-035",
                   "The lint rule count stays 41",
                   "**Upgrade:**", "hooks install docs/prd/<slug>", "from the 0.8.14 plugin", "commit `.prd-toolkit/`",
                   "before a ledger holds a fourth-form line", "The generated CI file is unchanged",
                   "only if it wants the replay", "`format: One test column (prd-toolkit 0.8.14)`",
                   "**Known limits:**", "E-034", "SIGTERM", "`GIT_INDEX_FILE`",
                   "**Evals:**", "`error-uncovered-code-red-run`", "`error-replay-finding-not-committed`",
                   "`handling-errors`", "evals/BASELINE.md"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e


def test_the_0_8_13_entry_says_what_0_8_14_closed():
    e = entry("0.8.13", "0.8.12")
    assert "E-017 stays open" in e and "resolved in 0.8.14" in e
    assert "E-032 is open" in e and "fixed in 0.8.14" in e


def test_the_priority_plan_marks_it_delivered():
    plan = (REPO / "docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md").read_text(encoding="utf-8")
    row = next(l for l in plan.splitlines() if l.startswith("| 8 | **0.8.14** |"))
    assert "delivered" in row and "| done |" in row and "E-017" in row
    conversion = next(l for l in plan.splitlines() if "**Conversion:**" in l)
    assert conversion.startswith("| — | backlog |")
