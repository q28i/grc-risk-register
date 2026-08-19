"""
Integration Tests for REST API Endpoints & RBAC Security Guards.
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


class TestApiIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create temp db and bind to database module
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp(suffix=".db")
        database.DB_PATH = cls.temp_db_path
        database.init_db(cls.temp_db_path)

        # Launch background test server on ephemeral port
        cls.port = 8765
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
                return resp.status, json.loads(resp_data) if resp_data else {}
        except urllib.error.HTTPError as e:
            err_data = e.read().decode('utf-8')
            return e.code, json.loads(err_data) if err_data else {}

    def test_01_login_endpoints(self):
        """Tests login with admin and analyst accounts, and rejection of bad credentials."""
        # Valid admin login
        status, data = self.make_request("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "admin")
        self.__class__.admin_token = data["token"]

        # Valid analyst login
        status, data = self.make_request("POST", "/api/auth/login", {"username": "analyst", "password": "analyst123"})
        self.assertEqual(status, 200)
        self.assertEqual(data["user"]["role"], "analyst")
        self.__class__.analyst_token = data["token"]

        # Invalid login
        status, data = self.make_request("POST", "/api/auth/login", {"username": "admin", "password": "WrongPassword"})
        self.assertEqual(status, 401)
        self.assertTrue(data.get("error"))

    def test_02_unauthenticated_rejection(self):
        """Tests that protected endpoints reject requests without a token (401)."""
        status, data = self.make_request("GET", "/api/dashboard")
        self.assertEqual(status, 401)

        status, data = self.make_request("GET", "/api/assets")
        self.assertEqual(status, 401)

    def test_03_rbac_privilege_enforcement(self):
        """Tests that Risk Analyst cannot access Administrator-only endpoints (403)."""
        # Analyst trying to view user list
        status, data = self.make_request("GET", "/api/users", token=self.analyst_token)
        self.assertEqual(status, 403)

        # Analyst trying to view audit logs
        status, data = self.make_request("GET", "/api/audit-logs", token=self.analyst_token)
        self.assertEqual(status, 403)

        # Admin can access user list and audit logs
        status, data = self.make_request("GET", "/api/users", token=self.admin_token)
        self.assertEqual(status, 200)
        self.assertTrue(len(data) >= 2)

        status, data = self.make_request("GET", "/api/audit-logs", token=self.admin_token)
        self.assertEqual(status, 200)

    def test_04_asset_and_risk_crud_flow(self):
        """Tests end-to-end Asset and Risk CRUD via HTTP API."""
        # 1. Create Asset as Analyst
        status, asset = self.make_request("POST", "/api/assets", {
            "name": "Integration Test API Gateway",
            "type": "Service",
            "importance": "High",
            "owner": "Cloud Ops",
            "description": "API Gateway cluster"
        }, token=self.analyst_token)

        self.assertEqual(status, 201)
        self.assertEqual(asset["asset_id"], "AST-001")
        asset_id = asset["id"]

        # 2. Create Risk linked to Asset
        status, risk = self.make_request("POST", "/api/risks", {
            "title": "API Gateway Authentication Bypass",
            "consequence": "Unauthorized API consumption and data manipulation.",
            "asset_id": asset_id,
            "likelihood": 3,
            "impact": 3,  # Score: 9 -> High
            "owner": "AppSec Team",
            "status": "Open"
        }, token=self.analyst_token)

        self.assertEqual(status, 201)
        self.assertEqual(risk["score"], 9)
        self.assertEqual(risk["level"], "High")

        # 3. Fetch Dashboard and verify KPI counts
        status, dash = self.make_request("GET", "/api/dashboard", token=self.analyst_token)
        self.assertEqual(status, 200)
        self.assertEqual(dash["summary"]["total_assets"], 1)
        self.assertEqual(dash["summary"]["total_risks"], 1)
        self.assertEqual(dash["summary"]["high_risks"], 1)
        self.assertEqual(dash["summary"]["open_risks"], 1)


if __name__ == "__main__":
    unittest.main()
