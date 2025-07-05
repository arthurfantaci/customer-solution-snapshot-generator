# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based system that generates Customer Success Snapshot documents from video meeting transcripts (VTT files). It uses NLP processing and AI models (primarily Anthropic's Claude) to extract insights, entities, and structured information from transcripts.

## Commands

### Setup Dependencies
Since there's no requirements.txt, install dependencies manually:
```bash
# Core dependencies
pip install nltk spacy webvtt-py pycaption markdown transformers
pip install anthropic langchain langchain-anthropic langchain-community
pip install langchain-openai langchain-voyageai python-dotenv faiss-cpu coreferee

# Download spaCy model
python -m spacy download en_core_web_sm
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
# Main processors
python snapshot_automation/vtt_to_html_processor.py      # VTT → HTML with NLP analysis
python snapshot_automation/vtt_to_markdown_processor.py   # VTT → Markdown with entities

# Utilities
python snapshot_automation/transcript_parallel.py  # RAG-based Q&A system
python snapshot_automation/transcript_tools.py     # LangChain agent for analysis
python snapshot_automation/converter.py            # Simple VTT → Markdown
```

**Note**: All scripts have hardcoded file paths that need updating before running.

## Architecture

### Core Processing Flow
1. **Input**: VTT transcript files from customer meetings
2. **Processing Pipeline**:
   - Parse VTT → Clean text → Extract entities/topics → Generate structured output
   - Uses spaCy for NLP, NLTK for tokenization, transformers for summarization
3. **Output**: HTML/Markdown documents structured as Customer Solution Snapshots

### Key Modules

- **vtt_to_html_processor.py/vtt_to_markdown_processor.py**: Primary transcript processors with different output formats
- **transcript_parallel.py**: RAG implementation using FAISS and VoyageAI embeddings for contextual Q&A
- **transcript_tools.py**: LangChain ReAct agent with web search and calculation tools
- **examples/claude_quickstart.py**: Direct Claude API integration example and test script

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

## Important Development Notes

1. **File Path Updates Required**: All scripts contain hardcoded Windows paths (e.g., `C:/Users/DQA/...`) that must be updated to your local paths.

2. **API Keys Required**:
   - `ANTHROPIC_API_KEY` (always required)
   - `VOYAGEAI_API_KEY` (for transcript_parallel.py)
   - `TAVILY_API_KEY` (for transcript_tools.py)

3. **No Test Suite**: Project has no automated tests. Verify changes by running scripts manually.

4. **Dependencies Not Managed**: No requirements.txt or pyproject.toml. Track any new dependencies added.

5. **VTT File Format**: Input files must be valid WebVTT format with timestamps and speaker labels.

6. **Template Files**: Document templates and AI prompts are in `snapshot_automation/template_files/`