# Code Review MCP Server

An **open-source** [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that brings senior-level code review into your editor. Use it with **Cursor** or any MCP client to get quality checks, refactor suggestions, security checks, and best-practice guidance as you code.

## Quick start

```bash
git clone <this-repo>
cd mcp_server
python -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python code_review_mcp_server.py
```

**With Cursor:** Add the server to your MCP config (e.g. copy `mcp.json` into `~/.cursor/` and set `workingDirectory` to this repo). Cursor will then offer tools like `senior_review`, `review_code_quality`, and `security_review` when you work on code.

## What it does

The server exposes **tools** over MCP that your editor can call to:

| Area | Tools |
|------|--------|
| **One-shot review** | `senior_review` — checklist and concrete suggestions (naming, errors, types, tests, security, DRY) |
| **Quality** | `review_code_quality` — long functions, nesting, type hints, error handling |
| **Security** | `security_review` — eval/exec, shell/SQL injection, hardcoded secrets, permissions |
| **Refactor** | `refactor_code` — split functions, reduce complexity, unused imports, naming |
| **Structure** | `suggest_code_split`, `suggest_folder_structure`, `suggest_reuse` — split by logic, folder layout, reuse existing code |
| **Tests** | `generate_tests` — scenarios and edge cases per function |
| **Static analysis** | ShellCheck (Bash), ESLint (JS/TS), patch generation |

So instead of "quick AI code," you get feedback that matches what a senior engineer would expect in a code review: clear structure, fewer security risks, and maintainable patterns.

## Requirements

- **Python 3.10+**
- **Optional:** [ShellCheck](https://www.shellcheck.net/) for Bash analysis, [ESLint](https://eslint.org/) (e.g. via `npx`) for JavaScript/TypeScript

## Project structure

```
mcp_server/
  main.py                      # Minimal entry point
  code_review_mcp_server.py    # Entry point with config and logging
  tools/                        # MCP tools (quality, security, refactor, etc.)
  utils/                        # Helpers (temp files, diffs)
  tests/                        # Unit tests (tools, utils, common)
  mcp.json                      # Example MCP config for Cursor
  requirements.txt
  requirements-dev.txt          # Dev deps (pytest); optional
  pyproject.toml               # Project metadata and pytest config
```

## Testing

From the project root (with the venv activated and deps installed):

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Or install dev deps and use pytest: `pip install -r requirements-dev.txt` then `pytest tests/ -v`.

## Usage

1. **Run the server** from the project directory:
   ```bash
   ./venv/bin/python code_review_mcp_server.py
   ```
   or `python main.py` (both use the same config and logging).

2. **Use from Cursor:** Point your Cursor MCP config at this repo. The example `mcp.json` uses relative paths: `workingDirectory` should resolve to the cloned repo (e.g. `../mcp_server` if the config file lives in `~/.cursor`). For reliability, you can set `workingDirectory` to the absolute path of this repo (e.g. `~/mcp_server`).

### Getting better results

- **Pass `file_path`** when calling `senior_review`, `review_code_quality`, or `security_review`. Findings will include `file:line` references so you can jump to the exact location.
- **Use `focus`** with `senior_review` to narrow the checklist: `"security"` (secrets, injection, permissions), `"api"` (naming, types, docs), or omit for the full checklist.
- **Review in small chunks.** Run review on one file or one concern at a time; large blobs of code produce noisier or vaguer feedback.
- **Ask for one thing at a time.** For example: “Run security_review on this file” or “Run senior_review with focus=api on this function.”

## License and author

**License:** MIT — see [LICENSE](LICENSE).  
**Author:** Dmitry Troshenkov.

Contributions and feedback are welcome.
