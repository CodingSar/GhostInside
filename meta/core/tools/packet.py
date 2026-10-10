#!/usr/bin/env python3
"""Print the research packet for one module and, optionally, one slice.

The packet is what workers need besides their guide: the effective
architecture and persistence rules, the stack, the review rules, and the
existing module and slice files. Every line carries its file and line number,
so plans and reports can cite rules exactly. Deterministic: no model reads
or copies these files.

Usage: packet.py <module> [<slice>]

Exit 0 with the packet. A new module or slice is reported as a note, not an
error. Exit 1 when the stack is not set or a harness file is missing.
Python standard library only. This is harness tooling, not the product stack.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("GHOSTINSIDE_ROOT", Path(__file__).resolve().parents[3]))
CORE = Path("meta/core/defaults")
PRODUCT = Path("meta/product")


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def stack_value(key):
    """Value of a row in meta/product/stack.md, without backticks. Stops when unset."""
    path = ROOT / PRODUCT / "stack.md"
    if not path.exists():
        fail(f"missing harness file: {PRODUCT / 'stack.md'}")
    for line in path.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and len(cells) >= 2 and cells[0] == key:
            value = cells[1].replace("`", "").strip()
            if not value or value.startswith("TBD"):
                fail(f"stack not set: '{key}' is TBD in meta/product/stack.md; run init-factory")
            return value
    fail(f"stack row missing: '{key}' in meta/product/stack.md")


def effective(name):
    """Product override when it exists, else the core default (HD-9)."""
    override = PRODUCT / name
    return override if (ROOT / override).exists() else CORE / name


def section(rel):
    path = ROOT / rel
    if not path.exists():
        fail(f"missing harness file: {rel}")
    print(f"== {rel} ==")
    for n, line in enumerate(path.read_text().splitlines(), 1):
        print(f"{rel}:{n}: {line}")
    print()


def main(argv):
    if not 1 <= len(argv) <= 2:
        fail("usage: packet.py <module> [<slice>]")
    module, slice_ = argv[0], (argv[1] if len(argv) == 2 else None)
    src = stack_value("source root")
    if re.search(r"\s", src):
        fail(f"source root must be a bare path in meta/product/stack.md, got: {src}")
    stems = [s.strip() for s in stack_value("entry file stems").split(",")]
    if len(stems) != 2 or not all(stems):
        fail("entry file stems must be two names, such as: index, handler")
    index_stem, handler_stem = stems

    print(f"# Packet: module={module}" + (f" slice={slice_}" if slice_ else ""))
    print()
    for rel in (effective("architecture.md"), effective("persistence.md"),
                PRODUCT / "stack.md", PRODUCT / "practices" / "review.md"):
        section(rel)

    notes = []
    catalog = Path(src) / "_about.md"
    if (ROOT / catalog).exists():
        section(catalog)
    else:
        notes.append(f"no catalog {catalog}")

    mod = Path(src) / "modules" / module
    if not (ROOT / mod).is_dir():
        notes.append(f"new module: {mod} does not exist")
    else:
        if (ROOT / mod / "_about.md").exists():
            section(mod / "_about.md")
        else:
            notes.append(f"no {mod}/_about.md")
        for f in sorted((ROOT / mod).glob(f"{index_stem}.*")):
            section(f.relative_to(ROOT))
        if slice_:
            sl = mod / "slices" / slice_
            if not (ROOT / sl).is_dir():
                notes.append(f"new slice: {sl} does not exist")
            else:
                print(f"== {sl} files ==")
                for f in sorted((ROOT / sl).iterdir()):
                    print(f.relative_to(ROOT))
                print()
                for f in sorted((ROOT / sl).glob(f"{handler_stem}.*")):
                    section(f.relative_to(ROOT))

    print("== notes ==")
    print("\n".join(notes) if notes else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
