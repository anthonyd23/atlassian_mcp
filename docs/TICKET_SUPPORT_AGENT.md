# Ticket Support Agent

## Overview

The Ticket Support Agent is a specialized set of 6 MCP tools designed to help AI assistants intelligently manage support ticket workflows. Unlike the standard Atlassian tools that provide direct API access, these agent tools expose structured data and context that enable AI to make informed decisions about ticket assignment, template compliance, and team workload management.

## Philosophy: Data Exposure vs. Decision Making

The agent follows a **"data exposure"** pattern rather than making decisions itself:

- ✅ **Agent Role**: Gather and structure data for AI analysis
- ✅ **AI Role**: Analyze data and make intelligent decisions
- ❌ **Not**: Hardcoded business logic or automatic assignments

This design allows the AI to:
- Apply contextual reasoning beyond simple rules
- Learn from patterns and feedback
- Adapt to changing team dynamics
- Explain its reasoning to users

## Tools

### 1. get_open_support_tickets

**Purpose**: Retrieve and categorize unassigned support tickets

**Returns**:
```json
{
  "alert_tickets": [
    {"key": "PROJ-123", "summary": "Production database down"}
  ],
  "other_tickets": [
    {"key": "PROJ-124", "summary": "Feature request for reporting"}
  ],
  "total_alerts": 1,
  "total_other": 1,
  "total": 2
}
```

**Categorization Logic**:
- Checks custom field value for "Alert" keyword
- Supports string, list, and object field formats
- Separates urgent alerts from standard requests

**Configuration**:
```yaml
ticket_support_agent:
  support_jql: 'assignee is EMPTY AND status = Open ORDER BY created DESC'
  template_mapping:
    "Support Request":
      custom_field: "customfield_10001"  # Field to check for "Alert"
```

### 2. check_ticket_template

**Purpose**: Validate ticket completeness against Confluence templates

**Input**: `issue_key` (e.g., "PROJ-123")

**Returns**:
```json
{
  "ticket": {
    "key": "PROJ-123",
    "fields": { /* all Jira fields */ }
  },
  "template_config": {
    "parent_page": "Support Templates",
    "custom_field": "customfield_10001"
  },
  "custom_field_value": "Standard Request",
  "template_parent": {
    "id": "12345",
    "title": "Support Templates"
  },
  "template_pages": [
    {"id": "12346", "title": "Standard Request Template"},
    {"id": "12347", "title": "Data Request Template"}
  ],
  "_ai_hints": {
    "next_steps": [
      "Parse custom_field_value to extract ticket type",
      "Match ticket type against template_pages",
      "Call get_page(page_id) to get full template content",
      "Compare ticket description vs template sections"
    ]
  }
}
```

**Special Handling**:
- **Alert tickets**: Automatically skipped (no template validation needed)
  ```json
  {"skipped": true, "reason": "Alert tickets do not require template validation"}
  ```

**AI Workflow**:
1. Parse `custom_field_value` to identify ticket type
2. Find matching template in `template_pages`
3. Use `get_page(page_id)` to fetch full template HTML
4. Parse both ticket description and template to extract sections
5. Compare completeness and provide feedback

**Configuration**:
```yaml
ticket_support_agent:
  template_mapping:
    "Support Request":
      parent_page: "Support Templates"  # Confluence page title or ID
      custom_field: "customfield_10001"  # Field containing ticket type
```

### 3. suggest_assignee

**Purpose**: Recommend optimal assignee based on workload and context

**Input**: `issue_key` (e.g., "PROJ-123")

**Returns**:
```json
{
  "ticket": {
    "key": "PROJ-123",
    "fields": { /* all fields */ },
    "comments": [
      {
        "author": "John Doe",
        "body": "I can help with this"
      }
    ]
  },
  "team": {
    "primary_team": [
      {
        "member": {"account_id": "user1", "name": "Alice"},
        "issue_count": 3,
        "issues": [
          {"key": "PROJ-100", "summary": "Task 1"},
          {"key": "PROJ-101", "summary": "Task 2"}
        ]
      }
    ],
    "secondary_team": [ /* similar structure */ ],
    "_debug": {
      "workload_statuses_configured": ["Open", "In Progress"],
      "using_custom_jql": true,
      "sample_jql": "assignee = 'user1' AND status IN ('Open', 'In Progress')"
    }
  },
  "_ai_hints": {
    "recommendation_criteria": [
      "1. ONLY suggest members from primary_team or secondary_team lists",
      "2. NEVER suggest people who commented but are not in team lists",
      "3. Prioritize primary_team over secondary_team",
      "4. Count tickets: prefer members with LOWEST ticket count",
      "5. Context continuity: ONLY if member is in team AND has related work",
      "6. Balance: avoid overloading (>8 tickets is high workload)"
    ]
  }
}
```

**AI Decision Factors**:
1. **Workload**: Prefer team members with fewer assigned tickets
2. **Team Priority**: Primary team before secondary team
3. **Context**: Consider comments and related work (but only for team members)
4. **Balance**: Avoid overloading individuals
5. **Availability**: Check for patterns in issue types

**Configuration**:
```yaml
ticket_support_agent:
  primary_team_members:
    - account_id: "user1"
      name: "Alice"
  secondary_team_members:
    - account_id: "user2"
      name: "Bob"
  excluded_issue_types:
    - "Epic"  # Don't count in workload
  workload_statuses:
    - "Open"
    - "In Progress"
    - "Blocked"
```

### 4. get_team_workload

**Purpose**: Get current workload for all team members

**Returns**:
```json
{
  "primary_team": [
    {
      "member": {"account_id": "user1", "name": "Alice"},
      "issue_count": 5,
      "issues": [
        {"key": "PROJ-100", "summary": "Task 1"},
        {"key": "PROJ-101", "summary": "Task 2"}
      ]
    }
  ],
  "secondary_team": [ /* similar structure */ ],
  "_debug": {
    "workload_statuses_configured": ["Open", "In Progress"],
    "using_custom_jql": true
  }
}
```

**Use Cases**:
- Dashboard/reporting on team capacity
- Identifying overloaded team members
- Planning new ticket assignments
- Workload balancing analysis

### 5. get_expertise_jql

**Purpose**: Construct JQL query to find member's expertise with similar tickets

**Input**: 
- `issue_key` (e.g., "PROJ-123")
- `member_account_id` (team member to check)
- `is_alert` (true for alert tickets, false for others)

**Returns**:
```json
{
  "jql": "assignee = 'user1' AND status = Closed AND issuetype = 'Support Request' AND 'Requested Work' = 'Data Analysis' AND summary ~ 'Daily Report*'",
  "extracted_values": {
    "account_id": "user1",
    "issue_type": "Support Request",
    "custom_field_value": "Data Analysis",
    "summary_prefix": "Daily Report"
  }
}
```

**How It Works**:
1. Extracts ticket fields (issue type, custom field value, summary prefix)
2. Handles cascading select fields (joins with " - ")
3. Replaces placeholders in configured JQL template
4. Returns ready-to-use JQL for `search_jira()`

**Configuration**:
```yaml
ticket_support_agent:
  # Custom field to extract (from template_mapping)
  template_mapping:
    "Support Request":
      custom_field: "customfield_10001"
  
  # JQL templates with placeholders
  alert_expertise_jql: 'assignee = "{account_id}" AND status = Closed AND issuetype = "{issue_type}" AND "Requested Work" = "{custom_field_value}" AND summary ~ "{summary_prefix}*"'
  other_expertise_jql: 'assignee = "{account_id}" AND status = Closed AND issuetype = "{issue_type}" AND "Requested Work" = "{custom_field_value}"'
```

**AI Workflow**:
1. Call `get_expertise_jql(issue_key, member_account_id, is_alert)`
2. Use returned JQL with `search_jira(jql)`
3. Count results to determine expertise level
4. Factor into assignment decision

### 6. check_troubleshooting

**Purpose**: Get troubleshooting documentation and code for alert tickets

**Input**: `issue_key` (e.g., "PROJ-123")

**Returns**:
```json
{
  "ticket": {
    "key": "PROJ-123",
    "summary": "Database Connection Alert",
    "description": "Alert triggered at 3am..."
  },
  "bitbucket_url": "https://git.company.com/projects/PROJ/repos/alerts/browse/sql/db_check.sql",
  "repo_slug": "alerts",
  "file_path": "sql/db_check.sql",
  "branch": "master",
  "troubleshooting_docs": [
    {"id": "12345", "title": "Database Alert Troubleshooting"},
    {"id": "12346", "title": "Connection Issues Guide"}
  ],
  "troubleshooting_parent": {
    "id": "12340",
    "title": "Alert Troubleshooting"
  },
  "doc_count": 2,
  "_ai_hints": {
    "workflow": [
      "1. FIRST: Review the 2 troubleshooting docs already provided",
      "2. Call get_page(page_id) on relevant docs to get full steps",
      "3. THEN: Use repo_slug, file_path, and branch to call get_file_content()",
      "4. Analyze code/SQL to understand alert logic",
      "5. Provide comprehensive guidance combining docs + code analysis"
    ]
  }
}
```

**Features**:
- **Bitbucket URL Extraction**: Parses Git URLs from ticket description (Cloud & Data Center formats)
- **URL Decoding**: Handles HTML entities and URL encoding automatically
- **Troubleshooting Docs**: Fetches all child pages recursively from configured parent
- **Branch Detection**: Auto-detects default branch from repository

**Configuration**:
```yaml
ticket_support_agent:
  # Confluence parent page containing troubleshooting docs
  troubleshooting_parent: "Alert Troubleshooting"  # Page title or ID
```

**AI Workflow**:
1. Call `check_troubleshooting(issue_key)`
2. Review `troubleshooting_docs` list
3. Call `get_page(page_id)` for relevant docs
4. Call `get_file_content(repo_slug, file_path, branch)` to read alert code
5. Analyze SQL/code logic
6. Combine documentation + code insights
7. Provide comprehensive troubleshooting guidance

## Configuration

### Complete Example

```yaml
ticket_support_agent:
  # Team members (Cloud: use account IDs, DC: use usernames)
  primary_team_members:
    - account_id: "712020:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      name: "Alice Smith"
    - account_id: "712020:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
      name: "Bob Jones"
  
  secondary_team_members:
    - account_id: "712020:zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
      name: "Charlie Brown"
  
  # Issue types to exclude from workload calculation
  excluded_issue_types:
    - "Epic"
    - "Initiative"
  
  # Statuses to count in workload (if not specified, uses default JQL)
  workload_statuses:
    - "Open"
    - "In Progress"
    - "Blocked"
    - "Waiting"
  
  # Template mapping for ticket validation
  template_mapping:
    "Support Request":
      parent_page: "Support Request Templates"  # Confluence page title or ID
      custom_field: "customfield_10001"  # Custom field with ticket type
    "Bug Report":
      parent_page: "Bug Report Templates"
      custom_field: "customfield_10002"
  
  # JQL query to find unassigned tickets
  support_jql: 'project = "SUPPORT" AND assignee is EMPTY AND status IN ("Open", "Waiting") ORDER BY created ASC'
```

### Platform-Specific Configuration

**Cloud (Account IDs)**:
```yaml
primary_team_members:
  - account_id: "712020:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    name: "Alice"
```

**Data Center (Usernames)**:
```yaml
primary_team_members:
  - account_id: "asmith"
    name: "Alice"
```

## Workload Calculation

### Default Behavior (No workload_statuses)

Uses Jira's `search_by_assignee` with default JQL:
```jql
assignee = 'user1' AND resolution = Unresolved
```

### Custom Statuses (workload_statuses configured)

Uses custom JQL with specified statuses:
```jql
assignee = 'user1' AND status IN ('Open', 'In Progress', 'Blocked')
```

### Excluded Issue Types

Automatically filters out specified issue types:
```jql
assignee = 'user1' AND status IN ('Open', 'In Progress') 
  AND issuetype != 'Epic' 
  AND issuetype != 'Initiative'
```

## AI Integration Examples

### Example 1: Assign Alert Ticket

**User**: "Assign the open alert tickets"

**AI Workflow**:
1. Call `get_open_support_tickets()` → finds 3 alert tickets
2. For each alert:
   - Call `suggest_assignee(ticket_key)`
   - Analyze team workload
   - Recommend assignee with lowest workload
   - Call `assign_issue(ticket_key, assignee)`
3. Report assignments to user

### Example 2: Check Ticket Completeness

**User**: "Is PROJ-123 complete?"

**AI Workflow**:
1. Call `check_ticket_template("PROJ-123")`
2. If skipped (Alert): "This is an alert ticket, no template required"
3. Otherwise:
   - Parse custom field to get ticket type
   - Find matching template
   - Call `get_page(template_id)` to get template content
   - Compare ticket description vs template sections
   - Report missing sections to user

### Example 3: Team Capacity Check

**User**: "Who has capacity for new tickets?"

**AI Workflow**:
1. Call `get_team_workload()`
2. Analyze issue counts per team member
3. Identify members with <5 tickets (good capacity)
4. Report available team members with current workload

## Lambda Deployment

The ticket support agent is fully integrated into Lambda deployment:

### Environment Variables

```yaml
# In template.yaml
Environment:
  Variables:
    AGENT_PRIMARY_TEAM: '["user1", "user2"]'  # JSON array
    AGENT_SECONDARY_TEAM: '["user3"]'
    AGENT_TEMPLATE_MAPPING: '{"Support Request": {...}}'  # JSON object
    AGENT_EXCLUDED_TYPES: '["Epic"]'
    AGENT_WORKLOAD_STATUSES: '["Open", "In Progress"]'
    AGENT_SUPPORT_JQL: 'assignee is EMPTY AND status = Open'
```

### Deployment Process

```bash
# 1. Configure in config.yaml
ticket_support_agent:
  primary_team_members: [...]
  # ... rest of config

# 2. Deploy
python deploy.py

# 3. Agent automatically initialized in Lambda
```

### Initialization Logic

```python
# lambda_handler.py
if agent_primary or agent_secondary:
    initialize_agent(
        json.loads(agent_primary),
        json.loads(agent_secondary),
        json.loads(template_mapping),
        confluence if confluence.available else None,
        json.loads(excluded_types),
        json.loads(workload_statuses),
        support_jql
    )
```

## Testing

### Unit Tests

```bash
pytest tests/unit/test_ticket_support_agent.py
```

Tests agent logic with mocked Jira/Confluence providers.

### Integration Tests

```bash
python tests/common/test_all_common_tools.py
```

Tests all 6 tools with real Atlassian credentials:
- Platform-agnostic (works with Cloud or Data Center)
- Auto-detects platform from config.yaml
- Requires `ticket_support_agent` configuration

## Best Practices

### Configuration

1. **Team Lists**: Keep updated as team changes
2. **Workload Statuses**: Match your workflow states
3. **Excluded Types**: Exclude non-work items (Epics, Initiatives)
4. **Support JQL**: Tune to match your ticket criteria

### AI Prompts

**Good Prompts**:
- "Assign the open alert tickets to available team members"
- "Check if PROJ-123 follows the template"
- "Who has the lightest workload right now?"

**Avoid**:
- "Assign all tickets to Alice" (bypasses workload analysis)
- "Just assign it to whoever" (no context consideration)

### Monitoring

Track agent tool usage in CloudWatch:
- `get_open_support_tickets` call frequency
- `suggest_assignee` recommendations
- Template validation pass/fail rates
- Team workload distribution over time

## Troubleshooting

### "Agent not configured"

**Cause**: Missing `ticket_support_agent` section in config.yaml

**Fix**:
```yaml
ticket_support_agent:
  primary_team_members: [...]
  secondary_team_members: [...]
```

### "No open tickets found"

**Cause**: `support_jql` returns no results

**Fix**: Verify JQL query in Jira UI, adjust criteria

### "Template pages not found"

**Cause**: Confluence page doesn't exist or wrong ID/title

**Fix**: 
1. Verify page exists in Confluence
2. Check `parent_page` value (can be title or ID)
3. Ensure Confluence provider is available

### "Workload calculation seems wrong"

**Cause**: `workload_statuses` doesn't match your workflow

**Fix**: Update statuses to match your Jira workflow states
