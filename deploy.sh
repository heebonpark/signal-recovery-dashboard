#!/bin/bash
# Data Intel PRO Deployment Script

echo "Starting Deployment Process..."

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing new Git repository..."
    git init
    git branch -M main
fi

# Ask for Remote URL if it doesn't exist
if ! git remote | grep -q 'origin'; then
    read -p "Enter GitHub Remote URL: " REMOTE_URL
    git remote add origin "$REMOTE_URL"
fi

# Add and Commit
git add .
git commit -m "Deploy 0303: Data Intel PRO Dashboard updates"

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo "Deployment complete! ✅"
