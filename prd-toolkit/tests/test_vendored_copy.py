"""This repository's own `.prd-toolkit/` is the plugin's bytes: CI's `check --ci` compares only the generated CI files."""
import os
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REPO = PLUGIN_ROOT.parent


def test_the_vendored_copy_matches_the_plugin(tmp_path):
    # an empty hooks directory: the result must not depend on which toolkit version this clone last installed its hooks from
    hooks_dir = tmp_path / "no-hooks"
    hooks_dir.mkdir()
    env = {**os.environ, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": str(hooks_dir)}
    run = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts/prd_hooks.py"), "check", "docs/prd/prd-toolkit"],
                         cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=120, env=env)
    assert run.returncode == 0 and not run.stdout and not run.stderr, run.stdout + run.stderr  # refresh it with the vendor-only snippet


def test_the_vendored_launcher_is_the_plugins_bytes_and_executable():
    for name in ("prd", "prd_dispatch.py", "requirements.txt"):
        assert (REPO / ".prd-toolkit" / name).read_bytes() == (PLUGIN_ROOT / "scripts" / name).read_bytes(), name
    assert (REPO / ".prd-toolkit/prd").stat().st_mode & 0o777 == 0o755
    assert (REPO / ".prd-toolkit/requirements.txt").read_text() == "openapi-spec-validator>=0.7\npyyaml>=6.0\nsqlglot>=25\n"
    assert not (REPO / ".prd-toolkit/requirements-publish.txt").exists()
