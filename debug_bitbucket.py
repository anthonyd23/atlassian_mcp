#!/usr/bin/env python3
import os
import requests

# Test Bitbucket API directly
username = os.getenv('ATLASSIAN_USERNAME')
token = os.getenv('ATLASSIAN_API_TOKEN')
workspace = os.getenv('BITBUCKET_WORKSPACE', 'anthonyd723')

print(f"Testing Bitbucket API...")
print(f"Username: {username}")
print(f"Workspace: {workspace}")
print(f"Token: {'*' * len(token) if token else 'NOT SET'}\n")

# Test 1: Get user info
print("1. Testing user endpoint...")
url = "https://api.bitbucket.org/2.0/user"
response = requests.get(url, auth=(username, token))
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}\n")

# Test 2: Get repositories
print("2. Testing repositories endpoint...")
url = f"https://api.bitbucket.org/2.0/repositories/{workspace}"
response = requests.get(url, auth=(username, token))
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}\n")

# Test 3: Try with Bearer token instead
print("3. Testing with Bearer token...")
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
