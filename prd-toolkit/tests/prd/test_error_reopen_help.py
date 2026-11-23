"""error-reopen AC-251.7 and AC-253.6: the help catalogue's entry kind.E (test-cases/error-reopen.yaml)."""
from __future__ import annotations

from error_reopen_support import assert_run, build, json_at, one_json_line


def _rules(tmp_path, monkeypatch) -> list[str]:
    """Run `python HELP --key kind.E --json` from <tmp> and return entries.0.rules, checked to be strings."""
    c = build(tmp_path, monkeypatch)
    r = c.run("python HELP --key kind.E --json")
    assert_run(r, 0, stderr="")
    doc = one_json_line(r)
    assert json_at(doc, "entries.0.key") == "kind.E", r.describe()
    rules = json_at(doc, "entries.0.rules")
    assert isinstance(rules, list) and all(isinstance(s, str) for s in rules), (
        f"entries.0.rules is not a list of strings: {rules!r}")
    return rules


def test_kind_e_names_the_reopened_line(tmp_path, monkeypatch):
    """@prd T-251.8"""
    rules = _rules(tmp_path, monkeypatch)
    line = 'Reopened: <YYYY-MM-DD>, "<reason>"; was Confirmed: <YYYY-MM-DD>, "<reply>"'
    assert any(line in s and "prd_error.py reopen" in s for s in rules), (
        "no rule of kind.E holds both texts:\n" + "\n".join(rules))


def test_kind_e_names_the_explanation_and_the_class(tmp_path, monkeypatch):
    """@prd T-253.9"""
    rules = _rules(tmp_path, monkeypatch)
    assert any("Explanation:" in s and "prd_error.py propose --explanation" in s for s in rules), (
        "no rule of kind.E holds both Explanation: and prd_error.py propose --explanation:\n" + "\n".join(rules))

    def names_the_classes(s: str) -> bool:
        i = s.find("Classification:")
        if i < 0:
            return False
        after = s[i + len("Classification:"):]
        return all(word in after for word in ("code bug", "not a defect", "unclassified"))

    assert any(names_the_classes(s) for s in rules), (
        "no rule of kind.E holds Classification: followed by code bug, not a defect and unclassified:\n"
        + "\n".join(rules))
