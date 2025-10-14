# Phase 6: Advanced Bitbucket & Jira Attachments

## Overview
Implement 7 remaining tools for Bitbucket advanced features and Jira attachments.

## Tools to Implement

### Jira (1 tool)
1. **add_attachment** - Upload files to issues

### Bitbucket (6 tools)
1. **list_pull_requests_by_author** - PRs by specific user
2. **list_commits_by_author** - Commits by specific user
3. **request_changes** - Request changes on PR
4. **get_branch_restrictions** - Get branch permissions
5. **get_build_status** - Get CI/CD build status
6. **create_webhook** - Set up webhooks

## Implementation Steps

### 1. Add Methods to Providers
- [ ] Add 1 method to `jira_provider.py` (Cloud)
- [ ] Add 1 method to `jira_dc_provider.py` (Data Center)
- [ ] Add 6 methods to `bitbucket_provider.py` (Cloud)
- [ ] Add 6 methods to `bitbucket_dc_provider.py` (Data Center)

### 2. Update Tool Definitions
- [ ] Add 7 new tool definitions to `tools.py`

### 3. Update Router
- [ ] Add routing for 7 new tools in `router.py`

### 4. Update Documentation
- [ ] Update README.md features section

### 5. Add Unit Tests
- [ ] Add 2 tests to `test_jira_provider.py`
- [ ] Add 2 tests to `test_jira_dc_provider.py`
- [ ] Add 12 tests to `test_bitbucket_provider.py`
- [ ] Add 12 tests to `test_bitbucket_dc_provider.py`

### 6. Update Integration Tests
- [ ] Add sample calls to `test_all_tools.py` (Cloud)
- [ ] Add sample calls to `test_all_dc_tools.py` (Data Center)
- [ ] Update tool counts: 82 → 89 total

### 7. Run Tests
- [ ] Run all unit tests (should be 155 total)
- [ ] Run integration tests
- [ ] Verify all tests pass

### 8. Commit Changes
- [ ] Git commit with message: "Phase 6: Add 7 advanced Bitbucket & Jira attachment tools"
- [ ] Push to both remotes

## API Endpoints

### Jira Cloud
- POST `/rest/api/2/issue/{issueKey}/attachments` - Add attachment (multipart/form-data)

### Jira Data Center
- POST `/rest/api/2/issue/{issueKey}/attachments` - Add attachment

### Bitbucket Cloud
- GET `/2.0/repositories/{workspace}/{repo}/pullrequests?q=author.uuid="{uuid}"` - PRs by author
- GET `/2.0/repositories/{workspace}/{repo}/commits?author={username}` - Commits by author
- POST `/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/request-changes` - Request changes
- GET `/2.0/repositories/{workspace}/{repo}/branch-restrictions` - Branch restrictions
- GET `/2.0/repositories/{workspace}/{repo}/commit/{hash}/statuses` - Build status
- POST `/2.0/repositories/{workspace}/{repo}/hooks` - Create webhook

### Bitbucket Data Center
- GET `/rest/api/1.0/projects/{project}/repos/{repo}/pull-requests?filterText=author:{username}` - PRs by author
- GET `/rest/api/1.0/projects/{project}/repos/{repo}/commits?author={username}` - Commits by author
- POST `/rest/api/1.0/projects/{project}/repos/{repo}/pull-requests/{id}/participants/{user}` - Request changes
- GET `/rest/branch-permissions/2.0/projects/{project}/repos/{repo}/restrictions` - Branch restrictions
- GET `/rest/build-status/1.0/commits/{hash}` - Build status
- POST `/rest/api/1.0/projects/{project}/repos/{repo}/webhooks` - Create webhook

## Notes
- **add_attachment** requires multipart/form-data handling
- **create_webhook** requires webhook URL and event configuration
- **get_build_status** integrates with CI/CD systems
- Some Bitbucket DC endpoints may require additional plugins
