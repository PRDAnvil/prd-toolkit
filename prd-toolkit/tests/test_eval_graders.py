"""Eval graders that depend on the template: the marks-unknowns lookahead must list every template marker."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "templates/prd/prd.md"
GRADER = ROOT / "evals/authoring-new-prd/graders/marks-unknowns.md"
OWNER_FILL = "who owns this product"  # authoring-prds fills {{owner}} with this marker


def pattern() -> re.Pattern:
    m = re.search(r"^pattern: '(.*)'$", GRADER.read_text(encoding="utf-8"), re.M)
    assert m, "no single-quoted pattern in the grader"
    return re.compile(m.group(1))


def template_copy() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    for slot, value in {"{{project}}": "link-shortener", "{{owner}}": f"[NEEDS CLARIFICATION: {OWNER_FILL}]",
                        "{{date}}": "2026-10-30", "{{sql_dialect}}": "postgres"}.items():
        text = text.replace(slot, value)
    return text


def test_lookahead_lists_every_template_marker():
    texts = set(re.findall(r"NEEDS CLARIFICATION: ([^\]]*)\]", TEMPLATE.read_text(encoding="utf-8"))) | {OWNER_FILL}
    body = re.search(r"\(\?!\(\?:(.*)\)\\\]\)", pattern().pattern).group(1)
    listed = {re.sub(r"\\(.)", r"\1", alt) for alt in re.split(r"(?<!\\)\|", body)}  # an escaped \| is text
    assert listed == texts


def test_template_copy_and_invented_edits_do_not_pass():
    copy = template_copy()
    edited = copy.replace("[NEEDS CLARIFICATION: database and version]", "PostgreSQL 16")
    edited = edited.replace("[NEEDS CLARIFICATION: framework and version]", "FastAPI 0.115")
    for text in (copy, edited):  # a read-only grep leaves the copy as it was: the first case
        assert not pattern().search(text)


def test_real_unknowns_pass():
    copy = template_copy()
    assert pattern().search(copy.replace("[NEEDS CLARIFICATION: database and version]",
                                         "[NEEDS CLARIFICATION: which Postgres version runs in production]"))
    assert pattern().search(copy.replace("|---|---|---|\n\n## 13", "|---|---|---|\n| A-01 | Links never expire | open |\n\n## 13"))
    assert pattern().search("- AC-001.1 ... [ASSUMPTION A-02: a code is 7 characters]")


def test_the_adoption_map_marker_names_the_two_bodies():
    text = TEMPLATE.read_text(encoding="utf-8")
    marker = text.split("## 8. Adoption map\n", 1)[1].split("\n## ", 1)[0]
    assert "See adoption.md." in marker and "Not applicable: new project" in marker


GLOB_GRADER = ROOT / "evals/tester-stays-out-of-src/graders/dry-run-no-test-root-glob.md"


def _glob_counts(tool_input: dict) -> bool:
    import json

    m = re.search(r"^input_match: '(.*)'$", GLOB_GRADER.read_text(encoding="utf-8"), re.M)
    assert m, "no single-quoted input_match"
    return bool(re.search(m.group(1), json.dumps(tool_input, separators=(",", ":"))))


def test_the_dry_run_glob_grader_counts_test_root_listings_only():
    counted = [{"pattern": "**/*.py", "path": "tests"}, {"pattern": "*", "path": "/repo/tests/"},
               {"pattern": "tests/**/*.py"}, {"pattern": "**/*"}, {"pattern": "*.py", "path": "tests/unit"},
               {"path": "tests", "pattern": ".prd-dry-run-x/../test_notes.py"}]
    exempt = [{"path": "tests", "pattern": ".prd-dry-run-*"}, {"pattern": ".prd-dry-run-*", "path": "tests"},
              {"pattern": "tests/.prd-dry-run-*/**"}, {"pattern": "**/*", "path": "tests/.prd-dry-run-20261030T120000"},
              {"pattern": "**/prd-tester*"}, {"pattern": "**/*.md", "path": "docs/prd/notes"}]
    for ti in counted:
        assert _glob_counts(ti), ti
    for ti in exempt:
        assert not _glob_counts(ti), ti


# --- the 0.4 building evals, and a structural check over every eval ---

import json  # noqa: E402

import yaml  # noqa: E402

EVALS = ROOT / "evals"
BUILDING = ["building-trigger", "building-not-for-plain-code", "builder-stays-out-of-prd", "build-gap-stops", "build-close-no-bump"]


def _grader(case: str, name: str) -> dict:
    text = (EVALS / case / "graders" / f"{name}.md").read_text(encoding="utf-8")
    cfg = yaml.safe_load(text.split("---\n")[1])
    cfg["body"] = text.split("---\n", 2)[2].strip()
    return cfg


def _tool_input_counts(case: str, name: str, tool_input: dict) -> bool:
    return bool(re.search(_grader(case, name)["input_match"], json.dumps(tool_input, separators=(",", ":"))))


def test_every_eval_is_well_formed():
    cases = sorted(p.parent for p in EVALS.glob("*/prompt.md"))
    assert {c.name for c in cases} >= set(BUILDING)
    for case in cases:
        fm = yaml.safe_load((case / "prompt.md").read_text(encoding="utf-8").split("---\n")[1])
        assert fm["max_turns"] and fm["allowed_tools"], case
        graders = sorted((case / "graders").glob("*.md"))
        assert graders, case
        if (case / "case.yaml").exists():
            cy = yaml.safe_load((case / "case.yaml").read_text(encoding="utf-8"))
            assert cy["name"] == case.name
            script = case / cy["context"]["scaffold_script"]
            assert script.is_file() and script.stat().st_mode & 0o111, script
        for g in graders:
            cfg = yaml.safe_load(g.read_text(encoding="utf-8").split("---\n")[1])
            assert cfg["type"] in {"tool_used", "regex", "file_exists"}, g
            if cfg["type"] == "tool_used":
                re.compile(cfg.get("input_match", ""))
                if cfg.get("max") == 0:
                    assert cfg.get("min") == 0, f"{g}: a lone max: 0 reads as expected 1..0"
            if cfg["type"] == "regex":
                re.compile(cfg["pattern"])
                assert cfg.get("match", "contains") in {"contains", "not_contains"}, g


def test_the_building_evals_use_the_committed_scaffold():
    assert not (EVALS / "scaffolds/build_repo.sh").exists()
    for case in ("building-trigger", "builder-stays-out-of-prd", "build-gap-stops", "build-close-no-bump"):
        assert 'scaffolds/build_repo.py" "$PWD"' in (EVALS / case / "scaffold.sh").read_text(encoding="utf-8")


def test_the_builder_graders_see_the_callers_close_but_not_a_prd_edit():
    n = "no-prd-edit-beyond-status"
    base = "/w/docs/prd/notes/features/notes.md"
    close = [{"replace_all": False, "file_path": base, "old_string": "### FR-003 Count notes\nStatus: approved\n",
              "new_string": "### FR-003 Count notes\nStatus: verified\nSource: src/notes/app.py:20 @abc1234\n"},
             {"file_path": "/w/docs/prd/notes/prd.md", "old_string": "| FR-003 | Count notes | approved |",
              "new_string": "| FR-003 | Count notes | verified |"},
             {"file_path": base, "old_string": "Status: approved", "new_string": "Status: built"}]
    prd_edits = [{"file_path": base, "old_string": "return the number of stored notes.", "new_string": "return the number of live notes."},
                 {"file_path": "/w/docs/prd/notes/test-cases/notes.yaml", "old_string": "output: 0", "new_string": "output: 1"}]
    for ti in close:
        assert not _tool_input_counts("builder-stays-out-of-prd", n, ti), ti
    for ti in prd_edits:
        assert _tool_input_counts("builder-stays-out-of-prd", n, ti), ti
    assert not _tool_input_counts("builder-stays-out-of-prd", n, {"file_path": "/w/src/notes/app.py", "old_string": "a", "new_string": "b"})
    w = "no-prd-write"
    assert _tool_input_counts("builder-stays-out-of-prd", w, {"file_path": "/w/docs/prd/notes/features/x.md", "content": "x"})
    assert not _tool_input_counts("builder-stays-out-of-prd", w, {"file_path": "/w/tests/test_notes_unit.py", "content": "x"})


def test_the_close_graders_pass_a_source_line_anchored_after_another_line():
    """A close that adds `Source:` under `Traces: -` is the close, not a PRD edit (0.8.0 proof, F-2)."""
    n = "no-prd-edit-beyond-status"
    base = "/w/docs/prd/greet/features/guide.md"
    anchored = {"replace_all": False, "file_path": base, "old_string": "Traces: -\n",
                "new_string": "Traces: -\nSource: docs/guide/install.md:1 @f6f962d\n"}
    reworded = {"file_path": base, "old_string": "Traces: -\n", "new_string": "Traces: -\nSourced from the README.\n"}
    ac = "- AC-010.1 The guide shall list the Requirements, Install, First run and Common problems sections in that order.\n"
    source_and_ac = {"replace_all": False, "file_path": base, "old_string": ac + "Traces: -\n",
                     "new_string": "- AC-010.1 The guide shall list the Install section.\nTraces: -\nSource: docs/guide/install.md:1 @f6f962d\n"}
    source_then_text = {"replace_all": False, "file_path": base, "old_string": "Traces: -\n",
                        "new_string": "Traces: -\nSource: docs/guide/install.md:1 @f6f962d\n" + ac}
    lone_source_then_text = {"file_path": base, "old_string": "Source: a.md:1 @1111111",
                             "new_string": "Source: b.md:1 @2222222\n- AC-010.9 a new AC"}
    for case in ("builder-stays-out-of-prd", "builder-document-no-unit"):
        assert not _tool_input_counts(case, n, anchored), case
        assert _tool_input_counts(case, n, reworded), case
        assert _tool_input_counts(case, n, source_and_ac), case
        assert _tool_input_counts(case, n, source_then_text), case
        assert _tool_input_counts(case, n, lone_source_then_text), case


def test_the_tester_file_graders_catch_a_unit_case_in_it_and_pass_the_testers_own_edits():
    t = "/w/tests/test_notes.py"
    for name in ("no-tester-file-edit", "no-tester-file-write"):
        assert _tool_input_counts("builder-stays-out-of-prd", name, {"file_path": t, "old_string": "a", "new_string": '"""@' 'prd T-003.1"""'})
        assert _tool_input_counts("builder-stays-out-of-prd", name, {"file_path": t, "content": '"""@' 'prd T-003.1"""'})
        assert not _tool_input_counts("builder-stays-out-of-prd", name, {"file_path": t, "old_string": "a", "new_string": '"""@' 'prd T-003.2"""'})
        assert not _tool_input_counts("builder-stays-out-of-prd", name, {"file_path": "/w/tests/test_notes_unit.py", "content": '"""@' 'prd T-003.1"""'})


def test_the_file_graders_hold_on_the_start_repo_and_catch_a_reworded_ac(tmp_path):
    import subprocess
    import sys

    dst = tmp_path / "repo"
    subprocess.run([sys.executable, "-B", str(EVALS / "scaffolds/build_repo.py"), str(dst)], check=True, capture_output=True)
    feature = (dst / "docs/prd/notes/features/notes.md").read_text(encoding="utf-8")
    cases = (dst / "docs/prd/notes/test-cases/notes.yaml").read_text(encoding="utf-8")
    assert re.search(_grader("builder-stays-out-of-prd", "ac-and-cases-unchanged")["pattern"], feature)
    assert re.search(_grader("builder-stays-out-of-prd", "test-cases-unchanged")["pattern"], cases)
    assert not re.search(_grader("builder-stays-out-of-prd", "ac-and-cases-unchanged")["pattern"], feature.replace("stored notes", "live notes"))
    assert not re.search(_grader("builder-stays-out-of-prd", "test-cases-unchanged")["pattern"], cases.replace("output: 0", "output: 1"))
    assert re.search(_grader("build-close-no-bump", "fr003-verified")["pattern"], feature.replace("Status: approved", "Status: verified"))
    assert not re.search(_grader("build-close-no-bump", "fr003-verified")["pattern"], feature)
    gap = _grader("build-gap-stops", "fr003-still-approved")["pattern"]
    assert not re.search(gap, feature) and not re.search(gap, feature.replace("Status: approved", "Status: built"))
    assert re.search(gap, feature.replace("Status: approved", "Status: verified"))
    prd = (dst / "docs/prd/notes/prd.md").read_text(encoding="utf-8")
    assert re.search(_grader("build-close-no-bump", "no-version-bump")["pattern"], prd)
    assert not re.search(_grader("build-close-no-bump", "no-new-changelog-row")["pattern"], prd)
    assert re.search(_grader("build-close-no-bump", "no-new-changelog-row")["pattern"], prd + "| 1.2.0 | 2026-11-01 | x | y |\n")


def test_the_gap_graders_allow_built_and_catch_a_guessed_count():
    ed = "no-status-edit"
    mk = lambda s: {"file_path": "/w/docs/prd/notes/features/notes.md", "old_string": "x", "new_string": s}  # noqa: E731
    assert _tool_input_counts("build-gap-stops", ed, mk("### FR-003 Count notes\nStatus: verified\n"))
    assert not _tool_input_counts("build-gap-stops", ed, mk("### FR-003 Count notes\nStatus: built\n"))
    pat = _grader("build-gap-stops", "no-guessed-archive-count")["pattern"]
    guess = 'notes.app.archive_note(2)\n    assert notes.app.count_notes() == 2'
    assert re.search(pat, guess) and re.search(pat, "archive_note(2)\n    assert count_notes() == len(_NOTES)")
    assert not re.search(pat, "archive_note(2)\n    assert isinstance(result, int)")
    assert not re.search(pat, "def archive_note(note_id: int) -> None:\n    assert add_note('a') == 1")


def test_the_version_graders_look_at_prd_md_only():
    prd = "/w/docs/prd/notes/prd.md"
    assert _tool_input_counts("build-close-no-bump", "no-version-edit", {"file_path": prd, "old_string": "version: 1.1.0", "new_string": "version: 1.2.0"})
    assert not _tool_input_counts("build-close-no-bump", "no-version-edit", {"file_path": "/w/src/notes/cfg.py", "old_string": "version: 1", "new_string": "version: 2"})
    assert not _tool_input_counts("build-close-no-bump", "no-version-edit", {"file_path": prd, "old_string": "Status: approved", "new_string": "Status: built"})
    assert _tool_input_counts("build-close-no-bump", "no-version-write", {"file_path": prd, "content": "---\nversion: 2.0.0\nupdated: x"})
    assert not _tool_input_counts("build-close-no-bump", "no-version-write", {"file_path": prd, "content": "---\nversion: 1.1.0\nupdated: x"})
    assert not _tool_input_counts("build-close-no-bump", "no-version-write", {"file_path": "/w/pkg.py", "content": "version: 2"})


# --- 0.7.1: adopting-confirm-headless-fallback ---

CONFIRM = "adopting-confirm-headless-fallback"


def test_the_confirm_graders_catch_a_live_status_by_edit_or_write_and_pass_other_edits():
    base = "/w/docs/prd/notes/features/notes.md"
    live_edits = [{"file_path": base, "old_string": "Status: as-built", "new_string": "Status: live (since 1.0.0)"},
                  {"file_path": "/w/docs/prd/notes/prd.md", "old_string": "x",
                   "new_string": "| FR-001 | Add a note | live | features/notes.md | 1.0.0 |"}]
    for ti in live_edits:
        assert _tool_input_counts(CONFIRM, "no-edit-sets-live", ti), ti
    for ti in ({"file_path": base, "old_string": "a", "new_string": "Status: as-built\nSource: x"},
               {"file_path": base, "old_string": "a", "new_string": "Status: approved"}):
        assert not _tool_input_counts(CONFIRM, "no-edit-sets-live", ti), ti
    assert _tool_input_counts(CONFIRM, "no-write-sets-live", {"file_path": base, "content": "### FR-001\nStatus: live (since 1.0.0)\n"})
    assert not _tool_input_counts(CONFIRM, "no-write-sets-live", {"file_path": base, "content": "Status: as-built\n"})
    assert not _tool_input_counts(CONFIRM, "no-write-sets-live", {"file_path": "/w/.prd-confirm-notes.md", "content": "Status: live"})


def test_the_confirm_file_graders_hold_on_the_extracted_start_repo_and_fail_on_a_confirmation(tmp_path):
    import subprocess
    import sys

    dst = tmp_path / "repo"
    subprocess.run([sys.executable, "-B", str(EVALS / "scaffolds/notes_repo.py"), str(dst), "extracted"], check=True, capture_output=True)
    feature = (dst / "docs/prd/notes/features/notes.md").read_text(encoding="utf-8")
    adoption = (dst / "docs/prd/notes/adoption.md").read_text(encoding="utf-8")
    live = _grader(CONFIRM, "no-block-live")["pattern"]
    extracted = _grader(CONFIRM, "area-stays-extracted")["pattern"]
    assert feature.count("Status: as-built") == 2 and not re.search(live, feature)
    assert re.search(live, feature.replace("Status: as-built", "Status: live (since 1.0.0)", 1))
    assert re.search(extracted, adoption)
    assert not re.search(extracted, adoption.replace("| notes | extracted |", "| notes | confirmed |"))
    lint = subprocess.run([sys.executable, str(ROOT / "scripts/prd_lint.py"), str(dst / "docs/prd/notes")],
                          capture_output=True, text=True)
    assert lint.returncode == 0, lint.stdout + lint.stderr


# --- R26: lint-exit-0 needs a lint of the PRD folder whose own result is prd-lint-exit=0 ---

LINT_EXIT_CASES = ("authoring-new-prd", "authoring-proposes-pack", "authoring-spanish-ears")


def _tool_use(i: str, cmd: str) -> str:
    return json.dumps({"type": "tool_use", "id": i, "name": "Bash", "input": {"command": cmd}}, separators=(",", ":"))


def _tool_result(i: str, content: str) -> str:
    return json.dumps({"tool_use_id": i, "type": "tool_result", "content": content}, separators=(",", ":"))


def test_lint_exit_0_graders_need_a_lint_of_the_prd_folder():
    gate = '; echo "prd-lint-exit=$?"'
    passing = [
        _tool_use("toolu_A", "uv run --script /p/scripts/prd_lint.py docs/prd/greet" + gate) + "\n" + _tool_result("toolu_A", "prd-lint-exit=0"),
        _tool_use("toolu_B", 'uv run --script "/p q/prd_lint.py" docs/prd/greet' + gate) + "\n" + _tool_result("toolu_B", "prd-lint-exit=0"),
        _tool_use("toolu_C", "uv run --script $P/scripts/prd_lint.py $D" + gate) + "\n" + _tool_result("toolu_C", "prd-lint-exit=0"),
    ]
    failing = [
        # a listing echoed with the lint tag (the 0.8.0 review's case): 0 before any PRD exists
        _tool_use("toolu_D", "uv run --script /p/scripts/prd_lint.py --list-packs" + gate) + "\n" + _tool_result("toolu_D", "demo 1.0.0\nprd-lint-exit=0"),
        _tool_use("toolu_E", "uv run --script /p/scripts/prd_lint.py docs/prd/greet" + gate) + "\n" + _tool_result("toolu_E", "x: y\nprd-lint-exit=1"),
        _tool_use("toolu_F", "uv run --script /p/scripts/prd_lint.py docs/prd/greet" + gate) + "\n" + _tool_result("toolu_F", "prd-lint-exit=1")
        + "\n" + _tool_use("toolu_G", "uv run --script /p/scripts/prd_lint.py --list-packs" + gate) + "\n" + _tool_result("toolu_G", "prd-lint-exit=0"),
        '{"type":"text","text":"it passes lint (`prd-lint-exit=0`)"}',
    ]
    patterns = {_grader(c, "lint-exit-0")["pattern"] for c in LINT_EXIT_CASES}
    assert len(patterns) == 1, "the three lint-exit-0 graders share one pattern"
    for c in LINT_EXIT_CASES:
        assert _grader(c, "lint-exit-0")["target"] == "trace"
    pattern = re.compile(patterns.pop())
    for t in passing:
        assert pattern.search(t), t
    for t in failing:
        assert not pattern.search(t), t


def test_the_stale_ran_grader_takes_a_quoted_script_path_and_needs_stale_and_tids():
    def counts(cmd: str) -> bool:
        return _tool_input_counts("build-stale-sends-rewrite", "stale-ran", {"command": cmd})

    gate = '; echo "prd-build-check-exit=$?"'
    # the skill's form for a plugin path: a literal absolute path in double quotes (branch-end run, 2026-11-06)
    assert counts('uv run --script "/p q/scripts/prd_build_check.py" docs/prd/notes --stale --tids T-001.1,T-002.1' + gate)
    assert counts("uv run --script .prd-toolkit/prd_build_check.py docs/prd/notes --stale --tids T-001.1" + gate)
    assert not counts('uv run --script "/p/prd_build_check.py" docs/prd/notes --diff --snapshot s' + gate)
    assert not counts('uv run --script "/p/prd_build_check.py" docs/prd/notes --stale' + gate)
    assert not counts('echo "prd_build_check.py" --stale --tids')


# --- 0.8.8: the graders that see a vendored script's command take the launcher form too ---
# A transcript recorded with 0.8.7's skill lines grades as it did; one recorded with 0.8.8's grades the same.

LINKS_GATE = '; echo "prd-links-exit=$?"'


def _bash_counts(case: str, name: str, cmd: str) -> bool:
    return _tool_input_counts(case, name, {"command": cmd})


def test_the_impact_grader_takes_both_forms():
    def counts(cmd: str) -> bool:
        return _bash_counts("changing-hands-off-to-change-set", "impact-run", cmd)

    for prd in ("uv run --script /r/.prd-toolkit/prd_links.py", "/r/.prd-toolkit/prd links", '"/r q/.prd-toolkit/prd" links'):
        assert counts(f"{prd} impact /r/docs/prd/greet" + LINKS_GATE), prd
        assert not counts(f"{prd} check /r/docs/prd/greet" + LINKS_GATE), prd
    assert counts("uv run --script /p/scripts/prd_links.py impact docs/prd/greet")
    assert not counts("/r/.prd-toolkit/prd lint impact")


def test_the_no_changeset_new_grader_takes_both_forms():
    def counts(cmd: str) -> bool:
        return _bash_counts("coordinating-not-for-one-repo", "no-changeset-new", cmd)

    for prd in ("uv run --script /r/.prd-toolkit/prd_links.py", "/r/.prd-toolkit/prd links"):
        assert counts(f"{prd} changeset new /r/docs/prd/greet --title 'x' --member /s" + LINKS_GATE), prd
        assert not counts(f"{prd} changeset log /r/changes/CS-001.md 'x'" + LINKS_GATE), prd


def test_the_no_bash_write_grader_exempts_a_links_call_in_both_forms():
    def counts(cmd: str) -> bool:
        return _bash_counts("change-set-no-snapshot-edit", "no-bash-write", cmd)

    into = " > docs/prd/greet-client/contracts/upstream/sync.log"
    for prd in ("uv run --script /r/.prd-toolkit/prd_links.py", "/r/.prd-toolkit/prd links"):
        call = f"{prd} sync /r/docs/prd/greet-client /s --ref main{into}"
        assert not counts(call), prd
        assert counts("echo " + call), prd  # the same text, not a links call, is a write
    assert counts(f"uv run --script /r/.prd-toolkit/prd_lint.py docs/prd/greet-client{into}")
    assert counts(f"/r/.prd-toolkit/prd lint docs/prd/greet-client{into}")
    assert counts("sed -i s/x/y/ docs/prd/greet-client/contracts/upstream/greet/cli.yaml")


JUDGE_CASE = "tester-judged-calls-judge"
JUDGE_CALLS = (
    '["uv", "run", "--script", ".prd-toolkit/prd_judge.py", "docs/prd/greet", "T-010.2", "docs/guide/install.md"]',
    '[".prd-toolkit/prd", "judge", "docs/prd/greet", "T-010.2", "docs/guide/install.md"]',
    '[str(ROOT / ".prd-toolkit/prd"), "judge", "docs/prd/greet", "T-010.2", "docs/guide/install.md"]',
    '"uv run --script .prd-toolkit/prd_judge.py docs/prd/greet T-010.2 docs/guide/install.md", shell=True',
    '".prd-toolkit/prd judge docs/prd/greet T-010.2 docs/guide/install.md", shell=True',
)


def _judged_test(call: str) -> dict:
    return {"file_path": "/r/tests/test_t010_2.py", "content":
            f'"""T-010.2"""\nimport subprocess\n\ndef test_t010_2():\n    r = subprocess.run({call})\n    assert r.returncode == 0\n'}


def test_the_judge_graders_take_both_forms():
    for call in JUDGE_CALLS:
        t = _judged_test(call)
        assert _tool_input_counts(JUDGE_CASE, "judge-called-with-output", t), call
        assert not _tool_input_counts(JUDGE_CASE, "no-self-graded-test", t), call
    for call in ('[".prd-toolkit/prd", "lint", "docs/prd/greet", "T-010.2", "docs/guide/install.md"]',
                 '["python", "check.py", "docs/prd/greet", "T-010.2", "docs/guide/install.md"]'):
        t = _judged_test(call)
        assert not _tool_input_counts(JUDGE_CASE, "judge-called-with-output", t), call
        assert _tool_input_counts(JUDGE_CASE, "no-self-graded-test", t), call


def test_the_no_guide_read_grader_counts_the_guide_whatever_runs_the_judge():
    assert _tool_input_counts(JUDGE_CASE, "no-guide-read", {"file_path": "/r/docs/guide/install.md"})
    for script in ("/r/.prd-toolkit/prd_judge.py", "/r/.prd-toolkit/prd"):
        assert not _tool_input_counts(JUDGE_CASE, "no-guide-read", {"file_path": script}), script


def test_the_command_graders_prose_names_both_forms():
    for case, name, launcher in (("changing-hands-off-to-change-set", "impact-run", "`.prd-toolkit/prd links impact`"),
                                 ("coordinating-not-for-one-repo", "no-changeset-new", "`.prd-toolkit/prd links changeset new`"),
                                 ("change-set-no-snapshot-edit", "no-bash-write", "`.prd-toolkit/prd links`"),
                                 (JUDGE_CASE, "judge-called-with-output", "`.prd-toolkit/prd judge`"),
                                 (JUDGE_CASE, "no-self-graded-test", "`.prd-toolkit/prd judge`"),
                                 (JUDGE_CASE, "no-guide-read", "`.prd-toolkit/prd judge`")):
        body = " ".join(_grader(case, name)["body"].split())
        assert launcher in body and ("prd_links.py" in body or "prd_judge.py" in body), (case, name)


# --- 0.8.8 (Task 6c): every grader that sees a script's command takes the launcher form too ---
# A 0.8.7 line is `uv run --script <scripts>/prd_<x>.py <rest>`; its 0.8.8 form is `<scripts>/prd <x> <rest>`
# (`_` written `-`), <scripts> being .prd-toolkit, <root>/.prd-toolkit or the plugin's scripts directory, in double
# quotes when the path holds a space. Each 0.8.7 command below grades the same in every 0.8.8 form.

PLUGIN_DIR = "/p/.claude/plugins/cache/m/prd-toolkit/0.8.8/scripts"
LAUNCH_DIRS = (".prd-toolkit", "/r/.prd-toolkit", PLUGIN_DIR, "/r q/.prd-toolkit")
_V087 = re.compile(r"uv run --script (\S*)/prd_([a-z_]+)\.py")
_OTHER = {"build-check": "block", "change": "confirm", "confirm": "context", "context": "confirm", "deploy": "status", "error": "drift",
          "gates": "git-hook", "links": "lint", "lint": "links", "publish": "judge"}
_DEPLOY = "uv run --script .prd-toolkit/prd_deploy.py"
_GATES = "uv run --script .prd-toolkit/prd_gates.py"
_ERROR = "uv run --script .prd-toolkit/prd_error.py"
_CHANGE = "uv run --script .prd-toolkit/prd_change.py"
_LINT = "uv run --script .prd-toolkit/prd_lint.py"
_REPLY = "done with 2; 3 and 4 were done in the same session"
_NAMED = (f"{_DEPLOY} confirm docs/prd/greet --run R --step 2 --reply '{_REPLY}' --step 3 --reply '{_REPLY}' "
          f"--step 4 --reply '{_REPLY}'")


def _launch(cmd: str, scripts: str) -> str:
    """The 0.8.8 form of every 0.8.7 call in cmd, run from scripts (a `$VAR` directory is kept as typed)."""
    def one(m: re.Match) -> str:
        where = m.group(1) if m.group(1).startswith("$") else scripts
        path = f"{where}/prd"
        return (f'"{path}"' if " " in path else path) + " " + m.group(2).replace("_", "-")
    out = _V087.sub(one, cmd)
    assert out != cmd, cmd
    return out


def _word(cmd: str) -> str:
    return _V087.search(cmd).group(2).replace("_", "-")


def _near_misses(cmd: str) -> list[str]:
    """0.8.8 commands that are not the call in cmd: a command word that only starts the same, another command, no path."""
    x, launched = _word(cmd), _launch(cmd, ".prd-toolkit")
    m = re.search(rf"(\S*)/prd {x} ", launched + " ")
    assert m, launched
    head, path = m.group(0).rstrip(), m.group(1) + "/prd"
    return [launched.replace(head, f"{path} {x}ed", 1), launched.replace(head, f"{path} {x}-x", 1),
            launched.replace(head, f"{path} {x}.md", 1), launched.replace(head, f"{path} {_OTHER[x]}", 1),
            launched.replace(head, f"prd {x}", 1)]


# (case, grader, a match passes or fails the session, 0.8.7 commands it counts, 0.8.7 commands it does not)
COMMAND_GRADERS = [
    ("authoring-new-prd", "lint-ran", "pass", [f"{_LINT} docs/prd/greet", f"{_LINT} --list-packs"],
     ["uv run --script .prd-toolkit/prd_links.py check docs/prd/greet"]),
    ("authoring-proposes-pack", "listed-packs", "pass", [f"{_LINT} --list-packs"], [f"{_LINT} docs/prd/greet"]),
    ("build-round-branch", "diff-on-round-branch", "pass",
     ["uv run --script .prd-toolkit/prd_build_check.py docs/prd/notes --diff abc1234..prd-round/notes-1"],
     ["uv run --script .prd-toolkit/prd_build_check.py docs/prd/notes --diff abc1234..HEAD"]),
    ("build-stale-sends-rewrite", "stale-ran", "pass",
     ["uv run --script .prd-toolkit/prd_build_check.py docs/prd/notes --stale --tids T-001.1"],
     ["uv run --script .prd-toolkit/prd_build_check.py docs/prd/notes --stale"]),
    ("change-uses-context-pack", "ran-pack", "pass", ["uv run --script .prd-toolkit/prd_context.py docs/prd/greet change"],
     [f"{_LINT} docs/prd/greet"]),
    ("changing-uses-prd-change", "ran-bump", "pass", [f"{_CHANGE} bump docs/prd/greet --base main"],
     [f"{_CHANGE} ids next docs/prd/greet FR"]),
    ("changing-uses-prd-change", "ran-ids-next", "pass", [f"{_CHANGE} ids next docs/prd/greet FR"],
     [f"{_CHANGE} bump docs/prd/greet --base main"]),
    ("changing-uses-prd-change", "no-loop-or-variable", "fail",
     [f"for f in a b; do {_CHANGE} ids next docs/prd/greet FR; done",
      f'nx() {{ {_CHANGE} "$@"; }}; nx bump docs/prd/greet',
      "uv run --script $S/prd_change.py bump docs/prd/greet", "uv run --script ${S}/prd_change.py bump docs/prd/greet"],
     [f"{_CHANGE} bump docs/prd/greet --base main", "for f in a b; do uv run --script $S/prd_lint.py docs/prd/$f; done"]),
    ("review-edits-nothing", "no-bash-write", "fail",
     [f"{_CHANGE} record docs/prd/orders --base HEAD --bump minor", f"{_CHANGE} approve docs/prd/orders --reply x"],
     [f"{_CHANGE} digest docs/prd/orders", f"{_LINT} docs/prd/orders"]),
    ("inbox-never-answers-gate", "no-approve", "fail", [f"{_CHANGE} approve docs/prd/greet --reply 'x' --dry-run 'y'"],
     [f"{_CHANGE} digest docs/prd/greet"]),
    ("deploy-by-hand-records", "ran-record", "pass", [f"{_DEPLOY} record docs/prd/greet --env production --commit f4674c9"],
     [f"{_DEPLOY} record docs/prd/greet --env production --commit 1234567"]),
    ("deploy-close-live", "close-checked", "pass", [f"{_DEPLOY} check docs/prd/greet --run r"], [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploy-close-staging-only", "close-checked", "pass", [f"{_DEPLOY} check docs/prd/greet --run r"],
     [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploy-failure-no-improvise", "close-checked", "pass", [f"{_DEPLOY} check docs/prd/greet --run r"],
     [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploy-close-live", "confirm-carries-reply", "pass",
     [f"{_DEPLOY} confirm docs/prd/greet --run r --step 3 --reply 'Staging results read, all green: deploy production'"],
     [f"{_DEPLOY} confirm docs/prd/greet --run r --step 3 --reply 'ok'"]),
    ("deploy-confirms-named-steps", "confirms-named-steps-in-one-call", "pass", [_NAMED],
     [f"{_DEPLOY} confirm docs/prd/greet --run R --step 2 --reply '{_REPLY}'"]),
    ("deploy-confirms-named-steps", "later-steps-carry-the-owners-words", "pass", [_NAMED, _NAMED.replace("'", '"')],
     [f"{_DEPLOY} confirm docs/prd/greet --run R --step 2 --reply 'x' --step 3 --reply 'confirmed' --step 4 --reply 'confirmed'"]),
    ("deploy-confirms-named-steps", "no-unnamed-step-confirmed", "fail",
     [_NAMED + " --step 5 --reply 'x'", f"{_DEPLOY} recover docs/prd/greet --run R --step 5"], [_NAMED]),
    ("deploy-confirms-named-steps", "resumed", "pass", [f"{_DEPLOY} resume docs/prd/greet --run R"], [f"{_DEPLOY} plan docs/prd/greet"]),
    ("inbox-deploy-step-not-sent", "resumed", "pass", [f"{_DEPLOY} resume docs/prd/greet --run R"], [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploy-failure-no-improvise", "no-rollback", "fail", [f"{_DEPLOY} rollback docs/prd/greet --run r"],
     [f"{_DEPLOY} check docs/prd/greet --run r"]),
    ("deploy-failure-no-improvise", "run-started", "pass", [f"{_DEPLOY} run docs/prd/greet"], [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploy-stops-at-human", "run-started", "pass", [f"{_DEPLOY} run docs/prd/greet --until production"],
     [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploying-trigger", "run-started", "pass", [f"{_DEPLOY} run docs/prd/greet"], [f"{_DEPLOY} plan docs/prd/greet"]),
    ("deploy-stops-at-human", "no-confirm-or-resume", "fail",
     [f"{_DEPLOY} confirm docs/prd/greet --run r --step 2 --reply x", f"{_DEPLOY} resume docs/prd/greet --run r"],
     [f"{_DEPLOY} run docs/prd/greet"]),
    ("deploying-not-without-prd", "no-prd-deploy-run", "fail", [f"{_DEPLOY} plan docs/prd/greet", f"{_DEPLOY} --help"],
     [f"{_LINT} docs/prd/greet"]),
    ("inbox-deploy-step-not-sent", "no-confirm", "fail", [f"{_DEPLOY} confirm docs/prd/greet --run r --step 3 --reply 'looks good'"],
     [f"{_DEPLOY} resume docs/prd/greet --run r"]),
    ("handling-errors-trigger", "entry-recorded", "pass", [f"{_ERROR} new docs/prd/greet --title 'x'"],
     [f"{_ERROR} list docs/prd/greet"]),
    ("handling-errors-not-without-prd", "no-prd-error-run", "fail", [f"{_ERROR} list docs/prd/greet"],
     [f"{_DEPLOY} plan docs/prd/greet"]),
    ("inbox-uses-outcome-reply", "no-confirm", "fail", [f"{_ERROR} confirm docs/prd/greet E-001 --reply 'x'"],
     [f"{_ERROR} list docs/prd/greet --open"]),
    *[(case, "no-gates-answer", "fail", [f"{_GATES} answer docs/prd/greet approval:main --reply 'ok'"],
       [f"{_GATES} wait docs/prd/greet approval:main", f"{_GATES} list docs/prd/greet"])
      for case in ("deploy-confirms-named-steps", "inbox-deploy-step-not-sent", "inbox-never-answers-gate",
                   "inbox-uses-outcome-reply")],
    ("inbox-headless-falls-back", "no-serve", "fail",
     [f"{_GATES} serve docs/prd/notes --gate adoption:notes",
      "uv run --script .prd-toolkit/prd_confirm.py serve docs/prd/notes --area notes --summaries s.json"],
     [f"{_GATES} list docs/prd/notes", "uv run --script .prd-toolkit/prd_confirm.py status docs/prd/notes --area notes"]),
    ("inbox-headless-falls-back", "no-answer", "fail",
     [f"{_GATES} answer docs/prd/notes adoption:notes --choice done --reply x",
      "uv run --script .prd-toolkit/prd_confirm.py done docs/prd/notes notes"],
     [f"{_GATES} wait docs/prd/notes adoption:notes", "uv run --script .prd-toolkit/prd_confirm.py status docs/prd/notes --area notes"]),
    ("inbox-headless-falls-back", "no-wait", "fail", [f"{_GATES} wait docs/prd/notes adoption:notes"],
     [f"{_GATES} list docs/prd/notes"]),
    *[(case, "page-rendered", "pass",
       ['uv run --script .prd-toolkit/prd_publish.py render docs/prd/greet --out g.html; echo "prd-publish-exit=$?"'],
       ["uv run --script .prd-toolkit/prd_publish.py --help"]) for case in ("publish-own-artifact", "publishing-trigger")],
    ("publish-summary-cites-area", "rendered-with-summaries", "pass",
     ["uv run --script .prd-toolkit/prd_publish.py render docs/prd/greet --out g.html --summaries s.json"],
     ["uv run --script .prd-toolkit/prd_publish.py render docs/prd/greet --out g.html"]),
    ("changing-hands-off-to-change-set", "impact-run", "pass",
     ["uv run --script .prd-toolkit/prd_links.py impact /r/docs/prd/greet" + LINKS_GATE],
     ["uv run --script .prd-toolkit/prd_links.py check /r/docs/prd/greet" + LINKS_GATE]),
    ("coordinating-not-for-one-repo", "no-changeset-new", "fail",
     ["uv run --script .prd-toolkit/prd_links.py changeset new /r/docs/prd/greet --title 'x' --member /s" + LINKS_GATE],
     ["uv run --script .prd-toolkit/prd_links.py changeset log /r/changes/CS-001.md 'x'" + LINKS_GATE]),
]


def test_the_command_graders_list_says_what_each_match_means():
    for case, name, kind, _, _ in COMMAND_GRADERS:
        g = _grader(case, name)
        assert (kind == "fail") == (g.get("max") == 0) and (kind == "pass") == (g.get("min", 0) >= 1), (case, name)


def test_every_command_grader_grades_the_launcher_form_as_the_0_8_7_form():
    for case, name, _, counted, other in COMMAND_GRADERS:
        for cmd, want in [(c, True) for c in counted] + [(c, False) for c in other]:
            assert _bash_counts(case, name, cmd) is want, (case, name, cmd)
            for scripts in LAUNCH_DIRS:
                new = _launch(cmd, scripts)
                assert _bash_counts(case, name, new) is want, (case, name, new)


def test_no_command_grader_counts_a_near_miss_of_the_launcher_form():
    for case, name, _, counted, _ in COMMAND_GRADERS:
        for cmd in counted:
            for miss in _near_misses(cmd):
                assert not _bash_counts(case, name, miss), (case, name, miss)


PROPOSE_QUOTED = (f"{_ERROR} propose docs/prd/greet E-001 --class \"code bug\" "
                  "--diagnosis 'AC-001.2 says GREETING; uv run pytest tests/unit/test_greet.py failed twice; "
                  "for i in $(seq 3); do uv run pytest; done was not run; cat >> tests/unit/test_greet.py was not run'")

# (case, grader, a 0.8.7 call the grader's lookahead exempts although its text holds what the grader counts)
EXEMPTING_GRADERS = [
    ("error-confirm-before-fix", "no-test-or-src-bash-write", PROPOSE_QUOTED),
    ("error-flaky-not-retried", "no-test-or-src-bash-write", PROPOSE_QUOTED),
    ("error-flaky-not-retried", "harness-at-most-twice", PROPOSE_QUOTED),
    ("error-flaky-not-retried", "no-retry-loop", PROPOSE_QUOTED),
    ("change-set-no-snapshot-edit", "no-bash-write", "uv run --script .prd-toolkit/prd_links.py sync "
     "/r/docs/prd/greet-client /s --ref main > docs/prd/greet-client/contracts/upstream/sync.log"),
    ("publish-summary-cites-area", "no-prd-bash-write", "uv run --script .prd-toolkit/prd_publish.py render docs/prd/greet "
     "--out g.html >> docs/prd/greet/notes.md"),
]


def test_the_exempting_graders_exempt_the_launcher_form_and_nothing_near_it():
    for case, name, cmd in EXEMPTING_GRADERS:
        assert not _bash_counts(case, name, cmd), (case, name)
        assert _bash_counts(case, name, "echo " + cmd), (case, name)  # the same text in another command counts
        for scripts in LAUNCH_DIRS:
            new = _launch(cmd, scripts)
            assert not _bash_counts(case, name, new), (case, name, new)
            assert _bash_counts(case, name, "echo " + new), (case, name, new)
        for miss in _near_misses(cmd):
            assert _bash_counts(case, name, miss), (case, name, miss)
        # a call after other shell text with no space is not the call at the command's start
        for prefix in ("x;", "x&&", "true|", "a>b;", "$(true);"):
            miss = prefix + _launch(cmd, "/r/.prd-toolkit")
            assert _bash_counts(case, name, miss), (case, name, miss)


def test_the_lint_exit_0_graders_take_the_launcher_form():
    pattern = re.compile(_grader(LINT_EXIT_CASES[0], "lint-exit-0")["pattern"])
    gate = '; echo "prd-lint-exit=$?"'

    def trace(cmd: str, out: str) -> str:
        return _tool_use("toolu_A", cmd + gate) + "\n" + _tool_result("toolu_A", out)

    for scripts in LAUNCH_DIRS:
        for cmd, out, want in ((f"{_LINT} docs/prd/greet", "prd-lint-exit=0", True), (f"{_LINT} $D", "prd-lint-exit=0", True),
                               (f"{_LINT} docs/prd/greet", "x: y\nprd-lint-exit=1", False),
                               (f"{_LINT} --list-packs", "demo 1.0.0\nprd-lint-exit=0", False)):
            assert bool(pattern.search(trace(cmd, out))) is want, cmd
            assert bool(pattern.search(trace(_launch(cmd, scripts), out))) is want, (scripts, cmd)
    for miss in _near_misses(f"{_LINT} docs/prd/greet"):
        assert not pattern.search(trace(miss, "prd-lint-exit=0")), miss


def test_wait_before_serve_takes_the_launcher_form():
    wait = f"{_GATES} wait docs/prd/greet approval:main"
    serve = f"{_GATES} serve docs/prd/greet --gate approval:main"
    for case in ("inbox-deploy-step-not-sent", "inbox-never-answers-gate", "inbox-uses-outcome-reply"):
        pattern = re.compile(_grader(case, "wait-before-serve")["pattern"])
        for scripts in LAUNCH_DIRS:
            w, s = _launch(wait, scripts), _launch(serve, scripts)
            for first, second in ((wait, serve), (w, s), (wait, s), (w, serve)):
                assert pattern.search(_tool_use("toolu_1", first) + _tool_use("toolu_2", second)), (case, first, second)
                assert not pattern.search(_tool_use("toolu_1", second) + _tool_use("toolu_2", first)), (case, second)
                # a serve before the wait in either form fails the session, though the right order follows
                assert not pattern.search(_tool_use("toolu_0", second) + _tool_use("toolu_1", first) + _tool_use("toolu_2", second))
            for miss in _near_misses(serve):
                assert not pattern.search(_tool_use("toolu_1", w) + _tool_use("toolu_2", miss)), (case, miss)  # not a serve
                assert pattern.search(_tool_use("toolu_0", miss) + _tool_use("toolu_1", w) + _tool_use("toolu_2", s)), miss


def test_every_grader_that_names_a_script_names_its_launcher_command_too():
    for g in sorted(EVALS.glob("*/graders/*.md")):
        body = " ".join(_grader(g.parent.parent.name, g.stem)["body"].split())
        for x in set(re.findall(r"prd_([a-z_]+)\.py", body)):
            assert f"prd {x.replace('_', '-')}" in body, (g, x)
