"""
Tests for utils: file_helpers (with_temp_file, generate_diff).
Run from project root: python -m pytest tests/ -v
"""
import unittest

from utils.file_helpers import with_temp_file, generate_diff


class TestGenerateDiff(unittest.TestCase):
    def test_generate_diff_basic(self):
        old = "a\nb\nc"
        new = "a\nb\nc\nd"
        result = generate_diff(old, new)
        self.assertIn("+d", result)

    def test_generate_diff_empty(self):
        result = generate_diff("", "")
        self.assertIsInstance(result, str)


class TestWithTempFile(unittest.TestCase):
    def test_with_temp_file_callback_receives_path(self):
        def callback(path):
            self.assertGreater(len(path), 0)
            with open(path, encoding="utf-8") as f:
                return f.read()

        result = with_temp_file("hello", callback)
        self.assertEqual(result, "hello")

    def test_with_temp_file_returns_callback_result(self):
        result = with_temp_file("x", lambda p: "ok")
        self.assertEqual(result, "ok")


if __name__ == "__main__":
    unittest.main()
