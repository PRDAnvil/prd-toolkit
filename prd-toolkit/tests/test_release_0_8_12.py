"""Pins for the 0.8.12 release: the version, the README's pack-writing section, the cards' area and URL, and the
changelog entry."""
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


def test_versions():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])  # the current release is pinned in the newest test_release_*.py
    d = plugin["description"]
    assert "a pack written from two adopted PRDs" in d and "/prd-toolkit:prd-pack" in d
    assert "best-practice sources" in d and "/prd-toolkit:prd-practices" in d and "a 41-rule linter" in d
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    assert f"Version {plugin['version']}." in README
    assert "and for 0.8.12 [docs/superpowers/specs/2026-11-15-prd-toolkit-0.8.12-pack-authoring-design.md]" in README


def test_readme_counts_what_the_plugin_holds():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) >= 11 and "authoring-packs" in skills  # the current count is pinned in the newest test_release_*.py
    assert len(commands) >= 12 and "prd-pack" in commands
    table = section("Commands and skills")
    assert "| `/prd-toolkit:prd-pack <PRD folder A> <PRD folder B> [<pack name>]` | `prd-toolkit:authoring-packs` |" in table
    for name in commands:
        assert f"`/prd-toolkit:{name}" in table, name


def test_readme_has_the_pack_writing_section():
    heads = re.findall(r"(?m)^## (.+)$", README)
    assert heads.index("Writing a pack") == heads.index("Packs") + 1
    s = flat(section("Writing a pack"))
    for needle in ("/prd-toolkit:prd-pack", "`prd-toolkit:authoring-packs`",
                   "<plugin>/scripts/prd pack compare <prd A> <prd B>",
                   "<plugin>/scripts/prd pack check <pack dir> <prd A> <prd B>",
                   "prd change pack docs/prd/<slug> <name> <X.Y.Z> --lift",
                   "`both`, `A` or `B`", "Contract types", "Vocabulary",
                   "1 when the two PRDs share no custom contract type",
                   '{"interface": 1, "kind": "pack.compare", "a", "b", "parts"}',
                   '{"interface": 1, "kind": "pack.check", "findings": [{"file", "message"}]}',
                   "`pack.yaml`", "`version: 0.1.0`", "`${PACK}`", "`samples/<type>/bad.*`", "`README.md`", "to-do list",
                   "Nothing else", "no helper code", "pushes, publishes or installs nothing",
                   "validator fails from the pack folder",
                   "`pack <name> <X.Y.Z> lifted; pending`", "`no dry run (pack lifted)`", "`--source <source>`",
                   "a conversion", "before 0.8.12"):
        assert needle in s, needle


def test_readme_cards_say_where():
    inbox = flat(section("Decision inbox"))
    for needle in ("prd gates list --json", "`areas`", "`url`", "`Area: <names>`", "`Area: none`", "a new tab",
                   "`Target:`", "`url <address>`", "`URL:`", "nothing fetches", "The text listing", "before 0.8.12"):
        assert needle in inbox, needle
    errors = flat(section("Handling errors"))
    for needle in ('.prd-toolkit/prd error new docs/prd/<slug> --title "<title>" --source "<where seen>" [--url <address>]',
                   ".prd-toolkit/prd error url docs/prd/<slug> E-nnn <address>", "`URL: <address>`", "`-` removes it",
                   "`Target:`", "`url`", "http://", "https://"):
        assert needle in errors, needle


def test_changelog_entry():
    c = section("Changelog")
    e = flat(c[c.index("- **0.8.12:**"):c.index("- **0.8.11:**")])
    for needle in ("`authoring-packs`", "/prd-toolkit:prd-pack", "`prd_pack.py`", "prd pack compare", "prd pack check",
                   "--lift", "--url", "prd error url", "`URL:`", "`Target:`", "`areas`", "`url`",
                   "7.3.0", "7.1.0", "pack-authoring", "card-context", "standards-run",
                   "E-025", "E-026", "E-027",
                   "**Upgrade:**", "hooks install docs/prd/<slug>", "hooks ci --github --force docs/prd/<slug>",
                   "**Known limits:**", "E-028", "E-029", "needs judgment", "ordinary words",
                   "**Evals and proof:**", "29 cases", "26 score 1.00", "two static web sites"):
        assert needle in e, needle
    assert "/Users/" not in e


def test_the_priority_plan_marks_it_delivered():
    plan = (REPO / "docs/superpowers/plans/2026-11-14-prd-toolkit-engine-ports.md").read_text(encoding="utf-8")
    row = next(l for l in plan.splitlines() if l.startswith("| 6 | **0.8.12** |"))
    assert "delivered" in row and "| done |" in row
