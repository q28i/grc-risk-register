"""
Automated Rebranding, Link Integrity & Scope Isolation Scanner.
Verifies that no upstream legacy names, vendor marketing, or unapproved staging terms appear in the working app.
"""

import unittest
import os
import re

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Unapproved terms that must NEVER appear in user-facing code/templates of the working app
FORBIDDEN_USER_FACING_TERMS = [
    r"grc4ciso",
    r"grcbit_",
    r"Semester 2",
    r"Semester 3",
    r"Semester 4",
    r"Roadmap Stage",
    r"Coming later",
    r"Future feature",
    r"Future development",
    r"Hidden functionality",
    r"OWASP/www-project-it-grc"
]

ALLOWED_EXTENSIONS = ('.html', '.js', '.css', '.py')


class TestRebrandingAndIsolation(unittest.TestCase):

    def test_no_forbidden_terms_in_application(self):
        """Scans all application files to ensure zero forbidden staging or upstream vendor terms."""
        violations = []

        for root, _, files in os.walk(APP_DIR):
            if "tests" in root:
                continue  # Skip test folder itself since it contains search strings

            for file in files:
                if file.endswith(ALLOWED_EXTENSIONS):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for term in FORBIDDEN_USER_FACING_TERMS:
                        matches = re.findall(term, content, re.IGNORECASE)
                        if matches:
                            violations.append(f"File '{file}' contains forbidden term: '{matches[0]}'")

        if violations:
            self.fail("Rebranding / Isolation violations found:\n" + "\n".join(violations))

    def test_project_identity_consistency(self):
        """Verifies that the index.html page title, brand header, and headings use 'GRC Risk Register'."""
        index_path = os.path.join(APP_DIR, "templates", "index.html")
        self.assertTrue(os.path.exists(index_path))

        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("<title>GRC Risk Register", content)
        self.assertIn('<h1 class="brand-title">GRC Risk Register</h1>', content)


if __name__ == "__main__":
    unittest.main()
