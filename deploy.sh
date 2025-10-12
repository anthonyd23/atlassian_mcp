#!/bin/bash

# Deployment script for Atlassian MCP Server

set -e

echo "Building and deploying Atlassian MCP Server..."

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "SAM CLI is not installed. Please install it first:"
    echo "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if required parameters are set
if [ -z "$ATLASSIAN_BASE_URL" ] || [ -z "$ATLASSIAN_USERNAME" ] || [ -z "$ATLASSIAN_API_TOKEN" ]; then
    echo "Please set the following environment variables:"
    echo "  ATLASSIAN_BASE_URL (e.g., https://yourcompany.atlassian.net)"
    echo "  ATLASSIAN_USERNAME (your Atlassian username/email)"
    echo "  ATLASSIAN_API_TOKEN (your Atlassian API token)"
    exit 1
fi

# Build the application
echo "Building SAM application..."
sam build

# Deploy the application
echo "Deploying to AWS..."
sam deploy \
    --guided \
    --parameter-overrides \
        AtlassianBaseUrl="$ATLASSIAN_BASE_URL" \
        AtlassianUsername="$ATLASSIAN_USERNAME" \
        AtlassianApiToken="$ATLASSIAN_API_TOKEN"

echo "Deployment complete!"
echo "Your MCP server is now available at the API Gateway URL shown above."