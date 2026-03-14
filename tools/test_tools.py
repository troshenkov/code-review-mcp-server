"""
Legacy test entry point: runs the full test suite from tests/.
Run from project root: python -m unittest discover -s tests -p 'test_*.py' -v
Or: python -m unittest tools.test_tools (this module runs discover).
"""
import unittest
import sys


def run():
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run()
