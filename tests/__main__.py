import unittest
import pytest
import sys
import os

def run_unittest_tests():
    # Import the test function directly
    from database import test_run_database
    print("\nRunning unittest tests from tests/database/all_tables.py ...")
    test_run_database()

def run_pytest_tests():
    print("\nRunning pytest tests from tests/Fixture/ ...")
    pytest_args = [os.path.join(os.path.dirname(__file__), 'Fixture')]
    # Run pytest and exit based on its result
    result = pytest.main(pytest_args)
    if result != 0:
        sys.exit(result)

if __name__ == '__main__':
    run_unittest_tests()
    run_pytest_tests()
