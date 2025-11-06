# Testing Guide

## Overview

The Atlassian MCP Server includes comprehensive testing at multiple levels:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test real API interactions with Atlassian services
- **Platform-Specific Tests**: Separate test suites for Cloud and Data Center

## Test Structure

```
tests/
├── unit/                    # Unit tests (mocked dependencies)
│   ├── test_jira_provider.py
│   ├── test_confluence_provider.py
│   ├── test_bitbucket_provider.py
│   ├── test_router.py
│   ├── test_validation.py
│   └── test_ticket_support_agent.py
├── cloud/                   # Cloud integration tests
│   └── test_all_cloud_tools.py
├── datacenter/              # Data Center integration tests
│   └── test_all_dc_tools.py
└── common/                  # Platform-agnostic tests
    └── test_all_common_tools.py
```

## Running Tests

### Unit Tests

Unit tests use mocked dependencies and don't require live credentials:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_validation.py

# Run with verbose output
pytest tests/unit/ -v
```

### Integration Tests

Integration tests connect to real Atlassian instances and require valid credentials in `config.yaml`.

#### Cloud Integration Tests

Tests all 94 Cloud tools (31 Jira + 30 Confluence + 33 Bitbucket):

```bash
python tests/cloud/test_all_cloud_tools.py
```

**Platform Detection:**
- Forces Cloud platform by loading Cloud credentials from config.yaml
- Clears Data Center environment variables to ensure isolation
- Auto-creates test resources (issues, pages, branches)
- Cleans up resources after testing

**Test Coverage:**
- ✅ All Jira Cloud tools
- ✅ All Confluence Cloud tools  
- ✅ All Bitbucket Cloud tools
- ✅ Write operations (create, update, delete)
- ✅ Read operations (get, list, search)

#### Data Center Integration Tests

Tests all 94 Data Center tools (31 Jira + 30 Confluence + 33 Bitbucket):

```bash
python tests/datacenter/test_all_dc_tools.py
```

**Platform Detection:**
- Forces Data Center platform by loading DC credentials from config.yaml
- Clears Cloud environment variables to ensure isolation
- Handles DC-specific authentication (PAT tokens)
- Adapts to server configuration differences

**Test Coverage:**
- ✅ All Jira Data Center tools
- ✅ All Confluence Data Center tools
- ✅ All Bitbucket Data Center tools
- ✅ Handles server-specific limitations gracefully

**Optional Test Parameters:**

```bash
# Test specific service only
python tests/datacenter/test_all_dc_tools.py --service jira

# Use existing issue (skip create/delete)
python tests/datacenter/test_all_dc_tools.py --jira-issue PROJ-123

# Use existing Confluence page
python tests/datacenter/test_all_dc_tools.py --confluence-page 12345

# Use existing Bitbucket repo
python tests/datacenter/test_all_dc_tools.py --bitbucket-repo my-repo
```

#### Common Agent Tests

Tests 4 ticket support agent tools (platform-agnostic):

```bash
python tests/common/test_all_common_tools.py
```

**Platform Detection:**
- Auto-detects platform using same logic as main.py:
  1. Checks `deployment_type` in config.yaml
  2. Falls back to DC credentials detection
  3. Defaults to Cloud if neither specified
- Imports appropriate providers based on detected platform
- Requires `ticket_support_agent` configuration in config.yaml

**Test Coverage:**
- ✅ get_open_support_tickets
- ✅ check_ticket_template
- ✅ suggest_assignee
- ✅ get_team_workload

## Platform Detection Logic

All tests and the main server use consistent platform detection:

### Priority Order

1. **DEPLOYMENT_TYPE environment variable** (highest priority)
2. **deployment_type in config.yaml**
3. **Data Center credentials detection** (presence of DC-specific env vars)
4. **Default to Cloud** (lowest priority)

### Configuration Examples

**Explicit Cloud:**
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://company.atlassian.net
  atlassian_username: user@company.com
  atlassian_api_token: token
```

**Explicit Data Center:**
```yaml
deployment_type: datacenter
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: token
```

**Auto-Detection (DC):**
```yaml
# No deployment_type specified
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: token
# Will detect as Data Center due to DC credentials
```

## Test Output Format

### Success Output

```
============================================================
JIRA CLOUD (31 tools available)
============================================================
  [PASS] list_projects
  [PASS] search_jira
  [PASS] create_issue (created PROJ-123 in project PROJ)
  [PASS] get_issue
  ...
  Tested: 30 of 31 Jira tools

============================================================
SUMMARY
============================================================
Tools tested: 80 of 94 available
Passed:       77
Failed:       0
Exceptions:   3 (expected failures due to server config)
Skipped:      14

[PASS] ALL TESTS PASSED
```

### Test Status Indicators

- **[PASS]**: Tool executed successfully
- **[FAIL]**: Unexpected error occurred
- **[EXCEPT]**: Expected failure (server config, permissions, etc.)
- **[SKIP]**: Test skipped (missing dependencies, optional features)
- **[INFO]**: Informational message about test execution

## Test Configuration

### Required Configuration

**For Cloud Tests:**
```yaml
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  bitbucket_workspace: your-workspace  # optional
  bitbucket_api_token: your-token      # optional
```

**For Data Center Tests:**
```yaml
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-token
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-token
  bitbucket_base_url: https://git.company.com
  bitbucket_pat_token: your-token
  bitbucket_project: PROJECT_KEY
```

**For Agent Tests:**
```yaml
ticket_support_agent:
  primary_team_members:
    - account_id: "user1"
      name: "User One"
  secondary_team_members:
    - account_id: "user2"
      name: "User Two"
  template_mapping:
    "Support Request":
      parent_page: "Templates"
      custom_field: "customfield_10001"
  support_jql: 'assignee is EMPTY AND status = Open'
```

## Test Isolation

### Cloud Tests
- Clears all Data Center environment variables
- Forces Cloud platform detection
- Uses Cloud-specific authentication (username + API token)

### Data Center Tests
- Clears all Cloud environment variables
- Forces Data Center platform detection
- Uses DC-specific authentication (PAT tokens)

### Common Tests
- Uses auto-detection logic
- Works with either platform
- Adapts to available configuration

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/unit/
```

## Best Practices

### Writing New Tests

1. **Unit Tests**: Mock external dependencies
   ```python
   @pytest.fixture
   def mock_jira():
       return MockJiraProvider()
   ```

2. **Integration Tests**: Use real credentials, clean up resources
   ```python
   # Create resource
   result = await jira.create_issue(...)
   test_issue = result['key']
   
   # Test operations
   ...
   
   # Cleanup
   await jira.delete_issue(test_issue)
   ```

3. **Platform-Specific**: Force platform detection
   ```python
   # Force Cloud
   os.environ['ATLASSIAN_BASE_URL'] = 'https://...'
   os.environ.pop('JIRA_PAT_TOKEN', None)
   ```

### Test Data Management

- Use descriptive test resource names: `[TEST] Integration Test Issue`
- Clean up all created resources
- Handle cleanup failures gracefully
- Log all resource creation for debugging

### Error Handling

- Distinguish between expected and unexpected failures
- Provide helpful error messages
- Include server response details in failures
- Suggest fixes for common issues

## Troubleshooting

### Common Issues

**"config.yaml not found"**
```bash
cp config.template.yaml config.yaml
# Edit config.yaml with your credentials
```

**"Platform not configured"**
- Ensure either `cloud` or `datacenter` section is filled in config.yaml
- Check that credentials are valid

**"Tests skipped"**
- Some tests require specific server features (sprints, webhooks, etc.)
- This is normal - check EXCEPT/SKIP messages for details

**"Connection refused"**
- Verify base URLs are correct
- Check network connectivity
- Ensure VPN is connected (for Data Center)

## Test Metrics

### Coverage Goals
- Unit tests: >80% code coverage
- Integration tests: All 98 tools tested
- Platform tests: Both Cloud and Data Center validated

### Performance Benchmarks
- Unit tests: <5 seconds total
- Integration tests: <2 minutes per platform
- Agent tests: <30 seconds
