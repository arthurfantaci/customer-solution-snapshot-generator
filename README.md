# Customer Solution Snapshot Generator

An automated Python tool that transforms video meeting transcripts (VTT files) into structured Customer Success Snapshot documents using NLP and AI technologies.

## Overview

This project streamlines the creation of customer success stories by automatically processing meeting transcripts to extract key information, insights, and metrics. It leverages advanced NLP techniques and AI models to generate comprehensive documentation from raw conversation data.

## Features

- **Transcript Processing**: Parse and clean VTT (WebVTT) caption files from recorded meetings
- **NLP Analysis**: Extract entities, topics, and technical terms using spaCy and NLTK
- **AI Enhancement**: Generate insights and summaries using Anthropic's Claude API
- **Multiple Output Formats**: Generate HTML or Markdown documentation
- **RAG System**: Query processed transcripts using vector similarity search
- **Flexible Architecture**: Multiple processing pipelines for different use cases
- **🚀 Lazy Loading**: Fast startup (~0.1s) with on-demand model loading
- **Modern Tooling**: Built with uv and ruff for maximum performance

## Quick Start

### Prerequisites

- Python 3.9+ (3.13 recommended)
- [uv](https://docs.astral.sh/uv/) package manager (10-100x faster than pip)

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator

# Install dependencies (creates .venv automatically)
uv sync

# Download spaCy language model
uv run python -m spacy download en_core_web_sm

# Configure API keys
cp snapshot_automation/.env.example snapshot_automation/.env
# Edit .env file and add your ANTHROPIC_API_KEY
```

**📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Usage

### Quick Start with Examples

1. Check out the examples directory to see sample inputs and outputs:
```bash
ls snapshot_automation/examples/
# Shows: sample_input.vtt, sample_output_markdown.md, sample_output_html.html,
#        Quest Enterprises_Kickoff_Transcript_Summary.md, claude_quickstart.py
```

2. View the examples README for detailed explanations:
```bash
cat snapshot_automation/examples/README.md
```

### Basic Transcript Processing

Process VTT transcript files using the modern CLI:

```bash
# Generate Markdown output (default)
uv run customer-snapshot process transcript.vtt

# Generate HTML output
uv run customer-snapshot process transcript.vtt -f html

# Specify custom output path
uv run customer-snapshot process transcript.vtt -o output.md

# Analyze transcript without processing
uv run customer-snapshot analyze transcript.vtt

# Validate VTT file format
uv run customer-snapshot process transcript.vtt --validate-only
```

**Test Claude API integration** (optional):
```bash
# Test direct Claude API connectivity
cd snapshot_automation/examples
uv run python claude_quickstart.py
```

### Advanced Features

#### RAG-Based Q&A System (Optional)
```bash
uv run python snapshot_automation/transcript_parallel.py
```
Query your transcripts using natural language with vector similarity search.
Requires `VOYAGEAI_API_KEY` in your `.env` file.

## Performance Features

### ⚡ Lazy Loading
All transcript processors use lazy loading for ML models:
- **Fast startup**: ~0.1s instead of ~5s (50x faster!)
- **Memory efficient**: 500MB+ savings when models not used
- **On-demand loading**: Models load automatically when functions are called
- **LRU caching**: Models cached after first load

### 🎯 Modern Development Tools
- **uv**: 10-100x faster than pip for installations
- **ruff**: Fast linter and formatter (replaces black, isort, flake8)
- **Pre-commit hooks**: Automatic code quality checks
- **Reproducible builds**: uv.lock for consistent environments

## Code Quality

```bash
# Format code
uv run ruff format .

# Check for linting issues
uv run ruff check .

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

## Output Structure

Generated Customer Solution Snapshots include 11 sections:

1. **Customer Information** - Company details and contacts
2. **Background** - Initial challenges and context
3. **Solution** - Implemented products/services
4. **Engagement Details** - Timeline and milestones
5. **Results** - Key achievements and metrics
6. **Adoption** - Usage statistics
7. **Financial Impact** - ROI and cost savings
8. **Long-Term Impact** - Strategic benefits
9. **Visuals** - Charts and graphics
10. **Additional Commentary** - Extra insights
11. **Executive Summary** - High-level overview

## Project Structure

```
customer-solution-snapshot-generator/
├── src/customer_snapshot/      # Main package (modern, well-structured)
│   ├── core/                   # Core processing
│   ├── io/                     # Input/output
│   ├── monitoring/             # Error tracking
│   └── utils/                  # Utilities
├── snapshot_automation/        # Legacy automation scripts
│   ├── model_loaders.py              # Lazy loading utilities
│   ├── transcript_pipeline.py        # Core pipeline
│   ├── transcript_parallel.py        # RAG Q&A (optional)
│   ├── examples/                     # Examples & demos
│   ├── template_files/               # Document templates
│   └── vtt_files/                    # Input/output directory
├── tests/                      # Test suites
│   ├── unit/
│   ├── integration/
│   └── manual/
├── scripts/                    # Utility scripts
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock file
└── .pre-commit-config.yaml     # Git hooks
```

## Key Technologies

- **NLP**: spaCy, NLTK, Transformers
- **AI/LLM**: Anthropic Claude, LangChain
- **Vector Search**: FAISS, VoyageAI
- **Transcript Parsing**: webvtt-py, pycaption
- **Package Management**: uv (Rust-based, ultra-fast)
- **Linting/Formatting**: ruff (Rust-based, 10-100x faster than alternatives)

## Example Use Case

The repository includes a real-world example of processing a Quest Enterprises project kickoff meeting:
- Customer: Quest Enterprises (Database Services)
- Project: Quiznos Analytics Cloud Platform implementation
- Timeline: July 2024
- Output: Structured snapshot documenting goals, milestones, and deliverables

## API Keys Required

- **ANTHROPIC_API_KEY** (required for all AI features)
- **VOYAGEAI_API_KEY** (optional, for RAG Q&A features)

Configure these in `snapshot_automation/.env` (copy from `.env.example`).

## Documentation

- **[SETUP.md](SETUP.md)** - Detailed development setup guide
- **[CLAUDE.md](CLAUDE.md)** - Guidelines for Claude Code development
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

## Development

### Adding Dependencies

```bash
# Add a production dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_validators.py

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Code Formatting

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .
```

## Contributing

Feel free to submit issues and enhancement requests!

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting: `uv run pytest && uv run ruff format .`
5. Submit a pull request

## License

This project is open source. Please check with the repository owner for specific license details.

## Acknowledgments

- Built with Anthropic's Claude API
- Uses LangChain for orchestration
- Leverages spaCy for NLP processing
- Modern tooling powered by uv and ruff

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ using modern Python tooling**
