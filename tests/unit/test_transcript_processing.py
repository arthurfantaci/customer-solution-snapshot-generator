"""
Unit tests for transcript processing functionality.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


# Add snapshot_automation to path for testing legacy code
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "snapshot_automation"))

from tests.fixtures import SIMPLE_VTT_CONTENT


class TestVTTReading:
    """Test cases for VTT file reading functionality."""

    @patch("webvtt.read")
    def test_read_vtt_success(self, mock_webvtt_read, temp_dir):
        """Test successful VTT file reading."""
        # Import after patching to avoid import-time execution
        from transcript_pipeline import read_vtt

        # Mock VTT captions
        mock_caption1 = Mock()
        mock_caption1.text = "Speaker 1: Hello world."
        mock_caption2 = Mock()
        mock_caption2.text = "Speaker 2: This is a test."

        mock_vtt = Mock()
        mock_vtt.__iter__ = lambda self: iter([mock_caption1, mock_caption2])
        mock_webvtt_read.return_value = mock_vtt

        test_file = temp_dir / "test.vtt"
        test_file.write_text(SIMPLE_VTT_CONTENT)

        result = read_vtt(str(test_file))

        assert "Speaker 1: Hello world." in result
        assert "Speaker 2: This is a test." in result
        mock_webvtt_read.assert_called_once()

    @patch("webvtt.read", side_effect=FileNotFoundError("File not found"))
    def test_read_vtt_file_not_found(self, mock_webvtt_read):
        """Test VTT reading with non-existent file."""
        from transcript_pipeline import read_vtt

        with pytest.raises(FileNotFoundError):
            read_vtt("/nonexistent/file.vtt")

    @patch("webvtt.read", side_effect=ValueError("Invalid VTT format"))
    def test_read_vtt_invalid_format(self, mock_webvtt_read, temp_dir):
        """Test VTT reading with invalid format."""
        from transcript_pipeline import read_vtt

        test_file = temp_dir / "invalid.vtt"
        test_file.write_text("Invalid VTT content")

        with pytest.raises(ValueError):
            read_vtt(str(test_file))


class TestTextCleaning:
    """Test cases for text cleaning functionality."""

    def test_clean_text_removes_speaker_labels(self):
        """Test that speaker labels are removed from text."""
        from transcript_pipeline import clean_text

        input_text = "Speaker 1: Hello world. Speaker 2: This is a test."
        result = clean_text(input_text)

        assert "Speaker 1:" not in result
        assert "Speaker 2:" not in result
        assert "Hello world." in result
        assert "This is a test." in result

    def test_clean_text_removes_timestamps(self):
        """Test that timestamps are removed from text."""
        from transcript_pipeline import clean_text

        input_text = "00:01:23.456 Hello world. 00:02:34.567 This is a test."
        result = clean_text(input_text)

        assert "00:01:23.456" not in result
        assert "00:02:34.567" not in result
        assert "Hello world." in result

    def test_clean_text_handles_empty_input(self):
        """Test text cleaning with empty input."""
        from transcript_pipeline import clean_text

        result = clean_text("")
        assert result == ""

    def test_clean_text_handles_whitespace(self):
        """Test text cleaning normalizes whitespace."""
        from transcript_pipeline import clean_text

        input_text = "   Multiple    spaces   between   words   "
        result = clean_text(input_text)

        # Should normalize to single spaces
        assert "Multiple spaces between words" in result.strip()


class TestTextFormatting:
    """Test cases for text formatting functionality."""

    def test_improve_formatting_basic(self):
        """Test basic text formatting improvements."""
        from transcript_pipeline import improve_formatting

        input_text = "hello world. this is a test sentence."
        result = improve_formatting(input_text)

        # Should capitalize sentences
        assert result.startswith("Hello world.")
        assert "This is a test sentence." in result

    def test_standardize_quotes(self):
        """Test quote standardization."""
        from transcript_pipeline import standardize_quotes

        input_text = "He said 'hello' and then 'goodbye'."
        result = standardize_quotes(input_text)

        # Should convert single quotes to double quotes
        assert '"hello"' in result
        assert '"goodbye"' in result
        assert "'" not in result

    def test_split_long_sentences(self):
        """Test splitting of very long sentences."""
        from transcript_pipeline import split_long_sentences

        # Create a long sentence with multiple clauses
        long_sentence = (
            "This is a very long sentence that contains multiple clauses "
            "and should be split into shorter sentences for better readability "
            "and understanding by the reader who might find it difficult to follow."
        )

        result = split_long_sentences(long_sentence)

        # Should be split into multiple sentences
        sentence_count = result.count(".")
        assert sentence_count > 1


class TestTechnicalTermExtraction:
    """Test cases for technical term extraction."""

    @patch("transcript_pipeline.nlp")
    def test_extract_technical_terms(self, mock_nlp):
        """Test extraction of technical terms from text."""
        from transcript_pipeline import extract_technical_terms

        # Mock spaCy document
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

        mock_nlp.return_value = mock_doc

        input_text = "We use Qlik Cloud Platform for data analytics."
        result = extract_technical_terms(input_text)

        assert isinstance(result, list)
        mock_nlp.assert_called_once_with(input_text)

    def test_extract_technical_terms_empty_input(self):
        """Test technical term extraction with empty input."""
        from transcript_pipeline import extract_technical_terms

        result = extract_technical_terms("")
        assert result == []


class TestProcessingPipeline:
    """Test cases for the main processing pipeline."""

    @patch("transcript_pipeline.read_vtt")
    @patch("transcript_pipeline.clean_text")
    @patch("transcript_pipeline.improve_formatting")
    @patch("transcript_pipeline.enhance_content")
    @patch("transcript_pipeline.standardize_quotes")
    @patch("transcript_pipeline.split_long_sentences")
    @patch("transcript_pipeline.extract_technical_terms")
    @patch("transcript_pipeline.output_result")
    def test_process_vtt_success(
        self,
        mock_output,
        mock_extract,
        mock_split,
        mock_standardize,
        mock_enhance,
        mock_improve,
        mock_clean,
        mock_read,
    ):
        """Test successful VTT processing pipeline."""
        from transcript_pipeline import process_vtt

        # Setup mocks
        mock_read.return_value = "Raw VTT text"
        mock_clean.return_value = "Cleaned text"
        mock_improve.return_value = "Improved text"
        mock_enhance.return_value = "Enhanced text"
        mock_standardize.return_value = "Standardized text"
        mock_split.return_value = "Split text"
        mock_extract.return_value = ["term1", "term2"]

        # Test the pipeline
        process_vtt("input.vtt", "output.md")

        # Verify all steps were called
        mock_read.assert_called_once_with("input.vtt")
        mock_clean.assert_called_once_with("Raw VTT text")
        mock_improve.assert_called_once_with("Cleaned text")
        mock_enhance.assert_called_once_with("Improved text")
        mock_standardize.assert_called_once_with("Enhanced text")
        mock_split.assert_called_once_with("Standardized text")
        mock_extract.assert_called_once_with("Split text")
        mock_output.assert_called_once_with("Split text", "output.md")

    @patch("transcript_pipeline.read_vtt", return_value="")
    @patch("transcript_pipeline.output_result")
    def test_process_vtt_empty_input(self, mock_output, mock_read):
        """Test processing pipeline with empty VTT content."""
        from transcript_pipeline import process_vtt

        process_vtt("empty.vtt", "output.md")

        mock_read.assert_called_once()
        # Should return early, not call output
        mock_output.assert_not_called()

    @patch(
        "transcript_pipeline.read_vtt", side_effect=FileNotFoundError("File not found")
    )
    def test_process_vtt_file_not_found(self, mock_read):
        """Test processing pipeline with file not found error."""
        from transcript_pipeline import process_vtt

        with pytest.raises(RuntimeError, match="VTT processing failed"):
            process_vtt("missing.vtt", "output.md")

    @patch("transcript_pipeline.read_vtt", side_effect=ValueError("Invalid file"))
    def test_process_vtt_invalid_file(self, mock_read):
        """Test processing pipeline with invalid file error."""
        from transcript_pipeline import process_vtt

        with pytest.raises(RuntimeError, match="VTT processing failed"):
            process_vtt("invalid.vtt", "output.md")


class TestOutputGeneration:
    """Test cases for output generation."""

    @patch("transcript_pipeline.safe_file_write")
    @patch("transcript_pipeline.sanitize_filename")
    def test_output_result_success(self, mock_sanitize, mock_write):
        """Test successful output generation."""
        from transcript_pipeline import output_result

        mock_sanitize.return_value = "sanitized_output.md"
        test_content = "# Test Output\n\nThis is test content."

        output_result(test_content, "/path/to/output.md")

        mock_sanitize.assert_called_once_with("output.md")
        mock_write.assert_called_once()

    @patch(
        "transcript_pipeline.safe_file_write",
        side_effect=PermissionError("Permission denied"),
    )
    def test_output_result_permission_error(self, mock_write):
        """Test output generation with permission error."""
        from transcript_pipeline import output_result

        with pytest.raises(PermissionError):
            output_result("content", "/protected/output.md")


@pytest.mark.integration
class TestEndToEndProcessing:
    """Integration tests for end-to-end processing."""

    @patch("transcript_pipeline.nlp")
    @patch("transcript_pipeline.safe_file_write")
    def test_end_to_end_processing(self, mock_write, mock_nlp, sample_vtt_file):
        """Test complete end-to-end processing workflow."""
        from transcript_pipeline import process_vtt

        # Mock NLP pipeline
        mock_doc = Mock()
        mock_doc.ents = []
        mock_doc.noun_chunks = []
        mock_nlp.return_value = mock_doc

        output_file = str(sample_vtt_file.parent / "output.md")

        # Should complete without errors
        process_vtt(str(sample_vtt_file), output_file)

        # Verify output was written
        mock_write.assert_called_once()
