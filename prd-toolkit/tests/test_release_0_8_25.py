"""Pins for the 0.8.25 release, the README's Edit hook section and the changing-prds close on stale CI files:
the version and the changelog entry."""
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
    assert plugin["version"] == "0.8.25"
    d = plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.25", d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.25"
    assert "Version 0.8.25." in flat(README[:README.index("\n## ")])


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12


def test_the_edit_hook_section():
    s = flat(section("Edit hook"))
    for needle in ("`scripts/prd_edit_hook.py`", "never from `.prd-toolkit/`", "PostToolUse", "once per area and session",
                   "At Stop.", "at most 20 per folder", "50 seconds", "`PRD_TOOLKIT_EDIT_HOOK=off`"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.25", "0.8.24")
    for needle in ("## Edit hook", "`changing-prds`", "a new enforced standards row", "approve", "change set",
                   "The lint rule count stays 41", "**Upgrade:**", "only its `VERSION` changes", "A PRD needs no change"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e and "~/" not in e
