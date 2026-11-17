"""pack-authoring: `prd_pack.py compare --json`, its refusals and the interface (FR-058; test-cases/pack-authoring.yaml)."""
from pack_authoring_support import (
    KN, KZ, K0, PACK, assert_json_at, assert_json_keys_at, one_json, part_lines, run,
)

A = "north/docs/prd/north"
B = "south/docs/prd/south"

# The part keys of AC-058.1, each with its title in the text (AC-057.1) and its line (AC-057.2 to AC-057.8).
PARTS = {
    "contract-types": ("Contract types", lambda e: f"{e['mark']} {e['type']}: {e['files']}; {e['validator']}"),
    "target-kinds": ("Target kinds", lambda e: f"{e['mark']} {e['type']}: {e['a']} in A, {e['b']} in B"),
    "levels": ("Levels", lambda e: (f"{e['mark']} {e['level']}: {e['command']}; environment {e['environment']}; "
                                    f"gate {e['gate']}; timeout {e['timeout']}")),
    "harness": ("Harness", lambda e: f"{e['mark']} {e['slot']}: {e['text']}"),
    "standards": ("Standards", lambda e: f"{e['mark']} {e['glob']}: {e['linter']}"),
    "skills": ("Skills", lambda e: f"{e['mark']} {e['activity']}: {e['skill']}"),
    "vocabulary": ("Vocabulary", lambda e: f"{e['mark']} {e['word']}: {e['a']} in A, {e['b']} in B"),
}


def _dash(entry: dict) -> dict:
    """A value the line prints as `-` is null in the JSON (AC-058.1)."""
    return {k: ("-" if v is None else v) for k, v in entry.items()}


def test_compare_json(tmp_path, monkeypatch):
    """@prd T-058.1"""
    K0(tmp_path, monkeypatch)
    r = run(PACK, "compare", "--json", A, B, cwd=tmp_path)
    assert r.code == 0, r.stderr
    assert r.stderr == ""
    assert_json_keys_at(r.stdout, {
        "": ["interface", "kind", "a", "b", "parts"],
        "parts": ["contract-types", "target-kinds", "levels", "harness", "standards", "skills", "vocabulary"],
        "parts.contract-types.0": ["mark", "type", "files", "validator"],
        "parts.target-kinds.0": ["mark", "type", "a", "b"],
        "parts.levels.0": ["mark", "level", "command", "environment", "gate", "timeout"],
        "parts.harness.0": ["mark", "slot", "text"],
        "parts.standards.0": ["mark", "glob", "linter"],
        "parts.skills.0": ["mark", "activity", "skill"],
        "parts.vocabulary.0": ["mark", "word", "a", "b"],
    })
    assert_json_at(r.stdout, {
        "interface": 1,
        "kind": "pack.compare",
        "a": "north/docs/prd/north",
        "b": "south/docs/prd/south",
        "parts.contract-types.2.mark": "A",
        "parts.contract-types.2.type": "forms",
        "parts.contract-types.2.files": "contracts/forms.yaml",
        "parts.target-kinds.0": {"mark": "both", "type": "pages", "a": 2, "b": 1},
        "parts.target-kinds.3": {"mark": "B", "type": "feeds", "a": 0, "b": 1},
        "parts.levels.0": {"mark": "both", "level": "unit", "command": "python3 -m pytest tests/unit",
                           "environment": "local", "gate": "build", "timeout": None},
        "parts.levels.2": {"mark": "B", "level": "integration", "command": "python3 -m pytest tests/site",
                           "environment": "local", "gate": "build", "timeout": None},
        "parts.harness.4": {"mark": "B", "slot": "Tools on the runner",
                            "text": "python3 and a headless browser on PATH; `tests/` sits at the repository root."},
        "parts.standards": [{"mark": "both", "glob": "site/**/*.html", "linter": "python3 tools/check_html.py"}],
        "parts.skills": [{"mark": "both", "activity": "a change to a page", "skill": "code-review"}],
        "parts.vocabulary.0": {"mark": "both", "word": "page", "a": 6, "b": 5},
    })
    # relations: each list of `parts` has one entry per line of the matching part of the text, in order,
    # and an entry's values are the ones that line prints.
    text = run(PACK, "compare", A, B, cwd=tmp_path)
    assert text.code == 0, text.stderr
    doc = one_json(r.stdout)
    for key, (title, line_of) in PARTS.items():
        lines = part_lines(text.stdout, title)[1:]
        if lines and lines[-1] == "":
            lines = lines[:-1]
        if lines == ["None."]:
            lines = []
        assert [line_of(_dash(e)) for e in doc["parts"][key]] == lines, key


def test_compare_shares_no_type(tmp_path, monkeypatch):
    """@prd T-058.2"""
    K0(tmp_path, monkeypatch)
    KN(tmp_path)
    message = ("north/docs/prd/north and south/docs/prd/south share no custom contract type; "
               "there is no pack to write")
    r1 = run(PACK, "compare", A, B, cwd=tmp_path)
    r2 = run(PACK, "compare", "--json", A, B, cwd=tmp_path)
    for r in (r1, r2):
        assert r.code == 1, r.stderr
        assert r.stderr == "prd_pack: " + message + "\n"
    assert r1.stdout == ""
    assert one_json(r2.stdout) == {"interface": 1, "kind": "pack.compare", "error": message}


def test_compare_one_side_has_no_custom_type(tmp_path, monkeypatch):
    """@prd T-058.3"""
    K0(tmp_path, monkeypatch)
    KZ(tmp_path)
    r1 = run(PACK, "compare", A, B, cwd=tmp_path)
    r2 = run(PACK, "compare", "--json", B, A, cwd=tmp_path)
    assert r1.code == 1, r1.stderr
    assert r2.code == 1, r2.stderr
    assert r1.stdout == ""
    assert r1.stderr == ("prd_pack: north/docs/prd/north and south/docs/prd/south share no custom contract type; "
                         "there is no pack to write\n")
    assert r2.stderr == ("prd_pack: south/docs/prd/south and north/docs/prd/north share no custom contract type; "
                         "there is no pack to write\n")
    assert one_json(r2.stdout) == {
        "interface": 1,
        "kind": "pack.compare",
        "error": ("south/docs/prd/south and north/docs/prd/north share no custom contract type; "
                  "there is no pack to write"),
    }


def test_missing_folder_and_usage(tmp_path, monkeypatch):
    """@prd T-058.4"""
    K0(tmp_path, monkeypatch)
    nowhere = f"{tmp_path.resolve()}/nowhere"
    runs = [
        run(PACK, "compare", A, "nowhere", cwd=tmp_path),
        run(PACK, "compare", "--json", A, "nowhere", cwd=tmp_path),
        run(PACK, "check", "plug/prd-packs/leaflet", A, "nowhere", cwd=tmp_path),
        run(PACK, "compare", A, cwd=tmp_path),
        run(PACK, cwd=tmp_path),
    ]
    for r in runs:
        assert r.code == 2, r.stderr
    r1, r2, r3, r4, r5 = runs
    assert r1.stdout == ""
    assert r1.stderr == f"prd_pack: {nowhere}: no prd.md\n"
    assert r2.stderr == f"prd_pack: {nowhere}: no prd.md\n"
    assert one_json(r2.stdout) == {"interface": 1, "kind": "pack.compare", "error": f"{nowhere}: no prd.md"}
    assert r3.stdout == ""
    assert r3.stderr == f"prd_pack: {nowhere}: no prd.md\n"
    assert r4.stdout == ""
    assert r4.stderr.splitlines()[0].startswith("usage: prd_pack.py"), r4.stderr
    assert "error: " in r4.stderr
    assert "Traceback" not in r4.stderr
    assert r5.stdout == ""
    assert r5.stderr.splitlines()[0].startswith("usage: prd_pack.py"), r5.stderr
    assert "Traceback" not in r5.stderr


def test_interface(tmp_path, monkeypatch):
    """@prd T-058.5"""
    K0(tmp_path, monkeypatch)
    r1 = run(PACK, "--interface", cwd=tmp_path)
    r2 = run(PACK, "compare", "--json=2", A, B, cwd=tmp_path)
    r3 = run(PACK, "compare", "--json=1", A, B, cwd=tmp_path)
    assert r1.code == 0, r1.stderr
    assert r1.stdout == "1\n"
    assert r1.stderr == ""
    assert r2.code == 2, r2.stderr
    assert one_json(r2.stdout) == {"interface": 1, "kind": "pack.compare",
                                   "error": "unsupported interface 2; this toolkit speaks 1"}
    assert r2.stderr == "prd_pack: unsupported interface 2; this toolkit speaks 1\n"
    assert r3.code == 0, r3.stderr
    assert r3.stderr == ""
    # relations: run_3's stdout equals that of `compare --json` in the same state, byte for byte.
    plain = run(PACK, "compare", "--json", A, B, cwd=tmp_path)
    assert r3.stdout == plain.stdout
