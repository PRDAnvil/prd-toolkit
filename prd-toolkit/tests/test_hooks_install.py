"""prd_hooks.py install | check | uninstall, in a temp git repo with the orders fixture."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from prdlint import hooks

PLUGIN_ROOT = Path(__file__).parent.parent
PLUGIN_VERSION = json.loads((PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text())["version"]
PRD = "docs/prd/orders"


def git(repo, *args, check=True):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=check)
    return r.stdout.strip()


@pytest.fixture
def repo(prd):
    root = prd.parent.parent.parent
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "T")
    (root / "src").mkdir()
    (root / "src/app.py").write_text("x = 1\n")
    return root


def test_install_vendors_and_writes_shims(repo):
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/VERSION").read_text().strip() == PLUGIN_VERSION
    assert all((repo / ".prd-toolkit" / f).is_file() for f in hooks.VENDORED)
    assert (repo / ".prd-toolkit/prdlint/model.py").is_file()
    assert not list((repo / ".prd-toolkit").rglob("__pycache__"))
    shim = (repo / ".git/hooks/commit-msg").read_text()
    assert hooks.MARKER in shim and PRD in shim and os.access(repo / ".git/hooks/commit-msg", os.X_OK)
    assert os.access(repo / ".prd-toolkit/prd_hooks.py", os.X_OK)


def test_install_is_idempotent_and_refreshes(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/prdlint/stale.py").write_text("x\n")
    (repo / ".prd-toolkit/prd_lint.py").write_text("# changed\n")
    hooks.install(repo, PRD)
    assert not (repo / ".prd-toolkit/prdlint/stale.py").exists()
    assert hooks.check(repo, PLUGIN_ROOT) == []


def test_existing_hook_is_never_overwritten(repo):
    (repo / ".git/hooks/pre-commit").write_text("#!/bin/sh\necho mine\n")
    lines = hooks.install(repo, PRD)
    assert (repo / ".git/hooks/pre-commit").read_text() == "#!/bin/sh\necho mine\n"
    assert any("add this line to .git/hooks/pre-commit" in x for x in lines)


def test_never_sets_hooks_path(repo):
    hooks.install(repo, PRD)
    assert git(repo, "config", "--get", "core.hooksPath", check=False) == ""


def test_check_flags_stale_version_and_changed_file(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/VERSION").write_text("0.0.1\n")
    (repo / ".prd-toolkit/prd_lint.py").write_text("# changed\n")
    problems = hooks.check(repo, PLUGIN_ROOT)
    assert any("VERSION 0.0.1" in x for x in problems) and any("prd_lint.py differs" in x for x in problems)


def test_uninstall_removes_only_marked_hooks(repo):
    hooks.install(repo, PRD)
    (repo / ".git/hooks/post-commit").write_text("#!/bin/sh\necho mine\n")
    hooks.uninstall(repo)
    assert not (repo / ".git/hooks/commit-msg").exists() and (repo / ".git/hooks/post-commit").exists()
    assert (repo / ".prd-toolkit/VERSION").exists()


def commit_in(cwd, message):
    git(cwd, "add", "app.py")
    return subprocess.run(["git", "commit", "-q", "-m", message], cwd=cwd, capture_output=True, text=True)


def test_end_to_end_commit_refused_from_subdirectory(repo):
    hooks.install(repo, PRD)
    r = commit_in(repo / "src", "Add x")
    assert r.returncode != 0 and "Refs" in r.stderr
    assert commit_in(repo / "src", "Add x\n\nRefs: none (no behaviour change)").returncode == 0


def test_shim_blocks_without_uv(repo):
    assert not Path("/usr/bin/uv").exists() and not Path("/bin/uv").exists()
    hooks.install(repo, PRD)
    msg = repo / "msg"
    msg.write_text("x\n")
    r = subprocess.run([str(repo / ".git/hooks/commit-msg"), str(msg)], cwd=repo, env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
    assert r.returncode != 0 and "prd-toolkit: uv is not on PATH; install uv to run this hook" in r.stderr


def run_vendored(repo, *args):
    return subprocess.run([sys.executable, str(repo / ".prd-toolkit/prd_hooks.py"), *args], cwd=repo, capture_output=True, text=True)


def test_vendored_install_writes_shims_only(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/VERSION").write_text("0.0.1\n")
    (repo / ".prd-toolkit/prd_lint.py").write_text("# changed\n")
    for h in ("commit-msg", "pre-commit"):
        (repo / ".git/hooks" / h).unlink()
    r = run_vendored(repo, "install", PRD)
    assert r.returncode == 0, r.stderr
    assert (repo / ".git/hooks/commit-msg").is_file() and (repo / ".git/hooks/pre-commit").is_file()
    assert (repo / ".prd-toolkit/VERSION").read_text() == "0.0.1\n"
    assert (repo / ".prd-toolkit/prd_lint.py").read_text() == "# changed\n"


def test_vendored_check_exits_2(repo):
    hooks.install(repo, PRD)
    r = run_vendored(repo, "check", PRD)
    assert r.returncode == 2 and "run check from the plugin, not the vendored copy" in r.stderr and r.stdout == ""


GUARD = 'command -v uv >/dev/null 2>&1 || { echo "prd-toolkit: uv is not on PATH; install uv to run this hook" >&2; exit 1; }'


SKIP = "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped"
SKIP_PREDATES = "prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped"
TOP = 'prd_top="$(git rev-parse --show-toplevel)" || exit 1; '


def appended(lines):
    line = next(x for x in lines if "add this line" in x)
    return line[line.index(TOP):]


def test_printed_line_is_appendable_sh(repo):
    (repo / ".git/hooks/commit-msg").write_text("#!/bin/sh\necho mine\n")
    lines = hooks.install(repo, PRD)
    line = next(x for x in lines if "add this line" in x)
    assert "exec" not in line and "before any `exit 0`" in line and "sh hook" in line
    hook, launcher = '"$prd_top/.prd-toolkit/prd_git_hook.py"', '"$prd_top/.prd-toolkit/prd"'
    assert line.endswith(
        f'{TOP}if [ -f {hook} ] && [ ! -f {launcher} ]; then echo "{SKIP_PREDATES}" >&2; '
        f'elif [ -f {hook} ] && [ -f {launcher} ] && [ -d "$prd_top/{PRD}" ]; then {GUARD}; '
        f'sh {launcher} git-hook commit-msg "$prd_top/{PRD}" "$@" || exit $?; else echo "{SKIP}" >&2; fi')


def test_appended_line_runs_and_propagates_failure(repo):
    log = repo / "log"
    (repo / ".git/hooks/commit-msg").write_text(f"#!/bin/sh\necho mine >> {log}\n")
    lines = hooks.install(repo, PRD)
    line = appended(lines)
    hook = repo / ".git/hooks/commit-msg"
    hook.write_text(f"#!/bin/sh\necho mine >> {log}\n{line}\necho after >> {log}\n")
    hook.chmod(0o755)
    (repo / "m").write_text("Add x\n\nRefs: none (no behaviour change)\n")
    r = subprocess.run([str(hook), str(repo / "m")], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0 and log.read_text().split() == ["mine", "after"]
    (repo / "m").write_text("Add x\n")
    git(repo, "add", "src/app.py")
    r = subprocess.run([str(hook), str(repo / "m")], cwd=repo, capture_output=True, text=True)
    assert r.returncode != 0 and log.read_text().split() == ["mine", "after", "mine"]


def test_prd_path_with_space_and_dollar(repo):
    odd = "docs/prd/my $prd"
    (repo / odd).parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/prd/orders").rename(repo / odd)
    hooks.install(repo, odd)
    git(repo, "add", "src/app.py")
    r = subprocess.run(["git", "commit", "-q", "-m", "Add x"], cwd=repo, capture_output=True, text=True)
    assert r.returncode != 0 and "Refs" in r.stderr


def test_hookspath_set_writes_no_shim(repo, tmp_path_factory):
    other = tmp_path_factory.mktemp("elsewhere")
    git(repo, "config", "core.hooksPath", str(other))
    lines = hooks.install(repo, PRD)
    assert list(other.iterdir()) == [] and not (repo / ".git/hooks/commit-msg").exists()
    assert sum("add this line" in x for x in lines) == 2 and any(str(other) in x for x in lines)
    other.joinpath("commit-msg").write_text(f"#!/bin/sh\n{hooks.MARKER}\n")
    assert hooks.uninstall(repo) and other.joinpath("commit-msg").exists()
    assert any("core.hooksPath" in x for x in hooks.uninstall(repo))


def test_marker_must_be_second_line(repo):
    mine = f"#!/bin/sh\necho x\n# note: {hooks.MARKER} is mentioned here\n{hooks.MARKER}\n"
    (repo / ".git/hooks/commit-msg").write_text(mine)
    lines = hooks.install(repo, PRD)
    assert (repo / ".git/hooks/commit-msg").read_text() == mine and any("add this line" in x for x in lines)
    hooks.uninstall(repo)
    assert (repo / ".git/hooks/commit-msg").read_text() == mine


def test_shim_has_lf_newlines(repo):
    hooks.install(repo, PRD)
    assert b"\r" not in (repo / ".git/hooks/commit-msg").read_bytes()


def test_vendored_install_when_repo_root_has_plugin_json(repo):
    hooks.install(repo, PRD)
    (repo / ".claude-plugin").mkdir()
    (repo / ".claude-plugin/plugin.json").write_text('{"version": "9"}')
    for h in ("commit-msg", "pre-commit"):
        (repo / ".git/hooks" / h).unlink()
    r = run_vendored(repo, "install", PRD)
    assert r.returncode == 0, r.stderr
    assert (repo / ".git/hooks/commit-msg").is_file()


def test_hook_run_leaves_no_pycache(repo):
    hooks.install(repo, PRD)
    git(repo, "add", "src/app.py")
    subprocess.run(["git", "commit", "-q", "-m", "Add x"], cwd=repo, capture_output=True, text=True)
    assert not list((repo / ".prd-toolkit").rglob("__pycache__"))


def test_commit_on_branch_without_vendored_copy_is_skipped(repo):
    """R36: hooks are per clone, the copy is per branch: a branch with no .prd-toolkit/ commits, with a message."""
    hooks.install(repo, PRD)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--no-verify", "-m", "Start")
    git(repo, "switch", "-q", "-c", "no-toolkit")
    git(repo, "rm", "-r", "-q", ".prd-toolkit")
    (repo / "src/app.py").write_text("x = 2\n")
    git(repo, "add", "src/app.py")
    r = subprocess.run(["git", "commit", "-q", "-m", "Change x"], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stderr.count(SKIP) == 2  # pre-commit and commit-msg


def test_commit_without_prd_folder_is_skipped(repo):
    hooks.install(repo, PRD)
    git(repo, "rm", "-r", "-q", "--cached", "docs", check=False)
    import shutil
    shutil.rmtree(repo / "docs")
    git(repo, "add", "src/app.py")
    r = subprocess.run(["git", "commit", "-q", "-m", "Change x"], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0 and SKIP in r.stderr


def test_appended_line_skips_without_copy_and_blocks_without_uv(repo):
    log = repo / "log"
    (repo / ".git/hooks/commit-msg").write_text("#!/bin/sh\necho mine\n")
    line = appended(hooks.install(repo, PRD))
    hook = repo / ".git/hooks/commit-msg"
    hook.write_text(f"#!/bin/sh\n{line}\necho after >> {log}\n")
    hook.chmod(0o755)
    (repo / "m").write_text("Add x\n")
    r = subprocess.run([str(hook), str(repo / "m")], cwd=repo, env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
    assert r.returncode != 0 and "prd-toolkit: uv is not on PATH" in r.stderr and not log.exists()
    (repo / ".prd-toolkit").rename(repo / "elsewhere")
    r = subprocess.run([str(hook), str(repo / "m")], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0 and SKIP in r.stderr and log.read_text().split() == ["after"]


def test_install_writes_gitignore_for_pycache(repo):
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/.gitignore").read_text() == "__pycache__/\n"
    assert hooks.check(repo, PLUGIN_ROOT) == []


def test_vendored_has_deploy_scripts(repo):
    assert "prd_deploy.py" in hooks.VENDORED and "prd_drift.py" in hooks.VENDORED
    hooks.install(repo, PRD)
    for f in ("prd_deploy.py", "prd_drift.py", "prdlint/deploy.py", "prdlint/drift.py"):
        assert (repo / ".prd-toolkit" / f).is_file(), f
    assert hooks.check(repo, PLUGIN_ROOT) == []


def test_check_reports_stale_deploy_script(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/prd_deploy.py").write_text("# stale\n")
    assert any("prd_deploy.py differs" in x for x in hooks.check(repo, PLUGIN_ROOT))


# --- the vendored copy must run from .prd-toolkit/ alone (task 11 fix round 2) ---

def test_vendors_the_block_template(repo):
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/templates/claude-block.md").read_bytes() == (PLUGIN_ROOT / "templates/claude-block.md").read_bytes()


def test_check_reports_a_stale_vendored_block_template(repo):
    hooks.install(repo, PRD)
    assert hooks.check(repo, PLUGIN_ROOT) == []
    (repo / ".prd-toolkit/templates/claude-block.md").write_text("old\n")
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/templates/claude-block.md differs from the plugin copy"]
    (repo / ".prd-toolkit/templates/claude-block.md").unlink()
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/templates/claude-block.md is missing"]


def test_every_vendored_script_runs_from_the_vendored_copy(repo):
    """No traceback, missing file or import error from any VENDORED script run in .prd-toolkit/ (exit codes for findings are fine)."""
    hooks.install(repo, PRD)
    git(repo, "add", "-A"); git(repo, "commit", "-q", "--no-verify", "-m", "init")
    (repo / "msg.txt").write_text("feat: x\n\nRefs: none (no behaviour change)\n")
    calls = {
        "prd_lint.py": [PRD], "prd_trace.py": [PRD], "prd_status.py": [PRD], "prd_context.py": [PRD],
        "prd_block.py": [PRD, "--claude-md", "CLAUDE.md"], "prd_build_check.py": [PRD, "--diff", "HEAD..HEAD"],
        "prd_deploy.py": ["plan", PRD], "prd_drift.py": [PRD], "prd_hooks.py": ["check", PRD],
        "prd_git_hook.py": ["commit-msg", PRD, "msg.txt"], "prd_error.py": ["list", PRD], "prd_links.py": ["check", PRD],
        "prd_confirm.py": ["status", PRD, "--area", "none"],
        "prd_judge.py": [PRD, "T-999.9", "msg.txt"], "prd_change.py": ["digest", PRD],
        "prd_gates.py": ["list", PRD], "prd_help.py": ["--json"],
    }
    launcher_files = {"prd", "prd_dispatch.py", "requirements.txt"}  # the launcher trio is covered by test_vendor_copies_the_launcher
    assert set(calls) == set(hooks.VENDORED) - launcher_files, set(hooks.VENDORED) ^ set(calls)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    for name, args in calls.items():
        r = subprocess.run([sys.executable, f".prd-toolkit/{name}", *args], cwd=repo, capture_output=True, text=True, env=env)
        err = r.stdout + r.stderr
        for bad in ("Traceback", "No such file", "ModuleNotFoundError", "ImportError", "FileNotFoundError"):
            assert bad not in err, (name, err[-600:])
    assert "prd-toolkit:start" in (repo / "CLAUDE.md").read_text()


def test_vendors_prd_links_and_check_reports_it_missing(repo):
    assert "prd_links.py" in hooks.VENDORED
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/prd_links.py").is_file() and (repo / ".prd-toolkit/prdlint/links.py").is_file()
    assert hooks.check(repo, PLUGIN_ROOT) == []
    (repo / ".prd-toolkit/prd_links.py").unlink()
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/prd_links.py is missing"]


def test_vendored_prd_links_checks_a_linked_prd(repo):
    hooks.install(repo, PRD)
    (repo / PRD / "links.md").write_text(
        "# Links\n\n## Upstreams\n\n| Upstream | Location | Version | Commit | Needs |\n|---|---|---|---|---|\n\n"
        "## Consumers\n\n| Consumer | Location |\n|---|---|\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    r = subprocess.run([sys.executable, ".prd-toolkit/prd_links.py", "check", "--ci", PRD], cwd=repo, capture_output=True, text=True, env=env)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", "")


def test_vendors_the_confirm_script_and_page(repo):
    assert "prd_confirm.py" in hooks.VENDORED
    files = hooks._source_files(hooks.SCRIPTS, hooks.PLUGIN_ROOT / "templates/hooks")
    assert "prd_confirm.py" in files and "confirm/form.html" in files and "confirm/panel.html" in files
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/confirm/form.html").read_bytes() == (PLUGIN_ROOT / "templates/confirm/form.html").read_bytes()
    assert (repo / ".prd-toolkit/confirm/panel.html").read_bytes() == (PLUGIN_ROOT / "templates/confirm/panel.html").read_bytes()
    assert (repo / ".prd-toolkit/prd_confirm.py").is_file()
    assert hooks.check(repo, PLUGIN_ROOT) == []


def test_check_reports_a_stale_vendored_confirm_page(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/confirm/form.html").write_text("old\n")
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/confirm/form.html differs from the plugin copy"]
    (repo / ".prd-toolkit/confirm/form.html").unlink()
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/confirm/form.html is missing"]
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/confirm/extra.html").write_text("x\n")
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/confirm/extra.html is not in the plugin"]
    hooks.install(repo, PRD)
    assert not (repo / ".prd-toolkit/confirm/extra.html").exists()


def test_vendors_prd_gates(repo):
    assert "prd_gates.py" in hooks.VENDORED
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/prd_gates.py").is_file() and (repo / ".prd-toolkit/prdlint/gates.py").is_file()
    assert hooks.check(repo, PLUGIN_ROOT) == []
    (repo / ".prd-toolkit/prd_gates.py").unlink()
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/prd_gates.py is missing"]


def test_vendors_the_inbox_page(repo):
    files = hooks._source_files(hooks.SCRIPTS, hooks.PLUGIN_ROOT / "templates/hooks")
    assert "gates/inbox.html" in files
    hooks.install(repo, PRD)
    assert (repo / ".prd-toolkit/gates/inbox.html").read_bytes() == (PLUGIN_ROOT / "templates/gates/inbox.html").read_bytes()
    assert hooks.check(repo, PLUGIN_ROOT) == []
    (repo / ".prd-toolkit/gates/inbox.html").write_text("old\n")
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/gates/inbox.html differs from the plugin copy"]


def test_vendor_copies_the_launcher(repo, tmp_path):
    hooks.install(repo, PRD)
    vendored = repo / ".prd-toolkit"
    assert all((vendored / n).is_file() for n in ("prd", "prd_dispatch.py", "requirements.txt"))
    assert os.access(vendored / hooks.LAUNCHER, os.X_OK)
    assert (vendored / "requirements.txt").read_text() == "openapi-spec-validator>=0.7\npyyaml>=6.0\nsqlglot>=25\n"
    assert not (vendored / "requirements-publish.txt").exists()
    env = {**os.environ, "UV_CACHE_DIR": str(tmp_path / "uv-cache")}
    run = subprocess.run(["sh", ".prd-toolkit/prd", "--version"], cwd=repo, capture_output=True, text=True, env=env, timeout=300)
    assert run.returncode == 0 and PLUGIN_VERSION in run.stdout, run.stdout + run.stderr


def test_check_reports_missing_launcher(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/prd").unlink()
    assert hooks.check(repo, PLUGIN_ROOT) == [".prd-toolkit/prd is missing"]


# --- 0.8.8: the shims run the launcher (spec §4, §5) ---

# The 0.8.7 templates/hooks/<hook>, with {{hook}} and {{prd}} as install substituted them.
SHIM_087 = """#!/bin/sh
# prd-toolkit hook: written by prd_hooks.py install; removed by prd_hooks.py uninstall
top=$(git rev-parse --show-toplevel) || exit 1
[ -f "$top/.prd-toolkit/prd_git_hook.py" ] && [ -d "$top/@PRD@" ] || { echo "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped" >&2; exit 0; }
command -v uv >/dev/null 2>&1 || { echo "prd-toolkit: uv is not on PATH; install uv to run this hook" >&2; exit 1; }
exec uv run --script "$top/.prd-toolkit/prd_git_hook.py" @HOOK@ "$top/@PRD@"@ARGS@
"""

# The line 0.8.7's install printed for a user's own commit-msg hook.
APPENDED_087 = (f'{TOP}if [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ -d "$prd_top/{PRD}" ]; then {GUARD}; '
                f'uv run --script "$prd_top/.prd-toolkit/prd_git_hook.py" commit-msg "$prd_top/{PRD}" "$@" || exit $?; '
                f'else echo "{SKIP}" >&2; fi')


def write_087_shims(repo, prd_rel=PRD):
    for hook in hooks.HOOKS:
        text = SHIM_087.replace("@HOOK@", hook).replace("@PRD@", prd_rel).replace("@ARGS@", ' "$@"' if hook == "commit-msg" else "")
        (repo / ".git/hooks" / hook).write_text(text)


def run_hook(repo, hook, *args):
    """Run the installed shim in repo with a uv cache of its own: the worker's pytest base temp, never the session's test cache."""
    env = {**os.environ, "UV_CACHE_DIR": str(repo.parent / "hook-uv-cache")}
    return subprocess.run([str(repo / ".git/hooks" / hook), *args], cwd=repo, env=env, capture_output=True, text=True, timeout=300)


def test_shim_uses_the_launcher(repo):
    hooks.install(repo, PRD)
    shim = (repo / ".git/hooks/pre-commit").read_text()
    assert 'exec sh "$top/.prd-toolkit/prd" git-hook pre-commit "$top/docs/prd/orders"' in shim
    assert "--script" not in shim
    msg = (repo / ".git/hooks/commit-msg").read_text()
    assert 'exec sh "$top/.prd-toolkit/prd" git-hook commit-msg "$top/docs/prd/orders" "$@"' in msg
    for text in (shim, msg):
        assert '[ -f "$top/.prd-toolkit/prd_git_hook.py" ] && [ -f "$top/.prd-toolkit/prd" ] && [ -d "$top/docs/prd/orders" ]' in text
        assert GUARD in text


def test_shim_skips_without_launcher(repo):  # a vendored copy older than 0.8.8: the skip says so, not "no .prd-toolkit/"
    assert hooks.SKIP_PREDATES == SKIP_PREDATES and hooks.SKIP == SKIP
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/prd").unlink()
    (repo / "m").write_text("Add x\n")
    for hook, args in (("pre-commit", ()), ("commit-msg", (str(repo / "m"),))):
        r = run_hook(repo, hook, *args)
        assert (r.returncode, r.stderr) == (0, SKIP_PREDATES + "\n"), (hook, r.stderr)
    import shutil
    shutil.rmtree(repo / ".prd-toolkit")  # no copy at all: the general message, as before
    r = run_hook(repo, "pre-commit")
    assert (r.returncode, r.stderr) == (0, SKIP + "\n"), r.stderr


def test_appended_line_skips_without_launcher(repo):
    (repo / ".git/hooks/commit-msg").write_text("#!/bin/sh\necho mine\n")
    line = appended(hooks.install(repo, PRD))
    hook = repo / ".git/hooks/commit-msg"
    hook.write_text(f"#!/bin/sh\n{line}\n")
    hook.chmod(0o755)
    (repo / ".prd-toolkit/prd").unlink()
    (repo / "m").write_text("Add x\n")
    r = subprocess.run([str(hook), str(repo / "m")], cwd=repo, capture_output=True, text=True)
    assert (r.returncode, r.stderr) == (0, SKIP_PREDATES + "\n"), r.stderr


# The 0.8.8 shim as the branch wrote it before the predates-0.8.8 skip line: one guard line, one skip message.
SHIM_088_FIRST = """#!/bin/sh
# prd-toolkit hook: written by prd_hooks.py install; removed by prd_hooks.py uninstall
top=$(git rev-parse --show-toplevel) || exit 1
[ -f "$top/.prd-toolkit/prd_git_hook.py" ] && [ -f "$top/.prd-toolkit/prd" ] && [ -d "$top/@PRD@" ] || { echo "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped" >&2; exit 0; }
command -v uv >/dev/null 2>&1 || { echo "prd-toolkit: uv is not on PATH; install uv to run this hook" >&2; exit 1; }
exec sh "$top/.prd-toolkit/prd" git-hook pre-commit "$top/@PRD@"
"""


def test_check_reports_a_shim_without_the_predates_skip(repo):
    from prdlint import model

    hooks.install(repo, PRD)
    (repo / ".git/hooks/pre-commit").write_text(SHIM_088_FIRST.replace("@PRD@", PRD))
    prd = model.load(repo / PRD)
    assert _shim_lines(hooks.check(repo, PLUGIN_ROOT, prd, PRD)) == ["stale: .git/hooks/pre-commit; run prd_hooks.py install"]
    assert "installed .git/hooks/pre-commit" in hooks.install(repo, PRD)
    assert _shim_lines(hooks.check(repo, PLUGIN_ROOT, prd, PRD)) == []


def test_shim_runs_launcher_without_exec_bit(repo):
    hooks.install(repo, PRD)
    (repo / ".prd-toolkit/prd").chmod(0o644)
    r = run_hook(repo, "pre-commit")
    assert r.returncode == 0 and hooks.SKIP not in r.stderr, r.stderr
    shim = repo / ".git/hooks/pre-commit"  # without `sh`, the same shim cannot run the launcher: the bit is really gone
    shim.write_text(shim.read_text().replace('exec sh "$top/.prd-toolkit/prd"', 'exec "$top/.prd-toolkit/prd"'))
    assert run_hook(repo, "pre-commit").returncode != 0


def test_shim_prd_path_with_space(repo):
    odd = "docs/prd/my orders"
    (repo / PRD).rename(repo / odd)
    hooks.install(repo, odd)
    assert f'exec sh "$top/.prd-toolkit/prd" git-hook pre-commit "$top/{odd}"' in (repo / ".git/hooks/pre-commit").read_text()
    r = run_hook(repo, "pre-commit")
    assert r.returncode == 0 and hooks.SKIP not in r.stderr, r.stderr
    git(repo, "add", "src/app.py")  # the hook really checks the PRD at the spaced path: a boundary commit without Refs is refused
    (repo / "m").write_text("Add x\n")
    r = run_hook(repo, "commit-msg", str(repo / "m"))
    assert r.returncode != 0 and "Refs" in r.stderr, r.stderr


def test_append_line_uses_the_launcher():
    line = hooks._append_line("commit-msg", PRD)
    assert 'sh "$prd_top/.prd-toolkit/prd" git-hook commit-msg "$prd_top/docs/prd/orders" "$@"' in line
    assert "--script" not in line and '[ -f "$prd_top/.prd-toolkit/prd" ]' in line
    assert not hooks.OLD_FORM.search(line) and hooks.OLD_FORM.search(APPENDED_087)


def test_install_rewrites_old_shims(repo):
    hooks.install(repo, PRD)
    write_087_shims(repo)
    lines = hooks.install(repo, PRD)
    assert "replaced .git/hooks/pre-commit (it used uv run --script)" in lines
    assert "replaced .git/hooks/commit-msg (it used uv run --script)" in lines
    assert not any(x.startswith("installed .git/hooks/") for x in lines)
    assert hooks.check(repo, PLUGIN_ROOT) == []
    assert "installed .git/hooks/pre-commit" in hooks.install(repo, PRD)  # a current shim is not "replaced"


def test_check_reports_old_shim(repo):
    hooks.install(repo, PRD)
    write_087_shims(repo)
    out = hooks.check(repo, PLUGIN_ROOT)
    assert out == ["stale: .git/hooks/commit-msg; run prd_hooks.py install", "stale: .git/hooks/pre-commit; run prd_hooks.py install"]


def test_check_with_prd_rel_reports_a_changed_shim(repo):
    from prdlint import model

    hooks.install(repo, PRD)
    prd = model.load(repo / PRD)
    assert [x for x in hooks.check(repo, PLUGIN_ROOT, prd, PRD) if ".git/hooks" in x] == []
    shim = repo / ".git/hooks/pre-commit"
    shim.write_text(shim.read_text() + "# edited\n")
    assert [x for x in hooks.check(repo, PLUGIN_ROOT, prd, PRD) if ".git/hooks" in x] == ["stale: .git/hooks/pre-commit; run prd_hooks.py install"]
    assert hooks.check(repo, PLUGIN_ROOT) == []  # without the PRD's path only the old form is judged


REPLACE_STALE = "replace its uv run --script … prd_git_hook.py line with the line prd_hooks.py install prints"


def test_check_reports_old_appended_line(repo):  # a user's own hook holding the 0.8.7 appended line
    hooks.install(repo, PRD)
    (repo / ".git/hooks/pre-commit").unlink()
    (repo / ".git/hooks/commit-msg").write_text(f"#!/bin/sh\necho mine\n{APPENDED_087}\n")
    assert hooks.check(repo, PLUGIN_ROOT) == [f"stale: .git/hooks/commit-msg; {REPLACE_STALE}"]
    (repo / ".git/hooks/commit-msg").write_text(f"#!/bin/sh\necho mine\n{hooks._append_line('commit-msg', PRD)}\n")
    assert hooks.check(repo, PLUGIN_ROOT) == []
    (repo / ".git/hooks/commit-msg").write_text("#!/bin/sh\necho mine\n")
    assert hooks.check(repo, PLUGIN_ROOT) == []


def _replace_message(lines, hook):
    return next(x for x in lines if f"/{hook}" in x and "replace" in x)


def test_install_says_replace_for_a_users_hook_holding_the_old_line(repo):
    """install never edits a hook that is not ours; on the 0.8.7 line it says to replace that line, not to add one."""
    own = repo / ".git/hooks/commit-msg"
    own.write_text(f"#!/bin/sh\necho mine\n{APPENDED_087}\n")
    lines = hooks.install(repo, PRD)
    assert own.read_text() == f"#!/bin/sh\necho mine\n{APPENDED_087}\n"
    msg = _replace_message(lines, "commit-msg")
    assert "add this line" not in msg
    assert msg == (".git/hooks/commit-msg already exists and was left alone; replace its uv run --script … prd_git_hook.py line "
                   "in .git/hooks/commit-msg with this line: " + hooks._append_line("commit-msg", PRD))


def test_check_is_clean_after_the_user_replaces_the_line(repo):
    own = repo / ".git/hooks/commit-msg"
    own.write_text(f"#!/bin/sh\necho mine\n{APPENDED_087}\necho after\n")
    msg = _replace_message(hooks.install(repo, PRD), "commit-msg")
    assert hooks.check(repo, PLUGIN_ROOT) == [f"stale: .git/hooks/commit-msg; {REPLACE_STALE}"]
    new = msg[msg.index(TOP):]
    own.write_text(own.read_text().replace(APPENDED_087, new))  # what the user does
    assert hooks.check(repo, PLUGIN_ROOT) == []


def test_hookspath_hook_with_the_old_line(repo, tmp_path_factory):
    """core.hooksPath: install writes no shim; on the 0.8.7 line both install and check say to replace it."""
    other = tmp_path_factory.mktemp("own-hooks")
    git(repo, "config", "core.hooksPath", str(other))
    (other / "commit-msg").write_text(f"#!/bin/sh\n{APPENDED_087}\n")
    lines = hooks.install(repo, PRD)
    msg = _replace_message(lines, "commit-msg")
    assert msg.startswith(f"core.hooksPath is set to {other}; no shim written; replace its uv run --script … prd_git_hook.py line in ")
    assert msg.endswith("with this line: " + hooks._append_line("commit-msg", PRD))
    assert any("add this line" in x and "/pre-commit" in x for x in lines)  # no hook there yet: add, as before
    out = [x for x in hooks.check(repo, PLUGIN_ROOT) if x.startswith("stale: ")]
    assert len(out) == 1 and out[0].endswith(f"/commit-msg; {REPLACE_STALE}"), out
    (other / "commit-msg").write_text(f"#!/bin/sh\n{msg[msg.index(TOP):]}\n")
    assert [x for x in hooks.check(repo, PLUGIN_ROOT) if x.startswith("stale: ")] == []


def test_check_without_installed_hooks_is_clean(repo):  # CI: a fresh checkout has no shim
    hooks.install(repo, PRD)
    [p.unlink() for p in (repo / ".git/hooks").glob("*")]
    assert hooks.check(repo, PLUGIN_ROOT) == []


def test_check_ci_ignores_installed_shims(repo):
    hooks.install(repo, PRD)
    write_087_shims(repo)
    cli = [sys.executable, str(PLUGIN_ROOT / "scripts/prd_hooks.py"), "check"]
    plain = subprocess.run([*cli, PRD], cwd=repo, capture_output=True, text=True)
    ci = subprocess.run([*cli, "--ci", PRD], cwd=repo, capture_output=True, text=True)
    assert "stale: .git/hooks/pre-commit; run prd_hooks.py install" in plain.stdout.splitlines(), plain.stdout + plain.stderr
    assert (ci.returncode, ci.stderr) == (0, "") and "stale: .git/hooks/" not in ci.stdout, ci.stdout + ci.stderr


def _shim_lines(lines):
    return [x for x in lines if "/hooks/" in x and x.startswith("stale: ")]


def test_check_outside_git_is_not_an_error(prd):
    """A vendored copy in a folder that is no git checkout: the shim loop adds nothing and raises nothing."""
    from prdlint import model

    root = prd.parent.parent.parent
    assert model.git_toplevel(root) is None, "the test folder is inside a git checkout"
    hooks.vendor(root, PRD)
    assert hooks.check(root, PLUGIN_ROOT) == []
    (root / ".prd-toolkit/prd_lint.py").write_text("# changed\n")
    assert hooks.check(root, PLUGIN_ROOT) == [".prd-toolkit/prd_lint.py differs from the plugin copy"]
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts/prd_hooks.py"), "check", PRD], cwd=root, capture_output=True, text=True)
    assert r.returncode in (0, 1) and "internal error" not in r.stderr, r.stdout + r.stderr


def test_check_two_prds_one_shim_is_not_stale(repo):
    """One shim per hook names the PRD installed last; checking another PRD of the same repository is no finding."""
    import shutil

    from prdlint import model

    other = "docs/prd/other"
    shutil.copytree(repo / PRD, repo / other)
    hooks.install(repo, PRD)
    for rel in (PRD, other):
        assert _shim_lines(hooks.check(repo, PLUGIN_ROOT, model.load(repo / rel), rel)) == [], rel
    write_087_shims(repo)
    for rel in (PRD, other):
        assert _shim_lines(hooks.check(repo, PLUGIN_ROOT, model.load(repo / rel), rel)) == [
            "stale: .git/hooks/commit-msg; run prd_hooks.py install", "stale: .git/hooks/pre-commit; run prd_hooks.py install"], rel


def test_check_reports_a_damaged_own_shim(repo):
    """Our marker, a body that differs from the template other than in the PRD path: stale, never an exception."""
    from prdlint import model

    hooks.install(repo, PRD)
    prd = model.load(repo / PRD)
    shim = repo / ".git/hooks/pre-commit"
    text = shim.read_text()
    shim.write_text(text.replace('exec sh "$top/.prd-toolkit/prd" git-hook', 'exec sh "$top/.prd-toolkit/prd" lint'))
    assert _shim_lines(hooks.check(repo, PLUGIN_ROOT, prd, PRD)) == ["stale: .git/hooks/pre-commit; run prd_hooks.py install"]
    shim.write_text("\n".join(ln for ln in text.split("\n") if "[ -d" not in ln))  # no PRD path left to read
    assert hooks._ours(shim)
    assert _shim_lines(hooks.check(repo, PLUGIN_ROOT, prd, PRD)) == ["stale: .git/hooks/pre-commit; run prd_hooks.py install"]
