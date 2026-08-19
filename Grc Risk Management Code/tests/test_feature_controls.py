"""
Unit & Integration Tests for Demo Account, Granular Feature Controls & RBAC Mutation Guards.
"""

import unittest
import sys
import os
import tempfile
import json
import threading
import time
import urllib.request
import urllib.error
from http.server import HTTPServer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database
import app
from app import GRCRequestHandler
from auth import verify_password


class TestFeatureControls(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create temp db and bind to database module
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp(suffix=".db")
        database.DB_PATH = cls.temp_db_path
        database.init_db(cls.temp_db_path)

        # Launch background test server on ephemeral port
        cls.port = 8799
        cls.server = HTTPServer(("127.0.0.1", cls.port), GRCRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.2)  # Allow server to bind

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        os.close(cls.temp_db_fd)
        if os.path.exists(cls.temp_db_path):
            os.remove(cls.temp_db_path)

    def make_request(self, method: str, path: str, body: dict = None, token: str = None):
        """Helper to send HTTP requests to test server."""
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(body).encode('utf-8') if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")

        try:
            with urllib.request.urlopen(req) as resp:
                resp_data = resp.read().decode('utf-8')
                try:
                    return resp.status, json.loads(resp_data) if resp_data else {}
                except json.JSONDecodeError:
                    return resp.status, resp_data
        except urllib.error.HTTPError as e:
            err_data = e.read().decode('utf-8')
            try:
                return e.code, json.loads(err_data) if err_data else {}
            except json.JSONDecodeError:
                return e.code, err_data

    def get_login_token(self, username: str, password: str) -> str:
        status, data = self.make_request("POST", "/api/auth/login", {
            "username": username,
            "password": password
        })
        self.assertEqual(status, 200)
        return data["token"]

    def test_01_feature_controls_schema_and_defaults(self):
        """Verify all 29 granular feature controls seeded with expected initial values."""
        controls = database.get_feature_controls()
        self.assertEqual(len(controls), 29)
        
        categories = {c["category"] for c in controls}
        expected_categories = {"Dashboard", "Assets", "Risks", "Reports", "Profile / Audit", "Administration"}
        self.assertEqual(categories, expected_categories)

        controls_dict = database.get_feature_controls_dict()
        # View and standard exploration features enabled for demo
        self.assertTrue(controls_dict.get("dashboard_view"))
        self.assertTrue(controls_dict.get("dashboard_refresh"))
        self.assertTrue(controls_dict.get("asset_view"))
        self.assertTrue(controls_dict.get("asset_search"))
        self.assertTrue(controls_dict.get("risk_view"))
        self.assertTrue(controls_dict.get("risk_search"))
        self.assertTrue(controls_dict.get("report_view"))
        self.assertTrue(controls_dict.get("report_print"))
        
        # Mutation and admin features disabled by default for demo
        self.assertFalse(controls_dict.get("asset_edit"))
        self.assertFalse(controls_dict.get("asset_archive"))
        self.assertFalse(controls_dict.get("risk_edit"))
        self.assertFalse(controls_dict.get("risk_archive"))
        self.assertFalse(controls_dict.get("report_export_csv"))
        self.assertFalse(controls_dict.get("admin_fc_view"))
        self.assertFalse(controls_dict.get("admin_fc_modify"))
        self.assertFalse(controls_dict.get("admin_users_view"))

    def test_02_demo_user_seed(self):
        """Verify demo account exists and has demo role."""
        demo_user = database.get_user_by_username("demo")
        self.assertIsNotNone(demo_user)
        self.assertEqual(demo_user["role"], "demo")
        self.assertEqual(demo_user["full_name"], "Demo User")
        self.assertTrue(verify_password("demo123", demo_user["password_hash"]))

    def test_03_is_feature_enabled_lookup(self):
        """Verify is_feature_enabled_for_demo helper returns correct states."""
        self.assertTrue(database.is_feature_enabled_for_demo("asset_view"))
        self.assertFalse(database.is_feature_enabled_for_demo("asset_edit"))
        self.assertFalse(database.is_feature_enabled_for_demo("non_existent_key"))

    def test_04_api_get_feature_controls(self):
        """Verify GET /api/feature-controls is accessible and returns controls."""
        status, data = self.make_request("GET", "/api/feature-controls")
        self.assertEqual(status, 200)
        self.assertIn("controls", data)
        self.assertIn("controls_dict", data)
        self.assertEqual(len(data["controls"]), 29)
        self.assertIn("asset_edit", data["controls_dict"])

    def test_05_admin_can_update_feature_controls(self):
        """Verify Admin can update feature controls via PUT /api/feature-controls."""
        admin_token = self.get_login_token("admin", "admin123")
        
        # Update asset_edit to true
        status, data = self.make_request("PUT", "/api/feature-controls", {
            "controls": {"asset_edit": True, "risk_archive": True}
        }, token=admin_token)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["controls_dict"]["asset_edit"])
        self.assertTrue(data["controls_dict"]["risk_archive"])

        # Reset back for subsequent tests
        database.update_feature_controls({"asset_edit": False, "risk_archive": False})

    def test_06_demo_user_cannot_update_feature_controls(self):
        """Verify Demo User receives 403 when attempting to modify feature controls."""
        demo_token = self.get_login_token("demo", "demo123")
        status, data = self.make_request("PUT", "/api/feature-controls", {
            "controls": {"asset_edit": True}
        }, token=demo_token)
        self.assertEqual(status, 403)

    def test_07_demo_mutation_rejection(self):
        """Verify backend rejects mutation endpoints (403) when disabled for demo user."""
        admin_token = self.get_login_token("admin", "admin123")
        demo_token = self.get_login_token("demo", "demo123")

        # Create asset as admin first
        status, created_asset = self.make_request("POST", "/api/assets", {
            "name": "SecOps Test Asset",
            "type": "System",
            "importance": "High",
            "owner": "SecOps Lead",
            "description": "Test System"
        }, token=admin_token)
        self.assertEqual(status, 201)
        asset_id = created_asset["id"]

        # Ensure asset_edit and asset_archive are disabled in DB
        database.update_feature_controls({"asset_edit": False, "asset_archive": False})

        # Demo user tries to update asset -> 403 Forbidden
        status, data = self.make_request("PUT", f"/api/assets/{asset_id}", {
            "name": "Modified Name"
        }, token=demo_token)
        self.assertEqual(status, 403)

        # Demo user tries to archive asset -> 403 Forbidden
        status, data = self.make_request("POST", f"/api/assets/{asset_id}/archive", {}, token=demo_token)
        self.assertEqual(status, 403)

        # Admin user can edit asset successfully -> 200
        status, data = self.make_request("PUT", f"/api/assets/{asset_id}", {
            "name": "Admin Modified Name"
        }, token=admin_token)
        self.assertEqual(status, 200)

    def test_08_login_page_cleanliness(self):
        """Verify that GET / serves login HTML with zero credential leaks or quick-login buttons."""
        status, html = self.make_request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIsInstance(html, str)
        self.assertIn("GRC Risk Register", html)
        self.assertIn("Cybersecurity Risk Management System", html)
        self.assertNotIn("quick-login", html.lower())
        self.assertNotIn("admin123", html)
        self.assertNotIn("demo123", html)
        self.assertNotIn("analyst123", html)
        self.assertNotIn("quick sign in", html.lower())

    def test_09_feature_controls_survive_reopen_and_reinit(self):
        """Verify that custom Feature Controls strictly survive application restarts and init_db re-runs."""
        # 1. Apply deliberate custom restrictions
        custom_toggles = {
            "asset_edit": False,
            "asset_archive": False,
            "risk_edit": False,
            "risk_archive": False,
            "report_export_csv": False
        }
        database.update_feature_controls(custom_toggles, db_path=self.temp_db_path)

        # 2. Verify saved in database
        saved_before = database.get_feature_controls_dict(self.temp_db_path)
        for key, expected_val in custom_toggles.items():
            self.assertEqual(saved_before.get(key), expected_val, f"Failed initial assert for {key}")

        # 3. Simulate application restart / re-initialization on existing database
        database.init_db(self.temp_db_path)

        # 4. Read back feature controls from SQLite
        saved_after = database.get_feature_controls_dict(self.temp_db_path)

        # 5. Assert all custom settings are 100% preserved
        for key, expected_val in custom_toggles.items():
            self.assertEqual(
                saved_after.get(key),
                expected_val,
                f"Feature control '{key}' was reset by database re-initialization!"
            )


if __name__ == "__main__":
    unittest.main()
