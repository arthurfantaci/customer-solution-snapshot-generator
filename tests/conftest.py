"""
Pytest configuration and shared fixtures.
"""
import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from unittest.mock import Mock

# Add src to Python path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from customer_snapshot.utils.config import Config


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_vtt_content() -> str:
    """Sample VTT content for testing."""
    return """WEBVTT

00:00:01.000 --> 00:00:05.000
Speaker 1: Welcome to the Qlik implementation meeting.

00:00:05.000 --> 00:00:10.000
Speaker 2: Thank you for joining us today. We'll discuss the project timeline.

00:00:10.000 --> 00:00:15.000
Speaker 1: The main goal is to implement Qlik Cloud Platform for data analytics.

00:00:15.000 --> 00:00:20.000
Speaker 2: We need to resolve ServiceNow data connector issues first.

00:00:20.000 --> 00:00:25.000
Speaker 1: The project will be completed in two phases over 80 hours.
"""


@pytest.fixture
def sample_vtt_file(temp_dir: Path, sample_vtt_content: str) -> Path:
    """Create a sample VTT file for testing."""
    vtt_file = temp_dir / "test_transcript.vtt"
    vtt_file.write_text(sample_vtt_content)
    return vtt_file


@pytest.fixture
def test_config(temp_dir: Path) -> Config:
    """Create a test configuration."""
    # Set test environment variables
    os.environ["ANTHROPIC_API_KEY"] = "test_key_123"
    os.environ["VOYAGEAI_API_KEY"] = "test_voyage_key"
    os.environ["MAX_FILE_SIZE"] = "1048576"  # 1MB for testing
    os.environ["DEBUG"] = "true"
    
    config = Config()
    # Override directories to use temp directory
    config.data_dir = temp_dir / "data"
    config.input_dir = temp_dir / "data" / "input"
    config.output_dir = temp_dir / "data" / "output"
    config.templates_dir = temp_dir / "data" / "templates"
    
    # Create test directories
    config._ensure_directories()
    
    return config


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="This is a test response from Claude.")]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_spacy_nlp():
    """Mock spaCy NLP pipeline for testing."""
    mock_nlp = Mock()
    mock_doc = Mock()
    
    # Mock entities
    mock_entity = Mock()
    mock_entity.text = "Qlik Cloud Platform"
    mock_entity.label_ = "PRODUCT"
    mock_doc.ents = [mock_entity]
    
    # Mock noun chunks
    mock_chunk = Mock()
    mock_chunk.text = "data analytics"
    mock_doc.noun_chunks = [mock_chunk]
    
    # Mock tokens
    mock_token = Mock()
    mock_token.is_stop = False
    mock_token.pos_ = "NOUN"
    mock_token.lemma_ = "analytics"
    mock_doc.__iter__ = lambda self: iter([mock_token])
    
    mock_nlp.return_value = mock_doc
    return mock_nlp


@pytest.fixture
def sample_processed_text() -> str:
    """Sample processed text output for testing."""
    return """# Meeting Transcript Summary

**Participants:** Speaker 1, Speaker 2

## Key Discussion Points

The meeting focused on implementing Qlik Cloud Platform for data analytics. The main objectives include:

- Resolving ServiceNow data connector issues
- Completing the project in two phases
- Allocating 80 hours for implementation

## Technical Terms Identified
- Qlik Cloud Platform
- ServiceNow
- data analytics
- data connector

## Next Steps
Phase 1 and Phase 2 implementation as discussed.
"""


@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment variables after each test."""
    yield
    # Clean up test environment variables
    test_vars = [
        "ANTHROPIC_API_KEY", "VOYAGEAI_API_KEY", "MAX_FILE_SIZE", 
        "DEBUG", "LOG_LEVEL", "CHUNK_SIZE"
    ]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]