"""`prd pack check`: a written pack against the two PRDs it was written from (FR-059). It writes nothing."""
import glob
import shlex
import shutil
import subprocess
from pathlib import Path

from . import packs
from .rules.contracts import _validator_timeout

SAMPLES = "samples"


def _globs(files) -> list[str]:
    return [files] if isinstance(files, str) else list(files)


def _matching(prd_dir: Path, files) -> list[str]:
    """The PRD's files that the type's glob or globs match, relative to the PRD folder, sorted; `**` spans folders."""
    found = {f for g in _globs(files) for f in glob.glob(g, root_dir=prd_dir, recursive=True)}
    return sorted(f for f in found if (prd_dir / f).is_file())


def _run(argv: list[str], cwd: Path, timeout: int) -> tuple[str | None, subprocess.CompletedProcess | None]:
    """(problem, None) when the validator cannot be run, else (None, the finished run)."""
    try:
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout)
    except FileNotFoundError:
        return f"validator not found: {argv[0]}", None
    except subprocess.TimeoutExpired:
        return f"validator timed out after {timeout}s", None
    except OSError:  # PermissionError, and every other reason the program cannot be run
        return f"validator not executable: {argv[0]}", None
    return None, done


def _failed(done: subprocess.CompletedProcess) -> str:
    """The first stderr line that is not blank, else the first such stdout line, else `exit <code>`."""
    lines = done.stderr.splitlines() + done.stdout.splitlines()
    return "validator failed: " + next((x for x in lines if x.strip()), f"exit {done.returncode}")


def _prd_findings(pack: packs.Pack, prds: list[tuple[str, Path]], timeout: int) -> list[str]:
    """Each type's validator on A's and then B's matching files, as lint runs a section 7 validator (AC-059.2)."""
    out = []
    for ct in pack.contract_types:
        for arg, prd_dir in prds:
            at = f"{arg}/prd.md: contract type {ct['type']}"
            files = _matching(prd_dir, ct["files"])
            if not files:
                out.append(f"{at}: glob matches no file")
                continue
            try:
                argv = packs.expand(ct["validator"], pack)
            except ValueError as e:
                out.append(f"{at}: validator does not parse: {e}")
                continue
            if not argv:
                continue
            problem, done = _run(argv + files, prd_dir, timeout)
            if problem:
                out.append(f"{at}: {problem}")
            elif done.returncode != 0:
                out.append(f"{at}: {_failed(done)}")
    return out


def _sample_findings(pack: packs.Pack, pack_arg: str, timeout: int) -> list[str]:
    """Each type's validator on each `samples/<type>/bad.*` file, from the pack folder; each must be refused
    (AC-059.3)."""
    out = []
    for ct in pack.contract_types:
        kind = ct["type"]
        folder = pack.root / SAMPLES / kind
        names = sorted(p.name for p in folder.iterdir() if p.name.startswith("bad.") and p.is_file()) if folder.is_dir() else []
        if not names:
            out.append(f"{pack_arg}/{SAMPLES}/{kind}: no bad.* sample; add a file the validator must refuse")
            continue
        for name in names:
            at = f"{pack_arg}/{SAMPLES}/{kind}/{name}"
            try:
                argv = packs.expand(ct["validator"], pack)
            except ValueError as e:
                out.append(f"{at}: validator does not parse: {e}")
                continue
            if not argv:
                continue
            problem, done = _run(argv + [f"{SAMPLES}/{kind}/{name}"], pack.root, timeout)
            if problem:
                out.append(f"{at}: {problem}")
            elif done.returncode == 0:
                out.append(f"{at}: the validator accepts it; a sample must be refused")
    return out


def _level_findings(pack: packs.Pack, pack_arg: str) -> list[str]:
    """Each `levels` item whose command's first word is not on PATH (AC-059.4)."""
    out = []
    for i, item in enumerate(pack.levels):
        try:
            words = shlex.split(item["command"])
        except ValueError:
            continue
        if words and shutil.which(words[0]) is None:
            out.append(f"{pack_arg}/{packs.MANIFEST}: levels[{i}] ({item['level']}): {words[0]} is not on PATH")
    return out


def check(pack_arg: str, prds: list[tuple[str, Path]]) -> list[str]:
    """Every finding, `<path>: <what>`, in AC-059.5's order: the manifest's one alone, else the PRD validator runs (A
    then B for each type), then the samples, then the levels. `prds` is (the folder as given, its path), A then B."""
    try:
        pack = packs.load_manifest(Path(pack_arg).resolve(), pack_arg)
    except packs.ManifestError as e:
        return [f"{pack_arg}/{packs.MANIFEST}: {e}"]
    timeout = _validator_timeout()
    return (_prd_findings(pack, prds, timeout) + _sample_findings(pack, pack_arg, timeout)
            + _level_findings(pack, pack_arg))


def split(finding: str) -> dict:
    """{"file", "message"}: the path before the finding's first `: `, then the rest (AC-059.6)."""
    file, _, message = finding.partition(": ")
    return {"file": file, "message": message}
