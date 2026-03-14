"""
Code structure tools for MCP server.
Helps split code by logic into separate files, suggest folder trees, and reuse existing code.
Author: Dmitry Troshenkov
Last Updated: March 2026
"""
import re
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def suggest_code_split(code: str, language: str = "python") -> str:
        """
        Suggests how to split code by logic into separate files and folder structure.
        Input: the current code (or a large file's content) and optional language.
        Returns a concrete plan: which file path each logical part should go in,
        so Cursor can create the files and folders. Use when refactoring a monolith
        or organizing new code by responsibility.
        """
        if not isinstance(code, str):
            return "Input error: code must be a string."
        if not code.strip():
            return "Input error: code is empty."

        language = (language or "python").strip().lower()
        plan = []

        if language == "python":
            # Heuristic: top-level classes and loose functions as split points
            classes = re.findall(r"^class\s+(\w+)\s*[:(]", code, re.MULTILINE)
            funcs = re.findall(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
            # Filter out methods (indented def)
            top_level_funcs = [
                m for m in re.finditer(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
                if m.start() == 0 or code[max(0, m.start() - 1)] == "\n"
            ]
            top_func_names = [m.group(1) for m in top_level_funcs]

            if classes:
                plan.append("Split by class (one file per domain or related group):")
                for i, name in enumerate(classes):
                    plan.append(f"  - {name} -> e.g. src/{name.lower()}.py or src/domain/{name.lower()}.py")
                plan.append("Add an __init__.py in each package directory to re-export public APIs.")
            if top_func_names and not classes:
                plan.append("Split by responsibility (group related functions):")
                plan.append(f"  - Top-level functions found: {', '.join(top_func_names[:10])}{'...' if len(top_func_names) > 10 else ''}")
                plan.append("  - Put helpers in utils/ or lib/, main flow in a single entry module.")
            if not classes and not top_func_names:
                plan.append("No obvious split points (no top-level classes or functions).")
                plan.append("Consider extracting logical blocks into modules (e.g. parsing, validation, I/O) and list them as separate files.")

            plan.append("")
            plan.append("Suggested folder tree (adjust to your project):")
            plan.append("  src/")
            if classes:
                plan.append("    __init__.py")
                for name in classes[:8]:
                    plan.append(f"    {name.lower()}.py   # class {name}")
            else:
                plan.append("    core.py      # main logic")
                plan.append("    utils.py     # helpers")
            plan.append("  tests/")
            plan.append("    test_*.py")

        else:
            plan.append(f"Language '{language}' detected. General split guidelines:")
            plan.append("  - One file per logical unit (e.g. component, service, or domain).")
            plan.append("  - Group by feature or layer (e.g. api/, services/, models/).")
            plan.append("  - Keep shared code in a common/ or utils/ module for reuse.")
            plan.append("  - Add an index/barrel file if needed to simplify imports.")

        return "\n".join(plan)

    @mcp.tool()
    def suggest_folder_structure(
        project_description: str,
        root_name: str = ".",
    ) -> str:
        """
        Suggests a folder tree for a new or existing project.
        Input: short project description (e.g. 'REST API with auth and admin') or type ('web app', 'CLI', 'library').
        Optional root_name is the project root (default '.').
        Returns a recommended directory layout so Cursor can create the folders and place files.
        """
        if not isinstance(project_description, str):
            return "Input error: project_description must be a string."
        if not project_description.strip():
            return "Input error: project_description is empty."

        desc = project_description.strip().lower()
        root = (root_name or ".").strip().rstrip("/")

        # Common templates
        if "api" in desc or "rest" in desc or "backend" in desc:
            tree = f"""
{root}/
  app/
    __init__.py
    main.py
    api/
      __init__.py
      routes/
    core/
    models/
    services/
  tests/
  config/
  requirements.txt
"""
        elif "cli" in desc or "command" in desc or "tool" in desc:
            tree = f"""
{root}/
  src/
    __init__.py
    cli.py
    commands/
    core/
  tests/
  pyproject.toml or setup.py
"""
        elif "lib" in desc or "package" in desc:
            tree = f"""
{root}/
  src/
    your_package/
      __init__.py
      core.py
      utils.py
  tests/
  pyproject.toml
"""
        elif "web" in desc or "frontend" in desc:
            tree = f"""
{root}/
  src/
    components/
    pages/
    utils/
  public/
  package.json
"""
        else:
            tree = f"""
{root}/
  src/
    __init__.py
    core.py
    utils.py
  tests/
  README.md
"""

        return (
            "Suggested folder structure (create these directories and use for new files):\n"
            + tree.strip()
            + "\n\nAdjust names (e.g. your_package, app) to match your project."
        )

    @mcp.tool()
    def suggest_reuse(code_snippet: str, existing_code_summary: str) -> str:
        """
        Suggests where to reuse existing code instead of duplicating logic.
        Input: (1) the code snippet you are writing or refactoring, (2) a short summary of
        existing modules (e.g. 'utils/helpers.py: parse_config, validate. auth/service.py: login, logout.').
        Cursor can build existing_code_summary from workspace search. Returns concrete suggestions:
        which existing function or module to use and how, so you can reuse instead of reimplementing.
        """
        if not isinstance(code_snippet, str):
            return "Input error: code_snippet must be a string."
        if not isinstance(existing_code_summary, str):
            return "Input error: existing_code_summary must be a string."
        if not code_snippet.strip():
            return "Input error: code_snippet is empty."

        suggestions = [
            "Reuse suggestions (use existing code instead of duplicating):",
            "",
        ]

        if not existing_code_summary.strip():
            suggestions.append(
                "No existing code summary provided. To get reuse suggestions, pass a summary of "
                "existing modules (e.g. file path and exported function/class names) in existing_code_summary."
            )
            return "\n".join(suggestions)

        # Simple keyword overlap: look for function/class names in snippet and match to summary
        summary_lower = existing_code_summary.lower()
        snippet_lower = code_snippet.lower()

        # Extract "path: name1, name2" from summary
        module_exports = re.findall(
            r"([a-zA-Z0-9_/.-]+\.(?:py|js|ts)?)\s*:\s*([a-zA-Z0-9_,\s]+)",
            existing_code_summary,
        )
        if not module_exports:
            # Fallback: split by lines or common separators
            for line in existing_code_summary.split("\n"):
                line = line.strip()
                if ":" in line:
                    path, _, names = line.partition(":")
                    module_exports.append((path.strip(), names.strip()))

        for path, names_str in module_exports:
            names = [n.strip() for n in re.split(r"[,;\s]+", names_str) if n.strip()]
            for name in names:
                if name.lower() in snippet_lower or name in code_snippet:
                    suggestions.append(f"  - Reuse '{name}' from {path} in this code.")
                    break

        if len(suggestions) == 2:
            suggestions.append(
                "  - Review existing_code_summary: group by file and list public functions/classes."
            )
            suggestions.append(
                "  - Prefer importing and calling existing helpers instead of copying logic."
            )

        suggestions.append("")
        suggestions.append(
            "Best practice: import from the existing module and call the function/class; "
            "avoid pasting the same logic into multiple files."
        )
        return "\n".join(suggestions)
