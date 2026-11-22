"""Shared helper of the error-replay characterization tests.

Everything here comes from docs/prd/prd-toolkit/testing.md (Harness; Fixtures, error-replay/files; Setup steps,
the error-replay paragraph and its table) and from the header of test-cases/error-replay.yaml: the scratch
repository <tmp>/repo, the environment that every run, every step's git command and the test's own git commands
use, the names a case's text holds (<bug>, <test>, <fix>, <merge>, <many>, FULL(<rev>), HEAD7, ERROR, LINT, HELP,
<tmp>), the way a command text becomes its argument list, and the effect LEFT_AS_IT_WAS.

A setup step that cannot be applied (a git command that exits other than 0, a line or a text it does not find)
raises SetupError inside the `case` fixture, so the test ends as an error, not a failure.

Three fixture texts start with a citation line of another PRD's T-id; this file never holds such a line whole
(testing.md, Layout): it builds the lines it deletes from parts.
"""
from __future__ import annotations

import functools
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml

from status_next_support import N0  # testing.md, Borrowed steps and helpers

REPO = Path(__file__).resolve().parents[3]  # tests/prd/<file> -> tests -> prd-toolkit -> the repository root
SCRIPTS_DIR = REPO / "prd-toolkit" / "scripts"
SCRIPTS = {  # the names the case file's header defines
    "ERROR": SCRIPTS_DIR / "prd_error.py",
    "LINT": SCRIPTS_DIR / "prd_lint.py",
    "HELP": SCRIPTS_DIR / "prd_help.py",
}
FIXTURE = REPO / "docs" / "prd" / "prd-toolkit" / "contracts" / "fixtures" / "error-replay" / "files.yaml"
ORDERS = Path("docs") / "prd" / "orders"
AT_PRD = "@" + "prd"

# testing.md, Subprocess environment and the error-replay paragraph: what a run never inherits, and what it adds.
_DROPPED_ENV = (
    "PYTHONIOENCODING", "PYTHONPATH", "PYTHONHOME", "PRD_LINT_CI", "PRD_HELP_FILE",
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "PRD_PLUGINS_FILE",
)
_GIT_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
TAGS = ("bug", "test", "fix", "merge")

RUN_TIMEOUT = 300  # seconds; a harness choice, so a hung command ends the test
RMANY_LIMIT = 10  # runs of fast-import before RMANY gives up; a harness choice (three are enough, p > 0.99)
RMANY_COMMITS = 20_000

REPLAY = "python ERROR replay docs/prd/orders E-001"
CHECK = "python ERROR check docs/prd/orders start..HEAD"


class SetupError(Exception):
    """A Setup step could not be applied: the test ends as an error, not a failure."""


@functools.lru_cache(maxsize=None)
def _fixture() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def files(key: str) -> str:
    """files.<key>: the text at that key of fixture error-replay/files."""
    texts = _fixture()
    if key not in texts:
        raise SetupError(f"fixture error-replay/files has no key {key!r}")
    return texts[key]


@dataclass
class Result:
    exit: int
    stdout: str
    stderr: str
    seconds: float
    before: dict | None = None
    after: dict | None = None
    scratch_after: list[str] = field(default_factory=list)

    def detail(self) -> str:
        return f"exit {self.exit}\n--- stdout\n{self.stdout}--- stderr\n{self.stderr}"


# -- text edits the steps make ------------------------------------------------------------------------------------

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise SetupError(f"{path} does not exist")
    return path.read_text(encoding="utf-8").split("\n")


def _write_lines(path: Path, lines: list[str]) -> None:
    path.write_bytes("\n".join(lines).encode("utf-8"))


def _heading_level(line: str) -> int:
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def _replace_under(path: Path, heading: str, old: str, new: str) -> None:
    """Under `heading` (up to the next heading of its level or higher), the one line `old` becomes `new`."""
    lines = _read_lines(path)
    found = [i for i, line in enumerate(lines) if line == heading]
    if len(found) != 1:
        raise SetupError(f"{path}: expected one heading {heading!r}, found {len(found)}")
    start, level = found[0] + 1, _heading_level(heading)
    end = next((j for j in range(start, len(lines)) if 0 < _heading_level(lines[j]) <= level), len(lines))
    hits = [i for i in range(start, end) if lines[i] == old]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {old!r} under {heading!r}, found {len(hits)}")
    lines[hits[0]] = new
    _write_lines(path, lines)


def _delete_line(path: Path, line: str) -> None:
    lines = _read_lines(path)
    hits = [i for i, text in enumerate(lines) if text == line]
    if len(hits) != 1:
        raise SetupError(f"{path}: expected one line {line!r}, found {len(hits)}")
    del lines[hits[0]]
    _write_lines(path, lines)


def _set_line(path: Path, number: int, new: str) -> None:
    """Line `number` (from 1) becomes `new`."""
    lines = _read_lines(path)
    if number > len(lines) or (number == len(lines) and lines[-1] == ""):
        raise SetupError(f"{path} has no line {number}")
    lines[number - 1] = new
    _write_lines(path, lines)


def _replace_in_line(path: Path, number: int, old: str, new: str) -> None:
    lines = _read_lines(path)
    if number > len(lines) or old not in lines[number - 1]:
        raise SetupError(f"{path}: line {number} does not hold {old!r}")
    lines[number - 1] = lines[number - 1].replace(old, new, 1)
    _write_lines(path, lines)


def ledger_with(key: str, line: str) -> str:
    """files.<key> with its line `Resolution: -` replaced by `line`, every other line as it was."""
    lines = files(key).split("\n")
    hits = [i for i, text in enumerate(lines) if text == "Resolution: -"]
    assert len(hits) == 1, f"files.{key} holds {len(hits)} lines `Resolution: -`"
    lines[hits[0]] = line
    return "\n".join(lines)


# -- assertion helpers (testing.md, Harness, Assertions) ----------------------------------------------------------

def _deep_same(a, b) -> bool:
    """JSON equality that tells a boolean from a number (YAML `1` is never JSON `true`)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, dict) or isinstance(b, dict):
        return isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b) \
            and all(_deep_same(a[k], b[k]) for k in a)
    if isinstance(a, list) or isinstance(b, list):
        return isinstance(a, list) and isinstance(b, list) and len(a) == len(b) \
            and all(_deep_same(x, y) for x, y in zip(a, b))
    return a == b


def one_json_line(stdout: str) -> dict:
    """The whole stdout must be one line ending in a newline; that line parsed as one JSON object."""
    assert stdout.endswith("\n") and len(stdout.splitlines()) == 1, f"stdout is not one line:\n{stdout}"
    doc = json.loads(stdout)
    assert isinstance(doc, dict), f"stdout is not a JSON object:\n{stdout}"
    return doc


def json_at(doc, path: str):
    """The value at a `.`-joined path of object keys and list indexes (`""` is the document itself)."""
    value = doc
    if path == "":
        return value
    for part in path.split("."):
        try:
            value = value[int(part)] if isinstance(value, list) else value[part]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise AssertionError(f"the document has no value at {path!r}: {doc}") from exc
    return value


def worktree_paths(porcelain: str) -> list[str]:
    """The paths of `git worktree list --porcelain`, each with symbolic links resolved."""
    return [os.path.realpath(line[len("worktree "):]) for line in porcelain.splitlines()
            if line.startswith("worktree ")]


def assert_left_as_it_was(res: Result) -> None:
    """LEFT_AS_IT_WAS (case file header): worktree list and status the same before and after; scratch empty."""
    assert res.before is not None and res.after is not None, "the scratch repository was not snapshotted"
    assert res.after["worktrees"] == res.before["worktrees"], \
        f"git worktree list changed:\n--- before\n{res.before['worktrees']}--- after\n{res.after['worktrees']}"
    assert res.after["status"] == res.before["status"], \
        f"git status changed:\n--- before\n{res.before['status']}--- after\n{res.after['status']}"
    assert res.scratch_after == [], f"<tmp>/scratch holds {res.scratch_after}"


def assert_worktrees_same_and_scratch_empty(res: Result) -> None:
    assert res.before is not None and res.after is not None, "the scratch repository was not snapshotted"
    assert res.after["worktrees"] == res.before["worktrees"], \
        f"git worktree list changed:\n--- before\n{res.before['worktrees']}--- after\n{res.after['worktrees']}"
    assert res.scratch_after == [], f"<tmp>/scratch holds {res.scratch_after}"


# -- the case -----------------------------------------------------------------------------------------------------

class Case:
    """One error-replay case: <tmp>, its scratch repository <tmp>/repo, its names, its runs."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.repo = tmp / "repo"
        self.scratch = tmp / "scratch"
        self.many: str | None = None
        self._frozen: dict[str, str] | None = None
        self.add_finalizer = None  # the `case` fixture sets it to request.addfinalizer (step RRO's mode reset)

    # environment and git

    def env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        env = dict(os.environ)
        for name in _DROPPED_ENV:
            env.pop(name, None)
        env.update(_GIT_ENV)
        env["TMPDIR"] = str(self.scratch)
        for name, value in (extra or {}).items():
            env[name] = self.expand(value)
        return env

    def git(self, cwd: Path, *args: str, stdin: bytes | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=cwd, env=self.env(), input=stdin,
                              capture_output=True, timeout=RUN_TIMEOUT)

    def _sgit(self, root: Path, *args: str, stdin: bytes | None = None) -> subprocess.CompletedProcess:
        proc = self.git(root, *args, stdin=stdin)
        if proc.returncode != 0:
            raise SetupError(f"git {' '.join(args)} exited {proc.returncode} in {root}: "
                             f"{proc.stderr.decode('utf-8', 'replace')}")
        return proc

    def _commit(self, root: Path, message: str) -> None:
        self._sgit(root, "add", "-A")
        self._sgit(root, "commit", "-q", "-m", message)

    def _tag(self, root: Path, name: str) -> None:
        self._sgit(root, "tag", name)

    # names (testing.md, the error-replay paragraph)

    def _compute_names(self) -> dict[str, str]:
        names: dict[str, str] = {}
        if not (self.repo / ".git").exists():
            return names
        for tag in TAGS:
            if self.git(self.repo, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}").returncode != 0:
                continue
            proc = self.git(self.repo, "rev-parse", "--short=7", tag)
            assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
            names[f"<{tag}>"] = proc.stdout.decode("utf-8").removesuffix("\n")
        if self.many is not None:
            names["<many>"] = self.many
        head = self.git(self.repo, "rev-parse", "HEAD")
        if head.returncode == 0:
            names["HEAD7"] = head.stdout.decode("utf-8").removesuffix("\n")[:7]
        return names

    def names(self) -> dict[str, str]:
        return self._frozen if self._frozen is not None else self._compute_names()

    def freeze(self) -> None:
        """Take the names after the case's last step."""
        self._frozen = self._compute_names()

    def full(self, rev: str) -> str:
        proc = self.git(self.repo, "rev-parse", rev)
        assert proc.returncode == 0, f"git rev-parse {rev}: {proc.stderr.decode('utf-8', 'replace')}"
        return proc.stdout.decode("utf-8").removesuffix("\n")

    def expand(self, text: str, *, quote: bool = False) -> str:
        """Replace FULL(<rev>), the tag names, <many>, HEAD7 and <tmp> (and, in a command, ERROR, LINT, HELP)."""
        q = shlex.quote if quote else (lambda s: s)
        text = re.sub(r"FULL\(([^)]*)\)", lambda m: self.full(m.group(1)), text)
        for name, value in self.names().items():
            text = text.replace(name, value)
        text = text.replace("<tmp>", q(str(self.tmp)))
        if quote:
            text = re.sub(r"\b(ERROR|LINT|HELP)\b", lambda m: q(str(SCRIPTS[m.group(1)])), text)
        left = re.findall(r"<(?:bug|test|fix|merge|many)>", text)
        if left:
            raise SetupError(f"no value for {left} in {text!r}: the steps set no such name")
        return text

    def expand_value(self, value):
        if isinstance(value, str):
            return self.expand(value)
        if isinstance(value, list):
            return [self.expand_value(v) for v in value]
        if isinstance(value, dict):
            return {k: self.expand_value(v) for k, v in value.items()}
        return value

    def argv(self, command: str) -> list[str]:
        """The command's argument list: names replaced, split as a POSIX shell splits, `python` the interpreter."""
        words = shlex.split(self.expand(command, quote=True))
        if words and words[0] == "python":
            words[0] = sys.executable
        return words

    # snapshots and runs

    def state(self, status_in: Path | None = None) -> dict | None:
        if not (self.repo / ".git").exists():
            return None
        wt = self.git(self.repo, "worktree", "list", "--porcelain")
        st = self.git(status_in or self.repo, "status", "--porcelain")
        assert wt.returncode == 0 and st.returncode == 0, \
            (wt.stderr + st.stderr).decode("utf-8", "replace")
        return {"worktrees": wt.stdout.decode("utf-8"), "status": st.stdout.decode("utf-8")}

    def scratch_entries(self) -> list[str]:
        return sorted(os.listdir(self.scratch))

    def run(self, command: str, cwd: Path | None = None, env: dict[str, str] | None = None,
            status_in: Path | None = None) -> Result:
        """Run one command of the case, the repository snapshotted just before and just after it."""
        argv = self.argv(command)
        before = self.state(status_in)
        start = time.monotonic()
        proc = subprocess.run(argv, cwd=cwd or self.repo, env=self.env(env), capture_output=True,
                              timeout=RUN_TIMEOUT)
        seconds = time.monotonic() - start
        after = self.state(status_in)
        return Result(proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"), seconds,
                      before, after, self.scratch_entries())

    def popen(self, command: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.Popen:
        """Start one command in the background (T-079.4), in the test's own process group."""
        return subprocess.Popen(self.argv(command), cwd=cwd or self.repo, env=self.env(env),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # expectations, every value expanded first

    def expect(self, res: Result, *, exit: int | None = None, stdout: str | None = None,
               stderr: str | None = None) -> None:
        if exit is not None:
            assert res.exit == exit, res.detail()
        if stdout is not None:
            assert res.stdout == self.expand(stdout), res.detail()
        if stderr is not None:
            assert res.stderr == self.expand(stderr), res.detail()

    def expect_lines(self, text: str, lines: list[str]) -> None:
        """stdout_exact_lines / stderr_exact_lines: str.splitlines() equals the list."""
        assert text.splitlines() == [self.expand(line) for line in lines], text

    def expect_json(self, res: Result, mapping: dict) -> dict:
        doc = one_json_line(res.stdout)
        want = self.expand_value(mapping)
        assert _deep_same(doc, want), f"--- got\n{doc}\n--- want\n{want}"
        return doc

    def expect_json_at(self, res: Result, mapping: dict) -> dict:
        doc = one_json_line(res.stdout)
        for path, value in mapping.items():
            got, want = json_at(doc, path), self.expand_value(value)
            assert _deep_same(got, want), f"at {path!r}: got {got!r}, want {want!r}\n{doc}"
        return doc

    def errors_md(self) -> bytes:
        return (self.repo / ORDERS / "errors.md").read_bytes()

    def expect_errors_md(self, text: str) -> None:
        got = self.errors_md().decode("utf-8")
        want = self.expand(text)
        assert got == want, f"--- errors.md\n{got}--- want\n{want}"

    # steps (testing.md, Setup steps, the error-replay table)

    def step(self, spec: str, resolution: str | None) -> None:
        """Run one step; "<step> in <X>" is that step with <X> in place of <tmp>/repo."""
        name, _, where = spec.partition(" in ")
        root = Path(self.expand(where)) if where else self.repo
        fn = getattr(self, f"_step_{name}", None)
        if fn is None:
            raise SetupError(f"no error-replay step {name!r}")
        fn(root, resolution)

    def _step_R0(self, root: Path, resolution) -> None:
        N0(root)
        for key, value in (("user.name", "Sample"), ("user.email", "sample@example.com"),
                           ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null")):
            self._sgit(root, "config", key, value)
        _delete_line(root / "tests" / "test_orders.py", f"# {AT_PRD} T-006.1")
        _delete_line(root / "tests" / "test_orders.py", f"# {AT_PRD} T-007.1")
        _replace_under(root / ORDERS / "prd.md", "## 8. Adoption map", "Not applicable: new project.",
                       "See adoption.md.")
        for key, rel in (("adoption", ORDERS / "adoption.md"), ("testing", ORDERS / "testing.md"),
                         ("one_py", Path("tools/one.py")), ("slow_py", Path("tools/slow.py")),
                         ("needs_py", Path("tools/needs.py")), ("gitignore", Path(".gitignore")),
                         ("importer", Path("src/importer.py")), ("calc_bug", Path("src/calc.py"))):
            _write(root / rel, files(key))
        self._commit(root, "base")
        self._tag(root, "bug")

    def _test_step(self, root: Path, key: str, rels: tuple[str, ...]) -> None:
        for rel in rels:
            _write(root / rel, files(key))
        self._commit(root, "test")
        self._tag(root, "test")

    def _step_RT(self, root: Path, resolution) -> None:
        self._test_step(root, "test_total", ("tests/test_total.py",))

    def _step_RTP(self, root: Path, resolution) -> None:
        self._test_step(root, "test_pass", ("tests/test_total.py",))

    def _step_RTS(self, root: Path, resolution) -> None:
        self._test_step(root, "test_total", ("tests/test total.py",))

    def _step_RTD(self, root: Path, resolution) -> None:
        self._test_step(root, "test_total", ("tests/a$b;c.py",))

    def _step_RTI(self, root: Path, resolution) -> None:
        self._test_step(root, "test_inv", ("tests/test_a.py", "tests/test_b.py"))

    def _step_RF(self, root: Path, resolution) -> None:
        _write(root / "src/calc.py", files("calc_fix"))
        self._commit(root, "fix")
        self._tag(root, "fix")

    def _step_RS(self, root: Path, resolution) -> None:
        _write(root / "src/calc.py", files("calc_still"))
        self._commit(root, "fix")
        self._tag(root, "fix")

    def _step_RFA(self, root: Path, resolution) -> None:
        _write(root / "src/calc.py", files("calc_fix"))
        importer = root / "src/importer.py"
        if not importer.is_file():
            raise SetupError(f"{importer} does not exist")
        text = importer.read_text(encoding="utf-8")
        importer.write_bytes((text + ("" if text.endswith("\n") or not text else "\n") + "y = 2\n").encode("utf-8"))
        self._commit(root, "fix")
        self._tag(root, "fix")

    def _step_RM(self, root: Path, resolution) -> None:
        self._sgit(root, "switch", "-q", "-c", "side")
        _write(root / "src/calc.py", files("calc_fix"))
        self._commit(root, "fix on side")
        self._sgit(root, "switch", "-q", "-")
        _write(root / "notes.txt", "notes\n")
        self._commit(root, "unrelated")
        self._sgit(root, "merge", "-q", "--no-ff", "-m", "merge", "side")
        self._tag(root, "merge")

    def _step_RL(self, root: Path, resolution) -> None:
        _write(root / "tests/test_later.py", files("test_later"))
        self._commit(root, "later")

    def _step_RK(self, root: Path, resolution) -> None:
        self._tag(root, "start")

    def _write_ledger(self, root: Path, resolution) -> None:
        if resolution is None:
            raise SetupError("step RE needs the case's resolution")
        text = files("ledger")
        if text.count("RESOLUTION") != 1:
            raise SetupError("files.ledger does not hold the word RESOLUTION once")
        _write(root / ORDERS / "errors.md", text.replace("RESOLUTION", self.expand(resolution)))

    def _step_RE(self, root: Path, resolution) -> None:
        self._write_ledger(root, resolution)
        self._commit(root, "resolve")

    def _step_REU(self, root: Path, resolution) -> None:
        self._write_ledger(root, resolution)

    def _step_RO(self, root: Path, resolution) -> None:
        _write(root / ORDERS / "errors.md", files("ledger_open"))
        self._commit(root, "open")

    def _step_RP(self, root: Path, resolution) -> None:
        _write(root / ORDERS / "errors.md", files("ledger_proposed"))
        self._commit(root, "proposed")

    def _step_RG(self, root: Path, resolution) -> None:
        _write(root / ORDERS / "errors.md", files("ledger_spec"))
        self._commit(root, "spec gap")

    def _step_RW(self, root: Path, resolution) -> None:
        _write(root / "tests/test_total.py", files("test_pass"))

    def _step_RN(self, root: Path, resolution) -> None:
        _write(root / ".ready", "ready\n")
        _set_line(root / ORDERS / "testing.md", 8,
                  "| integration | `pytest tests/integration` | local | build | `python3 tools/needs.py` |  |")

    def _step_RA(self, root: Path, resolution) -> None:
        """Line 8 names `tools/absent`, which no step writes, so the operating system cannot start it."""
        _set_line(root / ORDERS / "testing.md", 8,
                  "| integration | `pytest tests/integration` | local | build | `tools/absent` |  |")
        self._commit(root, "absent")

    def _step_RIW(self, root: Path, resolution) -> None:
        """Line 8's One test is a program that exits 0 only inside a git checkout (`git rev-parse` prints true)."""
        program = ("python3 -c \"raise SystemExit(0 if __import__('subprocess').run(['git', 'rev-parse', "
                   "'--is-inside-work-tree'], capture_output=True, text=True).stdout.split() == ['true'] "
                   "else 1)\"")
        _set_line(root / ORDERS / "testing.md", 8,
                  f"| integration | `pytest tests/integration` | local | build | `{program}` |  |")
        self._commit(root, "git check")

    def _restore_scratch_modes(self) -> None:
        """Set the mode of every folder under <tmp>/scratch back to 0o700, so that tmp_path can be removed."""
        if not self.scratch.is_dir():
            return
        for dirpath, dirnames, _ in os.walk(self.scratch):
            for name in dirnames:
                path = os.path.join(dirpath, name)
                if not os.path.islink(path):
                    os.chmod(path, 0o700)

    def _step_RRO(self, root: Path, resolution) -> None:
        """Line 8's One test is `python3 tools/ro.py`, which leaves the folder ro/x of each run's clone read-only."""
        if self.add_finalizer is None:
            raise SetupError("step RRO needs the `case` fixture's finalizer")
        self.add_finalizer(self._restore_scratch_modes)  # when the test ends: skipped, passed or failed
        if os.geteuid() == 0:
            pytest.skip("step RRO: root may remove a folder whatever its mode")
        _write(root / "tools/ro.py", files("ro_py"))
        _set_line(root / ORDERS / "testing.md", 8,
                  "| integration | `pytest tests/integration` | local | build | `python3 tools/ro.py` |  |")
        self._commit(root, "read-only")

    def _step_RQ(self, root: Path, resolution) -> None:
        testing = root / ORDERS / "testing.md"
        _set_line(testing, 5, "| Level | Harness command | Environment | Gate | ONE TEST | Timeout |")
        _replace_in_line(testing, 8, "`python3 tools/one.py`", '`python3 "tools/one.py"`')
        self._commit(root, "quoted")

    def _step_RC(self, root: Path, resolution) -> None:
        _write(root / ORDERS / "testing.md", files("testing_nocol"))
        self._commit(root, "no column")

    def _step_RB(self, root: Path, resolution) -> None:
        _write(root / ORDERS / "testing.md", files("testing_bad"))

    def _step_RX(self, root: Path, resolution) -> None:
        adoption = root / ORDERS / "adoption.md"
        if not adoption.is_file():
            raise SetupError(f"{adoption} does not exist")
        adoption.unlink()
        _replace_under(root / ORDERS / "prd.md", "## 8. Adoption map", "See adoption.md.",
                       "Not applicable: new project.")
        self._commit(root, "no map")

    def _step_RWT(self, root: Path, resolution) -> None:
        self._sgit(root, "worktree", "add", "-q", "--detach", str(self.tmp / "wt"), "HEAD")

    def _step_RNW(self, root: Path, resolution) -> None:
        """An empty regular file at `.git/worktrees`, where the git folder holds no entry of that name; no commit."""
        entry = root / ".git" / "worktrees"
        if os.path.lexists(entry):
            raise SetupError(f"{entry} already exists")
        entry.write_bytes(b"")

    def _step_RMANY(self, root: Path, resolution) -> None:
        for k in range(1, RMANY_LIMIT + 1):
            chunks = []
            for i in range(1, RMANY_COMMITS + 1):
                message = f"m{k}-{i}"
                chunks.append(f"commit refs/heads/many-{k}\n"
                              f"committer Sample <sample@example.com> 0 +0000\n"
                              f"data {len(message.encode('utf-8'))}\n"
                              f"{message}\n")
            self._sgit(root, "fast-import", "--quiet", stdin="".join(chunks).encode("utf-8"))
            shas = self._sgit(root, "rev-list", "--branches=many-*").stdout.decode("utf-8").split()
            seen: dict[str, str] = {}
            for sha in shas:
                prefix = sha[:7]
                if prefix in seen and seen[prefix] != sha:
                    self.many = prefix
                    return
                seen[prefix] = sha
        raise SetupError(f"RMANY found no two commits sharing 7 hex digits after {RMANY_LIMIT} runs")


# -- waits (testing.md, Harness, Waits: T-079.4) -------------------------------------------------------------------

def wait_for_number(path: Path, seconds: float) -> int:
    """Wait up to `seconds` until `path` holds a number; a wait that runs out fails the test."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            text = path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            text = ""
        if text.isdigit():
            return int(text)
        time.sleep(0.05)
    raise AssertionError(f"{path} held no number after {seconds} s")


def wait_until_gone(pid: int, seconds: float) -> bool:
    """True once no process has the ID `pid` (os.kill with signal 0 raises ProcessLookupError)."""
    deadline = time.monotonic() + seconds
    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def send_sigint(proc: subprocess.Popen) -> None:
    """SIGINT to the command's own process, never to a process group."""
    os.kill(proc.pid, signal.SIGINT)


# -- the fixture ---------------------------------------------------------------------------------------------------

@pytest.fixture
def case(request, tmp_path, monkeypatch) -> Case:
    """<tmp>/scratch made and the git variables set, then the case's steps run in order; names then taken."""
    steps, resolution = getattr(request, "param", ((), None))
    c = Case(tmp_path)
    c.add_finalizer = request.addfinalizer
    c.scratch.mkdir()
    for name, value in _GIT_ENV.items():
        monkeypatch.setenv(name, value)
    for spec in steps:
        c.step(spec, resolution)
    c.freeze()
    return c


def given(*steps: str, resolution: str | None = None):
    """Mark a test with its case's `setup:` list and `resolution`; the `case` fixture runs the steps."""
    ident = re.sub(r"[^A-Za-z0-9+]+", "_", "+".join(steps)) or "no-step"
    return pytest.mark.parametrize("case", [(steps, resolution)], indirect=True, ids=[ident])
