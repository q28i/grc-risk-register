"""
Unit and Integration Tests for Application Updater
"""

import unittest
import os
import sys
import shutil
import tempfile
import zipfile
import json
import importlib.util

# Dynamically import updater from DELETE BEFORE PRESENTATION/updater/updater.py
def _load_updater_module():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, "..", "..", "DELETE BEFORE PRESENTATION", "updater", "updater.py"),
        os.path.join(curr_dir, "..", "DELETE BEFORE PRESENTATION", "updater", "updater.py"),
        os.path.join(curr_dir, "updater", "updater.py")
    ]
    for c in candidates:
        if os.path.exists(c):
            spec = importlib.util.spec_from_file_location("updater", os.path.abspath(c))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("Could not locate updater.py in DELETE BEFORE PRESENTATION/updater/")

updater_mod = _load_updater_module()
parse_version = updater_mod.parse_version
is_newer_version = updater_mod.is_newer_version
get_current_version = updater_mod.get_current_version
apply_update = updater_mod.apply_update
check_for_updates = updater_mod.check_for_updates

class TestUpdater(unittest.TestCase):
    def test_version_parsing(self):
        self.assertEqual(parse_version("1.0.0"), (1, 0, 0))
        self.assertEqual(parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(parse_version("2.1"), (2, 1, 0))
        self.assertEqual(parse_version("v0.9.5-beta"), (0, 9, 5))

    def test_version_comparison(self):
        self.assertTrue(is_newer_version("1.1.0", "1.0.0"))
        self.assertTrue(is_newer_version("2.0.0", "1.9.9"))
        self.assertTrue(is_newer_version("1.0.1", "1.0.0"))
        self.assertFalse(is_newer_version("1.0.0", "1.0.0"))
        self.assertFalse(is_newer_version("0.9.0", "1.0.0"))

    def test_get_current_version(self):
        temp_dir = tempfile.mkdtemp()
        try:
            v_path = os.path.join(temp_dir, "VERSION")
            with open(v_path, "w", encoding="utf-8") as f:
                f.write("1.2.3\n")
            self.assertEqual(get_current_version(temp_dir), "1.2.3")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_safe_update_preserves_database(self):
        temp_app = tempfile.mkdtemp(prefix="test_app_")
        try:
            # Setup initial app state
            with open(os.path.join(temp_app, "VERSION"), "w") as f:
                f.write("1.0.0")
            with open(os.path.join(temp_app, "app.py"), "w") as f:
                f.write("# old app.py")
            db_path = os.path.join(temp_app, "grc_risk_register.db")
            with open(db_path, "w") as f:
                f.write("CRITICAL USER DATABASE CONTENT")

            # Create test update zip
            zip_dir = tempfile.mkdtemp()
            zip_path = os.path.join(zip_dir, "update.zip")
            with zipfile.ZipFile(zip_path, "w") as z:
                z.writestr("VERSION", "1.1.0")
                z.writestr("app.py", "# new updated app.py")
                z.writestr("new_feature.py", "# new feature")
                z.writestr("grc_risk_register.db", "EMPTY DB IN ZIP")

            # Apply update
            success, msg = apply_update(zip_path, temp_app)
            self.assertTrue(success)

            # Verify files
            with open(os.path.join(temp_app, "VERSION"), "r") as f:
                self.assertEqual(f.read().strip(), "1.1.0")
            with open(os.path.join(temp_app, "app.py"), "r") as f:
                self.assertEqual(f.read().strip(), "# new updated app.py")
            self.assertTrue(os.path.exists(os.path.join(temp_app, "new_feature.py")))

            # Verify user database is 100% PRESERVED
            with open(db_path, "r") as f:
                self.assertEqual(f.read(), "CRITICAL USER DATABASE CONTENT")

            shutil.rmtree(zip_dir, ignore_errors=True)
        finally:
            shutil.rmtree(temp_app, ignore_errors=True)

    def test_rollback_on_corrupt_update(self):
        temp_app = tempfile.mkdtemp(prefix="test_app_rollback_")
        try:
            with open(os.path.join(temp_app, "VERSION"), "w") as f:
                f.write("1.0.0")
            with open(os.path.join(temp_app, "app.py"), "w") as f:
                f.write("# original app.py")

            # Create a non-zip file
            corrupt_zip = os.path.join(temp_app, "corrupt.zip")
            with open(corrupt_zip, "w") as f:
                f.write("THIS IS NOT A VALID ZIP")

            success, msg = apply_update(corrupt_zip, temp_app)
            self.assertFalse(success)

            # Verify original files remain intact
            with open(os.path.join(temp_app, "app.py"), "r") as f:
                self.assertEqual(f.read(), "# original app.py")
        finally:
            shutil.rmtree(temp_app, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
