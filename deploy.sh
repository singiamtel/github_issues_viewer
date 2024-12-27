#!/usr/bin/env bash 

# Used to deploy the app on the VPS
set -euo pipefail

cd ~/servers/github_issues_viewer 

echo "Fetching latest changes..."
git fetch && git reset --hard origin/master

echo "Stopping containers..."
docker compose down

echo "Building and starting containers..."
docker compose up -d --build

echo "Deployment completed!" 