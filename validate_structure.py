#!/usr/bin/env python3
"""Validate project structure without requiring credentials"""
import os
import sys

def check_file(path, description):
    exists = os.path.exists(path)
    status = "[OK]" if exists else "[MISSING]"
    print(f"{status} {description}")
    return exists

def main():
    print("=" * 60)
    print("VALIDATING ATLASSIAN MCP SERVER STRUCTURE")
    print("=" * 60)
    
    checks = []
    
    print("\nData Center Providers:")
    checks.append(check_file("mcp_server/datacenter/jira_dc_provider.py", "Jira DC Provider"))
    checks.append(check_file("mcp_server/datacenter/confluence_dc_provider.py", "Confluence DC Provider"))
    checks.append(check_file("mcp_server/datacenter/bitbucket_dc_provider.py", "Bitbucket DC Provider"))
    checks.append(check_file("mcp_server/datacenter/__init__.py", "DC __init__.py"))
    
    print("\nCloud Providers:")
    checks.append(check_file("mcp_server/cloud/jira_provider.py", "Jira Cloud Provider"))
    checks.append(check_file("mcp_server/cloud/confluence_provider.py", "Confluence Cloud Provider"))
    checks.append(check_file("mcp_server/cloud/bitbucket_provider.py", "Bitbucket Cloud Provider"))
    
    print("\nCommon Modules:")
    checks.append(check_file("mcp_server/common/auth.py", "Authentication Module"))
    checks.append(check_file("mcp_server/common/tools.py", "Tools Definitions"))
    
    print("\nData Center Tests:")
    checks.append(check_file("tests/datacenter/test_jira_dc_tools.py", "Jira DC Tests"))
    checks.append(check_file("tests/datacenter/test_confluence_dc_tools.py", "Confluence DC Tests"))
    checks.append(check_file("tests/datacenter/test_bitbucket_dc_tools.py", "Bitbucket DC Tests"))
    checks.append(check_file("tests/datacenter/test_all_dc_tools.py", "All DC Tests"))
    
    print("\nCloud Tests:")
    checks.append(check_file("tests/cloud/test_all_tools.py", "All Cloud Tests"))
    
    print("\nCore Files:")
    checks.append(check_file("lambda_handler.py", "Lambda Handler"))
    checks.append(check_file("template.yaml", "SAM Template"))
    checks.append(check_file("README.md", "README"))
    
    print("\nDocumentation:")
    checks.append(check_file("PHASE2_SUMMARY.md", "Phase 2 Summary"))
    checks.append(check_file("PLATFORM_GUIDE.md", "Platform Guide"))
    checks.append(check_file("DEPLOYMENT_CHECKLIST.md", "Deployment Checklist"))
    
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"RESULT: {passed}/{total} checks passed")
    
    if passed == total:
        print("[OK] All files present - structure is valid!")
        print("\nNext steps:")
        print("  1. Test Cloud deployment: python tests/cloud/test_all_tools.py")
        print("  2. Deploy to AWS: sam build && sam deploy")
        print("  3. Test Data Center when on VPN (use tests/datacenter/)")
        return 0
    else:
        print("✗ Some files are missing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
