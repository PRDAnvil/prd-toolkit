"""lint-registries: FR-132, FR-133 and FR-134, the section 5 and 6 registries (test-cases/lint-registries.yaml)."""
from lint_registries_support import (  # noqa: F401  (case is a pytest fixture)
    S0, assert_exit, assert_stderr, assert_stdout, assert_stdout_exact_lines,
    assert_stdout_not_contains, case, delete_line, git_init, insert_after, replace,
    require_absent, require_no_skill_under, require_not_on_path, require_outside_git,
    require_toplevel_is_tmp, steps, write_lines,
)

STD = "| `**/*.sql` | {linter} | none; stand-in command for the fixture | code, schema.sql | {decision} |"


@steps(S0, replace("prd.md", 59, STD.format(linter="`python3 -m json.tool`", decision="maybe")))
def test_standards_decision_outside_set(case):
    """@prd T-132.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/prd.md:59: registries: standards Decision 'maybe' is not one of enforced, declined, proposed"])
    assert_stderr(r, "")


@steps(S0, replace("prd.md", 65, "| plans | superpowers:writing-plans | maybe |"))
def test_skills_decision_outside_set(case):
    """@prd T-132.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/prd.md:65: registries: skills Decision 'maybe' is not one of required, recommended, declined, proposed"])
    assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 59, STD.format(linter="`python3 -m json.tool`", decision="proposed")),
       replace("prd.md", 65, "| plans | superpowers:writing-plans | proposed |"))
def test_proposed_rows_while_approved(case):
    """@prd T-132.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [
        "docs/prd/orders/prd.md:59: registries: standards row is still 'proposed' but the PRD is Approved",
        "docs/prd/orders/prd.md:65: registries: skills row is still 'proposed' but the PRD is Approved",
    ])
    assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 4, "status: Draft"),
       replace("prd.md", 59, STD.format(linter="`python3 -m json.tool`", decision="proposed")),
       replace("prd.md", 65, "| plans | superpowers:writing-plans | proposed |"))
def test_proposed_rows_while_draft(case):
    """@prd T-132.4"""
    r = case.lint()
    assert_stdout_not_contains(r, "registries:")
    assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 59, STD.format(linter="`no-such-linter-xyz`", decision="`declined`")),
       replace("prd.md", 65, "| plans | nonexistent:skill | `recommended` |"))
def test_backticked_decisions(case):
    """@prd T-132.5"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0, replace("prd.md", 59, STD.format(linter="python3 -m json.tool", decision="enforced")))
def test_enforced_linter_without_backticks(case):
    """@prd T-133.1"""
    for args in ((), ("--ci",)):
        r = case.lint(*args)
        assert_exit(r, 1)
        assert_stdout_exact_lines(r, ["docs/prd/orders/prd.md:59: registries: enforced standards row has no linter command ('python3 -m json.tool'); put it in backticks"])
        assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 59, STD.format(linter="`no-such-linter-xyz --check src`", decision="enforced")),
       require_not_on_path("no-such-linter-xyz"))
def test_enforced_linter_not_on_path(case):
    """@prd T-133.2"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/prd.md:59: registries: enforced linter command 'no-such-linter-xyz' is not on PATH"])
    assert_stderr(r, "")


@steps(S0, replace("prd.md", 59, STD.format(linter="`'no such linter' -x`", decision="enforced")))
def test_enforced_linter_quoted_word(case):
    """@prd T-133.3"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, ["docs/prd/orders/prd.md:59: registries: enforced linter command 'no such linter' is not on PATH"])
    assert_stderr(r, "")


@steps(S0, replace("prd.md", 59, STD.format(linter="`no-such-linter-xyz --check src`", decision="enforced")))
def test_enforced_linter_in_ci(case):
    """@prd T-133.4"""
    for args, env in ((("--ci",), None), ((), {"PRD_LINT_CI": "1"})):
        r = case.lint(*args, env=env)
        assert_exit(r, 0)
        assert_stdout(r, "")
        assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 4, "status: Draft"),
       replace("prd.md", 59, STD.format(linter="no-such-linter-xyz", decision="proposed")),
       insert_after("prd.md", 59, "| `**/*.py` | `no-such-linter-xyz` | none | code | declined |"))
def test_unchecked_linter_on_declined_and_proposed(case):
    """@prd T-133.5"""
    r = case.lint()
    assert_stdout_not_contains(r, "registries:")
    assert_stderr(r, "")


NOT_INSTALLED = ("docs/prd/orders/prd.md:65: registries: required skill '{}' is not installed; "
                 "if it is built into Claude Code, mark the row 'recommended'")
PLUGINS_WITH_PATH = '{"plugins": {"superpowers@superpowers-marketplace": [{"installPath": "<tmp>/plug"}]}}'


@steps(S0, replace("prd.md", 65, "| plans | nonexistent:skill | required |"))
def test_required_skill_not_installed(case):
    """@prd T-134.1"""
    r = case.lint()
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [NOT_INSTALLED.format("nonexistent:skill")])
    assert_stderr(r, "")


@steps(S0, replace("prd.md", 65, "| tdd | `superpowers:test-driven-development` | required |"))
def test_required_plugin_skill_present_without_install_path(case):
    """@prd T-134.2"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0, write_lines("<tmp>/plugins.json", PLUGINS_WITH_PATH))
def test_required_plugin_skill_missing_under_install_path(case):
    """@prd T-134.3"""
    r = case.lint(env={"PRD_PLUGINS_FILE": "<tmp>/plugins.json"})
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [NOT_INSTALLED.format("superpowers:writing-plans")])
    assert_stderr(r, "")


@steps(S0,
       write_lines("<tmp>/plugins.json", PLUGINS_WITH_PATH),
       write_lines("<tmp>/plug/skills/writing-plans/SKILL.md", "# writing-plans"))
def test_required_plugin_skill_under_install_path(case):
    """@prd T-134.4"""
    r = case.lint(env={"PRD_PLUGINS_FILE": "<tmp>/plugins.json"})
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 65, "| plans | my-skill | required |"),
       require_outside_git, require_absent("<tmp>/home"))
def test_required_bare_skill_not_installed(case):
    """@prd T-134.5"""
    r = case.lint(env={"HOME": "<tmp>/home"})
    assert_exit(r, 1)
    assert_stdout_exact_lines(r, [NOT_INSTALLED.format("my-skill")])
    assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 65, "| plans | my-skill | required |"),
       write_lines("<tmp>/home/.claude/skills/my-skill/SKILL.md", "# my-skill"))
def test_required_bare_skill_under_home(case):
    """@prd T-134.6"""
    r = case.lint(env={"HOME": "<tmp>/home"})
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 65, "| plans | my-skill | required |"),
       git_init,
       write_lines("<tmp>/.claude/skills/my-skill/SKILL.md", "# my-skill"),
       require_toplevel_is_tmp, require_no_skill_under("<tmp>/home"))
def test_required_bare_skill_under_repository_root(case):
    """@prd T-134.7"""
    r = case.lint(env={"HOME": "<tmp>/home"})
    assert_stdout_not_contains(r, "registries:")
    assert_stderr(r, "")


@steps(S0, replace("prd.md", 65, "| plans | nonexistent:skill | required |"))
def test_required_skill_in_ci(case):
    """@prd T-134.8"""
    for args, env in ((("--ci",), None), ((), {"PRD_LINT_CI": "1"})):
        r = case.lint(*args, env=env)
        assert_exit(r, 0)
        assert_stdout(r, "")
        assert_stderr(r, "")


@steps(S0,
       replace("prd.md", 65, "| plans | nonexistent:skill | recommended |"),
       insert_after("prd.md", 65, "| reviews | other:skill | declined |"))
def test_unchecked_skill_on_recommended_and_declined(case):
    """@prd T-134.9"""
    r = case.lint()
    assert_exit(r, 0)
    assert_stdout(r, "")
    assert_stderr(r, "")
