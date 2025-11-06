"""MCP tool interface for ticket support agent"""

from typing import Dict, Any, List
from mcp_server.agents.ticket_support_agent import TicketSupportAgent


_agent: TicketSupportAgent = None
_config: Dict[str, Any] = {}


def initialize_agent(primary_team_members, secondary_team_members, 
                     template_mapping=None, confluence_provider=None, 
                     excluded_issue_types=None, workload_statuses=None, 
                     support_jql=None, troubleshooting_parent=None,
                     alert_expertise_jql=None, other_expertise_jql=None):
    """Initialize the ticket support agent"""
    global _agent, _config
    _agent = TicketSupportAgent(
        primary_team_members, secondary_team_members, 
        template_mapping, confluence_provider, excluded_issue_types, workload_statuses
    )
    _config['support_jql'] = support_jql or 'assignee is EMPTY AND status = Open ORDER BY created DESC'
    _config['confluence_provider'] = confluence_provider
    _config['troubleshooting_parent'] = troubleshooting_parent
    _config['alert_expertise_jql'] = alert_expertise_jql
    _config['other_expertise_jql'] = other_expertise_jql
    # Get custom field from template_mapping
    if template_mapping:
        first_issue_type = next(iter(template_mapping.keys()))
        _config['custom_field'] = template_mapping[first_issue_type].get('custom_field')
    else:
        _config['custom_field'] = None

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
    
    result = {
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
            ],
            'custom_field_value': f"{_config.get('custom_field', 'N/A')} value: {issue.get('fields', {}).get(_config.get('custom_field', ''))}"
        }
    }
    
    # Add expertise JQL queries if configured
    if _config.get('alert_expertise_jql'):
        result['alert_expertise_jql'] = _config['alert_expertise_jql']
    if _config.get('other_expertise_jql'):
        result['other_expertise_jql'] = _config['other_expertise_jql']
    
    return result

async def get_team_workload(jira) -> Dict[str, Any]:
    """Expose raw team workload data for AI to analyze"""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    async def search_func(account_id, excluded_issue_types=None):
        return await jira.search_by_assignee(account_id, excluded_issue_types=excluded_issue_types)
    
    async def jira_search_func(jql):
        return await jira.search(jql)
    
    return await _agent.get_team_context(search_func, jira_search_func)

async def get_expertise_jql(issue_key: str, member_account_id: str, is_alert: bool, jira) -> Dict[str, Any]:
    """Construct expertise JQL query with proper field extraction."""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    # Get the appropriate JQL template
    jql_template = _config.get('alert_expertise_jql' if is_alert else 'other_expertise_jql')
    if not jql_template:
        return {"error": "Expertise JQL not configured"}
    
    # Get custom field from template_mapping
    custom_field = _config.get('custom_field')
    if not custom_field:
        return {"error": "Custom field not configured in template_mapping"}
    
    # Get ticket to extract field values
    issue = await jira.get_issue(issue_key)
    fields = issue.get('fields', {})
    
    # Extract issue type
    issue_type = fields.get('issuetype', {}).get('name', '')
    
    # Extract custom field value (handles string, list, or dict)
    import json
    field_value = fields.get(custom_field)
    custom_field_text = ''
    if isinstance(field_value, str):
        try:
            parsed = json.loads(field_value)
            if isinstance(parsed, list):
                labels = [item.get('selectedOptionLabel', '') for item in parsed if isinstance(item, dict)]
                custom_field_text = ' - '.join(labels)
            else:
                custom_field_text = field_value
        except:
            custom_field_text = field_value
    elif isinstance(field_value, list):
        labels = [item.get('selectedOptionLabel', '') for item in field_value if isinstance(item, dict)]
        custom_field_text = ' - '.join(labels)
    elif isinstance(field_value, dict):
        custom_field_text = field_value.get('selectedOptionLabel', '')
    
    # Extract summary prefix (before first colon)
    summary = fields.get('summary', '')
    summary_prefix = summary.split(':')[0].strip() if ':' in summary else summary
    
    # Replace placeholders
    jql = jql_template.replace('{account_id}', member_account_id)
    jql = jql.replace('{issue_type}', issue_type)
    jql = jql.replace('{custom_field_value}', custom_field_text)
    jql = jql.replace('{summary_prefix}', summary_prefix)
    
    # Legacy placeholder support (for backward compatibility)
    jql = jql.replace('{requested_work}', custom_field_text)
    
    return {
        'jql': jql,
        'extracted_values': {
            'account_id': member_account_id,
            'issue_type': issue_type,
            'custom_field_value': custom_field_text,
            'summary_prefix': summary_prefix
        }
    }

async def check_troubleshooting(issue_key: str, jira, bitbucket=None) -> Dict[str, Any]:
    """Get troubleshooting documentation for alert ticket from configured Confluence parent page."""
    if not _agent:
        return {"error": "Ticket support agent not configured"}
    
    troubleshooting_parent = _config.get('troubleshooting_parent')
    if not troubleshooting_parent:
        # Still return ticket info and bitbucket URL even if no docs configured
        issue = await jira.get_issue(issue_key)
        fields = issue.get('fields', {})
        description = fields.get('description', '')
        
        import re
        import html
        from urllib.parse import unquote
        
        bitbucket_url = None
        repo_slug = None
        file_path = None
        branch = None
        
        if description:
            # Decode HTML entities first
            description = html.unescape(description)
            
            bitbucket_patterns = [
                r'https?://(?:[^\s<>"]*(?:bitbucket|git)[^\s<>"]+)',  # Domain contains bitbucket/git
                r'href=["\']([^"\'>]+(?:bitbucket|git)[^"\'>]+)["\']',  # HTML href
            ]
            
            for pattern in bitbucket_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                if matches:
                    bitbucket_url = matches[0]
                    break
            
            if bitbucket_url:
                # Decode URL encoding
                bitbucket_url = unquote(bitbucket_url)
                # Parse URL to extract repo_slug and file_path (handles both Cloud and Data Center formats)
                browse_match = re.search(r'/repos/([^/]+)/browse/(.+?)(?:\?|#|$|<)', bitbucket_url)
                if browse_match:
                    repo_slug = browse_match.group(1)
                    file_path = browse_match.group(2).rstrip()
                else:
                    # Try Data Center format with project
                    dc_match = re.search(r'/projects/[^/]+/repos/([^/]+)/browse/(.+?)(?:\?|#|$|<)', bitbucket_url)
                    if dc_match:
                        repo_slug = dc_match.group(1)
                        file_path = dc_match.group(2).rstrip()
                    
                    # Get default branch from repository
                    if bitbucket and repo_slug:
                        try:
                            repo_info = await bitbucket.get_repository(repo_slug)
                            branch = repo_info.get('defaultBranch', {}).get('displayId', 'master')
                        except:
                            branch = 'master'  # fallback
        
        return {
            'ticket': {
                'key': issue_key,
                'summary': fields.get('summary', ''),
                'description': description
            },
            'bitbucket_url': bitbucket_url,
            'repo_slug': repo_slug,
            'file_path': file_path,
            'branch': branch,
            'troubleshooting_docs': [],
            'note': 'Troubleshooting parent page not configured, but ticket details and Bitbucket URL (if present) are provided'
        }
    
    issue = await jira.get_issue(issue_key)
    context = await _agent.get_troubleshooting_context(issue, troubleshooting_parent)
    
    # Get default branch if repo_slug is present
    if bitbucket and context.get('repo_slug'):
        try:
            repo_info = await bitbucket.get_repository(context['repo_slug'])
            context['branch'] = repo_info.get('defaultBranch', {}).get('displayId', 'master')
        except:
            context['branch'] = 'master'  # fallback
    
    # Add hints for AI
    doc_count = len(context.get('troubleshooting_docs', []))
    context['_ai_hints'] = {
        'workflow': [
            f"1. FIRST: Review the {doc_count} troubleshooting docs already provided in troubleshooting_docs list",
            '2. Call get_page(page_id) on relevant docs to get full troubleshooting steps',
            '3. THEN: Use repo_slug, file_path, and branch to call get_file_content() to read the alert code',
            '4. Analyze code/SQL to understand alert logic and supplement documentation',
            '5. If SQL queries present, optionally use @gpprod to get schemas and run diagnostics',
            '6. Provide comprehensive guidance combining docs + code analysis'
        ],
        'note': 'Troubleshooting docs are pre-fetched from configured parent page - no need to search Confluence'
    }
    
    return context
