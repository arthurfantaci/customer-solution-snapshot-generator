# Manual Instructions: Creating GitHub Labels

If you prefer to create labels manually via the GitHub web interface instead of using the script, follow these steps:

## Access Labels Page

1. Navigate to: https://github.com/arthurfantaci/customer-solution-snapshot-generator/labels
2. Or: Repository → Issues tab → Labels (left sidebar)

## Create Required Labels

Click "New label" and create each of the following:

### Label 1: automated
- **Name**: `automated`
- **Description**: `For automated PRs created by bots`
- **Color**: `#7057ff` (purple)

### Label 2: github-actions
- **Name**: `github-actions`
- **Description**: `GitHub Actions workflow updates`
- **Color**: `#000000` (black)

### Label 3: dependencies
- **Name**: `dependencies`
- **Description**: `Dependency updates`
- **Color**: `#0366d6` (blue)

## Verification

After creating all labels, verify them at:
https://github.com/arthurfantaci/customer-solution-snapshot-generator/labels

These labels will be automatically applied by Dependabot to future PRs based on the configuration in `.github/dependabot.yml`.

## Using the Automated Script

Alternatively, you can use the automated script after setting up GitHub CLI:

```bash
# Authenticate GitHub CLI (one-time setup)
gh auth login

# Run the label creation script
./scripts/create_github_labels.sh
```
