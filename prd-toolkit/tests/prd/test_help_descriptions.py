"""Every lint rule carries a description, which only the help command prints (FR-038)."""
from help_support import LINT, json_doc, keys_at, m1, run, s0

ORDERS_FINDING = ("docs/prd/orders/contracts/errors.yaml:41: contracts-valid: duplicate key 'FORBIDDEN' "
                  "(first at line 25, again at line 41)\n")


def test_rules_match_list_rules(tmp_path):
    """@prd T-038.1"""
    run_1 = run(["--json"], tmp_path)
    run_2 = run(["--list-rules"], tmp_path, script=LINT)
    for r in (run_1, run_2):
        assert r.exit == 0
        assert r.stderr == ""
    rules = json_doc(run_1)["rules"]

    split = []
    for line in run_2.stdout_lines:
        parts = line.split(" ")
        assert len(parts) == 2, f"--list-rules line has not exactly one space: {line!r}"
        split.append(parts)
    assert [name for name, _ in split] == list(rules.keys())
    for name, severity in split:
        assert rules[name]["severity"] == severity, f"{name}: {rules[name]['severity']!r} != {severity!r}"

    for name, rule in rules.items():
        description = rule["description"]
        assert isinstance(description, str) and len(description) >= 1, f"{name}: description {description!r}"
        assert "\n" not in description and "\r" not in description, f"{name}: description {description!r}"


def test_lint_prints_no_description(tmp_path, monkeypatch):
    """@prd T-038.2"""
    root = s0(tmp_path, monkeypatch)
    m1(root)
    run_1 = run(["--json"], tmp_path)
    run_2 = run(["--list-rules"], tmp_path, script=LINT)
    run_3 = run(["docs/prd/orders"], tmp_path, script=LINT)
    run_4 = run(["--json", "docs/prd/orders"], tmp_path, script=LINT)

    assert run_1.exit == 0
    assert run_2.exit == 0
    assert run_3.exit == 1
    assert run_3.stdout == ORDERS_FINDING
    assert run_4.exit == 1
    doc_4 = json_doc(run_4)
    assert keys_at(doc_4, "findings.0") == ["file", "line", "rule", "severity", "message"]

    rules = json_doc(run_1)["rules"]
    messages = [f["message"] for f in doc_4["findings"]]
    for name, rule in rules.items():
        description = rule["description"]
        if description == "":  # a description that is the empty string is not compared
            continue
        assert description not in run_2.stdout, f"{name}'s description is in --list-rules"
        assert description not in run_3.stdout, f"{name}'s description is in the finding lines"
        for message in messages:
            assert description not in message, f"{name}'s description is in the --json message {message!r}"

    for line in run_2.stdout_lines:
        name, sep, severity = line.partition(" ")
        assert sep == " " and name in rules and severity in ("error", "warn"), \
            f"--list-rules line is not '<rule> error|warn': {line!r}"
