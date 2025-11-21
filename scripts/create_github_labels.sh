#!/bin/bash
# Script to create missing GitHub labels for Dependabot
#
# Prerequisites: GitHub CLI (gh) must be authenticated
# Run: gh auth login

set -e

REPO="arthurfantaci/customer-solution-snapshot-generator"

echo "=================================================="
echo "Creating Missing GitHub Labels"
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

# Labels to create based on dependabot.yml configuration
declare -A LABELS=(
  ["automated"]="7057ff:For automated PRs created by bots"
  ["github-actions"]="000000:GitHub Actions workflow updates"
  ["dependencies"]="0366d6:Dependency updates"
)

echo "This will create the following labels:"
for label in "${!LABELS[@]}"; do
  IFS=':' read -r color description <<< "${LABELS[$label]}"
  echo "  - $label (color: #$color)"
  echo "    Description: $description"
done
echo ""

read -p "Do you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "Creating labels..."
echo ""

CREATED_COUNT=0
EXISTS_COUNT=0
FAILED_COUNT=0

for label in "${!LABELS[@]}"; do
  IFS=':' read -r color description <<< "${LABELS[$label]}"

  echo -n "Creating label '$label'... "

  # Try to create the label
  if gh label create "$label" \
      --repo "$REPO" \
      --color "$color" \
      --description "$description" 2>/dev/null; then
    echo "✓ Created"
    ((CREATED_COUNT++))
  else
    # Check if it failed because label already exists
    if gh label list --repo "$REPO" --json name | grep -q "\"$label\""; then
      echo "⚠ Already exists"
      ((EXISTS_COUNT++))
    else
      echo "❌ Failed"
      ((FAILED_COUNT++))
    fi
  fi
done

echo ""
echo "=================================================="
echo "Summary:"
echo "  Created: $CREATED_COUNT"
echo "  Already exists: $EXISTS_COUNT"
echo "  Failed: $FAILED_COUNT"
echo "=================================================="
echo ""

if [ $CREATED_COUNT -gt 0 ] || [ $EXISTS_COUNT -gt 0 ]; then
  echo "✓ Labels are now configured for Dependabot"
  echo ""
  echo "You can view all labels at:"
  echo "https://github.com/$REPO/labels"
fi
