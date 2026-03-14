"""
Senior-level code review tool for MCP server.
Returns a checklist and concrete suggestions so code meets senior developer standards.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import ast
import re
from mcp.server.fastmcp import FastMCP


def _python_senior_checks(code: str) -> list[str]:
    """Run Python-specific checks; return list of findings."""
    findings = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["Invalid Python syntax; fix before review."]

    # Long functions (> ~40 lines)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            lines = (node.end_lineno or 0) - (node.lineno or 0) + 1
            if lines > 45:
                findings.append(f"Function '{node.name}' is long ({lines} lines). Split or extract helpers.")
            # Shallow complexity: count branches
            branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.ExceptHandler, ast.With, ast.For, ast.While)))
            if branches > 10:
                findings.append(f"Function '{node.name}' has high branching ({branches}). Simplify or extract.")

    # Magic numbers: count non-trivial numeric literals
    magic_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            v = node.value
            if v not in (0, 1, -1, 2) and not (isinstance(v, int) and 0 <= v <= 10):
                magic_count += 1
    if magic_count > 3:
        findings.append("Several magic numbers detected. Use named constants for readability.")

    # Missing docstrings on public functions/classes
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            doc = ast.get_docstring(node)
            if not doc:
                findings.append(f"Public '{node.name}' has no docstring. Add a one-line purpose and args/returns.")

    # Single-letter or very short names (heuristic)
    short_names = re.findall(r"\b([a-z])\b", code)
    if len(short_names) > 8:
        findings.append("Many single-letter names; prefer descriptive names for clarity.")

    return findings


def _generic_checks(code: str) -> list[str]:
    """Language-agnostic senior-level checks."""
    findings = []
    lines = code.splitlines()
    if len(lines) > 400:
        findings.append("File is very long. Split by responsibility (see suggest_code_split).")
    if "TODO" in code or "FIXME" in code or "XXX" in code:
        findings.append("Resolve TODO/FIXME/XXX before considering code done.")
    if "except:" in code or "except Exception:" in code:
        findings.append("Avoid bare 'except' or broad 'except Exception'; catch specific errors.")
    if "print(" in code and "def " in code:
        findings.append("Prefer logging over print() in production code.")
    # Duplicate block heuristic: same line repeated
    if lines:
        from collections import Counter
        counter = Counter(l.strip() for l in lines if len(l.strip()) > 20)
        for line, count in counter.most_common(3):
            if count >= 3:
                findings.append("Repeated code detected (DRY). Extract to a function or shared constant.")
                break
    return findings


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def senior_review(code: str, language: str = "python") -> str:
        """
        Review code against senior developer standards. Returns a checklist and concrete
        suggestions: naming, error handling, types, tests, security, DRY, documentation.
        Use this to make code production-ready and maintainable at a senior level.
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        if not code.strip():
            return "Input error: code is empty."

        lang = (language or "python").strip().lower()
        sections = ["Senior developer review\n"]

        # 1. Generic
        generic = _generic_checks(code)
        if generic:
            sections.append("Structure & discipline:")
            sections.extend("  - " + g for g in generic)
            sections.append("")
        else:
            sections.append("Structure & discipline: OK (file size, TODOs, error handling, DRY).")
            sections.append("")

        # 2. Language-specific
        if lang == "python":
            py_findings = _python_senior_checks(code)
            if py_findings:
                sections.append("Python-specific:")
                # Dedupe and limit
                seen = set()
                for f in py_findings[:12]:
                    if f not in seen:
                        seen.add(f)
                        sections.append("  - " + f)
                sections.append("")
            sections.append("Senior checklist:")
            sections.append("  [ ] Clear naming (no single-letter except loop indices)")
            sections.append("  [ ] Errors handled explicitly; no bare except")
            sections.append("  [ ] Types documented or type hints (public API)")
            sections.append("  [ ] No magic numbers; constants named")
            sections.append("  [ ] Functions small and single-purpose")
            sections.append("  [ ] Tests for main paths and edge cases")
            sections.append("  [ ] No secrets in code; use env/config")
            sections.append("  [ ] Logging instead of print for production")
        else:
            sections.append("Senior checklist (generic):")
            sections.append("  [ ] Clear naming and single responsibility")
            sections.append("  [ ] Explicit error handling")
            sections.append("  [ ] No duplicated logic (DRY)")
            sections.append("  [ ] Documented public API")
            sections.append("  [ ] Tests for critical behavior")

        return "\n".join(sections)
