# learning_mcp
Project so that I can learn how to build an MCP server.

# Config with UV on WSL
Closing Claude Desktop and restarting device finally allowed the MCP server to become visible

{
  "mcpServers": {
    "Demo": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "source ~/.bashrc && cd / && /home/pds/.local/bin/uv run --with mcp[cli] mcp run /home/pds/personal/learning_mcp/mcp-server-demo/main.py"
      ]
    }
  }
}
