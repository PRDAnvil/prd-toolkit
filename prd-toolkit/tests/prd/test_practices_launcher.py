"""FR-053: the launcher and a vendored copy answer the same (test-cases/practices.yaml)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from practices_support import DISPATCH, P0, PRACTICES, check, load_vendored, run, setup  # noqa: E402

ORDERS = "docs/prd/orders"


@pytest.fixture
def vendored_repo(tmp_path):
    """Step P0, then fixture repo/vendored with its check; a failed check ends the test as an error."""
    setup(tmp_path, P0)
    load_vendored(tmp_path)
    return tmp_path


def test_dispatcher_answers_as_the_script(tmp_path):
    """@prd T-053.1"""
    setup(tmp_path, P0)
    r1 = run(tmp_path, DISPATCH, "practices", ORDERS)
    r2 = run(tmp_path, PRACTICES, ORDERS)
    r3 = run(tmp_path, DISPATCH, "practices", "--json", ORDERS, "--paths", "src/a.py")
    r4 = run(tmp_path, PRACTICES, "--json", ORDERS, "--paths", "src/a.py")
    r5 = run(tmp_path, DISPATCH, "practices", "docs/prd/nothing")
    r6 = run(tmp_path, PRACTICES, "docs/prd/nothing")
    for r, code in ((r1, 0), (r2, 0), (r3, 0), (r4, 0), (r5, 2), (r6, 2)):
        check(r, exit=code)
    for a, b in ((r1, r2), (r3, r4), (r5, r6)):
        assert a.stdout_bytes == b.stdout_bytes and a.stderr_bytes == b.stderr_bytes, f"{a!r} != {b!r}"


def test_vendored_copy_answers_as_the_plugin(vendored_repo):
    """@prd T-053.2"""
    tmp = vendored_repo
    vendored = tmp / ".prd-toolkit" / "prd_practices.py"
    r1 = run(tmp, vendored, ORDERS)
    r2 = run(tmp, PRACTICES, ORDERS)
    r3 = run(tmp, vendored, "--json", ORDERS)
    r4 = run(tmp, PRACTICES, "--json", ORDERS)
    for r in (r1, r2, r3, r4):
        check(r, exit=0, stderr="")
    assert r1.stdout_bytes == r2.stdout_bytes, f"{r1!r} != {r2!r}"
    assert r3.stdout_bytes == r4.stdout_bytes, f"{r3!r} != {r4!r}"
