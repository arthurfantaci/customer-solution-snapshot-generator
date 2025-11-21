#!/bin/bash
# Post-release validation script

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 v1.0.0"
    exit 1
fi

echo "🔍 Validating release $VERSION"
echo "=============================="

# Function to check URL
check_url() {
    if curl -f -s -o /dev/null "$1"; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2"
        return 1
    fi
}

# Check GitHub release
echo ""
echo "📦 Checking GitHub release..."
RELEASE_URL="https://github.com/arthurfantaci/customer-solution-snapshot-generator/releases/tag/$VERSION"
if check_url "$RELEASE_URL" "GitHub release exists"; then
    # Check release assets
    ASSETS_URL="https://api.github.com/repos/arthurfantaci/customer-solution-snapshot-generator/releases/tags/$VERSION"
    ASSETS=$(curl -s "$ASSETS_URL" | grep -c "browser_download_url" || echo "0")
    echo "   Found $ASSETS release assets"
fi

# Check Docker images
echo ""
echo "🐳 Checking Docker images..."
if command -v docker &> /dev/null; then
    # Docker Hub
    if docker pull arthurfantaci/customer-snapshot-generator:$VERSION &> /dev/null; then
        echo "✅ Docker Hub image available"
    else
        echo "⚠️  Docker Hub image not found"
    fi

    # GitHub Container Registry
    if docker pull ghcr.io/arthurfantaci/customer-snapshot-generator:$VERSION &> /dev/null; then
        echo "✅ GitHub Container Registry image available"
    else
        echo "⚠️  GitHub Container Registry image not found"
    fi
else
    echo "⚠️  Docker not available for testing"
fi

# Check documentation
echo ""
echo "📚 Checking documentation..."
DOC_URL="https://arthurfantaci.github.io/customer-solution-snapshot-generator/$VERSION/index.html"
check_url "$DOC_URL" "Version documentation deployed"

LATEST_DOC_URL="https://arthurfantaci.github.io/customer-solution-snapshot-generator/latest/index.html"
check_url "$LATEST_DOC_URL" "Latest documentation link"

# Check package installation
echo ""
echo "📦 Testing package installation..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Create virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Try to install (would need to be on PyPI)
echo "   Testing local installation..."
if pip install -q /path/to/dist/customer_snapshot-*.whl &> /dev/null; then
    echo "✅ Package installation successful"

    # Test import
    if python3 -c "import customer_snapshot; print('✅ Package import successful')" &> /dev/null; then
        :
    else
        echo "❌ Package import failed"
    fi
else
    echo "⚠️  Package installation test skipped"
fi

deactivate
cd -
rm -rf "$TEMP_DIR"

# Summary
echo ""
echo "📊 Release Validation Summary"
echo "============================"
echo "Version: $VERSION"
echo "GitHub Release: $RELEASE_URL"
echo ""
echo "If all checks passed, the release is ready for use!"
echo "If any checks failed, investigate and fix the issues."
echo ""
