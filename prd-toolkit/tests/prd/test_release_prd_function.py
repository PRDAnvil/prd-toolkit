"""Black-box tests of the root README's prd shell function (test-cases/release.yaml, FR-274)."""

import pytest

from release_support import prd_function, run, snapshot, subprocess_env, write_line

# The lines the FR-274 setups write (test-cases/release.yaml), each followed by a newline.
PLUGIN_0_8_9 = "printf '%s\\n' plugin-0.8.9 \"$@\""
PLUGIN_0_8_19 = "printf '%s\\n' plugin-0.8.19 \"$@\""
VENDORED = "printf '%s\\n' vendored \"$@\""
WRONG = "printf '%s\\n' wrong-launcher \"$@\""


def _command(func, *args):
    """["sh", "-c", "FUNC\\nprd \\"$@\\"", "sh", <args>...]"""
    return ["sh", "-c", func + "\nprd \"$@\"", "sh", *args]


def _env(tmp, home):
    """The Subprocess environment (Harness) minus GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE and
    GIT_COMMON_DIR, plus the case's env: HOME and GIT_CEILING_DIRECTORIES=<tmp>."""
    return subprocess_env({"HOME": str(home), "GIT_CEILING_DIRECTORIES": str(tmp)}, drop_git=True)


def _git_init(tmp, home, folder):
    r = run(["git", "init", "-q", str(folder)], cwd=tmp, env=_env(tmp, home))
    assert r.returncode == 0, f"setup: git init {folder}: {r.stderr.decode('utf-8', 'replace')}"


def _setup_274_1(tmp):
    """The setup of T-274.1; returns FUNC."""
    func = prd_function()
    home = tmp / "home"
    write_line(home / ".claude/plugins/cache/prdanvil/prd-toolkit/0.8.9/scripts/prd", PLUGIN_0_8_9)
    write_line(home / ".claude/plugins/cache/prdanvil/prd-toolkit/0.8.19/scripts/prd", PLUGIN_0_8_19)
    _git_init(tmp, home, tmp / "repo")
    write_line(tmp / "repo/.prd-toolkit/prd", VENDORED)
    return func


def test_vendored_launcher(tmp_path):
    """@prd T-274.1"""
    tmp = tmp_path.resolve()
    func = _setup_274_1(tmp)
    before = snapshot(tmp)
    r = run(_command(func, "lint", "docs/prd/a b"), cwd=tmp / "repo", env=_env(tmp, tmp / "home"))
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    assert r.stdout == "vendored\nlint\ndocs/prd/a b\n".encode("utf-8"), r.stdout
    assert r.stderr == b"", r.stderr
    assert snapshot(tmp) == before, "a file under <tmp> changed"


def test_plugin_launcher_newest(tmp_path):
    """@prd T-274.2"""
    tmp = tmp_path.resolve()
    home = tmp / "home"
    func = _setup_274_1(tmp)
    _git_init(tmp, home, tmp / "novendor")
    (tmp / "plain").mkdir()
    before = snapshot(tmp)
    runs = [
        (tmp / "repo", ["publish", "docs/prd/a"], "plugin-0.8.19\npublish\ndocs/prd/a\n"),
        (tmp / "plain", ["status"], "plugin-0.8.19\nstatus\n"),
        (tmp / "novendor", ["lint"], "plugin-0.8.19\nlint\n"),
    ]
    for n, (cwd, args, expected) in enumerate(runs, 1):
        r = run(_command(func, *args), cwd=cwd, env=_env(tmp, home))
        assert r.returncode == 0, f"run_{n}: exit {r.returncode}: {r.stderr!r}"
        assert r.stdout == expected.encode("utf-8"), f"run_{n}: {r.stdout!r}"
    assert snapshot(tmp) == before, "a file under <tmp> changed"


def test_not_installed(tmp_path):
    """@prd T-274.3"""
    tmp = tmp_path.resolve()
    func = prd_function()
    home = tmp / "emptyhome"
    home.mkdir()
    (tmp / "plain").mkdir()
    write_line(tmp / "plain/scripts/prd", WRONG)
    before = snapshot(tmp)
    r = run(_command(func, "status"), cwd=tmp / "plain", env=_env(tmp, home))
    assert r.returncode == 127, (r.returncode, r.stdout, r.stderr)
    assert r.stdout == b"", r.stdout
    assert "prd-toolkit is not installed".encode("utf-8") in r.stderr, r.stderr
    assert snapshot(tmp) == before, "a file under <tmp> changed"
