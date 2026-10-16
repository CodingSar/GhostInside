#!/usr/bin/env python3
"""Tests for loop.py. Run: python3 -I meta/core/tools/test_loop.py

Each test builds a product repo in a temp dir: a git repo with a bare
`origin`, a set stack whose commands are fake scripts outside the repo, and a
fake `backlog` CLI on PATH that keeps tasks in a JSON file. The test plays
the main thread and the agents: it writes the files an agent would write and
reports its RETURN line. The real harness is untouched.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "loop.py"

FAKE_BACKLOG = r'''#!/usr/bin/env python3
import json, sys
from pathlib import Path
store = Path(__file__).with_name("tasks.json")
tasks = json.loads(store.read_text())
a = sys.argv[1:]
if a[:2] == ["task", "view"]:
    print(json.dumps({"task": tasks[a[2]]}))
    sys.exit(0)
if a[:2] == ["task", "edit"]:
    t, i = tasks[a[2]], 3
    while i < len(a):
        flag, val = a[i], a[i + 1]
        if flag == "-s": t["status"] = val
        elif flag == "-a": t["assignees"] = [val]
        elif flag == "--append-notes": t["implementationNotes"] = (t.get("implementationNotes") or "") + val + "\n"
        elif flag == "--plan": t["implementationPlan"] = val
        elif flag == "--check-ac": t["acceptanceCriteria"][int(val) - 1]["checked"] = True
        elif flag == "--final-summary": t["finalSummary"] = val
        i += 2
    store.write_text(json.dumps(tasks))
    sys.exit(0)
print("fake backlog: unsupported " + " ".join(a), file=sys.stderr)
sys.exit(1)
'''

# Fake stack commands. Behaviour comes from fake.json next to the script:
# {"tests": {name: "pass"|"fail"|"error"}, "targeted": exit code, "check": [exit code, output]}
FAKE_STACK = r'''#!/usr/bin/env python3
import json, sys
from pathlib import Path
cfg = json.loads(Path(__file__).with_name("fake.json").read_text())
mode = sys.argv[1]
if mode == "full":
    cases = []
    for name, status in cfg["tests"].items():
        child = {"pass": "", "fail": '<failure message="NotImplementedError"/>',
                 "error": '<error message="ImportError"/>'}[status]
        cases.append(f'<testcase classname="t" name="{name}">{child}</testcase>')
    Path(cfg["report"]).write_text("<testsuites><testsuite>" + "".join(cases) + "</testsuite></testsuites>")
    sys.exit(0 if all(s == "pass" for s in cfg["tests"].values()) else 1)
if mode == "targeted":
    sys.exit(cfg["targeted"])
if mode == "check":
    print(cfg["check"][1])
    sys.exit(cfg["check"][0])
'''

PLAN = """1. Pay an order
   Files: src/modules/billing/slices/pay/handler.py
   Criteria: 1, 2
   Test: {targeted} src/modules/billing/slices/pay
Catalog: src/modules/billing/_about.md :: - `pay`: pay an order"""


def load_module(root):
    spec = importlib.util.spec_from_file_location("loop_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = Path(root)
    return mod


class Repo:
    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.root = self.tmp / "repo"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.root.mkdir()
        (self.bin / "backlog").write_text(FAKE_BACKLOG)
        (self.bin / "backlog").chmod(0o755)
        (self.bin / "fake.py").write_text(FAKE_STACK)
        self.env = dict(os.environ, GHOSTINSIDE_ROOT=str(self.root),
                        PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                        GIT_COMMITTER_EMAIL="t@t")
        fake = f"python3 {self.bin / 'fake.py'}"
        self.targeted = f"{fake} targeted"
        self.files({
            ".gitignore": ".scratch/\nreports/\n",
            "meta/core/defaults/architecture.md": "# architecture\n",
            "meta/core/defaults/persistence.md": "# persistence\n",
            "meta/product/practices/review.md": "# review\n",
            "meta/product/stack.md": "\n".join(f"| {k} | `{v}` |" for k, v in {
                "test command (full)": f"{fake} full", "test command (targeted, takes a path)": self.targeted,
                "check command": f"{fake} check", "fix command": "true",
                "test report (JUnit XML)": "reports/junit.xml", "source root": "src",
                "test file pattern": r"^test_.*\.py$", "entry file stems": "index, handler"}.items()) + "\n",
            "src/_about.md": "# modules\n",
        })
        (self.root / "meta/core/tools").mkdir(parents=True)
        shutil.copy(TOOLS / "packet.py", self.root / "meta/core/tools/packet.py")
        (self.root / "reports").mkdir()
        self.fake(tests={}, targeted=0, check=[0, ""])
        self.tasks({"TASK-1": self.task(["GIVEN an order WHEN paid THEN status paid",
                                         "GIVEN a paid order WHEN paid again THEN rejected"])})
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        subprocess.run(["git", "init", "-q", "--bare", str(self.tmp / "origin.git")], check=True)
        self.git("remote", "add", "origin", str(self.tmp / "origin.git"))

    @staticmethod
    def task(texts):
        return {"id": "TASK-1", "status": "To Do", "implementationPlan": None,
                "acceptanceCriteria": [{"index": i, "text": t, "checked": False} for i, t in enumerate(texts, 1)]}

    def files(self, files):
        for rel, text in files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)

    def fake(self, **cfg):
        path = self.bin / "fake.json"
        old = json.loads(path.read_text()) if path.exists() else {"report": str(self.root / "reports/junit.xml")}
        path.write_text(json.dumps({**old, **cfg}))

    def tasks(self, tasks=None):
        store = self.bin / "tasks.json"
        if tasks is not None:
            store.write_text(json.dumps(tasks))
        return json.loads(store.read_text())

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env, check=True,
                              capture_output=True, text=True).stdout

    def loop(self, *args, stdin=None):
        out = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=self.root, env=self.env,
                             capture_output=True, text=True, input=stdin)
        return out.returncode, out.stdout.strip(), out.stderr.strip()

    def say(self, *args):
        return self.loop(*args)[1]

    def frame(self, line):
        """(agent, frame text, out path) of a LAUNCH line."""
        _, agent, path = line.split()
        return agent, (self.root / path).read_text(), path.replace(".in.md", ".out.md")

    def ok(self, line, text="done"):
        """Play the launched agent: write its output, return ok, get the next line."""
        _, _, out = self.frame(line)
        (self.root / out).write_text(text)
        return self.say("done", f"RETURN ok {out}")

    def to_red(self):
        line = self.say("start", "TASK-1")
        line = self.ok(line, "task: TASK-1\n")
        t = self.tasks()
        t["TASK-1"]["implementationPlan"] = PLAN.format(targeted=self.targeted)
        self.tasks(t)
        return self.ok(line)

    def write_tests(self, statuses):
        self.files({"src/modules/billing/slices/pay/handler.py": "def pay(order): raise NotImplementedError\n",
                    "src/modules/billing/slices/pay/test_pay.py": "# TASK-1#1, TASK-1#2\n"})
        self.fake(tests=statuses)


class LoopTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.r = Repo(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_happy_path_runs_a_task_to_done(self):
        r = self.r
        line = r.say("start", "TASK-1")
        self.assertTrue(line.startswith("LAUNCH intake .scratch/run-1/frames/01-intake.in.md"), line)
        line = r.ok(line, "task: TASK-1\n")
        self.assertTrue(line.startswith("LAUNCH planner"), line)
        t = r.tasks()
        self.assertEqual(t["TASK-1"]["status"], "In Progress")
        t["TASK-1"]["implementationPlan"] = PLAN.format(targeted=r.targeted)
        r.tasks(t)
        line = r.ok(line)
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "test-writer")
        self.assertIn("2. GIVEN a paid order", text)
        self.assertIn("- `src/modules/billing/`", text.split("## Edit only")[1])
        self.assertNotIn("## Edit only", (r.root / ".scratch/run-1/frames/01-intake.in.md").read_text())
        self.assertIn("- `.scratch/run-1/packets/rules.md`\n- `.scratch/run-1/packets/billing-pay.md`", text)
        rules = (r.root / ".scratch/run-1/packets/rules.md").read_text()
        module = (r.root / ".scratch/run-1/packets/billing-pay.md").read_text()
        self.assertIn("stack.md", rules)
        self.assertNotIn("stack.md", module)
        self.assertIn("new module: src/modules/billing does not exist", module)
        r.write_tests({"TASK-1#1 paid": "fail", "TASK-1#2 twice": "fail", "old test": "pass"})
        line = r.ok(line)
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "implementer")
        self.assertLess(text.index("## Edit only"), text.index("## Last line"))
        self.assertIn("- `src/modules/billing/slices/pay/handler.py`", text.split("## Edit only")[1])
        state = json.loads((r.root / ".scratch/run-1/state.json").read_text())
        self.assertEqual(state["pending"]["allow"], ["src/modules/billing/slices/pay/handler.py"])
        self.assertIn("- `pay`: pay an order", (r.root / "src/modules/billing/_about.md").read_text())
        r.files({"src/modules/billing/slices/pay/handler.py": "def pay(order): return 'paid'\n"})
        r.fake(tests={"TASK-1#1 paid": "pass", "TASK-1#2 twice": "pass", "old test": "pass"})
        line = r.ok(line)
        self.assertTrue(line.startswith("DONE TASK-1 done: 3 tests green, 2 criteria checked"), line)
        t = r.tasks()["TASK-1"]
        self.assertEqual(t["status"], "Done")
        self.assertTrue(all(c["checked"] for c in t["acceptanceCriteria"]))
        log = r.git("log", "--format=%s")
        # The fake Backlog keeps tasks outside the repo, so intake, plan, and close have nothing to commit.
        self.assertEqual(log.split("\n")[:3], ["TASK-1: step 1 Pay an order", "TASK-1: failing tests and stubs", "init"])
        self.assertEqual(r.git("rev-parse", "HEAD"), r.git("rev-parse", "origin/main"))

    def test_next_repeats_the_pending_instruction_after_a_restart(self):
        line = self.r.say("start", "TASK-1")
        self.assertEqual(self.r.say("next"), line)
        self.assertIn("intake", self.r.say("status"))

    def test_call_pushes_a_frame_and_resumes_the_caller_with_the_result(self):
        r = self.r
        line = r.ok(r.say("start", "TASK-1"), "task: TASK-1\n")
        self.assertTrue(line.startswith("LAUNCH planner .scratch/run-1/frames/02-planner.in.md"), line)
        call = ".scratch/run-1/frames/02-planner.call.md"
        r.files({call: "Which migration tool?"})
        line = r.say("done", f"RETURN call researcher {call}")
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "researcher")
        self.assertIn(call, text)
        self.assertIn("depth 1", r.say("status"))
        line = r.ok(line, "Use the stack's tool.")
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "planner")
        self.assertIn("03-researcher.out.md", text)
        self.assertIn("02-planner.in.md", text)
        self.assertIn("depth 0", r.say("status"))

    def test_disallowed_call_is_relaunched_once_then_stops(self):
        r = self.r
        line = r.to_red()
        _, _, out = r.frame(line)
        call = out.replace(".out.md", ".call.md")
        r.files({call: "x"})
        line = r.say("done", f"RETURN call researcher {call}")
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "test-writer")
        self.assertIn("may not call researcher", text)
        line = r.say("done", "I think I am finished.")
        self.assertTrue(line.startswith("STOP test-writer failed twice"), line)

    def test_ask_round_trip_through_the_main_thread(self):
        r = self.r
        line = r.say("start", "TASK-1")
        ask = ".scratch/run-1/frames/01-intake.ask.md"
        r.files({ask: "Confirm criterion 2?"})
        line = r.say("done", f"RETURN ask {ask}")
        answer = ".scratch/run-1/frames/01-intake.answer.md"
        self.assertEqual(line, f"ASK {ask} {answer}")
        code, out, _ = r.loop("done", f"RETURN ok {answer}")
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("ERROR write the user's answers"), out)
        r.files({answer: "Yes."})
        agent, text, _ = r.frame(r.say("done", f"RETURN ok {answer}"))
        self.assertEqual(agent, "intake")
        self.assertIn(answer, text)

    def test_assumed_criteria_stop_before_planning(self):
        r = self.r
        r.tasks({"TASK-1": r.task(["ASSUMED: GIVEN x WHEN y THEN z"])})
        line = r.ok(r.say("start", "TASK-1"), "task: TASK-1\n")
        self.assertEqual(line, "STOP criteria still ASSUMED: 1; confirm them with the user, then retry")

    def test_red_gate_rejects_a_passing_new_test_and_discards_the_changes(self):
        r = self.r
        line = r.to_red()
        r.write_tests({"TASK-1#1 paid": "pass", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "test-writer")
        self.assertIn("red gate failed", text)
        self.assertIn("- t TASK-1#1 paid: pass, expected a failing test", text)
        self.assertIn("Write the failing tests and stubs for TASK-1 again", text)
        self.assertFalse((r.root / "src/modules/billing/slices/pay/handler.py").exists())
        gate = (r.root / ".scratch/run-1/logs/red-gate.txt").read_text()
        self.assertIn("TASK-1#1 paid: pass, expected a failing test", gate)

    def test_red_gate_rejects_errors_and_missing_criteria(self):
        m = load_module(self.r.root)
        errors = m.red_gate("TASK-1", 3, [("t TASK-1#1 a", "error", ""), ("t TASK_1_2 b", "fail", ""),
                                           ("t other", "fail", "boom")])
        self.assertIn("t TASK-1#1 a: error, expected a failing test (assertion or not-implemented)", errors)
        self.assertIn("criterion 3: no test named TASK-1#3", errors)
        self.assertIn("t other: fail boom", errors)
        self.assertEqual(len(errors), 3)
        self.assertNotRegex("TASK-1#10", m.crit_re("TASK-1", 1))

    def test_implementer_outside_its_allowlist_stops_the_run(self):
        r = self.r
        line = r.to_red()
        r.write_tests({"TASK-1#1 paid": "fail", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        r.files({"src/shared/util.py": "x = 1\n"})
        line = r.ok(line)
        self.assertEqual(line, "STOP step 1 changed files outside its allowlist: src/shared/util.py")
        code, out, _ = r.loop("retry")
        self.assertTrue(out.startswith("STOP the working tree is not clean"), out)

    def test_failed_step_relaunch_carries_a_digest(self):
        r = self.r
        line = r.to_red()
        r.write_tests({"TASK-1#1 paid": "fail", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        r.files({"src/modules/billing/slices/pay/handler.py": "def pay(order): return 'paid'\n"})
        r.fake(targeted=1, tests={"TASK-1#1 paid": "pass", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "implementer")
        self.assertIn("Step 1: Pay an order, again.", text)
        self.assertIn("2. GIVEN a paid order WHEN paid again THEN rejected", text)
        self.assertIn("FAIL (exit 1, no JUnit report)", text)
        self.assertIn("Full output: `.scratch/run-1/logs/step-1.txt`", text)

    def test_the_test_command_prints_a_digest_and_keeps_the_log(self):
        r = self.r
        line = r.to_red()
        r.write_tests({"TASK-1#1 paid": "fail", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        r.fake(tests={"TASK-1#1 paid": "pass", "TASK-1#2 twice": "fail", "old": "pass"})
        code, out, _ = r.loop("test", f"python3 {r.bin / 'fake.py'} full")
        self.assertEqual(code, 1)
        self.assertEqual(out.split("\n")[0], "FAIL: 2 of 3 tests pass, 1 fail")
        self.assertIn("- t TASK-1#2 twice: fail NotImplementedError", out)
        self.assertTrue(out.endswith("Full output: `.scratch/run-1/logs/test-04-1.txt`"), out)
        self.assertIn("$ python3", (r.root / ".scratch/run-1/logs/test-04-1.txt").read_text())
        r.fake(tests={"TASK-1#1 paid": "pass", "TASK-1#2 twice": "pass"})
        code, out, _ = r.loop("test", f"python3 {r.bin / 'fake.py'} full")
        self.assertEqual((code, out.split("\n")[0]), (0, "PASS: 2 of 2 tests pass, 0 fail"))
        self.assertTrue(out.endswith("test-04-2.txt`"), out)
        code, out, _ = r.loop("test", "echo hi; echo there; exit 3")
        self.assertEqual(code, 1)
        self.assertIn("FAIL (exit 3, no JUnit report); last output lines:\n  hi\n  there", out)
        mod = load_module(r.root)
        many = [(f"t{i}", "fail", "boom") for i in range(30)]
        lines = mod.digest(1, "", many, "x.txt").split("\n")
        self.assertEqual(len(lines), mod.DIGEST_LINES)
        self.assertEqual(lines[-2], "- ... and 13 more")

    def test_plan_parsing(self):
        m = load_module(self.r.root)
        sv = {"full": "pytest", "targeted": "pytest", "src": "src", "tests": r"^test_.*\.py$"}
        plan = m.parse_plan(PLAN.format(targeted="pytest"), 2, sv)
        self.assertEqual(plan["steps"][0]["criteria"], [1, 2])
        self.assertEqual(plan["catalogs"], [["src/modules/billing/_about.md", "- `pay`: pay an order"]])
        bad = ("1. Hack\n   Files: meta/core/guides/test.md, src/modules/a/test_a.py\n   Criteria: 1\n"
               "   Test: rm -rf src\n2. Mask\n   Files: src/modules/a/index.py\n   Criteria: 2\n"
               "   Test: pytest src/modules/a; true\n")
        with self.assertRaises(ValueError) as e:
            m.parse_plan(bad, 2, sv)
        msg = str(e.exception)
        self.assertIn("file not allowed: meta/core/guides/test.md", msg)
        self.assertIn("test file in Files: src/modules/a/test_a.py", msg)
        self.assertIn("step 1: Test must be the full test command or start with: pytest", msg)
        self.assertIn("step 2: Test takes paths only after the targeted command", msg)
        with self.assertRaises(ValueError) as e:
            m.parse_plan(bad.replace("Criteria: 2", "Criteria: none"), 2, sv)
        self.assertIn("criteria not covered by any step: 2", str(e.exception))

    def test_an_agent_commit_stops_the_run(self):
        r = self.r
        line = r.to_red()
        r.write_tests({"TASK-1#1 paid": "fail", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        r.files({"src/shared/util.py": "x = 1\n"})
        r.git("add", "-A")
        r.git("commit", "-q", "-m", "sneaky")
        line = r.ok(line)
        self.assertTrue(line.startswith("STOP implementer moved HEAD from"), line)

    def test_a_red_suite_stops_the_run_before_planning(self):
        r = self.r
        r.fake(tests={"old test": "fail"})
        line = r.ok(r.say("start", "TASK-1"), "task: TASK-1\n")
        self.assertTrue(line.startswith("STOP the full test suite is not green before TASK-1 starts"), line)

    def test_return_grammar(self):
        m = load_module(self.r.root)
        fr = {"agent": "implementer", "out": "o.md", "call": "c.md", "ask": "a.md"}
        (self.r.root / "o.md").write_text("x")
        self.assertEqual(m.parse_return("notes\n`RETURN ok o.md`", fr), ("ok", "o.md"))
        self.assertEqual(m.parse_return("RETURN deviation needs shared/", fr), ("deviation", "needs shared/"))
        for text, err in (("done", "no RETURN line"), ("RETURN ok other.md", "must name o.md"),
                          ("RETURN maybe", "malformed"), ("RETURN blocked", "needs a reason"),
                          ("RETURN ask a.md", "may not ask")):
            with self.assertRaises(ValueError) as e:
                m.parse_return(text, fr)
            self.assertIn(err, str(e.exception))

    def test_stop_hook_holds_a_pending_run_but_not_an_ask_and_not_forever(self):
        r = self.r
        self.assertEqual(r.loop("hook-stop", stdin="{}")[0], 0)
        r.say("start", "TASK-1")
        code, _, err = r.loop("hook-stop", stdin="{}")
        self.assertEqual(code, 2)
        self.assertIn("loop.py done", err)
        r.loop("hook-stop", stdin="{}")
        r.loop("hook-stop", stdin="{}")
        self.assertEqual(r.loop("hook-stop", stdin="{}")[0], 0)
        ask = ".scratch/run-1/frames/01-intake.ask.md"
        r.files({ask: "q"})
        r.say("done", f"RETURN ask {ask}")
        self.assertEqual(r.loop("hook-stop", stdin="{}")[0], 0)

    def test_subagent_stop_hook_requires_a_valid_return_line(self):
        r = self.r
        r.say("start", "TASK-1")
        bad = json.dumps({"agent_type": "intake", "last_assistant_message": "All done!"})
        code, _, err = r.loop("hook-subagent-stop", stdin=bad)
        self.assertEqual(code, 2)
        self.assertIn("no RETURN line", err)
        r.files({".scratch/run-1/frames/01-intake.out.md": "task: TASK-1\n"})
        good = json.dumps({"agent_type": "intake",
                           "last_assistant_message": "RETURN ok .scratch/run-1/frames/01-intake.out.md"})
        self.assertEqual(r.loop("hook-subagent-stop", stdin=good)[0], 0)
        other = json.dumps({"agent_type": "Explore", "last_assistant_message": "hi"})
        self.assertEqual(r.loop("hook-subagent-stop", stdin=other)[0], 0)
        again = json.dumps({"agent_type": "intake", "last_assistant_message": "x", "stop_hook_active": True})
        self.assertEqual(r.loop("hook-subagent-stop", stdin=again)[0], 0)

    def test_tidy_routes_findings_and_stops_on_files_outside_the_plan(self):
        r = self.r
        line = r.to_red()
        r.write_tests({"TASK-1#1 paid": "fail", "TASK-1#2 twice": "fail"})
        line = r.ok(line)
        r.files({"src/modules/billing/slices/pay/handler.py": "def pay(order): return 'paid'\n"})
        r.fake(check=[1, "src/modules/billing/slices/pay/handler.py:1: E501 line too long"])
        line = r.ok(line)
        agent, text, _ = r.frame(line)
        self.assertEqual(agent, "implementer")
        self.assertIn("tidy: src/modules/billing/slices/pay/handler.py:1: E501", text)
        r.fake(check=[1, "src/_about.md:1: bad catalog"])
        line = r.ok(line)
        self.assertTrue(line.startswith("STOP check still fails after one tidy run"), line)

    def test_start_refuses_an_unset_stack(self):
        r = self.r
        r.files({"meta/product/stack.md": "| test command (full) | TBD |\n"})
        code, out, _ = r.loop("start", "TASK-1")
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("STOP stack"), out)


if __name__ == "__main__":
    unittest.main()
