#!/bin/bash
# Prepare release script - validates environment before release

set -e

echo "🔍 Validating release environment..."
echo "===================================="

# Check required tools
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed"
        return 1
    else
        echo "✅ $1 is available"
        return 0
    fi
}

MISSING_TOOLS=0

# Required tools
for tool in git python3 pip docker pytest bandit; do
    if ! check_tool $tool; then
        MISSING_TOOLS=$((MISSING_TOOLS + 1))
    fi
done

# Optional tools
echo ""
echo "Optional tools:"
for tool in gh hub; do
    check_tool $tool || true
done

if [ $MISSING_TOOLS -gt 0 ]; then
    echo ""
    echo "❌ Missing $MISSING_TOOLS required tools"
    exit 1
fi

echo ""
echo "📋 Checking repository status..."
echo "================================"

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory has uncommitted changes"
    echo "   Please commit or stash your changes"
    exit 1
else
    echo "✅ Working directory is clean"
fi

# Check branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Not on main branch (current: $CURRENT_BRANCH)"
    read -p "Switch to main branch? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        git pull origin main
    else
        exit 1
    fi
else
    echo "✅ On main branch"
    git pull origin main
fi

echo ""
echo "🧪 Running pre-release checks..."
echo "================================"

# Check Python environment
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip --version)"

# Install/update dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

# Download required models
echo ""
echo "📥 Downloading required models..."
python3 -m spacy download en_core_web_sm --quiet
python3 -m nltk.downloader punkt -q

# Run quick tests
echo ""
echo "🧪 Running quick validation tests..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from customer_snapshot import TranscriptProcessor
    print('✅ Core imports working')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Check Docker
echo ""
echo "🐳 Checking Docker..."
if docker info &> /dev/null; then
    echo "✅ Docker daemon is running"

    # Try to build image
    echo "   Testing Docker build..."
    if docker build -t release-test . --quiet; then
        echo "✅ Docker build successful"
        docker rmi release-test --force &> /dev/null
    else
        echo "⚠️  Docker build failed"
    fi
else
    echo "⚠️  Docker daemon not running"
fi

# Check for existing tags
echo ""
echo "📌 Recent version tags:"
git tag -l "v*" | tail -5

# Display current version
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo ""
echo "Current version: $CURRENT_VERSION"

echo ""
echo "✅ Release environment validated!"
echo ""
echo "Next steps:"
echo "1. Run: ./release.py [major|minor|patch|hotfix]"
echo "2. Follow the prompts"
echo "3. Review and merge the release PR"
echo "4. Push the release tag"
echo ""
