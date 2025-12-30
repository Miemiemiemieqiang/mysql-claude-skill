# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides MySQL database tools for Claude Code. It uses FastMCP to expose three main tools: `list_tables`, `show_create_table`, and `execute_query`.

## Architecture

- **Entry point**: `server.py` - The main MCP server file
- **MCP Framework**: Uses `FastMCP` from `mcp.server.fastmcp`
- **Database connector**: `mysql.connector` for MySQL connections
- **Configuration**: Environment variables loaded via `python-dotenv`

The server is configured as a FastMCP module with the entry point `server:mcp.run` (defined in pyproject.toml as `mysql-skill`).

## Required Environment Variables

The server expects these environment variables (typically in `.env` file, which is gitignored):
- `DB_HOST` - MySQL host (defaults to "localhost")
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_NAME` - Database name

## Development Commands

### Running the server locally
```bash
python server.py
```

### Using uv to run (as configured in .mcp.json)
```bash
uv --directory /path/to/mysql-claude-skill run python server.py
```

### Installing dependencies
```bash
uv sync
```

### Building for release
```bash
pip install build
python -m build
```

## Available MCP Tools

- `list_tables()` - Lists all tables in the database
- `show_create_table(table_name: str)` - Shows CREATE TABLE statement for a table
- `execute_query(sql: str)` - Executes SELECT queries only (safety restriction)

## Important Notes

- The `execute_query` tool only allows SELECT queries for safety reasons
- For production, consider enforcing read-only access at the database level
- The project uses Python 3.13+ (check pyproject.toml for exact version requirements)