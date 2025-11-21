"""
Utility functions for secure file handling and validation.
"""

import logging
from pathlib import Path
from typing import Optional, Union


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_file_path(
    file_path: Union[str, Path], allowed_extensions: Optional[list[str]] = None
) -> Path:
    """
    Validate file path before use for security.

    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.vtt', '.txt'])

    Returns:
        Path object if valid

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type not allowed or file too large
    """
    if allowed_extensions is None:
        allowed_extensions = [".vtt", ".txt", ".md", ".html"]

    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check if it's a file (not directory)
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Check file extension
    if path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Invalid file type. Allowed extensions: {allowed_extensions}")

    # Check file size (prevent DoS attacks) - 50MB limit
    max_size = 50 * 1024 * 1024  # 50MB
    if path.stat().st_size > max_size:
        raise ValueError(f"File too large. Maximum size: {max_size / (1024 * 1024)}MB")

    logger.info(f"File validation successful: {path}")
    return path


def safe_file_read(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """
    Safely read file with proper error handling.

    Args:
        file_path: Path to file
        encoding: File encoding

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is invalid
        ValueError: If file is too large
    """
    path = validate_file_path(file_path)

    try:
        with open(path, encoding=encoding) as f:
            content = f.read()
            logger.info(f"Successfully read file: {path}")
            return content
    except UnicodeDecodeError as e:
        logger.error(f"Invalid file encoding for {path}")
        raise ValueError(f"Invalid file encoding. Expected {encoding}") from e
    except Exception as e:
        logger.error(f"Error reading file {path}: {type(e).__name__}")
        raise


def safe_file_write(
    file_path: Union[str, Path], content: str, encoding: str = "utf-8"
) -> None:
    """
    Safely write file with proper error handling.

    Args:
        file_path: Path to output file
        content: Content to write
        encoding: File encoding

    Raises:
        PermissionError: If no write permission
        OSError: If disk full or other OS error
    """
    path = Path(file_path)

    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
            logger.info(f"Successfully wrote file: {path}")
    except PermissionError:
        logger.error(f"Permission denied writing to {path}")
        raise
    except OSError as e:
        logger.error(f"OS error writing to {path}: {e}")
        raise


def get_safe_output_path(
    input_path: Union[str, Path], suffix: str = "_processed"
) -> Path:
    """
    Generate a safe output path based on input path.

    Args:
        input_path: Input file path
        suffix: Suffix to add to filename

    Returns:
        Safe output path
    """
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
    return output_path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    sanitized = "".join(c for c in filename if c.isalnum() or c in ("-", "_", "."))

    # Prevent hidden files and current/parent directory references
    if sanitized.startswith(".") or sanitized in ("", ".", ".."):
        sanitized = f"safe_{sanitized}"

    return sanitized


def create_safe_directory(dir_path: Union[str, Path]) -> Path:
    """
    Create directory safely with proper permissions.

    Args:
        dir_path: Directory path to create

    Returns:
        Created directory path
    """
    path = Path(dir_path)

    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created/verified: {path}")
        return path
    except PermissionError:
        logger.error(f"Permission denied creating directory {path}")
        raise
    except OSError as e:
        logger.error(f"OS error creating directory {path}: {e}")
        raise
