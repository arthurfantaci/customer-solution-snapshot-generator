"""
Customer Solution Snapshot Generator

An automated Python tool that transforms video meeting transcripts (VTT files) 
into structured Customer Success Snapshot documents using NLP and AI technologies.
"""

__version__ = "0.1.0"
__author__ = "Customer Snapshot Team"

# Import main functionality
from .core.processor import TranscriptProcessor
from .utils.config import Config

__all__ = ["TranscriptProcessor", "Config"]