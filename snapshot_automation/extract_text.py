import os
import re
from collections import Counter

# Lazy loading for models - improves import speed and reduces memory usage
from model_loaders import (
    get_nlp_model_with_coreferee,
    get_sentence_tokenizer,
)
from pycaption import WebVTTReader
from spacy.lang.en.stop_words import STOP_WORDS


# Use relative paths from the current script location
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "vtt_files", "project_kickoff_transcript_v2.vtt")
output_file = os.path.join(script_dir, "vtt_files", "plain_text_output.txt")

# Extend the list of stop words
# additional_stop_words = {"said", "would", "could", "should", "will", "can", "may", "might"}
# STOP_WORDS.update(additional_stop_words)

# Words to exclude (customize this list as needed)
exclude_words = {
    "um",
    "uh",
    "like",
    "you know",
    "I mean",
    "okay",
    "yeah",
    "well",
    "right",
    "just",
    "really",
    "actually",
    "basically",
    "literally",
    "anyway",
    "anyways",
    "kinda",
    "sorta",
    "sort of",
    "kind of",
    "a lot",
    "in fact",
    "understood",
    "great",
    "excellent",
}


def format_speakers(text):
    # Define a pattern to match speaker labels
    pattern = r"(\s*-\s*)([a-zA-Z\s]+):"

    def format_speaker(match):
        # Extract the entire match and the name group
        match.group(0)
        name = match.group(2)

        # Capitalize each word in the name
        formatted_name = " ".join(word.capitalize() for word in name.split())

        # If it's not the start of the text, add a newline before the speaker
        if match.start() > 0:
            return f"\n\n{formatted_name}: "
        else:
            return f"\n\n{formatted_name}: "

    # Use re.sub with a function to replace and format speaker labels
    formatted_text = re.sub(pattern, format_speaker, text)

    return formatted_text


def clean_text(text):
    # Lazy load NLP model
    nlp = get_nlp_model_with_coreferee()
    # Tokenize the text
    doc = nlp(text)

    # Create a list to store the cleaned tokens
    cleaned_tokens = []

    for token in doc:
        # Convert token to lowercase for comparison
        lower_token = token.text.lower()

        # Check if the token is a whole word that should be excluded
        if (
            lower_token not in STOP_WORDS
            and lower_token not in exclude_words
            and not token.is_punct
        ):
            cleaned_tokens.append(token.text)

    # Join the cleaned tokens, preserving original spacing
    cleaned_text = " ".join(cleaned_tokens)

    # Remove multiple spaces
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return cleaned_text

    # # Remove extra whitespace
    # text = ' '.join(text.split())


def extract_text(captions):
    text = []
    current_speaker = None
    for caption in captions:
        caption_text = "".join(
            node.content for node in caption.nodes if hasattr(node, "content")
        )

        # Check if there's a speaker label
        speaker_match = re.match(r"^(\w+\s*\w*):(.*)$", caption_text)
        if speaker_match:
            speaker, content = speaker_match.groups()
            if speaker != current_speaker:
                if current_speaker is not None:  # Not the first speaker
                    text.append("\n\n")  # Add paragraph break
                current_speaker = speaker
            text.append(f"{speaker}: {content.strip()}")
        else:
            # If no speaker label, just add the text
            text.append(caption_text.strip())

    return " ".join(text)


def merge_captions(captions):
    merged = []
    current = None
    for caption in captions:
        if current is None:
            current = caption
        elif current.end == caption.start:
            # Merge the text
            current.nodes.extend(caption.nodes)
            current.end = caption.end
        else:
            merged.append(current)
            current = caption
    if current:
        merged.append(current)
    return merged


def improve_formatting(text):
    """Step 3: Improve formatting and structure"""
    # Lazy load sentence tokenizer
    sent_tokenize = get_sentence_tokenizer()
    # Split into sentences
    sentences = sent_tokenize(text)

    # Add markdown formatting
    formatted_text = "# Transcript\n\n"
    for sentence in sentences:
        formatted_text += f"{sentence.strip()}\n"

    return formatted_text


def enhance_content(text, min_freq=2, min_length=3):
    """Step 4: Enhance content with filtered entities and topics"""
    # Lazy load NLP model
    nlp = get_nlp_model_with_coreferee()
    doc = nlp(text)

    # Custom list of common expressions to exclude
    common_expressions = {
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
    def is_valid_span(span):
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


# Functions to address ambiguous pronouns
def resolve_coreferences(text):
    # Lazy load NLP model with coreferee
    nlp = get_nlp_model_with_coreferee()

    # Process the text
    doc = nlp(text)

    # Create a dictionary to store named entities
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "PRODUCT"]:
            entities[ent.text.lower()] = ent.text

    # Function to replace pronouns
    def replace_pronoun(match):
        match.group(0).lower()
        previous_sentence = doc[max(0, match.start() - 200) : match.start()].text

        for entity, full_name in entities.items():
            if entity in previous_sentence.lower():
                return full_name

        return match.group(0)

    # Replace pronouns
    resolved_text = re.sub(
        r"\b(he|she|it|they|them)\b", replace_pronoun, text, flags=re.IGNORECASE
    )

    return resolved_text


def clean_sentence(sentence):
    # List of filler words and phrases to remove
    filler_words = [
        r"^(Exactly.?|Well,?|Yeah,?|Yeah, so good|Okay|Sounds good|So,?|All right,?|Okay,?|Um,?|Uh,?|Like,?|You know,?|I mean,?|Right,?|Basically,?|Alright,?|Actually,?|Literally,?|Anyways?,?|Yeah,?|Great,?|Thanks,?)",
        r"(,? so ,?)",
        r"(,? ?you know,?)",
        r"(,? ?I mean,?)",
        r"(,? ?like,?)",
        r"(,? right\??)",
        r"(,? ?okay\??)",
    ]
    #

    # Combine all filler words into one regex pattern
    pattern = "|".join(filler_words)

    # Remove filler words and associated punctuation
    cleaned = re.sub(pattern, "", sentence, flags=re.IGNORECASE)

    # Remove leading/trailing whitespace and capitalize the first letter
    cleaned = cleaned.strip().capitalize()

    return cleaned


def process_text(plain_text):
    # Lazy load sentence tokenizer
    sent_tokenize = get_sentence_tokenizer()
    # Split the plain_text into sentences
    sentences = sent_tokenize(plain_text)

    # Clean each sentence
    cleaned_sentences = [clean_sentence(sentence) for sentence in sentences]

    # Join the cleaned sentences back into a single string
    cleaned_text = " ".join(cleaned_sentences)

    return cleaned_text


def clean_and_format_transcript(text):
    # Remove extra spaces and newlines
    text = re.sub(r"\s+", " ", text).strip()

    # Function to capitalize speaker names and add paragraph breaks
    def format_speaker(match):
        name = match.group(1)
        formatted_name = " ".join(word.capitalize() for word in name.split())
        return f"\n\n{formatted_name}: "

    # Format speaker names and add paragraph breaks
    text = re.sub(r"([a-zA-Z\s]+):", format_speaker, text)

    # Remove filler words
    filler_words = r"\b(alright|yeah|well|so)\b"
    text = re.sub(filler_words, "", text, flags=re.IGNORECASE)

    # Fix punctuation
    text = re.sub(r"\s+([.,:?!])", r"\1", text)  # Remove spaces before punctuation
    text = re.sub(
        r"([.,:?!])(?=[^\s])", r"\1 ", text
    )  # Add space after punctuation if missing
    text = re.sub(r"\.+", ".", text)  # Replace multiple periods with a single one
    text = re.sub(r",+", ",", text)  # Replace multiple commas with a single one

    # Capitalize the first letter of each sentence
    sentences = re.split(r"(?<=[.!?])\s+", text)
    formatted_sentences = [sentence.capitalize() for sentence in sentences if sentence]
    text = " ".join(formatted_sentences)

    # Fix contractions
    text = re.sub(r"(\w+)'\s*(\w+)", r"\1'\2", text)

    # Ensure "Transcript" is on its own line
    text = text.replace("Transcript", "\n# Transcript\n", 1)

    return text.strip()


reader = WebVTTReader()

# with open(input_file, 'r', encoding='utf-8') as f:
#     captions = reader.read(f.read())

# merged_captions = merge_captions(captions.get_captions('en-US'))

# # Create a new CaptionList with merged captions
# new_caption_list = CaptionList(merged_captions, layout_info=None)

# # Create a new caption set with merged captions
# new_captions = CaptionSet({'en-US': new_caption_list})

# writer = WebVTTWriter()
# output = writer.write(new_captions)
# with open(output_file, 'w', encoding='utf-8') as f:
#     f.write(output)


with open(input_file, encoding="utf-8") as f:
    captions = reader.read(f.read())

plain_text = extract_text(captions.get_captions("en-US"))

# plain_text = resolve_coreferences(plain_text)

plain_text = improve_formatting(plain_text)

plain_text = process_text(plain_text)

# Format the speakers
plain_text = format_speakers(plain_text)

# Clean and format the text
# formatted_text = clean_and_format_transcript(plain_text)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(plain_text)
