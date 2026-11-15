"""Pins for the 0.8.9 release: the version, the README's Help section and the changelog entry."""
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
    assert "a help catalogue" in plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], plugin["description"])]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    assert f"Version {plugin['version']}." in README


def test_readme_has_the_help_section():
    heads = re.findall(r"(?m)^## (.+)$", README)
    assert heads.index("The prd command") < heads.index("Help") == heads.index("Lint CLI") + 1
    a = README.index("\n## Help\n")
    s = flat(README[a:README.index("\n## ", a + 1)])
    for needle in (".prd-toolkit/prd help", "--key block.ac", "--rule ac-ears", "--json", "--interface",
                   '{"interface": 1, "kind": "help", "entries": [', '"rules": {', '"error"', "PRD_HELP_FILE",
                   "before 0.8.9", "exit 2"):
        assert needle in s, needle


def test_the_help_section_counts_what_the_catalogue_holds():
    import subprocess
    import sys
    import yaml
    rules = subprocess.run([sys.executable, str(ROOT / "scripts/prd_lint.py"), "--list-rules"],
                           capture_output=True, text=True, check=True).stdout.splitlines()
    a = README.index("\n## Help\n")
    s = flat(README[a:README.index("\n## ", a + 1)])
    entries = yaml.safe_load((ROOT / "references/help.yaml").read_text(encoding="utf-8"))
    assert f"{len(entries)} entries" in s
    assert f"{len(rules)} lint rules" in s


def test_changelog_entry():
    a = README.index("\n## Changelog\n")
    c = README[a:README.index("\n## ", a + 1)]
    e = flat(c[c.index("- **0.8.9:**"):c.index("- **0.8.8:**")])
    for needle in ("prd help", "--json", "--key", "--rule", "PRD_HELP_FILE", "6.3.0", "**Upgrade:**",
                   "hooks install docs/prd/<slug>", "**Evals:**", "not rerun"):
        assert needle in e, needle


def test_the_priority_plan_marks_it_delivered():
    plan = (REPO / "docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md").read_text(encoding="utf-8")
    row = next(l for l in plan.splitlines() if l.startswith("| 3 | **0.8.9** |"))
    assert "| done |" in row
