# Development Setup Guide

This guide will help you set up the development environment for the Customer Solution Snapshot Generator.

## Prerequisites

- Python 3.8+ (3.9 recommended)
- Git
- VS Code (recommended IDE)

## Quick Setup

### 1. Clone and Navigate
```bash
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements-minimal.txt

# Install coreferee separately (has spaCy version constraints)
pip install coreferee

# Download spaCy English model
python -m spacy download en_core_web_sm
```

### 4. Configure Environment
```bash
# Copy environment template
cp snapshot_automation/.env.example snapshot_automation/.env

# Edit .env file and add your API key
# ANTHROPIC_API_KEY=your_api_key_here
```

### 5. VS Code Setup

If you're using VS Code:

1. **Open the project**: `code .`
2. **Select Python Interpreter**: 
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose `./venv/bin/python`
3. **Install recommended extensions**:
   - Python
   - Pylance
   - Python Docstring Generator

## Verify Installation

Test that everything works:

```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python -c "import anthropic, langchain, spacy, webvtt, nltk; print('✅ All dependencies loaded successfully')"

# Test processors
cd snapshot_automation
python vtt_to_markdown_processor.py  # Test with example file
```

## Working with the Project

### Running Scripts
```bash
# Always activate virtual environment first
source venv/bin/activate

# Navigate to project directory
cd snapshot_automation

# Run processors
python vtt_to_html_processor.py
python vtt_to_markdown_processor.py
```

### Adding New Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package_name

# Update requirements (if needed)
pip freeze > requirements-minimal.txt
```

### VS Code Troubleshooting

If VS Code doesn't recognize the virtual environment:

1. **Reload VS Code**: `Cmd+Shift+P` → "Developer: Reload Window"
2. **Check interpreter**: `Cmd+Shift+P` → "Python: Select Interpreter" → Choose `./venv/bin/python`
3. **Clear cache**: Delete `.vscode/settings.json` and restart VS Code

## Common Issues

### spaCy Model Not Found
```bash
source venv/bin/activate
python -m spacy download en_core_web_sm
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify you're in the right directory
pwd  # Should end with customer-solution-snapshot-generator

# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

### API Key Issues
```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# Or check .env file
cat snapshot_automation/.env
```

## Development Workflow

1. **Always activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Navigate to working directory**:
   ```bash
   cd snapshot_automation
   ```

3. **Run your code**:
   ```bash
   python your_script.py
   ```

4. **Deactivate when done**:
   ```bash
   deactivate
   ```

## VS Code Integration Benefits

With the virtual environment properly configured, you'll get:

- ✅ **Code completion** for all installed packages
- ✅ **Type checking** and error detection
- ✅ **Integrated debugging** with breakpoints
- ✅ **Import suggestions** and auto-imports
- ✅ **Linting** and code formatting
- ✅ **Interactive Python REPL** in terminal

You're all set! 🚀