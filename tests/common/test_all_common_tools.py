#!/usr/bin/env python3
"""Test ticket support agent tools (platform-agnostic)"""
import asyncio
import os
import sys
import yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_config_and_detect_platform():
    """Load config and detect which platform to use"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.yaml')
    
    if not os.path.exists(config_path):
        print("\nError: config.yaml not found!")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Detect platform: deployment_type > DC credentials > cloud
    deployment_type = config.get('deployment_type', '').lower()
    if deployment_type:
        use_datacenter = (deployment_type == 'datacenter')
    else:
        dc_config = config.get('datacenter', {})
        has_dc = bool(dc_config.get('jira_base_url') or dc_config.get('confluence_base_url'))
        use_datacenter = has_dc
    
    # Load appropriate credentials
    if use_datacenter:
        dc = config.get('datacenter', {})
        os.environ['JIRA_BASE_URL'] = dc.get('jira_base_url', '')
        os.environ['JIRA_PAT_TOKEN'] = dc.get('jira_pat_token', '')
        os.environ['CONFLUENCE_BASE_URL'] = dc.get('confluence_base_url', '')
        os.environ['CONFLUENCE_PAT_TOKEN'] = dc.get('confluence_pat_token', '')
        print(f"Using Data Center platform")
        return 'datacenter', config
    else:
        cloud = config.get('cloud', {})
        os.environ['ATLASSIAN_BASE_URL'] = cloud.get('atlassian_base_url', '')
        os.environ['ATLASSIAN_USERNAME'] = cloud.get('atlassian_username', '')
        os.environ['ATLASSIAN_API_TOKEN'] = cloud.get('atlassian_api_token', '')
        print(f"Using Cloud platform")
        return 'cloud', config

async def test_ticket_support_tools():
    """Test 4 ticket support agent tools"""
    platform, config = load_config_and_detect_platform()
    
    agent_config = config.get('ticket_support_agent', {})
    if not agent_config.get('primary_team_members') or not agent_config.get('secondary_team_members'):
        print("  [SKIP] Ticket support agent not configured in config.yaml")
        return 0, 0, 0, 4
    
    # Import appropriate providers based on platform
    if platform == 'datacenter':
        from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
        from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
        jira = JiraDCProvider()
        confluence = ConfluenceDCProvider()
    else:
        from mcp_server.cloud.jira_provider import JiraProvider
        from mcp_server.cloud.confluence_provider import ConfluenceProvider
        jira = JiraProvider()
        confluence = ConfluenceProvider()
    
    if not jira.available:
        print("  [SKIP] Jira not available (required for ticket support agent)")
        return 0, 0, 0, 4
    
    # Initialize agent
    from mcp_server.common.ticket_support_tools import initialize_agent
    initialize_agent(
        agent_config.get('primary_team_members', []),
        agent_config.get('secondary_team_members', []),
        agent_config.get('template_mapping'),
        confluence if confluence.available else None,
        agent_config.get('excluded_issue_types', []),
        agent_config.get('workload_statuses'),
        agent_config.get('support_jql')
    )
    
    passed = failed = exceptions = skipped = 0
    
    from mcp_server.common.ticket_support_tools import (
        get_open_support_tickets,
        check_ticket_template,
        suggest_assignee,
        get_team_workload
    )
    
    # Test 1: get_open_support_tickets
    result = await get_open_support_tickets(jira)
    if 'error' in result:
        print(f"  [FAIL] get_open_support_tickets: {result['error']}")
        failed += 1
    else:
        total = result.get('total', 0)
        alert_count = result.get('total_alerts', 0)
        other_count = result.get('total_other', 0)
        print(f"  [PASS] get_open_support_tickets (found {total} tickets: {alert_count} alerts, {other_count} other)")
        passed += 1
    
    # Test 2: get_team_workload
    result = await get_team_workload(jira)
    if 'error' in result:
        print(f"  [FAIL] get_team_workload: {result['error']}")
        failed += 1
    else:
        print(f"  [PASS] get_team_workload")
        passed += 1
    
    # Test 3-4: check_ticket_template and suggest_assignee (need an issue)
    tickets = await get_open_support_tickets(jira)
    if tickets.get('alert_tickets') or tickets.get('other_tickets'):
        test_issue = (tickets.get('alert_tickets') or tickets.get('other_tickets'))[0]['key']
        
        result = await check_ticket_template(test_issue, jira)
        if 'error' in result:
            print(f"  [FAIL] check_ticket_template: {result['error']}")
            failed += 1
        else:
            print(f"  [PASS] check_ticket_template")
            passed += 1
        
        result = await suggest_assignee(test_issue, jira)
        if 'error' in result:
            print(f"  [FAIL] suggest_assignee: {result['error']}")
            failed += 1
        else:
            print(f"  [PASS] suggest_assignee")
            passed += 1
    else:
        print(f"  [SKIP] check_ticket_template (no open tickets)")
        print(f"  [SKIP] suggest_assignee (no open tickets)")
        skipped += 2
    
    return passed, failed, exceptions, skipped

if __name__ == "__main__":
    print("=" * 60)
    print("TICKET SUPPORT AGENT TEST")
    print("=" * 60)
    
    async def run_tests():
        print("\n" + "=" * 60)
        print("TICKET SUPPORT AGENT (4 tools available)")
        print("=" * 60)
        passed, failed, exceptions, skipped = await test_ticket_support_tools()
        print(f"  Tested: {passed + failed + exceptions} of 4 Ticket Support tools")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Tools tested: {passed + failed + exceptions} of 4 available")
        print(f"Passed:       {passed}")
        print(f"Failed:       {failed}")
        print(f"Exceptions:   {exceptions}")
        print(f"Skipped:      {skipped}")
        
        if failed > 0:
            print("\n[FAIL] SOME TESTS FAILED")
            return 1
        elif passed + exceptions == 0:
            print("\n[SKIP] NO TESTS RAN")
            return 0
        else:
            print("\n[PASS] ALL TESTS PASSED")
            return 0
    
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
