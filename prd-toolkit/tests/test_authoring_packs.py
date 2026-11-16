"""0.8.12 skill text: the authoring-packs skill and its command, its baseline, and the edits that name the pack
command, the lift and the URL of an entry or an area (spec §4, §5, §7, §8)."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
SKILL_DIR = ROOT / "skills/authoring-packs"
SKILL = SKILL_DIR / "SKILL.md"
RUN = SKILL_DIR / "running-a-pack.md"
COMMAND = ROOT / "commands/prd-pack.md"
BASELINE = ROOT / "evals/baselines/authoring-packs.md"
CHANGING = ROOT / "skills/changing-prds/SKILL.md"
ADOPTING = ROOT / "skills/adopting-prds/SKILL.md"
ERROR_SKILL = ROOT / "skills/handling-errors/SKILL.md"
ERROR_RUN = ROOT / "skills/handling-errors/running-an-error.md"
FORMAT = ROOT / "references/prd-format.md"
CONTRACT_TYPES = ROOT / "references/contract-types.md"


def flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    return yaml.safe_load(text.split("---\n", 2)[1])


# --- the skill ---

def test_skill_frontmatter_triggers():
    fm = frontmatter(SKILL)
    assert set(fm) == {"name", "description"} and fm["name"] == "authoring-packs"
    d = fm["description"]
    assert d.startswith("Use when") and len(d) <= 1024
    for s in ("pack", "two adopted PRDs", "custom contract types", "plugin", "/prd-toolkit:prd-pack", "docs/prd/",
              "merge", "install"):
        assert s in d, s


def test_skill_first_instruction_reads_the_procedure_whole():
    body = SKILL.read_text(encoding="utf-8").split("---\n", 2)[2].lstrip("\n")
    first = " ".join(body.split("\n\n", 1)[0].split())
    assert first.startswith("Read `${CLAUDE_PLUGIN_ROOT}/skills/authoring-packs/running-a-pack.md` whole")
    assert "(no offset, no limit" in first and "your next tool call" in first and "steps 1 to 7" in first
    assert RUN.is_file()


def test_skill_has_the_house_shape():
    text = SKILL.read_text(encoding="utf-8")
    heads = ["## Overview", "## Non-negotiable rules", "## Red Flags - STOP", "## Common Rationalizations",
             "## Related skills"]
    at = [text.index(h) for h in heads]
    assert at == sorted(at)
    assert "Violating the letter of these rules is violating the spirit." in text


# the spec's rules (§4, §5), verbatim
RULES = (
    "Both PRDs are Approved and lint clean, and each holds one or more custom contract types.",
    "a repository with no PRD is adopted first (`/prd-toolkit:prd-adopt`)",
    "Every manifest item comes from a line of one or both PRDs and the report says which; nothing a PRD does not "
    "hold is added (no helper, no rule, no level).",
    "A difference is the owner's to settle, never averaged.",
    "When the two PRDs' validators differ, the owner picks one; the skill merges none.",
    "One reply may decide them all, after the proposal is shown.",
    "It never pushes, publishes or installs.",
    "No helper code, `clarify.md`, `rubrics.md` or skill is drafted",
    "The PRDs themselves are not edited by this skill.",
)


def test_skill_states_the_spec_rules_verbatim():
    t = flat(SKILL)
    for rule in RULES:
        assert rule in t, rule


def test_red_flags_quote_the_baseline():
    a = SKILL.read_text(encoding="utf-8")
    flags = " ".join(a[a.index("## Red Flags - STOP"):a.index("## Common Rationalizations")].split())
    record = " ".join(BASELINE.read_text(encoding="utf-8").split())
    quoted = re.findall(r'"([^"]{30,})"', flags)
    assert len(quoted) >= 6
    for q in quoted:
        assert q in record, q


def test_baseline_is_generic():
    text = BASELINE.read_text(encoding="utf-8")
    assert text.startswith("# authoring-packs: pressure scenario and baseline\n")
    assert "## Results (RED)" in text and "Run WITHOUT the skill" in text
    assert not re.search(r"/Users/|/home/|~/", text)


# --- the procedure ---

STEPS = ("1. **Preconditions.**", "2. **Compare**", "3. **The proposal.**", "4. **The owner decides**",
         "5. **Where it goes.**", "6. **Write, check, commit.**", "7. **Report:**")


def test_procedure_runs_the_spec_steps_in_order():
    text = RUN.read_text(encoding="utf-8")
    at = [text.index(s) for s in STEPS]
    assert at == sorted(at)


def test_procedure_names_the_commands_as_they_run():
    t = flat(RUN)
    for cmd in ('<plugin scripts>/prd lint <A>; echo "prd-lint-exit=$?"',
                '<plugin scripts>/prd lint --list-packs; echo "prd-list-packs-exit=$?"',
                '<plugin scripts>/prd pack compare <A> <B>; echo "prd-pack-exit=$?"',
                '<plugin scripts>/prd pack compare --json <A> <B>; echo "prd-pack-exit=$?"',
                '<plugin scripts>/prd pack check <pack dir> <A> <B>; echo "prd-pack-exit=$?"',
                "prd change pack docs/prd/<slug> <name> 0.1.0 --lift", "no dry run (pack lifted)"):
        assert cmd in t, cmd
    # the PRD's own output lines, quoted as it gives them
    for line in ("share no custom contract type; there is no pack to write", "glob matches no file",
                 "the validator accepts it; a sample must be refused", "no bad.* sample",
                 "validator fails from the pack folder: <line>", "is not a custom row of section 7"):
        assert line in t, line


def test_procedure_writes_nothing_outside_the_decided_pack():
    t = flat(RUN)
    for s in ("Until the owner has replied to step 3's proposal, nothing is written",
              "With no one to answer", "write nothing: end with the proposal as the report",
              "Neither PRD is edited, at any step.", "No marketplace file, no remote.",
              "Commit** only when the check exits `0`", "never `--no-verify`. Nothing is pushed.",
              "Run neither: no push, no publish, no install, no lift.",
              "never change a validator to pass", "never stash it",
              "Never leave the item out yourself", "The check reports that itself",
              "write nothing: show the new comparison as a new step 3 proposal",
              "is not a side", "never initialised"):
        assert s in t, s
    assert "--no-verify" not in t.replace("never `--no-verify`", "")


def test_procedure_never_runs_an_install_or_a_push():
    for path in (SKILL, RUN, COMMAND):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith(("git push", "claude plugin install", "claude plugin marketplace add")):
                raise AssertionError(f"{path.name}: {line}")


# --- the command ---

def test_command_invokes_the_skill():
    fm = frontmatter(COMMAND)
    assert set(fm) == {"description"} and fm["description"].endswith("(prd-toolkit)")
    t = flat(COMMAND)
    assert "Invoke the prd-toolkit:authoring-packs skill first" in t
    assert "running-a-pack.md" in t and "$ARGUMENTS" in t and "<PRD folder A> <PRD folder B> [<pack name>]" in t


# --- the edits ---

def test_changing_prds_names_the_lift():
    a = CHANGING.read_text(encoding="utf-8")
    s = " ".join(a[a.index("## Packs and retargeting"):a.index("## Non-negotiable rules")].split())
    for needle in ('<plugin scripts>/prd change pack docs/prd/<slug> <name> <X.Y.Z> --lift; echo "prd-change-exit=$?"',
                   '<plugin scripts>/prd hooks install docs/prd/<slug>; echo "prd-hooks-exit=$?"',
                   "`--dry-run 'no dry run (pack lifted)'`", "`pack <name> <X.Y.Z> lifted; no dry run (pack lifted)`",
                   "`pack <name> <X.Y.Z> lifted; pending`", "--source", "you never install it",
                   "<the PRD folder> has uncommitted changes; commit or set them aside first"):
        assert needle in s, needle
    assert s.index("A new pack version is a scripted patch.") < s.index("A lift is a scripted patch too.")
    assert "(a version move or a lift, below, is not one)" in s
    # the approval commits the vendored pack (AC-060.9): no hand commit of it between `hooks install` and the approval
    lift = s[s.index("A lift is a scripted patch too."):]
    order = [lift.index(x) for x in ("--lift; echo", "prd hooks install docs/prd/<slug>",
                                     "`approve` stages the vendored pack and `.prd-toolkit/pack-sources.json`",
                                     "step 4's lint", "--dry-run 'no dry run (pack lifted)'")]
    assert order == sorted(order)
    assert "`git add .prd-toolkit`" not in lift and "chore: vendor pack" not in lift
    assert "never the pack folder or `pack-sources.json`" in lift


def test_adopting_prds_names_the_pack_command_and_the_area_url():
    t = flat(ADOPTING)
    assert "is the moment for `/prd-toolkit:prd-pack`" in t
    assert "`url <address>`" in t and "Ask the owner for it" in t and "never guessed" in t


def test_handling_errors_records_the_url_and_names_the_areas():
    run = flat(ERROR_RUN)
    assert "--evidence-file <TMP>/evidence.txt --url '<address>'; echo \"prd-error-exit=$?\"" in run
    assert "<scripts>/prd error url docs/prd/<slug> <E-nnn> '<address>'; echo \"prd-error-exit=$?\"" in run
    assert "never guess or build one" in run
    assert "Show the user: the entry and its class; its areas" in run
    assert "`prd error new … --url <address>`" in flat(ERROR_SKILL)
    assert "<scripts>/prd gates list docs/prd/<slug> --json; echo \"prd-gates-exit=$?\"" in run
    assert 'git commit -m "docs(prd): set the URL of <E-nnn>" -m "Refs: <E-nnn>"' in run


def test_old_vendored_copies_are_named():
    for path in (ERROR_RUN, ADOPTING):
        assert "holds no `prd_pack.py`, the vendored copy predates 0.8.12" in flat(path), path.name


def test_references_document_the_url_and_the_pack_from_two_prds():
    f = flat(FORMAT)
    for needle in ("URL: <address>", "`prd_error.py url <prd_dir> <E-id> <address>`",
                   "<E-id>: URL: must start with http:// or https:// and hold no white space",
                   "Target: url https://example.com/orders",
                   "Target: url must start with http:// or https:// and hold no white space"):
        assert needle in f, needle
    c = flat(CONTRACT_TYPES)
    for needle in ("### A pack written from two PRDs", "prd pack compare <prd A> <prd B>",
                   "prd pack check <pack dir> <prd A> <prd B>", "samples/<type>/bad.*",
                   "prd change pack <prd dir> <name> <X.Y.Z> --lift", "no dry run (pack lifted)"):
        assert needle in c, needle
