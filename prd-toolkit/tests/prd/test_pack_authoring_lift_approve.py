"""pack-authoring: approving a lift commits the vendored pack (AC-060.9; test-cases/pack-authoring.yaml)."""
from pack_authoring_support import CHANGE, HOOKS, KI, KW, K0, git, run

PRD = "docs/prd/north"
VENDORED = [
    ".prd-toolkit/pack-sources.json",
    ".prd-toolkit/packs/leaflet/README.md",
    ".prd-toolkit/packs/leaflet/pack.yaml",
    ".prd-toolkit/packs/leaflet/samples/pages/bad.yaml",
    ".prd-toolkit/packs/leaflet/samples/routes/bad.yaml",
]
APPROVED = "approved north 1.0.1 "


def test_approving_a_lift_commits_the_vendored_pack(tmp_path, monkeypatch):
    """@prd T-060.13"""
    K0(tmp_path, monkeypatch)
    KI(tmp_path)
    repo = tmp_path / "north"
    r1 = run(CHANGE, "pack", PRD, "leaflet", "0.1.0", "--lift", cwd=repo)
    r2 = run(HOOKS, "install", PRD, cwd=repo)
    KW(tmp_path)
    r3 = run(CHANGE, "approve", PRD, "--reply", "yes", "--dry-run", "no dry run (pack lifted)", cwd=repo)
    for i, r in enumerate((r1, r2, r3), 1):
        assert r.code == 0, f"run_{i}: {r.stdout}{r.stderr}"

    # run_3: stdout_exact_lines ["approved north 1.0.1 <sha>"], <sha> 7 or more characters HEAD starts with.
    head = git(repo, "rev-parse", "HEAD").splitlines()[0]
    assert len(r3.lines) == 1, r3.stdout
    line = r3.lines[0]
    assert line.startswith(APPROVED), r3.stdout
    sha = line[len(APPROVED):]
    assert len(sha) >= 7 and head.startswith(sha), f"{line!r}: <sha> is not 7 or more leading characters of {head}"

    # The approval commit holds exactly the five vendored paths under .prd-toolkit/.
    shown = git(repo, "show", "--no-color", "--name-only", "--format=", "HEAD").splitlines()
    assert sorted(p for p in shown if p.startswith(".prd-toolkit/")) == sorted(VENDORED), shown

    # None of them is left uncommitted, and the launcher stays untracked.
    porcelain = git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert [p for p in porcelain if any(p.endswith(v) for v in VENDORED)] == [], porcelain
    assert "?? .prd-toolkit/prd" in porcelain, porcelain
