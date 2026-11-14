"""scripts/prd: the sh launcher that runs prd_dispatch.py in one uv environment per requirements list."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
SCRIPTS = PLUGIN_ROOT / "scripts"


def copy_scripts(dest: Path) -> None:
    """The launcher, the dispatcher, requirements.txt and prd_status.py with prdlint/, and a VERSION, in dest."""
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("prd", "prd_dispatch.py", "requirements.txt", "prd_status.py"):
        shutil.copy2(SCRIPTS / name, dest / name)
    shutil.copytree(SCRIPTS / "prdlint", dest / "prdlint", ignore=shutil.ignore_patterns("__pycache__"))
    (dest / "VERSION").write_text("0.0.0-test\n")


def launch(where: Path, *args, cache: Path, cwd: Path | None = None, path: str | None = None, sh: bool = False):
    """Run where/prd with its own uv cache: directly, or through /bin/sh when sh is true."""
    env = {**os.environ, "UV_CACHE_DIR": str(cache)}
    if path is not None:
        env["PATH"] = path
    argv = ["/bin/sh", str(where / "prd")] if sh else [str(where / "prd")]
    return subprocess.run([*argv, *args], cwd=cwd, env=env, capture_output=True, text=True)


def test_launcher_two_clones_one_environment(tmp_path):
    cache = tmp_path / "cache"
    for name in ("clone a", "clone-b"):
        copy_scripts(tmp_path / name)
        # the three vendored packages may already be in the base interpreter, which needs no environment at all;
        # one small pinned package no interpreter here holds forces one, so the count proves "one, not two"
        with open(tmp_path / name / "requirements.txt", "a") as f:
            f.write("tomli-w==1.0.0\n")
        r = launch(tmp_path / name, "--version", cache=cache)
        assert r.returncode == 0, r.stderr
        assert r.stdout == "0.0.0-test\n"
    assert len(list((cache / "environments-v2").iterdir())) == 1


def test_launcher_ignores_host_project(tmp_path):
    host = tmp_path / "host"
    copy_scripts(host / ".prd-toolkit")
    (host / "pyproject.toml").write_text('[project]\nname="h"\nversion="0"\ndependencies=["no-such-package-xyz==9.9.9"]\n')
    r = launch(host / ".prd-toolkit", "--version", cache=tmp_path / "cache", cwd=host)
    assert r.returncode == 0, r.stderr
    assert r.stdout == "0.0.0-test\n"
    assert not (host / ".venv").exists() and not (host / "uv.lock").exists()


def test_launcher_first_run_quiet(tmp_path):
    copy_scripts(tmp_path / "c")
    r = launch(tmp_path / "c", "--version", cache=tmp_path / "empty-cache")
    assert r.returncode == 0 and r.stderr == "", r.stderr
    assert r.stdout == "0.0.0-test\n"


def test_launcher_without_uv(tmp_path):
    assert not any(Path(d, "uv").exists() for d in ("/usr/bin", "/bin")), "uv is in /usr/bin or /bin on this runner"
    copy_scripts(tmp_path / "c")
    r = launch(tmp_path / "c", "--version", cache=tmp_path / "cache", path="/usr/bin:/bin")
    assert r.returncode == 2 and r.stderr == "prd: uv is not on PATH; install uv\n", r.stderr
    assert r.stdout == ""


def test_launcher_from_another_cwd(tmp_path):
    copy_scripts(tmp_path / "c")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    for sh in (False, True):
        r = launch(tmp_path / "c", "--version", cache=tmp_path / "cache", cwd=elsewhere, sh=sh)
        assert r.returncode == 0, r.stderr
        assert r.stdout == "0.0.0-test\n"


def test_launcher_path_with_spaces(tmp_path):
    clone = tmp_path / "clone a"
    copy_scripts(clone)
    missing = tmp_path / "no such prd"
    for sh in (False, True):
        r = launch(clone, "status", str(missing), cache=tmp_path / "cache", sh=sh)
        assert r.returncode == 2
        assert r.stderr == f"prd_status: {missing.resolve().as_posix()}: no prd.md\n"


def test_launcher_is_executable():
    assert os.access(SCRIPTS / "prd", os.X_OK)


def test_launcher_publish_uses_its_own_requirements(tmp_path):
    """`prd publish` runs with requirements-publish.txt when it is beside the launcher: the vendored list lacks its packages."""
    copy_scripts(tmp_path / "c")
    for name in ("prd_publish.py", "requirements-publish.txt"):
        shutil.copy2(SCRIPTS / name, tmp_path / "c" / name)
    r = launch(tmp_path / "c", "publish", "--help", cache=tmp_path / "cache")
    want = subprocess.run([sys.executable, str(SCRIPTS / "prd_publish.py"), "--help"], capture_output=True, text=True)
    assert want.returncode == 0 and want.stdout.startswith("usage: prd_publish.py"), want.stderr
    assert (r.returncode, r.stdout) == (0, want.stdout), r.stderr
    # the environment holds the publish-only renderer, which neither requirements.txt nor the base interpreter has
    assert list((tmp_path / "cache/environments-v2").glob("*/*/lib/python*/site-packages/mermaidx")), "no environment from requirements-publish.txt"


def test_launcher_publish_without_its_file(tmp_path):
    """A vendored copy has neither prd_publish.py nor requirements-publish.txt: the dispatcher, not the launcher, refuses."""
    copy_scripts(tmp_path / "c")
    r = launch(tmp_path / "c", "publish", cache=tmp_path / "cache")
    here = (tmp_path / "c").resolve()
    assert r.returncode == 2 and r.stderr == f"prd: prd_publish.py is not in {here}; run prd_hooks.py install\n", r.stderr
