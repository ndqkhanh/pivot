#!/bin/bash
# Push Phase 0 to GitHub
# Run this script to create the GitHub repository and push Phase 0

set -e

echo "🚀 Pushing Pivot Phase 0 to GitHub..."
echo ""

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated. Please run:"
    echo "   gh auth login"
    exit 1
fi

# Create GitHub repository
echo "📦 Creating GitHub repository..."
gh repo create pivot \
  --public \
  --description "Production-grade AI Agent Reliability Harness - Unified evaluation, guardrails, and deterministic replay" \
  --source=. \
  --remote=origin \
  --push

echo ""
echo "✅ Phase 0 pushed to GitHub!"
echo ""
echo "📊 Repository: $(gh repo view --json url -q .url)"
echo "📝 Commits: $(git rev-list --count HEAD)"
echo "📄 Files: $(git ls-files | wc -l | xargs)"
echo ""
echo "🎯 Next: Start Phase 1 implementation (RFCs + MVP)"
