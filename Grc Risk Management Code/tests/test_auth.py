"""
Unit Tests for Authentication, Password Hashing, Sessions & RBAC.
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import (
    hash_password, verify_password, create_session, validate_session,
    revoke_session, clean_expired_sessions, _ACTIVE_SESSIONS
)


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        _ACTIVE_SESSIONS.clear()

    def test_password_hashing_and_verification(self):
        """Tests password hashing generates salted hashes and verifies accurately."""
        password = "SecurePassword!123"
        hashed = hash_password(password)

        self.assertIn("$", hashed)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_session_lifecycle(self):
        """Tests creation, validation, and revocation of session tokens."""
        user = {
            "id": 1,
            "username": "admin",
            "role": "admin",
            "full_name": "System Administrator"
        }

        token = create_session(user)
        self.assertIsNotNone(token)
        self.assertTrue(len(token) > 20)

        # Validate
        session = validate_session(token)
        self.assertIsNotNone(session)
        self.assertEqual(session["username"], "admin")
        self.assertEqual(session["role"], "admin")

        # Revoke
        revoked = revoke_session(token)
        self.assertTrue(revoked)

        # Re-validate (should be None)
        self.assertIsNone(validate_session(token))

    def test_invalid_and_expired_session(self):
        """Tests that invalid and expired tokens return None."""
        self.assertIsNone(validate_session("fake_token_12345"))
        self.assertIsNone(validate_session(None))

        # Manually create an expired session
        user = {"id": 2, "username": "analyst", "role": "analyst"}
        token = create_session(user)
        _ACTIVE_SESSIONS[token]["expires_at"] = time.time() - 10  # expired in past

        self.assertIsNone(validate_session(token))


if __name__ == "__main__":
    unittest.main()
