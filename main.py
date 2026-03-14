"""
Main entry point for MCP Server.
Initializes and runs the Code Review MCP Server.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
from mcp.server.fastmcp import FastMCP
from tools import register as register_tools


def main():
    mcp = FastMCP("code-review-mcp")
    register_tools(mcp)
    mcp.run()

if __name__ == "__main__":
    main()
