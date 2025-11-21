# Getting Started with Customer Solution Snapshot Generator

Welcome! This guide will help you get up and running with the Customer Solution Snapshot Generator quickly and efficiently.

## What is Customer Solution Snapshot Generator?

Customer Solution Snapshot Generator is an AI-powered tool that transforms customer conversation transcripts (VTT format) into structured, actionable business insights. It uses advanced NLP and the Anthropic Claude API to extract key information from sales calls, support tickets, customer interviews, and more.

### Key Benefits

- 🚀 **Save Time**: Automate transcript analysis that typically takes hours
- 🎯 **Extract Insights**: Identify pain points, requirements, and opportunities
- 📊 **Structured Output**: Get consistent, professional reports
- 🔒 **Secure**: No data storage, encrypted API communications
- 📈 **Scalable**: Process single files or large batches

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- **Anthropic API key** (get one from [console.anthropic.com](https://console.anthropic.com))
- **VTT transcript files** to process
- **2GB RAM minimum** (4GB recommended for large files)

## Quick Installation

Choose the installation method that works best for you:

### Option 1: Docker (Recommended for beginners)

```bash
# Pull the latest image
docker pull arthurfantaci/customer-snapshot-generator:latest

# Run with your API key
docker run -e ANTHROPIC_API_KEY=your_api_key_here \
  -v $(pwd)/input:/app/data/input \
  -v $(pwd)/output:/app/data/output \
  arthurfantaci/customer-snapshot-generator:latest \
  customer-snapshot process /app/data/input/your_file.vtt
```

### Option 2: pip Installation

```bash
# Install the package
pip install customer-snapshot

# Download required NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
```

### Option 3: From Source

```bash
# Clone the repository
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
```

## Initial Setup

### 1. Configure Your API Key

Set up your Anthropic API key using one of these methods:

```bash
# Method 1: Environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Method 2: .env file (create in your project directory)
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env

# Method 3: Configuration file
cat > config.yaml << EOF
api:
  anthropic_api_key: your-api-key-here
  model: claude-3-sonnet-20240229
EOF
```

### 2. Verify Installation

Test your installation:

```bash
# Check version
customer-snapshot --version

# Run health check
customer-snapshot health

# View configuration
customer-snapshot config-info
```

## Your First Analysis

Let's process your first transcript! Here's a step-by-step walkthrough:

### Step 1: Prepare Your Transcript

You need a VTT (WebVTT) file. If you don't have one, create a sample:

```vtt
WEBVTT

00:00:00.000 --> 00:00:15.000
John (Customer): Hi there, we're looking into upgrading our current CRM system. We've been having some performance issues.

00:00:15.000 --> 00:00:30.000
Sarah (Sales): I'd be happy to help you with that. Can you tell me more about the specific performance issues you're experiencing?

00:00:30.000 --> 00:00:50.000
John (Customer): The system is really slow when we're trying to pull reports, especially for our quarterly reviews. It sometimes takes 20-30 minutes.

00:00:50.000 --> 00:01:10.000
Sarah (Sales): That's definitely frustrating. How many users do you have on the system currently, and what's your data volume like?

00:01:10.000 --> 00:01:30.000
John (Customer): We have about 50 sales reps using it daily, and we've got about 5 years of customer data in there.
```

Save this as `sample_call.vtt`.

### Step 2: Process the Transcript

Run your first analysis:

```bash
# Basic processing
customer-snapshot process sample_call.vtt

# With custom output file
customer-snapshot process sample_call.vtt --output crm_upgrade_analysis.md

# Specify output format
customer-snapshot process sample_call.vtt --output-format html
```

### Step 3: Review the Results

Open the generated file (e.g., `sample_call_analysis.md`) to see your analysis:

```markdown
# Customer Solution Snapshot

**Date**: 2024-01-15
**Participants**: John (Customer), Sarah (Sales)
**Duration**: 1:30

## Executive Summary

Customer is experiencing significant performance issues with their current CRM system, particularly with report generation taking 20-30 minutes. They have 50 daily users and 5 years of historical data, indicating a substantial database that may require optimization or migration to a more robust solution.

## Key Discussion Points

1. **Performance Issues**
   - Report generation extremely slow (20-30 minutes)
   - Impact on quarterly reviews
   - System responsiveness concerns

2. **Current Environment**
   - 50 daily sales users
   - 5 years of accumulated customer data
   - Heavy usage patterns

## Pain Points Identified

- **System Performance**: Critical slowness affecting business operations
- **User Productivity**: Sales team efficiency impacted by slow reports
- **Business Processes**: Quarterly reviews hindered by system limitations

## Potential Solutions

- Database optimization and indexing
- Migration to more scalable CRM platform
- Data archiving strategy for historical records
- Performance monitoring and alerting

## Next Steps

- Conduct detailed technical assessment
- Analyze current data volume and structure
- Provide scalability recommendations
- Prepare upgrade proposal with timeline
```

## Common Use Cases

Here are some popular ways to use Customer Solution Snapshot Generator:

### Sales Call Analysis

```bash
# Process sales call with sales-specific template
customer-snapshot process sales_call.vtt \
  --template sales_analysis \
  --extract-action-items \
  --identify-competitors
```

### Support Ticket Summary

```bash
# Process support call with technical focus
customer-snapshot process support_call.vtt \
  --template support_summary \
  --extract-resolution-steps \
  --identify-root-cause
```

### Customer Interview Insights

```bash
# Process customer interview for product insights
customer-snapshot process customer_interview.vtt \
  --template product_feedback \
  --extract-feature-requests \
  --sentiment-analysis
```

### Batch Processing

```bash
# Process multiple files at once
customer-snapshot batch process ./transcripts/ \
  --output-dir ./analyses/ \
  --parallel \
  --progress
```

## Configuration Options

### Basic Configuration

Create a `config.yaml` file for persistent settings:

```yaml
# config.yaml
api:
  anthropic_api_key: ${ANTHROPIC_API_KEY}
  model: claude-3-sonnet-20240229
  timeout: 30

processing:
  chunk_size: 500
  enable_caching: true

output:
  default_format: markdown
  include_timestamps: true

monitoring:
  enabled: true
```

### Command Line Options

Customize processing with command-line options:

```bash
# Processing options
customer-snapshot process file.vtt \
  --chunk-size 1000 \
  --timeout 60 \
  --model claude-3-haiku-20240307

# Output options
customer-snapshot process file.vtt \
  --output-format json \
  --include-metadata \
  --extract-entities

# Performance options
customer-snapshot process file.vtt \
  --optimize-memory \
  --parallel \
  --verbose
```

## Monitoring and Health

### Check System Health

```bash
# Basic health check
customer-snapshot health

# Detailed health check
python healthcheck.py --verbose

# Interactive monitoring dashboard
python monitoring_dashboard.py --mode interactive
```

### View Processing Logs

```bash
# Enable verbose logging
customer-snapshot process file.vtt -vvv

# View log files
tail -f ~/.customer_snapshot/logs/app.log
```

## Next Steps

Now that you've successfully processed your first transcript, here are some next steps:

### 1. Explore Advanced Features

- **Custom Templates**: Create templates for your specific use cases
- **Batch Processing**: Process multiple files efficiently
- **API Integration**: Integrate with your existing systems
- **Performance Optimization**: Tune for your workload

### 2. Read the Documentation

- [User Guide](docs/USER_GUIDE.md) - Comprehensive usage guide
- [Advanced Features](docs/tutorials/ADVANCED_FEATURES.md) - Power user features
- [Use Cases](docs/tutorials/USE_CASES.md) - Real-world examples
- [API Documentation](docs/tutorials/API_EXAMPLES.md) - Integration examples

### 3. Join the Community

- **GitHub**: [Report issues and contribute](https://github.com/arthurfantaci/customer-solution-snapshot-generator)
- **Discussions**: [Ask questions and share ideas](https://github.com/arthurfantaci/customer-solution-snapshot-generator/discussions)

## Troubleshooting

If you encounter issues, here are quick solutions for common problems:

### Installation Issues

```bash
# Python version check
python --version  # Should be 3.8+

# Update pip
pip install --upgrade pip

# Install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install customer-snapshot
```

### API Key Issues

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages
```

### Processing Issues

```bash
# Check file format
head -n 1 your_file.vtt  # Should show "WEBVTT"

# Validate file
customer-snapshot validate your_file.vtt

# Enable debug mode
customer-snapshot process your_file.vtt --debug
```

### Performance Issues

```bash
# Enable memory optimization
customer-snapshot process large_file.vtt --optimize-memory

# Reduce chunk size
customer-snapshot process file.vtt --chunk-size 200

# Use faster model
customer-snapshot process file.vtt --model claude-3-haiku-20240307
```

## Support

If you need help:

1. **Check the [Troubleshooting Guide](docs/tutorials/TROUBLESHOOTING.md)**
2. **Search [existing issues](https://github.com/arthurfantaci/customer-solution-snapshot-generator/issues)**
3. **Create a new issue** with details about your problem

Include this information when asking for help:

```bash
# Generate diagnostic information
customer-snapshot diagnose --full > diagnostic_info.txt
```

## What's Next?

Congratulations! You've successfully set up and used Customer Solution Snapshot Generator. Here are some suggestions for what to do next:

- **Process real transcripts** from your business
- **Create custom templates** for your specific use cases
- **Set up batch processing** for multiple files
- **Integrate with your existing tools** using the API
- **Explore monitoring and analytics** features

Happy analyzing! 🚀

---

*For more detailed information, see the [complete User Guide](docs/USER_GUIDE.md) or explore our [tutorials](docs/tutorials/).*
