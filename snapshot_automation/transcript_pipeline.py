import os
import re

import webvtt

# Lazy loading for models - improves import speed and reduces memory usage
from model_loaders import get_nlp_model, get_sentence_tokenizer


def read_vtt(file_path):
    """Step 1: Read the .vtt file"""
    try:
        vtt = webvtt.read(file_path)
        full_text = " ".join([caption.text for caption in vtt])
        return full_text
    except Exception as e:
        print(f"Error reading VTT file: {e}")
        return ""


def clean_text(text):
    """Step 2: Clean up the text"""
    # Remove speaker labels (assuming they're in the format "Speaker:")
    text = re.sub(r"\b\w+:", "", text)

    # Remove any remaining timestamps
    text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", "", text)

    # Remove extra whitespace
    text = " ".join(text.split())

    return text


def improve_formatting(text):
    """Step 3: Improve formatting and structure"""
    # Lazy load sentence tokenizer
    sent_tokenize = get_sentence_tokenizer()

    # Split into sentences
    sentences = sent_tokenize(text)

    # Add markdown formatting
    formatted_text = "# Transcript\n\n"
    for sentence in sentences:
        formatted_text += f"- {sentence}\n"

    return formatted_text


def enhance_content(text):
    """Step 4: Enhance content"""
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


def standardize_quotes(text):
    """Step 4.5: Standardize quotes"""
    # Replace single quotes with double quotes
    text = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
    # Ensure quotes are properly paired
    text = re.sub(r'"([^"]*)"', r'"\1"', text)
    return text


def output_result(text, output_file):
    """Step 5: Output the result"""
    try:
        # Write markdown directly to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Output successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")


def process_vtt(input_file, output_file):
    """Main pipeline to process the .vtt file"""
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
