"""The launcher cases (test-cases/launcher.yaml): the Python the prd launcher runs on (FR-069)."""

from __future__ import annotations

from pathlib import Path

from launcher_support import LS0, LV, SCRIPTS, log_lines, plugin_version, run_launcher, subprocess_path


def _expected_log(python_value: str) -> list[str]:
    return [
        "python", "find", "--system", ">=3.11", "--",
        "run", "--quiet", "--no-project", "--project", SCRIPTS,
        "--python", python_value,
        "--with-requirements", SCRIPTS + "/requirements.txt",
        "python", SCRIPTS + "/prd_dispatch.py", "--version", "--",
    ]


def test_found_path_with_space_is_the_python(tmp_path: Path) -> None:
    """@prd T-069.1"""
    LS0(tmp_path)
    env = {
        "PATH": f"{tmp_path}/bin:{subprocess_path()}",
        "UV_STUB_LOG": f"{tmp_path}/uv.log",
        "UV_STUB_FIND": f"{tmp_path}/py 3/bin/python3",
    }
    r = run_launcher(["--version"], cwd=tmp_path, env=env)
    assert r.exit == 0
    assert r.stdout == b""
    assert r.stderr == b""
    assert log_lines(tmp_path / "uv.log") == _expected_log(f"{tmp_path}/py 3/bin/python3")


def test_find_fails_or_prints_nothing_falls_back(tmp_path: Path) -> None:
    """@prd T-069.2"""
    LS0(tmp_path)
    runs = [
        {
            "PATH": f"{tmp_path}/bin:{subprocess_path()}",
            "UV_STUB_LOG": f"{tmp_path}/uv1.log",
            "UV_STUB_FIND": f"{tmp_path}/py/bin/python3",
            "UV_STUB_FIND_EXIT": "1",
        },
        {
            "PATH": f"{tmp_path}/bin:{subprocess_path()}",
            "UV_STUB_LOG": f"{tmp_path}/uv2.log",
        },
    ]
    for i, env in enumerate(runs, start=1):
        r = run_launcher(["--version"], cwd=tmp_path, env=env)
        assert r.exit == 0, f"run_{i}"
        assert r.stdout == b"", f"run_{i}"
        assert r.stderr == b"", f"run_{i}"
    for name in ("uv1.log", "uv2.log"):
        assert log_lines(tmp_path / name) == _expected_log(">=3.11"), name


def test_unreadable_venv_interpreter_does_not_stop_it(tmp_path: Path) -> None:
    """@prd T-069.3"""
    with LV(tmp_path):
        r = run_launcher(["--version"], cwd=tmp_path / "work")
        assert r.exit == 0
        assert r.stdout == (plugin_version() + "\n").encode("utf-8")
        assert r.stderr == b""
