"""hooks-install: install writes the hook shims, leaves a user's hook alone, and the hook line runs the launcher
(features/hooks-install.md FR-101, FR-102, FR-103; test-cases/hooks-install.yaml)."""
import os
import shutil
import stat

from hooks_install_support import (  # noqa: F401
    LINE, N0E, ORDERS_REL, SHIM, SetupError, VENDOR, built, check_outside_git, git, given, hi_tmp,
    in_relative_order, run, write_exec,
)

INSTALL = "python HOOKS install docs/prd/orders"


def _n0e(tmp):
    N0E(tmp)


@given(_n0e)
def test_install_writes_both_shims(built):
    """@prd T-101.1"""
    tmp = built
    for _ in range(2):
        r = run(tmp, tmp, INSTALL)
        assert r.exit == 0, r
        assert r.stderr == "", r
        assert in_relative_order(r.stdout.splitlines(),
                                 ["installed .git/hooks/commit-msg", "installed .git/hooks/pre-commit"]), r
        for hook in ("commit-msg", "pre-commit"):
            path = tmp / ".git/hooks" / hook
            assert path.read_bytes() == SHIM(hook, ORDERS_REL).encode("utf-8"), hook
            assert stat.S_IMODE(os.stat(path).st_mode) == 0o755, hook


def _dollar_setup(tmp):
    N0E(tmp)
    (tmp / "docs/prd/orders").rename(tmp / "docs/prd/or $ders")


@given(_dollar_setup)
def test_install_escapes_the_prd_path(built):
    """@prd T-101.2"""
    tmp = built
    r = run(tmp, tmp, ["python", "HOOKS", "install", "docs/prd/or $ders"])
    assert r.exit == 0, r
    assert "installed .git/hooks/commit-msg" in r.stdout.splitlines(), r
    # the dollar sign is preceded by one backslash
    assert (tmp / ".git/hooks/commit-msg").read_bytes() == SHIM("commit-msg", "docs/prd/or \\$ders").encode("utf-8")


def _no_hooks_folder_setup(tmp):
    N0E(tmp)
    hooks = tmp / ".git/hooks"
    if not hooks.is_dir():
        raise SetupError(f"{hooks} is not there to delete")
    shutil.rmtree(hooks)


@given(_no_hooks_folder_setup)
def test_install_creates_the_hooks_folder(built):
    """@prd T-101.3"""
    tmp = built
    r1 = run(tmp, tmp, INSTALL)
    assert r1.exit == 0, r1
    assert in_relative_order(r1.stdout.splitlines(),
                             ["installed .git/hooks/commit-msg", "installed .git/hooks/pre-commit"]), r1
    assert (tmp / ".git/hooks/commit-msg").exists()
    assert (tmp / ".git/hooks/pre-commit").exists()
    r2 = run(tmp, tmp, "git config --get core.hooksPath")
    assert r2.exit == 1, r2
    assert r2.stdout == "", r2


_MINE = "#!/bin/sh\necho mine\n"


def _own_hook_setup(tmp):
    N0E(tmp)
    write_exec(tmp / ".git/hooks/pre-commit", _MINE)


@given(_own_hook_setup)
def test_install_leaves_a_users_hook_alone(built):
    """@prd T-102.1"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    expected = [
        "installed .git/hooks/commit-msg",
        '.git/hooks/pre-commit already exists and was left alone; add this line to .git/hooks/pre-commit (an sh hook; '
        'place it before any `exit 0` in it): prd_top="$(git rev-parse --show-toplevel)" || exit 1; '
        'if [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ ! -f "$prd_top/.prd-toolkit/prd" ]; '
        'then echo "prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped" >&2; '
        'elif [ -f "$prd_top/.prd-toolkit/prd_git_hook.py" ] && [ -f "$prd_top/.prd-toolkit/prd" ] '
        '&& [ -d "$prd_top/docs/prd/orders" ]; then command -v uv >/dev/null 2>&1 || '
        '{ echo "prd-toolkit: uv is not on PATH; install uv to run this hook" >&2; exit 1; }; '
        'sh "$prd_top/.prd-toolkit/prd" git-hook pre-commit "$prd_top/docs/prd/orders" "$@" || exit $?; '
        'else echo "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped" >&2; fi',
    ]
    assert in_relative_order(r.stdout.splitlines(), expected), r
    assert "installed .git/hooks/pre-commit" not in r.stdout, r
    assert (tmp / ".git/hooks/pre-commit").read_bytes() == _MINE.encode("utf-8")


_OLD = "#!/bin/sh\nuv run --script .prd-toolkit/prd_git_hook.py pre-commit docs/prd/orders\n"


def _old_hook_setup(tmp):
    N0E(tmp)
    write_exec(tmp / ".git/hooks/pre-commit", _OLD)


@given(_old_hook_setup)
def test_install_names_the_uv_run_line_to_replace(built):
    """@prd T-102.2"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    line = (".git/hooks/pre-commit already exists and was left alone; replace its uv run --script … "
            "prd_git_hook.py line in .git/hooks/pre-commit with this line: " + LINE("pre-commit"))
    assert line in r.stdout.splitlines(), r
    assert (tmp / ".git/hooks/pre-commit").read_bytes() == _OLD.encode("utf-8")


# -- FR-103: the hook line, run from an sh hook --

# T-103.1's stub launcher: writes each argument on its own line to the file STUB_LOG names, exits STUB_EXIT (0 unset).
_STUB = "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$STUB_LOG\"\nexit \"${STUB_EXIT:-0}\"\n"


def _t103(tmp):
    """The setup of T-103.1."""
    repo = tmp / "repo"
    N0E(repo)
    VENDOR(repo)
    write_exec(repo / ".prd-toolkit/prd", _STUB)
    write_exec(tmp / "hook.sh", "#!/bin/sh\n" + LINE("pre-commit") + "\necho after\n")


@given(_t103)
def test_hook_line_runs_the_launcher(built):
    """@prd T-103.1"""
    tmp = built
    repo = tmp / "repo"
    r = run(tmp, repo, "sh <tmp>/hook.sh a b", env={"STUB_LOG": "<tmp>/stub.log"})
    assert r.exit == 0, r
    assert r.stdout == "after\n", r
    assert r.stderr == "", r
    top = git(tmp, repo, "rev-parse", "--show-toplevel")
    assert top.exit == 0, top
    top_dir = top.stdout.rstrip("\n")
    assert (tmp / "stub.log").read_bytes().decode("utf-8").splitlines() == [
        "git-hook", "pre-commit", f"{top_dir}/docs/prd/orders", "a", "b",
    ]


@given(_t103)
def test_hook_line_exits_with_the_launchers_code(built):
    """@prd T-103.2"""
    tmp = built
    r = run(tmp, tmp / "repo", "sh <tmp>/hook.sh", env={"STUB_LOG": "<tmp>/stub.log", "STUB_EXIT": "3"})
    assert r.exit == 3, r
    assert r.stdout == "", r
    assert (tmp / "stub.log").exists()


def _no_uv_setup(tmp):
    _t103(tmp)
    git_path = shutil.which("git")
    if git_path is None:
        raise SetupError("no git on PATH")
    (tmp / "bin").mkdir()
    os.symlink(os.path.realpath(git_path), tmp / "bin" / "git")
    check = run(tmp, tmp, "<tmp>/bin/git --version", env={"PATH": "<tmp>/bin"})
    if check.exit != 0:
        raise SetupError(f"<tmp>/bin/git --version with PATH=<tmp>/bin exited {check.exit}: {check.stderr}")


@given(_no_uv_setup)
def test_hook_line_without_uv(built):
    """@prd T-103.3"""
    tmp = built
    r = run(tmp, tmp / "repo", "/bin/sh <tmp>/hook.sh", env={"STUB_LOG": "<tmp>/stub.log", "PATH": "<tmp>/bin"})
    assert r.exit == 1, r
    assert r.stdout == "", r
    assert r.stderr == "prd-toolkit: uv is not on PATH; install uv to run this hook\n", r
    assert not (tmp / "stub.log").exists()


def _no_launcher_setup(tmp):
    _t103(tmp)
    (tmp / "repo/.prd-toolkit/prd").unlink()


@given(_no_launcher_setup)
def test_hook_line_skips_a_copy_without_launcher(built):
    """@prd T-103.4"""
    tmp = built
    r = run(tmp, tmp / "repo", "sh <tmp>/hook.sh", env={"STUB_LOG": "<tmp>/stub.log"})
    assert r.exit == 0, r
    assert r.stdout == "after\n", r
    assert r.stderr == "prd-toolkit: .prd-toolkit/ on this branch predates 0.8.8 (no .prd-toolkit/prd); hook skipped\n", r
    assert not (tmp / "stub.log").exists()


@given(_t103)
def test_hook_line_skips_without_copy_or_prd_folder(built):
    """@prd T-103.5"""
    tmp = built
    repo = tmp / "repo"
    env = {"STUB_LOG": "<tmp>/stub.log"}
    skipped = "prd-toolkit: no .prd-toolkit/ (or no PRD folder) on this branch; hook skipped\n"
    (repo / "docs/prd/orders").rename(repo / "docs/prd/gone")
    r1 = run(tmp, repo, "sh <tmp>/hook.sh", env=env)
    (repo / "docs/prd/gone").rename(repo / "docs/prd/orders")
    (repo / ".prd-toolkit/prd_git_hook.py").unlink()
    r2 = run(tmp, repo, "sh <tmp>/hook.sh", env=env)
    for r in (r1, r2):
        assert r.exit == 0, r
        assert r.stdout == "after\n", r
        assert r.stderr == skipped, r
    assert not (tmp / "stub.log").exists()


def _outside_setup(tmp):
    _t103(tmp)
    (tmp / "outside").mkdir()
    check_outside_git(tmp, tmp / "outside")


@given(_outside_setup)
def test_hook_line_outside_a_work_tree(built):
    """@prd T-103.6"""
    tmp = built
    r = run(tmp, tmp / "outside", "sh <tmp>/hook.sh", env={"STUB_LOG": "<tmp>/stub.log"})
    assert r.exit == 1, r
    assert r.stdout == "", r
    assert not (tmp / "stub.log").exists()
