#!/usr/bin/env python3
"""Tests for packet.py. Run: python3 -I meta/core/tools/test_packet.py

Each test builds a fake repo root in a temp dir; GHOSTINSIDE_ROOT points the
script at it. The real harness files are untouched.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "packet.py"

HARNESS = {
    "meta/core/defaults/architecture.md": "# default architecture\nrule A\n",
    "meta/core/defaults/persistence.md": "# default persistence\n",
    "meta/product/practices/review.md": "# Review rules\n",
}
STACK_SET = "| source root | `src` |\n| entry file stems | `index, handler` |\n"
STACK_TBD = "| source root | TBD (default `src`) |\n| entry file stems | TBD |\n"


class PacketTest(unittest.TestCase):
    def run_packet(self, files, *args):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, text in files.items():
                p = Path(tmp) / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            env = dict(os.environ, GHOSTINSIDE_ROOT=tmp)
            out = subprocess.run([sys.executable, "-I", str(SCRIPT), *args],
                                 env=env, capture_output=True, text=True)
            return out.returncode, out.stdout, out.stderr

    def test_stack_tbd_stops(self):
        code, _, err = self.run_packet({**HARNESS, "meta/product/stack.md": STACK_TBD}, "billing")
        self.assertEqual(code, 1)
        self.assertIn("stack not set", err)

    def test_new_module_is_a_note(self):
        code, out, _ = self.run_packet({**HARNESS, "meta/product/stack.md": STACK_SET}, "billing", "pay")
        self.assertEqual(code, 0)
        self.assertIn("meta/core/defaults/architecture.md:2: rule A", out)
        self.assertIn("new module: src/modules/billing does not exist", out)

    def test_product_override_wins(self):
        files = {**HARNESS, "meta/product/stack.md": STACK_SET,
                 "meta/product/architecture.md": "# product architecture\n"}
        code, out, _ = self.run_packet(files, "billing")
        self.assertIn("== meta/product/architecture.md ==", out)
        self.assertNotIn("default architecture", out)

    def test_existing_module_and_slice(self):
        files = {**HARNESS, "meta/product/stack.md": STACK_SET,
                 "src/_about.md": "| `billing` | invoices |\n",
                 "src/modules/billing/_about.md": "- `pay`\n",
                 "src/modules/billing/index.py": "from .slices.pay.handler import pay\n",
                 "src/modules/billing/slices/pay/handler.py": "def pay(): ...\n",
                 "src/modules/billing/slices/pay/test_handler.py": "\n"}
        code, out, _ = self.run_packet(files, "billing", "pay")
        self.assertEqual(code, 0)
        self.assertIn("src/modules/billing/index.py:1: from .slices.pay.handler import pay", out)
        self.assertIn("src/modules/billing/slices/pay/test_handler.py", out)
        self.assertIn("src/modules/billing/slices/pay/handler.py:1: def pay(): ...", out)
        self.assertTrue(out.rstrip().endswith("== notes ==\nnone"))

    def test_new_slice_is_a_note(self):
        files = {**HARNESS, "meta/product/stack.md": STACK_SET,
                 "src/_about.md": "x\n", "src/modules/billing/_about.md": "x\n"}
        code, out, _ = self.run_packet(files, "billing", "refund")
        self.assertIn("new slice: src/modules/billing/slices/refund does not exist", out)

    def test_aligned_table_and_stems(self):
        stack = "|  source root     |  `app/src`  |\n| entry file stems | Index, Handler |\n"
        files = {**HARNESS, "meta/product/stack.md": stack,
                 "app/src/_about.md": "x\n", "app/src/modules/billing/_about.md": "x\n",
                 "app/src/modules/billing/Index.java": "class Index {}\n"}
        code, out, err = self.run_packet(files, "billing")
        self.assertEqual(code, 0, err)
        self.assertIn("app/src/modules/billing/Index.java:1: class Index {}", out)

    def test_annotated_value_stops(self):
        stack = "| source root | src (Python src layout) |\n| entry file stems | index, handler |\n"
        code, _, err = self.run_packet({**HARNESS, "meta/product/stack.md": stack}, "billing")
        self.assertEqual(code, 1)
        self.assertIn("bare path", err)

    def test_missing_row_and_file(self):
        code, _, err = self.run_packet({**HARNESS, "meta/product/stack.md": "| x | y |\n"}, "billing")
        self.assertIn("stack row missing: 'source root'", err)
        code, _, err = self.run_packet(HARNESS, "billing")
        self.assertEqual(code, 1)
        self.assertIn("missing harness file: meta/product/stack.md", err)

    def test_missing_harness_file_stops(self):
        files = {"meta/product/stack.md": STACK_SET}
        code, _, err = self.run_packet(files, "billing")
        self.assertEqual(code, 1)
        self.assertIn("missing harness file", err)


if __name__ == "__main__":
    unittest.main()
