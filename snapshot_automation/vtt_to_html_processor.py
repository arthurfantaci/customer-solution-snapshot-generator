"""VTT to HTML processor for transcript analysis and enhancement.

This module provides a complete pipeline for processing WebVTT transcript files,
including NLP-based entity extraction, topic identification, text formatting,
and HTML output generation. It uses spaCy for natural language processing,
NLTK for sentence tokenization, and transformers for summarization.

The main processing pipeline includes:
- Reading and validating VTT files
- Cleaning and normalizing transcript text
- Extracting named entities and topics
- Formatting text with Markdown
- Converting to HTML output

Example:
    Basic usage:
        >>> from vtt_to_html_processor import process_vtt
        >>> process_vtt("meeting.vtt", "meeting.html")
"""

import logging
import os
import re
from collections import Counter

import markdown
import webvtt

# Lazy loading for models - improves import speed and reduces memory usage
from model_loaders import (
    get_nlp_model_with_coreferee,
    get_sentence_tokenizer,
    get_summarizer,
)
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.tokens import Span
from utils import safe_file_write, sanitize_filename, validate_file_path


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_vtt(file_path: str) -> str:
    """Read and parse a WebVTT subtitle file with security validation.

    Validates the file path, reads the VTT file, and extracts all caption text
    into a single concatenated string. This function performs security checks
    to ensure only valid VTT files are processed.

    Args:
        file_path: Path to the WebVTT (.vtt) file to read.

    Returns:
        Concatenated text from all captions in the VTT file, with captions
        separated by spaces.

    Raises:
        FileNotFoundError: If the specified VTT file does not exist.
        ValueError: If the file is not a valid VTT file or has an invalid extension.
        RuntimeError: If an unexpected error occurs during file reading.

    Example:
        >>> text = read_vtt("meeting_transcript.vtt")
        >>> len(text) > 0
        True
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
    r"""Clean and normalize transcript text by removing metadata and formatting.

    Removes speaker labels, timestamps, and extra whitespace from VTT transcript
    text to produce clean, continuous prose suitable for NLP processing.

    Args:
        text: Raw transcript text containing speaker labels, timestamps, and
            irregular whitespace.

    Returns:
        Cleaned text with speaker labels and timestamps removed, and whitespace
        normalized to single spaces.

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
    """Convert plain text into structured Markdown format with sentence segmentation.

    Tokenizes the text into individual sentences using NLTK and formats each
    sentence as a Markdown bullet point under a "Transcript" heading.

    Args:
        text: Cleaned transcript text to format.

    Returns:
        Markdown-formatted text with a heading and bullet-pointed sentences.

    Example:
        >>> text = "This is sentence one. This is sentence two."
        >>> result = improve_formatting(text)
        >>> "# Transcript" in result
        True
        >>> result.count("- ") == 2
        True
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
    """Enhance content with filtered named entities and topic extraction using NLP.

    Uses spaCy with coreference resolution to extract and filter named entities
    and noun phrases from the text. Filters out common expressions, stop words,
    and low-frequency terms to identify meaningful entities and topics.

    Args:
        text: The input text to analyze and enhance.
        min_freq: Minimum frequency threshold for entities/topics to include.
            Entities appearing fewer times are filtered out.
        min_length: Minimum character length for valid entities/topics.

    Returns:
        Enhanced text with "Named Entities" and "Potential Topics" sections
        appended, listing filtered and deduplicated entities and topics.

    Example:
        >>> text = "Apple Inc. is located in California. Apple makes iPhones."
        >>> enhanced = enhance_content(text, min_freq=2)
        >>> "Named Entities" in enhanced
        True
        >>> "Apple" in enhanced
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

    def is_valid_span(span: Span) -> bool:
        """Check if a spaCy span is valid for entity/topic extraction.

        Validates that the span meets minimum length requirements, doesn't
        consist of stop words or excluded parts of speech, and isn't a
        common expression.

        Args:
            span: spaCy Span object to validate.

        Returns:
            True if the span is valid for extraction, False otherwise.
        """
        return (
            len(span) >= min_length
            and not any(
                token.is_stop or token.lemma_.lower() in stop_words for token in span
            )
            and not any(token.pos_ in exclude_pos for token in span)
            and span.lemma_.lower() not in common_expressions
        )

    # Extract and filter named entities
    entities = [ent.text for ent in doc.ents if is_valid_span(ent)]

    # Extract and filter noun phrases (potential topics)
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
    r"""Convert Markdown text to HTML and securely write to output file.

    Converts the Markdown-formatted text to HTML and writes it to a file with
    security measures including filename sanitization and safe file writing.

    Args:
        text: Markdown-formatted text to convert and write.
        output_file: Path where the HTML output should be written. The filename
            will be sanitized for security.

    Raises:
        Exception: If the file write operation fails for any reason.

    Example:
        >>> output_result("# Heading\n\nContent", "output.html")
        >>> # Creates output.html with HTML content
    """
    try:
        # Convert markdown to HTML
        html = markdown.markdown(text)

        # Get the directory and sanitize the filename
        output_dir = (
            os.path.dirname(output_file)
            if os.path.dirname(output_file)
            else os.path.dirname(os.path.abspath(__file__))
        )
        sanitized_filename = sanitize_filename(os.path.basename(output_file))
        safe_output_path = os.path.join(output_dir, sanitized_filename)

        safe_file_write(safe_output_path, html)
        logger.info(f"Output successfully written to {safe_output_path}")
    except Exception as e:
        logger.error(f"Failed to write output file: {type(e).__name__}")
        raise


# Functions to address formatting inconsistencies
def standardize_quotes(text: str) -> str:
    """Standardize quotation marks using regular expressions.

    Converts single quotes to double quotes and ensures proper pairing of
    quotation marks throughout the text for consistent formatting.

    Args:
        text: Text containing potentially inconsistent quotation marks.

    Returns:
        Text with standardized double quotation marks.

    Example:
        >>> standardize_quotes("He said 'hello' to me")
        'He said "hello" to me'
    """
    # Replace single quotes with double quotes
    text = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
    # Ensure quotes are properly paired
    text = re.sub(r'"([^"]*)"', r'"\1"', text)
    return text


def split_long_sentences(text: str, max_length: int = 50) -> str:
    """Split run-on sentences into shorter chunks using NLTK tokenization.

    Tokenizes text into sentences and splits any sentence exceeding the maximum
    word length into smaller chunks. Useful for improving readability of
    transcripts with very long sentences.

    Args:
        text: Text to process for sentence splitting.
        max_length: Maximum number of words allowed per sentence. Sentences
            exceeding this will be split into chunks.

    Returns:
        Text with long sentences split into shorter chunks, with periods added
        to maintain sentence structure.

    Example:
        >>> text = "This is a very long sentence " + " word" * 60
        >>> result = split_long_sentences(text, max_length=50)
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
    """Resolve coreferences by replacing pronouns with their antecedents.

    Uses the coreferee library with spaCy to identify coreference chains and
    replace pronouns with the entities they refer to, improving text clarity.

    Args:
        text: Text containing pronouns and potential coreferences.

    Returns:
        Text with pronouns replaced by their antecedents where coreferences
        are detected. If no coreferences are found, returns the original text.

    Example:
        >>> text = "John went to the store. He bought milk."
        >>> resolved = resolve_coreferences(text)
        >>> # Result might be: "John went to the store. John bought milk."
    """
    # Lazy load NLP model with coreferee
    nlp = get_nlp_model_with_coreferee()
    doc = nlp(text)  # Process the text with spaCy
    if doc._.has_coref:
        resolved_text = doc._.coref_chains.resolve(text)
        return resolved_text
    return text


def flag_ambiguous_pronouns(text: str) -> list[tuple[str, int]]:
    """Identify potentially ambiguous pronouns for manual review.

    Analyzes text to find pronouns that are not clear subjects or objects,
    which may indicate ambiguous references requiring manual review.

    Args:
        text: Text to analyze for ambiguous pronoun usage.

    Returns:
        List of tuples containing (pronoun_text, token_index) for each
        potentially ambiguous pronoun found. Empty list if none found.

    Example:
        >>> text = "She told her that it was done."
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
    that appear frequently in the text, filtering out common words and
    short terms to focus on domain-specific terminology.

    Args:
        text: Text to analyze for technical terms.
        min_count: Minimum frequency threshold for a term to be considered
            technical. Terms appearing fewer times are filtered out.
        min_length: Minimum character length for valid terms.

    Returns:
        List of technical terms (lemmatized and lowercase) that meet the
        frequency and length criteria. Empty list if none found.

    Example:
        >>> text = "API integration " * 25 + "database schema " * 25
        >>> terms = extract_technical_terms(text, min_count=20)
        >>> "integration" in terms or "schema" in terms
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
    """Generate a brief explanation for a technical term using AI summarization.

    Uses a transformer-based summarization model to generate a concise
    explanation of a term within its given context.

    Args:
        term: The technical term to explain.
        context: Contextual text surrounding the term to help generate
            a relevant explanation.

    Returns:
        Generated explanation text (15-20 tokens) for the term.

    Example:
        >>> explanation = generate_explanation("API", "REST API endpoints")
        >>> len(explanation) > 0
        True
    """
    # Lazy load summarizer model
    summarizer = get_summarizer()
    prompt = f"Explain the term '{term}' in the context of: {context}"
    explanation = summarizer(prompt, max_length=20, min_length=15, do_sample=False)[0][
        "summary_text"
    ]
    return explanation


def add_explanations(text: str, glossary: dict[str, str]) -> str:
    """Add inline explanations for technical terms in text.

    Replaces each technical term with the term followed by its explanation
    in parentheses, creating an annotated version of the text.

    Args:
        text: Original text containing technical terms.
        glossary: Dictionary mapping terms to their explanations. Only terms
            with non-empty explanations will be annotated.

    Returns:
        Text with technical terms annotated with their explanations in
        parentheses (e.g., "API (Application Programming Interface)").

    Example:
        >>> text = "The API is fast."
        >>> glossary = {"API": "Application Programming Interface"}
        >>> add_explanations(text, glossary)
        'The API (Application Programming Interface) is fast.'
    """
    for term, explanation in glossary.items():
        if explanation:  # Only add explanations that have been filled
            text = text.replace(term, f"{term} ({explanation})")
    return text


def process_vtt(input_file: str, output_file: str) -> None:
    """Execute the complete VTT-to-HTML processing pipeline.

    Orchestrates the full transcript processing workflow: reading VTT files,
    cleaning text, formatting with Markdown, extracting entities and topics,
    standardizing quotes, splitting long sentences, extracting technical terms,
    and generating HTML output.

    Args:
        input_file: Path to the input VTT file to process.
        output_file: Path where the processed HTML output should be written.

    Raises:
        FileNotFoundError: If the input VTT file does not exist.
        ValueError: If the input file is invalid or parameters are incorrect.
        RuntimeError: If any step in the processing pipeline fails.

    Example:
        >>> process_vtt("meeting.vtt", "meeting_processed.html")
        >>> # Creates meeting_processed.html with formatted transcript
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
        output_filename = "output.html"
    elif len(sys.argv) == 2:
        # Only input file provided
        input_filename = sys.argv[1]
        output_filename = "output.html"
    elif len(sys.argv) == 3:
        # Both input and output files provided
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    else:
        print("Usage: python vtt_to_html_processor.py [input_file] [output_file]")
        print("Defaults: input_file='input.vtt', output_file='output.html'")
        sys.exit(1)

    # Use relative paths from the current script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "vtt_files", input_filename)
    output_file = os.path.join(script_dir, "vtt_files", output_filename)

    process_vtt(input_file, output_file)
