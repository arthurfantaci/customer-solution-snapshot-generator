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

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/arthurfantaci/customer-solution-snapshot-generator.git
cd customer-solution-snapshot-generator
```

2. Install dependencies:
```bash
# Core dependencies
pip install nltk spacy webvtt-py pycaption markdown transformers
pip install anthropic langchain langchain-anthropic langchain-community
pip install langchain-voyageai python-dotenv faiss-cpu coreferee

# Download spaCy language model
python -m spacy download en_core_web_sm
```

3. Set up environment variables:
```bash
cd snapshot_automation
cp .env.example .env
```

4. Add your API keys to `.env`:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
VOYAGEAI_API_KEY=your_voyage_api_key_here  # Optional: for RAG features
TAVILY_API_KEY=your_tavily_api_key_here    # Optional: for web search
```

## Usage

### Quick Start with Examples

1. Check out the examples directory to see sample inputs and outputs:
```bash
ls snapshot_automation/examples/
# Shows: sample_input.vtt, sample_output_markdown.md, sample_output_html.html, Percona_Kickoff_Transcript_Summary.md
```

2. View the examples README for detailed explanations:
```bash
cat snapshot_automation/examples/README.md
```

### Basic Transcript Processing

1. Place your VTT transcript files in `snapshot_automation/vtt_files/`

2. Run the main processor:
```bash
# Generate HTML output with NLP analysis
python snapshot_automation/vtt_to_html_processor.py

# Generate Markdown output
python snapshot_automation/vtt_to_markdown_processor.py
```

**Note**: Update the hardcoded file paths in the scripts to match your system.

### Advanced Features

#### RAG-Based Q&A System
```bash
python snapshot_automation/transcript_parallel.py
```
Query your transcripts using natural language with vector similarity search.

#### AI Agent with Tools
```bash
python snapshot_automation/transcript_tools.py
```
Use LangChain agents with web search and calculation capabilities.

#### Simple Conversion
```bash
python snapshot_automation/converter.py
```
Convert VTT files to Markdown format with speaker timestamps.

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
snapshot_automation/
├── vtt_to_html_processor.py      # VTT to HTML processor
├── vtt_to_markdown_processor.py  # VTT to Markdown processor
├── transcript_parallel.py  # RAG implementation
├── transcript_tools.py     # LangChain agents
├── transcript_pipeline.py  # Simple processing pipeline
├── converter.py           # VTT to Markdown converter
├── extract_text.py        # Text extraction utilities
├── claude_quickstart.py   # Claude API test
├── examples/              # Example inputs and outputs
├── template_files/        # Document templates
├── vtt_files/            # Input/output directory
└── .env.example          # Environment template
```

## Key Technologies

- **NLP**: spaCy, NLTK, Transformers
- **AI/LLM**: Anthropic Claude, LangChain
- **Vector Search**: FAISS, VoyageAI
- **Transcript Parsing**: webvtt-py, pycaption

## Example Use Case

The repository includes a real-world example of processing a Percona project kickoff meeting:
- Customer: Percona (Database Services)
- Project: Qlik Cloud Platform implementation
- Timeline: July 2024
- Output: Structured snapshot documenting goals, milestones, and deliverables

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Please check with the repository owner for specific license details.

## Acknowledgments

- Built with Anthropic's Claude API
- Uses LangChain for orchestration
- Leverages spaCy for NLP processing