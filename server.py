# server.py
import mysql.connector
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("MySQL-Skill")

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@mcp.tool()
def test_connection() -> str:
    """Test the MySQL database connection. If it fails, provides hints on setting environment variables."""
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        return (
            f"Missing environment variables: {', '.join(missing)}. "
            "Please set them in a .env file or export them:\n"
            "  DB_HOST=localhost  (optional, defaults to localhost)\n"
            "  DB_USER=your_username\n"
            "  DB_PASSWORD=your_password\n"
            "  DB_NAME=your_database"
        )
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return "Connection successful."
    except Exception as e:
        host = os.getenv("DB_HOST", "localhost")
        return (
            f"Connection failed: {e}\n"
            f"Please check your environment variables:\n"
            f"  DB_HOST (current: {host})\n"
            f"  DB_USER, DB_PASSWORD, DB_NAME"
        )

@mcp.tool()
def list_tables() -> str:
    """List all tables in the database to understand the schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return f"Tables in database: {', '.join(tables)}"

@mcp.tool()
def show_create_table(table_name: str) -> str:
    """Show the CREATE TABLE statement for a specific table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[1] if result else f"Table '{table_name}' not found."
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def execute_query(sql: str) -> str:
    """
    Execute a SELECT SQL query on the MySQL database.
    Use this to fetch data based on user requests.
    """
    # Security: In production, enforce read-only users at the DB level
    if not sql.strip().lower().startswith("select"):
        return "Error: Only SELECT queries are allowed for safety."

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if not results:
            return "Query executed successfully, but no rows were returned."
        return str(results)
    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
