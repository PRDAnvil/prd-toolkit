"""card-context: write an entry's URL with prd error (FR-064), from docs/prd/prd-toolkit/test-cases/card-context.yaml."""
import itertools

from card_context_support import given_steps, orders, run, scratch, status_next_files, today  # noqa: F401

REFUSED_URL = "refused: URL: must start with http:// or https:// and hold no white space\n"


def _errors_md(tmp) -> str:
    return (orders(tmp) / "errors.md").read_bytes().decode("utf-8")


def _proposed_with_url(url: str) -> str:
    """files.errors_proposed (status-next/files) with `URL: <url>` directly after its line `Touches: FR-003`."""
    lines = status_next_files("errors_proposed").split("\n")
    lines.insert(lines.index("Touches: FR-003") + 1, f"URL: {url}")
    return "\n".join(lines)


@given_steps("N0")
def test_new_with_url(scratch):
    """@prd T-064.1"""
    folder = orders(scratch)
    d0 = today()
    r1 = run(folder, "ERROR", "new", ".", "--title", "A page shows the wrong total", "--source", "a reader",
             "--touches", "FR-006", "--url", "https://example.com/reports/2026-10")
    d1 = today()
    assert r1.exit == 0, r1
    assert r1.stdout == "E-001\n"
    assert r1.stderr == ""

    d2 = today()
    r2 = run(folder, "ERROR", "new", ".", "--title", "The report page is slow", "--source", "a reader",
             "--url", "https://example.com/reports/slow")
    d3 = today()
    assert r2.exit == 0, r2
    assert r2.stdout == "E-002\n"
    assert r2.stderr == ""

    def expected(first, second):
        return [
            "# Error ledger",
            "",
            "### E-001 A page shows the wrong total",
            f"Detected: {first.isoformat()}, a reader",
            "Classification: unclassified",
            "Touches: FR-006",
            "URL: https://example.com/reports/2026-10",
            "Diagnosis: -",
            "Resolution: -",
            "Recurrence of: -",
            "",
            "### E-002 The report page is slow",
            f"Detected: {second.isoformat()}, a reader",
            "Classification: unclassified",
            "URL: https://example.com/reports/slow",
            "Diagnosis: -",
            "Resolution: -",
            "Recurrence of: -",
        ]

    got = _errors_md(scratch).splitlines()
    candidates = [expected(a, b) for a, b in itertools.product({d0, d1}, {d2, d3})]
    assert got in candidates, f"errors.md lines:\n{got}\nexpected one of:\n{candidates}"


@given_steps("N0", "NE2")
def test_url_sets_and_replaces(scratch):
    """@prd T-064.2"""
    folder = orders(scratch)

    r1 = run(folder, "ERROR", "url", ".", "E-001", "https://example.com/runs/1001")
    assert r1.exit == 0, r1
    assert r1.stdout == "E-001 proposed code bug\n"
    assert r1.stderr == ""
    assert _errors_md(scratch) == _proposed_with_url("https://example.com/runs/1001")

    r2 = run(folder, "ERROR", "url", ".", "E-001", "https://example.com/runs/1002")
    assert r2.exit == 0, r2
    assert r2.stdout == "E-001 proposed code bug\n"
    assert r2.stderr == ""
    text = _errors_md(scratch)
    assert text == _proposed_with_url("https://example.com/runs/1002")
    assert [line for line in text.splitlines() if line.startswith("URL:")] == ["URL: https://example.com/runs/1002"]


@given_steps("N0", "NE2")
def test_url_dash_removes(scratch):
    """@prd T-064.3"""
    folder = orders(scratch)
    proposed = status_next_files("errors_proposed")
    runs = [
        ("E-001", "https://example.com/runs/1001"),
        ("E-001", "-"),
        ("E-001", "-"),
    ]
    for n, (eid, address) in enumerate(runs, start=1):
        r = run(folder, "ERROR", "url", ".", eid, address)
        assert r.exit == 0, (n, r)
        assert r.stdout == "E-001 proposed code bug\n", n
        assert r.stderr == "", n
        if n in (2, 3):
            assert _errors_md(scratch) == proposed, f"after run_{n}, errors.md is not files.errors_proposed"


@given_steps("N0", "NE2")
def test_refusals(scratch):
    """@prd T-064.4"""
    folder = orders(scratch)
    proposed = status_next_files("errors_proposed")
    runs = [
        (["url", ".", "E-001", "ftp://example.com/runs/1"], REFUSED_URL),
        (["url", ".", "E-009", "https://example.com/runs/9"], "refused: E-009 is not an entry\n"),
        (["new", ".", "--title", "A total is wrong", "--source", "a reader", "--url", "https://example.com/a b"],
         REFUSED_URL),
    ]
    for n, (args, stderr) in enumerate(runs, start=1):
        r = run(folder, "ERROR", *args)
        assert r.exit == 1, (n, r)
        assert r.stdout == "", n
        assert r.stderr == stderr, (n, r.stderr)
        assert _errors_md(scratch) == proposed, f"after run_{n}, errors.md is not files.errors_proposed"
