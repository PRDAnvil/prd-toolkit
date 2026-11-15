"""A rule registered with no description: the registry holds "" and the help document prints it so."""
import json

import pytest

from prdlint import registry
from prdlint import rules  # noqa: F401  (registers the toolkit's own rules first)

NAME = "zz-test-no-description"


@pytest.fixture
def bare_rule():
    """Register NAME with no description; put the registry back as it was when the test ends."""
    saved = {d: dict(getattr(registry, d)) for d in ("RULES", "SEVERITY", "DESCRIPTION") if hasattr(registry, d)}
    assert NAME not in registry.RULES
    registry.rule(NAME)(lambda prd: [])
    try:
        yield NAME
    finally:
        for d, before in saved.items():
            table = getattr(registry, d)
            table.clear()
            table.update(before)
    assert NAME not in registry.RULES and NAME not in registry.SEVERITY


def test_a_rule_registered_without_a_description(bare_rule, monkeypatch, capsys):
    """@prd T-038.3"""
    import prd_help

    monkeypatch.delenv("PRD_HELP_FILE", raising=False)
    assert registry.DESCRIPTION[bare_rule] == ""
    assert prd_help.main(["--json"]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n") and out.count("\n") == 1
    assert json.loads(out)["rules"][bare_rule] == {"severity": "error", "description": ""}
