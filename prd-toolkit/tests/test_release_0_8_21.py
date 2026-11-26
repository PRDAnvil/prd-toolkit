"""Pins for the 0.8.21 release, the deferred minors of 0.8.20's review: the version, the README's three
memory places and the changelog entry."""
import json
import re
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
    assert plugin["version"] == "0.8.21"
    d = plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.21", d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.21"
    assert "Version 0.8.21." in flat(README[:README.index("\n## ")])


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12


def test_the_adoption_section_names_the_three_memory_places():
    s = flat(section("Adopting an existing repo"))
    for needle in ("the auto-memory directory the session's system prompt names",
                   "`~/.claude/projects/<the repository root, each non-alphanumeric as ->/memory/`",
                   "a directory you name"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.21", "0.8.20")
    for needle in ("rule 3", "`adopting-memory-unrelated`", "`adopting-memory-headless-owner`",
                   "`adopting-memory-conflict`", "Agent", "Bash", "The lint rule count stays 41", "**Upgrade:**",
                   "A PRD needs no change"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e
