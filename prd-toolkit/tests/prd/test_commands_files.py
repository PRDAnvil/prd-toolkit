"""FR-281: the commands folder holds twelve command files of one shape (test-cases/commands.yaml)."""
from __future__ import annotations

import subprocess

from commands_support import NAMES, REPO, body, cmd, first_line, flat, fm, git_env, missing, present


def test_commands_folder_holds_twelve_tracked_files():
    """@prd T-281.1"""
    # input.read: the lines `git -C <repo> ls-files prd-toolkit/commands` prints, sorted
    # (testing.md, the commands paragraph: run as the case writes it, with the Subprocess
    # environment minus GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE and GIT_COMMON_DIR; its stdout
    # lines sorted with Python's `sorted`).
    r = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "prd-toolkit/commands"],
        capture_output=True,
        env=git_env(),
    )
    assert r.returncode == 0, (
        f"git ls-files exited {r.returncode}: {r.stderr.decode('utf-8', 'replace').strip()}"
    )
    read = sorted(r.stdout.decode("utf-8").splitlines())
    # expect.output.equals
    expected = [
        "prd-toolkit/commands/prd-adopt.md",
        "prd-toolkit/commands/prd-build.md",
        "prd-toolkit/commands/prd-change-set.md",
        "prd-toolkit/commands/prd-change.md",
        "prd-toolkit/commands/prd-context.md",
        "prd-toolkit/commands/prd-deploy.md",
        "prd-toolkit/commands/prd-error.md",
        "prd-toolkit/commands/prd-new.md",
        "prd-toolkit/commands/prd-pack.md",
        "prd-toolkit/commands/prd-practices.md",
        "prd-toolkit/commands/prd-publish.md",
        "prd-toolkit/commands/prd-status.md",
    ]
    assert read == expected


def test_commands_frontmatter_is_one_description_line():
    """@prd T-281.2"""
    problems = []
    for name in NAMES:
        if first_line(name) != "---":
            problems.append(f"{name}: first line is {first_line(name)!r}, not '---'")
        lines = fm(name)
        if len(lines) != 1:
            problems.append(f"{name}: FM holds {len(lines)} lines, not 1: {lines!r}")
            continue
        line = lines[0]
        if not line.startswith("description: "):
            problems.append(f"{name}: FM line {line!r} does not start with 'description: '")
            continue
        value = line[len("description: "):]
        if not value.endswith(" (prd-toolkit)"):
            problems.append(f"{name}: value {value!r} does not end with ' (prd-toolkit)'")
        for bad in present(value, [": ", " #"]):
            problems.append(f"{name}: value {value!r} holds {bad!r}")
    assert not problems, "\n".join(problems)


def test_commands_body_holds_arguments_once():
    """@prd T-281.3"""
    problems = []
    for name in NAMES:
        n = body(name).count("$ARGUMENTS")
        if n != 1:
            problems.append(f"{name}: BODY holds $ARGUMENTS {n} times, not 1")
    assert not problems, "\n".join(problems)


def test_commands_hold_no_bare_command_name_or_script_path():
    """@prd T-281.4"""
    lacks = [
        r"re:(?<![:A-Za-z0-9_-])/prd-(new|adopt|change-set|change|build|error|deploy|status|context|publish|practices|pack)\b",
        "uv run --script",
        "${CLAUDE_PLUGIN_ROOT}/scripts",
    ]
    problems = []
    for name in NAMES:
        for hit in present(cmd(name), lacks):
            problems.append(f"{name}: CMD holds {hit!r}")
    assert not problems, "\n".join(problems)


def test_commands_find_the_one_prd():
    """@prd T-281.5"""
    holds = ["Find the one `docs/prd/*/prd.md`. If there is more than one, ask which PRD."]
    problems = []
    for name in ["prd-build", "prd-change-set", "prd-context", "prd-deploy", "prd-error", "prd-publish", "prd-status"]:
        for m in missing(flat(body(name)), holds):
            problems.append(f"{name}: flat(BODY) lacks {m!r}")
    assert not problems, "\n".join(problems)
