"""scripts/prd: the sh launcher that runs prd_dispatch.py in one uv environment per requirements list."""
import os
import shutil
import subprocess
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
