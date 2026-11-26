"""Black-box tests of the release area's manifests (test-cases/release.yaml)."""

import re

from release_support import REPO, command_stems, entry, market, plugin


def test_marketplace_manifest_shape():
    """@prd T-268.1"""
    m = market()
    assert set(m.keys()) == {"name", "owner", "description", "plugins"}
    assert len(m.keys()) == 4
    assert m["name"] == "prdanvil"
    assert m["owner"]["name"] == "PRDAnvil"
    assert m["owner"]["url"] == "https://github.com/PRDAnvil"
    assert len(m["plugins"]) == 1
    e = m["plugins"][0]
    assert set(e.keys()) == {"name", "source", "version", "description"}
    assert len(e.keys()) == 4
    assert e["name"] == "prd-toolkit"
    assert e["source"] == "./prd-toolkit"


def test_marketplace_description():
    """@prd T-268.2"""
    assert market()["description"] == (
        "prd-toolkit: a living PRD as the single authority Claude Code agents build, test and deploy from"
    )


def test_plugin_manifest_shape():
    """@prd T-269.1"""
    p = plugin()
    assert set(p.keys()) == {"name", "version", "description", "author", "homepage", "license", "skills", "commands"}
    assert len(p.keys()) == 8
    assert p["name"] == "prd-toolkit"
    assert p["author"]["name"] == "Ivan Histand"
    assert p["author"]["url"] == "https://github.com/PRDAnvil"
    assert p["homepage"] == "https://github.com/PRDAnvil/prd-toolkit/tree/main/prd-toolkit"
    assert p["license"] == "MIT"
    assert p["skills"] == "./skills"
    assert p["commands"] == "./commands"


def test_plugin_manifest_names_entry_and_folders():
    """@prd T-269.2"""
    p = plugin()
    assert p["name"] == entry()["name"]
    assert (REPO / "prd-toolkit" / p["skills"]).is_dir()
    assert (REPO / "prd-toolkit" / p["commands"]).is_dir()


def test_versions_agree():
    """@prd T-270.1"""
    p = plugin()
    assert p["version"] == entry()["version"]
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", p["version"]) is not None


def test_descriptions_agree():
    """@prd T-271.1"""
    assert entry()["description"] == plugin()["description"]


def test_plugin_description_names_every_command():
    """@prd T-271.2"""
    # set(re.findall(r"/prd-toolkit:([a-z-]+)", PLUGIN["description"])): each name the
    # longest run of a-z and - after the colon (AC-271.2).
    named = set(re.findall(r"/prd-toolkit:([a-z-]+)", plugin()["description"]))
    # The set of stems of <repo>/prd-toolkit/commands/*.md, the glob matched as the shell
    # matches it, only regular files counting (testing.md, the release cases' paragraph).
    stems = command_stems()
    assert named == stems, (
        f"only in the description: {sorted(named - stems)}; only in commands/: {sorted(stems - named)}"
    )
