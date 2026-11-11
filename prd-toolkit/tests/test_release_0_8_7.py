"""Pins for the 0.8.7 release: the version, the full command names in everything the plugin writes or says, and the changelog entry with its upgrade note."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
COMMANDS = ("new", "adopt", "change-set", "change", "build", "error", "deploy", "status", "context", "publish")
BARE = re.compile(r"(?<![:A-Za-z0-9_-])/prd-(" + "|".join(COMMANDS) + r")\b")
# What the plugin writes or tells a reader to type. Past records keep their words: the evals' baselines and
# prompts, the README's changelog and older Known limits, errors.md, the dated specs and plans.
CURRENT = ("skills", "commands", "agents", "templates", "scripts", "references")
# A Red Flags row quotes a baseline session in its own words, bare name included (test_coordinating_skill pins it).
QUOTED = "then run `/prd-build welcome FR-001`.\" (C1)"


def flat(s: str) -> str:
    return " ".join(s.split())


def entry(ver: str, nxt: str) -> str:
    a = README.index("\n## Changelog\n")
    c = README[a:README.index("\n## ", a + 1)]
    return c[c.index(f"- **{ver}:**"):c.index(f"- **{nxt}:**")]


def test_versions():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert plugin["version"] == "0.8.7"
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [p["version"] for p in market["plugins"] if p["name"] == "prd-toolkit"] == ["0.8.7"]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.7"
    assert "Version 0.8.7." in README


def test_no_bare_command_names_in_what_the_plugin_says():
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", *CURRENT], capture_output=True, text=True, check=True)
    hits = []
    for rel in sorted(p for p in tracked.stdout.split("\0") if p):
        f = ROOT / rel
        if f.is_file() and f.suffix in (".md", ".py", ".html", ".json", ".yaml", ".sh"):
            text = f.read_text(encoding="utf-8").replace(QUOTED, "")
            hits += [f"{rel}: {m.group(0)}" for m in BARE.finditer(text)]
    hits += [f"plugin.json: {m.group(0)}" for m in BARE.finditer((ROOT / ".claude-plugin/plugin.json").read_text())]
    assert hits == []


def test_generated_blocks_name_the_commands_in_full():
    block = (ROOT / "templates/claude-block.md").read_text(encoding="utf-8")
    for c in ("context", "build", "change", "deploy", "error"):
        assert f"`/prd-toolkit:prd-{c}" in block, c
    readme = (ROOT / "templates/readme-prd.md").read_text(encoding="utf-8")
    for c in ("status", "context", "publish", "change", "build", "error"):
        assert f"`/prd-toolkit:prd-{c}" in readme, c
    assert not BARE.search((REPO / "CLAUDE.md").read_text(encoding="utf-8"))


def test_changelog_entry_and_upgrade_note():
    e = flat(entry("0.8.7", "0.8.6"))
    for eid in ("E-009", "E-010", "E-011", "E-012", "E-013", "E-014", "E-015", "E-016", "E-017"):
        assert f"({eid})" in e, eid
    assert "The toolkit's own PRD is 6.2.2." in e
    assert "`/prd-toolkit:prd-build`" in e
    for needle in ("claude plugin marketplace update prdanvil", "claude plugin update prd-toolkit@prdanvil", "/reload-plugins",
                   "prd_hooks.py install docs/prd/<slug>", "commits `.prd-toolkit/`"):
        assert needle in e, needle
