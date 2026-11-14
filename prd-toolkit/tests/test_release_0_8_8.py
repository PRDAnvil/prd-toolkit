"""Pins for the 0.8.8 release: what the plugin tells a reader to type runs a vendored copy through the launcher."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent


def tracked(*dirs: str) -> list[Path]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", *dirs], capture_output=True, text=True, check=True)
    return [ROOT / rel for rel in sorted(p for p in out.stdout.split("\0") if p)]


def test_no_vendored_script_is_run_by_its_file():
    hits = [f"{p}:{n}" for p in tracked("skills", "commands", "agents", "templates")
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if re.search(r"uv run --script \S*\.prd-toolkit/", line)]
    assert hits == []


def test_plugin_path_lines_are_untouched():
    n = sum(line.count("uv run --script <scripts>/") for p in tracked("skills", "commands", "agents")
            for line in p.read_text(encoding="utf-8").splitlines())
    assert n == 80        # 77 in skills, 2 in commands, 1 in agents, counted on bfb63da


def _paragraphs(text: str) -> list[str]:
    """Blank-line paragraphs, with each list item its own paragraph."""
    return [p for p in re.split(r"\n\s*\n|\n(?=\s*(?:[-*]|\d+\.) )", text) if p.strip()]


def test_skills_say_what_to_do_without_the_launcher():
    # A copy vendored before 0.8.8 has the scripts and no launcher: the passage that sends the user to
    # `prd_hooks.py install` names the launcher itself (`.prd-toolkit/prd`, not only `prd_<x>.py`).
    for rel in ("skills/coordinating-prds/running-a-change-set.md", "skills/testing-from-prds/SKILL.md",
                "agents/prd-tester.md"):
        paras = [p for p in _paragraphs((ROOT / rel).read_text(encoding="utf-8")) if "prd_hooks.py install" in p]
        assert paras, rel
        assert any("`.prd-toolkit/prd`" in p for p in paras), rel
