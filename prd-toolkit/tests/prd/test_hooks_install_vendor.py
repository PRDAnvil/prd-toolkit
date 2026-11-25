"""hooks-install: install writes the vendored copy, its packs and the .gitignore lines
(features/hooks-install.md FR-098, FR-099, FR-100; test-cases/hooks-install.yaml)."""
import json
import os
import shutil
import stat
from pathlib import Path

from hooks_install_support import (  # noqa: F401
    N0E, ORDERS_REL, PLUGIN, SCRIPTS, SetupError, V, built, files_outside_pycache, given, hi_tmp, insert_after,
    run, step_run, write, write_empty_no_git,
)

INSTALL = "python HOOKS install docs/prd/orders"

# AC-098.1, the files from scripts/, in its order.
_SCRIPT_FILES = [
    "prd_lint.py", "prd_trace.py", "prd_status.py", "prd_context.py", "prd_build_check.py",
    "prd_hooks.py", "prd_git_hook.py", "prd_deploy.py", "prd_drift.py", "prd_block.py", "prd_error.py",
    "prd_links.py", "prd_confirm.py", "prd_judge.py", "prd_change.py", "prd_gates.py", "prd_dispatch.py",
    "prd_help.py", "prd_practices.py", "prd_pack.py", "requirements.txt", "prd",
]


def _ac_098_1_files():
    """(plugin file, path under .prd-toolkit) for each file AC-098.1 lists, in its order."""
    pairs = [(SCRIPTS / name, name) for name in _SCRIPT_FILES]
    for rel in files_outside_pycache(SCRIPTS / "prdlint"):
        pairs.append((SCRIPTS / "prdlint" / rel, f"prdlint/{rel}"))
    templates = PLUGIN / "templates"
    for hook in ("commit-msg", "pre-commit"):
        pairs.append((templates / "hooks" / hook, f"hooks/{hook}"))
    for name in ("claude-block.md", "readme-prd.md", "readme-prds.md"):
        pairs.append((templates / name, f"templates/{name}"))
    for name in ("form.html", "panel.html"):
        pairs.append((templates / "confirm" / name, f"confirm/{name}"))
    pairs.append((templates / "gates" / "inbox.html", "gates/inbox.html"))
    judge = templates / "judge"
    for p in sorted(judge.rglob("*")):
        if p.is_file():
            pairs.append((p, f"judge/{p.relative_to(judge).as_posix()}"))
    for p in sorted((PLUGIN / "references" / "languages").glob("*.yaml")):
        pairs.append((p, f"languages/{p.name}"))
    pairs.append((PLUGIN / "references" / "help.yaml", "help.yaml"))
    pairs.append((PLUGIN / "LICENSE", "LICENSE"))
    return pairs


def _n0e(tmp):
    N0E(tmp)


@given(_n0e)
def test_install_writes_the_listed_files(built):
    """@prd T-098.1"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    vendored = tmp / ".prd-toolkit"
    for plugin_file, rel in _ac_098_1_files():
        copy = vendored / rel
        assert copy.is_file(), f"{rel} is missing from .prd-toolkit"
        assert copy.read_bytes() == plugin_file.read_bytes(), f"{rel} differs from {plugin_file}"
        assert stat.S_IMODE(os.stat(copy).st_mode) == stat.S_IMODE(os.stat(plugin_file).st_mode), rel
    leftovers = [p.relative_to(vendored).as_posix() for p in vendored.rglob("*")
                 if (p.is_dir() and p.name == "__pycache__") or (p.is_file() and p.name.endswith(".pyc"))]
    assert leftovers == []
    vendored_prdlint = {p.relative_to(vendored / "prdlint").as_posix()
                        for p in (vendored / "prdlint").rglob("*") if p.is_file()}
    assert vendored_prdlint == set(files_outside_pycache(SCRIPTS / "prdlint"))


@given(_n0e)
def test_install_writes_version_and_gitignore(built):
    """@prd T-098.2"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    assert r.stderr == "", r
    lines = r.stdout.splitlines()
    assert lines and lines[0] == f"vendored the toolkit into .prd-toolkit/ (version {V()})", r
    assert (tmp / ".prd-toolkit/VERSION").read_bytes() == f"{V()}\n".encode("utf-8")
    assert (tmp / ".prd-toolkit/.gitignore").read_bytes() == b"__pycache__/\n"


_LEFT_OUT = ("__pycache__", ".uv-test-cache", ".venv", ".pytest_cache")


def _plugin_copy_ignore():
    """The copytree ignore of T-098.3: the four folder names at any depth, and the session's UV_CACHE_DIR when it
    lies inside <repo>/prd-toolkit."""
    plugin = PLUGIN.resolve()
    uv_cache = None
    value = os.environ.get("UV_CACHE_DIR", "")
    if value:
        candidate = Path(value).resolve()
        if candidate == plugin or plugin in candidate.parents:
            uv_cache = candidate

    def ignore(src_dir, names):
        skipped = set()
        for name in names:
            path = Path(src_dir, name)
            if name in _LEFT_OUT and path.is_dir():
                skipped.add(name)
            elif uv_cache is not None and path.resolve() == uv_cache:
                skipped.add(name)
        return skipped

    return ignore


def _homepage_setup(tmp):
    N0E(tmp / "a")
    N0E(tmp / "b")
    shutil.copytree(PLUGIN, tmp / "plugin", symlinks=True, ignore=_plugin_copy_ignore())
    real = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    homepage = real.get("homepage")
    if not isinstance(homepage, str) or not homepage.strip():
        raise SetupError("<repo>/prd-toolkit/.claude-plugin/plugin.json has no homepage with text")
    manifest = tmp / "plugin" / ".claude-plugin" / "plugin.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    del data["homepage"]
    with manifest.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    write(tmp / "b" / ".prd-toolkit" / "HOMEPAGE", "https://stale.example.com\n")


@given(_homepage_setup)
def test_install_writes_or_leaves_out_homepage(built):
    """@prd T-098.3"""
    tmp = built
    r1 = run(tmp, tmp / "a", INSTALL)
    r2 = run(tmp, tmp / "b", "python <tmp>/plugin/scripts/prd_hooks.py install docs/prd/orders")
    assert r1.exit == 0, r1
    assert r2.exit == 0, r2
    homepage = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["homepage"]
    assert (tmp / "a/.prd-toolkit/HOMEPAGE").read_bytes() == (homepage.strip() + "\n").encode("utf-8")
    assert not (tmp / "b/.prd-toolkit/HOMEPAGE").exists()


def _stale_setup(tmp):
    N0E(tmp)
    step_run(tmp, tmp, INSTALL)
    write(tmp / ".prd-toolkit/prdlint/stale.py", "x = 1\n")
    write(tmp / ".prd-toolkit/judge/old/old.txt", "old\n")
    write(tmp / ".prd-toolkit/languages/xx.yaml", "language: xx\n")
    (tmp / ".prd-toolkit/hooks/empty").mkdir(parents=True)


@given(_stale_setup)
def test_install_deletes_files_it_does_not_write(built):
    """@prd T-098.4"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    for rel in ("prdlint/stale.py", "judge/old/old.txt", "judge/old", "languages/xx.yaml", "hooks/empty"):
        assert not (tmp / ".prd-toolkit" / rel).exists(), rel
    assert (tmp / ".prd-toolkit/hooks/commit-msg").exists()
    assert (tmp / ".prd-toolkit/hooks/pre-commit").exists()


@given(_n0e)
def test_install_writes_requirements_and_no_publish(built):
    """@prd T-098.5"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    assert (tmp / ".prd-toolkit/requirements.txt").read_bytes() == (
        b"openapi-spec-validator>=0.7\npyyaml>=6.0\nsqlglot>=25\n"
    )
    assert not (tmp / ".prd-toolkit/prd_publish.py").exists()
    assert not (tmp / ".prd-toolkit/requirements-publish.txt").exists()


def _empty_outside_git_setup(tmp):
    # T-098.6 setup: write each entry of fixture status-next/empty to <tmp>/<key>, run no git init; check that
    # `git rev-parse --show-toplevel` exits other than 0 in <tmp>, and otherwise end the test as an error.
    write_empty_no_git(tmp)


@given(_empty_outside_git_setup)
def test_install_outside_a_git_checkout(built):
    """@prd T-098.6"""
    tmp = built
    r = run(tmp, tmp, "python HOOKS install docs/prd/orders")
    expected_stderr = (
        "prd_hooks: " + os.path.realpath(tmp) + "/docs/prd/orders is not inside a git checkout\n"
    )
    assert r.exit == 2, r
    assert r.stdout == "", r
    assert r.stderr == expected_stderr, r
    # effect: none of <tmp>/.prd-toolkit, <tmp>/docs/prd/orders/.prd-toolkit and
    # <tmp>/docs/prd/orders/.gitignore exists
    for path in (tmp / ".prd-toolkit", tmp / "docs/prd/orders/.prd-toolkit", tmp / "docs/prd/orders/.gitignore"):
        assert not os.path.lexists(path), path


def _pack_line(tmp, line):
    insert_after(tmp / ORDERS_REL / "prd.md", "- Language: Python 3.12", line)


def _document_pack_setup(tmp):
    N0E(tmp)
    _pack_line(tmp, "- Pack: document 1.0.0 (prd-toolkit)")
    write(tmp / ".prd-toolkit/packs/old/pack.yaml", "pack: old\n")


@given(_document_pack_setup)
def test_install_vendors_the_named_packs(built):
    """@prd T-099.1"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 0, r
    packs = tmp / ".prd-toolkit/packs"
    assert sorted(os.listdir(packs)) == ["document", "service"]
    for name in ("document", "service"):
        assert (packs / name).is_dir(), name
        assert files_outside_pycache(packs / name) == files_outside_pycache(PLUGIN / "packs" / name), name


def _sources_setup(tmp):
    N0E(tmp / "a")
    N0E(tmp / "b")
    _pack_line(tmp / "b", "- Pack: document 1.0.0 (prd-toolkit)")


@given(_sources_setup)
def test_install_records_pack_sources(built):
    """@prd T-099.2"""
    tmp = built
    for repo in ("a", "b"):
        r = run(tmp, tmp / repo, INSTALL)
        assert r.exit == 0, (repo, r)
    assert (tmp / "a/.prd-toolkit/pack-sources.json").read_bytes() == b'{\n  "service": "prd-toolkit"\n}\n'
    assert (tmp / "b/.prd-toolkit/pack-sources.json").read_bytes() == (
        b'{\n  "document": "prd-toolkit",\n  "service": "prd-toolkit"\n}\n'
    )


_NO_WRITE = (".prd-toolkit", ".git/hooks/commit-msg", ".git/hooks/pre-commit", ".gitignore", "CLAUDE.md",
             "docs/prd/orders/README.md", "docs/prd/README.md")


def _nosuch_setup(tmp):
    N0E(tmp)
    _pack_line(tmp, "- Pack: nosuch 1.0.0 (prd-toolkit)")


@given(_nosuch_setup)
def test_install_refuses_an_unresolved_pack(built):
    """@prd T-099.3"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 2, r
    assert r.stdout == "", r
    assert "prd_hooks: install refused: pack nosuch 1.0.0 (prd-toolkit) not found; looked in: " in r.stderr, r
    for rel in _NO_WRITE:
        assert not (tmp / rel).exists(), rel


def _service_999_setup(tmp):
    N0E(tmp)
    _pack_line(tmp, "- Pack: service 9.9.9 (prd-toolkit)")


@given(_service_999_setup)
def test_install_refusal_names_the_version_found(built):
    """@prd T-099.4"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 2, r
    assert r.stdout == "", r
    for text in ("prd_hooks: install refused: pack service 9.9.9 (prd-toolkit) not found; looked in: ",
                 "; to move the PRD to service 1.0.0, run prd_change.py pack docs/prd/orders service 1.0.0"):
        assert text in r.stderr, (text, r)
    for rel in _NO_WRITE:
        assert not (tmp / rel).exists(), rel


def _gitignore_setup(tmp):
    N0E(tmp / "a")
    N0E(tmp / "b")
    write(tmp / "a/.gitignore", "node_modules\n  .prd-review.json  \nbuild")  # no newline at the end


@given(_gitignore_setup)
def test_install_appends_the_gitignore_lines(built):
    """@prd T-100.1"""
    tmp = built
    r1 = run(tmp, tmp / "a", INSTALL)
    assert r1.exit == 0, r1
    after_1 = (tmp / "a/.gitignore").read_bytes()
    assert after_1 == b"node_modules\n  .prd-review.json  \nbuild\n.prd-judge/\n"
    r2 = run(tmp, tmp / "a", INSTALL)
    assert r2.exit == 0, r2
    assert (tmp / "a/.gitignore").read_bytes() == after_1
    r3 = run(tmp, tmp / "b", INSTALL)
    assert r3.exit == 0, r3
    assert (tmp / "b/.gitignore").read_bytes() == b".prd-judge/\n.prd-review.json\n"
