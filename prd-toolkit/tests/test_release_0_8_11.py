"""Pins for the 0.8.11 release: the version, the README's Practices section and the changelog entry."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def flat(s: str) -> str:
    return " ".join(s.split())


def test_versions():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])  # the current release is pinned in the newest test_release_*.py
    assert "best-practice sources" in plugin["description"] and "/prd-toolkit:prd-practices" in plugin["description"]
    assert "a 41-rule linter" in plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], plugin["description"])]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    assert f"Version {plugin['version']}." in README


def test_readme_counts_what_the_plugin_holds():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) >= 11 and "sourcing-practices" in skills  # the current count is pinned in the newest test_release_*.py
    assert len(commands) >= 12 and "prd-practices" in commands
    a = README.index("\n## Commands and skills\n")
    table = README[a:README.index("\n## ", a + 1)]
    assert "| `/prd-toolkit:prd-practices [<PRD folder>] [<what to source>]` | `prd-toolkit:sourcing-practices` |" in table
    for name in commands:
        assert f"`/prd-toolkit:{name}" in table, name


def test_readme_has_the_practices_section():
    heads = re.findall(r"(?m)^## (.+)$", README)
    assert heads.index("Practices") == heads.index("Status") + 1
    a = README.index("\n## Practices\n")
    s = flat(README[a:README.index("\n## ", a + 1)])
    for needle in ("practices.md", "`S-nn`", "`P-nn`", "approved", "declined", "proposed", ".prd-toolkit/prd practices docs/prd/<slug>",
                   "--paths", "--json", '{"interface": 1, "kind": "practices", "sources": [', "/prd-toolkit:prd-practices",
                   "`practices`", "`P-nn: followed`", "`P-nn: not followed (<why>)`", "sources", "before 0.8.11"):
        assert needle in s, needle


def test_changelog_entry():
    a = README.index("\n## Changelog\n")
    c = README[a:README.index("\n## ", a + 1)]
    e = flat(c[c.index("- **0.8.11:**"):c.index("- **0.8.10:**")])
    for needle in ("practices.md", "prd practices", "/prd-toolkit:prd-practices", "41", "7.0.0", "**Upgrade:**",
                   "hooks install docs/prd/<slug>", "**Known limits:**", "E-022", "**Evals and proof:**"):
        assert needle in e, needle


def test_the_priority_plan_marks_it_delivered():
    plan = (REPO / "docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md").read_text(encoding="utf-8")
    row = next(l for l in plan.splitlines() if l.startswith("| 5 | **0.8.11** |"))
    assert "| done |" in row
