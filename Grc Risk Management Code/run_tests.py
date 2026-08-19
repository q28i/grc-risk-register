"""
GRC Risk Register - Unified Automated Test Runner
Runs all unit, integration, and security/rebranding test suites.
"""

import unittest
import sys
import os

# Set current working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_all_tests():
    print("\n=======================================================")
    print("  GRC RISK REGISTER - Automated Test Suite")
    print("=======================================================\n")

    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n-------------------------------------------------------")
    print(f"  Tests Run:    {result.testsRun}")
    print(f"  Failures:     {len(result.failures)}")
    print(f"  Errors:       {len(result.errors)}")
    print(f"  Status:       {'ALL TESTS PASSED' if result.wasSuccessful() else 'TESTS FAILED'}")
    print("-------------------------------------------------------\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
