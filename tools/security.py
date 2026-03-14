"""
Security analysis tool for MCP server.
Detects security problems to senior-level standards.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import re
from mcp.server.fastmcp import FastMCP


def _security_checks(code: str) -> list[str]:
    issues = []
    code_lower = code.lower()

    # Code execution / unsafe eval
    if "eval(" in code:
        issues.append("Use of eval() is unsafe. Prefer ast.literal_eval or explicit parsing.")
    if "exec(" in code:
        issues.append("exec() executes arbitrary code. Avoid or restrict to trusted input.")
    if "pickle.loads(" in code or "pickle.load(" in code:
        issues.append("pickle can execute arbitrary code. Prefer JSON or safe deserialization.")

    # Shell / command injection
    if "os.system(" in code:
        issues.append("Use subprocess with list args (no shell=True) instead of os.system().")
    if "subprocess." in code and "shell=true" in code_lower:
        issues.append("subprocess with shell=True is injection-prone. Use list arguments.")
    if re.search(r'subprocess\.\w+\([^)]*[\'"][^"\']*\$', code):
        issues.append("Avoid embedding variables in shell strings; use list args and env.")

    # Unsafe permissions
    if "chmod 777" in code or "0o777" in code or "chmod(0o777" in code:
        issues.append("Avoid 777 permissions. Use least privilege (e.g. 0o600, 0o755).")

    # SQL injection
    if re.search(r'(execute|executemany)\s*\(\s*f["\']', code) or re.search(r'%\s*\%|\.format\s*\([^)]*SELECT', code, re.I):
        issues.append("Parameterize SQL (use ? or %s placeholders), do not format SQL with user input.")

    # Secrets in code
    if re.search(r'(password|secret|api_key|apikey)\s*=\s*["\'][^"\']+["\']', code_lower):
        issues.append("Do not hardcode secrets. Use environment variables or a secrets manager.")
    if "Bearer " in code and "os.environ" not in code and "getenv" not in code_lower:
        if re.search(r'["\'][A-Za-z0-9_-]{20,}["\']', code):
            issues.append("Tokens/keys may be hardcoded. Use env or config.")

    # Insecure randomness
    if "random.random()" in code or "random.randint(" in code:
        if "crypt" not in code_lower and "secret" not in code_lower:
            pass  # OK for non-crypto
    if "random.random()" in code and ("password" in code_lower or "token" in code_lower):
        issues.append("Use secrets module for cryptographic randomness, not random.")

    return issues


def register(mcp: FastMCP):
    @mcp.tool()
    def security_review(code: str) -> str:
        """
        Detects security issues: eval/exec, shell injection, unsafe permissions,
        SQL injection, hardcoded secrets, insecure randomness.
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        issues = _security_checks(code)
        return "\n".join(issues) if issues else "No obvious security problems."
