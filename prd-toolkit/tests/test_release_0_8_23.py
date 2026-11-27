"""Pins for the 0.8.23 release, approve keeping the generated CI files current (E-093): the version
and the changelog entry."""
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
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    assert f"Version {plugin['version']}." in flat(README[:README.index("\n## ")])


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12


def test_changelog_entry():
    e = entry("0.8.23", "0.8.22")
    for needle in ("`prd change approve`", "`.github/workflows/prd-toolkit.yml`", "`.gitlab/prd-toolkit.yml`",
                   "`prd hooks check --ci`", "has uncommitted changes; commit or set them aside first",
                   "The lint rule count stays 41", "**Upgrade:**", "`prdlint/change_approve.py`",
                   "A PRD needs no change"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e and "~/" not in e


def test_the_approve_bullet_names_the_ci_files():
    b = flat(README[README.index("- `prd_change.py approve`"):])
    b = b[:b.index("- `prd_change.py", 5)] if "- `prd_change.py" in b[5:] else b[:800]
    assert "neither generated CI file" in b and "rewrites each generated CI file" in b
