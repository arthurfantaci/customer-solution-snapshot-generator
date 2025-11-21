# GitHub Repository Cleanup Scripts

This directory contains scripts and instructions for cleaning up the GitHub repository, specifically addressing the 15 open Dependabot PRs and related CI/CD issues.

## Problem Summary

The repository has 15 open Dependabot PRs because:

1. **Outdated Configuration**: Dependabot was configured for `pip` ecosystem, but the project migrated to `uv` for dependency management
2. **Missing Labels**: Dependabot PRs require labels (`automated`, `github-actions`, `dependencies`) that don't exist
3. **CI/CD Failures**: Workflows were failing due to missing requirements.txt files and outdated tooling (now fixed in commit c4eb084)
4. **Obsolete Updates**: Some PRs (like isort) update dependencies that have been replaced (by ruff)

## Cleanup Steps

### Prerequisites

Install and authenticate GitHub CLI:

```bash
# Install GitHub CLI (if not already installed)
# macOS:
brew install gh

# Linux:
# Follow: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Authenticate (one-time setup)
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

### Step 1: Commit Dependabot Configuration Changes

The dependabot.yml file has been updated to disable pip monitoring. Commit and push this change:

```bash
# From repository root
git add .github/dependabot.yml scripts/
git commit -m "chore: add GitHub cleanup scripts and update dependabot config"
git push
```

### Step 2: Create Missing GitHub Labels

**Option A - Automated (Recommended):**

```bash
./scripts/create_github_labels.sh
```

**Option B - Manual:**

See instructions in [MANUAL_LABEL_INSTRUCTIONS.md](./MANUAL_LABEL_INSTRUCTIONS.md)

### Step 3: Close Obsolete pip PRs

Close the 10 Dependabot PRs for pip dependencies (incompatible with uv):

```bash
./scripts/close_obsolete_dependabot_prs.sh
```

This will close PRs: #26, #25, #24, #23, #20, #19, #18, #16, #14, #13

### Step 4: Review and Merge GitHub Actions PRs

Review and merge the 5 valid GitHub Actions update PRs:

```bash
./scripts/merge_github_actions_prs.sh
```

This interactive script will guide you through reviewing and merging:
- PR #22: actions/setup-python v4 → v6
- PR #21: actions/github-script v6 → v8
- PR #5: docker/build-push-action v5 → v6
- PR #3: codecov/codecov-action v3 → v5
- PR #2: actions/cache v3 → v4

**Note**: Ensure CI passes on each PR before merging.

### Step 5: Clean Up Remote Branches (Optional)

After closing/merging PRs, delete the remote branches:

```bash
# List Dependabot branches
git branch -r | grep dependabot

# Or use this one-liner to delete all closed Dependabot branches:
gh pr list --state closed --limit 20 --json headRefName --jq '.[].headRefName' | \
  grep dependabot | \
  xargs -I {} git push origin --delete {}
```

## Script Reference

### close_obsolete_dependabot_prs.sh

Closes all pip-based Dependabot PRs that are incompatible with uv.

**Usage:**
```bash
./scripts/close_obsolete_dependabot_prs.sh
```

### create_github_labels.sh

Creates the three missing labels required by Dependabot configuration.

**Usage:**
```bash
./scripts/create_github_labels.sh
```

### merge_github_actions_prs.sh

Interactive script to review and merge GitHub Actions update PRs.

**Usage:**
```bash
./scripts/merge_github_actions_prs.sh
```

## Manual Dependency Updates

Since Dependabot pip monitoring is now disabled, update dependencies manually:

```bash
# Update all dependencies
uv sync --upgrade

# Update specific dependency
uv add package-name@latest

# Test the changes
uv run pytest tests/
```

## Troubleshooting

### GitHub CLI Not Authenticated

```bash
gh auth login
# Follow the prompts
```

### Script Permission Denied

```bash
chmod +x scripts/*.sh
```
