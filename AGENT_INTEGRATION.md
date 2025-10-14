# AI Agent Integration Guide

This guide shows how to integrate the Atlassian MCP Server with popular AI agents and development tools.

## Table of Contents

- [Amazon Q Developer](#amazon-q-developer)
- [Claude Desktop](#claude-desktop)
- [Cline (VS Code)](#cline-vs-code)
- [Cursor](#cursor)
- [Continue](#continue)
- [Zed Editor](#zed-editor)
- [Custom Integration](#custom-integration)

---

## Amazon Q Developer

**Location:** Amazon Q Developer Settings → MCP Servers

**Configuration File:**
- **Windows:** `%APPDATA%\Amazon Q\mcp_config.json`
- **Mac/Linux:** `~/.config/amazonq/mcp_config.json`

**Setup:**

```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
      }
    }
  }
}
```

**Example Prompts:**
- "Search Jira for issues assigned to me"
- "Create a new Jira issue in PROJECT-123"
- "Show me recent Confluence pages"
- "List open pull requests in my Bitbucket workspace"

---

## Claude Desktop

**Location:** Claude Desktop Settings → Developer → Edit Config

**Configuration File:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**Setup:**

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-api-token",
        "BITBUCKET_WORKSPACE": "your-workspace",
        "BITBUCKET_API_TOKEN": "your-bb-token"
      }
    }
  }
}
```

**Restart Required:** Yes, restart Claude Desktop after configuration changes.

---

## Cline (VS Code)

**Location:** VS Code → Cline Extension Settings → MCP Servers

**Configuration File:**
- **Windows:** `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- **Mac:** `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Linux:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Setup:**

```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
      }
    }
  }
}
```

**Alternative:** Use VS Code settings UI:
1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Search "Cline: Edit MCP Settings"
3. Add configuration

---

## Cursor

**Location:** Cursor Settings → Features → Model Context Protocol

**Configuration File:**
- **Windows:** `%APPDATA%\Cursor\User\globalStorage\mcp\mcp_config.json`
- **Mac:** `~/Library/Application Support/Cursor/User/globalStorage/mcp/mcp_config.json`
- **Linux:** `~/.config/Cursor/User/globalStorage/mcp/mcp_config.json`

**Setup:**

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
      }
    }
  }
}
```

**Usage:** Use `@atlassian` in Cursor chat to invoke MCP tools.

---

## Continue

**Location:** Continue Extension Settings → config.json

**Configuration File:**
- **Windows:** `%USERPROFILE%\.continue\config.json`
- **Mac/Linux:** `~/.continue/config.json`

**Setup:**

```json
{
  "models": [...],
  "mcpServers": [
    {
      "name": "atlassian-mcp",
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
      }
    }
  ]
}
```

**Note:** Continue uses array format for `mcpServers` instead of object format.

---

## Zed Editor

**Location:** Zed Settings → Extensions → MCP

**Configuration File:**
- **Mac:** `~/Library/Application Support/Zed/settings.json`
- **Linux:** `~/.config/zed/settings.json`

**Setup:**

```json
{
  "mcp": {
    "servers": {
      "atlassian": {
        "command": "python",
        "args": ["/absolute/path/to/mcp_server/main.py"],
        "env": {
          "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
          "ATLASSIAN_USERNAME": "your-email@company.com",
          "ATLASSIAN_API_TOKEN": "your-token"
        }
      }
    }
  }
}
```

---

## Custom Integration

### Using MCP Client Library

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server
server_params = StdioServerParameters(
    command="python",
    args=["/path/to/mcp_server/main.py"],
    env={
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
    }
)

# Connect and use
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        
        # Call a tool
        result = await session.call_tool("search_jira", {
            "jql": "assignee = currentUser() AND status = 'In Progress'"
        })
```

### Using HTTP API (AWS Deployment)

```python
import requests

API_URL = "https://your-api-gateway-url.amazonaws.com/Prod/mcp"
API_KEY = "your-api-key"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# List tools
response = requests.post(
    API_URL,
    headers=headers,
    json={"method": "tools/list"}
)

# Call a tool
response = requests.post(
    API_URL,
    headers=headers,
    json={
        "method": "tools/call",
        "params": {
            "name": "search_jira",
            "arguments": {
                "jql": "project = PROJ"
            }
        }
    }
)
```

---

## Configuration Tips

### 1. Use Absolute Paths
Always use absolute paths for the `main.py` file:
- ✅ `/Users/username/atlassian_mcp/mcp_server/main.py`
- ✅ `C:\Users\username\atlassian_mcp\mcp_server\main.py`
- ❌ `./mcp_server/main.py`

### 2. Python Command
Use the correct Python command for your system:
- Most systems: `python` or `python3`
- Virtual env: `/path/to/venv/bin/python`
- Windows venv: `C:\path\to\venv\Scripts\python.exe`

### 3. Environment Variables
You can also use system environment variables instead of inline `env`:
```bash
# Set once in your shell profile
export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
export ATLASSIAN_USERNAME="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-token"
```

Then simplify config:
```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"]
    }
  }
}
```

### 4. Multiple Environments
Configure different servers for different Atlassian instances:
```json
{
  "mcpServers": {
    "atlassian-prod": {
      "command": "python",
      "args": ["/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://prod.atlassian.net",
        "ATLASSIAN_USERNAME": "user@company.com",
        "ATLASSIAN_API_TOKEN": "prod-token"
      }
    },
    "atlassian-staging": {
      "command": "python",
      "args": ["/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://staging.atlassian.net",
        "ATLASSIAN_USERNAME": "user@company.com",
        "ATLASSIAN_API_TOKEN": "staging-token"
      }
    }
  }
}
```

---

## Troubleshooting

### Server Not Starting
1. Check Python is in PATH: `python --version`
2. Verify dependencies: `pip install -r mcp_server/requirements.txt`
3. Test manually: `python mcp_server/main.py`
4. Check logs in agent's developer console

### Authentication Errors
1. Verify credentials are correct
2. Check token hasn't expired
3. Ensure base URL includes `https://`
4. Test credentials with integration tests:
   ```bash
   python tests/cloud/test_all_tools.py
   ```

### Tools Not Appearing
1. Restart the agent/editor
2. Check MCP server is running (look for process)
3. Verify JSON syntax is valid
4. Check agent supports MCP protocol

### Permission Errors
1. Ensure API token has required permissions
2. Check user has access to projects/spaces
3. Verify workspace/project keys are correct

---

## Need Help?

- **Features:** See [README.md](README.md) for complete feature list
- **Configuration:** [QUICK_START.md](QUICK_START.md)
- **Deployment:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Issues:** [GitHub Issues](https://github.com/anthonyd23/atlassian_mcp/issues)
