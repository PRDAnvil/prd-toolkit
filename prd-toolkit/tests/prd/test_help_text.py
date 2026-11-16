"""The help command's text output: the index (FR-033), one entry and one rule (FR-034)."""
from help_support import json_doc, run


def test_index(tmp_path):
    """@prd T-033.1"""
    r = run([], tmp_path, catalogue=True)
    assert r.exit == 0
    assert r.stderr == ""
    assert r.stdout_lines == [
        "block.ac  Acceptance criterion", "kind.FR  Requirement", "marker.assumption  Assumption marker", "",
        "ac-ears  error", "ac-has-test  error", "assumption-indexed  error", "change-sets  error",
        "classified-fixtures  error", "contracts-valid  error", "deny-tested  error", "drift-rows  error",
        "error-codes  error", "error-entries  error", "fr-has-ac  error", "frontmatter  error",
        "glossary-synonym  error", "id-format  error", "id-removed-reused  error", "id-unique  error",
        "index-consistent  error", "judged-case  error", "language-table  error", "links-format  error",
        "markers-open  error", "nfr-bound  error", "open-questions-empty  error", "pack-resolves  error",
        "placeholder  error", "platform-word  warn", "practices  error", "production-gate  error",
        "registries  error",
        "runbook-env  error", "runbook-steps  error", "runbook-tests  error", "schema-refs  error",
        "sections  error", "snapshot-cited  error", "sufficiency  error", "test-cases-consistent  error",
        "test-level  error", "test-refs  error", "upstream-refs  error", "vague-word  error",
    ]


def test_key_with_every_part(tmp_path):
    """@prd T-034.1"""
    run_1 = run(["--key", "block.ac"], tmp_path, catalogue=True)
    run_2 = run(["--json"], tmp_path, catalogue=True)
    for r in (run_1, run_2):
        assert r.exit == 0
        assert r.stderr == ""
    doc = json_doc(run_2)
    assert run_1.stdout_lines == [
        "Acceptance criterion (block.ac)",
        "What: One testable statement of what the system does.",
        "Why: Each criterion gets a test case.",
        "Rules:",
        "- `- AC-nnn.n <text>`, where nnn is the requirement's number.",
        "- The text starts with an EARS opener.",
        "Checked by:",
        "- ac-ears: " + doc["rules"]["ac-ears"]["description"],
        "- platform-word: " + doc["rules"]["platform-word"]["description"],
        "See: Requirement blocks",
    ]


def test_key_with_no_optional_part(tmp_path):
    """@prd T-034.2"""
    r = run(["--key", "kind.FR"], tmp_path, catalogue=True)
    assert r.exit == 0
    assert r.stderr == ""
    assert r.stdout_lines == [
        "Requirement (kind.FR)",
        "What: One thing the system does.",
        "Why: A build is verified against it.",
    ]


def test_rule(tmp_path):
    """@prd T-034.3"""
    run_1 = run(["--rule", "ac-ears"], tmp_path, catalogue=True)
    run_2 = run(["--rule", "vague-word"], tmp_path, catalogue=True)  # no entry of the fixture names it
    run_3 = run(["--rule", "platform-word"], tmp_path, catalogue=True)
    run_4 = run(["--json"], tmp_path, catalogue=True)
    for r in (run_1, run_2, run_3, run_4):
        assert r.exit == 0
        assert r.stderr == ""
    rules = json_doc(run_4)["rules"]
    assert run_1.stdout_lines == [
        "ac-ears (error)",
        rules["ac-ears"]["description"],
        "Checks: block.ac, marker.assumption",
    ]
    assert run_2.stdout_lines == [
        "vague-word (error)",
        rules["vague-word"]["description"],
    ]
    assert run_3.stdout_lines == [
        "platform-word (warn)",
        rules["platform-word"]["description"],
        "Checks: block.ac",
    ]
