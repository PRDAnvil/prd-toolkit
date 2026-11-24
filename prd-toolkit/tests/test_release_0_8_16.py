"""Pins for the 0.8.16 release, a change set stopped before its first approval: the version, the Change sets section,
the coordinating-prds text, and the changelog entry."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
CHANGE_SET = (ROOT / "skills/coordinating-prds/running-a-change-set.md").read_text(encoding="utf-8")


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
    assert plugin["version"] == "0.8.16"
    d = plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.16", d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.16"
    assert "Version 0.8.16." in flat(README[:README.index("\n## ")])


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12


def test_readme_a_stop_before_the_approval():
    s = flat(section("Change sets"))
    for needle in ("A blocker in step 2", "with `changeset stop`, before any approval",
                   "(`changeset approve`, no `--amendment`)", "No State can be set while the record has no `Approval:` line"):
        assert needle in s, needle


def test_the_skill_clears_a_stop_with_the_one_approval():
    s = flat(CHANGE_SET)
    for needle in ("`stopped: <prd>: <reason>` with no `Approval:` line", "`stopped: <prd>: <reason>` with an `Approval:` line: step 5",
                   "A blocker in a member's step 2", "step 3's one approval clears the stop",
                   "no `--amendment` is ever used for it", "never by an `--amendment`, which needs an approval to amend"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.16", "0.8.15")
    for needle in ("`changeset stop`", "`changeset approve`", "`<prd> stop cleared by the first approval`", "(E-081)",
                   "(E-082)", "`coordinating-prds`", "Runner setup", "(E-073)", "FR-264, E-074", "`--ci-run",
                   "(E-075)", "(E-043)", "(E-044)", "(E-045)", "E-046 to E-048, E-050", "10.4.0",
                   "The lint rule count stays 41", "**Upgrade:**", "from the 0.8.16 plugin", "commit `.prd-toolkit/`",
                   "A PRD needs no change", "**Evals:**", "`change-set-stopped-before-approval`", "evals/BASELINE.md"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e
