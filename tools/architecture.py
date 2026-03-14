"""
Architecture review tool for MCP server.
Provides recommendations for software architecture.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import logging
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP):
    @mcp.tool()
    def review_architecture(problem: str, constraints: str = "") -> str:
        """
        Provides architecture recommendations for a problem with optional constraints.
        """
        try:
            if not isinstance(problem, str) or not isinstance(constraints, str):
                logging.error("Input error: problem and constraints must be strings.")
                return "Input error: problem and constraints must be strings."
            logging.info("Reviewing architecture for problem: %s", problem)
            return f"""
Architecture Review

Problem:
{problem}

Constraints:
{constraints}

Recommended guidelines:
- Minimal dependencies
- Clear modular design
- Explicit error handling
- Simple, maintainable code
"""
        except Exception as e:
            logging.error(f"Architecture review error: {str(e)}")
            return f"Architecture review error: {str(e)}"