"""Pins for the 0.8.10 release: the version, the README's Status section and the changelog entry."""
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
    assert plugin["version"] == "0.8.10"
    assert "what a PRD needs next" in plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.10", plugin["description"])]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.10"
    assert "Version 0.8.10." in README


def test_readme_has_the_status_section():
    import yaml
    contract = yaml.safe_load((REPO / "docs/prd/prd-toolkit/contracts/cli.yaml").read_text(encoding="utf-8"))
    wanted = contract["prd_status"]["next_kinds"]
    heads = re.findall(r"(?m)^## (.+)$", README)
    assert heads.index("Status") == heads.index("Help") + 1
    a = README.index("\n## Status\n")
    s = flat(README[a:README.index("\n## ", a + 1)])
    for needle in (".prd-toolkit/prd status docs/prd/<slug>", "## Next", "run: ", "--json", '"part": "Next"', '"kind"', '"ids"',
                   '"area"', '"command"', '"waits_on"', "Broken", "Waiting on you", "Work", "selects the Header by `part`"):
        assert needle in s, needle
    kinds = [k for k in re.findall(r"`([a-z-]+)`", s) if k in set(wanted)]
    assert list(dict.fromkeys(kinds)) == wanted   # every kind, named in the contract's order


def test_changelog_entry():
    a = README.index("\n## Changelog\n")
    c = README[a:README.index("\n## ", a + 1)]
    e = flat(c[c.index("- **0.8.10:**"):c.index("- **0.8.9:**")])
    for needle in ("Next", "prd status", "--json", "no longer", "Header", "6.4.0", "**Upgrade:**",
                   "hooks install docs/prd/<slug>", "**Evals:**"):
        assert needle in e, needle


def test_the_command_says_the_report_starts_with_next():
    text = flat((ROOT / "commands/prd-status.md").read_text(encoding="utf-8"))
    assert "starts with the part Next" in text
    assert "nine parts" not in text


def test_the_priority_plan_marks_it_delivered():
    plan = (REPO / "docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md").read_text(encoding="utf-8")
    row = next(l for l in plan.splitlines() if l.startswith("| 4 | **0.8.10** |"))
    assert "| done |" in row
