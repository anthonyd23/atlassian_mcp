"""Unit tests for ticket support agent"""

import pytest
from mcp_server.agents.ticket_support_agent import TicketSupportAgent


@pytest.fixture
def primary_team():
    return [
        {"account_id": "user1", "name": "Alice"},
        {"account_id": "user2", "name": "Bob"}
    ]


@pytest.fixture
def secondary_team():
    return [
        {"account_id": "user3", "name": "Charlie"}
    ]


@pytest.fixture
def template_mapping():
    return {
        "Bug": {
            "parent_page": "Bug Templates",
            "custom_field": "customfield_10001"
        }
    }


@pytest.fixture
def agent(primary_team, secondary_team, template_mapping):
    return TicketSupportAgent(primary_team, secondary_team, template_mapping)


@pytest.mark.asyncio
async def test_get_template_context_exposes_raw_data(agent):
    issue_data = {
        "key": "TEST-123",
        "fields": {
            "issuetype": {"name": "Bug"},
            "description": "Test description",
            "priority": {"name": "High"}
        }
    }
    
    context = await agent.get_template_context(issue_data)
    
    assert context['ticket']['key'] == "TEST-123"
    assert context['ticket']['fields'] == issue_data['fields']
    assert context['template_config'] is not None
    assert context['template_config']['parent_page'] == "Bug Templates"


@pytest.mark.asyncio
async def test_get_team_context_exposes_raw_issues(agent):
    async def mock_search(account_id, excluded_issue_types=None):
        workload_map = {
            "user1": {"results": [{"key": "T-1"}, {"key": "T-2"}]},
            "user2": {"results": [{"key": "T-3"}]},
            "user3": {"results": []}
        }
        return workload_map.get(account_id, {"results": []})
    
    context = await agent.get_team_context(mock_search)
    
    assert 'primary_team' in context
    assert 'secondary_team' in context
    assert len(context['primary_team']) == 2
    assert len(context['secondary_team']) == 1
    assert context['primary_team'][0]['member']['name'] == "Alice"
    assert len(context['primary_team'][0]['issues']) == 2


@pytest.mark.asyncio
async def test_template_context_without_confluence_provider():
    agent = TicketSupportAgent(
        [{"account_id": "u1", "name": "User1"}],
        [],
        {"Bug": {"parent_page": "Templates"}},
        confluence_provider=None
    )
    
    issue_data = {
        "key": "TEST-1",
        "fields": {"issuetype": {"name": "Bug"}}
    }
    
    context = await agent.get_template_context(issue_data)
    
    assert context['template_config'] is not None
    assert context['template_pages'] == []


@pytest.mark.asyncio
async def test_get_open_support_tickets_tool():
    from mcp_server.common.ticket_support_tools import initialize_agent, get_open_support_tickets
    
    # Initialize agent
    template_mapping = {
        'Support Request': {
            'parent_page': 'Templates',
            'custom_field': 'customfield_10001'
        }
    }
    initialize_agent(
        [{"account_id": "u1", "name": "User1"}],
        [],
        template_mapping
    )
    
    # Mock Jira
    class MockJira:
        async def search(self, jql):
            return {"results": [{"key": "T-1"}, {"key": "T-2"}]}
        
        async def get_issue(self, key):
            if key == "T-1":
                return {"fields": {"summary": "Alert issue", "customfield_10001": "Alert"}}
            return {"fields": {"summary": "Request issue", "customfield_10001": "Standard Request"}}
    
    result = await get_open_support_tickets(MockJira())
    
    assert 'alert_tickets' in result
    assert 'other_tickets' in result
    assert result['total_alerts'] == 1
    assert result['total_other'] == 1


@pytest.mark.asyncio
async def test_check_ticket_template_tool():
    from mcp_server.common.ticket_support_tools import initialize_agent, check_ticket_template
    
    # Initialize agent
    template_mapping = {
        'Support Request': {
            'parent_page': 'Templates',
            'custom_field': 'customfield_10001'
        }
    }
    initialize_agent(
        [{"account_id": "u1", "name": "User1"}],
        [],
        template_mapping
    )
    
    # Mock Jira
    class MockJira:
        async def get_issue(self, key):
            if key == "ALERT-1":
                return {
                    "key": "ALERT-1",
                    "fields": {
                        "issuetype": {"name": "Support Request"},
                        "customfield_10001": "Alert"
                    }
                }
            return {
                "key": "REQ-1",
                "fields": {
                    "issuetype": {"name": "Support Request"},
                    "customfield_10001": "Standard Request"
                }
            }
    
    # Test Alert skip
    result = await check_ticket_template("ALERT-1", MockJira())
    assert result['skipped'] is True
    assert 'Alert' in result['reason']
    
    # Test non-Alert returns context
    result = await check_ticket_template("REQ-1", MockJira())
    assert 'ticket' in result
    assert 'template_config' in result


@pytest.mark.asyncio
async def test_suggest_assignee_tool():
    from mcp_server.common.ticket_support_tools import initialize_agent, suggest_assignee
    
    # Initialize agent
    initialize_agent(
        [{"account_id": "u1", "name": "Alice"}],
        [{"account_id": "u2", "name": "Bob"}],
        {}
    )
    
    # Mock Jira
    class MockJira:
        async def get_issue(self, key):
            return {"key": key, "fields": {"summary": "Test"}}
        
        async def search_by_assignee(self, account_id, excluded_issue_types=None):
            return {"results": [{"key": "T-1"}] if account_id == "u1" else {"results": []}}
        
        async def search(self, jql):
            return {"results": []}
        
        async def get_issue_comments(self, key):
            return {"comments": [{"author": {"displayName": "Test"}, "body": "Comment"}]}
    
    result = await suggest_assignee("TEST-1", MockJira())
    
    assert 'ticket' in result
    assert 'team' in result
    assert 'comments' in result['ticket']
    assert len(result['ticket']['comments']) == 1


@pytest.mark.asyncio
async def test_get_team_workload_tool():
    from mcp_server.common.ticket_support_tools import initialize_agent, get_team_workload
    
    # Initialize agent
    initialize_agent(
        [{"account_id": "u1", "name": "Alice"}],
        [{"account_id": "u2", "name": "Bob"}],
        {}
    )
    
    # Mock Jira
    class MockJira:
        async def search_by_assignee(self, account_id, excluded_issue_types=None):
            return {"results": [{"key": "T-1", "summary": "Task 1"}] if account_id == "u1" else {"results": []}}
        
        async def search(self, jql):
            return {"results": []}
    
    result = await get_team_workload(MockJira())
    
    assert 'primary_team' in result
    assert 'secondary_team' in result
    assert len(result['primary_team']) == 1
    assert len(result['secondary_team']) == 1
    assert result['primary_team'][0]['issue_count'] == 1
