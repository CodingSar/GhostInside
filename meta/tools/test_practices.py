#!/usr/bin/env python3
"""Tests for practices.py. Run: python3 -I meta/tools/test_practices.py

Everything runs in temp dirs: a local bare repo stands in for the central
repo, a fake `gh` stands in for GitHub. The real meta/practices is untouched.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "practices.py"

GOOD = """---
id: lang/python
title: Python
researched: 2026-10-01
tier: standard
sources:
  - https://docs.python.org/3/
---

| ID | Level | Rule | Enforce | Source |
|---|---|---|---|---|
| PY-001 | MUST | Type-annotate every public function. | lint: ruff ANN | https://docs.astral.sh/ruff/rules/ |
| PY-002 | SHOULD | Keep one public entry per module. | review | https://peps.python.org/pep-0008/ |
"""


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class PracticesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.bare = t / "central.git"
        seed = t / "seed"
        seed.mkdir()
        (seed / "lang").mkdir()
        (seed / "lang" / "python.md").write_text(GOOD)
        (seed / "index.json").write_text(json.dumps({"version": 1, "packs": [
            {"id": "lang/python", "path": "lang/python.md", "researched": "2026-10-01", "tier": "standard"}
        ]}))
        git("init", "-q", "-b", "main", cwd=seed)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x", cwd=seed)
        git("add", "-A", cwd=seed)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "seed", cwd=seed)
        git("clone", "-q", "--bare", str(seed), str(self.bare), cwd=t)
        bin_dir = t / "bin"
        bin_dir.mkdir()
        fake_gh = bin_dir / "gh"
        fake_gh.write_text("#!/bin/sh\n[ \"$2\" = list ] && exit 0\necho https://example.test/pr/1\n")
        fake_gh.chmod(0o755)
        self.practices = t / "practices"
        self.practices.mkdir()
        self.env = dict(
            os.environ,
            GHOSTINSIDE_PRACTICES_URL=str(self.bare),
            GHOSTINSIDE_PRACTICES_CACHE=str(t / "cache"),
            GHOSTINSIDE_PRACTICES_DIR=str(self.practices),
            GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
            GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
            GHOSTINSIDE_GH=str(fake_gh),
        )
        self.t = t

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args],
                              env=self.env, capture_output=True, text=True)

    def write(self, rel, text):
        p = self.t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return str(p)

    def test_status_hit_stale_miss(self):
        self.assertEqual(self.run_cli("fetch").returncode, 0)
        out = self.run_cli("status", "lang/python", "domain/payments", "--today", "2026-10-05").stdout
        self.assertIn("hit lang/python", out)
        self.assertIn("miss domain/payments", out)
        out = self.run_cli("status", "lang/python", "--today", "2026-10-09").stdout
        self.assertIn("stale lang/python", out)

    def test_check_accepts_good_pack(self):
        r = self.run_cli("check", self.write("lang/python.md", GOOD))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_check_rejects_bad_packs(self):
        cases = {
            "bad level": GOOD.replace("| MUST |", "| MAY |"),
            "bad enforce": GOOD.replace("| review |", "| eyeball |"),
            "no source url": GOOD.replace("https://peps.python.org/pep-0008/", "pep8"),
            "pipe in rule": GOOD.replace("Keep one public", "Keep | one public"),
            "duplicate id": GOOD.replace("PY-002", "PY-001"),
            "missing field": GOOD.replace("tier: standard\n", ""),
        }
        for name, text in cases.items():
            r = self.run_cli("check", self.write("lang/python.md", text))
            self.assertEqual(r.returncode, 1, name)
        domain = GOOD.replace("id: lang/python", "id: domain/payments")
        r = self.run_cli("check", self.write("domain/payments.md", domain))
        self.assertIn("must be tier deep", r.stdout)
        r = self.run_cli("check", self.write("lang/other.md", GOOD))
        self.assertIn("file path must end with lang/python.md", r.stdout)

    def test_vendor_and_verify(self):
        self.run_cli("fetch")
        local = self.write("new/framework/fastapi.md", GOOD.replace("lang/python", "framework/fastapi")
                           .replace("PY-", "FA-").replace("title: Python", "title: FastAPI"))
        r = self.run_cli("vendor", "lang/python", local)
        self.assertEqual(r.returncode, 0, r.stderr)
        lock = json.loads((self.practices / "practices.lock").read_text())
        self.assertEqual([p["id"] for p in lock["packs"]], ["framework/fastapi", "lang/python"])
        self.assertEqual({p["origin"] for p in lock["packs"]}, {"central", "local"})
        review = (self.practices / "review.md").read_text()
        self.assertIn("PY-002 SHOULD", review)
        self.assertNotIn("PY-001", review)
        self.assertIn("| lang/python | PY-001 |", (self.practices / "enforced.md").read_text())
        self.assertEqual(self.run_cli("verify").returncode, 0)

        pack = self.practices / "packs" / "lang" / "python.md"
        pack.write_text(pack.read_text() + "\n")
        r = self.run_cli("verify")
        self.assertEqual(r.returncode, 1)
        self.assertIn("pack changed since vendor: lang/python", r.stdout)

    def test_vendor_set_is_exact(self):
        self.run_cli("fetch")
        local = self.write("x/framework/fastapi.md", GOOD.replace("lang/python", "framework/fastapi"))
        self.run_cli("vendor", "lang/python", local)
        self.run_cli("vendor", "lang/python")
        self.assertFalse((self.practices / "packs" / "framework" / "fastapi.md").exists())
        self.assertEqual(self.run_cli("verify").returncode, 0)

    def test_vendor_unknown_id_fails(self):
        self.run_cli("fetch")
        r = self.run_cli("vendor", "domain/payments")
        self.assertEqual(r.returncode, 1)

    def test_propose_pushes_branch_and_opens_pr(self):
        pack = self.write("p/domain/payments.md", GOOD.replace("lang/python", "domain/payments")
                          .replace("tier: standard", "tier: deep").replace("PY-", "PAY-"))
        r = self.run_cli("propose", pack)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("https://example.test/pr/1", r.stdout)
        heads = subprocess.run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/pack"],
                               cwd=self.bare, capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(len(heads), 1)
        self.assertTrue(heads[0].startswith("pack/domain-payments-2026-10-01-"))
        show = subprocess.run(["git", "show", f"{heads[0]}:index.json"], cwd=self.bare,
                              capture_output=True, text=True, check=True).stdout
        ids = [p["id"] for p in json.loads(show)["packs"]]
        self.assertEqual(ids, ["domain/payments", "lang/python"])

        rerun = self.run_cli("propose", pack)
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertIn("branch already pushed", rerun.stdout)

    def test_propose_without_gh_reports_branch(self):
        pack = self.write("p/domain/payments.md", GOOD.replace("lang/python", "domain/payments")
                          .replace("tier: standard", "tier: deep").replace("PY-", "PAY-"))
        self.env["GHOSTINSIDE_GH"] = str(self.t / "no-such-gh")
        r = self.run_cli("propose", pack)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("PR not opened: domain/payments branch=pack/domain-payments-", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
