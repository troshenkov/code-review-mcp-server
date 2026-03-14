"""
utils/__init__.py

Utility helpers used across the MCP server project.
This module exposes commonly used utility functions
for safe temporary file handling and diff generation.

Author: Dmitry Troshenkov
Last Updated: March 2026
"""

from .file_helpers import with_temp_file, generate_diff

__all__ = [
    "with_temp_file",
    "generate_diff",
]