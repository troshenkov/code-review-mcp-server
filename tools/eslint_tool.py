"""
eslint_tool.py
ESLint analysis tool for MCP server
Author: Dmitry Troshenkov
Last Updated: March 2026
"""

import subprocess
import tempfile
from mcp.server.fastmcp import FastMCP


def run_eslint_script(js_code: str) -> str:
    """
    Run ESLint on JavaScript/TypeScript code and return analysis results.
    Requires ESLint to be installed globally or in project node_modules.
    """
    def run_temp_file(fname: str) -> str:
        try:
            result = subprocess.run(
                ["npx", "eslint", "--stdin", "--stdin-filename", fname],
                input=js_code,
                text=True,
                capture_output=True,
            )
            output = result.stdout.strip()
            errors = result.stderr.strip()
            if output:
                return output
            elif errors:
                return f"ESLint error:\n{errors}"
            else:
                return "No ESLint issues found."
        except FileNotFoundError:
            return "ESLint or npx not found. Install ESLint globally or in project."

    # Use a temporary file name for ESLint to detect file type
    with tempfile.NamedTemporaryFile(suffix=".js") as temp_file:
        return run_temp_file(temp_file.name)


def register(mcp: FastMCP):
    """
    Register ESLint tool with MCP server.
    """
    @mcp.tool()
    def eslint_script(js_code: str) -> str:
        """
        Run ESLint on JavaScript/TypeScript code and return analysis results.
        Requires ESLint to be installed globally or in project node_modules.
        """
        return run_eslint_script(js_code)