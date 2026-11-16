"""The content of the help catalogue (references/help.yaml) and of the rule descriptions on the @rule registrations."""
import re
from pathlib import Path

import pytest
import yaml

from prdlint import registry
from prdlint import rules  # noqa: F401  (importing registers every rule module)

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parent
CATALOGUE = PLUGIN / "references/help.yaml"
FORMAT = PLUGIN / "references/prd-format.md"
CLI_YAML = REPO / "docs/prd/prd-toolkit/contracts/cli.yaml"

KEY = re.compile(r"[a-z]+(\.[A-Za-z_]+)+")
FORBIDDEN = ("http://", "https://", "/Users/", "/home/")
_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")


def _entries() -> list[dict]:
    data = yaml.safe_load(CATALOGUE.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _headings(text: str) -> set[str]:
    """The text of every Markdown heading outside a code fence."""
    out, fenced = set(), False
    for line in text.split("\n"):
        if _FENCE.match(line):
            fenced = not fenced
            continue
        m = None if fenced else _HEADING.match(line)
        if m:
            out.add(m.group(1))
    return out


def _texts(entry: dict) -> list[str]:
    """Every string the entry holds, list items included."""
    out = []
    for value in entry.values():
        out += value if isinstance(value, list) else [value]
    return [v for v in out if isinstance(v, str)]


ENTRIES = _entries()
IDS = [e.get("key", f"entry {n}") for n, e in enumerate(ENTRIES, 1)]


def test_every_rule_has_a_one_line_description():
    assert registry.RULES
    for name in registry.RULES:
        d = registry.DESCRIPTION.get(name)
        assert isinstance(d, str) and d.strip(), f"{name}: description {d!r}"
        assert "\n" not in d and "\r" not in d, f"{name}: description holds a line break"


def test_headings_helper_skips_fenced_text():
    """The heading reader the `see` check uses ignores a heading inside a code fence (so that check can fail)."""
    assert _headings("# A\n```\n## B\n```\n## C\n") == {"A", "C"}


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_entry_fields(entry):
    for field in ("key", "name", "what", "why"):
        assert isinstance(entry.get(field), str) and entry[field].strip(), f"{field}: {entry.get(field)!r}"
    for field in ("rules", "checked_by"):
        if field in entry:
            value = entry[field]
            assert isinstance(value, list) and value, f"{field} must be a non-empty list"
            assert all(isinstance(v, str) and v.strip() for v in value), f"{field}: {value!r}"


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_checked_by_names_registered_rules(entry):
    unknown = [r for r in entry.get("checked_by", []) if r not in registry.RULES]
    assert unknown == [], f"checked_by names no registered rule: {unknown}"


@pytest.mark.parametrize("entry", [e for e in ENTRIES if "see" in e], ids=[e["key"] for e in ENTRIES if "see" in e])
def test_see_is_a_heading_of_the_format_reference(entry):
    assert entry["see"] in _headings(FORMAT.read_text(encoding="utf-8")), f"no heading {entry['see']!r} in prd-format.md"


def test_keys_are_unique_and_well_formed():
    keys = [e.get("key") for e in ENTRIES]
    assert len(keys) == len(set(keys)), f"repeated keys: {sorted({k for k in keys if keys.count(k) > 1})}"
    bad = [k for k in keys if not (isinstance(k, str) and KEY.fullmatch(k))]
    assert bad == [], f"keys not of the form {KEY.pattern}: {bad}"


def test_no_url_or_home_path():
    texts = [(e.get("key"), t) for e in ENTRIES for t in _texts(e)]
    texts += [(name, d) for name, d in registry.DESCRIPTION.items() if name in registry.RULES]
    hits = [(where, bad) for where, text in texts for bad in FORBIDDEN if bad in text]
    assert hits == []
