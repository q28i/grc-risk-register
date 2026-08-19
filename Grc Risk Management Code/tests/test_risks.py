"""
Unit Tests for Risk Management, Linkage, Scoring, and Lifecycle States.
"""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
    init_db, create_asset, create_risk, get_risks, get_risk_by_id,
    update_risk, archive_risk, unarchive_risk
)
from models import validate_risk_payload, ValidationError


class TestRiskManagement(unittest.TestCase):

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.temp_db_path)
        # Create an asset to link risks against
        self.asset = create_asset({
            "name": "Production Database Server",
            "type": "Data",
            "importance": "High",
            "owner": "DBA Team"
        }, db_path=self.temp_db_path)

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_risk_creation_and_auto_scoring(self):
        """Tests that creating a risk computes deterministic score and level correctly."""
        risk_data = {
            "title": "Unauthenticated Data Access",
            "consequence": "Direct data leakage and exposure of confidential records.",
            "asset_id": self.asset["id"],
            "likelihood": 3,
            "impact": 2,
            "owner": "Security Engineer",
            "status": "Open",
            "notes": "Firewall rules pending."
        }
        validated = validate_risk_payload(risk_data)
        created = create_risk(validated, db_path=self.temp_db_path)

        self.assertEqual(created["risk_id"], "RSK-001")
        self.assertEqual(created["title"], "Unauthenticated Data Access")
        self.assertEqual(created["score"], 6)  # 3 * 2 = 6
        self.assertEqual(created["level"], "High")
        self.assertEqual(created["asset_id"], self.asset["id"])
        self.assertEqual(created["asset_name"], "Production Database Server")

    def test_risk_creation_fails_on_nonexistent_asset(self):
        """Tests that linking to a non-existent asset ID raises an error."""
        invalid_data = {
            "title": "Orphan Risk",
            "consequence": "No asset.",
            "asset_id": 9999,  # Does not exist
            "likelihood": 2,
            "impact": 2,
            "owner": "Tester"
        }
        with self.assertRaises(ValueError):
            create_risk(invalid_data, db_path=self.temp_db_path)

    def test_risk_update_recalculates_score(self):
        """Tests that updating likelihood or impact recalculates the score and level."""
        risk = create_risk({
            "title": "Initial Risk",
            "consequence": "Initial consequence",
            "asset_id": self.asset["id"],
            "likelihood": 1,
            "impact": 1,  # Score: 1 -> Low
            "owner": "Analyst"
        }, db_path=self.temp_db_path)

        self.assertEqual(risk["score"], 1)
        self.assertEqual(risk["level"], "Low")

        # Update likelihood to 3 and impact to 3 -> Score 9 (High)
        updated = update_risk(risk["id"], {
            "likelihood": 3,
            "impact": 3,
            "status": "In Progress"
        }, db_path=self.temp_db_path)

        self.assertEqual(updated["score"], 9)
        self.assertEqual(updated["level"], "High")
        self.assertEqual(updated["status"], "In Progress")

    def test_risk_status_lifecycle(self):
        """Tests progression through Open -> In Progress -> Treated -> Closed."""
        risk = create_risk({
            "title": "Lifecycle Test",
            "consequence": "Test consequence",
            "asset_id": self.asset["id"],
            "likelihood": 2,
            "impact": 2,
            "owner": "Analyst",
            "status": "Open"
        }, db_path=self.temp_db_path)

        for next_status in ["In Progress", "Treated", "Closed"]:
            updated = update_risk(risk["id"], {"status": next_status}, db_path=self.temp_db_path)
            self.assertEqual(updated["status"], next_status)

    def test_risk_soft_archiving_and_filtering(self):
        """Tests archiving a risk removes it from active queries while retaining it for audit."""
        r1 = create_risk({
            "title": "Risk 1",
            "consequence": "C1",
            "asset_id": self.asset["id"],
            "likelihood": 2,
            "impact": 2,
            "owner": "A1"
        }, db_path=self.temp_db_path)

        r2 = create_risk({
            "title": "Risk 2",
            "consequence": "C2",
            "asset_id": self.asset["id"],
            "likelihood": 1,
            "impact": 1,
            "owner": "A2"
        }, db_path=self.temp_db_path)

        self.assertEqual(len(get_risks(active_only=True, db_path=self.temp_db_path)), 2)

        # Archive r1
        archive_risk(r1["id"], db_path=self.temp_db_path)

        # Active list should have only 1
        active = get_risks(active_only=True, db_path=self.temp_db_path)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["id"], r2["id"])

        # Unarchive r1
        unarchive_risk(r1["id"], db_path=self.temp_db_path)
        self.assertEqual(len(get_risks(active_only=True, db_path=self.temp_db_path)), 2)


if __name__ == "__main__":
    unittest.main()
