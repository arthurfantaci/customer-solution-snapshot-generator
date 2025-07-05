"""
VTT file reading functionality.
"""
import logging
from pathlib import Path
from typing import Union, Iterator

import webvtt

from ..utils.config import Config
from ..utils.validators import validate_file_path
from ..utils.memory_optimizer import StreamingVTTReader, memory_profile

logger = logging.getLogger(__name__)


class VTTReader:
    """
    Reader for WebVTT (Video Text Track) files.
    
    Handles secure reading and parsing of VTT files with proper
    error handling and validation.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the VTT reader.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.streaming_reader = StreamingVTTReader()
        logger.debug("VTTReader initialized")

    @memory_profile
    def read_vtt(self, file_path: Union[str, Path]) -> str:
        """
        Read and parse a VTT file.
        
        Args:
            file_path: Path to the VTT file
            
        Returns:
            Combined text content from all captions
            
        Raises:
            FileNotFoundError: If the VTT file doesn't exist
            ValueError: If the VTT file is malformed
            RuntimeError: If reading fails for other reasons
        """
        try:
            # Validate file path and type
            validated_path = validate_file_path(
                file_path, 
                allowed_extensions=['.vtt'],
                max_size=self.config.max_file_size
            )
            
            logger.info(f"Reading VTT file: {validated_path}")
            
            # Check file size to determine reading strategy
            file_size = validated_path.stat().st_size / (1024 * 1024)  # MB
            
            if file_size > 10:  # Use streaming for large files
                logger.info(f"Using streaming reader for large file ({file_size:.1f} MB)")
                return self.read_vtt_streaming(validated_path)
            else:
                # Use standard reading for smaller files
                vtt = webvtt.read(str(validated_path))
                
                # Extract text from all captions
                caption_texts = []
                for caption in vtt:
                    if caption.text.strip():  # Skip empty captions
                        caption_texts.append(caption.text.strip())
                
                # Combine all caption text
                full_text = " ".join(caption_texts)
                
                logger.info(f"Successfully read VTT file with {len(vtt)} captions")
                logger.debug(f"Extracted {len(full_text)} characters of text")
                
                return full_text
            
        except FileNotFoundError:
            logger.error(f"VTT file not found: {file_path}")
            raise
        except ValueError as e:
            logger.error(f"Invalid VTT file format: {e}")
            raise ValueError(f"Invalid VTT file: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error reading VTT file: {type(e).__name__}: {e}")
            raise RuntimeError("Failed to read VTT file") from e
    
    def read_vtt_streaming(self, file_path: Union[str, Path]) -> str:
        """
        Read VTT file using memory-efficient streaming.
        
        Args:
            file_path: Path to the VTT file
            
        Returns:
            Combined text content from all captions
        """
        try:
            caption_texts = []
            subtitle_count = 0
            
            for subtitle in self.streaming_reader.read_streaming(file_path):
                if subtitle.get('text') and subtitle['text'].strip():
                    caption_texts.append(subtitle['text'].strip())
                    subtitle_count += 1
                    
                    # Periodically yield control and manage memory
                    if subtitle_count % 1000 == 0:
                        logger.debug(f"Processed {subtitle_count} subtitles...")
            
            # Combine all caption text
            full_text = " ".join(caption_texts)
            
            logger.info(f"Successfully read VTT file with {subtitle_count} captions (streaming)")
            logger.debug(f"Extracted {len(full_text)} characters of text")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Streaming VTT read failed: {e}")
            raise RuntimeError("Failed to read VTT file using streaming") from e
    
    def read_vtt_iterator(self, file_path: Union[str, Path]) -> Iterator[str]:
        """
        Read VTT file and yield text chunks for memory-efficient processing.
        
        Args:
            file_path: Path to the VTT file
            
        Yields:
            Text content from individual captions
        """
        try:
            validated_path = validate_file_path(
                file_path, 
                allowed_extensions=['.vtt'],
                max_size=self.config.max_file_size
            )
            
            for subtitle in self.streaming_reader.read_streaming(validated_path):
                if subtitle.get('text') and subtitle['text'].strip():
                    yield subtitle['text'].strip()
                    
        except Exception as e:
            logger.error(f"Iterator VTT read failed: {e}")
            raise RuntimeError("Failed to iterate VTT file") from e

    def validate_vtt_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that a file is a properly formatted VTT file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is valid VTT format
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid VTT format
        """
        try:
            validated_path = validate_file_path(file_path, allowed_extensions=['.vtt'])
            
            # Check file header
            with open(validated_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if not first_line.startswith('WEBVTT'):
                    raise ValueError("File does not start with WEBVTT header")
            
            # Try to parse with webvtt library
            vtt = webvtt.read(str(validated_path))
            
            # Basic validation - should have at least one caption
            if len(vtt) == 0:
                logger.warning("VTT file contains no captions")
                return False
            
            logger.debug(f"VTT file validation successful: {len(vtt)} captions found")
            return True
            
        except Exception as e:
            logger.error(f"VTT validation failed: {e}")
            raise ValueError(f"Invalid VTT file: {e}") from e

    def get_vtt_metadata(self, file_path: Union[str, Path]) -> dict:
        """
        Extract metadata from a VTT file.
        
        Args:
            file_path: Path to the VTT file
            
        Returns:
            Dictionary containing VTT metadata
        """
        try:
            validated_path = validate_file_path(file_path, allowed_extensions=['.vtt'])
            vtt = webvtt.read(str(validated_path))
            
            # Calculate metadata
            total_captions = len(vtt)
            total_duration = 0
            
            if total_captions > 0:
                # Get duration from first to last caption
                first_caption = vtt[0]
                last_caption = vtt[-1]
                
                # Convert to seconds (basic parsing)
                start_seconds = self._time_to_seconds(first_caption.start)
                end_seconds = self._time_to_seconds(last_caption.end)
                total_duration = end_seconds - start_seconds
            
            # Count unique speakers (basic heuristic)
            speakers = set()
            for caption in vtt:
                # Look for speaker patterns like "Speaker 1:", "John:", etc.
                import re
                speaker_match = re.match(r'^([A-Za-z\s]+\d*):', caption.text)
                if speaker_match:
                    speakers.add(speaker_match.group(1))
            
            metadata = {
                "total_captions": total_captions,
                "duration_seconds": total_duration,
                "estimated_speakers": len(speakers),
                "speaker_names": sorted(list(speakers)) if speakers else [],
                "file_size_bytes": validated_path.stat().st_size
            }
            
            logger.debug(f"Extracted VTT metadata: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract VTT metadata: {e}")
            return {}

    def _time_to_seconds(self, time_str: str) -> float:
        """
        Convert VTT timestamp to seconds.
        
        Args:
            time_str: Timestamp string (e.g., "00:01:23.456")
            
        Returns:
            Time in seconds as float
        """
        try:
            # Handle format: HH:MM:SS.mmm or MM:SS.mmm
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
            elif len(parts) == 2:
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
            else:
                return float(time_str)
        except (ValueError, IndexError):
            logger.warning(f"Could not parse timestamp: {time_str}")
            return 0.0

    def extract_speakers(self, file_path: Union[str, Path]) -> list:
        """
        Extract speaker information from VTT file.
        
        Args:
            file_path: Path to the VTT file
            
        Returns:
            List of identified speaker names
        """
        try:
            validated_path = validate_file_path(file_path, allowed_extensions=['.vtt'])
            vtt = webvtt.read(str(validated_path))
            
            speakers = set()
            import re
            
            for caption in vtt:
                # Look for various speaker patterns
                patterns = [
                    r'^([A-Za-z][A-Za-z\s]*\d?):\s*',  # "Speaker 1:", "John:"
                    r'>>([A-Za-z][A-Za-z\s]*):',        # ">>John:"
                    r'\[([A-Za-z][A-Za-z\s]*)\]',       # "[John]"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, caption.text)
                    for match in matches:
                        speaker_name = match.strip()
                        if len(speaker_name) > 1 and len(speaker_name) < 50:
                            speakers.add(speaker_name)
            
            speaker_list = sorted(list(speakers))
            logger.debug(f"Identified {len(speaker_list)} speakers: {speaker_list}")
            
            return speaker_list
            
        except Exception as e:
            logger.error(f"Failed to extract speakers: {e}")
            return []


class VTTParsingError(Exception):
    """Custom exception for VTT parsing errors."""
    pass