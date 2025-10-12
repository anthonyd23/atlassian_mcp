#!/usr/bin/env python3
import os
import requests
import json

username = os.getenv('ATLASSIAN_USERNAME')
token = os.getenv('ATLASSIAN_API_TOKEN')
base_url = os.getenv('ATLASSIAN_BASE_URL')

print(f"Testing Jira API...")
print(f"Base URL: {base_url}")
print(f"Username: {username}\n")

import base64
credentials = f"{username}:{token}"
encoded = base64.b64encode(credentials.encode()).decode()
headers = {
    'Authorization': f'Basic {encoded}',
    'Content-Type': 'application/json'
}

# Test 1: Get myself
print("1. Testing /rest/api/2/myself...")
url = f"{base_url}/rest/api/2/myself"
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}\n")

# Test 2: Get projects
print("2. Testing /rest/api/2/project...")
url = f"{base_url}/rest/api/2/project"
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}\n")

# Test 3: Search with simple JQL
print("3. Testing /rest/api/2/search...")
url = f"{base_url}/rest/api/2/search"
payload = {'jql': 'order by created DESC', 'maxResults': 5}
response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
