#!/usr/bin/env python3
import os
import requests

# Test Bitbucket API directly
username = os.getenv('ATLASSIAN_USERNAME')
token = os.getenv('BITBUCKET_API_TOKEN', os.getenv('ATLASSIAN_API_TOKEN'))
workspace = os.getenv('BITBUCKET_WORKSPACE', 'anthonyd723')

print(f"Using BITBUCKET_API_TOKEN: {'SET' if os.getenv('BITBUCKET_API_TOKEN') else 'NOT SET (using ATLASSIAN_API_TOKEN)'}")

print(f"\nTesting Bitbucket API...")
print(f"Username: {username}")
print(f"Workspace: {workspace}")
print(f"Token length: {len(token) if token else 0}\n")

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
