"""
Code quality analysis tool for MCP server.
Checks for common code quality issues to senior-level standards.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import ast
import re
from mcp.server.fastmcp import FastMCP


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    """Return maximum nesting depth of control flow."""
    if isinstance(node, (ast.If, ast.ExceptHandler, ast.With, ast.For, ast.While)):
        depth += 1
    child_depths = [depth]
    for child in ast.iter_child_nodes(node):
        child_depths.append(_max_nesting(child, depth))
    return max(child_depths) if child_depths else depth


def _python_quality(code: str) -> list[str]:
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["Invalid Python syntax."]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            lines = (node.end_lineno or 0) - (node.lineno or 0) + 1
            if lines > 50:
                issues.append(f"Function '{node.name}' is very long ({lines} lines). Split or extract.")
            nesting = _max_nesting(node)
            if nesting > 4:
                issues.append(f"Function '{node.name}' has deep nesting ({nesting}). Flatten or extract.")
        if isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            if len(methods) > 15:
                issues.append(f"Class '{node.name}' has many methods ({len(methods)}). Consider splitting responsibility.")

    # Missing error handling
    if "try:" not in code and "except" not in code and "set -e" not in code:
        if "def " in code or "open(" in code or "requests." in code or "subprocess." in code:
            issues.append("Missing error handling (try/except or set -e for shell).")

    # Over-abstraction
    if code.count("class ") > 5:
        issues.append("Possible over-abstraction (many classes). Prefer composition.")

    # TODOs
    if "TODO" in code or "FIXME" in code:
        issues.append("TODO/FIXME left in code. Resolve before merge.")

    # File size
    if len(code.splitlines()) > 500:
        issues.append("File too large. Split by responsibility.")

    # Type hints: suggest for public functions
    if "def " in code and " -> " not in code and ":" in code:
        # Only suggest if there are several defs
        defs = re.findall(r"^\s*def\s+\w+", code, re.MULTILINE)
        if len(defs) >= 2:
            issues.append("Consider adding return type hints for public functions.")

    return issues


def register(mcp: FastMCP):
    @mcp.tool()
    def review_code_quality(code: str, language: str = "python") -> str:
        """
        Checks for code quality issues at a senior level:
        - Missing error handling
        - Over-abstraction, overly large files
        - Long functions, deep nesting
        - TODOs, missing type hints
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        if not code.strip():
            return "Input error: code is empty."

        lang = (language or "python").strip().lower()
        if lang == "python":
            issues = _python_quality(code)
        else:
            issues = []
            if "try:" not in code and "except" not in code and "set -e" not in code:
                issues.append("Consider explicit error handling.")
            if len(code.splitlines()) > 500:
                issues.append("File too large.")
            if "TODO" in code or "FIXME" in code:
                issues.append("TODO/FIXME left in code.")

        return "\n".join(issues) if issues else "No major issues detected."
