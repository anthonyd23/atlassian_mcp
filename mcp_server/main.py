
from fastapi import FastAPI, Depends, HTTPException, status
from mcp_server.auth import Auth
from mcp_server.bitbucket_provider import BitbucketProvider
from mcp_server.confluence_provider import ConfluenceProvider
from mcp_server.jira_provider import JiraProvider

app = FastAPI(title="MCP Server for Atlassian Tools")

auth = Auth()
bitbucket_provider = BitbucketProvider()
confluence_provider = ConfluenceProvider()
jira_provider = JiraProvider()

def authenticate(token: str):
    if not auth.authenticate(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/")
def read_root():
    return {"message": "MCP Server for Atlassian Tools"}

@app.get("/context/bitbucket")
def get_bitbucket_context(token: str = Depends(authenticate)):
    return bitbucket_provider.get_context()

@app.get("/context/confluence")
def get_confluence_context(token: str = Depends(authenticate)):
    return confluence_provider.get_context()

@app.get("/context/jira")
def get_jira_context(token: str = Depends(authenticate)):
    return jira_provider.get_context()
