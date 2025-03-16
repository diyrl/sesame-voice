#!/bin/bash

# Push code to GitHub repository
REPO_URL="https://github.com/diyrl/sesame-voice.git"
CURRENT_DIR=$(pwd)
DIRNAME=$(basename "$CURRENT_DIR")

# Rename README_APP.md to README.md
if [ -f "README_APP.md" ]; then
    echo "Renaming README_APP.md to README.md..."
    mv README_APP.md README.md
fi

# Make sure directory structure exists
mkdir -p static/audio outputs

# Check if this is already a git repository
if [ -d ".git" ]; then
    echo "This is already a git repository."
else
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding files to git..."
git add .

# Create initial commit
echo "Creating commit..."
git commit -m "Initial commit: CSM Speech Generator Web Interface

A web interface for the Conversation Speech Model (CSM) implementation 
for Apple Silicon using MLX. This provides a user-friendly way to generate
natural-sounding speech with various voice options."

# Set the remote repository
echo "Setting remote repository..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

# Push to GitHub
echo "Pushing to GitHub..."
echo "You may be prompted for your GitHub credentials."
git push -u origin main

echo ""
echo "======================================================================================"
echo "✅ Repository pushed to $REPO_URL"
echo "======================================================================================"
echo ""
echo "If you encountered any authentication issues, make sure you have configured GitHub"
echo "authentication properly. You may need to:"
echo ""
echo "1. Create a personal access token: https://github.com/settings/tokens"
echo "2. Use the token as your password when prompted"
echo ""
echo "Or set up SSH authentication: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
echo "======================================================================================"