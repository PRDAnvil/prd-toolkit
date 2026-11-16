"""The catalogue the help command reads (FR-037), and a vendored copy's answer (FR-039)."""
import yaml

from help_support import (  # noqa: F401  (vendored_fixture registers the fixture `vendored`)
    CLI_YAML, SHIPPED, assert_json_at, json_doc, run, vendored_fixture, write_lines,
)


def test_catalogue_from_setting(tmp_path):
    """@prd T-037.1"""
    write_lines(tmp_path / "one.yaml", ["- key: a.b", "  name: Only entry", "  what: W", "  why: Y"])
    r = run(["--json"], tmp_path, env={"PRD_HELP_FILE": f"{tmp_path}/one.yaml"})
    assert r.exit == 0
    assert r.stderr == ""
    assert_json_at(json_doc(r), {"entries": [{"key": "a.b", "name": "Only entry", "what": "W", "why": "Y"}]})


def test_shipped_catalogue_when_unset_or_empty(tmp_path):
    """@prd T-037.2"""
    run_1 = run(["--json"], tmp_path)                                # PRD_HELP_FILE unset
    run_2 = run(["--json"], tmp_path, env={"PRD_HELP_FILE": ""})     # PRD_HELP_FILE empty
    for r in (run_1, run_2):
        assert r.exit == 0
        assert r.stderr == ""
    assert run_1.stdout_bytes == run_2.stdout_bytes
    # the shipped catalogue, not the fixture, which has none
    assert any(e.get("key") == "kind.UJ" for e in json_doc(run_1)["entries"])


def test_shipped_catalogue_covers_the_keys(tmp_path):
    """@prd T-037.3"""
    r = run(["--json"], tmp_path)  # PRD_HELP_FILE unset: the shipped catalogue
    assert r.exit == 0
    assert r.stderr == ""
    entries = json_doc(r)["entries"]
    keys = [e["key"] for e in entries]

    listed = yaml.safe_load(CLI_YAML.read_text(encoding="utf-8"))["prd_help"]["keys"]
    missing = [k for k in listed if k not in keys]
    assert missing == [], f"cli.yaml prd_help.keys with no entry: {missing}"

    assert len(keys) == len(set(keys)), f"duplicate keys: {sorted(k for k in set(keys) if keys.count(k) > 1)}"

    names = {e["key"]: e["name"] for e in entries}
    kinds = ["kind.UJ", "kind.FR", "kind.NFR", "kind.T", "kind.E", "kind.CS"]
    assert [names.get(k) for k in kinds] == [
        "User journey", "Requirement", "Quality requirement", "Test case", "Error", "Change set",
    ]


def test_shipped_catalogue_covers_practices(tmp_path):
    """@prd T-037.4"""
    run_1 = run(["--json"], tmp_path)                 # PRD_HELP_FILE unset: the shipped catalogue
    run_2 = run(["--rule", "practices"], tmp_path)
    for r in (run_1, run_2):
        assert r.exit == 0
        assert r.stderr == ""

    entries = json_doc(run_1)["entries"]
    by_key = {}
    for e in entries:
        by_key.setdefault(e["key"], e)

    assert "kind.S" in by_key, "no entry with the key kind.S"
    assert by_key["kind.S"]["name"] == "Source"
    assert "kind.P" in by_key, "no entry with the key kind.P"
    assert by_key["kind.P"]["name"] == "Practice"

    for key in ("file.practices", "table.sources", "table.practices"):
        assert key in by_key, f"no entry with the key {key}"

    five = ["kind.S", "kind.P", "file.practices", "table.sources", "table.practices"]
    for key in five:
        checked_by = by_key[key].get("checked_by")
        assert isinstance(checked_by, list), f"{key}: checked_by is {checked_by!r}, not a list"
        assert "practices" in checked_by, f"{key}: checked_by {checked_by!r} does not hold practices"

    lines = run_2.stdout_lines
    assert lines, "run_2 printed no stdout line"
    assert lines[0] == "practices (error)"
    last = lines[-1]
    assert last.startswith("Checks: "), f"last line {last!r} does not start with 'Checks: '"
    named = last[len("Checks: "):].split(", ")
    missing = [k for k in five if k not in named]
    assert missing == [], f"Checks line {last!r} does not name {missing}"


def test_vendored_copy_answers_the_same(tmp_path, vendored):
    """@prd T-039.1"""
    run_1 = run(["--json"], tmp_path, script=vendored / "prd_help.py")
    run_2 = run(["--json"], tmp_path)
    for r in (run_1, run_2):
        assert r.exit == 0
        assert r.stderr == ""
    assert run_1.stdout_bytes == run_2.stdout_bytes
    copied = vendored / "help.yaml"
    assert copied.is_file(), f"{copied} does not exist"
    assert copied.read_bytes() == SHIPPED.read_bytes()
