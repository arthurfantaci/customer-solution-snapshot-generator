# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based system that generates Customer Success Snapshot documents from video meeting transcripts (VTT files). It uses NLP processing and AI models (primarily Anthropic's Claude) to extract insights, entities, and structured information from transcripts.

## Modern Development Setup

This project uses modern Python tooling:
- **uv**: Fast Python package manager (10-100x faster than pip)
- **ruff**: Fast linter and formatter (replaces black, isort, flake8)
- **Python 3.9+**: Minimum required version

### Quick Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and navigate
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator

# Install dependencies (creates .venv automatically)
uv sync

# Install development dependencies
uv sync --extra dev

# Download spaCy model
uv run python -m spacy download en_core_web_sm
```

### Environment Configuration

```bash
# Copy and configure environment variables
cp snapshot_automation/.env.example snapshot_automation/.env
# Then add your ANTHROPIC_API_KEY (required) and other API keys as needed
```

### Running Scripts

**First**, check out the examples to see what the output looks like:
```bash
ls snapshot_automation/examples/  # View example inputs and outputs
cat snapshot_automation/examples/README.md  # Read examples documentation
```

**Then**, run the processors:
```bash
# Main processors (with lazy loading for fast startup)
uv run python snapshot_automation/vtt_to_html_processor.py      # VTT → HTML with NLP analysis
uv run python snapshot_automation/vtt_to_markdown_processor.py   # VTT → Markdown with entities

# Utilities
uv run python snapshot_automation/transcript_parallel.py  # RAG-based Q&A system
uv run python snapshot_automation/transcript_tools.py     # LangChain agent for analysis
uv run python snapshot_automation/converter.py            # Simple VTT → Markdown
```

**Note**: All scripts have hardcoded file paths that need updating before running.

## Code Quality Tools

### Formatting and Linting

```bash
# Format code
uv run ruff format .

# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually
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
```

## Architecture

### Core Processing Flow
1. **Input**: VTT transcript files from customer meetings
2. **Processing Pipeline**:
   - Parse VTT → Clean text → Extract entities/topics → Generate structured output
   - Uses spaCy for NLP, NLTK for tokenization, transformers for summarization
   - **Lazy Loading**: Models load on-demand for fast startup and memory efficiency
3. **Output**: HTML/Markdown documents structured as Customer Solution Snapshots

### Key Modules

#### Main Package (`src/customer_snapshot/`)
- **core/**: Core processing logic (processors, NLP engine, validators)
- **io/**: Input/output handlers
- **utils/**: Utilities (config, memory optimization, file handling)
- **monitoring/**: System monitoring, health checks, error tracking
- **ai/**: AI model integrations and prompts

#### Legacy Automation (`snapshot_automation/`)
- **vtt_to_html_processor.py**: VTT → HTML with NLP analysis
- **vtt_to_markdown_processor.py**: VTT → Markdown with entities
- **transcript_pipeline.py**: Core transcript processing
- **model_loaders.py**: Lazy loading for ML models (spaCy, NLTK, transformers)
- **transcript_parallel.py**: RAG implementation using FAISS and VoyageAI embeddings
- **transcript_tools.py**: LangChain ReAct agent with web search and calculation tools

### Data Flow
```
VTT File → Parser → Text Cleaner → NLP Processor → AI Enhancement → Formatted Output
                                        ↓
                                  Vector Store (FAISS)
                                        ↓
                                    Q&A System
```

### Customer Solution Snapshot Structure
Generated documents include 11 sections:
1. Customer Information
2. Background
3. Solution
4. Engagement/Implementation Details
5. Results and Achievements
6. Adoption and Usage
7. Financial Impact
8. Long-Term Impact
9. Visuals
10. Additional Commentary
11. Executive Summary

## Performance Features

### Lazy Loading
All transcript processors use lazy loading for ML models:
- **Fast imports**: ~0.1s instead of ~5s
- **Memory efficient**: 500MB+ savings when models not used
- **On-demand loading**: Models load automatically when functions are called

### Caching
- **LRU caching**: Models cached after first load
- **Smart NLTK data**: Automatic download and caching

## Important Development Notes

1. **Modern Tooling**: Project uses `uv` for dependency management and `ruff` for linting/formatting. All configurations are in `pyproject.toml`.

2. **File Path Updates Required**: All scripts contain hardcoded file paths (e.g., `C:/Users/DQA/...`) that must be updated to your local paths.

3. **API Keys Required**:
   - `ANTHROPIC_API_KEY` (always required)
   - `VOYAGEAI_API_KEY` (for transcript_parallel.py)
   - `TAVILY_API_KEY` (for transcript_tools.py)

4. **Test Suite**: Project has pytest-based tests. Run with `uv run pytest`. Current coverage: 27%.

5. **VTT File Format**: Input files must be valid WebVTT format with timestamps and speaker labels.

6. **Template Files**: Document templates and AI prompts are in `snapshot_automation/template_files/`

## Project Structure

```
customer-solution-snapshot-generator/
├── src/customer_snapshot/     # Main package (modern, well-structured)
│   ├── ai/                    # AI integrations
│   ├── core/                  # Core processing
│   ├── io/                    # Input/output
│   ├── monitoring/            # System monitoring
│   └── utils/                 # Utilities
├── snapshot_automation/       # Legacy automation scripts
│   ├── model_loaders.py       # Lazy loading utilities
│   ├── transcript_pipeline.py # Core pipeline
│   ├── vtt_to_html_processor.py
│   ├── vtt_to_markdown_processor.py
│   └── examples/              # Example inputs/outputs
├── tests/                     # Test suites
│   ├── unit/
│   ├── integration/
│   └── manual/
├── scripts/                   # Utility scripts
│   ├── benchmarking/
│   ├── deployment/
│   ├── monitoring/
│   └── optimization/
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
└── .pre-commit-config.yaml    # Git hooks
```

## Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv sync

# Lock dependencies
uv lock
```

## Git Workflow

```bash
# Format code before committing
uv run ruff format .

# Check for issues
uv run ruff check --fix .

# Commit (pre-commit hooks will run automatically)
git add .
git commit -m "Your message"

# Push
git push
```
