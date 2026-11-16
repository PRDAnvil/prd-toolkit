"""pack-authoring: `prd_pack.py check` (FR-059; test-cases/pack-authoring.yaml)."""
from pack_authoring_support import KP1, KP2, KP3, KP4, KP5, KP6, KP8, K0, PACK, one_json, run

CHECK = ("check", "plug/prd-packs/leaflet", "north/docs/prd/north", "south/docs/prd/south")
CHECK_JSON = ("check", "--json", "plug/prd-packs/leaflet", "north/docs/prd/north", "south/docs/prd/south")


def test_check_manifest_refused(tmp_path, monkeypatch):
    """@prd T-059.1"""
    K0(tmp_path, monkeypatch)
    KP4(tmp_path)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 1, r.stderr
    assert r.stderr == ""
    assert r.lines == ["plug/prd-packs/leaflet/pack.yaml: pack leaflet: pack.yaml: unknown key colour"]


def test_check_validators_on_both_prds(tmp_path, monkeypatch):
    """@prd T-059.2"""
    K0(tmp_path, monkeypatch)
    KP5(tmp_path)
    KP6(tmp_path)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 1, r.stderr
    assert r.stderr == ""
    assert r.lines == [
        "south/docs/prd/south/prd.md: contract type pages: glob matches no file",
        "north/docs/prd/north/prd.md: contract type routes: validator failed: exit 1",
    ]


def test_check_no_bad_sample(tmp_path, monkeypatch):
    """@prd T-059.3"""
    K0(tmp_path, monkeypatch)
    KP1(tmp_path)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 1, r.stderr
    assert r.stderr == ""
    assert r.lines == ["plug/prd-packs/leaflet/samples/routes: no bad.* sample; add a file the validator must refuse"]


def test_check_sample_accepted(tmp_path, monkeypatch):
    """@prd T-059.4"""
    K0(tmp_path, monkeypatch)
    KP2(tmp_path)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 1, r.stderr
    assert r.stderr == ""
    assert r.lines == ["plug/prd-packs/leaflet/samples/pages/bad.yaml: the validator accepts it; a sample must be refused"]


def test_check_level_command_not_on_path(tmp_path, monkeypatch):
    """@prd T-059.5"""
    K0(tmp_path, monkeypatch)
    KP3(tmp_path)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 1, r.stderr
    assert r.stderr == ""
    assert r.lines == ["plug/prd-packs/leaflet/pack.yaml: levels[0] (unit): no-such-runner is not on PATH"]


def test_check_clean_pack(tmp_path, monkeypatch):
    """@prd T-059.6"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 0, r.stdout + r.stderr
    assert r.stdout == ""
    assert r.stderr == ""


def test_check_json(tmp_path, monkeypatch):
    """@prd T-059.7"""
    K0(tmp_path, monkeypatch)
    r1 = run(PACK, *CHECK_JSON, cwd=tmp_path)
    KP1(tmp_path)
    r2 = run(PACK, *CHECK_JSON, cwd=tmp_path)
    assert r1.code == 0, r1.stdout + r1.stderr
    assert r1.stderr == ""
    assert one_json(r1.stdout) == {"interface": 1, "kind": "pack.check", "findings": []}
    assert r2.code == 1, r2.stderr
    assert r2.stderr == ""
    assert one_json(r2.stdout) == {
        "interface": 1,
        "kind": "pack.check",
        "findings": [
            {"file": "plug/prd-packs/leaflet/samples/routes",
             "message": "no bad.* sample; add a file the validator must refuse"},
        ],
    }


def test_check_validator_fails_from_pack_folder(tmp_path, monkeypatch):
    """@prd T-059.8"""
    K0(tmp_path, monkeypatch)
    KP8(tmp_path)
    r = run(PACK, *CHECK, cwd=tmp_path)
    assert r.code == 1, r.stdout + r.stderr
    assert r.stderr == ""
    assert r.lines == [
        "north/docs/prd/north/prd.md: contract type pages: validator fails from the pack folder: "
        "Traceback (most recent call last):",
        "south/docs/prd/south/prd.md: contract type pages: validator fails from the pack folder: "
        "Traceback (most recent call last):",
    ]
