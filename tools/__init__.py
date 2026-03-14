"""
tools/__init__.py
Initialize MCP tools package.
Automatically registers all tools for MCP server.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
from mcp.server.fastmcp import FastMCP

from . import (
    architecture,
    code_quality,
    code_structure,
    security,
    senior_review,
    simplify,
    patch,
    refactor,
    tests,
    shellcheck_tool,
    eslint_tool,
)


def register(mcp: FastMCP) -> None:
    """
    Register all MCP tools with the given MCP server instance.
    """
    architecture.register(mcp)
    code_quality.register(mcp)
    code_structure.register(mcp)
    security.register(mcp)
    senior_review.register(mcp)
    simplify.register(mcp)
    patch.register(mcp)
    refactor.register(mcp)
    tests.register(mcp)
    shellcheck_tool.register(mcp)
    eslint_tool.register(mcp)