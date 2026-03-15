"""
Tests for MCP tools: simplify, patch, code_quality, security, refactor.
Run from project root: python -m pytest tests/ -v
"""
import unittest
from typing import Any, cast

from tools.simplify import simplify_code
from tools.patch import generate_patch
from tools.code_quality import review_code_quality
from tools.security import security_review
from tools.refactor import refactor_code
from tools.ruff_tool import ruff_check


class TestSimplify(unittest.TestCase):
    def test_simplify_code_valid(self):
        code = "class A:\nclass B:\nclass C:\nclass D:\n" + "\n".join(f"import x{i}" for i in range(12))
        result = simplify_code(code)
        self.assertIn("Too many classes", result)
        self.assertIn("Too many dependencies", result)

    def test_simplify_code_invalid(self):
        result = simplify_code(cast(Any, 123))
        self.assertIn("Input error", result)

    def test_simplify_code_simple(self):
        result = simplify_code("def f(): pass")
        self.assertIn("Code structure looks simple", result)


class TestPatch(unittest.TestCase):
    def test_generate_patch_valid(self):
        old = "print('hello')"
        new = "print('hello world')"
        diff = generate_patch(old, new)
        self.assertIn("-print('hello')", diff)
        self.assertIn("+print('hello world')", diff)

    def test_generate_patch_invalid(self):
        diff = generate_patch(cast(Any, 123), "abc")
        self.assertIn("Input error", diff)


class TestCodeQuality(unittest.TestCase):
    def test_review_code_quality_input_error(self):
        result = review_code_quality(cast(Any, 123))
        self.assertIn("Input error", result)

    def test_review_code_quality_empty(self):
        result = review_code_quality("")
        self.assertIn("Input error", result)

    def test_review_code_quality_todo(self):
        result = review_code_quality("x = 1  # TODO fix")
        self.assertIn("TODO", result)

    def test_review_code_quality_ok(self):
        # Code with type hint and no risky calls may still get "error handling" hint; check we get a report
        result = review_code_quality("def f() -> int:\n    return 1")
        self.assertIn("Code quality", result)
        self.assertTrue("No major issues" in result or "error handling" in result or "issues" in result.lower())


class TestSecurity(unittest.TestCase):
    def test_security_review_eval(self):
        result = security_review("x = eval(user_input)")
        self.assertIn("eval", result)

    def test_security_review_input_error(self):
        result = security_review(cast(Any, 123))
        self.assertIn("Input error", result)

    def test_security_review_ok(self):
        result = security_review("def f(): return 1")
        self.assertIn("No obvious security problems", result)


class TestRefactor(unittest.TestCase):
    def test_refactor_code_input_error(self):
        result = refactor_code(cast(Any, 123))
        self.assertIn("Input error", result)

    def test_refactor_code_returns_suggestions(self):
        result = refactor_code("def f(): pass")
        self.assertIn("Refactoring suggestions", result)


class TestRuff(unittest.TestCase):
    def test_ruff_check_input_error(self):
        result = ruff_check(cast(Any, 123))
        self.assertIn("Input error", result)

    def test_ruff_check_returns_string(self):
        result = ruff_check("x = 1")
        self.assertIsInstance(result, str)
        self.assertTrue("Ruff" in result or "ruff" in result.lower())


if __name__ == "__main__":
    unittest.main()
