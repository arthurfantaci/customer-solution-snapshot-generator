"""
Core transcript processing functionality with type hints and proper error handling.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from customer_snapshot.io.output_writer import OutputWriter
from customer_snapshot.io.vtt_reader import VTTReader
from customer_snapshot.monitoring.error_tracker import ErrorCategory
from customer_snapshot.utils.config import Config
from customer_snapshot.utils.error_handling import (
    handle_file_operations,
    with_error_tracking,
)
from customer_snapshot.utils.memory_optimizer import (
    MemoryOptimizer,
    memory_profile,
    start_memory_monitoring,
)
from customer_snapshot.utils.validators import validate_file_path

from .nlp_engine import NLPEngine


logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """
    Main class for processing VTT transcripts into customer solution snapshots.

    This class orchestrates the entire processing pipeline from reading VTT files
    to generating formatted output documents.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize the transcript processor.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config.get_default()
        self.config.validate()

        # Initialize memory optimizer
        self.memory_optimizer = MemoryOptimizer(self.config)

        # Start memory monitoring if configured
        if getattr(self.config, "enable_memory_monitoring", True):
            start_memory_monitoring(self.config, interval=30)

        self.vtt_reader = VTTReader(self.config)
        self.nlp_engine = NLPEngine(self.config)
        self.output_writer = OutputWriter(self.config)

        logger.info("TranscriptProcessor initialized successfully")

    @memory_profile
    @with_error_tracking(category=ErrorCategory.FILE_IO)
    @handle_file_operations
    def process_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        output_format: str = "markdown",
    ) -> Path:
        """
        Process a VTT file and generate formatted output.

        Args:
            input_path: Path to the input VTT file
            output_path: Path for output file (optional, auto-generated if None)
            output_format: Output format ('markdown' or 'html')

        Returns:
            Path to the generated output file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file format is invalid
            RuntimeError: If processing fails
        """
        # Enable memory optimizations for large files
        file_size = Path(input_path).stat().st_size / (1024 * 1024)  # MB
        if file_size > 10:  # Files larger than 10MB
            self.memory_optimizer.optimize_for_large_files()
            logger.info(f"Applied large file optimizations for {file_size:.1f} MB file")

        try:
            with self.memory_optimizer.memory_monitoring("File processing"):
                # Validate input file
                input_path = validate_file_path(input_path, allowed_extensions=[".vtt"])
                logger.info(f"Processing VTT file: {input_path}")

                # Generate output path if not provided
                if output_path is None:
                    output_path = self._generate_output_path(input_path, output_format)

                # Process the transcript through the pipeline
                processed_content = self._process_pipeline(input_path)

                if not processed_content.strip():
                    logger.warning("No content extracted from VTT file")
                    raise ValueError("No processable content found in VTT file")

                # Write output
                final_output_path = self.output_writer.write_output(
                    content=processed_content,
                    output_path=output_path,
                    format_type=output_format,
                )

                # Force cleanup after processing
                self.memory_optimizer.force_garbage_collection()

                logger.info(f"Processing completed successfully: {final_output_path}")
                return final_output_path

        except FileNotFoundError:
            logger.error(f"Input file not found: {input_path}")
            raise
        except ValueError as e:
            logger.error(f"Invalid input: {e}")
            raise
        except Exception as e:
            logger.error(f"Processing failed: {type(e).__name__}: {e}")
            raise RuntimeError("VTT processing failed") from e

    def _process_pipeline(self, input_path: Path) -> str:
        """
        Execute the complete processing pipeline.

        Args:
            input_path: Path to the VTT file

        Returns:
            Processed text content
        """
        # Step 1: Read VTT file
        raw_text = self.vtt_reader.read_vtt(input_path)
        logger.debug(f"Read {len(raw_text)} characters from VTT file")

        # Step 2: Clean and format text
        cleaned_text = self.nlp_engine.clean_text(raw_text)
        logger.debug("Text cleaning completed")

        # Step 3: Improve formatting
        formatted_text = self.nlp_engine.improve_formatting(cleaned_text)
        logger.debug("Text formatting completed")

        # Step 4: Enhance with NLP analysis
        enhanced_text = self.nlp_engine.enhance_content(formatted_text)
        logger.debug("NLP enhancement completed")

        # Step 5: Apply final formatting
        final_text = self._apply_final_formatting(enhanced_text)
        logger.debug("Final formatting completed")

        return final_text

    def _apply_final_formatting(self, text: str) -> str:
        """
        Apply final formatting steps to the text.

        Args:
            text: Text to format

        Returns:
            Finally formatted text
        """
        # Standardize quotes
        text = self.nlp_engine.standardize_quotes(text)

        # Split long sentences
        text = self.nlp_engine.split_long_sentences(text)

        return text

    def _generate_output_path(self, input_path: Path, output_format: str) -> Path:
        """
        Generate an output path based on input path and format.

        Args:
            input_path: Input file path
            output_format: Desired output format

        Returns:
            Generated output path
        """
        extension_map = {"markdown": ".md", "html": ".html"}

        extension = extension_map.get(output_format, ".md")
        output_path = input_path.parent / f"{input_path.stem}_processed{extension}"

        return output_path

    def extract_technical_terms(self, text: str) -> list[str]:
        """
        Extract technical terms from processed text.

        Args:
            text: Text to analyze

        Returns:
            List of identified technical terms
        """
        return self.nlp_engine.extract_technical_terms(text)

    def get_processing_stats(self) -> dict[str, Union[int, str]]:
        """
        Get statistics about the last processing operation.

        Returns:
            Dictionary containing processing statistics
        """
        return {
            "nlp_model": self.config.spacy_model,
            "chunk_size": self.config.chunk_size,
            "max_tokens": self.config.max_tokens,
            "last_processed": "N/A",  # Could track last processing time
        }

    def validate_configuration(self) -> bool:
        """
        Validate the current configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            self.config.validate()
            return True
        except ValueError:
            raise


class ProcessingError(Exception):
    """Custom exception for processing errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class ValidationError(ProcessingError):
    """Custom exception for validation errors."""

    pass
