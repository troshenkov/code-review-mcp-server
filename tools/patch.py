"""
Patch generation tool for MCP server.
Generates unified diffs between code versions.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import difflib
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP):
    @mcp.tool()
    def generate_patch(old_code: str, new_code: str) -> str:
        """
        Generates unified diff between old_code and new_code.
        """
        try:
            if not isinstance(old_code, str) or not isinstance(new_code, str):
                return "Input error: Both old_code and new_code must be strings."
            diff = difflib.unified_diff(
                old_code.splitlines(),
                new_code.splitlines(),
                lineterm=""
            )
            return "\n".join(diff)
        except Exception as e:
            return f"Patch generation error: {str(e)}"