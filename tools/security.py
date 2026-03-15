"""
Security analysis tool for MCP server.
Detects security problems to senior-level standards.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import re
from fastmcp import FastMCP

from .common import require_str

# Compiled regexes (avoid recompiling on every call)
_RE_SUBPROCESS_SHELL_VAR = re.compile(r'subprocess\.\w+\([^)]*[\'"][^"\']*\$')
_RE_SQL_FORMAT = re.compile(r'(execute|executemany)\s*\(\s*f["\']')
_RE_SQL_SELECT_FORMAT = re.compile(r'%\s*\%|\.format\s*\([^)]*SELECT', re.I)
_RE_SECRET_ASSIGN = re.compile(r'(password|secret|api_key|apikey)\s*=\s*["\'][^"\']+["\']')
_RE_LONG_TOKEN = re.compile(r'["\'][A-Za-z0-9_-]{20,}["\']')


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
    if _RE_SUBPROCESS_SHELL_VAR.search(code):
        issues.append("Avoid embedding variables in shell strings; use list args and env.")

    # Unsafe permissions
    if "chmod 777" in code or "0o777" in code or "chmod(0o777" in code:
        issues.append("Avoid 777 permissions. Use least privilege (e.g. 0o600, 0o755).")

    # SQL injection
    if _RE_SQL_FORMAT.search(code) or _RE_SQL_SELECT_FORMAT.search(code):
        issues.append("Parameterize SQL (use ? or %s placeholders), do not format SQL with user input.")

    # Secrets in code
    if _RE_SECRET_ASSIGN.search(code_lower):
        issues.append("Do not hardcode secrets. Use environment variables or a secrets manager.")
    if "Bearer " in code and "os.environ" not in code and "getenv" not in code_lower:
        if _RE_LONG_TOKEN.search(code):
            issues.append("Tokens/keys may be hardcoded. Use env or config.")

    # Insecure randomness
    if "random.random()" in code or "random.randint(" in code:
        if "crypt" not in code_lower and "secret" not in code_lower:
            pass  # OK for non-crypto
    if "random.random()" in code and ("password" in code_lower or "token" in code_lower):
        issues.append("Use secrets module for cryptographic randomness, not random.")

    # Unsafe YAML load (arbitrary code execution)
    if "yaml.load(" in code and "yaml.safe_load" not in code and "Loader=" not in code:
        issues.append("yaml.load() is unsafe. Use yaml.safe_load() or pass Loader=.")

    # tempfile.mktemp() is racy; prefer NamedTemporaryFile or mkstemp
    if "tempfile.mktemp(" in code or "mktemp()" in code:
        issues.append("tempfile.mktemp() is racy. Use tempfile.NamedTemporaryFile or mkstemp.")

    # SSL verification disabled
    if "verify=false" in code_lower or "verify=False" in code or "verify: false" in code_lower:
        issues.append("Disabling SSL verification (verify=False) is insecure. Fix certs or use strict verification.")

    return issues


def security_review(code: str, file_path: str | None = None) -> str:
    """
    Detects security issues: eval/exec, shell injection, unsafe permissions,
    SQL injection, hardcoded secrets, insecure randomness.
    """
    err = require_str(code, "code")
    if err:
        return err
    issues = _security_checks(code)
    lines = ["## Security review"]
    if file_path:
        lines.append(f"File: {file_path}")
        lines.append("")
    if issues:
        lines.extend("  - " + i for i in issues)
    else:
        lines.append("No obvious security problems.")
    return "\n".join(lines)


def register(mcp: FastMCP):
    mcp.tool()(security_review)
