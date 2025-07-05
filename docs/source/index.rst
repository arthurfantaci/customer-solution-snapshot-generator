Customer Solution Snapshot Generator Documentation
==================================================

.. image:: https://img.shields.io/badge/version-0.1.0-blue.svg
   :target: #
   :alt: Version

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: #
   :alt: License

An automated Python tool that transforms video meeting transcripts (VTT files) into structured Customer Success Snapshot documents using NLP and AI technologies.

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   quickstart
   user_guide
   cli_reference
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/core
   api/io
   api/utils
   api/cli

.. toctree::
   :maxdepth: 2
   :caption: Development:

   architecture
   contributing
   testing
   deployment

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources:

   changelog
   troubleshooting
   faq
   glossary

Overview
--------

The Customer Solution Snapshot Generator is a comprehensive tool designed to automate the creation of professional customer success documentation from meeting transcripts. It leverages advanced Natural Language Processing (NLP) and AI technologies to extract key insights, identify technical terms, and structure information into readable customer success stories.

Key Features
------------

🎯 **Intelligent Processing**
   - Advanced NLP analysis using spaCy and NLTK
   - AI-powered content enhancement with Anthropic's Claude
   - Automatic entity extraction and topic identification

📄 **Multiple Output Formats**
   - Professional Markdown documentation
   - Styled HTML reports with embedded CSS
   - Customizable templates and formatting

🔒 **Enterprise Security**
   - Secure file handling with validation
   - API key protection and sanitization
   - Input validation and path traversal protection

🧪 **Production Ready**
   - Comprehensive testing suite with 80%+ coverage
   - Automated CI/CD pipeline with quality gates
   - Professional CLI interface with Click

⚙️ **Configurable & Scalable**
   - Environment-based configuration
   - Docker containerization support
   - Performance monitoring and optimization

Quick Start
-----------

1. **Installation**

   .. code-block:: bash

      pip install customer-solution-snapshot-generator

2. **Configuration**

   .. code-block:: bash

      # Copy environment template
      cp .env.example .env
      
      # Add your API keys
      echo "ANTHROPIC_API_KEY=your_key_here" >> .env

3. **Basic Usage**

   .. code-block:: bash

      # Process a VTT file
      customer-snapshot process transcript.vtt
      
      # Generate HTML output
      customer-snapshot process transcript.vtt -f html -o report.html

4. **Python API**

   .. code-block:: python

      from customer_snapshot import TranscriptProcessor, Config
      
      # Initialize processor
      config = Config.get_default()
      processor = TranscriptProcessor(config)
      
      # Process transcript
      output_path = processor.process_file("transcript.vtt")
      print(f"Generated: {output_path}")

Architecture Overview
--------------------

The system follows a modular architecture with clear separation of concerns:

.. code-block:: text

    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
    │   CLI/API       │    │  Core Processor  │    │  Output Writer  │
    │                 │────│                  │────│                 │
    │ - Click CLI     │    │ - Orchestration  │    │ - Markdown      │
    │ - Python API    │    │ - Error Handling │    │ - HTML          │
    └─────────────────┘    └──────────────────┘    └─────────────────┘
             │                        │                        │
             │                        │                        │
    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
    │   VTT Reader    │    │   NLP Engine     │    │  Configuration  │
    │                 │    │                  │    │                 │
    │ - File parsing  │    │ - spaCy/NLTK     │    │ - Environment   │
    │ - Validation    │    │ - Entity extract │    │ - Validation    │
    └─────────────────┘    └──────────────────┘    └─────────────────┘

Use Cases
---------

**Customer Success Teams**
   Generate professional success stories from customer meeting recordings

**Sales Teams**
   Create compelling case studies from prospect interactions

**Project Managers**
   Document project outcomes and stakeholder feedback

**Support Teams**
   Transform support call transcripts into knowledge base articles

Support & Community
------------------

- **GitHub Repository**: https://github.com/arthurfantaci/customer-solution-snapshot-generator
- **Issue Tracker**: https://github.com/arthurfantaci/customer-solution-snapshot-generator/issues
- **Documentation**: https://customer-snapshot-generator.readthedocs.io/

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`