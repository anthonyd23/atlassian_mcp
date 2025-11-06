"""MCP tool interface for ticket support agent"""

from typing import Dict, Any, List
from mcp_server.agents.ticket_support_agent import TicketSupportAgent


_agent: TicketSupportAgent = None
_config: Dict[str, Any] = {}


def initialize_agent(primary_team_members, secondary_team_members, 
                     template_mapping=None, confluence_provider=None, 
                     excluded_issue_types=None, workload_statuses=None, 
                     support_jql=None):
    """Initialize the ticket support agent"""
    global _agent, _config
    _agent = TicketSupportAgent(
        primary_team_members, secondary_team_members, 
        template_mapping, confluence_provider, excluded_issue_types, workload_statuses
    )
    _config['support_jql'] = support_jql or 'assignee is EMPTY AND status = Open ORDER BY created DESC'

async def get_open_support_tickets(jira) -> Dict[str, Any]:
    """Get list of open support tickets, separated by type."""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    # Get first issue type from template mapping to find custom field
    first_issue_type = next(iter(_agent.template_mapping.keys())) if _agent.template_mapping else None
    template_config = _agent.template_mapping.get(first_issue_type, {}) if first_issue_type else {}
    custom_field = template_config.get('custom_field')
    
    # Use configured JQL query
    jql = _config.get('support_jql', 'assignee is EMPTY AND status = Open ORDER BY created DESC')
    result = await jira.search(jql)
    
    alert_tickets = []
    other_tickets = []
    
    for t in result.get('results', []):
        key = t.get('key')
        
        # Fetch full issue to get custom field
        full_issue = await jira.get_issue(key)
        fields = full_issue.get('fields', {})
        summary = fields.get('summary', '')
        field_value = fields.get(custom_field)
        
        # Parse field value
        is_alert = False
        if isinstance(field_value, str) and 'Alert' in field_value:
            is_alert = True
        elif isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, dict) and 'Alert' in item.get('selectedOptionLabel', ''):
                    is_alert = True
                    break
        elif isinstance(field_value, dict) and 'Alert' in field_value.get('selectedOptionLabel', ''):
            is_alert = True
        
        ticket_info = {'key': key, 'summary': summary}
        if is_alert:
            alert_tickets.append(ticket_info)
        else:
            other_tickets.append(ticket_info)
    
    return {
        'alert_tickets': alert_tickets,
        'other_tickets': other_tickets,
        'total_alerts': len(alert_tickets),
        'total_other': len(other_tickets),
        'total': len(alert_tickets) + len(other_tickets)
    }

async def check_ticket_template(issue_key: str, jira) -> Dict[str, Any]:
    """Validate single ticket against template. Skips validation for Alert tickets."""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    issue = await jira.get_issue(issue_key)
    fields = issue.get('fields', {})
    issue_type = fields.get('issuetype', {}).get('name', '')
    
    # Check if Alert type - skip validation
    template_config = _agent.template_mapping.get(issue_type, {})
    custom_field = template_config.get('custom_field')
    if custom_field:
        field_value = fields.get(custom_field)
        
        # Check for Alert
        is_alert = False
        if isinstance(field_value, str) and 'Alert' in field_value:
            is_alert = True
        elif isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, dict) and 'Alert' in item.get('selectedOptionLabel', ''):
                    is_alert = True
                    break
        elif isinstance(field_value, dict) and 'Alert' in field_value.get('selectedOptionLabel', ''):
            is_alert = True
        
        if is_alert:
            return {'skipped': True, 'reason': 'Alert tickets do not require template validation'}
    
    context = await _agent.get_template_context(issue)
    
    # Add hints for AI
    context['_ai_hints'] = {
        'next_steps': [
            'Parse custom_field_value to extract ticket type path',
            'For each template_page, call get_child_pages(page_id) to check for nested templates',
            'Match ticket type path against all templates (parent and children)',
            'Call get_page(page_id) on matched template to get full content with URL',
            'Parse ticket description HTML to extract sections',
            'Parse template body HTML to extract expected sections',
            'Compare ticket sections vs template sections'
        ],
        'available_tools': [
            'get_child_pages(page_id) - Get child pages to find nested templates',
            'get_page(page_id) - Get full template content including body HTML and URL'
        ]
    }
    
    return context

async def suggest_assignee(issue_key: str, jira) -> Dict[str, Any]:
    """Suggest assignee for single ticket based on workload."""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    # Get team workload
    issue = await jira.get_issue(issue_key)
    
    async def search_func(account_id, excluded_issue_types=None):
        return await jira.search_by_assignee(account_id, excluded_issue_types=excluded_issue_types)
    
    async def jira_search_func(jql):
        return await jira.search(jql)
    
    team_context = await _agent.get_team_context(search_func, jira_search_func)
    
    # Get comments
    comments_result = await jira.get_issue_comments(issue_key)
    comments = comments_result.get('comments', [])
    
    # Add comments to issue
    issue['comments'] = [{
        'author': c.get('author', {}).get('displayName', 'Unknown'),
        'body': c.get('body', '')
    } for c in comments]
    
    return {
        'ticket': issue,
        'team': team_context,
        '_ai_hints': {
            'recommendation_criteria': [
                '1. ONLY suggest members from primary_team or secondary_team lists',
                '2. NEVER suggest people who commented but are not in team lists',
                '3. Prioritize primary_team over secondary_team',
                '4. Count tickets: prefer members with LOWEST ticket count',
                '5. Context continuity: ONLY if member is in team AND has related work',
                '6. Balance: avoid overloading (>8 tickets is high workload)'
            ]
        }
    }

async def get_team_workload(jira) -> Dict[str, Any]:
    """Expose raw team workload data for AI to analyze"""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    async def search_func(account_id, excluded_issue_types=None):
        return await jira.search_by_assignee(account_id, excluded_issue_types=excluded_issue_types)
    
    async def jira_search_func(jql):
        return await jira.search(jql)
    
    return await _agent.get_team_context(search_func, jira_search_func)
