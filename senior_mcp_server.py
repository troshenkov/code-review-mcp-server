from mcp.server.fastmcp import FastMCP
import subprocess
import difflib
import tempfile
import os

mcp = FastMCP("senior-engineering-mcp")

@mcp.tool()
def review_architecture(problem: str, constraints: str = "") -> str:
    return f"""
Architecture Review

Problem:
{problem}

Constraints:
{constraints}

Recommended guidelines:
- minimal dependencies
- clear modules
- explicit error handling
- simple design
"""

@mcp.tool()
def review_code_quality(code: str) -> str:
    issues = []

    if "try:" not in code and "except" not in code and "set -e" not in code:
        issues.append("Missing error handling")

    if code.count("class ") > 5:
        issues.append("Possible over-abstraction")

    if "TODO" in code:
        issues.append("TODO left in code")

    if len(code.splitlines()) > 500:
        issues.append("File too large")

    return "\n".join(issues) if issues else "No major issues detected."

@mcp.tool()
def security_review(code: str) -> str:
    issues = []

    if "eval(" in code:
        issues.append("Use of eval() detected")

    if "os.system(" in code:
        issues.append("Use subprocess instead of os.system")

    if "chmod 777" in code:
        issues.append("Unsafe permissions")

    return "\n".join(issues) if issues else "No obvious security problems."

@mcp.tool()
def simplify_code(code: str) -> str:
    suggestions = []

    if code.count("class ") > 3:
        suggestions.append("Too many classes")

    if code.count("import ") > 10:
        suggestions.append("Too many dependencies")

    return "\n".join(suggestions) if suggestions else "Code structure looks simple."

@mcp.tool()
def generate_patch(old_code: str, new_code: str) -> str:
    diff = difflib.unified_diff(
        old_code.splitlines(),
        new_code.splitlines(),
        lineterm=""
    )
    return "\n".join(diff)

@mcp.tool()
def generate_tests(code: str) -> str:
    return """
Recommended tests:
1. Normal input
2. Invalid input
3. Boundary values
4. Failure cases
"""

@mcp.tool()
def shellcheck_script(script: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(script.encode())
        fname = f.name

    try:
        result = subprocess.run(
            ["shellcheck", fname],
            capture_output=True,
            text=True
        )
        return result.stdout or "ShellCheck found no issues."
    finally:
        os.remove(fname)

if __name__ == "__main__":
    mcp.run()
