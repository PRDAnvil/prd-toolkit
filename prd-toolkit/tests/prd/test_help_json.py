"""The help command's JSON document and its interface number (FR-035)."""
from help_support import RULES, assert_json_at, json_doc, json_equal, keys_at, run


def test_json_document(tmp_path):
    """@prd T-035.1"""
    r = run(["--json"], tmp_path, catalogue=True)
    assert r.exit == 0
    assert r.stderr == ""
    doc = json_doc(r)
    assert keys_at(doc, "") == ["interface", "kind", "entries", "rules"]
    assert keys_at(doc, "entries.0") == ["key", "name", "what", "why", "rules", "checked_by", "see"]
    assert keys_at(doc, "entries.1") == ["key", "name", "what", "why"]
    assert keys_at(doc, "entries.2") == ["key", "name", "what", "why", "checked_by"]
    assert keys_at(doc, "rules.ac-ears") == ["severity", "description"]
    assert_json_at(doc, {
        "interface": 1,
        "kind": "help",
        "entries": [
            {
                "key": "block.ac",
                "name": "Acceptance criterion",
                "what": "One testable statement of what the system does.",
                "why": "Each criterion gets a test case.",
                "rules": ["`- AC-nnn.n <text>`, where nnn is the requirement's number.",
                          "The text starts with an EARS opener."],
                "checked_by": ["ac-ears", "platform-word"],
                "see": "Requirement blocks",
            },
            {"key": "kind.FR", "name": "Requirement", "what": "One thing the system does.",
             "why": "A build is verified against it."},
            {"key": "marker.assumption", "name": "Assumption marker",
             "what": "A guess the author made — written where it applies.",
             "why": "An open assumption blocks approval.", "checked_by": ["ac-ears"]},
        ],
        "rules.ac-ears.severity": "error",
        "rules.platform-word.severity": "warn",
    })
    # The dash as itself, in UTF-8 (the bytes e2 80 94), never as a \u escape.
    assert "made — written" in r.stdout
    assert b"made \xe2\x80\x94 written" in r.stdout_bytes
    assert "\\u2014" not in r.stdout
    assert list(doc["rules"].keys()) == RULES


def test_json_with_key_or_rule(tmp_path):
    """@prd T-035.2"""
    run_1 = run(["--json", "--key", "kind.FR"], tmp_path, catalogue=True)
    run_2 = run(["--json", "--rule", "ac-ears"], tmp_path, catalogue=True)
    run_3 = run(["--json", "--rule", "vague-word"], tmp_path, catalogue=True)  # no entry of the fixture names it
    run_4 = run(["--json"], tmp_path, catalogue=True)
    for r in (run_1, run_2, run_3, run_4):
        assert r.exit == 0
        assert r.stderr == ""
    doc_1, doc_2, doc_3, doc_4 = (json_doc(r) for r in (run_1, run_2, run_3, run_4))

    assert_json_at(doc_1, {"entries": [{"key": "kind.FR", "name": "Requirement",
                                        "what": "One thing the system does.",
                                        "why": "A build is verified against it."}]})

    assert keys_at(doc_2, "rules") == ["ac-ears"]
    assert_json_at(doc_2, {"entries.0.key": "block.ac", "entries.1.key": "marker.assumption",
                           "rules.ac-ears.severity": "error"})

    assert keys_at(doc_3, "rules") == ["vague-word"]
    assert_json_at(doc_3, {"entries": []})

    assert json_equal(doc_1["rules"], doc_4["rules"])
    assert len(doc_2["entries"]) == 2
    assert json_equal(doc_2["entries"], [doc_4["entries"][0], doc_4["entries"][2]])
    assert json_equal(doc_2["rules"]["ac-ears"], doc_4["rules"]["ac-ears"])


def test_json_equals_1(tmp_path):
    """@prd T-035.3"""
    run_1 = run(["--json=1"], tmp_path, catalogue=True)
    run_2 = run(["--json"], tmp_path, catalogue=True)
    for r in (run_1, run_2):
        assert r.exit == 0
        assert r.stderr == ""
    assert run_1.stdout_bytes == run_2.stdout_bytes


def test_interface(tmp_path):
    """@prd T-035.4"""
    runs = [
        run(["--interface"], tmp_path),
        run(["--interface", "--json=2"], tmp_path),
        # the file does not exist
        run(["--interface", "--key", "nothing"], tmp_path,
            env={"PRD_HELP_FILE": str(tmp_path / "missing.yaml")}),
    ]
    for r in runs:
        assert r.exit == 0
        assert r.stderr == ""
        assert r.stdout == "1\n"
