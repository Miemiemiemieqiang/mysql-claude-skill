# server.py
import json
import re
import os
import functools
from contextlib import contextmanager

import mysql.connector
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("MySQL-Skill")


def _check_env_vars():
    """Return diagnostic string if required env vars are missing, else None."""
    required = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        return (
            f"Missing environment variables: {', '.join(missing)}. "
            "Please set them in a .env file or export them:\n"
            "  DB_HOST=localhost  (optional, defaults to localhost)\n"
            "  DB_USER=your_username\n"
            "  DB_PASSWORD=your_password\n"
            "  DB_NAME=your_database"
        )
    return None


@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    try:
        yield conn
    finally:
        conn.close()


def with_db_error_handling(func):
    """Decorator that wraps tool functions with unified error handling and env var diagnostics."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        env_err = _check_env_vars()
        if env_err:
            return env_err
        try:
            return func(*args, **kwargs)
        except Exception as e:
            host = os.getenv("DB_HOST", "localhost")
            return (
                f"Database Error: {e}\n"
                f"Please check your environment variables:\n"
                f"  DB_HOST (current: {host})\n"
                f"  DB_USER, DB_PASSWORD, DB_NAME"
            )
    return wrapper


@mcp.tool()
@with_db_error_handling
def list_tables() -> str:
    """List all table names in the connected database. Use this to discover available tables before querying. Returns comma-separated table names."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
    return f"Tables in database: {', '.join(tables)}"


@mcp.tool()
@with_db_error_handling
def show_create_table(table_name: str) -> str:
    """Show the full CREATE TABLE DDL for a given table, including columns, types, indexes, and constraints. Use this to understand a table's schema before writing queries. `table_name`: exact table name from `list_tables`."""
    if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
        return "Error: Invalid table name. Only letters, digits, and underscores are allowed."
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        cursor.close()
    return result[1] if result else f"Table '{table_name}' not found."


@mcp.tool()
@with_db_error_handling
def execute_query(sql: str) -> str:
    """Execute a read-only SQL query and return results as JSON. Only SELECT statements are allowed. Use `list_tables` and `show_create_table` to understand the schema before writing queries. For large tables, always use LIMIT."""
    stripped = sql.strip().lower()
    if not stripped.startswith("select"):
        return "Error: Only SELECT queries are allowed for safety."
    if "into outfile" in stripped or "into dumpfile" in stripped:
        return "Error: INTO OUTFILE/DUMPFILE is not allowed."

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()

    if not results:
        return "Query executed successfully, but no rows were returned."
    return json.dumps(results, default=str, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
