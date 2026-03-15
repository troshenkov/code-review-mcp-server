"""
Ruff integration tool for MCP server.
Runs Ruff linter on Python code for fast static analysis.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import os
import subprocess
import tempfile
from fastmcp import FastMCP

from .common import require_str

SUBPROCESS_TIMEOUT = 30


def run_ruff_check(code: str) -> str:
    """Run Ruff check on Python code. Returns findings or a success message."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".py", delete=False
    ) as f:
        f.write(code)
        fname = f.name
    try:
        try:
            result = subprocess.run(
                ["ruff", "check", fname],
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
            )
            report = result.stdout.strip()
            err = result.stderr.strip()
            if report:
                return report
            if result.returncode != 0 and err:
                return f"Ruff error:\n{err}"
            return "Ruff found no issues."
        except FileNotFoundError:
            return "Ruff not found. Install with: pip install ruff"
        except subprocess.TimeoutExpired:
            return f"Ruff timed out after {SUBPROCESS_TIMEOUT}s. Try a smaller snippet."
    finally:
        os.remove(fname)


def ruff_check(code: str) -> str:
    """Run Ruff on Python code. Returns lint findings or success message."""
    err = require_str(code, "code")
    if err:
        return err
    return run_ruff_check(code)


def register(mcp: FastMCP):
    mcp.tool()(ruff_check)
