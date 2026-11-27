"""FR-282: prd-status and prd-context share one Which script paragraph (test-cases/commands.yaml)."""
from __future__ import annotations

from commands_support import flat, missing, para, which_script_paragraphs

FILES = ["prd-status", "prd-context"]


def _check_holds(holds: list[str]) -> None:
    problems = []
    for name in FILES:
        for m in missing(flat(para(name)), holds):
            problems.append(f"{name}: flat(PARA) lacks {m!r}")
    assert not problems, "\n".join(problems)


def test_which_script_paragraph_is_one_and_identical():
    """@prd T-282.1"""
    counts = {name: len(which_script_paragraphs(name)) for name in FILES}
    assert counts == {"prd-status": 1, "prd-context": 1}
    assert para("prd-status") == para("prd-context")


def test_which_script_paragraph_names_scripts_directory():
    """@prd T-282.2"""
    _check_holds([
        "`${CLAUDE_PLUGIN_ROOT}` is empty inside a Bash call, so no command holds it.",
        "`<scripts>` is `.prd-toolkit` when the repository has a `.prd-toolkit/` directory: that is the copy its hooks and CI run.",
        "Otherwise `<scripts>` is the plugin's `scripts` directory, written as a literal absolute path (in double quotes if it holds a space): the plugin root is two directories above the skill's base directory",
        "load `prd-toolkit:changing-prds`, which is loaded only to read its base directory: none of its steps are followed",
        "Glob for `.prd-toolkit/prd*` once to decide",
        "use the same `<scripts>` for every command.",
        "A script that is not found is a tool error: report it, never guess another path.",
    ])


def test_which_script_paragraph_stops_before_0_6():
    """@prd T-282.3"""
    _check_holds([
        "When `.prd-toolkit/` exists but holds no `prd_error.py`, the vendored copy predates 0.6: stop, and tell the user to run `prd_hooks.py install docs/prd/<slug>` from the plugin (the README's form) and commit `.prd-toolkit/`.",
    ])


def test_which_script_paragraph_stops_before_0_8_8():
    """@prd T-282.4"""
    _check_holds([
        "When `.prd-toolkit/` exists but holds no `prd`, the vendored copy predates 0.8.8: stop, and tell the user the same and, when `.github/workflows/prd-toolkit.yml` or `.gitlab/prd-toolkit.yml` exists, also to run `prd_hooks.py ci --<forge> --force docs/prd/<slug>` from the plugin and commit both together.",
    ])
