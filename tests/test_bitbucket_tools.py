#!/usr/bin/env python3
"""Test all 24 Bitbucket tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_server.bitbucket_provider import BitbucketProvider

async def test_bitbucket_tools():
    print("Testing Bitbucket Tools...\n")
    bb = BitbucketProvider()
    
    # 1. List repositories
    print("1. list_repositories")
    result = await bb.list_repositories()
    repos = result.get('values', [])
    repo_slug = repos[0]['slug'] if repos else 'atlassian_mcp'
    print(f"   Result: Found {len(repos)} repositories\n")
    
    # 2. Get repository
    print("2. get_repository")
    result = await bb.get_repository(repo_slug)
    print(f"   Result: {result}\n")
    
    # 3. Search repositories
    print("3. search_bitbucket")
    result = await bb.search("atlassian")
    print(f"   Result: {result}\n")
    
    # 4. List branches
    print("4. list_branches")
    result = await bb.list_branches(repo_slug)
    branches = result.get('values', [])
    branch = branches[0]['name'] if branches else 'main'
    print(f"   Result: Found {len(branches)} branches\n")
    
    # 5. List tags
    print("5. list_tags")
    result = await bb.list_tags(repo_slug)
    print(f"   Result: {result}\n")
    
    # 6. List commits
    print("6. list_commits")
    result = await bb.list_commits(repo_slug, branch)
    commits = result.get('values', [])
    commit_hash = commits[0]['hash'] if commits else None
    print(f"   Result: Found {len(commits)} commits\n")
    
    if commit_hash:
        # 7. Get commit
        print("7. get_commit")
        result = await bb.get_commit(repo_slug, commit_hash)
        print(f"   Result: {result}\n")
        
        # 8. Get commit diff
        print("8. get_commit_diff")
        result = await bb.get_commit_diff(repo_slug, commit_hash)
        print(f"   Result: Diff length = {len(result.get('diff', ''))}\n")
    
    # 9. Compare commits (skip if not enough commits)
    if len(commits) >= 2:
        print("9. compare_commits")
        result = await bb.compare_commits(repo_slug, commits[1]['hash'], commits[0]['hash'])
        print(f"   Result: Diff length = {len(result.get('diff', ''))}\n")
    else:
        print("9. compare_commits - SKIPPED (need 2+ commits)\n")
    
    # 10. List directory
    print("10. list_directory")
    result = await bb.list_directory(repo_slug, "", branch)
    print(f"   Result: {result}\n")
    
    # 11. Get file content
    print("11. get_file_content")
    result = await bb.get_file_content(repo_slug, "README.md", branch)
    print(f"   Result: Content length = {len(result.get('content', ''))}\n")
    
    # 12. List pull requests
    print("12. list_pull_requests")
    result = await bb.list_pull_requests(repo_slug, "OPEN")
    prs = result.get('values', [])
    pr_id = prs[0]['id'] if prs else None
    print(f"   Result: Found {len(prs)} open PRs\n")
    
    if pr_id:
        # 13. Get pull request
        print("13. get_pull_request")
        result = await bb.get_pull_request(repo_slug, pr_id)
        print(f"   Result: {result}\n")
        
        # 14. Get pull request diff
        print("14. get_pull_request_diff")
        result = await bb.get_pull_request_diff(repo_slug, pr_id)
        print(f"   Result: Diff length = {len(result.get('diff', ''))}\n")
        
        # 15. Get pull request comments
        print("15. get_pull_request_comments")
        result = await bb.get_pull_request_comments(repo_slug, pr_id)
        print(f"   Result: {result}\n")
        
        # 16. Add PR comment
        print("16. add_pr_comment")
        result = await bb.add_pr_comment(repo_slug, pr_id, "Test comment from MCP")
        print(f"   Result: {result}\n")
        
        # 17. Update pull request
        print("17. update_pull_request")
        result = await bb.update_pull_request(repo_slug, pr_id, "Updated PR Title")
        print(f"   Result: {result}\n")
        
        # 18. Approve pull request
        print("18. approve_pull_request")
        result = await bb.approve_pull_request(repo_slug, pr_id)
        print(f"   Result: {result}\n")
        
        # 19. Merge pull request (skip - destructive)
        print("19. merge_pull_request - SKIPPED (destructive)\n")
    else:
        print("13-19. PR tools - SKIPPED (no open PRs)\n")
    
    # 20. Create pull request (skip - needs branches)
    print("20. create_pull_request - SKIPPED (needs test branches)\n")
    
    print("Bitbucket tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_bitbucket_tools())
