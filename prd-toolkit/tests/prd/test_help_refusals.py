"""What the help command refuses, and how it says so (FR-036)."""
from help_support import json_doc, json_equal, run, write_lines

USAGE = "usage: prd_help.py [-h] [--key KEY | --rule RULE] [--json] [--interface]\n"


def test_unknown_key_or_rule(tmp_path):
    """@prd T-036.1"""
    run_1 = run(["--key", "block.nothing"], tmp_path, catalogue=True)
    assert run_1.exit == 2
    assert run_1.stdout == ""
    assert run_1.stderr == "prd_help: no entry 'block.nothing'\n"

    run_2 = run(["--rule", "no-such-rule"], tmp_path, catalogue=True)
    assert run_2.exit == 2
    assert run_2.stdout == ""
    assert run_2.stderr == "prd_help: no rule 'no-such-rule'\n"


def test_usage_errors(tmp_path):
    """@prd T-036.2"""
    case_env = {"COLUMNS": "40"}
    run_1 = run(["--key", "block.ac", "--rule", "ac-ears"], tmp_path, catalogue=True, case_env=case_env)
    run_2 = run(["--bogus"], tmp_path, catalogue=True, case_env=case_env)
    run_3 = run(["extra"], tmp_path, catalogue=True, case_env=case_env)
    for r in (run_1, run_2, run_3):
        assert r.exit == 2
        assert r.stdout == ""
    assert run_1.stderr == USAGE + "prd_help.py: error: argument --rule: not allowed with argument --key\n"
    assert run_2.stderr == USAGE + "prd_help.py: error: unrecognized arguments: --bogus\n"
    assert run_3.stderr == USAGE + "prd_help.py: error: unrecognized arguments: extra\n"


def test_catalogue_that_cannot_be_used(tmp_path):
    """@prd T-036.3"""
    t = tmp_path
    (t / "b2.yaml").write_bytes(b"key: a.b\n")
    write_lines(t / "b3.yaml", ["- key: a.b", "  name: A", "  what: W"])
    write_lines(t / "b4.yaml", ["- key: a.b", "  name: A", "  what: W", "  why: Y",
                                "- key: a.b", "  name: B", "  what: W", "  why: Y"])
    write_lines(t / "b5.yaml", ["- key: a.b", "  name: A", "  what: W", "  why: Y",
                                "  checked_by: [ac-ears, no-such-rule]"])
    write_lines(t / "b6.yaml", ["- ["])
    write_lines(t / "b7.yaml", ["- just text"])
    write_lines(t / "b8.yaml", ["- key: a.b", "  name: A", "  what: W", "  why: Y", "  rules: one rule"])
    write_lines(t / "b9.yaml", ["- key: a.b", "  name: A", "  what: W", "  why: Y", "  see: [a, b]"])
    write_lines(t / "b10.yaml", ["- key: a.b", '  name: ""', "  what: W", "  why: Y"])

    def help_with(name, *args):
        return run(list(args), t, env={"PRD_HELP_FILE": f"{t}/{name}"})

    runs = [
        help_with("b1.yaml"),                       # the file does not exist
        help_with("b2.yaml"),
        help_with("b3.yaml", "--key", "a.b"),
        help_with("b4.yaml", "--rule", "ac-ears"),
        help_with("b5.yaml"),
        help_with("b6.yaml"),
        help_with("b7.yaml"),
        help_with("b8.yaml"),
        help_with("b9.yaml"),
        help_with("b10.yaml", "--key", "nothing"),  # the catalogue wins over the unknown key
    ]
    for r in runs:
        assert r.exit == 2
        assert r.stdout == ""
        assert "Traceback" not in r.stderr

    assert runs[0].stderr == f"prd_help: {t}/b1.yaml: no such file\n"
    assert runs[1].stderr == f"prd_help: {t}/b2.yaml: top level must be a list\n"
    assert runs[2].stderr == f"prd_help: {t}/b3.yaml: entry 1: missing 'why'\n"
    assert runs[3].stderr == f"prd_help: {t}/b4.yaml: entry 2: duplicate key 'a.b'\n"
    assert runs[4].stderr == f"prd_help: {t}/b5.yaml: entry 1: checked_by names no rule 'no-such-rule'\n"
    run_6_lines = runs[5].stderr_lines
    assert len(run_6_lines) == 1, runs[5].stderr
    assert run_6_lines[0].startswith(f"prd_help: {t}/b6.yaml: YAML parse error: "), runs[5].stderr
    assert runs[6].stderr == f"prd_help: {t}/b7.yaml: entry 1: must be a mapping\n"
    assert runs[7].stderr == f"prd_help: {t}/b8.yaml: entry 1: 'rules' must be a list of strings\n"
    assert runs[8].stderr == f"prd_help: {t}/b9.yaml: entry 1: 'see' must be a string\n"
    assert runs[9].stderr == f"prd_help: {t}/b10.yaml: entry 1: missing 'name'\n"


def test_json_refusals(tmp_path):
    """@prd T-036.4"""
    t = tmp_path
    (t / "b2.yaml").write_bytes(b"key: a.b\n")
    run_1 = run(["--json", "--key", "block.nothing"], t, catalogue=True)
    run_2 = run(["--json", "--rule", "no-such-rule"], t, catalogue=True)
    run_3 = run(["--json", "--bogus"], t, catalogue=True)
    run_4 = run(["--json"], t, catalogue=True, env={"PRD_HELP_FILE": f"{t}/b2.yaml"})
    for r in (run_1, run_2, run_3, run_4):
        assert r.exit == 2

    assert json_equal(json_doc(run_1), {"interface": 1, "kind": "help", "error": "no entry 'block.nothing'"})
    assert run_1.stderr == "prd_help: no entry 'block.nothing'\n"

    assert json_equal(json_doc(run_2), {"interface": 1, "kind": "help", "error": "no rule 'no-such-rule'"})
    assert run_2.stderr == "prd_help: no rule 'no-such-rule'\n"

    assert json_equal(json_doc(run_3), {"interface": 1, "kind": "help", "error": "unrecognized arguments: --bogus"})
    assert run_3.stderr_lines, run_3.stderr
    assert run_3.stderr_lines[0].startswith("usage: prd_help.py"), run_3.stderr
    assert run_3.stderr_lines[-1] == "prd_help.py: error: unrecognized arguments: --bogus"

    assert json_equal(json_doc(run_4), {"interface": 1, "kind": "help",
                                        "error": f"{t}/b2.yaml: top level must be a list"})
    assert run_4.stderr == f"prd_help: {t}/b2.yaml: top level must be a list\n"


def test_unsupported_interface(tmp_path):
    """@prd T-036.5"""
    # the file does not exist, and is not read
    r = run(["--json=2"], tmp_path, env={"PRD_HELP_FILE": str(tmp_path / "missing.yaml")})
    assert r.exit == 2
    assert json_equal(json_doc(r), {"interface": 1, "kind": "help",
                                    "error": "unsupported interface 2; this toolkit speaks 1"})
    assert r.stderr == "prd_help: unsupported interface 2; this toolkit speaks 1\n"
