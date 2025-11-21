"""VTT to Markdown processor with NLP-enhanced entity extraction and topic analysis.

This module provides a comprehensive pipeline for processing WebVTT transcript files
into Markdown format with enhanced NLP features including:
- Named entity recognition and extraction
- Topic identification from noun phrases
- Coreference resolution for pronouns
- Technical term extraction and glossary generation
- Quote standardization and sentence splitting
- Ambiguous pronoun detection

The pipeline consists of multiple stages from raw VTT parsing through to
formatted Markdown output with structured entity and topic sections.
"""

import logging
import os
import re
from collections import Counter
from typing import Any

import webvtt

# Lazy loading for models - improves import speed and reduces memory usage
from model_loaders import (
    get_nlp_model_with_coreferee,
    get_sentence_tokenizer,
    get_summarizer,
)
from spacy.lang.en.stop_words import STOP_WORDS
from utils import safe_file_write, sanitize_filename, validate_file_path


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_vtt(file_path: str) -> str:
    """Read and parse a WebVTT subtitle file with security validation.

    Validates the file path and extension, reads all captions from the VTT file,
    and concatenates them into a single text string.

    Args:
        file_path: Path to the WebVTT (.vtt) file to read.

    Returns:
        Concatenated text from all captions in the VTT file.

    Raises:
        FileNotFoundError: If the specified VTT file does not exist.
        ValueError: If the file is not a valid VTT file or extension is invalid.
        RuntimeError: If an unexpected error occurs during file reading.

    Example:
        >>> text = read_vtt("meeting_transcript.vtt")
        >>> print(len(text))
        15420
    """
    try:
        # Validate file path and type
        validated_path = validate_file_path(file_path, allowed_extensions=[".vtt"])

        vtt = webvtt.read(str(validated_path))
        full_text = " ".join([caption.text for caption in vtt])
        logger.info(f"Successfully read VTT file with {len(vtt)} captions")
        return full_text
    except FileNotFoundError:
        logger.error(f"VTT file not found: {file_path}")
        raise
    except ValueError as e:
        logger.error(f"Invalid VTT file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading VTT file: {type(e).__name__}")
        raise RuntimeError("Failed to read VTT file") from e


def clean_text(text: str) -> str:
    r"""Clean and normalize transcript text.

    Removes speaker labels, timestamps, and extra whitespace from the raw
    transcript text to prepare it for NLP processing.

    Args:
        text: Raw transcript text with speaker labels and timestamps.

    Returns:
        Cleaned text with speaker labels, timestamps, and extra whitespace removed.

    Example:
        >>> raw = "Speaker1: Hello there  \n  Speaker2: How are you?"
        >>> clean_text(raw)
        'Hello there How are you?'
    """
    # Remove speaker labels (assuming they're in the format "Speaker:")
    text = re.sub(r"\b\w+:", "", text)

    # Remove any remaining timestamps
    text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", "", text)

    # Remove extra whitespace
    text = " ".join(text.split())

    return text


def improve_formatting(text: str) -> str:
    r"""Convert text into structured Markdown format with bullet points.

    Splits the text into sentences using NLTK tokenization and formats each
    sentence as a Markdown bullet point under a "Transcript" heading.

    Args:
        text: Cleaned transcript text to format.

    Returns:
        Markdown-formatted text with heading and bulleted sentences.

    Example:
        >>> text = "First sentence. Second sentence."
        >>> improve_formatting(text)
        '# Transcript\\n\\n- First sentence.\\n- Second sentence.\\n'
    """
    # Lazy load sentence tokenizer
    sent_tokenize = get_sentence_tokenizer()

    # Split into sentences
    sentences = sent_tokenize(text)

    # Add markdown formatting
    formatted_text = "# Transcript\n\n"
    for sentence in sentences:
        formatted_text += f"- {sentence.strip()}\n"

    return formatted_text


def enhance_content(text: str, min_freq: int = 2, min_length: int = 3) -> str:
    """Enhance transcript with filtered named entities and topic extraction.

    Uses spaCy NLP with coreference resolution to extract and filter named entities
    and noun phrases (topics) from the text. Filters out common expressions,
    stop words, and low-frequency terms to focus on meaningful content.

    Args:
        text: Formatted transcript text to enhance.
        min_freq: Minimum occurrence frequency for entities/topics to be included.
        min_length: Minimum token length for valid spans.

    Returns:
        Enhanced text with appended sections for Named Entities and Potential Topics.

    Example:
        >>> text = "John Smith from Acme Corp discussed the API integration..."
        >>> enhanced = enhance_content(text)
        >>> "## Named Entities" in enhanced
        True
    """
    # Lazy load NLP model with coreferee
    nlp = get_nlp_model_with_coreferee()
    doc = nlp(text)

    # Custom list of common expressions to exclude
    common_expressions = {
        "Yeah",
        "you know",
        "Excellent",
        "Great",
        "Understood",
        "Okay",
        "I mean",
        "kind of",
        "sort of",
        "a lot",
        "in fact",
        "Okay, ",
        "Alright, ",
    }

    # Parts of speech to exclude
    exclude_pos = ["DET", "PRON", "ADP", "CONJ", "CCONJ", "PART", "INTJ"]

    # Extend stop words
    stop_words = STOP_WORDS.union(
        {"said", "would", "could", "should", "will", "can", "may", "might"}
    )

    # Function to check if a span is valid
    def is_valid_span(span: Any) -> bool:
        """Check if a spaCy span meets validity criteria for extraction."""
        return (
            len(span) >= min_length
            and not any(
                token.is_stop or token.lemma_.lower() in stop_words for token in span
            )
            and not any(token.pos_ in exclude_pos for token in span)
            and span.lemma_.lower() not in common_expressions
        )

    # Extract and filter named entities
    # entities = list(set([ent.text for ent in doc.ents if is_valid_span(ent)]))
    entities = [ent.text for ent in doc.ents if is_valid_span(ent)]

    # Extract and filter noun phrases (potential topics)
    # noun_phrases = list(set([chunk.text for chunk in doc.noun_chunks if is_valid_span(chunk)]))
    noun_phrases = [chunk.text for chunk in doc.noun_chunks if is_valid_span(chunk)]

    # Count occurrences and filter by frequency
    entity_counts = Counter(entities)
    topic_counts = Counter(noun_phrases)

    filtered_entities = [e for e, count in entity_counts.items() if count >= min_freq]
    filtered_topics = [t for t, count in topic_counts.items() if count >= min_freq]

    # Construct enhanced text
    enhanced_text = text + "\n\n## Named Entities\n\n"
    enhanced_text += (
        ", ".join(set(filtered_entities))
        if filtered_entities
        else "No named entities found."
    )

    enhanced_text += "\n\n## Potential Topics\n\n"
    enhanced_text += (
        ", ".join(set(filtered_topics))
        if filtered_topics
        else "No potential topics found."
    )

    return enhanced_text


def output_result(text: str, output_file: str) -> None:
    """Write the processed transcript to output file securely.

    Sanitizes the filename and uses secure file writing to prevent path
    traversal attacks and other security issues.

    Args:
        text: Processed transcript text to write.
        output_file: Path to the output file (filename will be sanitized).

    Raises:
        PermissionError: If no write permission for output file.
        OSError: If disk full or other OS error occurs.

    Example:
        >>> output_result("Processed transcript...", "output.md")
        # Creates output.md with sanitized filename
    """
    try:
        # Get the directory and sanitize the filename
        output_dir = (
            os.path.dirname(output_file)
            if os.path.dirname(output_file)
            else os.path.dirname(os.path.abspath(__file__))
        )
        sanitized_filename = sanitize_filename(os.path.basename(output_file))
        safe_output_path = os.path.join(output_dir, sanitized_filename)

        safe_file_write(safe_output_path, text)
        logger.info(f"Output successfully written to {safe_output_path}")
    except Exception as e:
        logger.error(f"Failed to write output file: {type(e).__name__}")
        raise


# Functions to address formatting inconsistencies
def standardize_quotes(text: str) -> str:
    r"""Standardize quotation marks using regular expressions.

    Replaces single quotes with double quotes and ensures quotes are properly
    paired throughout the text.

    Args:
        text: Text with potentially inconsistent quotation marks.

    Returns:
        Text with standardized double quotes.

    Example:
        >>> text = "He said 'hello' and she replied 'hi'"
        >>> standardize_quotes(text)
        'He said "hello" and she replied "hi"'
    """
    # Replace single quotes with double quotes
    text = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
    # Ensure quotes are properly paired
    text = re.sub(r'"([^"]*)"', r'"\1"', text)
    return text


def split_long_sentences(text: str, max_length: int = 50) -> str:
    """Split run-on sentences into shorter chunks using NLTK.

    Tokenizes text into sentences and splits any sentence longer than
    max_length words into multiple shorter sentences.

    Args:
        text: Text potentially containing long run-on sentences.
        max_length: Maximum number of words per sentence chunk.

    Returns:
        Text with long sentences split into shorter chunks.

    Example:
        >>> long_text = " ".join(["word"] * 100)
        >>> result = split_long_sentences(long_text, max_length=30)
        >>> len(result.split(".")) > 1
        True
    """
    # Lazy load sentence tokenizer
    sent_tokenize = get_sentence_tokenizer()
    sentences = sent_tokenize(text)
    new_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > max_length:
            # Split the sentence into chunks
            chunks = [
                words[i : i + max_length] for i in range(0, len(words), max_length)
            ]
            new_sentences.extend([" ".join(chunk) + "." for chunk in chunks])
        else:
            new_sentences.append(sentence)
    return " ".join(new_sentences)


# Functions to address ambiguous pronouns
def resolve_coreferences(text: str) -> str:
    """Resolve pronoun coreferences using spaCy coreferee.

    Uses coreference resolution to replace pronouns with their antecedents,
    making the text more explicit and easier to understand.

    Args:
        text: Text with pronouns to resolve.

    Returns:
        Text with pronouns replaced by their antecedents, or original text
        if no coreferences detected.

    Example:
        >>> text = "John went to the store. He bought milk."
        >>> resolve_coreferences(text)
        'John went to the store. John bought milk.'
    """
    # Lazy load NLP model with coreferee
    nlp = get_nlp_model_with_coreferee()
    doc = nlp(text)  # Process the text with spaCy
    if doc._.has_coref:
        resolved_text = doc._.coref_chains.resolve(text)
        return resolved_text  # type: ignore[no-any-return]
    return text


def flag_ambiguous_pronouns(text: str) -> list[tuple[str, int]]:
    """Identify potentially ambiguous pronouns for manual review.

    Finds pronouns that are not subjects or direct objects, which may be
    ambiguous or difficult to resolve automatically.

    Args:
        text: Text to analyze for ambiguous pronouns.

    Returns:
        List of tuples containing (pronoun_text, token_index) for each
        potentially ambiguous pronoun found.

    Example:
        >>> text = "She told her that it was important."
        >>> ambiguous = flag_ambiguous_pronouns(text)
        >>> len(ambiguous) > 0
        True
    """
    # Lazy load NLP model
    nlp = get_nlp_model_with_coreferee()
    doc = nlp(text)
    ambiguous_pronouns = []
    for token in doc:
        if token.pos_ == "PRON" and token.dep_ not in ["nsubj", "dobj"]:
            ambiguous_pronouns.append((token.text, token.i))
    return ambiguous_pronouns


# Functions to address technical jargon
def extract_technical_terms(
    text: str, min_count: int = 20, min_length: int = 3
) -> list[str]:
    """Extract frequently occurring technical terms from text.

    Uses spaCy NLP to identify nouns, proper nouns, adjectives, and verbs
    that appear frequently and are not common words, likely representing
    domain-specific terminology.

    Args:
        text: Text to extract technical terms from.
        min_count: Minimum occurrences for a term to be considered technical.
        min_length: Minimum character length for valid terms.

    Returns:
        List of technical terms meeting the frequency and length criteria.

    Example:
        >>> text = "API integration API authentication API endpoints" * 10
        >>> terms = extract_technical_terms(text, min_count=5)
        >>> "api" in terms
        True
    """
    # Lazy load NLP model
    nlp = get_nlp_model_with_coreferee()
    doc = nlp(text)

    # Define parts of speech to exclude
    exclude_pos = ["DET", "PRON", "ADP", "CONJ", "CCONJ", "PART", "INTJ"]

    # Create a set of common words to exclude (you can add more)
    common_words = set(STOP_WORDS)
    common_words.update(
        ["said", "would", "could", "should", "will", "can", "may", "might"]
    )

    # Filter terms
    terms = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ not in exclude_pos
        and token.pos_
        in ["NOUN", "PROPN", "ADJ", "VERB"]  # Include adjectives and verbs
        and token.is_alpha
        and len(token.text) >= min_length
        and token.lemma_.lower() not in common_words
    ]

    # Count occurrences and filter by frequency
    term_counts = Counter(terms)
    technical_terms = [
        term for term, count in term_counts.items() if count >= min_count
    ]

    return technical_terms


def generate_explanation(term: str, context: str) -> str:
    """Generate AI explanation for a technical term using transformer model.

    Uses a summarization model to generate a brief explanation of a term
    based on its context in the transcript.

    Args:
        term: Technical term to explain.
        context: Context in which the term appears.

    Returns:
        AI-generated explanation of the term (15-20 tokens).

    Example:
        >>> explanation = generate_explanation("API", "web service integration")
        >>> len(explanation) > 0
        True
    """
    # Lazy load summarizer model
    summarizer = get_summarizer()
    prompt = f"Explain the term '{term}' in the context of: {context}"
    explanation = summarizer(prompt, max_length=20, min_length=15, do_sample=False)[0][
        "summary_text"
    ]
    return explanation  # type: ignore[no-any-return]


def add_explanations(text: str, glossary: dict[str, str]) -> str:
    """Add inline explanations for technical terms in text.

    Replaces technical terms with the format "term (explanation)" throughout
    the text based on a provided glossary dictionary.

    Args:
        text: Text to add explanations to.
        glossary: Dictionary mapping terms to their explanations.

    Returns:
        Text with inline explanations added for glossary terms.

    Example:
        >>> text = "The API provides data access."
        >>> glossary = {"API": "Application Programming Interface"}
        >>> add_explanations(text, glossary)
        'The API (Application Programming Interface) provides data access.'
    """
    for term, explanation in glossary.items():
        if explanation:  # Only add explanations that have been filled
            text = text.replace(term, f"{term} ({explanation})")
    return text


def process_vtt(input_file: str, output_file: str) -> None:
    """Main pipeline to process VTT transcript files into enhanced Markdown.

    Orchestrates the complete processing pipeline from VTT parsing through
    cleaning, formatting, NLP enhancement, and Markdown output generation.

    Pipeline stages:
    1. Read and parse VTT file
    2. Clean text (remove labels, timestamps, whitespace)
    3. Format as Markdown with bullet points
    4. Enhance with entities and topics via NLP
    5. Standardize quotes
    6. Split long sentences
    7. Extract technical terms
    8. Write formatted output

    Args:
        input_file: Path to input VTT file to process.
        output_file: Path to output Markdown file to create.

    Raises:
        FileNotFoundError: If input VTT file doesn't exist.
        ValueError: If input file format is invalid.
        RuntimeError: If processing fails for any other reason.

    Example:
        >>> process_vtt("meeting.vtt", "meeting_processed.md")
        # Creates meeting_processed.md with enhanced Markdown transcript
    """
    try:
        # Step 1: Read the .vtt file
        text = read_vtt(input_file)
        if not text:
            logger.warning("No text extracted from VTT file")
            return

        # Step 2: Clean up the text
        text = clean_text(text)

        # Step 3: Improve formatting and structure
        text = improve_formatting(text)

        # Step 4: Enhance content
        text = enhance_content(text)

        # Step 4.5: Standardize quotes
        text = standardize_quotes(text)

        # Step 4.6: Split long sentences
        text = split_long_sentences(text)

        # Step 4.9: Extract technical terms
        technical_terms = extract_technical_terms(text)
        logger.info(f"Extracted {len(technical_terms)} technical terms")

        # Step 5: Output the result
        output_result(text, output_file)

        logger.info("Processing completed successfully")

    except FileNotFoundError:
        logger.error("Input file not found")
        raise
    except ValueError:
        logger.error("Invalid input file or parameters")
        raise
    except Exception as e:
        logger.error(f"Processing failed: {type(e).__name__}")
        raise RuntimeError("VTT processing failed") from e


# Main entry point
if __name__ == "__main__":
    import sys

    # Parse command-line arguments
    if len(sys.argv) == 1:
        # No arguments provided, use defaults
        input_filename = "input.vtt"
        output_filename = "output.md"
    elif len(sys.argv) == 2:
        # Only input file provided
        input_filename = sys.argv[1]
        output_filename = "output.md"
    elif len(sys.argv) == 3:
        # Both input and output files provided
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    else:
        print("Usage: python vtt_to_markdown_processor.py [input_file] [output_file]")
        print("Defaults: input_file='input.vtt', output_file='output.md'")
        sys.exit(1)

    # Use relative paths from the current script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "vtt_files", input_filename)
    output_file = os.path.join(script_dir, "vtt_files", output_filename)

    process_vtt(input_file, output_file)
