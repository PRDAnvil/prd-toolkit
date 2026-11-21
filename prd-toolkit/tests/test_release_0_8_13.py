"""Pins for the 0.8.13 release, the fixes: the version, the README lines for what the fixes changed, the changelog
entry, the earlier entries' open lines, and the priority plan's rows."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
FIXED = ("E-019", "E-020", "E-021", "E-022", "E-023", "E-024", "E-028", "E-030", "E-031")


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
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])  # the current release is pinned in the newest test_release_*.py
    d = plugin["description"]
    assert "a pack written from two adopted PRDs" in d and "/prd-toolkit:prd-pack" in d and "a 41-rule linter" in d
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    assert f"Version {plugin['version']}." in README


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) >= 11 and len(commands) >= 12  # the current counts are pinned in the newest test_release_*.py
    table = section("Commands and skills")
    for name in commands:
        assert f"`/prd-toolkit:{name}" in table, name


def test_readme_says_what_the_fixes_changed():
    launcher = flat(section("The prd command"))
    for needle in ('`uv python find --system ">=3.11"`', "runs on the path it prints", "`.venv`", "as before",
                   "0.8.13"):
        assert needle in launcher, needle
    hooks = flat(section("Hooks and CI"))
    for needle in ("Where `core.hooksPath` is set", "the toolkit's own", "`# prd-toolkit hook`", "0.8.13"):
        assert needle in hooks, needle
    inbox = flat(section("Decision inbox"))
    for needle in ("One card for an error entry (0.8.13)", "`error-class:E-nnn`", "the first worktree",
                   "the same title and the same `Detected:` value", "`prd gates list`"):
        assert needle in inbox, needle
    pack = flat(section("Writing a pack"))
    for needle in ("the pack declares at least one contract type",
                   "`pack <name> <X.Y.Z> declares no contract type; a lift moves a PRD onto a pack that declares its custom types`",
                   "`platform-word` finding", "`vocabulary`"):
        assert needle in pack, needle


def test_changelog_entry():
    e = entry("0.8.13", "0.8.12")
    for needle in FIXED + (
            "E-029", "not a defect", "no new command, skill or lint rule",
            '`uv python find --system ">=3.11"`', "`core.hooksPath`", "`error-class`", "`Area notes`", "--lift",
            "`prd_help: <path>: cannot read: <message>`", "second full stop", "a test root", "`review-edits-nothing`",
            "8.3.1", "8.0.0", "`launcher`", "`hook-shims`", "`inbox-cards`", "`context-notes`", "`eval-scaffolds`",
            "`tester-paths`", "FR-069", "FR-074", "The lint rule count stays 41", "0.8.14",
            "**Upgrade:**", "hooks install docs/prd/<slug>", "`parts`", "`interface` stays 1",
            "**Known limits:**", "E-017", "E-032", "`prd gates list --worktrees`",
            "**Evals:**", "evals/BASELINE.md"):
        assert needle in e, needle
    assert "/Users/" not in e


def test_earlier_entries_say_what_0_8_13_fixed():
    for version, before, ids in (("0.8.12", "0.8.11", ("E-028", "E-030", "E-019 to E-024")),
                                 ("0.8.11", "0.8.10", ("E-022", "E-023", "E-024")),
                                 ("0.8.10", "0.8.9", ("E-021",)),
                                 ("0.8.9", "0.8.8", ("E-020",))):
        e = entry(version, before)
        assert "fixed in 0.8.13" in e or "0.8.13 fixes" in e, version
        for i in ids:
            assert i in e, (version, i)


def test_the_baseline_has_the_0_8_13_section():
    base = (ROOT / "evals/BASELINE.md").read_text(encoding="utf-8")
    heads = re.findall(r"(?m)^## (.+)$", base)
    at = next(i for i, h in enumerate(heads) if h.startswith("0.8.13:"))  # a later release's section comes first
    assert heads[at + 1].startswith("0.8.12:")
    s = flat(base[base.index("\n## 0.8.13:"):base.index("\n## 0.8.12:")])
    for case in ("deploy-by-hand-records", "deploy-close-live", "deploy-close-staging-only",
                 "deploy-failure-no-improvise", "deploy-stops-at-human", "deploying-trigger", "review-edits-nothing",
                 "changing-refuses-retarget"):
        assert f"`{case}`" in s, case
    assert "E-019" in s and "/Users/" not in s


def test_the_priority_plan_has_the_fixes_and_moves_conversion():
    plan = (REPO / "docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md").read_text(encoding="utf-8")
    rows = plan.splitlines()
    fixes = next(l for l in rows if l.startswith("| 7 | **0.8.13** |"))
    assert "delivered" in fixes and "| done |" in fixes and "Conversion" not in fixes
    # 0.8.14 became the errors release and conversion went to the backlog (owner, 2026-11-19; the 0.8.14 spec)
    conversion = next(l for l in rows if "**Conversion:**" in l)
    assert conversion.startswith("| — | backlog |") or conversion.startswith("| 8 | **0.8.14** |")
    assert not [l for l in rows if l.startswith("|") and "after 0.8.13" in l]
    assert "conversion moves to 0.8.14" in plan
