"""hooks-install: install refreshes the managed blocks and refuses a broken marker
(features/hooks-install.md FR-104; test-cases/hooks-install.yaml)."""
from hooks_install_support import N0E, built, given, hi_tmp, in_relative_order, run, write  # noqa: F401

INSTALL = "python HOOKS install docs/prd/orders"
_BLOCK_FILES = ("CLAUDE.md", "docs/prd/orders/README.md", "docs/prd/README.md")


def _n0e(tmp):
    N0E(tmp)


@given(_n0e)
def test_install_refreshes_the_managed_blocks(built):
    """@prd T-104.1"""
    tmp = built
    r1 = run(tmp, tmp, INSTALL)
    assert r1.exit == 0, r1
    assert in_relative_order(r1.stdout.splitlines(), [
        "installed .git/hooks/pre-commit",
        "refreshed CLAUDE.md",
        "refreshed docs/prd/orders/README.md",
        "refreshed docs/prd/README.md",
    ]), r1
    after_1 = {}
    for rel in _BLOCK_FILES:
        assert (tmp / rel).is_file(), rel
        after_1[rel] = (tmp / rel).read_bytes()
    r2 = run(tmp, tmp, INSTALL)
    assert r2.exit == 0, r2
    assert "refreshed " not in r2.stdout, r2
    for rel in _BLOCK_FILES:
        assert (tmp / rel).read_bytes() == after_1[rel], rel


_BROKEN = "<!-- prd-toolkit:start -->\n<!-- prd-toolkit:start -->\n<!-- prd-toolkit:end -->\n"


def _broken_setup(tmp):
    N0E(tmp)
    write(tmp / "CLAUDE.md", _BROKEN)


@given(_broken_setup)
def test_install_refuses_a_broken_marker(built):
    """@prd T-104.2"""
    tmp = built
    r = run(tmp, tmp, INSTALL)
    assert r.exit == 1, r
    assert r.stdout == "", r
    assert ("prd_hooks: install refused: CLAUDE.md: more than one prd-toolkit block; fix the marker, "
            "then run prd_block.py docs/prd/orders") in r.stderr.splitlines(), r
    for rel in (".prd-toolkit", ".gitignore", "docs/prd/orders/README.md",
                ".git/hooks/commit-msg", ".git/hooks/pre-commit"):
        assert not (tmp / rel).exists(), rel
    assert (tmp / "CLAUDE.md").read_bytes() == _BROKEN.encode("utf-8")
