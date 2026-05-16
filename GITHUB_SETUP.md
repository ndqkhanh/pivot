# GitHub Setup Guide

This guide helps you push the Pivot project to GitHub.

---

## Prerequisites

- GitHub account
- GitHub CLI (`gh`) installed ✅
- Git configured with your credentials

---

## Step 1: Create GitHub Repository

```bash
# Navigate to project directory
cd /Users/khanhnguyen/Downloads/MyCV/research/harness-engineering/projects/pivot

# Create GitHub repository (choose one method)

# Method 1: Using GitHub CLI (Recommended)
gh repo create pivot --public --source=. --remote=origin --push

# Method 2: Using GitHub CLI with description
gh repo create pivot \
  --public \
  --description "Production-grade AI Agent Reliability Harness - Unified evaluation, guardrails, and deterministic replay" \
  --source=. \
  --remote=origin \
  --push

# Method 3: Manual (via GitHub web interface)
# 1. Go to https://github.com/new
# 2. Repository name: pivot
# 3. Description: Production-grade AI Agent Reliability Harness
# 4. Public repository
# 5. Do NOT initialize with README (we already have one)
# 6. Create repository
# 7. Then run:
git remote add origin https://github.com/YOUR_USERNAME/pivot.git
git branch -M main
git push -u origin main
```

---

## Step 2: Verify Push

```bash
# Check remote
git remote -v

# Check branch
git branch -a

# View on GitHub
gh repo view --web
```

---

## Step 3: Set Up GitHub Actions (Optional)

The repository includes CI/CD workflows in `.github/workflows/` (to be created in Phase 1).

---

## Phase Completion Checklist

After completing each phase, push to GitHub:

### Phase 0: Foundation ✅
```bash
git push origin main
git tag -a v0.0.1 -m "Phase 0: Foundation complete"
git push origin v0.0.1
```

### Phase 1: MVP (M3-6)
```bash
git push origin main
git tag -a v0.1.0 -m "Phase 1: MVP complete"
git push origin v0.1.0
```

### Phase 2: V1.0 (M7-12)
```bash
git push origin main
git tag -a v1.0.0 -m "Phase 2: V1.0 complete"
git push origin v1.0.0
```

### Phase 3: Production (M13-18)
```bash
git push origin main
git tag -a v1.5.0 -m "Phase 3: Production hardening complete"
git push origin v1.5.0
```

---

## Recommended: Set Up Branch Protection

After creating the repository:

```bash
# Protect main branch
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":[]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```

---

## Quick Command Reference

```bash
# Status
git status

# Add all changes
git add -A

# Commit
git commit -m "feat: description"

# Push
git push origin main

# Create tag
git tag -a v0.1.0 -m "Version 0.1.0"
git push origin v0.1.0

# View commits
git log --oneline --graph --all

# View remote
gh repo view --web
```

---

## Troubleshooting

### Authentication Issues

```bash
# Login to GitHub CLI
gh auth login

# Check authentication status
gh auth status

# Refresh token
gh auth refresh
```

### Push Rejected

```bash
# Pull first
git pull origin main --rebase

# Then push
git push origin main
```

### Remote Already Exists

```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/pivot.git
```

---

## Next Steps

1. **Create GitHub repository** using one of the methods above
2. **Push Phase 0** to GitHub
3. **Continue with Phase 1 implementation**
4. **Push after each phase completion**

---

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username.
