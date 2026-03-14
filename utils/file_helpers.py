"""
Utility functions for MCP server.
Handles temporary files and diff generation.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import difflib
import os
import tempfile
from typing import Callable


def with_temp_file(content: str, callback: Callable[[str], str]) -> str:
    """
    Creates a temporary file with the given content, runs the callback with
    the file path, then cleans up the file.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        fname = f.name
    try:
        return callback(fname)
    finally:
        os.remove(fname)


def generate_diff(old_text: str, new_text: str) -> str:
    """
    Returns a unified diff between old_text and new_text.
    """
    diff = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        lineterm="",
    )
    return "\n".join(diff)