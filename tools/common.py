"""
Shared types and helpers for MCP tools.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
from typing import Any

# (message, line_number or None)
Finding = tuple[str, int | None]


def format_finding(finding: Finding, file_path: str | None) -> str:
    """Format a finding for display, optionally with file:line."""
    msg, line = finding
    if file_path and line is not None:
        return f"  - {file_path}:{line}: {msg}"
    if line is not None:
        return f"  - line {line}: {msg}"
    return f"  - {msg}"


def require_str(value: Any, name: str = "input") -> str | None:
    """
    Validate that value is a non-empty string.
    Returns None if valid, else an error message string.
    """
    if not isinstance(value, str):
        return f"Input error: {name} must be a string."
    if not value.strip():
        return f"Input error: {name} is empty."
    return None
