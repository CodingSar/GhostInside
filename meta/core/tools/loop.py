#!/usr/bin/env python3
"""Dispatcher loop: run one Backlog task through the factory from a thin main thread.

The main thread is a trampoline (HD-16). It runs `loop.py next` and does
exactly what the one printed line says:

  LAUNCH <agent> <frame>      launch that subagent with: Read <frame> and follow it.
  ASK <questions> <answers>   ask the user the questions, write the answers file
  DONE <summary>              report the summary and stop
  STOP <reason>               report the reason and stop; the user decides

After a LAUNCH it reports back with `loop.py done "<the agent's RETURN line>"`,
after an ASK with `loop.py done "RETURN ok <answers>"`. `done` prints the
next instruction.

Everything deterministic runs here: preflight, the baseline suite, activation,
packets, the red gate, test and check runs, the allowlist and plan-diff
checks, the check that no agent moved HEAD, the review diff, tidy routing, close-out, commits,
and the push. Judgment runs in fresh subagents that end
with one RETURN line. An agent that needs another agent or the user returns
`call` or `ask`: its frame is pushed on a stack in .scratch/<run>/state.json
and it is relaunched with the result when the callee returns. All state is on
disk, so the main thread can clear its context at any point.

Usage:
  loop.py start TASK-n | <request file>
  loop.py next
  loop.py done "<RETURN line>"
  loop.py status
  loop.py retry      after a STOP the user has resolved
  loop.py abandon
  loop.py report [--all]      metrics of the current run (or one line per run)
  loop.py test "<command>"    run a test command for the pending frame: full output to
                              the run logs, a digest on stdout, exit 0 when green
  loop.py hook-stop | hook-subagent-stop    hooks; read the hook JSON on stdin

Python standard library only. This is harness tooling, not the product stack.
"""

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("GHOSTINSIDE_ROOT", Path(__file__).resolve().parents[3]))
SCRATCH = ".scratch"
GUIDES = {
    "intake": "meta/core/guides/intake.md",
    "planner": "meta/core/guides/plan.md",
    "researcher": "meta/core/guides/research.md",
    "test-writer": "meta/core/guides/test.md",
    "implementer": "meta/core/guides/implement.md",
    "reviewer": "meta/core/guides/review.md",
}
CALLS = {"intake": ["researcher"], "planner": ["researcher"]}  # allowed edges
ASKERS = {"intake", "planner"}
MAX_DEPTH = 3
STEP_FILES = 4  # files per plan step; small models finish short steps (HD-23)
DIFF_LINES = 600  # the reviewer's diff is cut here (HD-24)
GAP_RE = re.compile(r"^- (\S+?):(\d+): (.+)$")          # frames in one chain, caller included
STOP_BLOCKS = 3        # times the Stop hook holds the main thread before letting go
BUDGET = 2             # implementer iterations
STACK_KEYS = {
    "full": "test command (full)",
    "targeted": "test command (targeted, takes a path)",
    "check": "check command",
    "fix": "fix command",
    "report": "test report (JUnit XML)",
    "src": "source root",
    "tests": "test file pattern",
    "stems": "entry file stems",
}
RETURN_RE = re.compile(r"^RETURN (ok|call|ask|deviation|blocked)(?: (.*))?$")
TERMINAL = ("done", "stopped")


class Stop(Exception):
    """A stop rule fired. The message is the reason the user sees."""


# ---------- files, commands ----------

def run_dir(st):
    return ROOT / SCRATCH / st["run"]


def current_run():
    p = ROOT / SCRATCH / "current"
    return (p.read_text().strip() or None) if p.exists() else None


def load(run):
    return json.loads((ROOT / SCRATCH / run / "state.json").read_text())


def save(st):
    p = run_dir(st) / "state.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(p)


def log(st, line):
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(run_dir(st) / "log.md", "a") as f:
        f.write(f"{stamp} {line.rstrip()}\n")


def first_line(text):
    return next((l.strip() for l in text.splitlines() if l.strip()), "(no output)")


def sh(st, cmd, name):
    """Run a stack command. Output goes to a log file; the caller gets the code and the path."""
    out = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    logs = run_dir(st) / "logs"
    logs.mkdir(exist_ok=True)
    path = logs / f"{name}.txt"
    path.write_text(f"$ {cmd}\nexit {out.returncode}\n{out.stdout}{out.stderr}")
    return out.returncode, out.stdout + out.stderr, str(path.relative_to(ROOT))


def tool(args, what):
    out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if out.returncode:
        raise Stop(f"{what} failed: {first_line(out.stderr or out.stdout)}")
    return out.stdout


def git(*args):
    return tool(["git", *args], "git " + args[0])


def backlog(*args):
    return tool(["backlog", *args], "backlog " + " ".join(args[:2]))


def task_json(task):
    return json.loads(backlog("task", "view", task, "--json"))["task"]


def changed_paths():
    """Paths that differ from HEAD, untracked files included, ignored files not."""
    paths = []
    for line in git("status", "--porcelain", "-uall").splitlines():
        p = line[3:]
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        paths.append(p.strip('"'))
    return paths


def commit(st, msg):
    git("add", "-A")
    if git("status", "--porcelain").strip():
        git("commit", "-q", "-m", msg)
        log(st, f"commit: {msg}")


def stack_values():
    path = ROOT / "meta/product/stack.md"
    if not path.exists():
        raise Stop("missing meta/product/stack.md")
    rows = {}
    for line in path.read_text().splitlines():
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                rows[cells[0]] = cells[1].replace("`", "").strip()
    values = {}
    for k, key in STACK_KEYS.items():
        v = rows.get(key)
        if v is None:
            raise Stop(f"stack row missing: '{key}' in meta/product/stack.md; amend the factory with init-factory")
        if not v or v.startswith("TBD"):
            raise Stop(f"stack not set: '{key}' is TBD in meta/product/stack.md; run init-factory")
        values[k] = v
    return values


# ---------- RETURN lines and frames ----------

def parse_return(text, fr):
    """(kind, arg) of the last RETURN line in text, checked against frame fr. ValueError if invalid."""
    found = [l.strip().strip("`").strip() for l in (text or "").splitlines()
             if l.strip().strip("`").startswith("RETURN ")]
    if not found:
        raise ValueError("no RETURN line")
    m = RETURN_RE.match(found[-1])
    if not m:
        raise ValueError(f"malformed RETURN line: {found[-1]}")
    kind, arg = m.group(1), (m.group(2) or "").strip()
    agent = fr["agent"]
    if kind == "ok":
        if arg != fr["out"]:
            raise ValueError(f"RETURN ok must name {fr['out']}")
        if not (ROOT / arg).is_file():
            raise ValueError(f"output file missing: {arg}")
    elif kind == "call":
        parts = arg.split()
        if len(parts) != 2:
            raise ValueError("RETURN call needs <agent> <request file>")
        if parts[0] not in CALLS.get(agent, []):
            raise ValueError(f"{agent} may not call {parts[0]}")
        if parts[1] != fr["call"] or not (ROOT / parts[1]).is_file():
            raise ValueError(f"the call request must be written to {fr['call']}")
    elif kind == "ask":
        if agent not in ASKERS:
            raise ValueError(f"{agent} may not ask the user")
        if arg != fr["ask"] or not (ROOT / arg).is_file():
            raise ValueError(f"the questions must be written to {fr['ask']}")
    elif not arg:
        raise ValueError(f"RETURN {kind} needs a reason")
    return kind, arg


def frame_text(st, fr, body):
    agent = fr["agent"]
    lines = [f"# Frame {fr['n']}: {agent}", "",
             f"Read `{GUIDES[agent]}` in full first, then do the job below by it.", "",
             f"Task: {st.get('task') or 'not created yet'}", "", "## Job", "", body.rstrip(), "",
             "## Files", "", f"- Write your output to `{fr['out']}`."]
    returns = [f"RETURN ok {fr['out']}"]
    if CALLS.get(agent):
        lines.append(f"- To call {', '.join(CALLS[agent])}: write the request to `{fr['call']}`.")
        returns.append(f"RETURN call {'|'.join(CALLS[agent])} {fr['call']}")
    if agent in ASKERS:
        lines.append(f"- To ask the user: write the questions to `{fr['ask']}`.")
        returns.append(f"RETURN ask {fr['ask']}")
    returns += ["RETURN deviation <reason>", "RETURN blocked <reason>"]
    if fr.get("allow"):
        lines += ["", "## Edit only", "", "The guard hook rejects a write anywhere else:", "",
                  *[f"- `{a}`" for a in fr["allow"]]]
    lines += ["", "## Last line", "",
              "Your reply ends with exactly one of these lines, with nothing after it:", "",
              "```", *returns, "```", ""]
    return "\n".join(lines)


def launch(st, agent, body, job=None, retry_of=None, allow=None):
    """allow: the paths (or prefixes ending in /) the agent may write, enforced by guard.py
    at write time; None leaves only the harness protection."""
    st["seq"] += 1
    n = st["seq"]
    base = f"{SCRATCH}/{st['run']}/frames/{n:02d}-{agent}"
    fr = {"kind": "launch", "n": n, "agent": agent, "in": base + ".in.md", "out": base + ".out.md",
          "call": base + ".call.md", "ask": base + ".ask.md", "job": job or base + ".in.md",
          "retry_of": retry_of or n, "head": git("rev-parse", "HEAD").strip(), "allow": allow}
    (ROOT / base).parent.mkdir(parents=True, exist_ok=True)
    text = frame_text(st, fr, body)
    (ROOT / fr["in"]).write_text(text)
    st["pending"] = fr
    log(st, f"launch {n:02d} {agent} {len(text.encode())}b")


def relaunch(st, fr, reason):
    """Launch the same job again, once, with the reason it was rejected."""
    launch(st, fr["agent"], f"Do the job in `{fr['job']}` again; write to the files of this frame, "
                            f"not that one's.\n\n{reason}",
           job=fr["job"], retry_of=fr["retry_of"], allow=fr.get("allow"))


def resume(st, caller, result):
    """Relaunch a suspended caller with the result of its call or question."""
    asked = caller["via"] == "ask"
    req = caller["ask"] if asked else caller["call"]
    who = "the user" if asked else caller["callee"]
    out = f"\n- Your earlier output: `{caller['out']}`" if (ROOT / caller["out"]).is_file() else ""
    body = (f"You stopped to {'ask the user' if asked else 'call ' + who}. Continue the same job; write to "
            f"the files of this frame, not the earlier ones.\n\n"
            f"- The job: `{caller['job']}`{out}\n- Your request: `{req}`\n- The answer from {who}: `{result}`")
    launch(st, caller["agent"], body, job=caller["job"], allow=caller.get("allow"))


# ---------- the plan ----------

STEP_RE = re.compile(r"^(\d+)\.\s+(.+)$")
FIELD_RE = re.compile(r"^\s+(Files|Criteria|Test):\s*(.*)$")
SPECIAL_RE = re.compile(r"^(Retire|Change|Catalog):\s*(.+)$")


def parse_plan(text, n_criteria, sv):
    """Plan dict from the Backlog plan field, or ValueError listing every problem."""
    steps, special, errors = [], {"Retire": [], "Change": [], "Catalog": []}, []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        if m := STEP_RE.match(line):
            steps.append({"n": int(m.group(1)), "title": m.group(2).strip(), "files": [], "criteria": [], "test": ""})
        elif (m := FIELD_RE.match(line)) and steps:
            field, value = m.group(1), m.group(2).strip()
            if field == "Files":
                steps[-1]["files"] = [f.strip().strip("`") for f in value.split(",") if f.strip()]
            elif field == "Criteria":
                if value.lower() != "none":
                    try:
                        steps[-1]["criteria"] = [int(c) for c in value.replace("#", "").split(",") if c.strip()]
                    except ValueError:
                        errors.append(f"step {steps[-1]['n']}: Criteria must be numbers or none")
            else:
                steps[-1]["test"] = value.strip("`")
        elif m := SPECIAL_RE.match(line.strip()):
            special[m.group(1)].append(m.group(2).strip())
        elif line[0].isspace() and steps:
            steps[-1]["title"] += " " + line.strip()
        else:
            errors.append(f"unreadable line: {line.strip()[:80]}")
    if not steps:
        errors.append("no numbered steps")
    for i, s in enumerate(steps, 1):
        if s["n"] != i:
            errors.append(f"step {s['n']}: steps must be numbered 1, 2, 3, ...")
        if not s["files"]:
            errors.append(f"step {s['n']}: no Files line")
        elif len(s["files"]) > STEP_FILES:
            errors.append(f"step {s['n']}: {len(s['files'])} files, at most {STEP_FILES} per step; split it")
        for f in s["files"]:
            if f.startswith(("/", "meta/", ".claude/", "backlog/", SCRATCH)) or ".." in f.split("/"):
                errors.append(f"step {s['n']}: file not allowed: {f}")
            elif re.search(sv["tests"], f.rsplit("/", 1)[-1]):
                errors.append(f"step {s['n']}: test file in Files: {f} (tests belong to the test-writer; "
                              f"use a Retire or Change line)")
        for c in s["criteria"]:
            if not 1 <= c <= n_criteria:
                errors.append(f"step {s['n']}: no criterion {c}")
        if not s["test"]:
            errors.append(f"step {s['n']}: no Test line")
        elif s["test"] != sv["full"] and not s["test"].startswith(sv["targeted"] + " "):
            errors.append(f"step {s['n']}: Test must be the full test command or start with: {sv['targeted']}")
        elif s["test"] != sv["full"] and re.search(r"[;&|<>`$()\n]", s["test"][len(sv["targeted"]):]):
            errors.append(f"step {s['n']}: Test takes paths only after the targeted command, no shell operators")
    covered = {c for s in steps for c in s["criteria"]}
    missing = [c for c in range(1, n_criteria + 1) if c not in covered]
    if missing:
        errors.append(f"criteria not covered by any step: {', '.join(map(str, missing))}")
    catalogs = []
    for c in special["Catalog"]:
        path, _, entry = c.partition(" :: ")
        if not entry or not path.endswith("_about.md") or not path.startswith(sv["src"] + "/"):
            errors.append(f"Catalog line must be <{sv['src']}/.../_about.md> :: <line>: {c[:80]}")
        catalogs.append([path.strip(), entry.strip()])
    retired = []
    for r in special["Retire"]:
        path, _, rest = r.partition(" :: ")
        if not rest or " -> " not in rest:
            errors.append(f"Retire line must be <file> :: <test> -> delete|rewrite as TASK-n#k: {r[:80]}")
        retired.append(path.strip())
    for c in special["Change"]:
        if " :: " not in c or " -> " not in c:
            errors.append(f"Change line must be <handler> :: <old> -> <new>: {c[:80]}")
    if errors:
        raise ValueError("\n".join(errors))
    return {"steps": steps, "retire": special["Retire"], "change": special["Change"],
            "catalogs": catalogs, "retired_files": retired}


def plan_modules(st, sv):
    """(module, slice or None) pairs the plan's files live in."""
    pat = re.compile(rf"^{re.escape(sv['src'])}/modules/([^/]+)(?:/slices/([^/]+))?/")
    seen = []
    for s in st["plan"]["steps"]:
        for f in s["files"]:
            if (m := pat.match(f)) and (m.group(1), m.group(2)) not in seen:
                seen.append((m.group(1), m.group(2)))
    return seen


def task_allowed(st, sv, path):
    """True when a changed path belongs to this task: plan files, catalogs, retired tests,
    tests and index files in the plan's modules, screen mockups, and Backlog files."""
    plan = st["plan"]
    if path.startswith(("backlog/", "meta/product/screens/")):
        return True
    if path in {f for s in plan["steps"] for f in s["files"]}:
        return True
    if path in {c[0] for c in plan["catalogs"]} or path in plan["retired_files"]:
        return True
    name = path.rsplit("/", 1)[-1]
    stems = [x.strip() for x in sv["stems"].split(",")]
    for module, _ in plan_modules(st, sv):
        if path.startswith(f"{sv['src']}/modules/{module}/"):
            if re.search(sv["tests"], name) or name.split(".")[0] == stems[0]:
                return True
    return False


def red_allow(st, sv):
    """Write allowlist of the test-writer: Backlog, screens, the plan's modules, catalogs, retired files."""
    plan = st["plan"]
    paths = ["backlog/", "meta/product/screens/"]
    paths += [f"{sv['src']}/modules/{m}/" for m, _ in plan_modules(st, sv)]
    paths += [c[0] for c in plan["catalogs"]] + list(plan["retired_files"])
    paths += [f for s in plan["steps"] for f in s["files"]]
    return list(dict.fromkeys(paths))


# ---------- test reports ----------

def junit(sv):
    """[(name, status, message)] from the JUnit report, or None when it is missing or unreadable."""
    path = ROOT / sv["report"]
    if not path.is_file():
        return None
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    results, counted_errors, suite_errors = [], 0, 0
    for suite in root.iter("testsuite"):
        suite_errors += int(suite.get("errors") or 0)
    for tc in root.iter("testcase"):
        name = f"{tc.get('classname', '')} {tc.get('name', '')}".strip()
        status, msg = "pass", ""
        for child in tc:
            if child.tag in ("failure", "error", "skipped"):
                status = {"failure": "fail", "error": "error", "skipped": "skip"}[child.tag]
                msg = first_line(child.get("message") or child.text or "")
                break
        counted_errors += status == "error"
        results.append((name, status, msg))
    if suite_errors > counted_errors:
        results.append(("(test suite)", "error", f"{suite_errors - counted_errors} errors outside test cases"))
    return results


def crit_re(task, k=None):
    """Matches TASK-12#2 and the closest identifier form, such as TASK_12_2."""
    num = task.split("-", 1)[1]
    k = rf"{k}" if k else r"\d+"
    return re.compile(rf"TASK[-_]{num}(?:#|_){k}(?!\d)")


DIGEST_LINES = 20


def run_tests(st, sv, cmd, name):
    """Run a test command. (code, results, log path, digest); results from a fresh JUnit report."""
    report = ROOT / sv["report"]
    if report.exists():
        report.unlink()
    code, output, path = sh(st, cmd, name)
    results = junit(sv)
    return code, results, path, digest(code, output, results, path)


def full_tests(st, sv, name):
    return run_tests(st, sv, sv["full"], name)[:3]


def digest(code, output, results, log_path):
    """At most DIGEST_LINES lines: the verdict and counts, one line per failing test (its first
    message line), or the last 10 output lines when there is no report, and the log path."""
    if results is None:
        tail = [l for l in output.splitlines() if l.strip()][-10:]
        lines = [f"{'PASS' if code == 0 else 'FAIL'} (exit {code}, no JUnit report); last output lines:",
                 *[f"  {l[:200]}" for l in tail]]
    else:
        bad = [(n, s, m) for n, s, m in results if s not in ("pass", "skip")]
        verdict = "PASS" if code == 0 and not bad else "FAIL"
        lines = [f"{verdict}: {len(results) - len(bad)} of {len(results)} tests pass, {len(bad)} fail"
                 + (f" (exit {code})" if code and not bad else "")]
        room = DIGEST_LINES - 3
        lines += [f"- {n}: {s} {m}".rstrip()[:200] for n, s, m in bad[:room]]
        if len(bad) > room:
            lines.append(f"- ... and {len(bad) - room} more")
    return "\n".join(lines + [f"Full output: `{log_path}`"])


def red_gate(task, n_criteria, results):
    if results is None:
        return ["no readable JUnit report: check the 'test report (JUnit XML)' row of the stack"]
    errors = []
    for k in range(1, n_criteria + 1):
        tests = [r for r in results if crit_re(task, k).search(r[0])]
        if not tests:
            errors.append(f"criterion {k}: no test named {task}#{k}")
        errors += [f"{n}: {s}, expected a failing test (assertion or not-implemented)"
                   for n, s, _ in tests if s != "fail"]
    errors += [f"{n}: {s} {m}".rstrip() for n, s, m in results
               if not crit_re(task).search(n) and s != "pass"]
    return errors


# ---------- phases ----------

def criteria(task):
    return [(c["index"], c["text"]) for c in task_json(task)["acceptanceCriteria"]]


def packets(st, sv):
    """Write the packets of the plan's modules: rules.md once per run, then one per module without
    the rules. Returns their paths, rules first."""
    pdir = run_dir(st) / "packets"
    pdir.mkdir(exist_ok=True)
    jobs = [(["--rules"], "rules")]
    jobs += [([m] + ([s] if s else []) + ["--no-rules"], "-".join([m] + ([s] if s else [])))
             for m, s in plan_modules(st, sv)]
    paths = []
    for args, name in jobs:
        p = pdir / f"{name}.md"
        if name != "rules" or not p.exists():
            out = subprocess.run([sys.executable, "-I", str(ROOT / "meta/core/tools/packet.py"), *args],
                                 cwd=ROOT, capture_output=True, text=True,
                                 env=dict(os.environ, GHOSTINSIDE_ROOT=str(ROOT)))
            if out.returncode:
                raise Stop(f"packet.py {' '.join(args)} failed: {first_line(out.stderr)}")
            p.write_text(out.stdout)
        paths.append(str(p.relative_to(ROOT)))
    return paths


def check_allowlist(st, allowed, what):
    outside = [p for p in changed_paths() if not allowed(p)]
    if outside:
        raise Stop(f"{what} changed files outside its allowlist: {', '.join(outside[:10])}")


def enter_intake(st, sv):
    if st["task"]:
        body = f"Task {st['task']} exists. Check it by the intake guide: the source rule, ASSUMED criteria, and screens."
    else:
        body = f"Create the task for this request from the user, written verbatim in `{st['request']}`."
    launch(st, "intake", body)


def done_intake(st, sv, fr):
    text = (ROOT / fr["out"]).read_text()
    m = re.search(r"^task:\s*(TASK-\d+)\s*$", text, re.M)
    if not m:
        return relaunch_once(st, fr, "intake", f"Your output must start with the line `task: TASK-<n>`.")
    st["task"] = m.group(1)
    commit(st, f"{st['task']}: intake")
    st["phase"] = "activate"


def enter_activate(st, sv):
    t = st["task"]
    code, results, log_path = full_tests(st, sv, "baseline")
    if code or results is None or any(s != "pass" for _, s, _ in results):
        raise Stop(f"the full test suite is not green before {t} starts: {log_path}; "
                   f"fix main first, then retry")
    st["start"] = git("rev-parse", "HEAD").strip()
    backlog("task", "edit", t, "-s", "In Progress", "-a", "@claude")
    backlog("task", "edit", t, "--append-notes", f"start: {st['start']}")
    st["phase"] = "plan"


def enter_plan(st, sv):
    assumed = [str(k) for k, text in criteria(st["task"]) if text.strip().startswith("ASSUMED:")]
    if assumed:
        raise Stop(f"criteria still ASSUMED: {', '.join(assumed)}; confirm them with the user, then retry")
    launch(st, "planner", f"Plan {st['task']}. Write the plan into the task with `backlog task edit {st['task']} --plan`, "
                          f"in the format of the guide.")


def done_plan(st, sv, fr):
    t = task_json(st["task"])
    try:
        st["plan"] = parse_plan(t.get("implementationPlan"), len(t["acceptanceCriteria"]), sv)
    except ValueError as e:
        return relaunch_once(st, fr, "plan", f"The plan in the task was rejected:\n\n{e}\n\nFix it with "
                                             f"`backlog task edit {st['task']} --plan`.")
    commit(st, f"{st['task']}: plan")
    st["phase"] = "red"


def enter_red(st, sv):
    crit = criteria(st["task"])
    plan = st["plan"]
    slices = [f"{sv['src']}/modules/{m}" + (f"/slices/{s}" if s else "") for m, s in plan_modules(st, sv)]
    body = "\n".join([
        f"Write the failing tests and stubs for {st['task']}.", "", "Criteria:",
        *[f"{k}. {text}" for k, text in crit], "", "Slice paths:", *[f"- {s}" for s in slices], "",
        "Packets (read them):", *[f"- `{p}`" for p in packets(st, sv)], "",
        "Retire lines:", *([f"- {r}" for r in plan["retire"]] or ["- none"]), "",
        "Change lines:", *([f"- {c}" for c in plan["change"]] or ["- none"]), "",
        f"Full test command: `{sv['full']}`"])
    launch(st, "test-writer", body, allow=red_allow(st, sv))


def done_red(st, sv, fr):
    check_allowlist(st, lambda p: task_allowed(st, sv, p), "test-writer")
    sh(st, sv["fix"], "red-fix")
    for path, entry in st["plan"]["catalogs"]:
        p = ROOT / path
        text = p.read_text() if p.exists() else ""
        if entry not in text:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text + ("" if not text or text.endswith("\n") else "\n") + entry + "\n")
    _, results, log_path, dg = run_tests(st, sv, sv["full"], "red")
    errors = red_gate(st["task"], len(criteria(st["task"])), results)
    if errors:
        report = run_dir(st) / "logs" / "red-gate.txt"
        report.write_text("\n".join(errors) + "\n")
        git("checkout", "--", ".")
        git("clean", "-fdq", "--", sv["src"])
        shown = errors[:DIGEST_LINES - 3] + ([f"... and {len(errors) - DIGEST_LINES + 3} more"]
                                             if len(errors) > DIGEST_LINES - 3 else [])
        return relaunch_once(st, fr, "red", "\n".join([
            f"Write the failing tests and stubs for {st['task']} again. The red gate failed and your changes "
            f"were discarded. Every criterion needs one failing test named {st['task']}#k; every other test "
            f"stays green.", "", "Gate findings:", *[f"- {e}" for e in shown], "",
            f"Gate report: `{report.relative_to(ROOT)}`", dg]))
    commit(st, f"{st['task']}: failing tests and stubs")
    backlog("task", "edit", st["task"], "--append-notes", "red gate: ok")
    st["phase"], st["step"] = "step", 0


def step_body(st, sv, s, crit):
    texts = dict(crit)
    return "\n".join([
        f"Step {s['n']}: {s['title']}", "", "Criteria:",
        *([f"{k}. {texts[k]}" for k in s["criteria"]] or ["none (wiring step)"]), "",
        f"Targeted test command: `{s['test']}`", "",
        "Packets (read them):", *[f"- `{p}`" for p in packets(st, sv)], "",
        f"Iteration budget: {BUDGET}"])


def enter_step(st, sv):
    steps = st["plan"]["steps"]
    if st["step"] >= len(steps):
        st["phase"] = "review"
        return
    s = steps[st["step"]]
    launch(st, "implementer", step_body(st, sv, s, criteria(st["task"])), allow=s["files"])


def done_step(st, sv, fr):
    s = st["plan"]["steps"][st["step"]]
    check_allowlist(st, lambda p: p in s["files"], f"step {s['n']}")
    code, _, _, dg = run_tests(st, sv, s["test"], f"step-{s['n']}")
    if code:
        git("checkout", "--", ".")
        git("clean", "-fdq", "--", sv["src"])
        texts = dict(criteria(st["task"]))
        return relaunch_once(st, fr, f"step-{s['n']}", "\n".join([
            f"Step {s['n']}: {s['title']}, again. Your targeted tests still failed and your changes were "
            f"discarded. Make these pass:", *[f"{k}. {texts[k]}" for k in s["criteria"]], "", dg]))
    backlog("task", "edit", st["task"], "--append-notes", f"step {s['n']}: ok")
    commit(st, f"{st['task']}: step {s['n']} {s['title']}"[:72])
    st["step"] += 1


def findings(output, st, sv):
    """{'source': {path: [lines]}, 'test': {...}, 'outside': {...}} from check output."""
    found = {"source": {}, "test": {}, "outside": {}}
    for line in output.splitlines():
        for tok in re.findall(r"[A-Za-z0-9_.][A-Za-z0-9_./-]*", line):
            path = tok.split(":")[0].lstrip("./")
            if not path or not (ROOT / path).is_file():
                continue
            name = path.rsplit("/", 1)[-1]
            if not task_allowed(st, sv, path):
                kind = "outside"
            elif re.search(sv["tests"], name):
                kind = "test"
            else:
                kind = "source"
            found[kind].setdefault(path, []).append(line.strip())
    return found


def plan_files(st):
    return list(dict.fromkeys(f for s in st["plan"]["steps"] for f in s["files"]))


def enter_review(st, sv):
    """After the last step: a fresh-context reviewer reads the diff, the criteria, and the tests."""
    if st["reviewed"]:
        st["phase"] = "tidy"
        return
    diff = git("diff", f"{st['start']}..HEAD", "--", sv["src"])
    lines = diff.splitlines()
    if len(lines) > DIFF_LINES:
        lines = lines[:DIFF_LINES] + [f"... cut: {len(lines) - DIFF_LINES} more lines; open the files for the rest"]
    rdir = run_dir(st) / "review"
    rdir.mkdir(exist_ok=True)
    diff_path = rdir / "diff.md"
    diff_path.write_text("\n".join(lines) + "\n")
    changed = git("diff", "--name-only", f"{st['start']}..HEAD", "--", sv["src"]).split()
    tests = [p for p in changed if re.search(sv["tests"], p.rsplit("/", 1)[-1])]
    body = "\n".join([
        f"Review the change for {st['task']}.", "", "Criteria:",
        *[f"{k}. {text}" for k, text in criteria(st["task"])], "",
        f"Diff: `{diff_path.relative_to(ROOT)}`", "",
        "Test files:", *([f"- `{t}`" for t in tests] or ["- none changed"])])
    launch(st, "reviewer", body, allow=[])


def review_fix_body(st, sv, gaps):
    texts = dict(criteria(st["task"]))
    return "\n".join([
        f"Review fix for {st['task']}: a reviewer found these gaps between the criteria and the code. "
        f"Close each one; the full test suite must stay green.", "", "Gaps:",
        *[f"- {f}:{n}: {what}" for f, n, what in gaps], "", "Criteria:",
        *[f"{k}. {t}" for k, t in texts.items()], "",
        f"Targeted test command: `{sv['full']}`", "",
        "Packets (read them):", *[f"- `{p}`" for p in packets(st, sv)], "",
        f"Iteration budget: {BUDGET}"])


def done_review(st, sv, fr):
    if fr["agent"] == "reviewer":
        check_allowlist(st, lambda p: False, "reviewer")
        text = (ROOT / fr["out"]).read_text()
        changed = set(git("diff", "--name-only", f"{st['start']}..HEAD", "--", sv["src"]).split())
        gaps = [(m.group(1), m.group(2), m.group(3)) for m in map(GAP_RE.match, text.splitlines())
                if m and m.group(1) in changed]  # a gap outside the diff is noise, not a finding
        st["reviewed"] = True
        if not gaps:
            log(st, "review: no gaps")
            st["phase"] = "tidy"
            return
        log(st, f"review: {len(gaps)} gaps")
        backlog("task", "edit", st["task"], "--append-notes", f"review: {len(gaps)} gaps, one fix run")
        return launch(st, "implementer", review_fix_body(st, sv, gaps[:8]), allow=plan_files(st))
    files = plan_files(st)
    check_allowlist(st, lambda p: p in files, "review fix")
    code, _, _, dg = run_tests(st, sv, sv["full"], "review-fix")
    if code:
        git("checkout", "--", ".")
        git("clean", "-fdq", "--", sv["src"])
        return relaunch_once(st, fr, "review-fix", "\n".join([
            "Review fix, again. The full suite failed after your changes and they were discarded. "
            "Close the gaps without breaking a test:", "", dg]))
    commit(st, f"{st['task']}: review fixes")
    st["phase"] = "tidy"


def enter_tidy(st, sv):
    if st["tidy_queue"]:
        agent, paths, lines = st["tidy_queue"][0]
        body = "\n".join(["tidy: " + lines[0], *lines[1:40], "", f"Test command: `{sv['full']}`"])
        log(st, f"tidy {agent}")
        return launch(st, agent, body, allow=paths)
    sh(st, sv["fix"], "tidy-fix")
    code, output, log_path = sh(st, sv["check"], f"check-{'2' if st['tidied'] else '1'}")
    if code == 0:
        commit(st, f"{st['task']}: tidy")
        st["phase"] = "verify"
        return
    if st["tidied"]:
        raise Stop(f"check still fails after one tidy run: {log_path}")
    f = findings(output, st, sv)
    if f["outside"]:
        raise Stop(f"check findings outside this plan's files: {', '.join(list(f['outside'])[:10])}; "
                   f"the user adds a tidy step to the plan or ends the run with a follow-up task ({log_path})")
    if not f["source"] and not f["test"]:
        raise Stop(f"check failed with no finding in a file: {log_path}")
    st["tidied"] = True
    for agent, kind in (("implementer", "source"), ("test-writer", "test")):
        if f[kind]:
            lines = [l for ls in f[kind].values() for l in ls]
            st["tidy_queue"].append([agent, list(f[kind]), list(dict.fromkeys(lines))])


def done_tidy(st, sv, fr):
    agent, paths, _ = st["tidy_queue"][0]
    check_allowlist(st, lambda p: p in paths, f"tidy run of {agent}")
    st["tidy_queue"].pop(0)


def enter_verify(st, sv):
    code, results, log_path = full_tests(st, sv, "verify")
    if code or results is None or any(s != "pass" for _, s, _ in results):
        raise Stop(f"full test suite is not green: {log_path}")
    code, _, log_path = sh(st, sv["check"], "verify-check")
    if code:
        raise Stop(f"check command failed: {log_path}")
    diff = git("diff", "--name-only", f"{st['start']}..HEAD").split() + changed_paths()
    outside = sorted({p for p in diff if not task_allowed(st, sv, p)})
    if outside:
        raise Stop(f"changed files outside the plan: {', '.join(outside[:10])}; ask the user")
    if any(p.startswith(("meta/", ".claude/")) for p in diff):
        code, out, _ = sh(st, "meta/core/tools/check-harness.sh", "check-harness")
        if code:
            raise Stop(f"check-harness failed: {first_line(out)}")
    st["evidence"] = [[n, s] for n, s, _ in results]
    st["phase"] = "close"


def enter_close(st, sv):
    t, crit = st["task"], criteria(st["task"])
    results = st["evidence"]
    proven = [k for k, _ in crit
              if (ts := [s for n, s in results if crit_re(t, k).search(n)]) and all(s == "pass" for s in ts)]
    missing = [str(k) for k, _ in crit if k not in proven]
    if missing:
        raise Stop(f"criteria without a passing test: {', '.join(missing)}")
    args = ["task", "edit", t]
    for k in proven:
        args += ["--check-ac", str(k)]
    backlog(*args)
    steps = "; ".join(f"{s['n']}. {s['title']}" for s in st["plan"]["steps"])
    summary = (f"Steps: {steps}. Retired tests: {len(st['plan']['retire'])}. Verified: full suite "
               f"{len(results)}/{len(results)} passed, check command exit 0, changed files within the plan. "
               f"Criteria checked by their passing TASK tests: {', '.join(map(str, proven))}.")
    backlog("task", "edit", t, "--final-summary", summary, "-s", "Done")
    commit(st, f"{t}: close")
    st["phase"] = "push"


def enter_push(st, sv):
    tool(["git", "push", "origin", "main"], "git push origin main")
    st["phase"] = "done"
    st["summary"] = (f"{st['task']} done: {len(st['evidence'])} tests green, "
                     f"{len(criteria(st['task']))} criteria checked, pushed {git('rev-parse', '--short', 'HEAD').strip()}")
    log(st, "done")


PHASES = {
    "intake": (enter_intake, done_intake),
    "activate": (enter_activate, None),
    "plan": (enter_plan, done_plan),
    "red": (enter_red, done_red),
    "step": (enter_step, done_step),
    "review": (enter_review, done_review),
    "tidy": (enter_tidy, done_tidy),
    "verify": (enter_verify, None),
    "close": (enter_close, None),
    "push": (enter_push, None),
}


def relaunch_once(st, fr, key, reason):
    st["retries"][key] = st["retries"].get(key, 0) + 1
    if st["retries"][key] > 1:
        raise Stop(f"{fr['agent']} failed twice ({key}): {first_line(reason)}")
    log(st, f"relaunch {key}")
    relaunch(st, fr, reason)


def stop(st, reason):
    st["stopped_in"], st["phase"], st["stop"] = st["phase"], "stopped", reason
    st["pending"], st["stack"] = None, []
    log(st, f"STOP {reason}")


def advance(st):
    """Run deterministic phases until the main thread has something to do. Returns the instruction."""
    try:
        sv = stack_values()
        while not st["pending"] and st["phase"] not in TERMINAL:
            PHASES[st["phase"]][0](st, sv)
    except Stop as e:
        stop(st, str(e))
    st["stop_blocks"] = 0
    save(st)
    return instruction(st)


def instruction(st):
    p = st["pending"]
    if st["phase"] == "stopped":
        return f"STOP {st['stop']}"
    if st["phase"] == "done":
        return f"DONE {st['summary']}"
    if p["kind"] == "ask":
        return f"ASK {p['q']} {p['answer']}"
    return f"LAUNCH {p['agent']} {p['in']}"


# ---------- commands ----------

def need_run():
    run = current_run()
    if not run:
        raise SystemExit("STOP no run; start one with: loop.py start TASK-n | <request file>")
    return load(run)


def cmd_start(arg):
    cur = current_run()
    if cur and load(cur)["phase"] not in TERMINAL:
        print(f"STOP run {cur} is still open: run `loop.py next`, or `loop.py abandon` it")
        return 1
    try:
        stack_values()
    except Stop as e:
        print(f"STOP {e}")
        return 1
    if [p for p in changed_paths() if not p.startswith(SCRATCH + "/")]:
        print("STOP the working tree is not clean: commit or discard changes first")
        return 1
    runs = [int(p.name[4:]) for p in (ROOT / SCRATCH).glob("run-*") if p.name[4:].isdigit()]
    st = {"run": f"run-{max(runs, default=0) + 1}", "task": None, "request": None, "phase": "intake",
          "seq": 0, "pending": None, "stack": [], "retries": {}, "step": 0, "plan": None, "start": None,
          "tidy_queue": [], "tidied": False, "reviewed": False, "evidence": [], "stop": None, "stop_blocks": 0}
    run_dir(st).mkdir(parents=True)
    if re.fullmatch(r"TASK-\d+", arg):
        st["task"] = arg
    elif (ROOT / arg).is_file():
        req = run_dir(st) / "request.md"
        req.write_text((ROOT / arg).read_text())
        st["request"] = str(req.relative_to(ROOT))
    else:
        run_dir(st).rmdir()
        print(f"STOP not a task id or a request file: {arg}")
        return 1
    (ROOT / SCRATCH / "current").write_text(st["run"] + "\n")
    log(st, f"start {arg}")
    print(advance(st))
    return 0


def cmd_next():
    st = need_run()
    print(advance(st) if st["phase"] not in TERMINAL else instruction(st))
    return 0


def cmd_done(text):
    st = need_run()
    p = st["pending"]
    if not p:
        print(instruction(st) if st["phase"] in TERMINAL else "ERROR nothing is pending; run `loop.py next`")
        return 1
    if p["kind"] == "ask":
        found = [l.strip() for l in text.splitlines() if l.strip().startswith("RETURN ")]
        if not found or found[-1] != f"RETURN ok {p['answer']}" or not (ROOT / p["answer"]).is_file():
            print(f"ERROR write the user's answers to {p['answer']}, then run: loop.py done \"RETURN ok {p['answer']}\"")
            return 1
        log(st, f"answer {p['answer']}")
        st["pending"] = None
        resume(st, st["stack"].pop(), p["answer"])
        print(advance(st))
        return 0
    head = git("rev-parse", "HEAD").strip()
    if p.get("head") and head != p["head"]:
        # Allowlist checks compare the working tree to HEAD; an agent's commit would hide its files.
        stop(st, f"{p['agent']} moved HEAD from {p['head'][:12]} to {head[:12]}; only loop.py commits. "
                 f"Inspect with `git log {p['head'][:12]}..HEAD`, reset to {p['head'][:12]} if unwanted, then retry")
        print(advance(st))
        return 0
    try:
        kind, arg = parse_return(text, p)
    except ValueError as e:
        log(st, f"bad return {p['n']:02d}: {e}")
        st["pending"] = None
        try:
            relaunch_once(st, p, f"return-{p['retry_of']}",
                          f"Your previous reply was rejected: {e}. End with exactly one RETURN line from the frame.")
        except Stop as s:
            stop(st, str(s))
        print(advance(st))
        return 0
    log(st, f"return {p['n']:02d} {p['agent']}: {kind} {arg}")
    st["pending"] = None
    try:
        if kind in ("deviation", "blocked"):
            raise Stop(f"{p['agent']} returned {kind}: {arg}")
        if kind == "call":
            callee, req = arg.split()
            if len(st["stack"]) + 2 > MAX_DEPTH:
                raise Stop(f"call depth over {MAX_DEPTH}: {p['agent']} -> {callee}")
            st["stack"].append({**p, "via": "call", "callee": callee})
            launch(st, callee, f"Request from {p['agent']}: read `{req}` and answer it.")
        elif kind == "ask":
            st["stack"].append({**p, "via": "ask"})
            st["pending"] = {"kind": "ask", "q": arg, "answer": p["ask"].replace(".ask.md", ".answer.md")}
            log(st, f"ask {arg}")
        elif st["stack"]:
            resume(st, st["stack"].pop(), arg)
        else:
            PHASES[st["phase"]][1](st, stack_values(), p)
    except Stop as e:
        stop(st, str(e))
    print(advance(st))
    return 0


def cmd_test(cmd):
    """Run a test command for the pending frame (the worker calls this): digest out, full log kept."""
    run = current_run()
    if not run:
        print("ERROR no pending run")
        return 1
    st, sv = load(run), stack_values()
    n = st["pending"]["n"] if st.get("pending") else 0
    k = len(list((run_dir(st) / "logs").glob(f"test-{n:02d}-*.txt"))) + 1 if (run_dir(st) / "logs").is_dir() else 1
    code, results, _, dg = run_tests(st, sv, cmd, f"test-{n:02d}-{k}")
    print(dg)
    return 0 if code == 0 and results is not None and all(s in ("pass", "skip") for _, s, _ in results) else 1


LOG_LINE = re.compile(r"^(\S+) (\S+) ?(.*)$")


def report(run):
    """Metrics of one run from its log.md and state.json (HD-22)."""
    st = load(run)
    lines = [LOG_LINE.match(l) for l in (ROOT / SCRATCH / run / "log.md").read_text().splitlines()]
    lines = [(m.group(1), m.group(2), m.group(3)) for m in lines if m]
    times = [datetime.fromisoformat(t) for t, _, _ in lines]
    launches, relaunched, frame_bytes = {}, set(), 0
    for _, kind, rest in lines:
        if kind == "launch":
            parts = rest.split()
            launches[parts[1]] = launches.get(parts[1], 0) + 1
            frame_bytes += int(parts[2][:-1]) if len(parts) > 2 and parts[2].endswith("b") else 0
        elif kind == "relaunch":
            relaunched.add(rest)
    steps_done = sum(1 for _, k, rest in lines if k == "commit:" and re.search(r": step \d+ ", rest))
    step_relaunches = sum(1 for k in relaunched if k.startswith("step-"))
    outcome = st["phase"] + (f" ({first_line(st['stop'])[:60]})" if st["phase"] == "stopped" else "")
    return {"run": run, "task": st["task"] or "-", "outcome": outcome,
            "elapsed": str(times[-1] - times[0]).split(".")[0] if times else "-",
            "launches": launches, "relaunches": len(relaunched),
            "stops": sum(1 for _, k, _ in lines if k == "STOP"),
            "first_try": f"{max(steps_done - step_relaunches, 0)}/{len(st['plan']['steps']) if st['plan'] else 0}",
            "tidy": sum(1 for _, k, _ in lines if k == "tidy"), "frame_bytes": frame_bytes}


def cmd_report(all_runs):
    runs = sorted((p.name for p in (ROOT / SCRATCH).glob("run-*") if p.name[4:].isdigit()),
                  key=lambda n: int(n[4:])) if all_runs else [current_run()]
    if not runs or runs == [None]:
        print("idle: no run")
        return 0
    for run in runs:
        if not (ROOT / SCRATCH / run / "state.json").is_file():
            continue
        m = report(run)
        per = " ".join(f"{a}={n}" for a, n in sorted(m["launches"].items()))
        if all_runs:
            print(f"{m['run']} {m['task']} {m['outcome']} elapsed={m['elapsed']} launches={sum(m['launches'].values())} "
                  f"relaunches={m['relaunches']} stops={m['stops']} first-try={m['first_try']} tidy={m['tidy']} "
                  f"frames={m['frame_bytes']}b")
        else:
            print("\n".join([f"run: {m['run']}", f"task: {m['task']}", f"outcome: {m['outcome']}",
                             f"elapsed: {m['elapsed']}", f"launches: {sum(m['launches'].values())} ({per})",
                             f"relaunches: {m['relaunches']}", f"stops: {m['stops']}",
                             f"steps green on first try: {m['first_try']}", f"tidy runs: {m['tidy']}",
                             f"frame bytes written: {m['frame_bytes']}"]))
    return 0


def cmd_status():
    run = current_run()
    if not run:
        print("idle: no run")
        return 0
    st = load(run)
    step = f" step {st['step'] + 1}/{len(st['plan']['steps'])}" if st["plan"] and st["phase"] == "step" else ""
    print(f"{run} {st['task'] or '(no task yet)'} {st['phase']}{step} depth {len(st['stack'])}: {instruction(st)}")
    return 0


def cmd_retry():
    st = need_run()
    if st["phase"] != "stopped":
        print("ERROR the run is not stopped")
        return 1
    dirty = [p for p in changed_paths() if not p.startswith(("backlog/", SCRATCH + "/"))]
    if dirty:
        print(f"STOP the working tree is not clean: {', '.join(dirty[:10])}; commit or discard first")
        return 1
    st["phase"], st["stop"], st["retries"], st["tidy_queue"] = st.pop("stopped_in"), None, {}, []
    log(st, "retry")
    print(advance(st))
    return 0


def cmd_abandon():
    st = need_run()
    if st["phase"] not in TERMINAL:
        stop(st, "abandoned by the user")
        save(st)
    (ROOT / SCRATCH / "current").unlink()
    print(f"abandoned {st['run']}")
    return 0


def hook_stop(event):
    """Stop hook: hold the main thread while a run waits on it, at most STOP_BLOCKS times in a row."""
    run = current_run()
    if not run:
        return 0
    st = load(run)
    if st["phase"] in TERMINAL or (st["pending"] or {}).get("kind") == "ask":
        return 0
    if st["stop_blocks"] >= STOP_BLOCKS:
        return 0
    st["stop_blocks"] += 1
    save(st)
    p = st["pending"]
    todo = (f"The last instruction was: {instruction(st)}. When that agent has returned, run "
            f"`python3 -I meta/core/tools/loop.py done \"<its RETURN line>\"`." if p else
            "Run `python3 -I meta/core/tools/loop.py next`.")
    print(f"A factory run is in progress ({run}). {todo} Do what it prints.", file=sys.stderr)
    return 2


def hook_subagent_stop(event):
    """SubagentStop hook: a loop agent may not finish without a valid RETURN line for its frame."""
    run = current_run()
    if not run or event.get("stop_hook_active"):
        return 0
    st = load(run)
    p = st["pending"]
    if not p or p.get("kind") != "launch" or event.get("agent_type") not in (p["agent"], None, ""):
        return 0
    try:
        parse_return(event.get("last_assistant_message") or "", p)
    except ValueError as e:
        print(f"Your reply was rejected: {e}. Finish the job of `{p['in']}`, then end with exactly one "
              f"RETURN line from its 'Last line' section.", file=sys.stderr)
        return 2
    return 0


def main(argv):
    if not argv:
        print(__doc__.split("Usage:")[1].split("Python")[0].strip())
        return 1
    cmd, rest = argv[0], argv[1:]
    if cmd in ("hook-stop", "hook-subagent-stop"):
        try:
            event = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            event = {}
        try:
            return (hook_stop if cmd == "hook-stop" else hook_subagent_stop)(event)
        except (OSError, ValueError, KeyError):
            return 0  # a broken run must never trap the session
    simple = {"next": cmd_next, "status": cmd_status, "retry": cmd_retry, "abandon": cmd_abandon}
    try:
        if cmd == "start" and len(rest) == 1:
            return cmd_start(rest[0])
        if cmd == "done" and len(rest) == 1:
            return cmd_done(rest[0])
        if cmd == "test" and len(rest) == 1:
            return cmd_test(rest[0])
        if cmd == "report" and rest in ([], ["--all"]):
            return cmd_report(bool(rest))
        if cmd in simple and not rest:
            return simple[cmd]()
    except Stop as e:
        print(f"STOP {e}")
        return 1
    print("ERROR usage: loop.py start <TASK-n|request file> | next | done \"<RETURN line>\" | test \"<command>\" "
          "| report [--all] | status | retry | abandon")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
