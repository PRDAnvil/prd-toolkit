"""Black-box tests of pyproject.toml and uv.lock (test-cases/release.yaml, FR-277)."""

import tomllib

from release_support import read_text


def _pyproject():
    return tomllib.loads(read_text("prd-toolkit/pyproject.toml"))


def test_pyproject_project():
    """@prd T-277.1"""
    p = _pyproject()
    assert p["project"]["version"] == "0.1.0"
    assert p["project"]["requires-python"] == ">=3.11"
    assert p["project"]["dependencies"] == ["pyyaml>=6.0", "sqlglot>=25", "openapi-spec-validator>=0.7", "markdown-it-py>=3.0"]
    assert p["dependency-groups"]["dev"] == ["pytest>=8", "pytest-xdist>=3"]
    assert p["tool"]["uv"]["package"] is False


def test_pytest_options():
    """@prd T-277.2"""
    o = _pyproject()["tool"]["pytest"]["ini_options"]
    assert o["testpaths"] == ["tests"]
    assert o["pythonpath"] == ["scripts", "tests"]
    assert "fixtures" in o["norecursedirs"]


def test_uv_lock():
    """@prd T-277.3"""
    lock = tomllib.loads(read_text("prd-toolkit/uv.lock"))
    pyproject = _pyproject()
    assert lock["requires-python"] == ">=3.11"
    # One [[package]] named prd-toolkit.
    pkgs = [p for p in lock["package"] if p.get("name") == "prd-toolkit"]
    assert len(pkgs) == 1, f"{len(pkgs)} [[package]] entries named prd-toolkit"
    pkg = pkgs[0]
    assert pkg["source"] == {"virtual": "."}
    assert pkg["version"] == pyproject["project"]["version"]
    # AC-277.3: metadata.requires-dist and metadata.requires-dev.dev, each compared as a set of
    # (name, specifier), each pair read from an entry's `name` and `specifier` keys.
    dist = {(d["name"], d["specifier"]) for d in pkg["metadata"]["requires-dist"]}
    assert dist == {
        ("markdown-it-py", ">=3.0"),
        ("openapi-spec-validator", ">=0.7"),
        ("pyyaml", ">=6.0"),
        ("sqlglot", ">=25"),
    }
    dev = {(d["name"], d["specifier"]) for d in pkg["metadata"]["requires-dev"]["dev"]}
    assert dev == {("pytest", ">=8"), ("pytest-xdist", ">=3")}
