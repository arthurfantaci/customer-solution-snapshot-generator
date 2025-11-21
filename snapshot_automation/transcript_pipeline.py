"""Multi-stage VTT transcript processing pipeline with NLP enhancements.

This module implements a complete processing pipeline for WebVTT transcript files,
transforming raw captions into formatted, enhanced markdown documents. The pipeline
consists of five main stages:

1. Read VTT: Load and extract text from WebVTT files
2. Clean Text: Remove speaker labels, timestamps, and extra whitespace
3. Improve Formatting: Split into sentences and add markdown structure
4. Enhance Content: Extract named entities and topics using spaCy NLP
5. Output Result: Write formatted markdown to file

The module uses lazy loading for expensive NLP models (spaCy, NLTK) to minimize
import time and memory usage when models aren't needed.
"""

import os
import re

import webvtt

# Lazy loading for models - improves import speed and reduces memory usage
from model_loaders import get_nlp_model, get_sentence_tokenizer


def read_vtt(file_path: str) -> str:
    """Read and extract text from a WebVTT subtitle file.

    Loads a .vtt file using the webvtt library and concatenates all caption
    text into a single string with spaces between captions.

    Args:
        file_path: Path to the .vtt file to read.

    Returns:
        Concatenated text from all captions, or empty string if error occurs.

    Example:
        >>> text = read_vtt("transcript.vtt")
        >>> print(text[:50])
        'Welcome to the meeting. Today we will discuss...'
    """
    try:
        vtt = webvtt.read(file_path)
        full_text = " ".join([caption.text for caption in vtt])
        return full_text
    except Exception as e:
        print(f"Error reading VTT file: {e}")
        return ""


def clean_text(text: str) -> str:
    r"""Clean and normalize transcript text by removing labels and timestamps.

    Performs three cleaning operations:
    1. Removes speaker labels in "Speaker:" format
    2. Removes VTT timestamp patterns (HH:MM:SS.mmm --> HH:MM:SS.mmm)
    3. Normalizes whitespace by collapsing multiple spaces

    Args:
        text: Raw transcript text to clean.

    Returns:
        Cleaned text with labels, timestamps, and extra whitespace removed.

    Example:
        >>> raw = "John: Hello there  00:00:01.000 --> 00:00:03.000  everyone"
        >>> clean_text(raw)
        'Hello there everyone'
    """
    # Remove speaker labels (assuming they're in the format "Speaker:")
    text = re.sub(r"\b\w+:", "", text)

    # Remove any remaining timestamps
    text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", "", text)

    # Remove extra whitespace
    text = " ".join(text.split())

    return text


def improve_formatting(text: str) -> str:
    """Format transcript text as markdown with sentence-level bullets.

    Tokenizes text into sentences using NLTK's sentence tokenizer (lazy loaded)
    and formats each sentence as a markdown bullet point under a "Transcript" heading.

    Args:
        text: Cleaned transcript text to format.

    Returns:
        Markdown-formatted text with heading and bulleted sentences.

    Example:
        >>> text = "This is sentence one. This is sentence two."
        >>> print(improve_formatting(text))
        # Transcript

        - This is sentence one.
        - This is sentence two.
    """
    # Lazy load sentence tokenizer
    sent_tokenize = get_sentence_tokenizer()

    # Split into sentences
    sentences = sent_tokenize(text)

    # Add markdown formatting
    formatted_text = "# Transcript\n\n"
    for sentence in sentences:
        formatted_text += f"- {sentence}\n"

    return formatted_text


def enhance_content(text: str) -> str:
    """Enhance transcript with NLP-extracted entities and topics.

    Uses spaCy NLP (lazy loaded) to perform:
    - Named entity recognition (people, organizations, locations, etc.)
    - Noun phrase extraction for identifying potential discussion topics

    Appends two markdown sections to the input text:
    - "Named Entities": Unique entities found in the transcript
    - "Potential Topics": Unique noun phrases that may represent key topics

    Args:
        text: Formatted transcript text to enhance.

    Returns:
        Original text with appended Named Entities and Potential Topics sections.

    Example:
        >>> text = "John works at Acme Corp in New York."
        >>> enhanced = enhance_content(text)
        >>> "Named Entities" in enhanced and "Acme Corp" in enhanced
        True
    """
    # Lazy load NLP model only when needed
    nlp = get_nlp_model()
    doc = nlp(text)

    # Extract named entities
    entities = [ent.text for ent in doc.ents]

    # Extract noun phrases (potential topics)
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]

    enhanced_text = text + "\n\n## Named Entities\n\n"
    enhanced_text += (
        ", ".join(set(entities)) if entities else "No named entities found."
    )

    enhanced_text += "\n\n## Potential Topics\n\n"
    enhanced_text += (
        ", ".join(set(noun_phrases)) if noun_phrases else "No potential topics found."
    )

    return enhanced_text


def standardize_quotes(text: str) -> str:
    r"""Normalize quote characters to double quotes.

    Performs two transformations:
    1. Replaces standalone single quotes with double quotes
    2. Ensures quoted content uses consistent double quotes

    Args:
        text: Text with potentially inconsistent quote characters.

    Returns:
        Text with standardized double quotes.

    Example:
        >>> text = "He said 'hello' and left."
        >>> standardize_quotes(text)
        'He said "hello" and left.'

    Note:
        This function is currently not used in the main pipeline (process_vtt).
    """
    # Replace single quotes with double quotes
    text = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
    # Ensure quotes are properly paired
    text = re.sub(r'"([^"]*)"', r'"\1"', text)
    return text


def output_result(text: str, output_file: str) -> None:
    r"""Write processed transcript text to a file.

    Writes the enhanced markdown text to the specified output file using UTF-8
    encoding. Prints success or error messages to console.

    Args:
        text: Processed transcript content to write.
        output_file: Path to output file (typically .html or .md extension).

    Example:
        >>> output_result("# Transcript\n\nContent here...", "output.html")
        Output successfully written to output.html
    """
    try:
        # Write markdown directly to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Output successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")


def process_vtt(input_file: str, output_file: str) -> None:
    """Execute complete VTT processing pipeline from input to output.

    Orchestrates the five-stage pipeline:
    1. Read VTT file and extract text
    2. Clean text (remove labels, timestamps, whitespace)
    3. Improve formatting (sentence tokenization, markdown bullets)
    4. Enhance content (NLP entity and topic extraction)
    5. Write output to file

    Processing stops early if VTT file cannot be read.

    Args:
        input_file: Path to input .vtt file.
        output_file: Path to output file (typically .html or .md).

    Example:
        >>> process_vtt("transcript.vtt", "formatted_output.html")
        Output successfully written to formatted_output.html
        Processing complete. Output saved to formatted_output.html
    """
    # Step 1: Read the .vtt file
    text = read_vtt(input_file)
    if not text:
        return

    # Step 2: Clean up the text
    text = clean_text(text)

    # Step 3: Improve formatting and structure
    text = improve_formatting(text)

    # Step 4: Enhance content
    text = enhance_content(text)

    # Step 5: Output the result
    output_result(text, output_file)

    print(f"Processing complete. Output saved to {output_file}")


# Usage
if __name__ == "__main__":
    # Use relative paths from the current script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(
        script_dir, "vtt_files", "project_kickoff_transcript_v2.vtt"
    )
    output_file = os.path.join(script_dir, "vtt_files", "formatted_transcript.html")
    process_vtt(input_file, output_file)
