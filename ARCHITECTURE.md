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
│               │                        │  + API Key    │
│  MCP Server   │                        │      │        │
└───────┬───────┘                        │      ▼        │
        │                                │   Lambda      │
        │                                │  Function     │
        │                                └───────┬───────┘
        │                                        │
        └────────────────┬───────────────────────┘
                         │
                         ▼
                ┌────────────────┐
                │  router.py     │
                │  Tool Routing  │
                └────────┬───────┘
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
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│  validation.py  │              │    auth.py      │
│  - Input checks │              │  - CloudAuth    │
│  - URL encoding │              │  - DCAuth       │
└─────────────────┘              └─────────────────┘
       │                                │
       └────────────────┬───────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  requests.Session│
              │  - Retry logic   │
              │  - Timeouts      │
              │  - Pooling       │
              └─────────┬────────┘
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
- API Gateway with API key authentication
- Environment variables from Lambda config
- Rate limiting: 100 req/sec, 200 burst

### Core Components

**router.py**
- Central routing for all tools
- Maps tool names to provider methods
- Shared by both main.py and lambda_handler.py
- Single source of truth for tool dispatch

**Providers**
- Cloud: jira_provider.py, confluence_provider.py, bitbucket_provider.py
- Data Center: jira_dc_provider.py, confluence_dc_provider.py, bitbucket_dc_provider.py
- Each implements service-specific API calls
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

### Request Flow

1. **User request** → Amazon Q Developer
2. **MCP protocol** → main.py (local) or API Gateway (AWS)
3. **Tool routing** → router.py dispatches to provider
4. **Validation** → Input checked and sanitized
5. **Authentication** → Headers added by auth class
6. **HTTP request** → requests.Session with retry logic
7. **API call** → Atlassian REST API
8. **Response** → Returned through MCP protocol

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

1. **API Gateway** - API key required, rate limiting
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
sam build
sam deploy --guided
→ API Gateway URL + API Key
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
