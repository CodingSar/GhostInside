#!/usr/bin/env python3
"""Deterministic structure check for product code (meta/core/defaults/architecture.md).

Checks the module and slice layout, the _about.md catalogs, forbidden folder
and file names, and the size caps. Import boundaries are language specific and
belong to the stack's boundary checker, not to this script.

Usage:
  structure.py --ext .py --test '^test_.*\\.py$' [--root src] [--index index]
               [--handler handler] [--case kebab|snake|camel|pascal]
               [--max-lines 200] [--max-test-lines 300] [--max-slices 12]

Exit 0 when clean, 1 with one FAIL line per finding otherwise.
Python standard library only. This is harness tooling, not the product stack.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT_DIRS = {"app", "shared", "modules"}
MODULE_DIRS = {"slices", "migrations"}
FORBIDDEN = {
    "utils", "util", "helpers", "helper", "services", "service",
    "common", "lib", "misc", "manager", "managers",
}
IGNORED_DIRS = {"node_modules", "dist", "build", "target", "venv"}
CATALOG = "_about.md"
CASES = {
    "kebab": r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$",
    "snake": r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$",
    "camel": r"^[a-z][a-zA-Z0-9]*$",
    "pascal": r"^[A-Z][a-zA-Z0-9]*$",
}


def ignored(path):
    name = path.name
    return name.startswith((".", "__")) or name in IGNORED_DIRS


def subdirs(path):
    return sorted(p for p in path.iterdir() if p.is_dir() and not ignored(p))


def named_in(catalog, name):
    """True when the catalog names it in backticks, as architecture.md asks."""
    return catalog.exists() and f"`{name}`" in catalog.read_text()


def has_stem(folder, stem, exts):
    return any(p.is_file() and p.stem == stem and p.suffix in exts for p in folder.iterdir())


def check(args):
    root = Path(args.root)
    parts = [e.strip() for e in args.ext.split(",") if e.strip()]
    exts = {e if e.startswith(".") else f".{e}" for e in parts}
    if not exts:
        return ["--ext: no extensions given"]
    case = re.compile(CASES[args.case]) if args.case else None
    test_re = re.compile(args.test)
    fails = []

    def bad(path, msg):
        fails.append(f"{path}: {msg}")

    if not root.is_dir():
        return [f"{root}: source root missing"]

    if not (root / CATALOG).exists():
        bad(root, f"no {CATALOG} catalog")
    for d in subdirs(root):
        if d.name not in ROOT_DIRS:
            bad(d, f"top-level folder must be one of {', '.join(sorted(ROOT_DIRS))}")

    modules = root / "modules"
    for mod in subdirs(modules) if modules.is_dir() else []:
        if case and not case.match(mod.name):
            bad(mod, f"module name is not {args.case} case")
        if not named_in(root / CATALOG, mod.name):
            bad(mod, f"module not named in {root / CATALOG}")
        if not (mod / CATALOG).exists():
            bad(mod, f"no {CATALOG} catalog")
        if not has_stem(mod, args.index, exts):
            bad(mod, f"no {args.index} entry file")
        for d in subdirs(mod):
            if d.name not in MODULE_DIRS:
                bad(d, f"module folder must be one of {', '.join(sorted(MODULE_DIRS))}")
        slices = subdirs(mod / "slices") if (mod / "slices").is_dir() else []
        if len(slices) > args.max_slices:
            bad(mod, f"{len(slices)} slices, cap {args.max_slices}; propose a module split")
        for sl in slices:
            if case and not case.match(sl.name):
                bad(sl, f"slice name is not {args.case} case")
            if not named_in(mod / CATALOG, sl.name):
                bad(sl, f"slice not named in {mod / CATALOG}")
            if not has_stem(sl, args.handler, exts):
                bad(sl, f"no {args.handler} entry file")
            for d in subdirs(sl):
                bad(d, "slices are flat; no folders inside a slice")

    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(ignored(Path(part)) for part in rel.parts):
            continue
        # Files directly in the root may be language entry files (lib.rs, __init__.py).
        if p.stem.lower() in FORBIDDEN and not (p.is_file() and p.parent == root):
            bad(p, "forbidden name; put the code in the slice, module model, or shared kernel")
        if p.is_file() and p.suffix in exts:
            lines = len(p.read_text(errors="replace").splitlines())
            cap = args.max_test_lines if test_re.search(p.name) else args.max_lines
            if lines > cap:
                bad(p, f"{lines} lines, cap {cap}")
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="src")
    ap.add_argument("--ext", required=True, help="comma-separated source extensions, such as .py or .ts,.tsx")
    ap.add_argument("--test", required=True, help="regex on the file name that marks a test file")
    ap.add_argument("--index", default="index")
    ap.add_argument("--handler", default="handler")
    ap.add_argument("--case", choices=sorted(CASES), help="required case of module and slice names")
    ap.add_argument("--max-lines", type=int, default=200)
    ap.add_argument("--max-test-lines", type=int, default=300)
    ap.add_argument("--max-slices", type=int, default=12)
    fails = check(ap.parse_args(argv))
    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        return 1
    print("ok: structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
