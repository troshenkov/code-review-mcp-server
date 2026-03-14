"""
Senior-level code review tool for MCP server.
Returns a checklist and concrete suggestions so code meets senior developer standards.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import ast
import re
from mcp.server.fastmcp import FastMCP

from .common import Finding, format_finding, require_str


def _python_senior_checks(code: str) -> list[Finding]:
    """Run Python-specific checks; return list of (message, line)."""
    findings: list[Finding] = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [("Invalid Python syntax; fix before review.", None)]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            line = node.lineno or 0
            nlines = (node.end_lineno or 0) - line + 1
            if nlines > 45:
                findings.append((f"Function '{node.name}' is long ({nlines} lines). Split or extract helpers.", line))
            branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.ExceptHandler, ast.With, ast.For, ast.While)))
            if branches > 10:
                findings.append((f"Function '{node.name}' has high branching ({branches}). Simplify or extract.", line))

    magic_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            v = node.value
            if v not in (0, 1, -1, 2) and not (isinstance(v, int) and 0 <= v <= 10):
                magic_count += 1
    if magic_count > 3:
        findings.append(("Several magic numbers detected. Use named constants for readability.", None))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            doc = ast.get_docstring(node)
            if not doc:
                line = node.lineno or None
                findings.append((f"Public '{node.name}' has no docstring. Add a one-line purpose and args/returns.", line))

    short_names = re.findall(r"\b([a-z])\b", code)
    if len(short_names) > 8:
        findings.append(("Many single-letter names; prefer descriptive names for clarity.", None))

    # Mutable default argument (e.g. def f(x=[]):) — common bug
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    line = node.lineno or None
                    findings.append(("Mutable default argument (list/dict/set). Use None and assign inside the function.", line))
                    break

    # Too many arguments — hard to use and test
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            nargs = len(node.args.args) + len(node.args.kwonlyargs)
            if nargs > 7:
                line = node.lineno or None
                findings.append((f"Function '{node.name}' has many arguments ({nargs}). Consider a options object or dataclass.", line))

    # assert used for validation (assert can be disabled with -O; use explicit checks in production)
    if re.search(r"^\s*assert\s+", code, re.MULTILINE) and "def test_" not in code and "pytest" not in code.lower():
        findings.append(("assert used for validation; use explicit if/raise in production (assert is disabled with -O).", None))

    return findings


def _generic_checks(code: str) -> list[Finding]:
    """Language-agnostic senior-level checks."""
    findings: list[Finding] = []
    lines = code.splitlines()
    nlines = len(lines)
    if nlines >= 1000:
        findings.append(("File 1000+ lines — strong signal to split: by feature, tab/section, or layer (e.g. routes vs handlers). Use suggest_code_split.", None))
    elif nlines >= 700:
        findings.append(("File 700+ lines. Sweet spot is 200–400; split unless one coherent unit (e.g. single form).", None))
    elif nlines > 400:
        findings.append(("File over ~400 lines. Consider splitting; 200–400 per file is the sweet spot for one clear responsibility.", None))
    if "TODO" in code or "FIXME" in code or "XXX" in code:
        findings.append(("Resolve TODO/FIXME/XXX before considering code done.", None))
    if "except:" in code or "except Exception:" in code:
        findings.append(("Avoid bare 'except' or broad 'except Exception'; catch specific errors.", None))
    # except: pass or except Exception: pass (swallowed errors)
    if re.search(r"except\s*(?:Exception)?\s*:\s*pass\b", code):
        findings.append(("Empty except with pass swallows errors. Log or re-raise.", None))
    if "print(" in code and "def " in code:
        findings.append(("Prefer logging over print() in production code.", None))
    if lines:
        from collections import Counter
        counter = Counter(l.strip() for l in lines if len(l.strip()) > 20)
        for line_content, count in counter.most_common(3):
            if count >= 3:
                findings.append(("Repeated code detected (DRY). Extract to a function or shared constant.", None))
                break

    # Deprecated / legacy patterns
    if ".has_key(" in code:
        findings.append(("dict.has_key() was removed in Python 3. Use 'key in d'.", None))
    if "urllib2" in code and "urllib.request" not in code:
        findings.append(("urllib2 is Python 2. Use urllib.request (or requests) for Python 3.", None))

    return findings


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def senior_review(
        code: str,
        language: str = "python",
        file_path: str | None = None,
        focus: str | None = None,
    ) -> str:
        """
        Review code against senior developer standards. Returns a structured report:
        Summary, Findings (with file:line when file_path is provided), and Checklist.
        Use when: you want production-ready, maintainable code (naming, errors, types,
        tests, security, DRY, docs). Prefer passing file_path when available so
        findings cite location. focus can narrow the checklist: "security", "api", or
        omit for full review.
        """
        err = require_str(code, "code")
        if err:
            return err

        lang = (language or "python").strip().lower()
        focus_key = (focus or "").strip().lower() or "all"
        sections = ["## Senior developer review", ""]

        # 1. Generic
        generic = _generic_checks(code)
        if generic:
            sections.append("## Findings (structure & discipline)")
            for f in generic:
                sections.append(format_finding(f, file_path))
            sections.append("")
        else:
            sections.append("## Findings (structure & discipline)")
            sections.append("  OK — file size, TODOs, error handling, DRY.")
            sections.append("")

        # 2. Language-specific
        if lang == "python":
            py_findings = _python_senior_checks(code)
            if py_findings:
                sections.append("## Findings (Python-specific)")
                seen: set[str] = set()
                for f in py_findings[:12]:
                    if f[0] not in seen:
                        seen.add(f[0])
                        sections.append(format_finding(f, file_path))
                sections.append("")

        sections.append("## Checklist")
        if focus_key == "security":
            sections.append("  [ ] No eval/exec on user input; no shell injection")
            sections.append("  [ ] No secrets in code; use env/config")
            sections.append("  [ ] Parameterized SQL / safe deserialization")
        elif focus_key == "api":
            sections.append("  [ ] Clear naming and single responsibility")
            sections.append("  [ ] Types documented or type hints (public API)")
            sections.append("  [ ] Documented public API and edge cases")
        else:
            sections.append("  [ ] Clear naming (no single-letter except loop indices)")
            sections.append("  [ ] Errors handled explicitly; no bare except")
            sections.append("  [ ] Types documented or type hints (public API)")
            sections.append("  [ ] No magic numbers; constants named")
            sections.append("  [ ] Functions small and single-purpose")
            sections.append("  [ ] File size: ~200–400 lines sweet spot; 500–700 OK if coherent; 1000+ split by feature/tab/layer")
            sections.append("  [ ] Tests for main paths and edge cases")
            sections.append("  [ ] No secrets in code; use env/config")
            sections.append("  [ ] Logging instead of print for production")

        return "\n".join(sections)
