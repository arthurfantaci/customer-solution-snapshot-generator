#!/bin/bash
# Script to close obsolete Dependabot PRs for pip dependencies
# These PRs are incompatible with the project's migration to uv
#
# Prerequisites: GitHub CLI (gh) must be authenticated
# Run: gh auth login

set -e

REPO="arthurfantaci/customer-solution-snapshot-generator"
CLOSE_MESSAGE="Closing this PR as the project has migrated from pip to uv for dependency management. Dependencies are now managed through pyproject.toml and uv.lock files. Manual updates can be performed using \`uv sync --upgrade\`. Thank you Dependabot!"

echo "=================================================="
echo "Closing Obsolete Dependabot pip PRs"
echo "=================================================="
echo ""
echo "Repository: $REPO"
echo "Total PRs to close: 10"
echo ""

# List of pip-based Dependabot PRs to close
# PR numbers based on web scraping results
declare -a PIP_PRS=(
  "26:Bump isort from 5.13.2 to 6.1.0 (OBSOLETE - replaced by ruff)"
  "25:Bump nltk from 3.8.1 to 3.9.2"
  "24:Bump pycaption from 2.2.1 to 2.2.18"
  "23:Bump pytest-asyncio from 0.23.7 to 1.2.0"
  "20:Bump pre-commit from 3.7.1 to 4.3.0"
  "19:Bump langchain from 0.2.11 to 0.3.27"
  "18:Bump line-profiler from 4.1.3 to 5.0.0"
  "16:Bump bandit from 1.7.9 to 1.8.6"
  "14:Bump coreferee from 1.4.0 to 1.4.1"
  "13:Bump sphinx from 7.3.7 to 7.4.7"
)

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
  echo "❌ ERROR: GitHub CLI is not authenticated"
  echo "Please run: gh auth login"
  exit 1
fi

echo "✓ GitHub CLI authenticated"
echo ""

# Ask for confirmation
echo "This will close the following PRs:"
for pr in "${PIP_PRS[@]}"; do
  PR_NUM=$(echo "$pr" | cut -d: -f1)
  PR_TITLE=$(echo "$pr" | cut -d: -f2-)
  echo "  - PR #$PR_NUM: $PR_TITLE"
done
echo ""
read -p "Do you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "Closing PRs..."
echo ""

# Close each PR
CLOSED_COUNT=0
FAILED_COUNT=0

for pr in "${PIP_PRS[@]}"; do
  PR_NUM=$(echo "$pr" | cut -d: -f1)
  PR_TITLE=$(echo "$pr" | cut -d: -f2-)

  echo -n "Closing PR #$PR_NUM... "

  if gh pr close "$PR_NUM" --repo "$REPO" --comment "$CLOSE_MESSAGE" 2>/dev/null; then
    echo "✓ Closed"
    ((CLOSED_COUNT++))
  else
    echo "❌ Failed (may already be closed)"
    ((FAILED_COUNT++))
  fi
done

echo ""
echo "=================================================="
echo "Summary:"
echo "  Successfully closed: $CLOSED_COUNT"
echo "  Failed/Already closed: $FAILED_COUNT"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Delete remote branches: git push origin --delete <branch-name>"
echo "2. Or use: gh pr list --state closed --limit 15 | grep dependabot"
