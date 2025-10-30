# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
├─────────────────────────────────────────────────────────────────┤
│                      Amazon Q Developer                         │
│                    (or other MCP client)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol (stdio/HTTP)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────┐                        ┌───────────────┐
│  Local Mode   │                        │   AWS Mode    │
│   (stdio)     │                        │   (HTTP)      │
├───────────────┤                        ├───────────────┤
│   main.py     │                        │ API Gateway   │
│               │                        │ + IAM Auth    │
│  MCP Server   │                        │      │        │
└───────┬───────┘                        │      ▼        │
        │                                │   Lambda      │
        │                                │  Function     │
        │                                └───────┬───────┘
        │                                        │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌────────────────┬────────────────┐
        │   router.py    │ tool_schemas.py│
        │ Tool Routing   │  MCP Schemas   │
        └────────┬───────┴────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Jira         │  │ Confluence   │  │ Bitbucket    │
│ Provider     │  │ Provider     │  │ Provider     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  validation.py  │
                │  - Input checks │
                │  - URL encoding │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    auth.py      │
                │  - CloudAuth    │
                │  - DCAuth       │
                └────────┬────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  requests.Session│
                │  - Retry logic   │
                │  - Timeouts      │
                │  - Pooling       │
                └────────┬─────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Jira Cloud/  │ │ Confluence   │ │ Bitbucket    │
│ Data Center  │ │ Cloud/DC     │ │ Cloud/DC     │
│ REST API     │ │ REST API     │ │ REST API     │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Component Details

### Entry Points

**Local Mode (main.py)**
- Runs as stdio MCP server
- Used by Amazon Q Developer locally
- Direct Python execution
- Environment variables from shell/IDE config

**AWS Mode (lambda_handler.py)**
- Runs as HTTP endpoint via Lambda
- API Gateway with IAM authentication
- Environment variables from Lambda config
- CloudWatch monitoring and structured logging

### Core Components

**router.py**
- Central routing for all tools
- Maps tool names to provider methods
- Shared by both main.py and lambda_handler.py
- Single source of truth for tool dispatch

**tool_schemas.py**
- MCP tool schema definitions
- Input validation schemas for each tool
- Used by both local and AWS modes
- Works with router.py to provide complete tool functionality

**Providers**
- Cloud: jira_provider.py, confluence_provider.py, bitbucket_provider.py
- Data Center: jira_dc_provider.py, confluence_dc_provider.py, bitbucket_dc_provider.py
- Each implements service-specific API calls
- Auto-detect availability based on environment variables
- Automatic platform detection via auth classes

**validation.py**
- Input validation before API calls
- URL encoding for path parameters
- Path traversal prevention
- Format validation (issue keys, page IDs, etc.)

**auth.py**
- CloudAuth: Basic auth with API tokens
- DataCenterAuth: Bearer token with PAT
- Platform auto-detection via service-specific PAT tokens

### Tool Processing Flow

**Tool Registration (Startup):**
1. `tools.py` provides tool names and descriptions
2. `tool_schemas.py` provides JSON schemas for input validation
3. Combined into MCP Tool objects with validation rules

**Tool Execution (Runtime):**
1. **User request** → Amazon Q Developer
2. **MCP protocol** → main.py (local) or API Gateway (AWS)
3. **Schema validation** → Arguments validated against tool_schemas.py
4. **Tool routing** → router.py dispatches to provider method
5. **Input validation** → Additional checks in validation.py
6. **Authentication** → Headers added by auth class
7. **HTTP request** → requests.Session with retry logic
8. **API call** → Atlassian REST API
9. **Response** → Returned through MCP protocol

### router.py ↔ tool_schemas.py Integration

```python
# Tool registration combines both components:
Tool(name=tool["name"], 
     description=tool["description"],
     inputSchema=TOOL_SCHEMAS.get(tool["name"], {}))

# Execution flow:
User Input → Schema Validation → Router Dispatch → Provider Method
```

- **tool_schemas.py**: Defines what inputs are valid (JSON Schema)
- **router.py**: Defines what happens when tool is called (execution logic)
- Together they provide complete tool functionality: validation + execution

## Platform Detection

```python
if JIRA_PAT_TOKEN or CONFLUENCE_PAT_TOKEN or BITBUCKET_PAT_TOKEN:
    → Data Center mode
    → Use DataCenterAuth (Bearer token)
    → Use *_dc_provider.py classes
else:
    → Cloud mode
    → Use CloudAuth (Basic auth)
    → Use cloud/*_provider.py classes
```

## Security Layers

1. **API Gateway** - IAM authentication required
2. **Input Validation** - All inputs validated before use
3. **URL Encoding** - Path parameters sanitized
4. **HTTPS** - All traffic encrypted in transit
5. **Environment Variables** - Credentials encrypted at rest (Lambda)

## Error Handling

```
User Input
    ↓
Validation (validation.py)
    ↓ (if invalid)
Return {'error': 'message'}
    ↓ (if valid)
API Call with Retry
    ↓ (429, 500, 502, 503, 504)
Exponential Backoff (3 attempts)
    ↓ (if still fails)
Return {'error': 'message'}
    ↓ (if success)
Return API Response
```

## Deployment Modes

### Local Development
```
pip install -r mcp_server/requirements.txt
export ATLASSIAN_BASE_URL=...
export ATLASSIAN_API_TOKEN=...
python mcp_server/main.py
```

### AWS Lambda
```
cp config.template.yaml config.yaml
# Edit config.yaml with credentials
python deploy.py
→ API Gateway URL (IAM authenticated)
```

## Monitoring (AWS Only)

- **CloudWatch Logs** - All Lambda invocations
- **Custom Metrics** - Tool usage and duration
- **CloudWatch Dashboard** - Visual overview
- **Alarms** - Email alerts for errors/throttles
- **Structured Logging** - JSON logs with context

## Technology Stack

- **Language**: Python 3.11+
- **MCP Protocol**: stdio (local) / HTTP (AWS)
- **HTTP Client**: requests with urllib3.Retry
- **AWS Services**: Lambda, API Gateway, CloudWatch
- **Deployment**: AWS SAM
- **Testing**: pytest with unittest.mock
