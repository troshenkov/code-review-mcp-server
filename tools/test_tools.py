import unittest
from tools.simplify import simplify_code
from tools.patch import generate_patch

class TestSimplifyTool(unittest.TestCase):
    def test_simplify_code_valid(self):
        code = "class A:\nclass B:\nclass C:\nclass D:\nimport os\nimport sys\n"
        result = simplify_code(code)
        self.assertIn("Too many classes", result)
        self.assertIn("Too many dependencies", result)

    def test_simplify_code_invalid(self):
        result = simplify_code(123)
        self.assertIn("Input error", result)

class TestPatchTool(unittest.TestCase):
    def test_generate_patch_valid(self):
        old = "print('hello')"
        new = "print('hello world')"
        diff = generate_patch(old, new)
        self.assertIn("-print('hello')", diff)
        self.assertIn("+print('hello world')", diff)

    def test_generate_patch_invalid(self):
        diff = generate_patch(123, "abc")
        self.assertIn("Input error", diff)

if __name__ == "__main__":
    unittest.main()
