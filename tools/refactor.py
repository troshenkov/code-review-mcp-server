"""
Automatic code refactoring tool for MCP server.
Suggests refactoring improvements using structure analysis (e.g. AST for Python).
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import ast
import re
from mcp.server.fastmcp import FastMCP


def _python_refactor_suggestions(code: str) -> list[str]:
    suggestions = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["Fix syntax errors before refactoring."]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            lines = (node.end_lineno or 0) - (node.lineno or 0) + 1
            if lines > 35:
                suggestions.append(f"Split long function '{node.name}' ({lines} lines) into smaller functions.")
            # Branch count as complexity proxy
            branches = sum(
                1 for n in ast.walk(node)
                if isinstance(n, (ast.If, ast.ExceptHandler, ast.With, ast.For, ast.While))
            )
            if branches > 8:
                suggestions.append(f"Reduce complexity in '{node.name}' (e.g. extract helpers, early returns).")

    # Unused imports (simple heuristic: import X and X not in code except in import)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                if "." in name:
                    name = name.split(".")[0]
                imports.add(name)
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imports.add(name)
    for imp in imports:
        # Exclude common side-effect imports
        if imp in ("re", "os", "sys", "json", "logging", "ast"):
            continue
        if imp not in ("*",) and code.count(imp) <= 1:
            suggestions.append(f"Possible unused import or single use: '{imp}'. Remove or reuse.")

    # Single-letter names in function args (except i,j,k in loops)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for a in node.args.args:
                if a.arg and len(a.arg) == 1 and a.arg not in "ijk":
                    suggestions.append(f"Rename short argument '{a.arg}' in '{node.name}' for clarity.")

    if not suggestions:
        suggestions.append("Rename variables for clarity where unclear.")
        suggestions.append("Split large functions; reduce cyclomatic complexity.")
        suggestions.append("Remove dead code and unused imports.")

    return suggestions[:10]


def register(mcp: FastMCP):
    @mcp.tool()
    def refactor_code(code: str, language: str = "python") -> str:
        """
        Suggests refactoring improvements: split long functions, reduce complexity,
        remove dead/unused code, rename for clarity. Uses structure (e.g. AST for Python).
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        if not code.strip():
            return "Input error: code is empty."

        lang = (language or "python").strip().lower()
        if lang == "python":
            suggestions = _python_refactor_suggestions(code)
        else:
            suggestions = [
                "Split large functions into smaller, single-purpose ones.",
                "Reduce nesting; use early returns or extract helpers.",
                "Rename variables for clarity; remove dead code.",
            ]
        return "Refactoring suggestions:\n" + "\n".join("  - " + s for s in suggestions)
