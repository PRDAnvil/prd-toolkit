"""Pins for the 0.8.19 release, the technical view refined: the version, the Technical view section and the
changelog entry."""
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
    assert plugin["version"] == "0.8.19"
    d = plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.19", d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.19"
    assert "Version 0.8.19." in flat(README[:README.index("\n## ")])


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12


def test_technical_view_section():
    s = flat(section("Technical view"))
    for needle in ("with assumption markers left out", "joined by commas", "only when every ref holds",
                   "leaving out the test roots", "`prd hooks ci` generates"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.19", "0.8.18")
    for needle in ("`[ASSUMPTION …]`", "(AC-265.2)", "joined by `, `", "(AC-266.3)", "`tests/` when it names none",
                   "`.github/workflows/prd-toolkit.yml`", "(AC-266.4)", "13.0.0", "FR-265 and FR-266 are verified",
                   "The lint rule count stays 41", "**Upgrade:**", "from the 0.8.19 plugin", "commit `.prd-toolkit/`",
                   "A PRD needs no change"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e
