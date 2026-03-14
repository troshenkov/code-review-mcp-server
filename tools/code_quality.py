"""
Code quality analysis tool for MCP server.
Checks for common code quality issues to senior-level standards.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import ast
import re
from mcp.server.fastmcp import FastMCP

# (message, line_number or None)
Finding = tuple[str, int | None]


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    """Return maximum nesting depth of control flow."""
    if isinstance(node, (ast.If, ast.ExceptHandler, ast.With, ast.For, ast.While)):
        depth += 1
    child_depths = [depth]
    for child in ast.iter_child_nodes(node):
        child_depths.append(_max_nesting(child, depth))
    return max(child_depths) if child_depths else depth


def _python_quality(code: str) -> list[Finding]:
    issues: list[Finding] = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [("Invalid Python syntax.", None)]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            line = node.lineno or 0
            nlines = (node.end_lineno or 0) - line + 1
            if nlines > 50:
                issues.append((f"Function '{node.name}' is very long ({nlines} lines). Split or extract.", line))
            nesting = _max_nesting(node)
            if nesting > 4:
                issues.append((f"Function '{node.name}' has deep nesting ({nesting}). Flatten or extract.", line))
        if isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            if len(methods) > 15:
                line = node.lineno or None
                issues.append((f"Class '{node.name}' has many methods ({len(methods)}). Consider splitting responsibility.", line))

    if "try:" not in code and "except" not in code and "set -e" not in code:
        if "def " in code or "open(" in code or "requests." in code or "subprocess." in code:
            issues.append(("Missing error handling (try/except or set -e for shell).", None))

    if code.count("class ") > 5:
        issues.append(("Possible over-abstraction (many classes). Prefer composition.", None))

    if "TODO" in code or "FIXME" in code:
        issues.append(("TODO/FIXME left in code. Resolve before merge.", None))

    if len(code.splitlines()) > 500:
        issues.append(("File too large. Split by responsibility.", None))

    if "def " in code and " -> " not in code and ":" in code:
        defs = re.findall(r"^\s*def\s+\w+", code, re.MULTILINE)
        if len(defs) >= 2:
            issues.append(("Consider adding return type hints for public functions.", None))

    # Long lines hurt readability and review (report up to 3 with line numbers)
    long_line_numbers = [i for i, line in enumerate(code.splitlines(), start=1) if len(line) > 120]
    for i in long_line_numbers[:3]:
        issues.append(("Line exceeds 120 characters. Break or shorten for readability.", i))

    return issues


def _format_finding(finding: Finding, file_path: str | None) -> str:
    msg, line = finding
    if file_path and line is not None:
        return f"  - {file_path}:{line}: {msg}"
    if line is not None:
        return f"  - line {line}: {msg}"
    return f"  - {msg}"


def register(mcp: FastMCP):
    @mcp.tool()
    def review_code_quality(code: str, language: str = "python", file_path: str | None = None) -> str:
        """
        Checks for code quality issues at a senior level: missing error handling,
        over-abstraction, long functions, deep nesting, TODOs, missing type hints.
        Pass file_path when available so findings include file:line references.
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        if not code.strip():
            return "Input error: code is empty."

        lang = (language or "python").strip().lower()
        if lang == "python":
            issues = _python_quality(code)
        else:
            issues: list[Finding] = []
            if "try:" not in code and "except" not in code and "set -e" not in code:
                issues.append(("Consider explicit error handling.", None))
            if len(code.splitlines()) > 500:
                issues.append(("File too large.", None))
            if "TODO" in code or "FIXME" in code:
                issues.append(("TODO/FIXME left in code.", None))

        if not issues:
            return "## Code quality\n\nNo major issues detected."
        lines = ["## Code quality", ""]
        for f in issues:
            lines.append(_format_finding(f, file_path))
        return "\n".join(lines)
