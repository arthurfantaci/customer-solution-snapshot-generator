"""
NLP processing engine for text analysis and enhancement.
"""
import logging
import re
from collections import Counter
from typing import Dict, List, Set, Tuple, Union, Optional

import nltk
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

from ..utils.config import Config

logger = logging.getLogger(__name__)


class NLPEngine:
    """
    Natural Language Processing engine for transcript analysis.
    
    Handles text cleaning, entity extraction, topic identification,
    and content enhancement using spaCy and NLTK.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the NLP engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self._nlp_model: Optional[spacy.Language] = None
        self._setup_nltk()
        logger.info("NLPEngine initialized")

    @property
    def nlp(self) -> spacy.Language:
        """Lazy load the spaCy model."""
        if self._nlp_model is None:
            self._nlp_model = self._load_spacy_model()
        return self._nlp_model

    def _load_spacy_model(self) -> spacy.Language:
        """
        Load and configure the spaCy NLP model.
        
        Returns:
            Configured spaCy language model
            
        Raises:
            RuntimeError: If model loading fails
        """
        try:
            nlp_model = spacy.load(self.config.spacy_model)
            logger.info(f"Loaded spaCy model: {self.config.spacy_model}")
            return nlp_model
        except OSError as e:
            logger.error(f"Failed to load spaCy model {self.config.spacy_model}: {e}")
            raise RuntimeError(f"Could not load spaCy model: {self.config.spacy_model}") from e

    def _setup_nltk(self) -> None:
        """Download required NLTK data."""
        try:
            nltk.download('punkt', quiet=True)
            logger.debug("NLTK punkt tokenizer downloaded")
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")

    def clean_text(self, text: str) -> str:
        """
        Clean raw transcript text by removing speaker labels and timestamps.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove speaker labels (e.g., "Speaker 1:", "John:", etc.)
        text = re.sub(r'^[A-Za-z\s]+\d*:\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\b[A-Z][a-zA-Z\s]+:\s*', '', text)
        
        # Remove timestamps (e.g., "00:01:23.456")
        text = re.sub(r'\b\d{2}:\d{2}:\d{2}\.\d{3}\b', '', text)
        text = re.sub(r'\b\d{1,2}:\d{2}:\d{2}\b', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        logger.debug(f"Text cleaned: {len(text)} characters")
        return text

    def improve_formatting(self, text: str) -> str:
        """
        Improve text formatting and structure.
        
        Args:
            text: Text to format
            
        Returns:
            Formatted text
        """
        if not text:
            return ""
        
        # Capitalize first letter of sentences
        sentences = nltk.sent_tokenize(text)
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                formatted_sentences.append(sentence)
        
        # Join with proper spacing
        formatted_text = ' '.join(formatted_sentences)
        
        logger.debug("Text formatting improved")
        return formatted_text

    def standardize_quotes(self, text: str) -> str:
        """
        Standardize quotation marks in text.
        
        Args:
            text: Text to standardize
            
        Returns:
            Text with standardized quotes
        """
        # Replace single quotes with double quotes
        text = re.sub(r"(?<!\w)'|'(?!\w)", '"', text)
        # Fix curly quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text

    def split_long_sentences(self, text: str, max_length: int = 150) -> str:
        """
        Split overly long sentences for better readability.
        
        Args:
            text: Text to process
            max_length: Maximum sentence length in characters
            
        Returns:
            Text with split sentences
        """
        sentences = nltk.sent_tokenize(text)
        processed_sentences = []
        
        for sentence in sentences:
            if len(sentence) <= max_length:
                processed_sentences.append(sentence)
            else:
                # Split on conjunctions and commas
                parts = re.split(r',\s+(?=and|but|or|however|therefore|moreover)', sentence)
                processed_sentences.extend(part.strip() for part in parts if part.strip())
        
        return ' '.join(processed_sentences)

    def enhance_content(self, text: str) -> str:
        """
        Enhance content with entity and topic analysis.
        
        Args:
            text: Text to enhance
            
        Returns:
            Enhanced text with identified entities and topics
        """
        if not text:
            return ""
        
        try:
            doc = self.nlp(text)
            
            # Extract entities and topics
            entities = self._extract_entities(doc)
            topics = self._extract_topics(doc)
            
            # Add enhancement section
            enhancement = self._create_enhancement_section(entities, topics)
            
            # Combine original text with enhancements
            enhanced_text = f"{text}\n\n{enhancement}"
            
            logger.debug(f"Content enhanced with {len(entities)} entities and {len(topics)} topics")
            return enhanced_text
            
        except Exception as e:
            logger.warning(f"Content enhancement failed: {e}")
            return text

    def _extract_entities(self, doc: spacy.tokens.Doc) -> List[Tuple[str, str]]:
        """
        Extract named entities from spaCy document.
        
        Args:
            doc: Processed spaCy document
            
        Returns:
            List of (entity_text, entity_label) tuples
        """
        entities = []
        for ent in doc.ents:
            if self._is_valid_entity(ent):
                entities.append((ent.text, ent.label_))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)
        
        return unique_entities

    def _extract_topics(self, doc: spacy.tokens.Doc) -> List[str]:
        """
        Extract potential topics from noun chunks.
        
        Args:
            doc: Processed spaCy document
            
        Returns:
            List of topic strings
        """
        topics = []
        for chunk in doc.noun_chunks:
            if self._is_valid_topic(chunk):
                topics.append(chunk.text)
        
        # Count frequency and filter
        topic_counts = Counter(topics)
        filtered_topics = [
            topic for topic, count in topic_counts.items()
            if count >= self.config.min_entity_frequency
        ]
        
        return filtered_topics[:10]  # Limit to top 10 topics

    def _is_valid_entity(self, entity: spacy.tokens.Span) -> bool:
        """
        Check if an entity is valid for inclusion.
        
        Args:
            entity: spaCy entity span
            
        Returns:
            True if entity is valid
        """
        # Filter by length
        if len(entity.text) < self.config.min_entity_length:
            return False
        
        # Filter out common, low-value entities
        excluded_labels = {'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL'}
        if entity.label_ in excluded_labels:
            return False
        
        # Filter out stop words
        if entity.text.lower() in STOP_WORDS:
            return False
        
        return True

    def _is_valid_topic(self, chunk: spacy.tokens.Span) -> bool:
        """
        Check if a noun chunk is a valid topic.
        
        Args:
            chunk: spaCy span representing a noun chunk
            
        Returns:
            True if chunk represents a valid topic
        """
        # Filter by length
        if len(chunk.text) < self.config.min_entity_length:
            return False
        
        # Check if contains meaningful content
        if any(token.is_stop or token.pos_ in ['DET', 'PRON'] for token in chunk):
            return False
        
        return True

    def _create_enhancement_section(self, entities: List[Tuple[str, str]], topics: List[str]) -> str:
        """
        Create an enhancement section with entities and topics.
        
        Args:
            entities: List of extracted entities
            topics: List of extracted topics
            
        Returns:
            Formatted enhancement section
        """
        enhancement_parts = []
        
        if entities:
            enhancement_parts.append("## Key Entities Identified")
            for entity_text, entity_label in entities:
                enhancement_parts.append(f"- **{entity_text}** ({entity_label})")
        
        if topics:
            enhancement_parts.append("\n## Topics Discussed")
            for topic in topics:
                enhancement_parts.append(f"- {topic}")
        
        return "\n".join(enhancement_parts) if enhancement_parts else ""

    def extract_technical_terms(self, text: str) -> List[str]:
        """
        Extract technical terms from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of technical terms
        """
        if not text:
            return []
        
        try:
            doc = self.nlp(text)
            
            # Extract technical terms from entities and noun phrases
            technical_terms = set()
            
            # From entities
            for ent in doc.ents:
                if ent.label_ in ['PRODUCT', 'ORG', 'TECHNOLOGY']:
                    technical_terms.add(ent.text)
            
            # From noun phrases (potential technical terms)
            for chunk in doc.noun_chunks:
                if self._is_technical_term(chunk):
                    technical_terms.add(chunk.text)
            
            return sorted(list(technical_terms))
            
        except Exception as e:
            logger.warning(f"Technical term extraction failed: {e}")
            return []

    def _is_technical_term(self, chunk: spacy.tokens.Span) -> bool:
        """
        Determine if a noun chunk represents a technical term.
        
        Args:
            chunk: spaCy span to evaluate
            
        Returns:
            True if chunk appears to be a technical term
        """
        text = chunk.text.lower()
        
        # Common technical indicators
        tech_indicators = [
            'platform', 'api', 'database', 'analytics', 'dashboard',
            'connector', 'cloud', 'data', 'system', 'service',
            'integration', 'framework', 'protocol', 'interface'
        ]
        
        return any(indicator in text for indicator in tech_indicators)

    def get_text_statistics(self, text: str) -> Dict[str, Union[int, float]]:
        """
        Get statistical information about the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {}
        
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0
        }