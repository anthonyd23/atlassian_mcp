"""Ticket Support Agent - exposes data for AI reasoning"""

from typing import Dict, List, Optional


def _escape_jql(value: str) -> str:
    """Escape single quotes in JQL values by doubling them"""
    return value.replace("'", "''")


class TicketSupportAgent:
    """Minimal agent that exposes data for AI clients to make decisions"""
    
    def __init__(self, primary_team_members: List[Dict], secondary_team_members: List[Dict], 
                 template_mapping: Optional[Dict] = None, confluence_provider=None, 
                 excluded_issue_types: List[str] = None, workload_statuses: List[str] = None):
        """Initialize agent with team configuration"""
        self.primary_team_members = primary_team_members
        self.secondary_team_members = secondary_team_members
        self.team_members = primary_team_members + secondary_team_members
        self.template_mapping = template_mapping or {}
        self.confluence_provider = confluence_provider
        self.excluded_issue_types = excluded_issue_types or []
        self.workload_statuses = workload_statuses
    
    async def get_template_context(self, issue_data: Dict) -> Dict:
        """Expose raw ticket and template data for AI to analyze"""
        import json
        
        fields = issue_data.get('fields', {})
        issue_type = fields.get('issuetype', {}).get('name', '')
        
        # Return raw ticket data
        context = {
            'ticket': {
                'key': issue_data.get('key'),
                'fields': fields  # All fields for AI to inspect
            },
            'template_config': None,
            'template_pages': []
        }
        
        # Get template config if exists
        template_config = self.template_mapping.get(issue_type) if self.template_mapping else None
        if template_config:
            context['template_config'] = template_config
            
            # Parse custom field if specified
            custom_field = template_config.get('custom_field')
            if custom_field:
                field_value = fields.get(custom_field)
                if isinstance(field_value, str) and field_value.startswith('['):
                    try:
                        field_value = json.loads(field_value)
                    except:
                        pass
                context['custom_field_value'] = field_value
            
            # Get Confluence template pages if provider available
            if self.confluence_provider:
                parent_page_id = template_config.get('parent_page')
                if parent_page_id:
                    try:
                        parent = await self.confluence_provider.get_page_by_title_or_id(parent_page_id)
                        if parent:
                            # Return lightweight parent info (no body) - AI can fetch full content if needed
                            context['template_parent'] = {
                                'id': parent.get('id'),
                                'title': parent.get('title')
                            }
                            
                            children = await self.confluence_provider.get_child_pages(parent['id'])
                            # Return lightweight list (id, title only) - AI can fetch full content on-demand
                            template_pages = []
                            for child in children.get('results', []):
                                template_pages.append({
                                    'id': child.get('id'),
                                    'title': child.get('title')
                                })
                            context['template_pages'] = template_pages
                            context['template_page_count'] = len(template_pages)
                    except Exception as e:
                        context['error'] = str(e)
        
        return context

    async def get_troubleshooting_context(self, issue_data: Dict, troubleshooting_parent: str) -> Dict:
        """Expose troubleshooting docs for AI to provide guidance"""
        import re
        import html
        from urllib.parse import unquote
        
        fields = issue_data.get('fields', {})
        description = fields.get('description', '')
        
        # Extract Bitbucket URL from description and parse it
        bitbucket_url = None
        repo_slug = None
        file_path = None
        
        if description:
            # Decode HTML entities first
            description = html.unescape(description)
            
            # Match Bitbucket/Git URLs (handle both plain text and HTML, Cloud and Data Center)
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
                # Data Center: /projects/PROJECT/repos/REPO/browse/path
                # Cloud: /repos/REPO/browse/path
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
        
        context = {
            'ticket': {
                'key': issue_data.get('key'),
                'summary': fields.get('summary', ''),
                'description': description
            },
            'bitbucket_url': bitbucket_url,
            'repo_slug': repo_slug,
            'file_path': file_path,
            'branch': None,  # Will be populated by wrapper if bitbucket provider available
            'troubleshooting_docs': []
        }
        
        # Get troubleshooting docs from configured parent page
        if self.confluence_provider and troubleshooting_parent:
            try:
                # Try as page ID first
                if troubleshooting_parent.isdigit():
                    parent = await self.confluence_provider.get_page(troubleshooting_parent)
                else:
                    # Search by title using CQL
                    search_result = await self.confluence_provider.cql_search(f'title = "{troubleshooting_parent}" AND type = page', limit=1)
                    results = search_result.get('results', [])
                    parent = results[0].get('content') if results else None
                
                if parent and 'error' not in parent:
                    parent_id = parent.get('id')
                    context['troubleshooting_parent'] = {
                        'id': parent_id,
                        'title': parent.get('title')
                    }
                    
                    # Try get_descendants first (works in Cloud), fall back to recursive (Data Center)
                    descendants = await self.confluence_provider.get_descendants(parent_id)
                    if 'error' not in descendants and descendants.get('results'):
                        for child in descendants['results']:
                            context['troubleshooting_docs'].append({
                                'id': child.get('id'),
                                'title': child.get('title')
                            })
                    else:
                        # Recursive approach for Data Center
                        async def get_all_children(page_id, docs_list):
                            children = await self.confluence_provider.get_child_pages(page_id)
                            for child in children.get('results', []):
                                docs_list.append({
                                    'id': child.get('id'),
                                    'title': child.get('title')
                                })
                                await get_all_children(child.get('id'), docs_list)
                        
                        await get_all_children(parent_id, context['troubleshooting_docs'])
                    
                    context['doc_count'] = len(context['troubleshooting_docs'])
            except Exception as e:
                context['error'] = str(e)
        
        return context
    
    async def get_team_context(self, search_by_assignee_func, jira_search_func=None) -> Dict:
        """Expose raw team workload data for AI to analyze"""
        team_data = []
        
        for member in self.team_members:
            account_id = member['account_id']
            try:
                # Use custom JQL if workload_statuses specified
                if self.workload_statuses and jira_search_func:
                    escaped_account_id = _escape_jql(account_id)
                    escaped_statuses = "', '".join(_escape_jql(s) for s in self.workload_statuses)
                    jql = f"assignee = '{escaped_account_id}' AND status IN ('{escaped_statuses}')"
                    if self.excluded_issue_types:
                        for issue_type in self.excluded_issue_types:
                            escaped_type = _escape_jql(issue_type)
                            jql += f" AND issuetype != '{escaped_type}'"
                    result = await jira_search_func(jql)
                    self._last_jql = jql
                else:
                    result = await search_by_assignee_func(account_id, excluded_issue_types=self.excluded_issue_types)
                
                issues = result.get('results', [])
                
                # Return only essential fields to avoid exceeding character limit
                lightweight_issues = [{
                    'key': i.get('key'),
                    'summary': i.get('summary', i.get('fields', {}).get('summary', ''))
                } for i in issues]
                
                team_data.append({
                    'member': member,
                    'issue_count': len(issues),
                    'issues': lightweight_issues
                })
            except Exception as e:
                team_data.append({
                    'member': member,
                    'error': str(e)
                })
        
        return {
            'primary_team': [d for d in team_data if d['member'] in self.primary_team_members],
            'secondary_team': [d for d in team_data if d['member'] in self.secondary_team_members],
            '_debug': {
                'workload_statuses_configured': self.workload_statuses,
                'using_custom_jql': bool(self.workload_statuses and jira_search_func),
                'sample_jql': getattr(self, '_last_jql', 'N/A')
            }
        }
