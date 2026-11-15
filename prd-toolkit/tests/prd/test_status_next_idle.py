"""status-next FR-046: nothing waits (test-cases/status-next.yaml)."""
from status_next_support import given_steps, json_lines, next_items_json, next_part_lines, orders, run
from status_next_support import scratch  # noqa: F401  (the pytest fixture the setup steps run in)


@given_steps("N0", "NLV")
def test_idle_item_ends_at_live_when_operations_names_an_environment(scratch):
    """@prd T-046.1"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Nothing waits. Everything approved is live.",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "Nothing waits. Everything approved is live.", "kind": "idle", "ids": [], "area": null, "command": null, "waits_on": null}
""")


@given_steps("N0E")
def test_idle_item_ends_at_verified_when_operations_names_no_environment(scratch):
    """@prd T-046.2"""
    folder = orders(scratch)
    runs = [run(folder, "STATUS", "."), run(folder, "STATUS", "--json", ".")]
    for r in runs:
        assert (r.exit, r.stderr) == (0, ""), r
    assert next_part_lines(runs[0].stdout) == [
        "## Next",
        "",
        "1. Nothing waits. Everything approved is verified.",
        "",
    ]
    assert next_items_json(runs[1].stdout) == json_lines(r"""
{"part": "Next", "id": null, "text": "Nothing waits. Everything approved is verified.", "kind": "idle", "ids": [], "area": null, "command": null, "waits_on": null}
""")
