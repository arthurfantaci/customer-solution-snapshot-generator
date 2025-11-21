# Development Setup Guide

This guide will help you set up the development environment for the Customer Solution Snapshot Generator using modern Python tooling.

## Prerequisites

- Python 3.9+ (3.13 recommended)
- Git
- VS Code (recommended IDE)

## Quick Setup

### 1. Install uv (Fast Python Package Manager)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### 2. Clone and Navigate

```bash
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator
```

### 3. Install Dependencies with uv

```bash
# Install all dependencies (creates .venv automatically)
uv sync

# Install development dependencies
uv sync --extra dev

# Download spaCy English model
uv run python -m spacy download en_core_web_sm
```

That's it! The `uv sync` command automatically:
- Creates a virtual environment in `.venv/`
- Installs all dependencies from `pyproject.toml`
- Uses `uv.lock` for reproducible builds

### 4. Configure Environment

```bash
# Copy environment template
cp snapshot_automation/.env.example snapshot_automation/.env

# Edit .env file and add your API keys
# ANTHROPIC_API_KEY=your_api_key_here
```

### 5. VS Code Setup

If you're using VS Code:

1. **Open the project**: `code .`
2. **Select Python Interpreter**:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose `./.venv/bin/python`
3. **Install recommended extensions**:
   - Python
   - Pylance
   - Ruff (for linting and formatting)

## Verify Installation

Test that everything works:

```bash
# Test imports
uv run python -c "import anthropic, langchain, spacy, webvtt, nltk; print('✅ All dependencies loaded successfully')"

# Run tests
uv run pytest

# Test a processor (fast startup with lazy loading!)
uv run python snapshot_automation/transcript_pipeline.py
```

## Working with the Project

### Running Scripts

```bash
# Main processors (with lazy loading for fast startup)
uv run python snapshot_automation/vtt_to_html_processor.py
uv run python snapshot_automation/vtt_to_markdown_processor.py

# Utilities
uv run python snapshot_automation/transcript_parallel.py
uv run python snapshot_automation/converter.py
```

### Code Quality Tools

```bash
# Format code with ruff
uv run ruff format .

# Check for linting issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_validators.py

# Run tests in parallel (faster)
uv run pytest -n auto
```

### Adding New Dependencies

```bash
# Add a production dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update all dependencies
uv sync

# Lock dependencies (updates uv.lock)
uv lock
```

## Common Commands

### uv Quick Reference

```bash
uv sync              # Install/update dependencies from pyproject.toml
uv sync --extra dev  # Include dev dependencies
uv add package       # Add a new dependency
uv remove package    # Remove a dependency
uv run command       # Run a command in the virtual environment
uv pip list          # List installed packages
uv pip show package  # Show package details
```

### Development Workflow

```bash
# 1. Make changes to code

# 2. Format and check
uv run ruff format .
uv run ruff check --fix .

# 3. Run tests
uv run pytest

# 4. Commit (pre-commit hooks run automatically)
git add .
git commit -m "Your message"

# 5. Push
git push
```

## Common Issues

### spaCy Model Not Found

```bash
uv run python -m spacy download en_core_web_sm
```

### Import Errors

```bash
# Ensure dependencies are installed
uv sync

# Check Python version
uv run python --version  # Should be 3.9+

# Verify you're in the right directory
pwd  # Should end with customer-solution-snapshot-generator
```

### API Key Issues

```bash
# Check if API key is set
cat snapshot_automation/.env

# Or check environment variable
echo $ANTHROPIC_API_KEY
```

### Virtual Environment Issues

```bash
# Remove and recreate virtual environment
rm -rf .venv
uv sync

# Select correct interpreter in VS Code
# Cmd+Shift+P → "Python: Select Interpreter" → .venv/bin/python
```

## VS Code Integration

### Recommended Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.linting.enabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  }
}
```

### Benefits

With the virtual environment properly configured, you'll get:

- ✅ **Fast imports**: Lazy loading makes imports ~50x faster
- ✅ **Code completion** for all installed packages
- ✅ **Type checking** and error detection with Pylance
- ✅ **Integrated debugging** with breakpoints
- ✅ **Import suggestions** and auto-imports
- ✅ **Automatic linting** with ruff
- ✅ **Format on save** with ruff
- ✅ **Interactive Python REPL** in terminal

## Performance Features

### Lazy Loading

All transcript processors now use lazy loading:
- **Fast startup**: ~0.1s instead of ~5s
- **Memory efficient**: 500MB+ savings when models not used
- **On-demand loading**: Models load automatically when needed

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
uv run pre-commit install
```

Now every commit will automatically:
- Format code with ruff
- Check for linting issues
- Run type checks with mypy
- Validate YAML files
- Check for trailing whitespace

## Advanced Setup

### Development with Multiple Python Versions

```bash
# Specify Python version
uv venv --python 3.11

# Or use system Python
uv venv --python python3.13
```

### Custom Virtual Environment Location

```bash
# Use custom location
UV_PROJECT_ENVIRONMENT=/path/to/venv uv sync
```

### Offline Development

```bash
# Create a cache for offline use
uv cache prune
uv sync --offline  # Use cached packages
```

## Migrating from pip

If you were using the old setup:

```bash
# Remove old virtual environment
rm -rf venv/

# Remove old requirements files (already done)
# requirements.txt, requirements-dev.txt, etc. are now obsolete

# Install with uv
uv sync

# All dependencies are now managed in pyproject.toml
```

## Why uv?

- **10-100x faster** than pip for installations
- **Reproducible builds** with uv.lock
- **Better dependency resolution** with fewer conflicts
- **Rust-based** for maximum performance
- **Compatible with pip** for easy migration
- **Modern best practices** built-in

You're all set! 🚀

For more information, see:
- [uv documentation](https://docs.astral.sh/uv/)
- [ruff documentation](https://docs.astral.sh/ruff/)
- [CLAUDE.md](./CLAUDE.md) for development guidelines
