# MCP Server Tools

This directory contains modular tools used by the MCP server for code review, refactoring, security analysis, linting, and test generation.

## Tools
- `senior_review.py`: **Senior-level review** — checklist and concrete suggestions (naming, errors, types, tests, security, DRY, docs).
- `architecture.py`: Architecture recommendations
- `code_quality.py`: Code quality (AST: long functions, nesting, type hints, error handling)
- `code_structure.py`: Split code by logic; folder trees; reuse existing code
- `eslint_tool.py`: ESLint integration for JS/TS
- `patch.py`: Patch/diff generation
- `refactor.py`: Refactoring (AST: split functions, complexity, unused imports, naming)
- `security.py`: Security (eval/exec, shell/SQL injection, secrets, pickle, permissions)
- `shellcheck_tool.py`: ShellCheck integration for Bash
- `simplify.py`: Code simplification suggestions
- `tests.py`: Test recommendations (per-function and edge cases)

## Adding New Tools
To add a new tool, create a Python file and implement a `register(mcp)` function to register the tool with the MCP server.

## License
MIT License
