"""
Logging configuration for Customer Solution Snapshot Generator.

This module provides centralized logging configuration with security-aware
logging practices and proper formatting.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Set up comprehensive logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for file logging
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging("DEBUG", "app.log")
        >>> logger.info("Application started")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Default format string
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    formatter = SecureFormatter(format_string)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Create logger for this package
    package_logger = logging.getLogger("customer_snapshot")
    package_logger.info(f"Logging configured at level: {log_level}")

    return package_logger


class SecureFormatter(logging.Formatter):
    """
    Secure logging formatter that sanitizes sensitive information.

    This formatter automatically redacts common patterns that might
    contain sensitive information like API keys, passwords, etc.
    """

    # Patterns to redact from log messages
    SENSITIVE_PATTERNS = [
        # API keys
        (r"api[_-]?key[s]?[:\s=]+[\w-]+", r"api_key=[REDACTED]"),
        (r"anthropic[_-]?api[_-]?key[:\s=]+[\w-]+", r"anthropic_api_key=[REDACTED]"),
        (r"voyage[_-]?api[_-]?key[:\s=]+[\w-]+", r"voyage_api_key=[REDACTED]"),
        # Tokens
        (r"token[s]?[:\s=]+[\w.-]+", r"token=[REDACTED]"),
        (r"bearer\s+[\w.-]+", r"bearer [REDACTED]"),
        # Passwords
        (r"password[s]?[:\s=]+\S+", r"password=[REDACTED]"),
        (r"passwd[:\s=]+\S+", r"passwd=[REDACTED]"),
        # Credit card numbers (basic pattern)
        (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", r"[CREDIT_CARD_REDACTED]"),
        # Email addresses (partial redaction)
        (r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"\1***@\2"),
        # IP addresses (partial redaction)
        (r"\b(\d{1,3})\.\d{1,3}\.\d{1,3}\.(\d{1,3})\b", r"\1.***.***.\2"),
    ]

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with sensitive information redacted.

        Args:
            record: Log record to format

        Returns:
            Formatted and sanitized log message
        """
        # Format the message normally first
        formatted_message = super().format(record)

        # Apply sensitive pattern redaction
        sanitized_message = self._sanitize_message(formatted_message)

        return sanitized_message

    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize message by redacting sensitive patterns.

        Args:
            message: Original log message

        Returns:
            Sanitized message with sensitive data redacted
        """
        import re

        sanitized = message

        for pattern, replacement in self.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized


class StructuredLogger:
    """
    Structured logger for consistent logging with metadata.

    Provides convenience methods for logging with consistent structure
    and automatic context information.
    """

    def __init__(self, name: str, extra_context: Optional[dict] = None):
        """
        Initialize structured logger.

        Args:
            name: Logger name (usually module name)
            extra_context: Additional context to include in all log messages
        """
        self.logger = logging.getLogger(name)
        self.extra_context = extra_context or {}

    def _log_with_context(
        self, level: int, message: str, context: Optional[dict] = None, **kwargs
    ) -> None:
        """
        Log message with structured context.

        Args:
            level: Logging level
            message: Log message
            context: Additional context for this message
            **kwargs: Additional keyword arguments
        """
        # Combine default context with message-specific context
        full_context = {**self.extra_context}
        if context:
            full_context.update(context)

        # Format message with context
        if full_context:
            context_str = " | ".join(f"{k}={v}" for k, v in full_context.items())
            formatted_message = f"{message} | {context_str}"
        else:
            formatted_message = message

        self.logger.log(level, formatted_message, **kwargs)

    def debug(self, message: str, context: Optional[dict] = None, **kwargs) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, context, **kwargs)

    def info(self, message: str, context: Optional[dict] = None, **kwargs) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, context, **kwargs)

    def warning(self, message: str, context: Optional[dict] = None, **kwargs) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, context, **kwargs)

    def error(self, message: str, context: Optional[dict] = None, **kwargs) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, context, **kwargs)

    def critical(self, message: str, context: Optional[dict] = None, **kwargs) -> None:
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, context, **kwargs)


def get_logger(name: str, extra_context: Optional[dict] = None) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)
        extra_context: Additional context to include in all messages

    Returns:
        Structured logger instance

    Example:
        >>> logger = get_logger(__name__, {"component": "transcript_processor"})
        >>> logger.info("Processing started", {"file": "input.vtt"})
    """
    return StructuredLogger(name, extra_context)


def configure_third_party_loggers(level: str = "WARNING") -> None:
    """
    Configure third-party library loggers to reduce noise.

    Args:
        level: Log level for third-party loggers
    """
    # Common noisy third-party loggers
    third_party_loggers = [
        "urllib3.connectionpool",
        "requests.packages.urllib3",
        "anthropic._base_client",
        "httpx",
        "httpcore",
        "openai",
        "transformers.tokenization_utils_base",
        "transformers.configuration_utils",
        "transformers.modeling_utils",
    ]

    numeric_level = getattr(logging, level.upper(), logging.WARNING)

    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
        logger.propagate = False


def log_function_call(func):
    """
    Decorator to automatically log function calls with parameters.

    Args:
        func: Function to decorate

    Returns:
        Decorated function

    Example:
        >>> @log_function_call
        ... def process_file(filename):
        ...     return f"Processed {filename}"
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)

        # Log function entry (be careful with sensitive parameters)
        logger.debug(
            f"Calling {func.__name__} with {len(args)} args and {len(kwargs)} kwargs"
        )

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {type(e).__name__}: {e}")
            raise

    return wrapper
