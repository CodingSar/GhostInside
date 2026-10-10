#!/usr/bin/env python3
"""Deterministic helper for practice packs (decision-8).

The model researches and judges. This script does the mechanical parts:
compare facets with the central index, check pack format, vendor packs with a
lock, verify the lock, and propose new packs to the central repo as a PR.

Subcommands:
  fetch                     clone or update the central repo cache, print its sha
  status <id>...            print hit|stale|miss per facet id against the cache
  check <pack.md>...        validate pack format; exit 1 on any error
  vendor <id|pack.md>...    vendor exactly this set into meta/practices/packs/,
                            write practices.lock, regenerate review.md and enforced.md
  verify                    exit 1 when vendored files do not match the lock
  propose <pack.md>         open a PR adding or replacing the pack in the central repo

Python standard library only. This is harness tooling, not the product stack.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENTRAL_URL = os.environ.get(
    "GHOSTINSIDE_PRACTICES_URL", "git@github.com:CodingSar/GhostInsidePractices.git"
)
CACHE = Path(os.environ.get("GHOSTINSIDE_PRACTICES_CACHE", ROOT / ".cache" / "practices"))
PRACTICES = Path(os.environ.get("GHOSTINSIDE_PRACTICES_DIR", ROOT / "meta" / "practices"))
PACKS = PRACTICES / "packs"
LOCK = PRACTICES / "practices.lock"
REVIEW = PRACTICES / "review.md"
ENFORCED = PRACTICES / "enforced.md"

KINDS = ("lang", "framework", "datastore", "domain", "concern")
DEEP_KINDS = ("domain", "concern")
STALE_DAYS = 7
HEADER = ["ID", "Level", "Rule", "Enforce", "Source"]
ID_RE = re.compile(r"^[a-z]+/[a-z0-9][a-z0-9-]*$")
RULE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")
ENFORCE_RE = re.compile(r"^(lint: \S.*|check-cmd: \S.*|test|review)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def git(*args, cwd=None):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        fail(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout.strip()


# ---------- pack parsing ----------

def parse_pack(text):
    """Return (front matter dict, rule rows, errors)."""
    errors = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, [], ["missing front matter opening ---"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [], ["missing front matter closing ---"]

    meta, key = {}, None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        m = re.match(r"^([a-z_]+):\s*(.*)$", raw)
        if m:
            key, value = m.group(1), m.group(2).strip()
            meta[key] = value if value else []
        elif raw.lstrip().startswith("- ") and key and isinstance(meta.get(key), list):
            meta[key].append(raw.lstrip()[2:].strip())
        else:
            errors.append(f"front matter line not understood: {raw!r}")

    rows, header_seen = [], False
    for raw in lines[end + 1:]:
        s = raw.strip()
        if not s.startswith("|"):
            if header_seen and s:
                errors.append(f"text after rule table: {s!r}")
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not header_seen:
            if cells != HEADER:
                errors.append(f"table header must be {' | '.join(HEADER)}")
            header_seen = True
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        rows.append(cells)
    if not header_seen:
        errors.append("no rule table")
    return meta, rows, errors


def check_text(text, path_hint=None):
    meta, rows, errors = parse_pack(text)
    if not meta and errors:
        return errors
    for field in ("id", "title", "researched", "tier", "sources"):
        if field not in meta or meta[field] in ("", []):
            errors.append(f"front matter field missing or empty: {field}")
    pid = meta.get("id", "")
    if pid and not ID_RE.match(pid):
        errors.append(f"id must look like <kind>/<name>: {pid}")
    kind = pid.split("/")[0] if "/" in pid else ""
    if pid and kind not in KINDS:
        errors.append(f"id kind must be one of {', '.join(KINDS)}: {kind}")
    if path_hint and pid and not str(path_hint).replace(os.sep, "/").endswith(pid + ".md"):
        errors.append(f"file path must end with {pid}.md")
    researched = meta.get("researched", "")
    if researched and not DATE_RE.match(str(researched)):
        errors.append(f"researched must be YYYY-MM-DD: {researched}")
    tier = meta.get("tier", "")
    if tier and tier not in ("deep", "standard"):
        errors.append(f"tier must be deep or standard: {tier}")
    if kind in DEEP_KINDS and tier == "standard":
        errors.append(f"{kind}/ packs must be tier deep")
    if "sources" in meta and not isinstance(meta["sources"], list):
        errors.append("sources must be a list")
    if not rows and not any(e == "no rule table" for e in errors):
        errors.append("rule table has no rules")
    seen = set()
    for n, cells in enumerate(rows, 1):
        if len(cells) != 5:
            errors.append(f"rule row {n}: expected 5 cells, got {len(cells)} (no | in rule text)")
            continue
        rid, level, rule, enforce, source = cells
        if not RULE_ID_RE.match(rid):
            errors.append(f"rule row {n}: bad ID {rid!r}")
        if rid in seen:
            errors.append(f"rule row {n}: duplicate ID {rid}")
        seen.add(rid)
        if level not in ("MUST", "SHOULD"):
            errors.append(f"rule {rid}: Level must be MUST or SHOULD")
        if not rule:
            errors.append(f"rule {rid}: empty Rule")
        if not ENFORCE_RE.match(enforce):
            errors.append(f"rule {rid}: Enforce must be lint: <..>, check-cmd: <..>, test, or review")
        if not source.startswith(("http://", "https://")):
            errors.append(f"rule {rid}: Source must be a URL")
    return errors


# ---------- central cache ----------

def load_index(root):
    path = Path(root) / "index.json"
    if not path.exists():
        fail(f"no index.json in {root}; run fetch")
    data = json.loads(path.read_text())
    if data.get("version") != 1:
        fail("index.json version must be 1")
    return {p["id"]: p for p in data.get("packs", [])}


def cmd_fetch(_args):
    if (CACHE / ".git").exists():
        git("fetch", "-q", "origin", cwd=CACHE)
        git("reset", "-q", "--hard", "origin/HEAD", cwd=CACHE)
    else:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "-q", CENTRAL_URL, str(CACHE))
    print(git("rev-parse", "HEAD", cwd=CACHE))


def today(args):
    return dt.date.fromisoformat(args.today) if args.today else dt.date.today()


def cmd_status(args):
    index = load_index(CACHE)
    now = today(args)
    for fid in args.ids:
        entry = index.get(fid)
        if not entry:
            print(f"miss {fid}")
            continue
        age = (now - dt.date.fromisoformat(entry["researched"])).days
        state = "stale" if age > STALE_DAYS else "hit"
        print(f"{state} {fid} researched={entry['researched']} age={age}d")


def cmd_check(args):
    bad = 0
    for p in args.files:
        errors = check_text(Path(p).read_text(), path_hint=p)
        for e in errors:
            print(f"{p}: {e}")
        bad += bool(errors)
        if not errors:
            print(f"ok {p}")
    sys.exit(1 if bad else 0)


# ---------- vendoring ----------

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render_views(entries):
    """review.md holds review rules for worker context; enforced.md lists the rest."""
    review = [
        "# Review rules",
        "",
        "Generated by `meta/tools/practices.py vendor` from `meta/practices/packs/`.",
        "Do not edit. These are the pack rules no tool enforces; workers apply them.",
        "",
    ]
    enforced = [
        "# Enforced rules",
        "",
        "Generated by `meta/tools/practices.py vendor`. Do not edit.",
        "init-factory compiles each rule below into tool config, a check command, or a test.",
        "",
        "| Pack | ID | Level | Rule | Enforce |",
        "|---|---|---|---|---|",
    ]
    for pid in sorted(entries):
        meta, rows, _ = parse_pack((PACKS / f"{pid}.md").read_text())
        rv = [r for r in rows if r[3] == "review"]
        if rv:
            review.append(f"## {pid}")
            review.append("")
            review += [f"- {r[0]} {r[1]}: {r[2]}" for r in rv]
            review.append("")
        for r in rows:
            if r[3] != "review":
                enforced.append(f"| {pid} | {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
    return "\n".join(review).rstrip() + "\n", "\n".join(enforced) + "\n"


def cmd_vendor(args):
    index = load_index(CACHE) if (CACHE / "index.json").exists() else {}
    sha = git("rev-parse", "HEAD", cwd=CACHE) if (CACHE / ".git").exists() else None
    chosen = {}
    for item in args.items:
        p = Path(item)
        if item.endswith(".md") and p.exists():
            errors = check_text(p.read_text())
            if errors:
                fail(f"{item}: " + "; ".join(errors))
            meta, _, _ = parse_pack(p.read_text())
            chosen[meta["id"]] = (p, "local")
        elif item in index:
            chosen[item] = (CACHE / index[item]["path"], "central")
        else:
            fail(f"not in central index and not a pack file: {item}")

    if PACKS.exists():
        shutil.rmtree(PACKS)
    lock = {"version": 1, "central": CENTRAL_URL, "sha": sha, "packs": []}
    for pid, (src, origin) in sorted(chosen.items()):
        dest = PACKS / f"{pid}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        meta, _, _ = parse_pack(dest.read_text())
        lock["packs"].append({
            "id": pid,
            "origin": origin,
            "researched": meta["researched"],
            "sha256": sha256(dest),
        })
    LOCK.write_text(json.dumps(lock, indent=2) + "\n")
    review, enforced = render_views(chosen)
    REVIEW.write_text(review)
    ENFORCED.write_text(enforced)
    print(f"vendored {len(chosen)} packs; lock {LOCK}")


def cmd_verify(_args):
    if not LOCK.exists():
        fail("no practices.lock")
    lock = json.loads(LOCK.read_text())
    errors = []
    locked = {p["id"] for p in lock["packs"]}
    for p in lock["packs"]:
        f = PACKS / f"{p['id']}.md"
        if not f.exists():
            errors.append(f"locked pack missing: {p['id']}")
        elif sha256(f) != p["sha256"]:
            errors.append(f"pack changed since vendor: {p['id']}")
    for f in PACKS.rglob("*.md") if PACKS.exists() else []:
        pid = f.relative_to(PACKS).with_suffix("").as_posix()
        if pid not in locked:
            errors.append(f"pack not in lock: {pid}")
    if not errors:
        review, enforced = render_views(locked)
        if not REVIEW.exists() or REVIEW.read_text() != review:
            errors.append("review.md out of date; run vendor")
        if not ENFORCED.exists() or ENFORCED.read_text() != enforced:
            errors.append("enforced.md out of date; run vendor")
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        sys.exit(1)
    print(f"ok: {len(locked)} packs match practices.lock")


# ---------- upstream ----------

def cmd_propose(args):
    src = Path(args.file)
    errors = check_text(src.read_text())
    if errors:
        fail("; ".join(errors))
    meta, _, _ = parse_pack(src.read_text())
    pid = meta["id"]
    branch = f"pack/{pid.replace('/', '-')}-{meta['researched']}"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "central"
        git("clone", "-q", CENTRAL_URL, str(work))
        git("checkout", "-q", "-b", branch, cwd=work)
        dest = work / f"{pid}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        existed = dest.exists()
        shutil.copyfile(src, dest)
        idx_path = work / "index.json"
        idx = json.loads(idx_path.read_text())
        packs = [p for p in idx["packs"] if p["id"] != pid]
        packs.append({"id": pid, "path": f"{pid}.md", "researched": meta["researched"], "tier": meta["tier"]})
        idx["packs"] = sorted(packs, key=lambda p: p["id"])
        idx_path.write_text(json.dumps(idx, indent=2) + "\n")
        verb = "Refresh" if existed else "Add"
        git("add", "-A", cwd=work)
        git("commit", "-q", "-m", f"{verb} pack {pid} (researched {meta['researched']})", cwd=work)
        git("push", "-q", "-u", "origin", branch, cwd=work)
        body = (
            f"{verb} pack `{pid}`, tier `{meta['tier']}`, researched {meta['researched']}.\n\n"
            "Approved locally by the user during init-factory. Needs a human merge (decision-8)."
        )
        out = subprocess.run(
            ["gh", "pr", "create", "--title", f"{verb} pack {pid}", "--body", body, "--head", branch],
            cwd=work, capture_output=True, text=True,
        )
        if out.returncode != 0:
            fail(f"gh pr create: {out.stderr.strip()}")
        print(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch").set_defaults(fn=cmd_fetch)
    s = sub.add_parser("status")
    s.add_argument("ids", nargs="+")
    s.add_argument("--today", help="YYYY-MM-DD, for tests")
    s.set_defaults(fn=cmd_status)
    c = sub.add_parser("check")
    c.add_argument("files", nargs="+")
    c.set_defaults(fn=cmd_check)
    v = sub.add_parser("vendor")
    v.add_argument("items", nargs="+")
    v.set_defaults(fn=cmd_vendor)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    p = sub.add_parser("propose")
    p.add_argument("file")
    p.set_defaults(fn=cmd_propose)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
