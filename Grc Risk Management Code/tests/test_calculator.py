"""
Unit Tests for Qualitative Risk Calculation Engine
Tests deterministic 3x3 Likelihood x Impact Qualitative Risk Matrix.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from risk_calculator import calculate_risk, get_matrix_definition


class TestRiskCalculator(unittest.TestCase):

    def test_all_nine_cartesian_coordinates(self):
        """Tests all 9 combinations of Likelihood (1-3) and Impact (1-3)."""
        expected_results = {
            (1, 1): (1, "Low"),
            (1, 2): (2, "Low"),
            (1, 3): (3, "Medium"),
            (2, 1): (2, "Low"),
            (2, 2): (4, "Medium"),
            (2, 3): (6, "High"),
            (3, 1): (3, "Medium"),
            (3, 2): (6, "High"),
            (3, 3): (9, "High"),
        }

        for (l, i), (expected_score, expected_level) in expected_results.items():
            with self.subTest(likelihood=l, impact=i):
                res = calculate_risk(l, i)
                self.assertEqual(res["likelihood"], l)
                self.assertEqual(res["impact"], i)
                self.assertEqual(res["score"], expected_score)
                self.assertEqual(res["level"], expected_level)
                self.assertTrue(res["color"].startswith("#"))
                self.assertIn("guidance", res)

    def test_invalid_likelihood_out_of_bounds(self):
        """Tests that likelihood outside 1-3 is rejected."""
        with self.assertRaises(ValueError):
            calculate_risk(0, 2)
        with self.assertRaises(ValueError):
            calculate_risk(4, 2)
        with self.assertRaises(ValueError):
            calculate_risk(-1, 2)

    def test_invalid_impact_out_of_bounds(self):
        """Tests that impact outside 1-3 is rejected."""
        with self.assertRaises(ValueError):
            calculate_risk(2, 0)
        with self.assertRaises(ValueError):
            calculate_risk(2, 5)
        with self.assertRaises(ValueError):
            calculate_risk(2, -3)

    def test_string_numeric_conversion(self):
        """Tests that string representations of numbers are parsed correctly."""
        res = calculate_risk("3", "2")
        self.assertEqual(res["score"], 6)
        self.assertEqual(res["level"], "High")

    def test_non_numeric_type_rejection(self):
        """Tests that invalid types raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_risk("high", "severe")
        with self.assertRaises(ValueError):
            calculate_risk(None, 2)

    def test_matrix_definition_structure(self):
        """Tests that the matrix definition structure returns 3 rows of 3 columns."""
        definition = get_matrix_definition()
        self.assertIn("matrix", definition)
        self.assertEqual(len(definition["matrix"]), 3)
        for row in definition["matrix"]:
            self.assertEqual(len(row), 3)


if __name__ == "__main__":
    unittest.main()
