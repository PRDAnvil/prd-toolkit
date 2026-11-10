"""Pins for the 0.8.6 release: the toolkit published from PRDAnvil/prd-toolkit, its marketplace, its license and its upgrade note."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPO = ROOT.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
HOMEPAGE = "https://github.com/PRDAnvil/prd-toolkit/tree/main/prd-toolkit"
ADD = "/plugin marketplace add PRDAnvil/prd-toolkit"
INSTALL = "/plugin install prd-toolkit@prdanvil"
OLD = ("prd-toolkit@ihistand", "cache/ihistand", "ihistand/claude-plugins")


def flat(s: str) -> str:
    return " ".join(s.split())


def section(text: str, title: str) -> str:
    assert text.count(f"\n## {title}\n") == 1, title
    a = text.index(f"\n## {title}\n") + 1
    b = text.find("\n## ", a + 1)
    return text[a:b if b > 0 else len(text)]


def entry(ver: str, nxt: str) -> str:
    c = section(README, "Changelog")
    return c[c.index(f"- **{ver}:**"):c.index(f"- **{nxt}:**")]


def test_versions():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert plugin["version"] == "0.8.6"
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [p["version"] for p in market["plugins"] if p["name"] == "prd-toolkit"] == ["0.8.6"]
    assert (REPO / ".prd-toolkit/VERSION").read_text().strip() == "0.8.6"
    assert "Version 0.8.6." in README


def test_marketplace():
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert market["name"] == "prdanvil"
    assert market["owner"]["url"] == "https://github.com/PRDAnvil"
    assert [(p["name"], p["source"]) for p in market["plugins"]] == [("prd-toolkit", "./prd-toolkit")]
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert plugin["license"] == "MIT"
    assert plugin["homepage"] == HOMEPAGE
    assert plugin["author"]["email"] == "ivan@badgeretl.com"


def test_license():
    texts = [(REPO / p).read_bytes() for p in ("LICENSE", "prd-toolkit/LICENSE", ".prd-toolkit/LICENSE")]
    assert texts[0] == texts[1] == texts[2]
    assert texts[0].startswith(b"MIT License\n")


def test_install_lines():
    blocks = re.findall(r"```\n(.*?)```", README, re.S)
    assert any(ADD in b and INSTALL in b for b in blocks)


def test_upgrade_note():
    e = flat(entry("0.8.6", "0.8.5"))
    for needle in ("claude plugin uninstall prd-toolkit@ihistand", ADD, INSTALL, "/reload-plugins"):
        assert needle in e, needle


def test_no_old_marketplace_names():
    hits = []
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT).as_posix()
        if not f.is_file() or rel == "README.md" or rel.startswith("tests/") or "__pycache__" in f.parts or ".uv-test-cache" in f.parts:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        hits += [f"{rel}: {o}" for o in OLD if o in text]
    assert hits == []
    c = section(README, "Changelog")
    outside = README.replace(c, "")
    assert [o for o in OLD if o in outside] == []
