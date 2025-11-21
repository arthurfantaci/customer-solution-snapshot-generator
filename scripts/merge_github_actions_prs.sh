#!/bin/bash
# Script to review and merge GitHub Actions Dependabot PRs
#
# Prerequisites: GitHub CLI (gh) must be authenticated
# Run: gh auth login

set -e

REPO="arthurfantaci/customer-solution-snapshot-generator"

echo "=================================================="
echo "GitHub Actions PRs - Review and Merge"
echo "=================================================="
echo ""
echo "Repository: $REPO"
echo ""

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
  echo "❌ ERROR: GitHub CLI is not authenticated"
  echo "Please run: gh auth login"
  exit 1
fi

echo "✓ GitHub CLI authenticated"
echo ""

# GitHub Actions PRs to review
declare -a ACTIONS_PRS=(
  "22:actions/setup-python v4 → v6"
  "21:actions/github-script v6 → v8"
  "5:docker/build-push-action v5 → v6"
  "3:codecov/codecov-action v3 → v5"
  "2:actions/cache v3 → v4"
)

echo "GitHub Actions PRs to Review:"
for pr in "${ACTIONS_PRS[@]}"; do
  PR_NUM=$(echo "$pr" | cut -d: -f1)
  PR_TITLE=$(echo "$pr" | cut -d: -f2-)
  echo "  - PR #$PR_NUM: $PR_TITLE"
done
echo ""
echo "This script will help you review and merge these PRs one by one."
echo ""

read -p "Do you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo ""

MERGED_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0

for pr in "${ACTIONS_PRS[@]}"; do
  PR_NUM=$(echo "$pr" | cut -d: -f1)
  PR_TITLE=$(echo "$pr" | cut -d: -f2-)

  echo "=================================================="
  echo "PR #$PR_NUM: $PR_TITLE"
  echo "=================================================="
  echo ""

  # Get PR status
  echo "Fetching PR details..."
  PR_STATUS=$(gh pr view "$PR_NUM" --repo "$REPO" --json state,mergeable,statusCheckRollup 2>/dev/null)

  if [ $? -ne 0 ]; then
    echo "❌ Failed to fetch PR details"
    ((FAILED_COUNT++))
    continue
  fi

  # Check if PR is open
  STATE=$(echo "$PR_STATUS" | jq -r '.state')
  if [ "$STATE" != "OPEN" ]; then
    echo "⚠ PR is $STATE - skipping"
    ((SKIPPED_COUNT++))
    continue
  fi

  # Display PR information
  echo ""
  gh pr view "$PR_NUM" --repo "$REPO"
  echo ""

  # Check CI status
  echo "Checking CI status..."
  CHECKS_STATUS=$(echo "$PR_STATUS" | jq -r '.statusCheckRollup[].conclusion' 2>/dev/null | sort | uniq)

  if echo "$CHECKS_STATUS" | grep -q "FAILURE"; then
    echo "❌ Some checks are failing"
    echo ""
    echo "Would you like to view the failed checks? (yes/no)"
    read VIEW_CHECKS
    if [ "$VIEW_CHECKS" = "yes" ]; then
      gh pr checks "$PR_NUM" --repo "$REPO"
    fi
  elif echo "$CHECKS_STATUS" | grep -q "PENDING"; then
    echo "⚠ Some checks are still running"
  else
    echo "✓ All checks passed (or no checks required)"
  fi

  echo ""
  echo "Actions:"
  echo "  1. Merge this PR"
  echo "  2. Skip this PR"
  echo "  3. View diff"
  echo "  4. View checks"
  echo "  5. Open in browser"
  echo "  6. Abort script"
  echo ""
  read -p "Choose action (1-6): " ACTION

  case $ACTION in
    1)
      echo ""
      echo "Merging PR #$PR_NUM..."
      if gh pr merge "$PR_NUM" --repo "$REPO" --auto --squash; then
        echo "✓ PR #$PR_NUM merged successfully"
        ((MERGED_COUNT++))
      else
        echo "❌ Failed to merge PR #$PR_NUM"
        ((FAILED_COUNT++))
      fi
      ;;
    2)
      echo "Skipping PR #$PR_NUM"
      ((SKIPPED_COUNT++))
      ;;
    3)
      gh pr diff "$PR_NUM" --repo "$REPO"
      echo ""
      read -p "Press Enter to continue..."
      # Re-prompt for action
      echo "Would you like to merge this PR? (yes/no)"
      read MERGE_NOW
      if [ "$MERGE_NOW" = "yes" ]; then
        gh pr merge "$PR_NUM" --repo "$REPO" --auto --squash && ((MERGED_COUNT++)) || ((FAILED_COUNT++))
      else
        ((SKIPPED_COUNT++))
      fi
      ;;
    4)
      gh pr checks "$PR_NUM" --repo "$REPO"
      echo ""
      read -p "Press Enter to continue..."
      # Re-prompt for action
      echo "Would you like to merge this PR? (yes/no)"
      read MERGE_NOW
      if [ "$MERGE_NOW" = "yes" ]; then
        gh pr merge "$PR_NUM" --repo "$REPO" --auto --squash && ((MERGED_COUNT++)) || ((FAILED_COUNT++))
      else
        ((SKIPPED_COUNT++))
      fi
      ;;
    5)
      gh pr view "$PR_NUM" --repo "$REPO" --web
      echo "Opened in browser. Skipping for now..."
      ((SKIPPED_COUNT++))
      ;;
    6)
      echo "Aborting..."
      break
      ;;
    *)
      echo "Invalid choice. Skipping PR #$PR_NUM"
      ((SKIPPED_COUNT++))
      ;;
  esac

  echo ""
done

echo ""
echo "=================================================="
echo "Summary:"
echo "  Merged: $MERGED_COUNT"
echo "  Skipped: $SKIPPED_COUNT"
echo "  Failed: $FAILED_COUNT"
echo "=================================================="
echo ""

if [ $MERGED_COUNT -gt 0 ]; then
  echo "✓ Successfully merged $MERGED_COUNT GitHub Actions updates"
  echo ""
  echo "Recommended: Pull the latest changes from main"
  echo "  git pull origin main"
fi
