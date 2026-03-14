"""
Code Review MCP Server main entry point.
Initializes and runs the Code Review MCP Server.
Adds error handling, logging, and configuration validation.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import logging
import json
import sys
from mcp.server.fastmcp import FastMCP
from tools import register as register_tools

CONFIG_PATH = "mcp.json"


def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        logging.error("Failed to load config: %s", e)
        return None
    except json.JSONDecodeError as e:
        logging.error("Invalid config JSON: %s", e)
        return None


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Code Review MCP Server...")

    config = load_config(CONFIG_PATH)
    if not config:
        logging.error("Configuration missing or invalid. Exiting.")
        sys.exit(1)

    try:
        mcp = FastMCP("code-review-mcp")
        register_tools(mcp)
        logging.info("All tools registered successfully.")
        mcp.run()
        logging.info("MCP server is running.")
    except Exception as e:
        logging.error(f"Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
