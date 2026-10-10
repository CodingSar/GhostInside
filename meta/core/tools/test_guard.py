#!/usr/bin/env python3
"""Tests for guard.py. Run: python3 -I meta/core/tools/test_guard.py"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "guard.py"

BLOCKED = [
    "git push --force",
    "git push -f origin main",
    "git push -uf origin main",
    "git push --force-with-lease origin main",
    "git push --force-with-lease=main origin main",
    "git push --force-if-includes origin main",
    "git push --mirror",
    "git push origin +main",
    "git -C repo push --force",
    "git -c core.x=y push -f",
    "cd x && git push --force",
    "FOO=1 git push -f",
    "env git push -f",
    "rm -rf build",
    "rm -fr build",
    "rm -r -f build",
    "rm -Rf build",
    "rm --recursive --force build",
    "/bin/rm -rf build",
    "echo ok; rm -rf /",
    "bash -c 'git push --force'",
    "sh -c \"rm -rf x\"",
    "eval git push -f",
    "sudo ls",
    "ls | xargs rm -rf",
    "echo hi\nrm -rf x",
    "cd x\ngit push --force origin main",
    "bash -lc 'git push -f'",
    "bash -ec 'rm -rf x'",
    "timeout 60 git push -f",
    "nice git push -f",
    "nice -n 5 rm -rf x",
    "if true; then rm -rf x; fi",
    "{ rm -rf x; }",
    "! rm -rf x",
    "for d in a b; do rm -rf $d; done",
    "echo `rm -rf x`",
    "echo $(git push --force)",
    "find . -exec rm -rf {} +",
    "find . -name x -execdir rm -fr {} \\;",
    "env -u FOO git push -f",
    "xargs -n1 rm -rf",
    "git push --force-w origin main",
    "git push --mirr",
    "git push --for origin main",
    "rm --rec --forc x",
    "git push -f 'unbalanced",
]

ALLOWED = [
    "git push origin main",
    "git push -q origin main",
    "git push -u origin main",
    "git status",
    "git commit -m 'git push --force is blocked'",
    "rm file.txt",
    "rm -r empty-dir",
    "rm -f file.txt",
    "echo rm -rf",
    "grep -rf patterns.txt .",
    "python3 -I meta/core/tools/check-harness.sh",
    "",
    "git push --follow-tags origin main",
    "git push --no-force-with-lease origin main",
    "timeout 60 git push origin main",
    "find . -name '*.pyc' -exec rm {} +",
    "echo 'line1\nline2'",
    "git commit -m 'subject\n\nbody'",
]


class GuardTest(unittest.TestCase):
    def test_blocked(self):
        for cmd in BLOCKED:
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(guard.check(cmd))

    def test_allowed(self):
        for cmd in ALLOWED:
            with self.subTest(cmd=cmd):
                self.assertIsNone(guard.check(cmd))

    def test_hook_exit_codes(self):
        def run(cmd):
            event = {"tool_name": "Bash", "tool_input": {"command": cmd}}
            return subprocess.run([sys.executable, "-I", str(SCRIPT)], input=json.dumps(event),
                                  capture_output=True, text=True)
        blocked = run("git push --force")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("force push", blocked.stderr)
        self.assertEqual(run("git push origin main").returncode, 0)


if __name__ == "__main__":
    unittest.main()
