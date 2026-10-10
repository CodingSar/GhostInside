#!/usr/bin/env python3
"""Tests for structure.py. Run: python3 -I meta/core/tools/test_structure.py

Each test builds a small source tree in a temp dir and runs the check on it.
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import structure  # noqa: E402

GOOD = {
    "_about.md": "| `billing` | invoices |",
    "app/main.py": "",
    "shared/db.py": "",
    "modules/billing/_about.md": "- `create-invoice`: create one invoice",
    "modules/billing/index.py": "",
    "modules/billing/store.py": "",
    "modules/billing/migrations/001_billing_invoice.sql": "",
    "modules/billing/slices/create-invoice/handler.py": "",
    "modules/billing/slices/create-invoice/test_handler.py": "",
}


class StructureTest(unittest.TestCase):
    def run_check(self, files, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "src"
            for rel, text in files.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            out = io.StringIO()
            with redirect_stdout(out):
                code = structure.main(["--root", str(root), "--ext", ".py",
                                       "--test", r"^test_.*\.py$", *extra])
            return code, out.getvalue().replace(str(root) + "/", "")

    def test_good_tree_passes(self):
        code, out = self.run_check(GOOD)
        self.assertEqual(code, 0, out)

    def test_missing_root(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = structure.main(["--root", "/nonexistent/src", "--ext", ".py", "--test", "x"])
        self.assertEqual(code, 1)
        self.assertIn("source root missing", out.getvalue())

    def test_catalogs_must_name_modules_and_slices(self):
        files = dict(GOOD)
        files["_about.md"] = "nothing"
        files["modules/billing/_about.md"] = "nothing"
        code, out = self.run_check(files)
        self.assertEqual(code, 1)
        self.assertIn("modules/billing: module not named", out)
        self.assertIn("create-invoice: slice not named", out)

    def test_entry_files_required(self):
        files = {k: v for k, v in GOOD.items()
                 if not k.endswith(("/index.py", "/handler.py"))}
        code, out = self.run_check(files)
        self.assertIn("modules/billing: no index entry file", out)
        self.assertIn("create-invoice: no handler entry file", out)

    def test_layout_folders(self):
        files = dict(GOOD)
        files["services/x.py"] = ""
        files["modules/billing/extra/x.py"] = ""
        files["modules/billing/slices/create-invoice/sub/x.py"] = ""
        code, out = self.run_check(files)
        self.assertIn("services: top-level folder must be one of", out)
        self.assertIn("modules/billing/extra: module folder must be one of", out)
        self.assertIn("create-invoice/sub: slices are flat", out)

    def test_forbidden_names(self):
        files = dict(GOOD)
        files["modules/billing/helpers.py"] = ""
        files["lib.py"] = ""  # root-level entry files are allowed
        code, out = self.run_check(files)
        self.assertIn("modules/billing/helpers.py: forbidden name", out)
        self.assertNotIn("lib.py", out)

    def test_size_caps(self):
        files = dict(GOOD)
        files["modules/billing/store.py"] = "x\n" * 201
        files["modules/billing/slices/create-invoice/test_handler.py"] = "x\n" * 250
        code, out = self.run_check(files)
        self.assertIn("modules/billing/store.py: 201 lines, cap 200", out)
        self.assertNotIn("test_handler.py", out)

    def test_slice_cap(self):
        files = dict(GOOD)
        names = []
        for i in range(3):
            name = f"s{i}"
            names.append(name)
            files[f"modules/billing/slices/{name}/handler.py"] = ""
        files["modules/billing/_about.md"] = " ".join(names + ["create-invoice"])
        code, out = self.run_check(files, "--max-slices", "3")
        self.assertIn("4 slices, cap 3", out)

    def test_ignored_dirs(self):
        files = dict(GOOD)
        files["modules/billing/__pycache__/helpers.py"] = "x\n" * 500
        code, out = self.run_check(files)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
