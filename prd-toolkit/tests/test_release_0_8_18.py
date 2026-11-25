"""Pins for the 0.8.18 release, the technical view: the version, the Technical view section and the changelog
entry."""
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
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])  # the current release is pinned in the newest test_release_*.py
    d = plugin["description"]
    assert "a generated technical view that sets the PRD beside the code" in d
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    assert f"Version {plugin['version']}." in flat(README[:README.index("\n## ")])


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12
    assert (ROOT / "scripts/prd_trd.py").is_file() and (REPO / ".prd-toolkit/prd_trd.py").is_file()


def test_technical_view_section():
    s = flat(section("Technical view"))
    for needle in ("prd trd docs/prd/<slug>", "--out trd.md", "never part of the PRD", "the black-box tester never reads it",
                   "the same bytes", "Requirements to code", "Uncovered code", "`.prd-toolkit/`", "exit 1"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.18", "0.8.17")
    for needle in ("`prd trd <prd_dir> [--out FILE]`", "(see Technical view)", "FR-265 to FR-267", "12.0.0",
                   "(FR-098, FR-119, FR-120)", "21 commands", "The lint rule count stays 41", "**Upgrade:**",
                   "from the 0.8.18 plugin", "commit `.prd-toolkit/`", "A PRD needs no change"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e
