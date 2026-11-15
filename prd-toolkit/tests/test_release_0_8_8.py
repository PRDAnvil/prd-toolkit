"""Pins for the 0.8.8 release: what the plugin tells a reader to type runs a vendored copy through the launcher."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent


def tracked(*dirs: str) -> list[Path]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", *dirs], capture_output=True, text=True, check=True)
    return [ROOT / rel for rel in sorted(p for p in out.stdout.split("\0") if p)]


def test_no_vendored_script_is_run_by_its_file():
    hits = [f"{p}:{n}" for p in tracked("skills", "commands", "agents", "templates")
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if re.search(r"uv run --script \S*\.prd-toolkit/", line)]
    assert hits == []


def test_no_skill_line_runs_a_script_by_its_file():
    hits = [f"{p}:{n}" for p in tracked("skills", "commands", "agents", "templates")
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if re.search(r"uv run --script\s+.*?prd_\w+\.py", line)]  # a placeholder may hold a space
    assert hits == []


def test_every_scripts_command_uses_the_launcher():
    n = sum(len(re.findall(r"<scripts>/prd [a-z][a-z-]*\b", p.read_text(encoding="utf-8")))
            for p in tracked("skills", "commands", "agents"))
    assert n >= 80        # the 80 `uv run --script <scripts>/` lines counted on 94a4ba2


# one sentence: the CI step is part of the 0.8.8 stop, so an agent in a healthy repository has nothing to recite
CI_CLAUSE = ("predates 0.8.8: stop, and tell the user the same and, when `.github/workflows/prd-toolkit.yml` or "
             "`.gitlab/prd-toolkit.yml` exists, also to run `prd_hooks.py ci --<forge> --force docs/prd/<slug>` "
             "from the plugin and commit both together.")


def test_every_scripts_definition_checks_for_the_launcher():
    # install leaves a generated workflow stale (it runs `sh .prd-toolkit/prd`): the guard names the ci rerun too
    visited = []
    for p in tracked("skills", "commands"):
        text = p.read_text(encoding="utf-8")
        if "`<scripts>` is `.prd-toolkit` when" in text:
            para = " ".join(next(par for par in text.split("\n\n") if "`<scripts>` is `.prd-toolkit` when" in par).split())
            assert "When `.prd-toolkit/` exists but holds no `prd`," in para and CI_CLAUSE in para, p
            assert "the user also runs" not in para, p
            visited.append(p.relative_to(ROOT).as_posix())
    assert len(visited) == 8, visited


def test_every_launcher_command_in_a_skill_exists():
    from prd_dispatch import COMMANDS
    # `<dir>/prd <command>`: the `/prd ` path segment, so prose such as "the PRD" never counts
    found = [(p.name, c) for p in tracked("skills", "commands", "agents")
             for c in re.findall(r"/prd ([a-z][a-z-]*)", p.read_text(encoding="utf-8"))]
    assert len(found) >= 80
    assert [f for f in found if f[1] not in COMMANDS] == []


def _paragraphs(text: str) -> list[str]:
    """Blank-line paragraphs, with each list item its own paragraph."""
    return [p for p in re.split(r"\n\s*\n|\n(?=\s*(?:[-*]|\d+\.) )", text) if p.strip()]


def test_skills_say_what_to_do_without_the_launcher():
    # A copy vendored before 0.8.8 has the scripts and no launcher: the passage that sends the user to
    # `prd_hooks.py install` names the launcher itself (`.prd-toolkit/prd`, not only `prd_<x>.py`).
    for rel in ("skills/coordinating-prds/running-a-change-set.md", "skills/testing-from-prds/SKILL.md",
                "agents/prd-tester.md"):
        paras = [p for p in _paragraphs((ROOT / rel).read_text(encoding="utf-8")) if "prd_hooks.py install" in p]
        assert paras, rel
        assert any("`.prd-toolkit/prd`" in p for p in paras), rel


def test_the_launcher_is_named_where_a_vendored_copy_is_checked():
    def flat(rel: str) -> str:
        return " ".join((ROOT / rel).read_text(encoding="utf-8").split())

    # a 0.8.7 copy passes the 0.6 and 0.8.1 checks, then the close's `.prd-toolkit/prd hooks` lines find no launcher
    assert ("When `.prd-toolkit/` exists but holds no `prd`, the vendored copy predates 0.8.8: stop, and tell the user the same and,"
            in flat("skills/changing-prds/SKILL.md"))
    assert ("and so is a judged test that finds no `.prd-toolkit/prd` or `.prd-toolkit/prd_judge.py`"
            in flat("skills/handling-errors/SKILL.md"))
    rules = flat("skills/coordinating-prds/SKILL.md")
    assert "Call the starting repository's vendored launcher, `.prd-toolkit/prd links`." in rules
    assert "vendored `.prd-toolkit/prd_links.py`" not in rules


def _readme_without_past_records() -> str:
    """README.md minus the `## Changelog` and `## Known limits (...)` sections, which record past releases."""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    kept = []
    for section in re.split(r"(?m)^(?=## )", text):
        if section.startswith("## Changelog") or section.startswith("## Known limits ("):
            continue
        kept.append(section)
    return "".join(kept)


def test_readme_runs_the_vendored_copy_through_the_launcher():
    full = (ROOT / "README.md").read_text(encoding="utf-8")
    text = _readme_without_past_records()
    assert len(text) < len(full)          # the helper removed the past-record sections
    assert ".prd-toolkit/prd " in text    # and the examples are still there
    assert [l for l in text.splitlines() if re.search(r"uv run --script \S*\.prd-toolkit/", l)] == []


def test_readme_says_how_to_run_the_vendored_copy():
    text = _readme_without_past_records()
    assert ".prd-toolkit/prd <command>" in text
    assert ".prd-toolkit/<script>.py" not in text


def _entry(ver: str, nxt: str) -> str:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    a = text.index("\n## Changelog\n")
    c = text[a:text.index("\n## ", a + 1)]
    return c[c.index(f"- **{ver}:**"):c.index(f"- **{nxt}:**")]


def test_versions():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert plugin["version"] == "0.8.8"
    assert "`prd` command" in plugin["description"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["version"], p["description"]) for p in market["plugins"] if p["name"] == "prd-toolkit"] == [
        ("0.8.8", plugin["description"])]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.8"
    assert "Version 0.8.8." in (ROOT / "README.md").read_text(encoding="utf-8")


def test_changelog_has_the_upgrade_note():
    e = " ".join(_entry("0.8.8", "0.8.7").split())
    for needle in ("prd_hooks.py install docs/prd/<slug>", "ci --github --force docs/prd/<slug>", "--force",
                   ".prd-toolkit/prd hooks install docs/prd/<slug>", "core.hooksPath", "environments-v2", "6.2.3",
                   "**Known limits:**", "E-019", "**Evals and proof:**"):
        assert needle in e, needle


def test_readme_has_the_prd_command_section():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    heads = re.findall(r"(?m)^## (.+)$", text)
    assert heads.index("The prd command") == heads.index("Lint CLI") - 1
    s = text[text.index("\n## The prd command\n"):text.index("\n## Lint CLI\n")]
    for needle in ("prd --help", "prd --version", ".prd-toolkit/prd", "publish", "sh .prd-toolkit/prd"):
        assert needle in s, needle
    assert len(s.strip().splitlines()) <= 20
