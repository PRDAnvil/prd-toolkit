"""Pins for the 0.8.15 release, an error class settled on a run: the version, the README sections for the
explanation, the sixth class, `reopen` and the card's question answer, and the changelog entry."""
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
    assert "a class settled on a run and taken back when a run shows it wrong" in d and "a 41-rule linter" in d
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        (plugin["version"], d)]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == plugin["version"]
    intro = flat(README[:README.index("\n## ")])
    assert f"Version {plugin['version']}." in intro and "`prd error reopen`" in intro


def test_the_plugin_holds_what_it_held():
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    assert len(skills) == 11 and len(commands) == 12


def test_readme_the_loop_rests_on_a_run():
    s = flat(section("Handling errors"))
    for needle in ("A code reading is not a reproduction", "`propose --class unclassified`",
                   "or since 0.8.15 `not a defect`", "with `--explanation`",
                   "A reply that doubts or asks is not a confirmation",
                   '[--explanation "<plain words>"]',
                   '.prd-toolkit/prd error reopen docs/prd/<slug> E-nnn --reason "<why>"'):
        assert needle in s, needle


def test_readme_a_class_settled_on_a_run():
    s = flat(section("Handling errors"))
    for needle in ("**A class settled on a run (0.8.15).**",
                   "`Reopened: 2026-11-23, \"the reply was unsure\"; was Confirmed: 2026-11-22, \"I guess, sure?\"`",
                   "`E-001 proposed code bug`", "`refused: E-001 is not confirmed`", "`refused: E-001 is resolved`",
                   "`prd_error: the reason is empty`", "`Reopened: changed`", "`Reopened: added without its Confirmed:`",
                   "`E-001: Reopened: must be '<YYYY-MM-DD>, \"<reason>\"; was Confirmed: <YYYY-MM-DD>, \"<reply>\"'`",
                   "environment, standard, not a defect, unclassified", "`resolve --not-a-defect`",
                   "prints `E-nnn unclassified` and opens no `error-class` gate",
                   "never resolved by a commit made without it",
                   "since 0.8.15 they skip `Reopened:` lines too"):
        assert needle in s, needle


def test_readme_the_question_on_an_error_card():
    s = flat(section("Decision inbox"))
    for needle in ("**A question on an error card (0.8.15).**", "Ask a question", "`choice` `question`",
                   "writes nothing to `errors.md` and commits nothing",
                   "`prd gates answer <prd_dir> error-class:E-nnn --choice question --reply '<words>'`",
                   "`recorded a question for error-class:E-nnn`", "behind a disclosure"):
        assert needle in s, needle


def test_changelog_entry():
    e = entry("0.8.15", "0.8.14")
    for needle in ("`prd error reopen`", "`--explanation`", "`--class unclassified`", "`not a defect`",
                   "Ask a question", "`prd gates wait`", "`Reopened:`", "10.0.0", "`error-reopen`",
                   "FR-251", "FR-253", "FR-254", "AC-026.2", "AC-145.1", "AC-146.4", "AC-067.3",
                   "The lint rule count stays 41", "`adopting-prds`",
                   "**Upgrade:**", "hooks install docs/prd/<slug>", "from the 0.8.15 plugin", "commit `.prd-toolkit/`",
                   "The generated CI file is unchanged", "a PRD needs no change",
                   "**Evals:**", "`error-reproduce-before-propose`", "`error-unsure-reply-not-confirmed`",
                   "`error-reverify-before-fix`", "evals/BASELINE.md"):
        assert needle in e, needle
    assert "/Users/" not in e and "/private/" not in e and "docs/superpowers" not in e
