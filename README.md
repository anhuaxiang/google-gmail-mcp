# Google Gmail MCP

A Model Context Protocol (MCP) server that provides Google Gmail integration for AI assistants like Claude.


```json

{
  "mcpServers": {
    "google-gmail": {
      "env": {
        "GOOGLE_ACCESS_TOKEN": "GOOGLE_ACCESS_TOKEN",
        "GOOGLE_REFRESH_TOKEN": "GOOGLE_REFRESH_TOKEN",
        "GOOGLE_CLIENT_ID": "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET": "GOOGLE_CLIENT_SECRET"
      },
      "command": "uvx",
      "args": [
        "google-mail-mcpserver"
      ]
    }
  }
}
```