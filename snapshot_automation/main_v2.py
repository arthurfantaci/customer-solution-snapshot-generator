import webvtt
import nltk
from nltk.tokenize import sent_tokenize
import spacy
import coreferee
import re
import os

from collections import Counter
from transformers import pipeline
from spacy.lang.en.stop_words import STOP_WORDS

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Add coreferee to the spaCy pipeline
nlp.add_pipe('coreferee')


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
    text = re.sub(r'\b\w+:', '', text)
    
    # Remove any remaining timestamps
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def improve_formatting(text):
    """Step 3: Improve formatting and structure"""
    # Split into sentences
    sentences = sent_tokenize(text)
    
    # Add markdown formatting
    formatted_text = "# Transcript\n\n"
    for sentence in sentences:
        formatted_text += f"- {sentence.strip()}\n"
    
    return formatted_text

def enhance_content(text, min_freq=2, min_length=3):
    """Step 4: Enhance content with filtered entities and topics"""
    doc = nlp(text)
    
    # Custom list of common expressions to exclude
    common_expressions = set(["Yeah", "you know", "Excellent", "Great", "Understood", "Okay", "I mean", "kind of", "sort of", "a lot", "in fact", "Understood", "Great", "Okay, ", "Alright, "])
    
    # Parts of speech to exclude
    exclude_pos = ['DET', 'PRON', 'ADP', 'CONJ', 'CCONJ', 'PART', 'INTJ']
    
    # Extend stop words
    stop_words = STOP_WORDS.union({"said", "would", "could", "should", "will", "can", "may", "might"})
    
    # Function to check if a span is valid
    def is_valid_span(span):
        return (len(span) >= min_length and
                not any(token.is_stop or token.lemma_.lower() in stop_words for token in span) and
                not any(token.pos_ in exclude_pos for token in span) and
                span.lemma_.lower() not in common_expressions)
    
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
    enhanced_text += ", ".join(set(filtered_entities)) if filtered_entities else "No named entities found."
    
    enhanced_text += "\n\n## Potential Topics\n\n"
    enhanced_text += ", ".join(set(filtered_topics)) if filtered_topics else "No potential topics found."
    
    return enhanced_text

def output_result(text, output_file):
    """Step 5: Output the result"""
    try:
        # Write markdown directly to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Output successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

# Functions to address formatting inconsistencies
def standardize_quotes(text):
    """Step 4.5: Use Regular Expressions to standardize quotation marks"""
    # Replace single quotes with double quotes
    text = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
    # Ensure quotes are properly paired
    text = re.sub(r'"([^"]*)"', r'"\1"', text)
    return text

def split_long_sentences(text, max_length=50):
    """Step 4.6: Use NLTK to split run-on sentences into shorter sentences"""
    sentences = nltk.sent_tokenize(text)
    new_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > max_length:
            # Split the sentence into chunks
            chunks = [words[i:i + max_length] for i in range(0, len(words), max_length)]
            new_sentences.extend([' '.join(chunk) + '.' for chunk in chunks])
        else:
            new_sentences.append(sentence)
    return ' '.join(new_sentences)

# Functions to address ambiguous pronouns
def resolve_coreferences(text):
    """Step 4.7: Use coreference resolution to replace pronouns with their antecedents"""
    doc = nlp(text)  # Process the text with spaCy
    if doc._.has_coref:
        resolved_text = doc._.coref_chains.resolve(text)
        return resolved_text
    return text

def flag_ambiguous_pronouns(text):
    """Step 4.8: Identify potentially ambiguous pronouns for manual review"""
    doc = nlp(text)
    ambiguous_pronouns = []
    for token in doc:
        if token.pos_ == 'PRON' and token.dep_ not in ['nsubj', 'dobj']:
            ambiguous_pronouns.append((token.text, token.i))
    return ambiguous_pronouns

# Functions to address technical jargon
def extract_technical_terms(text, min_count=20, min_length=3):
    doc = nlp(text)
    
    # Define parts of speech to exclude
    exclude_pos = ['DET', 'PRON', 'ADP', 'CONJ', 'CCONJ', 'PART', 'INTJ']
    
    # Create a set of common words to exclude (you can add more)
    common_words = set(STOP_WORDS)
    common_words.update(['said', 'would', 'could', 'should', 'will', 'can', 'may', 'might'])
    
    # Filter terms
    terms = [
        token.lemma_.lower() for token in doc 
        if token.pos_ not in exclude_pos
        and token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']  # Include adjectives and verbs
        and token.is_alpha
        and len(token.text) >= min_length
        and token.lemma_.lower() not in common_words
    ]
    
    # Count occurrences and filter by frequency
    term_counts = Counter(terms)
    technical_terms = [term for term, count in term_counts.items() if count >= min_count]
    
    return technical_terms

def generate_explanation(term, context):
    prompt = f"Explain the term '{term}' in the context of: {context}"
    explanation = summarizer(prompt, max_length=20, min_length=15, do_sample=False)[0]['summary_text']
    return explanation

def add_explanations(text, glossary):
    for term, explanation in glossary.items():
        if explanation:  # Only add explanations that have been filled
            text = text.replace(term, f"{term} ({explanation})")
    return text


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
    
    # Step 4.7: Resolve coreferences
    # text = resolve_coreferences(text)
    
    # Step 4: Enhance content
    text = enhance_content(text)

    # Step 4.5: Standardize quotes
    text = standardize_quotes(text)

    # Step 4.6: Split long sentences
    text = split_long_sentences(text)

    # Step 4.8: Flag ambiguous pronouns
    # ambiguous_pronouns = flag_ambiguous_pronouns(text)
    # print("Potentially ambiguous pronouns:", ambiguous_pronouns)
    
    # Step 4.9: Extract technical terms
    technical_terms = extract_technical_terms(text)
    print("Technical Terms:", technical_terms)

    # Step 5: Output the result
    output_result(text, output_file)

    print(f"Processing complete. Output saved to {output_file}")

# Main entry point
if __name__ == "__main__":
    input_file = "C:/Users/DQA/kickoff_transcript/snapshot_automation/vtt_files/project_kickoff_transcript_v2.vtt"
    output_file = "C:/Users/DQA/kickoff_transcript/snapshot_automation/vtt_files/formatted_transcript_v2.md"
    process_vtt(input_file, output_file)