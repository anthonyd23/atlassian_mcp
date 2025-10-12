# Atlassian MCP Server

A Model Context Protocol (MCP) server for Atlassian tools (Bitbucket, Confluence, and Jira) deployed on AWS.

## Features

- **Bitbucket Integration**: Search repositories, access pull requests
- **Confluence Integration**: Search pages and spaces, access content
- **Jira Integration**: Search issues using JQL, access projects
- **AWS Deployment**: Serverless deployment using Lambda and API Gateway

## Prerequisites

1. **Atlassian API Token**: Generate from your Atlassian account settings
2. **AWS CLI**: Configured with appropriate permissions
3. **SAM CLI**: For deployment to AWS

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r mcp_server/requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
   export ATLASSIAN_USERNAME="your-email@company.com"
   export ATLASSIAN_API_TOKEN="your-api-token"
   ```

3. **Deploy to AWS**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## Local Development

Run the MCP server locally:

```bash
cd mcp_server
python main.py
```

## API Endpoints

Once deployed, your MCP server will be available at:
- `POST /mcp` - Main MCP protocol endpoint
- `GET /mcp` - Health check

## MCP Resources

- `atlassian://bitbucket/repositories` - List Bitbucket repositories
- `atlassian://confluence/spaces` - List Confluence spaces  
- `atlassian://jira/projects` - List Jira projects

## MCP Tools

- `search_bitbucket` - Search Bitbucket repositories and projects
- `search_confluence` - Search Confluence pages and spaces
- `search_jira` - Search Jira issues using JQL

## Configuration

The server uses the following environment variables:

- `ATLASSIAN_BASE_URL` - Your Atlassian instance URL
- `ATLASSIAN_USERNAME` - Your Atlassian username/email
- `ATLASSIAN_API_TOKEN` - Your Atlassian API token

## Security

- API tokens are stored as encrypted environment variables in Lambda
- All API calls use HTTPS
- Basic authentication with Atlassian APIs