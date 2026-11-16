"""pack-authoring: the launcher and a vendored copy answer as the plugin's prd_pack.py (FR-061; test-cases/pack-authoring.yaml)."""
from pack_authoring_support import DISPATCH, K0, PACK, kvc_fixture, run, vpack  # noqa: F401  (kvc: step KVC)

A = "north/docs/prd/north"
B = "south/docs/prd/south"
CHECK_JSON = ("check", "--json", "plug/prd-packs/leaflet", A, B)


def test_launcher_answers_as_the_script(tmp_path, monkeypatch):
    """@prd T-061.1"""
    K0(tmp_path, monkeypatch)
    r1 = run(DISPATCH, "pack", "compare", A, B, cwd=tmp_path)
    r2 = run(PACK, "compare", A, B, cwd=tmp_path)
    r3 = run(DISPATCH, "pack", *CHECK_JSON, cwd=tmp_path)
    r4 = run(PACK, *CHECK_JSON, cwd=tmp_path)
    r5 = run(DISPATCH, "pack", "compare", A, "nowhere", cwd=tmp_path)
    r6 = run(PACK, "compare", A, "nowhere", cwd=tmp_path)
    for i, (r, code) in enumerate(((r1, 0), (r2, 0), (r3, 0), (r4, 0), (r5, 2), (r6, 2)), 1):
        assert r.code == code, f"run_{i}: exit {r.code}: {r.stderr}"
    assert (r1.stdout, r1.stderr) == (r2.stdout, r2.stderr)
    assert (r3.stdout, r3.stderr) == (r4.stdout, r4.stderr)
    assert (r5.stdout, r5.stderr) == (r6.stdout, r6.stderr)


def test_vendored_copy_answers_as_the_plugin(tmp_path, monkeypatch, kvc):
    """@prd T-061.2"""
    K0(tmp_path, monkeypatch)
    vendored = vpack(tmp_path)
    r1 = run(vendored, "compare", A, B, cwd=tmp_path)
    r2 = run(PACK, "compare", A, B, cwd=tmp_path)
    r3 = run(vendored, "compare", "--json", A, B, cwd=tmp_path)
    r4 = run(PACK, "compare", "--json", A, B, cwd=tmp_path)
    for i, r in enumerate((r1, r2, r3, r4), 1):
        assert r.code == 0, f"run_{i}: exit {r.code}: {r.stderr}"
        assert r.stderr == "", f"run_{i}"
    assert r1.stdout == r2.stdout
    assert r3.stdout == r4.stdout
