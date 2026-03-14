"""
mcp-server package

Code Review MCP Server
Provides modular tools for code review, refactoring,
security analysis, and lint integration.

Author: Dmitry Troshenkov
Last Updated: March 2026
"""

__version__ = "1.0.0"
__author__ = "Dmitry Troshenkov"

# Optional: expose main entry
from .code_review_mcp_server import main

__all__ = [
    "main",
]