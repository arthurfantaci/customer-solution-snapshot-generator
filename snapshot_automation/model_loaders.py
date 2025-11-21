"""
Lazy loading utilities for ML models.

This module provides lazy loading functions for expensive ML models (spaCy, transformers)
to improve import times and reduce memory usage when models aren't needed.
"""

import logging
from collections.abc import Callable
from functools import lru_cache
from typing import Any


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_nlp_model(model_name: str = "en_core_web_sm") -> Any:
    """
    Lazy load spaCy NLP model.

    The model is only loaded on first call and cached for subsequent calls.
    This prevents slow imports when spaCy functionality isn't needed.

    Args:
        model_name: Name of the spaCy model to load (default: en_core_web_sm).

    Returns:
        Loaded spaCy Language object.

    Raises:
        OSError: If model cannot be loaded.

    Example:
        >>> nlp = get_nlp_model()
        >>> doc = nlp("Hello world")
    """
    import spacy

    logger.info(f"Loading spaCy model: {model_name}")
    try:
        nlp = spacy.load(model_name)
        logger.info(f"Successfully loaded spaCy model: {model_name}")
        return nlp
    except OSError as e:
        logger.warning(f"Model {model_name} not found. Attempting download...")
        try:
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)
            logger.info(f"Successfully downloaded and loaded: {model_name}")
            return nlp
        except Exception as download_error:
            logger.error(f"Failed to download model {model_name}: {download_error}")
            raise OSError(
                f"Could not load or download spaCy model '{model_name}'. "
                f"Please install it manually: python -m spacy download {model_name}"
            ) from e


@lru_cache(maxsize=1)
def get_nlp_model_with_coreferee(model_name: str = "en_core_web_sm") -> Any:
    """
    Lazy load spaCy NLP model with coreferee pipeline component.

    Args:
        model_name: Name of the spaCy model to load (default: en_core_web_sm).

    Returns:
        Loaded spaCy Language object with coreferee added to pipeline.

    Note:
        Requires coreferee package and spacy<3.6.0 for compatibility.

    Example:
        >>> nlp = get_nlp_model_with_coreferee()
        >>> doc = nlp("John said he likes apples.")
    """

    logger.info(f"Loading spaCy model with coreferee: {model_name}")
    nlp = get_nlp_model(model_name)

    if "coreferee" not in nlp.pipe_names:
        try:
            nlp.add_pipe("coreferee")
            logger.info("Added coreferee to spaCy pipeline")
        except Exception as e:
            logger.warning(f"Could not add coreferee to pipeline: {e}")
            logger.warning("Continuing without coreference resolution")

    return nlp


@lru_cache(maxsize=1)
def get_summarizer(model_name: str = "facebook/bart-large-cnn") -> Any:
    """
    Lazy load transformer summarization model.

    The model is only loaded on first call and cached for subsequent calls.
    This prevents slow imports and high memory usage when summarization isn't needed.

    Args:
        model_name: HuggingFace model identifier (default: facebook/bart-large-cnn).

    Returns:
        HuggingFace pipeline object for summarization.

    Example:
        >>> summarizer = get_summarizer()
        >>> summary = summarizer("Long text here...", max_length=100)
    """
    from transformers import pipeline

    logger.info(f"Loading summarization model: {model_name}")
    summarizer = pipeline("summarization", model=model_name)
    logger.info(f"Successfully loaded summarizer: {model_name}")
    return summarizer


@lru_cache(maxsize=1)
def ensure_nltk_data() -> bool:
    """
    Ensure NLTK data is downloaded.

    Downloads punkt tokenizer if not already present.
    Uses caching to avoid repeated downloads.

    Returns:
        bool: True if data is available, False otherwise.
    """
    import nltk

    try:
        nltk.data.find("tokenizers/punkt")
        return True
    except LookupError:
        logger.info("Downloading NLTK punkt tokenizer...")
        try:
            nltk.download("punkt", quiet=True)
            logger.info("Successfully downloaded NLTK data")
            return True
        except Exception as e:
            logger.error(f"Failed to download NLTK data: {e}")
            return False


def get_sentence_tokenizer() -> Callable[[str], list[str]]:
    """
    Get NLTK sentence tokenizer (with data download if needed).

    Returns:
        Function: sent_tokenize function from NLTK.

    Example:
        >>> sent_tokenize = get_sentence_tokenizer()
        >>> sentences = sent_tokenize("First sentence. Second sentence.")
    """
    from nltk.tokenize import sent_tokenize

    ensure_nltk_data()
    return sent_tokenize


# Pre-warm functions (optional - call these in background if desired)
def preload_all_models() -> None:
    """
    Preload all models in background.

    Call this function to warm up model cache if you know you'll need them.
    Useful for pre-warming in production environments.

    Example:
        >>> import threading
        >>> threading.Thread(target=preload_all_models, daemon=True).start()
    """
    logger.info("Pre-loading all models...")
    try:
        get_nlp_model()
        get_summarizer()
        ensure_nltk_data()
        logger.info("All models pre-loaded successfully")
    except Exception as e:
        logger.warning(f"Some models failed to pre-load: {e}")


def clear_model_cache() -> None:
    """
    Clear all cached models to free memory.

    Use this to force models to be reloaded on next access.
    Useful for testing or when models need to be updated.

    Example:
        >>> clear_model_cache()  # Free ~500MB+ of memory
    """
    get_nlp_model.cache_clear()
    get_nlp_model_with_coreferee.cache_clear()
    get_summarizer.cache_clear()
    ensure_nltk_data.cache_clear()
    logger.info("Cleared all model caches")
