#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0", "sqlglot>=25", "openapi-spec-validator>=0.7"]
# ///
"""Print the PRD's technical view: its stack, architecture, registries and contract types beside the code at HEAD.
Exit 0 printed or written, 1 an --out path refused, 2 usage or tool error."""
import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # leave .prd-toolkit/ as it was (AC-267.3)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prdlint import deps  # noqa: E402

for _module, _package in (("yaml", "pyyaml"), ("sqlglot", "sqlglot"), ("openapi_spec_validator", "openapi-spec-validator")):
    deps.require(_module, _package)

from prdlint import model, trd  # noqa: E402

REFUSED = "refused: --out must lie outside the PRD folder and .prd-toolkit/"


def _within(path: Path, folder: Path) -> bool:
    return path == folder or folder in path.parents


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="prd_trd.py", description="Print the PRD's technical view.")
    parser.add_argument("prd_dir", help="the PRD folder, in a git work tree with a commit")
    parser.add_argument("--out", metavar="FILE",
                        help="write the view to FILE in place of stdout, creating the file but not its folder")
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code in (0, None) else 2
    folder = Path(args.prd_dir).resolve()
    names = {p.name: p for p in folder.iterdir()} if folder.is_dir() else {}
    if "prd.md" not in names or not names["prd.md"].is_file():  # the exact name, as the loader reads it
        print(f"prd_trd: {folder}: no prd.md", file=sys.stderr)
        return 2
    top = model.git_toplevel(folder)
    if top is None:
        print(f"prd_trd: {folder} is not in a git work tree", file=sys.stderr)
        return 2
    top = top.resolve()
    sha = trd.head(top)
    if sha is None:
        print("prd_trd: the repository has no commit", file=sys.stderr)
        return 2
    if args.out is not None:
        out = Path(args.out).resolve()
        if _within(out, folder) or _within(out, top / ".prd-toolkit"):
            print(REFUSED, file=sys.stderr)
            return 1
    text = trd.view(model.load(folder), top, sha).encode("utf-8")
    if args.out is None:
        sys.stdout.buffer.write(text)
        return 0
    try:
        with open(args.out, "wb") as f:
            f.write(text)
    except OSError as e:
        print(f"prd_trd: cannot write {args.out}: {e.strerror or e}", file=sys.stderr)
        return 2
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # the PRD may hold text outside ASCII; never crash in a C locale
        _stream.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
