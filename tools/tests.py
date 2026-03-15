"""
Test generation tool for MCP server.
Suggests test scenarios and edge cases from code structure.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import ast
from fastmcp import FastMCP


def _python_test_suggestions(code: str) -> str:
    suggestions = [
        "Recommended tests:",
        "  1. Normal input (happy path).",
        "  2. Invalid input (wrong type, empty, None).",
        "  3. Boundary values (empty list, zero, max length).",
        "  4. Failure cases (exceptions, errors).",
        "",
    ]
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "\n".join(suggestions)

    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    for node in funcs[:8]:
        if node.name.startswith("_"):
            continue
        args = [a.arg for a in node.args.args if a.arg != "self"]
        if args:
            suggestions.append(f"  - '{node.name}': test with valid args; with None/empty for {args[0]}; and invalid types.")
        else:
            suggestions.append(f"  - '{node.name}': test return value and side effects.")
    if funcs:
        suggestions.append("")
    suggestions.append("Use pytest or unittest; mock I/O and external calls.")

    return "\n".join(suggestions)


def register(mcp: FastMCP):
    @mcp.tool()
    def generate_tests(code: str, language: str = "python") -> str:
        """
        Suggests test scenarios for the given code: happy path, invalid input,
        boundaries, failure cases. For Python, infers functions and suggests per-function tests.
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        if not code.strip():
            return "Input error: code is empty."

        lang = (language or "python").strip().lower()
        if lang == "python":
            return _python_test_suggestions(code)
        return """
Recommended tests:
1. Normal input
2. Invalid input
3. Boundary values
4. Failure cases
"""
