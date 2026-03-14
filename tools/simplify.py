"""
Code simplification tool for MCP server.
Detects opportunities to simplify code structure.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP):
    @mcp.tool()
    def simplify_code(code: str) -> str:
        """
        Detects code simplification opportunities.
        """
        try:
            if not isinstance(code, str):
                return "Input error: code must be a string."
            suggestions = []

            if code.count("class ") > 3:
                suggestions.append("Too many classes")

            if code.count("import ") > 10:
                suggestions.append("Too many dependencies")

            return "\n".join(suggestions) if suggestions else "Code structure looks simple."
        except Exception as e:
            return f"Simplification error: {str(e)}"