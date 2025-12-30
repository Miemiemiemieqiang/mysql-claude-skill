# MySQL MCP Server

A Model Context Protocol (MCP) server that provides MySQL database tools for Claude Code. This server allows Claude to interact with MySQL databases by listing tables, inspecting schemas, and executing SELECT queries.

## Features

- **List Tables**: Quickly view all tables in your database
- **Inspect Schema**: View `CREATE TABLE` statements to understand table structure
- **Execute Queries**: Run SELECT queries to fetch data (SELECT-only for safety)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/mysql-claude-skill.git
cd mysql-claude-skill
```

2. Install dependencies using uv:
```bash
uv sync
```

## Configuration

Create a `.env` file in the project root with your MySQL credentials:

```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
```

## Usage

### Running the Server

```bash
python server.py
```

Or using uv:
```bash
uv run python server.py
```

### Configuring Claude Code

Add to your Claude Code MCP configuration (`.mcp.json`):

```json
{
  "mcpServers": {
    "mysql-skill": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mysql-claude-skill",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_tables()` | List all tables in the database |
| `show_create_table(table_name)` | Show the CREATE TABLE statement for a specific table |
| `execute_query(sql)` | Execute a SELECT query on the database |

## Security

- The `execute_query` tool only allows SELECT queries for safety
- For production use, consider enforcing read-only access at the database user level
- Never commit your `.env` file with real credentials

## Requirements

- Python 3.13+
- MySQL 5.7+ or MariaDB 10.2+

## Development

### Building for Release

```bash
pip install build
python -m build
```

### Running Tests

```bash
pytest
```

## License

MIT