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

# Download NLTK data
uv run python -c "import nltk; nltk.download('punkt', quiet=True)"
```

### Environment Configuration

```bash
# Copy and configure environment variables
cp snapshot_automation/.env.example snapshot_automation/.env
# Then add your ANTHROPIC_API_KEY (required) and other API keys as needed
```

## Common Commands

### Development Workflow

```bash
# Format code (always run before committing)
uv run ruff format .

# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Type checking
uv run mypy src/customer_snapshot/ --ignore-missing-imports

# Security scanning
uv run bandit -r src/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_validators.py

# Run integration tests only
uv run pytest tests/integration/ -v

# Run performance tests (marked as slow)
uv run pytest tests/integration/ -m slow -v
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks (includes ruff, mypy, bandit, pydocstyle)
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files

# Update hooks to latest versions
uv run pre-commit autoupdate
```

### Building and Packaging

```bash
# Build package
uv run python -m build

# Check package integrity
twine check dist/*
```

## Architecture

### Dual Architecture: Modern Package + Legacy Scripts

The project has two parallel implementations that serve different purposes:

1. **`src/customer_snapshot/`** - Modern, well-structured Python package
   - Proper error handling, type hints, and comprehensive docstrings
   - Memory optimization and monitoring features
   - Used for production-grade implementations

2. **`snapshot_automation/`** - Legacy automation scripts
   - Quick prototyping and experimentation
   - Contains the actual working processors with hardcoded paths
   - **Important**: All executable scripts are in this directory

### Core Processing Flow

```
VTT File → Parser → Text Cleaner → NLP Processor → AI Enhancement → Formatted Output
                                        ↓
                                  Vector Store (FAISS)
                                        ↓
                                    Q&A System
```

### Key Modules

#### Main Package (`src/customer_snapshot/`)

- **core/processor.py**: Main `TranscriptProcessor` class with decorators for error tracking and memory profiling
- **core/nlp_engine.py**: NLP processing using spaCy and NLTK
- **io/vtt_reader.py**: VTT file parsing and validation
- **io/output_writer.py**: HTML/Markdown output generation
- **utils/memory_optimizer.py**: Memory optimization for large files
- **monitoring/**: System monitoring, health checks, error tracking
- **ai/**: AI model integrations and prompts

#### Legacy Automation (`snapshot_automation/`)

**Main Processors** (these are what you actually run):
- **vtt_to_html_processor.py**: VTT → HTML with NLP analysis
- **vtt_to_markdown_processor.py**: VTT → Markdown with entities
- **converter.py**: Simple VTT → Markdown converter

**Supporting Modules**:
- **transcript_pipeline.py**: Five-stage pipeline (read_vtt → clean_text → improve_formatting → enhance_with_nlp → output)
- **model_loaders.py**: Lazy loading utilities with `@lru_cache` decorators
  - `get_nlp_model()`: Loads spaCy models on-demand
  - `get_sentence_tokenizer()`: Loads NLTK punkt tokenizer
  - `get_summarization_pipeline()`: Loads transformers models
- **transcript_parallel.py**: RAG implementation using FAISS and VoyageAI embeddings
- **transcript_tools.py**: LangChain ReAct agent with web search (Tavily) and calculation tools

### Lazy Loading Architecture

All models use lazy loading to improve startup time (50x faster):
- Models imported via `model_loaders.py` functions, not direct imports
- `@lru_cache` ensures models load once and are reused
- Import time: ~0.1s vs ~5s without lazy loading
- Memory savings: 500MB+ when models not used

### Document Generation

Generated Customer Solution Snapshots include 11 sections:
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

### Template Files

Located in `snapshot_automation/template_files/`:
- **Customer Solution Snapshot Template.docx**: Main document template
- **quest_enterprises_snapshot_template.docx**: Example template
- **System_Prompt_Customer_Success_Snapshot.txt**: AI prompt for section generation
- **All_Prompt_Details.txt**: Complete prompt documentation

## Running Scripts

**Important**: All main processing scripts have hardcoded file paths that need updating before running. Look for paths like `C:/Users/DQA/...` and update them to your local paths.

**First**, check examples:
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

## CI/CD Pipeline

The `.github/workflows/ci.yml` defines a comprehensive CI/CD pipeline:

1. **Test Job**: Runs on Python 3.8, 3.9, 3.10, 3.11
   - Installs dependencies via `uv sync --extra dev`
   - Downloads spaCy and NLTK models
   - Runs linting, type checking, security scanning
   - Runs pytest with coverage
   - Uploads coverage to Codecov

2. **Quality Job**: Additional code quality checks
   - Ruff formatting and linting
   - Bandit security analysis
   - MyPy type checking

3. **Security Job**: Comprehensive security scanning
   - Trivy vulnerability scanner
   - Safety dependency checks
   - Semgrep static analysis

4. **Build Job**: Package building
   - Builds wheel and source distribution
   - Validates with twine

5. **Integration Job**: Integration and performance tests

## Important Development Notes

1. **Modern Tooling**: All configurations are in `pyproject.toml`. Use `uv` for dependency management and `ruff` for linting/formatting.

2. **File Paths**: Legacy scripts in `snapshot_automation/` contain hardcoded Windows paths that must be updated.

3. **API Keys Required**:
   - `ANTHROPIC_API_KEY` (always required)
   - `VOYAGEAI_API_KEY` (optional, for transcript_parallel.py)
   - `TAVILY_API_KEY` (optional, for transcript_tools.py)

4. **Test Coverage**: Current coverage is 27%. Coverage target in `pyproject.toml` is 80%.

5. **VTT File Format**: Input files must be valid WebVTT format with timestamps and speaker labels.

6. **Pre-commit Hooks**: The project uses extensive pre-commit hooks including:
   - ruff (linting and formatting)
   - mypy (type checking)
   - bandit (security)
   - pydocstyle (docstring conventions - Google style)
   - detect-secrets (secret scanning)

## Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Add RAG-specific dependencies
uv sync --extra rag

# Update all dependencies
uv sync

# Lock dependencies
uv lock
```

## Code Style Guidelines

- **Docstrings**: Google style (enforced by pydocstyle)
- **Type hints**: Required for all new code (checked by mypy with `--strict`)
- **Line length**: 88 characters (Black-compatible)
- **Import order**: Handled by ruff's isort integration
- **Security**: No secrets in code (checked by detect-secrets)

## Performance Considerations

1. **Large Files**: The `TranscriptProcessor` automatically applies memory optimizations for files > 10MB
2. **Model Loading**: Always use lazy loading functions from `model_loaders.py`
3. **Memory Monitoring**: Available via `MemoryOptimizer` class with context managers
4. **Chunking**: Not yet implemented but planned for very large transcripts
