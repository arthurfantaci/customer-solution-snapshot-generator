# User Guide - Customer Solution Snapshot Generator

Welcome to the Customer Solution Snapshot Generator! This guide will help you get started and make the most of this powerful tool for processing customer conversation transcripts.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Configuration](#configuration)
6. [Output Formats](#output-formats)
7. [Performance Tips](#performance-tips)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

## Introduction

The Customer Solution Snapshot Generator is an AI-powered tool that transforms VTT (WebVTT) transcript files from customer conversations into structured, actionable insights. It uses advanced NLP techniques and the Anthropic Claude API to:

- Extract key discussion points
- Identify customer pain points and requirements
- Summarize proposed solutions
- Generate formatted reports for easy sharing

### Key Features

- 🚀 **Fast Processing**: Optimized for speed and efficiency
- 🧠 **AI-Powered Analysis**: Uses Claude API for intelligent insights
- 📊 **Multiple Output Formats**: Markdown, HTML, and JSON
- 🔒 **Secure**: No data storage, API key encryption
- 📈 **Scalable**: Handles files from KB to GB in size
- 🛡️ **Enterprise-Ready**: Monitoring, error tracking, and health checks

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Anthropic API key
- 2GB RAM minimum (4GB recommended)
- Internet connection for API calls

### Installation

#### Option 1: Using pip

```bash
# Install the package
pip install customer-snapshot

# Download required NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
```

#### Option 2: Using Docker

```bash
# Pull the latest image
docker pull arthurfantaci/customer-snapshot-generator:latest

# Run with your API key
docker run -e ANTHROPIC_API_KEY=your_key_here \
  -v $(pwd)/input:/app/data/input \
  -v $(pwd)/output:/app/data/output \
  arthurfantaci/customer-snapshot-generator:latest
```

#### Option 3: From source

```bash
# Clone the repository
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator

# Install dependencies
pip install -r requirements.txt

# Install NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
```

### Setting Up Your API Key

The Anthropic API key is required for processing. Set it up using one of these methods:

```bash
# Method 1: Environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Method 2: .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env

# Method 3: Pass as parameter
customer-snapshot process input.vtt --api-key your-api-key-here
```

## Basic Usage

### Command Line Interface

The primary way to use the tool is through the command line:

```bash
# Basic usage - process a single file
customer-snapshot process transcript.vtt

# Specify output file
customer-snapshot process transcript.vtt --output report.md

# Choose output format
customer-snapshot process transcript.vtt --output-format html

# Process multiple files
customer-snapshot process *.vtt --output-dir reports/
```

### Docker Usage

```bash
# Process a single file
docker run -v $(pwd):/app/data \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  arthurfantaci/customer-snapshot-generator:latest \
  customer-snapshot process /app/data/transcript.vtt

# Process with custom output
docker run -v $(pwd)/input:/app/data/input \
  -v $(pwd)/output:/app/data/output \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  arthurfantaci/customer-snapshot-generator:latest \
  customer-snapshot process /app/data/input/transcript.vtt \
  --output /app/data/output/report.md
```

### Python API

```python
from customer_snapshot import TranscriptProcessor

# Initialize processor
processor = TranscriptProcessor()

# Process a file
output_path = processor.process_file(
    input_path="transcript.vtt",
    output_format="markdown"
)

print(f"Report generated: {output_path}")
```

## Advanced Features

### Batch Processing

Process multiple files efficiently:

```bash
# Process all VTT files in a directory
customer-snapshot batch process ./transcripts/ --output-dir ./reports/

# Process with pattern matching
customer-snapshot batch process ./data/*.vtt --output-format json

# Parallel processing (uses all CPU cores)
customer-snapshot batch process ./transcripts/ --parallel
```

### Custom Templates

Use custom templates for output formatting:

```bash
# Use a custom template
customer-snapshot process transcript.vtt --template ./templates/executive_summary.md

# Available built-in templates
customer-snapshot list-templates
```

### Memory Optimization

For large files, use memory-optimized mode:

```bash
# Enable memory optimization
customer-snapshot process large_transcript.vtt --optimize-memory

# Set custom chunk size (in MB)
customer-snapshot process huge_file.vtt --chunk-size 10
```

### Monitoring and Health Checks

Monitor the system health and performance:

```bash
# Check system health
customer-snapshot health

# View monitoring dashboard
python monitoring_dashboard.py --mode interactive

# Check error analysis
python error_analysis_dashboard.py --mode interactive
```

## Configuration

### Configuration File

Create a `config.yaml` file for persistent settings:

```yaml
# config.yaml
api:
  anthropic_api_key: ${ANTHROPIC_API_KEY}
  model: claude-3-sonnet-20240229
  max_retries: 3
  timeout: 30

processing:
  chunk_size: 500
  enable_caching: true
  cache_ttl: 3600
  
output:
  default_format: markdown
  include_timestamps: true
  include_speaker_labels: true
  
nlp:
  language: en
  extract_entities: true
  sentiment_analysis: true

monitoring:
  enabled: true
  error_tracking: true
  performance_tracking: true
```

Load custom configuration:

```bash
customer-snapshot process transcript.vtt --config config.yaml
```

### Environment Variables

Available environment variables:

```bash
# API Configuration
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Processing Options
CHUNK_SIZE=500
ENABLE_CACHING=true
CACHE_TTL=3600

# Output Options
DEFAULT_OUTPUT_FORMAT=markdown
OUTPUT_DIRECTORY=./output

# Monitoring
ENABLE_MONITORING=true
ENABLE_ERROR_TRACKING=true
LOG_LEVEL=INFO

# Performance
MAX_WORKERS=4
MEMORY_LIMIT_MB=2048
```

### Command Options

Complete list of command-line options:

```bash
customer-snapshot process --help

Options:
  --output, -o PATH           Output file path
  --output-format, -f FORMAT  Output format (markdown|html|json)
  --template, -t PATH         Custom template file
  --config, -c PATH          Configuration file
  --api-key KEY              Anthropic API key
  --model MODEL              Claude model to use
  --chunk-size SIZE          Processing chunk size in KB
  --optimize-memory          Enable memory optimization
  --parallel                 Enable parallel processing
  --verbose, -v              Verbose output
  --quiet, -q               Suppress output
  --dry-run                  Preview without processing
```

## Output Formats

### Markdown (Default)

Clean, readable format ideal for documentation:

```markdown
# Customer Solution Snapshot

**Date**: 2024-01-15
**Participants**: John Doe (Customer), Jane Smith (Sales Engineer)

## Executive Summary

The customer is looking for a solution to...

## Key Discussion Points

1. **Current Challenges**
   - Challenge 1
   - Challenge 2

2. **Requirements**
   - Requirement 1
   - Requirement 2

## Proposed Solutions

...
```

### HTML

Web-ready format with styling:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Customer Solution Snapshot</title>
    <style>
        /* Professional styling included */
    </style>
</head>
<body>
    <h1>Customer Solution Snapshot</h1>
    <!-- Formatted content -->
</body>
</html>
```

### JSON

Structured data for integration:

```json
{
  "metadata": {
    "date": "2024-01-15",
    "participants": ["John Doe", "Jane Smith"],
    "duration": "45:32"
  },
  "summary": {
    "executive_summary": "...",
    "key_points": [...],
    "action_items": [...]
  },
  "analysis": {
    "sentiment": "positive",
    "topics": ["cloud migration", "security"],
    "entities": {...}
  }
}
```

## Performance Tips

### Optimizing for Large Files

1. **Enable Memory Optimization**
   ```bash
   customer-snapshot process large_file.vtt --optimize-memory
   ```

2. **Adjust Chunk Size**
   ```bash
   # Larger chunks for better context (more memory)
   customer-snapshot process file.vtt --chunk-size 1000
   
   # Smaller chunks for less memory
   customer-snapshot process file.vtt --chunk-size 200
   ```

3. **Use Streaming Mode**
   ```bash
   # For files > 100MB
   customer-snapshot process huge_file.vtt --stream
   ```

### Batch Processing Tips

1. **Parallel Processing**
   ```bash
   # Use all CPU cores
   customer-snapshot batch process ./files/ --parallel
   
   # Limit workers
   customer-snapshot batch process ./files/ --max-workers 4
   ```

2. **Progress Tracking**
   ```bash
   # Show progress bar
   customer-snapshot batch process ./files/ --progress
   ```

3. **Resume Failed Jobs**
   ```bash
   # Resume from last checkpoint
   customer-snapshot batch process ./files/ --resume
   ```

### API Rate Limiting

Handle API rate limits gracefully:

```yaml
# config.yaml
api:
  rate_limit:
    requests_per_minute: 50
    retry_after_rate_limit: true
    backoff_factor: 2
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error**: `ANTHROPIC_API_KEY environment variable not set`

**Solution**:
```bash
# Set the API key
export ANTHROPIC_API_KEY="your-key-here"

# Or use .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

#### 2. Out of Memory

**Error**: `MemoryError: Unable to allocate array`

**Solution**:
```bash
# Enable memory optimization
customer-snapshot process file.vtt --optimize-memory --chunk-size 100
```

#### 3. VTT Parse Error

**Error**: `Invalid VTT format`

**Solution**:
- Ensure file starts with `WEBVTT`
- Check for proper timestamp format
- Validate UTF-8 encoding

#### 4. Network Timeout

**Error**: `API request timeout`

**Solution**:
```bash
# Increase timeout
customer-snapshot process file.vtt --timeout 60

# Enable retries
customer-snapshot process file.vtt --max-retries 5
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Maximum verbosity
customer-snapshot process file.vtt -vvv

# Debug specific component
export LOG_LEVEL=DEBUG
export DEBUG_COMPONENT=nlp_engine

# Save debug logs
customer-snapshot process file.vtt --debug --log-file debug.log
```

### Health Checks

Run comprehensive health checks:

```bash
# Basic health check
customer-snapshot health

# Detailed health check
python healthcheck.py --verbose

# Check specific components
customer-snapshot health --check api
customer-snapshot health --check nlp
customer-snapshot health --check filesystem
```

## Examples

### Example 1: Sales Call Analysis

```bash
# Process sales call transcript
customer-snapshot process sales_call_2024_01_15.vtt \
  --output sales_summary.md \
  --template templates/sales_call.md

# Result includes:
# - Customer pain points
# - Product requirements
# - Budget discussions
# - Next steps
```

### Example 2: Support Ticket Summary

```bash
# Process support conversation
customer-snapshot process support_ticket_12345.vtt \
  --output-format json \
  --include-metadata \
  --extract-action-items

# Result includes:
# - Issue description
# - Troubleshooting steps
# - Resolution
# - Follow-up actions
```

### Example 3: Executive Briefing

```bash
# Generate executive summary
customer-snapshot process quarterly_review.vtt \
  --template templates/executive_brief.md \
  --output exec_summary.pdf \
  --format pdf
```

### Example 4: Batch Processing Pipeline

```bash
#!/bin/bash
# process_transcripts.sh

# Set up environment
export ANTHROPIC_API_KEY="your-key"
export OUTPUT_DIR="./reports/$(date +%Y%m%d)"

# Create output directory
mkdir -p $OUTPUT_DIR

# Process all transcripts
customer-snapshot batch process ./transcripts/*.vtt \
  --output-dir $OUTPUT_DIR \
  --output-format markdown \
  --template templates/standard.md \
  --parallel \
  --progress

# Generate summary report
customer-snapshot report $OUTPUT_DIR \
  --output $OUTPUT_DIR/summary.html
```

## Best Practices

### 1. Organize Your Files

```
project/
├── input/
│   ├── 2024-01/
│   │   ├── call_001.vtt
│   │   └── call_002.vtt
│   └── 2024-02/
├── output/
│   ├── 2024-01/
│   └── 2024-02/
├── templates/
├── config.yaml
└── .env
```

### 2. Use Templates

Create reusable templates for consistent output:

```markdown
<!-- templates/standard.md -->
# Customer Interaction Summary

**Date**: {{ date }}
**Duration**: {{ duration }}
**Participants**: {{ participants }}

## Overview
{{ executive_summary }}

## Key Topics
{{ key_topics }}

## Action Items
{{ action_items }}

## Next Steps
{{ next_steps }}
```

### 3. Monitor Performance

Regularly check system performance:

```bash
# Weekly performance report
customer-snapshot performance report --last 7d

# Monitor error rates
python error_analysis_dashboard.py --mode report
```

### 4. Backup Important Data

```bash
# Backup processed reports
tar -czf reports_backup_$(date +%Y%m%d).tar.gz ./output/

# Backup configuration
cp config.yaml config.yaml.backup
```

## Getting Help

### Resources

- **Documentation**: https://arthurfantaci.github.io/customer-solution-snapshot-generator/
- **GitHub Issues**: https://github.com/arthurfantaci/customer-solution-snapshot-generator/issues
- **Examples**: See the `examples/` directory in the repository

### Support Commands

```bash
# Show version
customer-snapshot --version

# Show configuration
customer-snapshot config-info

# Run diagnostics
customer-snapshot diagnose

# Get help
customer-snapshot --help
customer-snapshot process --help
```

### Community

- Report bugs via GitHub Issues
- Request features via GitHub Discussions
- Contribute via Pull Requests

---

*Thank you for using Customer Solution Snapshot Generator! We hope this guide helps you make the most of the tool.*