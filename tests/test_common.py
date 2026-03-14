"""Tests for tools.common."""
import unittest

from tools.common import Finding, format_finding, require_str


class TestRequireStr(unittest.TestCase):
    def test_accepts_non_empty_string(self):
        self.assertIsNone(require_str("code", "code"))

    def test_rejects_non_string(self):
        self.assertIn("must be a string", require_str(123, "code"))

    def test_rejects_empty_string(self):
        self.assertIn("empty", require_str("", "code"))

    def test_rejects_whitespace_only(self):
        self.assertIn("empty", require_str("  \n", "code"))


class TestFormatFinding(unittest.TestCase):
    def test_format_with_line(self):
        f: Finding = ("msg", 5)
        self.assertIn("line 5", format_finding(f, None))
        self.assertIn("msg", format_finding(f, None))

    def test_format_with_file_path(self):
        f: Finding = ("msg", 5)
        self.assertIn("path.py:5", format_finding(f, "path.py"))

    def test_format_no_line(self):
        f: Finding = ("msg", None)
        self.assertEqual(format_finding(f, None), "  - msg")


if __name__ == "__main__":
    unittest.main()
