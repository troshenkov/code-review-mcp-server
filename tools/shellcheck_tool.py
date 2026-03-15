"""
ShellCheck integration tool for MCP server.
Runs ShellCheck on Bash scripts for static analysis.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import subprocess
from fastmcp import FastMCP
from utils.file_helpers import with_temp_file


def register(mcp: FastMCP):
    @mcp.tool()
    def shellcheck_script(script: str) -> str:
        """
        Runs ShellCheck on a Bash script.
        """
        def run(fname):
            try:
                result = subprocess.run(
                    ["shellcheck", fname],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                # ShellCheck exits non-zero when it finds issues and writes them to stdout
                report = result.stdout.strip()
                if report:
                    return report
                if result.returncode != 0 and result.stderr.strip():
                    return f"ShellCheck error:\n{result.stderr.strip()}"
                return "ShellCheck found no issues."
            except FileNotFoundError:
                return "ShellCheck not found. Please install ShellCheck."
            except subprocess.TimeoutExpired:
                return "ShellCheck timed out after 30s. Try a smaller script or increase timeout."

        return with_temp_file(script, run)
