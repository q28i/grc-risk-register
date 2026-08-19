"""
Unit Tests for Asset Management, Validation & Safe Archiving.
"""

import unittest
import sys
import os
import tempfile
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
    init_db, create_asset, get_assets, get_asset_by_id, update_asset,
    archive_asset, unarchive_asset
)
from models import validate_asset_payload, ValidationError


class TestAssetManagement(unittest.TestCase):

    def setUp(self):
        # Create temporary database for isolated testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.temp_db_path)

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_asset_validation_valid(self):
        """Tests validation passes with correct fields."""
        data = {
            "name": "Customer Records Database",
            "type": "Data",
            "importance": "High",
            "owner": "Data Custodian",
            "description": "Stores user profiles and billing."
        }
        validated = validate_asset_payload(data)
        self.assertEqual(validated["name"], "Customer Records Database")
        self.assertEqual(validated["type"], "Data")
        self.assertEqual(validated["importance"], "High")

    def test_asset_validation_invalid_type(self):
        """Tests that invalid asset types are rejected."""
        data = {
            "name": "Bad Asset",
            "type": "QuantumServer",  # Invalid type
            "importance": "High",
            "owner": "Admin"
        }
        with self.assertRaises(ValidationError):
            validate_asset_payload(data)

    def test_asset_crud_and_id_generation(self):
        """Tests asset creation auto-generates AST-001, AST-002 and stores records."""
        a1 = create_asset({
            "name": "Asset One",
            "type": "System",
            "importance": "High",
            "owner": "SecOps",
            "description": "Desc 1"
        }, db_path=self.temp_db_path)

        self.assertEqual(a1["asset_id"], "AST-001")
        self.assertEqual(a1["name"], "Asset One")

        a2 = create_asset({
            "name": "Asset Two",
            "type": "Device",
            "importance": "Low",
            "owner": "IT Helpdesk",
            "description": "Desc 2"
        }, db_path=self.temp_db_path)

        self.assertEqual(a2["asset_id"], "AST-002")

        # Fetch
        fetched = get_asset_by_id(a1["id"], db_path=self.temp_db_path)
        self.assertEqual(fetched["name"], "Asset One")

        # Update
        updated = update_asset(a1["id"], {"name": "Updated Asset One", "importance": "Medium"}, db_path=self.temp_db_path)
        self.assertEqual(updated["name"], "Updated Asset One")
        self.assertEqual(updated["importance"], "Medium")

    def test_asset_soft_archiving_and_restore(self):
        """Tests soft archiving hides asset from active list, and unarchiving restores it."""
        asset = create_asset({
            "name": "Archive Test Asset",
            "type": "Service",
            "importance": "Medium",
            "owner": "Network Team"
        }, db_path=self.temp_db_path)

        # Active list should contain it
        active_assets = get_assets(active_only=True, db_path=self.temp_db_path)
        self.assertEqual(len(active_assets), 1)

        # Archive
        archived = archive_asset(asset["id"], db_path=self.temp_db_path)
        self.assertTrue(archived)

        # Active list should now be empty
        active_after = get_assets(active_only=True, db_path=self.temp_db_path)
        self.assertEqual(len(active_after), 0)

        # All list (including archived) should contain it
        all_assets = get_assets(active_only=False, db_path=self.temp_db_path)
        self.assertEqual(len(all_assets), 1)
        self.assertEqual(all_assets[0]["active"], 0)

        # Restore / Unarchive
        restored = unarchive_asset(asset["id"], db_path=self.temp_db_path)
        self.assertTrue(restored)

        # Active list should contain it again
        active_restored = get_assets(active_only=True, db_path=self.temp_db_path)
        self.assertEqual(len(active_restored), 1)


if __name__ == "__main__":
    unittest.main()
